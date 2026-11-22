"""
Unit tests for apply_subscription action plugin.

Tests cover:
- Successful subscription creation
- Missing required parameters
- Invalid parameter types
- OLMException handling
- Different install modes
- Optional catalog source parameters

Note: This test uses the REAL mas.devops.olm.applySubscription() function.
We mock the Kubernetes DynamicClient but use the real function logic.
"""
from unittest.mock import Mock, patch

# Import the action module (path setup is in conftest.py)
import apply_subscription
import pytest
from ansible.errors import AnsibleError

ActionModule = apply_subscription.ActionModule

# Import mock helpers
import kubernetes_mocks


@pytest.fixture(autouse=True)
def no_existing_subscription():
    """Default the managed-subscription mismatch lookup to 'no existing
    subscription' for every test: the mismatch check now runs on every call
    (even with no approval mode set), and the mock DynamicClient's
    auto-attributes would otherwise look like a mismatching subscription.
    Tests that exercise the mismatch check patch getSubscription themselves
    (an inner patch takes precedence over this one)."""
    with patch('apply_subscription.getSubscription', return_value=None):
        yield


class TestApplySubscription:
    """Tests for apply_subscription action plugin"""

    @pytest.fixture
    def action_module(self, action_module_base):
        """Create an instance of the action module for testing"""
        module = ActionModule(**action_module_base)
        return module

    @patch('apply_subscription.get_api_client')
    @patch('apply_subscription.applySubscription')
    def test_successful_subscription_creation(self, mock_apply_sub, mock_get_api_client, action_module):
        """Test successful subscription creation"""
        # Arrange
        mock_client = kubernetes_mocks.create_mock_dynamic_client()
        mock_get_api_client.return_value = mock_client

        mock_subscription = kubernetes_mocks.create_mock_subscription(
            name='ibm-sls-sub',
            namespace='test-namespace',
            state='AtLatestKnown'
        )
        mock_apply_sub.return_value = mock_subscription

        action_module._task.args = {
            'namespace': 'test-namespace',
            'package_name': 'ibm-sls',
            'package_channel': '3.x'
        }

        # Act
        result = action_module.run()

        # Assert
        assert result['success'] is True
        assert result['failed'] is False
        assert result['changed'] is False
        assert 'Successfully applied subscription' in result['message']
        assert 'ibm-sls' in result['message']
        mock_apply_sub.assert_called_once()

    def test_missing_namespace_raises_error(self, action_module):
        """Test that missing namespace parameter raises AnsibleError"""
        # Arrange
        action_module._task.args = {
            'package_name': 'ibm-sls',
            'package_channel': '3.x'
        }

        # Act & Assert
        with pytest.raises(AnsibleError, match="namespace argument was not provided"):
            action_module.run()

    def test_invalid_package_name_type_raises_error(self, action_module):
        """Test that non-string package_name raises AnsibleError"""
        # Arrange
        action_module._task.args = {
            'namespace': 'test-namespace',
            'package_name': 123,  # Invalid: not a string
            'package_channel': '3.x'
        }

        # Act & Assert
        with pytest.raises(AnsibleError, match="packageName argument is not a string"):
            action_module.run()

    @patch('apply_subscription.get_api_client')
    @patch('apply_subscription.applySubscription')
    def test_with_custom_install_mode(self, mock_apply_sub, mock_get_api_client, action_module):
        """Test subscription with AllNamespaces install mode"""
        # Arrange
        mock_client = kubernetes_mocks.create_mock_dynamic_client()
        mock_get_api_client.return_value = mock_client

        mock_subscription = kubernetes_mocks.create_mock_subscription(
            name='ibm-mas-sub',
            namespace='test-namespace',
            state='AtLatestKnown'
        )
        mock_apply_sub.return_value = mock_subscription

        action_module._task.args = {
            'namespace': 'test-namespace',
            'package_name': 'ibm-mas',
            'package_channel': '8.x',
            'install_mode': 'AllNamespaces'
        }

        # Act
        result = action_module.run()

        # Assert
        assert result['success'] is True
        assert 'AllNamespaces' in result['message']
        # Verify applySubscription was called with correct install mode
        call_args = mock_apply_sub.call_args
        assert call_args[0][7] == 'AllNamespaces'  # installMode is 8th argument

    @patch('apply_subscription.get_api_client')
    @patch('apply_subscription.applySubscription')
    def test_with_catalog_source_parameters(self, mock_apply_sub, mock_get_api_client, action_module):
        """Test subscription with custom catalog source"""
        # Arrange
        mock_client = kubernetes_mocks.create_mock_dynamic_client()
        mock_get_api_client.return_value = mock_client

        mock_subscription = kubernetes_mocks.create_mock_subscription(
            name='custom-sub',
            namespace='test-namespace',
            state='AtLatestKnown'
        )
        mock_apply_sub.return_value = mock_subscription

        action_module._task.args = {
            'namespace': 'test-namespace',
            'package_name': 'custom-operator',
            'package_channel': '1.x',
            'catalog_source': 'custom-catalog',
            'catalog_source_namespace': 'openshift-marketplace'
        }

        # Act
        result = action_module.run()

        # Assert
        assert result['success'] is True
        # Verify catalog source parameters were passed
        call_args = mock_apply_sub.call_args
        assert call_args[0][4] == 'custom-catalog'  # catalogSource
        assert call_args[0][5] == 'openshift-marketplace'  # catalogSourceNamespace

    @patch('apply_subscription.get_api_client')
    @patch('apply_subscription.applySubscription')
    def test_olm_exception_raises_ansible_error(self, mock_apply_sub, mock_get_api_client, action_module):
        """Test that OLMException is converted to AnsibleError"""
        # Arrange
        mock_client = kubernetes_mocks.create_mock_dynamic_client()
        mock_get_api_client.return_value = mock_client

        from mas.devops.olm import OLMException
        mock_apply_sub.side_effect = OLMException("Subscription creation failed")

        action_module._task.args = {
            'namespace': 'test-namespace',
            'package_name': 'ibm-sls',
            'package_channel': '3.x'
        }

        # Act & Assert
        with pytest.raises(AnsibleError, match="Error applying subscription"):
            action_module.run()

    @patch('apply_subscription.get_api_client')
    @patch('apply_subscription.applySubscription')
    def test_none_subscription_returns_failure(self, mock_apply_sub, mock_get_api_client, action_module):
        """Test that None subscription result returns failure"""
        # Arrange
        mock_client = kubernetes_mocks.create_mock_dynamic_client()
        mock_get_api_client.return_value = mock_client

        mock_apply_sub.return_value = None

        action_module._task.args = {
            'namespace': 'test-namespace',
            'package_name': 'ibm-sls',
            'package_channel': '3.x'
        }

        # Act
        result = action_module.run()

        # Assert
        assert result['success'] is False
        assert result['failed'] is True
        assert result['changed'] is False
        assert 'Failed to apply subscription' in result['message']

    @patch('apply_subscription.get_api_client')
    @patch('apply_subscription.applySubscription')
    def test_with_config_parameter(self, mock_apply_sub, mock_get_api_client, action_module):
        """Test subscription with config parameter"""
        # Arrange
        mock_client = kubernetes_mocks.create_mock_dynamic_client()
        mock_get_api_client.return_value = mock_client

        mock_subscription = kubernetes_mocks.create_mock_subscription(
            name='configured-sub',
            namespace='test-namespace',
            state='AtLatestKnown'
        )
        mock_apply_sub.return_value = mock_subscription

        config_data = {'key': 'value'}
        action_module._task.args = {
            'namespace': 'test-namespace',
            'package_name': 'ibm-mas',
            'package_channel': '8.x',
            'config': config_data
        }

        # Act
        result = action_module.run()

        # Assert
        assert result['success'] is True
        # Verify config was passed
        call_args = mock_apply_sub.call_args
        assert call_args[0][6] == config_data  # config is 7th argument

    @patch('apply_subscription.get_api_client')
    @patch('apply_subscription.applySubscription')
    def test_default_path_does_not_opt_in_to_new_style(self, mock_apply_sub, mock_get_api_client, action_module):
        """Regression: with no approval mode set (no arg, no env var) the library
        call keeps its legacy shape -- no new-style approval handling kwargs"""
        mock_get_api_client.return_value = kubernetes_mocks.create_mock_dynamic_client()
        mock_apply_sub.return_value = kubernetes_mocks.create_mock_subscription(
            name='ibm-sls-sub', namespace='test-namespace', state='AtLatestKnown'
        )

        action_module._task.args = {
            'namespace': 'test-namespace',
            'package_name': 'ibm-sls',
            'package_channel': '3.x'
        }

        result = action_module.run()

        assert result['success'] is True
        kwargs = mock_apply_sub.call_args.kwargs
        assert 'onApprovalRequired' not in kwargs
        assert 'autoApproveInitialInstall' not in kwargs
        # With no mode requested the effective mode defaults to Automatic,
        # and it is passed through explicitly
        assert kwargs['installPlanApproval'] == 'Automatic'

    @patch('apply_subscription.get_api_client')
    @patch('apply_subscription.applySubscription')
    def test_manual_mode_from_env_uses_release_and_waits(self, mock_apply_sub, mock_get_api_client, action_module, monkeypatch):
        """Manual mode from OLM_APPROVAL_MODE: applySubscription releases when an
        install plan is pending and the module waits for the human approval"""
        monkeypatch.setenv('OLM_APPROVAL_MODE', 'Manual')
        mock_get_api_client.return_value = kubernetes_mocks.create_mock_dynamic_client()

        subscription = kubernetes_mocks.create_mock_subscription(
            name='ibm-sls-sub', namespace='test-namespace', state='UpgradePending'
        )
        approvalInfo = {
            'installPlan': 'install-plan-1',
            'namespace': 'test-namespace',
            'subscription': 'ibm-sls-sub',
            'package': 'ibm-sls',
            'csvNames': ['ibm-sls.v3.8.0'],
            'currentCSV': None,
            'targetCSV': 'ibm-sls.v3.8.0',
            'created': '2026-11-15T10:00:00Z',
        }
        mock_apply_sub.return_value = (subscription, approvalInfo)

        action_module._task.args = {
            'namespace': 'test-namespace',
            'package_name': 'ibm-sls',
            'package_channel': '3.x'
        }

        with patch('apply_subscription.waitForSubscriptionApproval') as mock_wait:
            result = action_module.run()

        assert result['success'] is True
        kwargs = mock_apply_sub.call_args.kwargs
        assert kwargs['installPlanApproval'] == 'Manual'
        assert kwargs['onApprovalRequired'] == 'return'
        mock_wait.assert_called_once()
        assert mock_wait.call_args.kwargs['packageName'] == 'ibm-sls'
        assert mock_wait.call_args.kwargs['targetCSV'] == 'ibm-sls.v3.8.0'
        assert mock_wait.call_args.kwargs['approvalMode'] == 'Manual'

    @patch('apply_subscription.get_api_client')
    @patch('apply_subscription.applySubscription')
    def test_manual_mode_without_starting_csv_no_longer_fatal(self, mock_apply_sub, mock_get_api_client, action_module, monkeypatch):
        """Manual mode without starting_csv is now supported (the module waits for
        approval instead of requiring a starting_csv to auto-approve)"""
        monkeypatch.setenv('OLM_APPROVAL_MODE', 'Manual')
        mock_get_api_client.return_value = kubernetes_mocks.create_mock_dynamic_client()
        mock_apply_sub.return_value = kubernetes_mocks.create_mock_subscription(
            name='ibm-sls-sub', namespace='test-namespace', state='AtLatestKnown'
        )

        action_module._task.args = {
            'namespace': 'test-namespace',
            'package_name': 'ibm-sls',
            'package_channel': '3.x'
        }

        result = action_module.run()

        assert result['success'] is True

    @patch('apply_subscription.get_api_client')
    @patch('apply_subscription.applySubscription')
    def test_approval_mode_arg_overrides_env(self, mock_apply_sub, mock_get_api_client, action_module, monkeypatch):
        """An explicit install_plan_approval argument wins over OLM_APPROVAL_MODE,
        keeping legacy call shape for Automatic"""
        monkeypatch.setenv('OLM_APPROVAL_MODE', 'Manual')
        mock_get_api_client.return_value = kubernetes_mocks.create_mock_dynamic_client()
        mock_apply_sub.return_value = kubernetes_mocks.create_mock_subscription(
            name='ibm-sls-sub', namespace='test-namespace', state='AtLatestKnown'
        )

        action_module._task.args = {
            'namespace': 'test-namespace',
            'package_name': 'ibm-sls',
            'package_channel': '3.x',
            'install_plan_approval': 'Automatic'
        }

        result = action_module.run()

        assert result['success'] is True
        kwargs = mock_apply_sub.call_args.kwargs
        assert kwargs['installPlanApproval'] == 'Automatic'
        assert 'onApprovalRequired' not in kwargs

    @patch('apply_subscription.get_api_client')
    def test_invalid_approval_mode_env_raises(self, mock_get_api_client, action_module, monkeypatch):
        """An invalid OLM_APPROVAL_MODE fails fast, naming the env var"""
        monkeypatch.setenv('OLM_APPROVAL_MODE', 'banana')
        mock_get_api_client.return_value = kubernetes_mocks.create_mock_dynamic_client()

        action_module._task.args = {
            'namespace': 'test-namespace',
            'package_name': 'ibm-sls',
            'package_channel': '3.x'
        }

        with pytest.raises(AnsibleError, match="OLM_APPROVAL_MODE must be one of"):
            action_module.run()

    @patch('apply_subscription.get_api_client')
    @patch('apply_subscription.applySubscription')
    def test_approval_mode_mismatch_with_existing_subscription(self, mock_apply_sub, mock_get_api_client, action_module, monkeypatch):
        """OLM_APPROVAL_MODE conflicting with the existing subscription for the
        package fails fast (managed-subscription mismatch check)"""
        monkeypatch.setenv('OLM_APPROVAL_MODE', 'Automatic')
        mock_get_api_client.return_value = kubernetes_mocks.create_mock_dynamic_client()

        existing = Mock()
        existing.metadata.name = 'ibm-sls-sub'
        existing.spec.installPlanApproval = 'Manual'

        action_module._task.args = {
            'namespace': 'test-namespace',
            'package_name': 'ibm-sls',
            'package_channel': '3.x'
        }

        with patch('apply_subscription.getSubscription', return_value=existing):
            with pytest.raises(AnsibleError, match="approval mode mismatch for ibm-sls in test-namespace"):
                action_module.run()

        mock_apply_sub.assert_not_called()

    @patch('apply_subscription.get_api_client')
    @patch('apply_subscription.applySubscription')
    def test_mismatch_check_runs_when_mode_unset(self, mock_apply_sub, mock_get_api_client, action_module):
        """With no approval mode requested (default Automatic) an existing
        Manual subscription for the package still fails fast -- this is the
        slow-fail-to-fast-fail bug fix"""
        mock_get_api_client.return_value = kubernetes_mocks.create_mock_dynamic_client()
        mock_apply_sub.return_value = kubernetes_mocks.create_mock_subscription(
            name='ibm-sls-sub', namespace='test-namespace', state='AtLatestKnown'
        )

        existing = Mock()
        existing.metadata.name = 'ibm-sls-sub'
        existing.spec.installPlanApproval = 'Manual'

        action_module._task.args = {
            'namespace': 'test-namespace',
            'package_name': 'ibm-sls',
            'package_channel': '3.x'
        }

        with patch('apply_subscription.getSubscription', return_value=existing):
            with pytest.raises(AnsibleError, match="approval mode is not set \\(default 'Automatic'\\)"):
                action_module.run()

        mock_apply_sub.assert_not_called()


