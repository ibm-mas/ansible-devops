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


def makeStatus(namespace="test-namespace", approvalMode="Manual", pendingApprovals=None, subscriptions=None, converged=True):
    pendingApprovals = pendingApprovals if pendingApprovals is not None else []
    return {
        "namespace": namespace,
        "approvalMode": approvalMode,
        "pendingApprovals": pendingApprovals,
        "blocking": len(pendingApprovals) > 0,
        "subscriptions": subscriptions if subscriptions is not None else [],
        "failedInstallPlans": [],
        "converged": converged,
    }


def makeSubscriptionEntry(
    name="test-operator",
    package="test-operator",
    converged=True,
    installedCSV="test-operator.v2.0.0",
    targetCSV="test-operator.v2.0.0",
    skipped=False,
    skipReason=None,
):
    return {
        "name": name,
        "package": package,
        "channel": "stable",
        "state": "AtLatestKnown" if converged else "UpgradePending",
        "installedCSV": installedCSV,
        "targetCSV": targetCSV,
        "installPlanRef": "install-plan-1",
        "converged": converged,
        "skipped": skipped,
        "skipReason": skipReason,
        "resolutionError": None,
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

    def test_converged_namespace_returns_without_waiting(self):
        display = Mock()
        status = makeStatus(pendingApprovals=[])
        with patch.object(olm_approvals, "getNamespaceApprovalStatus", return_value=status):
            with patch.object(olm_approvals, "waitForSubscriptionConvergence", return_value=status) as mockWait:
                result = olm_approvals.waitForSubscriptionApproval(Mock(), display, "test-namespace")

        mockWait.assert_called_once()
        assert result is status
        assert result["waited"] is False
        display.display.assert_not_called()

    def test_automatic_mode_mismatch_raises(self):
        display = Mock()
        status = makeStatus(approvalMode="Automatic", pendingApprovals=[APPROVAL])
        with patch.object(olm_approvals, "getNamespaceApprovalStatus", return_value=status):
            with patch.object(olm_approvals, "waitForSubscriptionConvergence") as mockWait:
                with pytest.raises(ValueError, match="Install plans are waiting for manual approval in namespace test-namespace"):
                    olm_approvals.waitForSubscriptionApproval(Mock(), display, "test-namespace", approvalMode="Automatic")

        # The mismatch fails before any wait begins
        mockWait.assert_not_called()

    def test_unset_mode_mismatch_raises_with_remedy(self):
        display = Mock()
        status = makeStatus(approvalMode="Manual", pendingApprovals=[APPROVAL])
        with patch.object(olm_approvals, "getNamespaceApprovalStatus", return_value=status):
            with patch.object(olm_approvals, "waitForSubscriptionConvergence"):
                with pytest.raises(ValueError) as excinfo:
                    olm_approvals.waitForSubscriptionApproval(Mock(), display, "test-namespace", approvalMode=None)

        # An unset mode is an Automatic context: fail fast with the approve
        # commands and the OLM_APPROVAL_MODE=Manual remedy
        message = str(excinfo.value)
        assert "approval mode is 'Automatic'" in message
        assert "oc patch installplan/install-plan-1" in message
        assert "OLM_APPROVAL_MODE=Manual" in message

    def test_manual_wait_displays_notices_and_waits_for_convergence(self):
        display = Mock()
        blocking = makeStatus(pendingApprovals=[APPROVAL])
        final = makeStatus(pendingApprovals=[])
        with patch.object(olm_approvals, "getNamespaceApprovalStatus", return_value=blocking):
            with patch.object(olm_approvals, "waitForSubscriptionConvergence", return_value=final) as mockWait:
                result = olm_approvals.waitForSubscriptionApproval(
                    Mock(),
                    display,
                    "test-namespace",
                    packageName="test-operator",
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
        assert mockWait.call_args.kwargs["onPending"] is not None

    def test_automatic_context_runs_the_convergence_wait_too(self):
        display = Mock()
        unconverged = makeStatus(
            approvalMode="Automatic",
            pendingApprovals=[],
            subscriptions=[makeSubscriptionEntry(converged=False, installedCSV=None)],
            converged=False,
        )
        with patch.object(olm_approvals, "getNamespaceApprovalStatus", return_value=unconverged):
            with patch.object(olm_approvals, "waitForSubscriptionConvergence", return_value=unconverged) as mockWait:
                result = olm_approvals.waitForSubscriptionApproval(Mock(), display, "test-namespace", timeout=600, approvalMode="Automatic")

        # Automatic runs the same convergence wait (OLM issues the approvals
        # itself; the wait is for the resulting rollout)
        mockWait.assert_called_once()
        assert mockWait.call_args.kwargs["timeout"] == 600
        assert result["waited"] is False

    def test_package_status_is_echoed_in_the_result(self):
        display = Mock()
        entry = makeSubscriptionEntry(name="test-operator", package="test-operator")
        final = makeStatus(pendingApprovals=[], subscriptions=[entry], converged=True)
        with patch.object(olm_approvals, "getNamespaceApprovalStatus", return_value=makeStatus(pendingApprovals=[])):
            with patch.object(olm_approvals, "waitForSubscriptionConvergence", return_value=final):
                result = olm_approvals.waitForSubscriptionApproval(Mock(), display, "test-namespace", packageName="test-operator")

        assert result["packageStatus"] is entry

    def test_mixed_namespace_reported_not_fatal(self):
        display = Mock()
        blocking = makeStatus(approvalMode="Mixed", pendingApprovals=[APPROVAL])
        final = makeStatus(pendingApprovals=[])
        with patch.object(olm_approvals, "getNamespaceApprovalStatus", return_value=blocking):
            with patch.object(olm_approvals, "waitForSubscriptionConvergence", return_value=final):
                result = olm_approvals.waitForSubscriptionApproval(Mock(), display, "test-namespace", approvalMode="Manual")

        assert result is final
        displayed = " ".join(str(call.args[0]) for call in display.display.call_args_list)
        assert "mix of approval modes" in displayed

    def test_new_plan_appearing_mid_wait_gets_a_notice(self):
        display = Mock()
        blocking = makeStatus(pendingApprovals=[APPROVAL])
        final = makeStatus(pendingApprovals=[])
        with patch.object(olm_approvals, "getNamespaceApprovalStatus", return_value=blocking):
            with patch.object(olm_approvals, "waitForSubscriptionConvergence", return_value=final) as mockWait:
                olm_approvals.waitForSubscriptionApproval(Mock(), display, "test-namespace", approvalMode="Manual")

        onPending = mockWait.call_args.kwargs["onPending"]
        noticesBefore = display.display.call_count

        # A second plan appears mid-wait (a multi-step upgrade path): it gets
        # its notice too, the already-noticed plan does not get a repeat
        secondApproval = dict(APPROVAL, installPlan="install-plan-2")
        midWait = makeStatus(pendingApprovals=[APPROVAL, secondApproval], converged=False)
        assert onPending(midWait, 2) is not False

        displayed = " ".join(str(call.args[0]) for call in display.display.call_args_list[noticesBefore:])
        assert "Waiting for manual approval of install plan install-plan-2" in displayed
        assert displayed.count("Waiting for manual approval of install plan install-plan-1") == 0

    def test_late_mismatch_fails_fast_in_automatic_context(self):
        display = Mock()
        initial = makeStatus(approvalMode="Automatic", pendingApprovals=[])
        with patch.object(olm_approvals, "getNamespaceApprovalStatus", return_value=initial):
            with patch.object(olm_approvals, "waitForSubscriptionConvergence", return_value=initial) as mockWait:
                olm_approvals.waitForSubscriptionApproval(Mock(), display, "test-namespace", approvalMode=None)

        onPending = mockWait.call_args.kwargs["onPending"]

        # A plan appears after the initial snapshot (a just-created
        # Subscription's first plan): the same mismatch, caught late
        lateBlocking = makeStatus(approvalMode="Automatic", pendingApprovals=[APPROVAL], converged=False)
        with pytest.raises(ValueError, match="Install plans are waiting for manual approval"):
            onPending(lateBlocking, 1)

    def test_waited_true_when_pending_only_seen_mid_wait(self):
        display = Mock()
        initial = makeStatus(pendingApprovals=[])
        final = makeStatus(pendingApprovals=[])
        midWait = makeStatus(pendingApprovals=[APPROVAL], converged=False)

        def runWait(dynClient, namespace, timeout=None, pollInterval=30, onPending=None):
            onPending(midWait, 1)
            return final

        with patch.object(olm_approvals, "getNamespaceApprovalStatus", return_value=initial):
            with patch.object(olm_approvals, "waitForSubscriptionConvergence", side_effect=runWait):
                result = olm_approvals.waitForSubscriptionApproval(Mock(), display, "test-namespace", approvalMode="Manual")

        assert result["waited"] is True

    def test_timeout_error_repeats_approve_commands(self):
        display = Mock()
        blocking = makeStatus(pendingApprovals=[APPROVAL])
        with patch.object(olm_approvals, "getNamespaceApprovalStatus", return_value=blocking):
            with patch.object(olm_approvals, "waitForSubscriptionConvergence", side_effect=OLMTimeoutError("timed out")):
                with pytest.raises(OLMTimeoutError) as excinfo:
                    olm_approvals.waitForSubscriptionApproval(Mock(), display, "test-namespace", timeout=300, approvalMode="Manual")

        assert "Timed out after 300s" in str(excinfo.value)
        assert "oc patch installplan/install-plan-1" in str(excinfo.value)

    def test_timeout_in_automatic_context_reraises_subscription_list(self):
        display = Mock()
        unconverged = makeStatus(approvalMode="Automatic", pendingApprovals=[], subscriptions=[makeSubscriptionEntry(converged=False)], converged=False)
        with patch.object(olm_approvals, "getNamespaceApprovalStatus", return_value=unconverged):
            with patch.object(
                olm_approvals,
                "waitForSubscriptionConvergence",
                side_effect=OLMTimeoutError(
                    "Timed out after 300s waiting for Subscriptions in test-namespace to reach their channel head:\n  test-operator: v1 -> v2"
                ),
            ):
                with pytest.raises(OLMTimeoutError) as excinfo:
                    olm_approvals.waitForSubscriptionApproval(Mock(), display, "test-namespace", timeout=300, approvalMode="Automatic")

        # Automatic: the underlying per-Subscription message is re-raised
        # unchanged (there are no approve commands to repeat)
        assert "test-operator: v1 -> v2" in str(excinfo.value)

    def test_status_line_logged_on_first_poll_and_then_time_gated(self):
        display = Mock()
        blocking = makeStatus(pendingApprovals=[APPROVAL])
        final = makeStatus(pendingApprovals=[])

        with patch.object(olm_approvals, "getNamespaceApprovalStatus", return_value=blocking):
            with patch.object(olm_approvals, "waitForSubscriptionConvergence", return_value=final) as mockWait:
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

    def test_automatic_status_line_names_unconverged_subscriptions(self):
        display = Mock()
        unconverged = makeStatus(
            approvalMode="Automatic",
            pendingApprovals=[],
            subscriptions=[makeSubscriptionEntry(name="test-operator", converged=False, installedCSV=None)],
            converged=False,
        )
        with patch.object(olm_approvals, "getNamespaceApprovalStatus", return_value=unconverged):
            with patch.object(olm_approvals, "waitForSubscriptionConvergence", return_value=unconverged) as mockWait:
                olm_approvals.waitForSubscriptionApproval(Mock(), display, "test-namespace", timeout=7200, approvalMode="Automatic")

        onPending = mockWait.call_args.kwargs["onPending"]
        assert onPending(unconverged, 1) is not False
        statusLine = str(display.display.call_args.args[0])
        assert "Waiting for 1 subscription(s) in test-namespace to reach their channel head" in statusLine
        assert "test-operator" in statusLine
        assert "approval deadline" in statusLine

    def test_status_line_logged_again_after_interval(self):
        display = Mock()
        blocking = makeStatus(pendingApprovals=[APPROVAL])
        final = makeStatus(pendingApprovals=[])

        with patch.object(olm_approvals, "getNamespaceApprovalStatus", return_value=blocking):
            with patch.object(olm_approvals, "waitForSubscriptionConvergence", return_value=final) as mockWait:
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


# Made with Bob
