"""
Unit tests for the wait_for_subscription_approval action plugin.

The DynamicClient and the shared olm_approvals helper are mocked: these
tests cover the module's argument handling, its namespace and cluster-wide
modes, and its error translation.
"""

from unittest.mock import Mock, patch

import pytest

# Import the action module (path setup is in conftest.py)
import wait_for_subscription_approval
from ansible.errors import AnsibleError
from mas.devops.olm import OLMException, OLMTimeoutError

ActionModule = wait_for_subscription_approval.ActionModule


def makeStatus(namespace, approvalMode="Manual", pendingApprovals=None):
    pendingApprovals = pendingApprovals if pendingApprovals is not None else []
    return {
        "namespace": namespace,
        "approvalMode": approvalMode,
        "pendingApprovals": pendingApprovals,
        "blocking": len(pendingApprovals) > 0,
    }


class TestWaitForSubscriptionApproval:
    """Tests for wait_for_subscription_approval action plugin"""

    @pytest.fixture
    def action_module(self, action_module_base):
        """Create an instance of the action module for testing"""
        return ActionModule(**action_module_base)

    @patch("wait_for_subscription_approval.get_api_client")
    @patch("wait_for_subscription_approval.waitForSubscriptionApproval", autospec=True)
    def test_namespace_mode_delegates_to_helper(self, mock_wait, mock_get_api_client, action_module):
        """Test the single-namespace mode passes through package and timeout"""
        mock_get_api_client.return_value = Mock()
        mock_wait.return_value = makeStatus("test-namespace", pendingApprovals=[])

        action_module._task.args = {"namespace": "test-namespace", "package_name": "ibm-sls", "timeout": 600}

        result = action_module.run()

        assert result["success"] is True
        assert result["failed"] is False
        assert result["changed"] is False
        assert result["namespaces"] == ["test-namespace"]
        assert "No install plans are waiting for approval" in result["message"]
        mock_wait.assert_called_once()
        assert mock_wait.call_args.kwargs["packageName"] == "ibm-sls"
        assert mock_wait.call_args.kwargs["timeout"] == 600

    @patch("wait_for_subscription_approval.get_api_client")
    @patch("wait_for_subscription_approval.waitForSubscriptionApproval", autospec=True)
    def test_message_reports_granted_only_when_the_wait_actually_waited(self, mock_wait, mock_get_api_client, action_module):
        """The success message must not claim approvals were granted when nothing was ever pending"""
        mock_get_api_client.return_value = Mock()
        mock_wait.return_value = dict(makeStatus("test-namespace", pendingApprovals=[]), waited=True)

        action_module._task.args = {"namespace": "test-namespace"}

        result = action_module.run()

        assert result["success"] is True
        assert result["message"] == "All install plan approvals have been granted in: test-namespace (and all subscriptions are at their channel head)"

    @patch("wait_for_subscription_approval.get_api_client")
    @patch("wait_for_subscription_approval.waitForSubscriptionApproval", autospec=True)
    @patch("wait_for_subscription_approval.waitForClusterApproval", autospec=True)
    def test_cluster_wide_mode_delegates_to_the_cluster_helper(self, mock_cluster_wait, mock_wait, mock_get_api_client, action_module):
        """The cluster-wide mode (no namespace) is a single waitForClusterApproval call.

        The helper owns the full-scope up-front report and the unified
        multi-namespace wait (the settle-before-discover ordering is covered
        by the module_utils tests); the plugin just passes through the
        resolved timeout/poll interval and maps the result.
        """
        mock_get_api_client.return_value = Mock()
        mock_cluster_wait.return_value = {"waited": True, "namespaces": ["ns-a", "ns-b"], "statuses": {}}

        action_module._task.args = {"timeout": 600, "poll_interval": 15}

        result = action_module.run()

        assert result["success"] is True
        assert result["namespaces"] == ["ns-a", "ns-b"]
        assert result["message"] == "All install plan approvals have been granted in: ns-a, ns-b (and all subscriptions are at their channel head)"
        mock_cluster_wait.assert_called_once()
        assert mock_cluster_wait.call_args.kwargs["timeout"] == 600
        assert mock_cluster_wait.call_args.kwargs["pollInterval"] == 15
        # The per-namespace helper is not used in cluster-wide mode
        mock_wait.assert_not_called()

    @patch("wait_for_subscription_approval.get_api_client")
    @patch("wait_for_subscription_approval.waitForClusterApproval", autospec=True)
    def test_cluster_wide_mode_with_nothing_pending(self, mock_cluster_wait, mock_get_api_client, action_module):
        """Test the cluster-wide mode is a no-op success when nothing is pending"""
        mock_get_api_client.return_value = Mock()
        mock_cluster_wait.return_value = {"waited": False, "namespaces": [], "statuses": {}}

        action_module._task.args = {}

        result = action_module.run()

        assert result["success"] is True
        assert result["namespaces"] == []
        assert "No install plans are waiting for approval" in result["message"]

    @patch("wait_for_subscription_approval.get_api_client")
    @patch("wait_for_subscription_approval.waitForClusterApproval", autospec=True)
    def test_cluster_wide_mode_timeout_raises_ansible_error(self, mock_cluster_wait, mock_get_api_client, action_module):
        """Test that OLMTimeoutError from the cluster gate is converted to an actionable AnsibleError"""
        mock_get_api_client.return_value = Mock()
        mock_cluster_wait.side_effect = OLMTimeoutError("Timed out waiting for install plan approval in namespace ns-a")

        action_module._task.args = {}

        with pytest.raises(AnsibleError, match="Timed out waiting for install plan approval"):
            action_module.run()

    @patch("wait_for_subscription_approval.get_api_client")
    @patch("wait_for_subscription_approval.waitForSubscriptionApproval", autospec=True)
    def test_timeout_raises_ansible_error(self, mock_wait, mock_get_api_client, action_module):
        """Test that OLMTimeoutError is converted to an actionable AnsibleError"""
        mock_get_api_client.return_value = Mock()
        mock_wait.side_effect = OLMTimeoutError("Timed out after 300s waiting for manual install plan approval")

        action_module._task.args = {"namespace": "test-namespace"}

        with pytest.raises(AnsibleError, match="Timed out after 300s"):
            action_module.run()

    @patch("wait_for_subscription_approval.get_api_client")
    @patch("wait_for_subscription_approval.waitForSubscriptionApproval", autospec=True)
    def test_olm_exception_raises_ansible_error(self, mock_wait, mock_get_api_client, action_module):
        """Test that OLMException is converted to AnsibleError"""
        mock_get_api_client.return_value = Mock()
        mock_wait.side_effect = OLMException("boom")

        action_module._task.args = {"namespace": "test-namespace"}

        with pytest.raises(AnsibleError, match="Error waiting for install plan approval"):
            action_module.run()

    @patch("wait_for_subscription_approval.get_api_client")
    def test_invalid_approval_mode_env_raises(self, mock_get_api_client, action_module, monkeypatch):
        """Test that an invalid OLM_APPROVAL_MODE fails fast naming the env var"""
        monkeypatch.setenv("OLM_APPROVAL_MODE", "banana")
        mock_get_api_client.return_value = Mock()

        action_module._task.args = {"namespace": "test-namespace"}

        with pytest.raises(AnsibleError, match="OLM_APPROVAL_MODE must be one of"):
            action_module.run()

    @patch("wait_for_subscription_approval.get_api_client")
    def test_invalid_timeout_env_raises(self, mock_get_api_client, action_module, monkeypatch):
        """Test that a non-integer OLM_APPROVAL_TIMEOUT fails fast"""
        monkeypatch.setenv("OLM_APPROVAL_TIMEOUT", "banana")
        mock_get_api_client.return_value = Mock()

        action_module._task.args = {"namespace": "test-namespace"}

        with pytest.raises(AnsibleError, match="approval timeout must be an integer"):
            action_module.run()


# Made with Bob
