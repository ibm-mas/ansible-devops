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
        assert command == "oc patch installplan/install-plan-1 -n test-namespace --type merge -p '{\"spec\":{\"approved\":true}}'"
        assert "or use the OpenShift Console" in olm_approvals.formatApprovalNotice(APPROVAL)[3]


class TestWaitForSubscriptionApproval:
    """Tests for the wait orchestration in waitForSubscriptionApproval."""

    def test_noop_when_nothing_pending(self):
        display = Mock()
        status = makeStatus(pendingApprovals=[])
        with patch.object(olm_approvals, "getNamespaceApprovalStatus", return_value=status):
            result = olm_approvals.waitForSubscriptionApproval(Mock(), display, "test-namespace")

        assert result is status
        display.display.assert_not_called()

    def test_automatic_mode_mismatch_raises(self):
        display = Mock()
        status = makeStatus(approvalMode="Automatic", pendingApprovals=[APPROVAL])
        with patch.object(olm_approvals, "getNamespaceApprovalStatus", return_value=status):
            with pytest.raises(ValueError, match="Install plans are waiting for manual approval in namespace test-namespace"):
                olm_approvals.waitForSubscriptionApproval(Mock(), display, "test-namespace", approvalMode="Automatic")

    def test_manual_wait_displays_notices_and_waits_for_operator(self):
        display = Mock()
        blocking = makeStatus(pendingApprovals=[APPROVAL])
        final = makeStatus(pendingApprovals=[])
        with patch.object(olm_approvals, "getNamespaceApprovalStatus", side_effect=[blocking, final]):
            with patch.object(olm_approvals, "waitForNamespaceApprovals") as mockWait:
                with patch.object(olm_approvals, "waitForInstallPlanComplete") as mockPlanComplete:
                    with patch.object(olm_approvals, "waitForSubscriptionStable") as mockStable:
                        result = olm_approvals.waitForSubscriptionApproval(
                            Mock(), display, "test-namespace",
                            packageName="test-operator", targetCSV="test-operator.v2.0.0",
                            timeout=600, approvalMode="Manual"
                        )

        assert result is final
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
            with patch.object(olm_approvals, "waitForNamespaceApprovals"):
                with patch.object(olm_approvals, "waitForInstallPlanComplete"):
                    with patch.object(olm_approvals, "waitForSubscriptionStable"):
                        result = olm_approvals.waitForSubscriptionApproval(
                            Mock(), display, "test-namespace", approvalMode="Manual"
                        )

        assert result is final
        displayed = " ".join(str(call.args[0]) for call in display.display.call_args_list)
        assert "mix of approval modes" in displayed

    def test_timeout_error_repeats_approve_commands(self):
        display = Mock()
        blocking = makeStatus(pendingApprovals=[APPROVAL])
        with patch.object(olm_approvals, "getNamespaceApprovalStatus", return_value=blocking):
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
            with patch.object(olm_approvals, "waitForNamespaceApprovals") as mockWait:
                with patch.object(olm_approvals, "waitForInstallPlanComplete"):
                    with patch.object(olm_approvals, "waitForSubscriptionStable"):
                        olm_approvals.waitForSubscriptionApproval(
                            Mock(), display, "test-namespace", timeout=7200, approvalMode="Manual"
                        )

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
            with patch.object(olm_approvals, "waitForNamespaceApprovals") as mockWait:
                with patch.object(olm_approvals, "waitForInstallPlanComplete"):
                    with patch.object(olm_approvals, "waitForSubscriptionStable"):
                        olm_approvals.waitForSubscriptionApproval(
                            Mock(), display, "test-namespace", timeout=7200, approvalMode="Manual"
                        )

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

# Made with Bob
