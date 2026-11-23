"""
Unit tests for the olm_approvals module_utils helper.

The mas.devops.olm functions the helper calls are mocked: these tests cover
the collection-side behavior (env var resolution, notice formatting, the
wait/timeout orchestration and the approval mode mismatch check), not the
python-devops library itself.
"""

from unittest.mock import Mock, patch

import pytest
from mas.devops.olm import OLMTimeoutError

from ansible_collections.ibm.mas_devops.plugins.module_utils import olm_approvals

APPROVAL = {
    "installPlan": "install-plan-1",
    "namespace": "test-namespace",
    "subscription": "test-operator",
    "package": "test-operator",
    "csvNames": ["test-operator.v2.0.0"],
    "currentCSV": "test-operator.v1.0.0",
    "targetCSV": "test-operator.v2.0.0",
    "created": "2026-11-15T10:00:00Z",
}


def makeStatus(namespace="test-namespace", approvalMode="Manual", pendingApprovals=None):
    pendingApprovals = pendingApprovals if pendingApprovals is not None else []
    return {
        "namespace": namespace,
        "approvalMode": approvalMode,
        "pendingApprovals": pendingApprovals,
        "blocking": len(pendingApprovals) > 0,
    }


@pytest.fixture(autouse=True)
def isolate_olm_approval_env(monkeypatch):
    monkeypatch.delenv("OLM_APPROVAL_MODE", raising=False)
    monkeypatch.delenv("OLM_APPROVAL_TIMEOUT", raising=False)


class TestResolveApprovalMode:
    """Tests for resolveApprovalMode precedence and validation."""

    def test_task_arg_takes_precedence_over_env(self, monkeypatch):
        monkeypatch.setenv("OLM_APPROVAL_MODE", "Manual")
        assert olm_approvals.resolveApprovalMode("Automatic") == "Automatic"

    def test_env_used_when_no_task_arg(self, monkeypatch):
        monkeypatch.setenv("OLM_APPROVAL_MODE", "Manual")
        assert olm_approvals.resolveApprovalMode(None) == "Manual"

    def test_none_when_neither_set(self):
        assert olm_approvals.resolveApprovalMode(None) is None

    def test_invalid_env_value_raises(self, monkeypatch):
        monkeypatch.setenv("OLM_APPROVAL_MODE", "banana")
        with pytest.raises(ValueError, match="OLM_APPROVAL_MODE must be one of"):
            olm_approvals.resolveApprovalMode(None)

    def test_invalid_task_arg_raises(self):
        with pytest.raises(ValueError, match="install_plan_approval must be one of"):
            olm_approvals.resolveApprovalMode("banana")


class TestResolveApprovalTimeout:
    """Tests for resolveApprovalTimeout precedence."""

    def test_task_arg_takes_precedence_over_env(self, monkeypatch):
        monkeypatch.setenv("OLM_APPROVAL_TIMEOUT", "600")
        assert olm_approvals.resolveApprovalTimeout(300) == 300

    def test_env_used_when_no_task_arg(self, monkeypatch):
        monkeypatch.setenv("OLM_APPROVAL_TIMEOUT", "600")
        assert olm_approvals.resolveApprovalTimeout(None) == 600

    def test_default_when_neither_set(self):
        assert olm_approvals.resolveApprovalTimeout(None) == 7200


class TestFormatApprovalNotice:
    """Tests for the human-facing notice formatting."""

    def test_notice_contains_plan_package_and_csv_transition(self):
        lines = olm_approvals.formatApprovalNotice(APPROVAL)
        assert lines[0] == "Waiting for manual approval of install plan install-plan-1 in namespace test-namespace"
        assert "test-operator.v1.0.0 -> test-operator.v2.0.0" in lines[1]
        assert "test-operator.v2.0.0" in lines[2]

    def test_notice_handles_no_current_csv(self):
        approval = dict(APPROVAL, currentCSV=None)
        lines = olm_approvals.formatApprovalNotice(approval)
        assert "(not installed) -> test-operator.v2.0.0" in lines[1]

    def test_approve_command_is_a_merge_patch(self):
        command = olm_approvals.approveCommand(APPROVAL)
        assert command == 'oc patch installplan/install-plan-1 -n test-namespace --type merge -p \'{"spec":{"approved":true}}\''
        assert "or use the OpenShift Console" in olm_approvals.formatApprovalNotice(APPROVAL)[3]


