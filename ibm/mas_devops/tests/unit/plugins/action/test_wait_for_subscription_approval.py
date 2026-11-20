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

    @patch('wait_for_subscription_approval.get_api_client')
    @patch('wait_for_subscription_approval.waitForSubscriptionApproval')
    def test_namespace_mode_delegates_to_helper(self, mock_wait, mock_get_api_client, action_module):
        """Test the single-namespace mode passes through package and timeout"""
        mock_get_api_client.return_value = Mock()
        mock_wait.return_value = makeStatus("test-namespace", pendingApprovals=[])

        action_module._task.args = {
            'namespace': 'test-namespace',
            'package_name': 'ibm-sls',
            'timeout': 600
        }

        result = action_module.run()

        assert result['success'] is True
        assert result['failed'] is False
        assert result['changed'] is False
        assert result['namespaces'] == ['test-namespace']
        mock_wait.assert_called_once()
        assert mock_wait.call_args.kwargs['packageName'] == 'ibm-sls'
        assert mock_wait.call_args.kwargs['timeout'] == 600

    @patch('wait_for_subscription_approval.get_api_client')
    @patch('wait_for_subscription_approval.waitForSubscriptionApproval')
    def test_cluster_wide_mode_waits_for_every_namespace(self, mock_wait, mock_get_api_client, action_module):
        """Test the cluster-wide mode (no namespace) discovers and waits for each namespace"""
        mock_get_api_client.return_value = Mock()
        mock_wait.side_effect = [makeStatus("ns-a"), makeStatus("ns-b")]
        with patch('wait_for_subscription_approval.getPendingInstallPlans') as mockPending:
            mockPending.return_value = [
                {'installPlan': 'plan-2', 'namespace': 'ns-b'},
                {'installPlan': 'plan-1', 'namespace': 'ns-a'},
            ]

            action_module._task.args = {}

            result = action_module.run()

        assert result['success'] is True
        assert result['namespaces'] == ['ns-a', 'ns-b']
        # Cluster-wide waits are per namespace, in a stable order, with no package filter
        assert [call.args[2] for call in mock_wait.call_args_list] == ['ns-a', 'ns-b']
        assert all('packageName' not in call.kwargs or call.kwargs['packageName'] is None for call in mock_wait.call_args_list)

    @patch('wait_for_subscription_approval.get_api_client')
    @patch('wait_for_subscription_approval.getPendingInstallPlans')
    def test_cluster_wide_mode_with_nothing_pending(self, mock_pending, mock_get_api_client, action_module):
        """Test the cluster-wide mode is a no-op success when nothing is pending"""
        mock_get_api_client.return_value = Mock()
        mock_pending.return_value = []

        action_module._task.args = {}

        result = action_module.run()

        assert result['success'] is True
        assert 'No install plans are waiting for approval' in result['message']

    @patch('wait_for_subscription_approval.get_api_client')
    @patch('wait_for_subscription_approval.waitForSubscriptionApproval')
    def test_timeout_raises_ansible_error(self, mock_wait, mock_get_api_client, action_module):
        """Test that OLMTimeoutError is converted to an actionable AnsibleError"""
        mock_get_api_client.return_value = Mock()
        mock_wait.side_effect = OLMTimeoutError("Timed out after 300s waiting for manual install plan approval")

        action_module._task.args = {'namespace': 'test-namespace'}

        with pytest.raises(AnsibleError, match="Timed out after 300s"):
            action_module.run()

    @patch('wait_for_subscription_approval.get_api_client')
    @patch('wait_for_subscription_approval.waitForSubscriptionApproval')
    def test_olm_exception_raises_ansible_error(self, mock_wait, mock_get_api_client, action_module):
        """Test that OLMException is converted to AnsibleError"""
        mock_get_api_client.return_value = Mock()
        mock_wait.side_effect = OLMException("boom")

        action_module._task.args = {'namespace': 'test-namespace'}

        with pytest.raises(AnsibleError, match="Error waiting for install plan approval"):
            action_module.run()

    @patch('wait_for_subscription_approval.get_api_client')
    def test_invalid_approval_mode_env_raises(self, mock_get_api_client, action_module, monkeypatch):
        """Test that an invalid OLM_APPROVAL_MODE fails fast naming the env var"""
        monkeypatch.setenv('OLM_APPROVAL_MODE', 'banana')
        mock_get_api_client.return_value = Mock()

        action_module._task.args = {'namespace': 'test-namespace'}

        with pytest.raises(AnsibleError, match="OLM_APPROVAL_MODE must be one of"):
            action_module.run()

    @patch('wait_for_subscription_approval.get_api_client')
    def test_invalid_timeout_env_raises(self, mock_get_api_client, action_module, monkeypatch):
        """Test that a non-integer OLM_APPROVAL_TIMEOUT fails fast"""
        monkeypatch.setenv('OLM_APPROVAL_TIMEOUT', 'banana')
        mock_get_api_client.return_value = Mock()

        action_module._task.args = {'namespace': 'test-namespace'}

        with pytest.raises(AnsibleError, match="approval timeout must be an integer"):
            action_module.run()

# Made with Bob
