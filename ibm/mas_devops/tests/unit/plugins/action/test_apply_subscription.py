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
import pytest
from unittest.mock import Mock, patch
from ansible.errors import AnsibleError

# Import the action module (path setup is in conftest.py)
import apply_subscription
ActionModule = apply_subscription.ActionModule

# Import mock helpers
import kubernetes_mocks


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


# Made with Bob