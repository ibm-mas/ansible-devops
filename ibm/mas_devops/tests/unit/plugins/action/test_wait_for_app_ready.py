"""
Unit tests for wait_for_app_ready action plugin.
"""

import pytest
from unittest.mock import Mock, patch
from ansible.errors import AnsibleError

import wait_for_app_ready
ActionModule = wait_for_app_ready.ActionModule


class TestWaitForAppReady:
    """Test cases for wait_for_app_ready action plugin."""

    @pytest.fixture
    def action_module(self, action_module_base):
        """Create ActionModule instance"""
        module = ActionModule(**action_module_base)
        return module

    def test_app_ready_without_workspace(self, action_module, mock_display):
        """Test when app is ready without workspace ID."""
        # Arrange
        action_module._task.args = {
            'host': 'https://api.example.com',
            'api_key': 'test-key',
            'instance_id': 'inst1',
            'application_id': 'manage',
            'retries': 50,
            'delay': 60
        }

        mock_client = Mock()

        # Act
        with patch('wait_for_app_ready.get_api_client', return_value=mock_client):
            with patch('wait_for_app_ready.waitForAppReady', return_value=True) as mock_wait:
                result = action_module.run()

        # Assert
        assert result['success'] is True
        assert result['changed'] is False
        assert 'inst1/manage' in result['message']
        assert 'is ready' in result['message']
        mock_wait.assert_called_once()

    def test_app_ready_with_workspace(self, action_module, mock_display):
        """Test when app is ready with workspace ID."""
        # Arrange
        action_module._task.args = {
            'instance_id': 'inst1',
            'application_id': 'manage',
            'workspace_id': 'ws1',
            'retries': 50,
            'delay': 60
        }

        mock_client = Mock()

        # Act
        with patch('wait_for_app_ready.get_api_client', return_value=mock_client):
            with patch('wait_for_app_ready.waitForAppReady', return_value=True) as mock_wait:
                result = action_module.run()

        # Assert
        assert result['success'] is True
        assert result['changed'] is False
        assert 'inst1/manage-ws1' in result['message']
        # Verify function was called with correct parameters (don't check display functions)
        call_args = mock_wait.call_args
        assert call_args.kwargs['dynClient'] == mock_client
        assert call_args.kwargs['instanceId'] == 'inst1'
        assert call_args.kwargs['applicationId'] == 'manage'
        assert call_args.kwargs['workspaceId'] == 'ws1'
        assert call_args.kwargs['retries'] == 50
        assert call_args.kwargs['delay'] == 60

    def test_app_not_ready(self, action_module, mock_display):
        """Test when app is not ready after retries."""
        # Arrange
        action_module._task.args = {
            'instance_id': 'inst1',
            'application_id': 'manage',
            'retries': 10,
            'delay': 30
        }

        mock_client = Mock()

        # Act
        with patch('wait_for_app_ready.get_api_client', return_value=mock_client):
            with patch('wait_for_app_ready.waitForAppReady', return_value=False):
                result = action_module.run()

        # Assert
        assert result['success'] is False
        assert result['changed'] is False
        assert 'is not ready' in result['message']

    def test_missing_instance_id_raises_error(self, action_module, mock_display):
        """Test that missing instance_id raises AnsibleError."""
        # Arrange
        action_module._task.args = {
            'application_id': 'manage'
        }

        # Act & Assert
        with pytest.raises(AnsibleError, match="instance_id argument was not provided"):
            action_module.run()

    def test_missing_application_id_raises_error(self, action_module, mock_display):
        """Test that missing application_id raises AnsibleError."""
        # Arrange
        action_module._task.args = {
            'instance_id': 'inst1'
        }

        # Act & Assert
        with pytest.raises(AnsibleError, match="application_id argument was not provided"):
            action_module.run()

    def test_default_retries_and_delay(self, action_module, mock_display):
        """Test that default retries and delay values are used."""
        # Arrange
        action_module._task.args = {
            'instance_id': 'inst1',
            'application_id': 'manage'
            # retries and delay not provided, should use defaults
        }

        mock_client = Mock()

        # Act
        with patch('wait_for_app_ready.get_api_client', return_value=mock_client):
            with patch('wait_for_app_ready.waitForAppReady', return_value=True) as mock_wait:
                result = action_module.run()

        # Assert
        assert result['success'] is True
        # Verify defaults were used (50 retries, 60 delay)
        call_args = mock_wait.call_args
        assert call_args.kwargs['retries'] == 50
        assert call_args.kwargs['delay'] == 60

    def test_custom_retries_and_delay(self, action_module, mock_display):
        """Test with custom retries and delay values."""
        # Arrange
        action_module._task.args = {
            'instance_id': 'inst1',
            'application_id': 'manage',
            'retries': 100,
            'delay': 120
        }

        mock_client = Mock()

        # Act
        with patch('wait_for_app_ready.get_api_client', return_value=mock_client):
            with patch('wait_for_app_ready.waitForAppReady', return_value=True) as mock_wait:
                result = action_module.run()

        # Assert
        assert result['success'] is True
        call_args = mock_wait.call_args
        assert call_args.kwargs['retries'] == 100
        assert call_args.kwargs['delay'] == 120

    def test_with_custom_host_and_api_key(self, action_module, mock_display):
        """Test with custom Kubernetes host and API key."""
        # Arrange
        custom_host = 'https://custom.api.com:6443'
        custom_api_key = 'custom-key-123'

        action_module._task.args = {
            'host': custom_host,
            'api_key': custom_api_key,
            'instance_id': 'inst1',
            'application_id': 'manage'
        }

        mock_client = Mock()

        # Act
        with patch('wait_for_app_ready.get_api_client', return_value=mock_client) as mock_get_client:
            with patch('wait_for_app_ready.waitForAppReady', return_value=True):
                result = action_module.run()

        # Assert
        mock_get_client.assert_called_once_with(api_key=custom_api_key, host=custom_host)
        assert result['success'] is True

# Made with Bob