# Made with Bob

    @patch('apply_subscription.get_api_client')
    @patch('apply_subscription.applySubscription')
    def test_manual_mode_preserves_existing_automatic_subscription(self, mock_apply_sub, mock_get_api_client, action_module, monkeypatch):
        """A resolved Manual mode over an existing Automatic subscription warns
        and preserves the subscription's Automatic mode (it keeps rolling
        freely) instead of failing -- this is what keeps mixed-approval
        clusters updatable"""
        monkeypatch.setenv('OLM_APPROVAL_MODE', 'Manual')
        mock_get_api_client.return_value = kubernetes_mocks.create_mock_dynamic_client()
        mock_apply_sub.return_value = kubernetes_mocks.create_mock_subscription(
            name='ibm-sls-sub', namespace='test-namespace', state='AtLatestKnown'
        )

        existing = Mock()
        existing.metadata.name = 'ibm-sls-sub'
        existing.spec.installPlanApproval = 'Automatic'

        action_module._task.args = {
            'namespace': 'test-namespace',
            'package_name': 'ibm-sls',
            'package_channel': '3.x'
        }

        with patch('apply_subscription.getSubscription', return_value=existing):
            with patch('apply_subscription.Display') as mock_display:
                result = action_module.run()

        assert result['success'] is True
        # The warning explains the preserve decision
        mock_display.return_value.warning.assert_called_once()
        warningText = mock_display.return_value.warning.call_args[0][0]
        assert 'preserving the subscription\'s Automatic approval mode' in warningText
        # The subscription is applied with its existing Automatic mode and the
        # legacy (non-waiting) call shape
        kwargs = mock_apply_sub.call_args.kwargs
        assert kwargs['installPlanApproval'] == 'Automatic'
        assert 'onApprovalRequired' not in kwargs

    @patch('apply_subscription.get_api_client')
    @patch('apply_subscription.applySubscription')
    def test_explicit_arg_conflicting_with_existing_subscription_fails(self, mock_apply_sub, mock_get_api_client, action_module):
        """An explicit install_plan_approval argument is imposing: it fails on
        conflict in either direction (here Manual over an existing Automatic
        subscription, which a resolved Manual mode would have preserved)"""
        mock_get_api_client.return_value = kubernetes_mocks.create_mock_dynamic_client()
        mock_apply_sub.return_value = kubernetes_mocks.create_mock_subscription(
            name='ibm-sls-sub', namespace='test-namespace', state='AtLatestKnown'
        )

        existing = Mock()
        existing.metadata.name = 'ibm-sls-sub'
        existing.spec.installPlanApproval = 'Automatic'

        action_module._task.args = {
            'namespace': 'test-namespace',
            'package_name': 'ibm-sls',
            'package_channel': '3.x',
            'install_plan_approval': 'Manual'
        }

        with patch('apply_subscription.getSubscription', return_value=existing):
            with pytest.raises(AnsibleError, match="install_plan_approval is set to 'Manual'"):
                action_module.run()

        mock_apply_sub.assert_not_called()
