"""
Unit tests for update_global_pull_secret action plugin.

Tests the update_global_pull_secret action which updates the global pull secret
in openshift-config namespace with registry credentials.
"""

import pytest
from unittest.mock import Mock, patch
from ansible.errors import AnsibleError

import update_global_pull_secret
ActionModule = update_global_pull_secret.ActionModule


class TestUpdateGlobalPullSecret:
    """Test cases for update_global_pull_secret action plugin."""

    @pytest.fixture
    def action_module(self, action_module_base):
        """Create ActionModule instance"""
        module = ActionModule(**action_module_base)
        return module

    def test_successful_global_pull_secret_update(self, action_module, mock_display):
        """Test successful global pull secret update."""
        # Arrange
        action_module._task.args = {
            'registry_url': 'quay.io',
            'username': 'test-user',
            'password': 'test-password',
            'host': 'https://api.example.com',
            'api_key': 'test-key'
        }

        mock_result = {
            'changed': True,
            'name': 'pull-secret',
            'namespace': 'openshift-config',
            'registry': 'quay.io'
        }

        mock_client = Mock()

        # Act
        with patch('update_global_pull_secret.get_api_client', return_value=mock_client):
            with patch('update_global_pull_secret.updateGlobalPullSecret', return_value=mock_result) as mock_update:
                result = action_module.run()

        # Assert
        assert result['success'] is True
        assert result['failed'] is False
        assert result['changed'] is True
        assert 'Successfully updated global pull secret' in result['message']
        assert 'quay.io' in result['message']
        assert result['name'] == 'pull-secret'
        assert result['namespace'] == 'openshift-config'
        assert result['registry'] == 'quay.io'
        mock_update.assert_called_once_with(mock_client, 'quay.io', 'test-user', 'test-password')

    def test_missing_registry_url_raises_error(self, action_module, mock_display):
        """Test that missing registry_url raises AnsibleError."""
        # Arrange
        action_module._task.args = {
            'username': 'test-user',
            'password': 'test-password'
        }

        # Act & Assert
        with pytest.raises(AnsibleError, match="registry_url argument was not provided"):
            action_module.run()

    def test_missing_username_raises_error(self, action_module, mock_display):
        """Test that missing username raises AnsibleError."""
        # Arrange
        action_module._task.args = {
            'registry_url': 'quay.io',
            'password': 'test-password'
        }

        # Act & Assert
        with pytest.raises(AnsibleError, match="username argument was not provided"):
            action_module.run()

    def test_missing_password_raises_error(self, action_module, mock_display):
        """Test that missing password raises AnsibleError."""
        # Arrange
        action_module._task.args = {
            'registry_url': 'quay.io',
            'username': 'test-user'
        }

        # Act & Assert
        with pytest.raises(AnsibleError, match="password argument was not provided"):
            action_module.run()

    def test_with_custom_host_and_api_key(self, action_module, mock_display):
        """Test with custom Kubernetes host and API key."""
        # Arrange
        custom_host = 'https://custom.api.com:6443'
        custom_api_key = 'custom-key-123'

        action_module._task.args = {
            'registry_url': 'docker.io',
            'username': 'docker-user',
            'password': 'docker-pass',
            'host': custom_host,
            'api_key': custom_api_key
        }

        mock_result = {
            'changed': True,
            'name': 'pull-secret',
            'namespace': 'openshift-config',
            'registry': 'docker.io'
        }

        mock_client = Mock()

        # Act
        with patch('update_global_pull_secret.get_api_client', return_value=mock_client) as mock_get_client:
            with patch('update_global_pull_secret.updateGlobalPullSecret', return_value=mock_result):
                result = action_module.run()

        # Assert
        mock_get_client.assert_called_once_with(api_key=custom_api_key, host=custom_host)
        assert result['success'] is True

    def test_update_with_private_registry(self, action_module, mock_display):
        """Test update with private registry URL."""
        # Arrange
        action_module._task.args = {
            'registry_url': 'registry.private.com:5000',
            'username': 'private-user',
            'password': 'private-pass'
        }

        mock_result = {
            'changed': True,
            'name': 'pull-secret',
            'namespace': 'openshift-config',
            'registry': 'registry.private.com:5000'
        }

        mock_client = Mock()

        # Act
        with patch('update_global_pull_secret.get_api_client', return_value=mock_client):
            with patch('update_global_pull_secret.updateGlobalPullSecret', return_value=mock_result):
                result = action_module.run()

        # Assert
        assert result['success'] is True
        assert result['registry'] == 'registry.private.com:5000'
        assert 'registry.private.com:5000' in result['message']

    def test_update_with_no_changes(self, action_module, mock_display):
        """Test update when no changes are made (secret already exists)."""
        # Arrange
        action_module._task.args = {
            'registry_url': 'quay.io',
            'username': 'test-user',
            'password': 'test-password'
        }

        mock_result = {
            'changed': False,
            'name': 'pull-secret',
            'namespace': 'openshift-config',
            'registry': 'quay.io'
        }

        mock_client = Mock()

        # Act
        with patch('update_global_pull_secret.get_api_client', return_value=mock_client):
            with patch('update_global_pull_secret.updateGlobalPullSecret', return_value=mock_result):
                result = action_module.run()

        # Assert
        assert result['success'] is True
        assert result['failed'] is False
        assert result['changed'] is False

    def test_update_with_minimal_result(self, action_module, mock_display):
        """Test update when result has minimal fields."""
        # Arrange
        action_module._task.args = {
            'registry_url': 'quay.io',
            'username': 'test-user',
            'password': 'test-password'
        }

        # Result with missing optional fields
        mock_result = {}

        mock_client = Mock()

        # Act
        with patch('update_global_pull_secret.get_api_client', return_value=mock_client):
            with patch('update_global_pull_secret.updateGlobalPullSecret', return_value=mock_result):
                result = action_module.run()

        # Assert
        assert result['success'] is True
        assert result['failed'] is False
        assert result['changed'] is True  # Default when not in result
        assert result['name'] is None
        assert result['namespace'] is None
        assert result['registry'] is None

# Made with Bob