class TestWaitForSubscriptionApproval:
    """Tests for the wait orchestration in waitForSubscriptionApproval."""

    def test_noop_when_nothing_pending(self):
        display = Mock()
        status = makeStatus(pendingApprovals=[])
        with patch.object(olm_approvals, "getNamespaceApprovalStatus", return_value=status):
            with patch.object(olm_approvals, "getSubscriptionInstallPlanRefs", return_value={}):
                result = olm_approvals.waitForSubscriptionApproval(Mock(), display, "test-namespace")

        assert result is status
        assert result["waited"] is False
        display.display.assert_not_called()

    def test_automatic_mode_mismatch_raises(self):
        display = Mock()
        status = makeStatus(approvalMode="Automatic", pendingApprovals=[APPROVAL])
        with patch.object(olm_approvals, "getNamespaceApprovalStatus", return_value=status):
            with patch.object(olm_approvals, "getSubscriptionInstallPlanRefs", return_value={}) as mockRefs:
                with pytest.raises(ValueError, match="Install plans are waiting for manual approval in namespace test-namespace"):
                    olm_approvals.waitForSubscriptionApproval(Mock(), display, "test-namespace", approvalMode="Automatic")

        # An Automatic namespace never enters the generation race pre-gate
        mockRefs.assert_not_called()

    def test_unset_mode_mismatch_raises_with_remedy(self):
        display = Mock()
        status = makeStatus(approvalMode="Manual", pendingApprovals=[APPROVAL])
        with patch.object(olm_approvals, "getNamespaceApprovalStatus", return_value=status):
            with patch.object(olm_approvals, "getSubscriptionInstallPlanRefs", return_value={}):
                with pytest.raises(ValueError) as excinfo:
                    olm_approvals.waitForSubscriptionApproval(Mock(), display, "test-namespace", approvalMode=None)

        # An unset mode is an Automatic context: fail fast with the approve
        # commands and the OLM_APPROVAL_MODE=Manual remedy
        message = str(excinfo.value)
        assert "approval mode is 'Automatic'" in message
        assert "oc patch installplan/install-plan-1" in message
        assert "OLM_APPROVAL_MODE=Manual" in message

    def test_manual_wait_displays_notices_and_waits_for_operator(self):
        display = Mock()
        blocking = makeStatus(pendingApprovals=[APPROVAL])
        final = makeStatus(pendingApprovals=[])
        with patch.object(olm_approvals, "getNamespaceApprovalStatus", side_effect=[blocking, final]):
            with patch.object(olm_approvals, "getSubscriptionInstallPlanRefs", return_value={}):
                with patch.object(olm_approvals, "waitForNamespaceApprovals") as mockWait:
                    with patch.object(olm_approvals, "waitForInstallPlanComplete") as mockPlanComplete:
                        with patch.object(olm_approvals, "waitForSubscriptionStable") as mockStable:
                            result = olm_approvals.waitForSubscriptionApproval(
                                Mock(),
                                display,
                                "test-namespace",
                                packageName="test-operator",
                                targetCSV="test-operator.v2.0.0",
                                timeout=600,
                                approvalMode="Manual",
                            )

        assert result is final
        assert result["waited"] is True
        displayed = " ".join(str(call.args[0]) for call in display.display.call_args_list)
        assert "Waiting for manual approval of install plan install-plan-1" in displayed
        assert "oc patch installplan/install-plan-1" in displayed

        mockWait.assert_called_once()
        assert mockWait.call_args.kwargs["timeout"] == 600
        onPending = mockWait.call_args.kwargs["onPending"]
        assert onPending is not None

        mockPlanComplete.assert_called_once()
        assert mockPlanComplete.call_args.args[2] == "install-plan-1"
        mockStable.assert_called_once()
        assert mockStable.call_args.kwargs["targetCSV"] == "test-operator.v2.0.0"

    def test_mixed_namespace_reported_not_fatal(self):
        display = Mock()
        blocking = makeStatus(approvalMode="Mixed", pendingApprovals=[APPROVAL])
        final = makeStatus(pendingApprovals=[])
        with patch.object(olm_approvals, "getNamespaceApprovalStatus", side_effect=[blocking, final]):
            with patch.object(olm_approvals, "getSubscriptionInstallPlanRefs", return_value={}):
                with patch.object(olm_approvals, "waitForNamespaceApprovals"):
                    with patch.object(olm_approvals, "waitForInstallPlanComplete"):
                        with patch.object(olm_approvals, "waitForSubscriptionStable"):
                            result = olm_approvals.waitForSubscriptionApproval(Mock(), display, "test-namespace", approvalMode="Manual")

        assert result is final
        displayed = " ".join(str(call.args[0]) for call in display.display.call_args_list)
        assert "mix of approval modes" in displayed

    def test_timeout_error_repeats_approve_commands(self):
        display = Mock()
        blocking = makeStatus(pendingApprovals=[APPROVAL])
        with patch.object(olm_approvals, "getNamespaceApprovalStatus", return_value=blocking):
            with patch.object(olm_approvals, "getSubscriptionInstallPlanRefs", return_value={}):
                with patch.object(olm_approvals, "waitForNamespaceApprovals", side_effect=OLMTimeoutError("timed out")):
                    with pytest.raises(OLMTimeoutError) as excinfo:
                        olm_approvals.waitForSubscriptionApproval(Mock(), display, "test-namespace", timeout=300, approvalMode="Manual")

        assert "Timed out after 300s" in str(excinfo.value)
        assert "oc patch installplan/install-plan-1" in str(excinfo.value)

    def test_status_line_logged_on_first_poll_and_then_time_gated(self):
        display = Mock()
        blocking = makeStatus(pendingApprovals=[APPROVAL])
        final = makeStatus(pendingApprovals=[])

        with patch.object(olm_approvals, "getNamespaceApprovalStatus", side_effect=[blocking, final]):
            with patch.object(olm_approvals, "getSubscriptionInstallPlanRefs", return_value={}):
                with patch.object(olm_approvals, "waitForNamespaceApprovals") as mockWait:
                    with patch.object(olm_approvals, "waitForInstallPlanComplete"):
                        with patch.object(olm_approvals, "waitForSubscriptionStable"):
                            olm_approvals.waitForSubscriptionApproval(Mock(), display, "test-namespace", timeout=7200, approvalMode="Manual")

        onPending = mockWait.call_args.kwargs["onPending"]
        noticesBeforeStatusLines = display.display.call_count

        # First poll logs the status line immediately
        assert onPending(blocking, 1) is not False
        assert display.display.call_count == noticesBeforeStatusLines + 1
        assert "Waiting for install plan approval since" in str(display.display.call_args.args[0])
        assert "approval deadline" in str(display.display.call_args.args[0])

        # A poll seconds later does not log again (5 minute interval)
        assert onPending(blocking, 2) is not False
        assert display.display.call_count == noticesBeforeStatusLines + 1

    def test_status_line_logged_again_after_interval(self):
        display = Mock()
        blocking = makeStatus(pendingApprovals=[APPROVAL])
        final = makeStatus(pendingApprovals=[])

        with patch.object(olm_approvals, "getNamespaceApprovalStatus", side_effect=[blocking, final]):
            with patch.object(olm_approvals, "getSubscriptionInstallPlanRefs", return_value={}):
                with patch.object(olm_approvals, "waitForNamespaceApprovals") as mockWait:
                    with patch.object(olm_approvals, "waitForInstallPlanComplete"):
                        with patch.object(olm_approvals, "waitForSubscriptionStable"):
                            olm_approvals.waitForSubscriptionApproval(Mock(), display, "test-namespace", timeout=7200, approvalMode="Manual")

        onPending = mockWait.call_args.kwargs["onPending"]
        assert onPending(blocking, 1) is not False
        baseline = display.display.call_count

        # Advance wall clock past the status interval: the next poll logs again
        # (datetime itself is immutable, so the module's datetime binding is
        # replaced with a fake whose now() returns the advanced time)
        future = olm_approvals.datetime.now(olm_approvals.timezone.utc).timestamp() + olm_approvals.STATUS_INTERVAL + 1
        fake_datetime = Mock(wraps=olm_approvals.datetime)
        fake_datetime.now = Mock(return_value=olm_approvals.datetime.fromtimestamp(future, tz=olm_approvals.timezone.utc))
        with patch.object(olm_approvals, "datetime", fake_datetime):
            assert onPending(blocking, 2) is not False

        assert display.display.call_count == baseline + 1


