"""
Unit tests for update_ibm_entitlement action plugin.

This module tests the update_ibm_entitlement action which creates/updates
IBM entitlement secrets in Kubernetes namespaces.

Note: These tests use REAL mas.devops.ocp.createNamespace() and
mas.devops.mas.updateIBMEntitlementKey() functions. We only mock the
Kubernetes API client.
"""

import pytest
from unittest.mock import Mock, patch
from ansible.errors import AnsibleError

# Import the action module
import update_ibm_entitlement
ActionModule = update_ibm_entitlement.ActionModule


class TestUpdateIBMEntitlement:
    """Test cases for update_ibm_entitlement action plugin."""

    @pytest.fixture
    def action_module(self, action_module_base):
        """Create ActionModule instance"""
        module = ActionModule(**action_module_base)
        return module

    def test_successful_entitlement_update_with_icr_credentials(self, action_module, mock_display):
        """Test successful entitlement update with ICR credentials."""
        # Arrange
        action_module._task.args = {
            'namespace': 'mas-core',
            'icr_username': 'cp',
            'icr_password': 'test-entitlement-key',
            'host': 'https://api.example.com',
            'api_key': 'test-key'
        }

        # Mock secret returned by updateIBMEntitlementKey
        mock_secret = Mock()
        mock_secret.metadata.name = 'ibm-entitlement'
        mock_secret.to_dict.return_value = {
            'metadata': {'name': 'ibm-entitlement', 'namespace': 'mas-core'},
            'type': 'kubernetes.io/dockerconfigjson'
        }

        mock_client = Mock()

        # Act
        with patch('update_ibm_entitlement.get_api_client', return_value=mock_client):
            with patch('update_ibm_entitlement.createNamespace') as mock_create_ns:
                with patch('update_ibm_entitlement.updateIBMEntitlementKey', return_value=mock_secret) as mock_update:
                    result = action_module.run()

        # Assert
        assert result['success'] is True
        assert result['failed'] is False
        assert result['changed'] is False
        assert 'Successfully updated IBM entitlement in mas-core' in result['message']
        assert 'ibm-entitlement' in result['message']
        assert result['metadata']['name'] == 'ibm-entitlement'

        # Verify real functions were called
        mock_create_ns.assert_called_once_with(mock_client, 'mas-core', None)
        mock_update.assert_called_once_with(
            mock_client, 'mas-core', 'cp', 'test-entitlement-key',
            None, None, None
        )

    def test_successful_entitlement_update_with_artifactory_credentials(self, action_module, mock_display):
        """Test successful entitlement update with Artifactory credentials."""
        # Arrange
        action_module._task.args = {
            'namespace': 'mas-core',
            'icr_username': 'cp',
            'icr_password': 'test-entitlement-key',
            'artifactory_username': 'art-user',
            'artifactory_password': 'art-token',
            'host': 'https://api.example.com',
            'api_key': 'test-key'
        }

        mock_secret = Mock()
        mock_secret.metadata.name = 'ibm-entitlement'
        mock_secret.to_dict.return_value = {
            'metadata': {'name': 'ibm-entitlement', 'namespace': 'mas-core'}
        }

        mock_client = Mock()

        # Act
        with patch('update_ibm_entitlement.get_api_client', return_value=mock_client):
            with patch('update_ibm_entitlement.createNamespace'):
                with patch('update_ibm_entitlement.updateIBMEntitlementKey', return_value=mock_secret) as mock_update:
                    result = action_module.run()

        # Assert
        assert result['success'] is True
        assert result['failed'] is False
        mock_update.assert_called_once_with(
            mock_client, 'mas-core', 'cp', 'test-entitlement-key',
            'art-user', 'art-token', None
        )

    def test_successful_entitlement_update_with_custom_secret_name(self, action_module, mock_display):
        """Test successful entitlement update with custom secret name."""
        # Arrange
        action_module._task.args = {
            'namespace': 'mas-core',
            'icr_username': 'cp',
            'icr_password': 'test-entitlement-key',
            'secret_name': 'custom-entitlement-secret',
            'host': 'https://api.example.com',
            'api_key': 'test-key'
        }

        mock_secret = Mock()
        mock_secret.metadata.name = 'custom-entitlement-secret'
        mock_secret.to_dict.return_value = {
            'metadata': {'name': 'custom-entitlement-secret', 'namespace': 'mas-core'}
        }

        mock_client = Mock()

        # Act
        with patch('update_ibm_entitlement.get_api_client', return_value=mock_client):
            with patch('update_ibm_entitlement.createNamespace'):
                with patch('update_ibm_entitlement.updateIBMEntitlementKey', return_value=mock_secret) as mock_update:
                    result = action_module.run()

        # Assert
        assert result['success'] is True
        assert 'custom-entitlement-secret' in result['message']
        mock_update.assert_called_once_with(
            mock_client, 'mas-core', 'cp', 'test-entitlement-key',
            None, None, 'custom-entitlement-secret'
        )

    def test_successful_entitlement_update_with_kyverno_label(self, action_module, mock_display):
        """Test successful entitlement update with Kyverno namespace label."""
        # Arrange
        action_module._task.args = {
            'namespace': 'mas-core',
            'icr_username': 'cp',
            'icr_password': 'test-entitlement-key',
            'namespace_kyverno_label': 'audit',
            'host': 'https://api.example.com',
            'api_key': 'test-key'
        }

        mock_secret = Mock()
        mock_secret.metadata.name = 'ibm-entitlement'
        mock_secret.to_dict.return_value = {
            'metadata': {'name': 'ibm-entitlement', 'namespace': 'mas-core'}
        }

        mock_client = Mock()

        # Act
        with patch('update_ibm_entitlement.get_api_client', return_value=mock_client):
            with patch('update_ibm_entitlement.createNamespace') as mock_create_ns:
                with patch('update_ibm_entitlement.updateIBMEntitlementKey', return_value=mock_secret):
                    result = action_module.run()

        # Assert
        assert result['success'] is True
        mock_create_ns.assert_called_once_with(mock_client, 'mas-core', 'audit')

    def test_missing_namespace_raises_error(self, action_module, mock_display):
        """Test that missing namespace parameter raises AnsibleError."""
        # Arrange
        action_module._task.args = {
            'icr_username': 'cp',
            'icr_password': 'test-entitlement-key'
        }

        # Act & Assert
        with pytest.raises(AnsibleError, match="namespace argument was not provided"):
            action_module.run()

    def test_with_custom_host_and_api_key(self, action_module, mock_display):
        """Test with custom Kubernetes host and API key."""
        # Arrange
        custom_host = 'https://custom.api.com:6443'
        custom_api_key = 'custom-key-123'

        action_module._task.args = {
            'namespace': 'mas-core',
            'icr_username': 'cp',
            'icr_password': 'test-entitlement-key',
            'host': custom_host,
            'api_key': custom_api_key
        }

        mock_secret = Mock()
        mock_secret.metadata.name = 'ibm-entitlement'
        mock_secret.to_dict.return_value = {
            'metadata': {'name': 'ibm-entitlement', 'namespace': 'mas-core'}
        }

        mock_client = Mock()

        # Act
        with patch('update_ibm_entitlement.get_api_client', return_value=mock_client) as mock_get_client:
            with patch('update_ibm_entitlement.createNamespace'):
                with patch('update_ibm_entitlement.updateIBMEntitlementKey', return_value=mock_secret):
                    result = action_module.run()

        # Assert
        mock_get_client.assert_called_once_with(api_key=custom_api_key, host=custom_host)
        assert result['success'] is True

    def test_entitlement_update_with_all_parameters(self, action_module, mock_display):
        """Test entitlement update with all optional parameters."""
        # Arrange
        action_module._task.args = {
            'namespace': 'mas-core',
            'icr_username': 'cp',
            'icr_password': 'test-entitlement-key',
            'artifactory_username': 'art-user',
            'artifactory_password': 'art-token',
            'secret_name': 'custom-secret',
            'namespace_kyverno_label': 'enforce',
            'host': 'https://api.example.com',
            'api_key': 'test-key'
        }

        mock_secret = Mock()
        mock_secret.metadata.name = 'custom-secret'
        mock_secret.to_dict.return_value = {
            'metadata': {'name': 'custom-secret', 'namespace': 'mas-core'},
            'type': 'kubernetes.io/dockerconfigjson',
            'data': {'dockerconfigjson': 'base64-encoded-data'}
        }

        mock_client = Mock()

        # Act
        with patch('update_ibm_entitlement.get_api_client', return_value=mock_client):
            with patch('update_ibm_entitlement.createNamespace') as mock_create_ns:
                with patch('update_ibm_entitlement.updateIBMEntitlementKey', return_value=mock_secret) as mock_update:
                    result = action_module.run()

        # Assert
        assert result['success'] is True
        assert result['failed'] is False
        assert result['metadata']['name'] == 'custom-secret'
        assert result['type'] == 'kubernetes.io/dockerconfigjson'

        # Verify all parameters were passed correctly
        mock_create_ns.assert_called_once_with(mock_client, 'mas-core', 'enforce')
        mock_update.assert_called_once_with(
            mock_client, 'mas-core', 'cp', 'test-entitlement-key',
            'art-user', 'art-token', 'custom-secret'
        )

    def test_entitlement_update_without_optional_credentials(self, action_module, mock_display):
        """Test entitlement update with only required ICR credentials."""
        # Arrange
        action_module._task.args = {
            'namespace': 'mas-core',
            'icr_username': 'cp',
            'icr_password': 'test-entitlement-key'
        }

        mock_secret = Mock()
        mock_secret.metadata.name = 'ibm-entitlement'
        mock_secret.to_dict.return_value = {
            'metadata': {'name': 'ibm-entitlement', 'namespace': 'mas-core'}
        }

        mock_client = Mock()

        # Act
        with patch('update_ibm_entitlement.get_api_client', return_value=mock_client):
            with patch('update_ibm_entitlement.createNamespace'):
                with patch('update_ibm_entitlement.updateIBMEntitlementKey', return_value=mock_secret) as mock_update:
                    result = action_module.run()

        # Assert
        assert result['success'] is True
        # Verify None values passed for optional parameters
        mock_update.assert_called_once_with(
            mock_client, 'mas-core', 'cp', 'test-entitlement-key',
            None, None, None
        )

# Made with Bob