class TestWaitForSubscriptionApprovalGenerationRace:
    """Tests for the creation-to-generation race pre-gate.

    A Manual/Mixed namespace snapshot taken moments after Subscription
    creation (or a Subscription patch) can miss the InstallPlans OLM has not
    generated yet: the pre-gate waits for generation (fresh Subscriptions,
    no installPlanRef) and settles on status stability (pre-existing
    Subscriptions, possibly just patched) before the blocking check runs.
    """

    def test_fresh_subscription_waits_for_generation_then_notices(self):
        display = Mock()
        before = makeStatus(pendingApprovals=[])
        blocking = makeStatus(pendingApprovals=[APPROVAL])
        final = makeStatus(pendingApprovals=[])

        with patch.object(olm_approvals, "getNamespaceApprovalStatus", side_effect=[before, blocking, final]):
            with patch.object(olm_approvals, "getSubscriptionInstallPlanRefs", return_value={"test-operator": None}):
                with patch.object(olm_approvals, "waitForSubscriptionInstallPlans") as mockGenerate:
                    with patch.object(olm_approvals, "waitForSubscriptionResolution") as mockSettle:
                        with patch.object(olm_approvals, "waitForNamespaceApprovals"):
                            result = olm_approvals.waitForSubscriptionApproval(Mock(), display, "test-namespace", approvalMode="Manual")

        # All Subscriptions were fresh: the ref appearing is the resolution
        # event, so no settle poll is needed
        mockGenerate.assert_called_once()
        mockSettle.assert_not_called()
        assert result["waited"] is True

    def test_settled_subscription_settles_before_checking(self):
        display = Mock()
        before = makeStatus(pendingApprovals=[])
        blocking = makeStatus(pendingApprovals=[APPROVAL])
        final = makeStatus(pendingApprovals=[])

        with patch.object(olm_approvals, "getNamespaceApprovalStatus", side_effect=[before, blocking, final]):
            with patch.object(olm_approvals, "getSubscriptionInstallPlanRefs", return_value={"test-operator": "install-plan-0"}):
                with patch.object(olm_approvals, "waitForSubscriptionInstallPlans") as mockGenerate:
                    with patch.object(olm_approvals, "waitForSubscriptionResolution") as mockSettle:
                        with patch.object(olm_approvals, "waitForNamespaceApprovals"):
                            result = olm_approvals.waitForSubscriptionApproval(Mock(), display, "test-namespace", approvalMode="Manual")

        # A pre-existing ref means the Subscription may have been patched
        # moments ago: settle on status stability instead of generation
        mockGenerate.assert_not_called()
        mockSettle.assert_called_once()
        assert result["waited"] is True

    def test_mixed_fresh_and_settled_subscriptions_wait_both_ways(self):
        display = Mock()
        before = makeStatus(pendingApprovals=[])
        final = makeStatus(pendingApprovals=[])

        with patch.object(olm_approvals, "getNamespaceApprovalStatus", side_effect=[before, final]):
            with patch.object(olm_approvals, "getSubscriptionInstallPlanRefs", return_value={"fresh": None, "settled": "install-plan-0"}):
                with patch.object(olm_approvals, "waitForSubscriptionInstallPlans") as mockGenerate:
                    with patch.object(olm_approvals, "waitForSubscriptionResolution") as mockSettle:
                        olm_approvals.waitForSubscriptionApproval(Mock(), display, "test-namespace", approvalMode="Manual")

        mockGenerate.assert_called_once()
        mockSettle.assert_called_once()

    def test_generation_wait_failure_propagates(self):
        display = Mock()
        before = makeStatus(pendingApprovals=[])

        with patch.object(olm_approvals, "getNamespaceApprovalStatus", return_value=before):
            with patch.object(olm_approvals, "getSubscriptionInstallPlanRefs", return_value={"test-operator": None}):
                with patch.object(
                    olm_approvals,
                    "waitForSubscriptionInstallPlans",
                    side_effect=OLMTimeoutError("Timed out after 600s waiting for OLM to generate InstallPlans"),
                ):
                    with pytest.raises(OLMTimeoutError, match="Timed out after 600s"):
                        olm_approvals.waitForSubscriptionApproval(Mock(), display, "test-namespace", approvalMode="Manual")

    def test_automatic_namespace_skips_the_pre_gate(self):
        display = Mock()
        status = makeStatus(approvalMode="Automatic", pendingApprovals=[])

        with patch.object(olm_approvals, "getNamespaceApprovalStatus", return_value=status):
            with patch.object(olm_approvals, "getSubscriptionInstallPlanRefs") as mockRefs:
                result = olm_approvals.waitForSubscriptionApproval(Mock(), display, "test-namespace")

        # OLM approves by itself in Automatic namespaces: no pre-gate, no
        # delay, exactly the behavior before the race fix
        mockRefs.assert_not_called()
        assert result["waited"] is False


# Made with Bob
