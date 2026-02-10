"""
Unit tests for verify_app_version action plugin.
"""

import pytest
from unittest.mock import Mock, patch
from ansible.errors import AnsibleError

import verify_app_version
ActionModule = verify_app_version.ActionModule


class TestVerifyAppVersion:
    """Test cases for verify_app_version action plugin."""

    @pytest.fixture
    def action_module(self, action_module_base):
        """Create ActionModule instance"""
        module = ActionModule(**action_module_base)
        return module

    def test_manage_app_version_matches_first_attempt(self, action_module, mock_display):
        """Test when manage app version matches on first attempt."""
        # Arrange
        action_module._task.args = {
            'host': 'https://api.example.com',
            'api_key': 'test-key',
            'mas_instance_id': 'inst1',
            'mas_app_id': 'manage',
            'mas_app_version': '8.7.0',
            'retries': 3,
            'delay': 5
        }

        mock_app = Mock()
        mock_app.metadata.namespace = 'mas-inst1-manage'
        mock_app.metadata.name = 'inst1'
        mock_app.status.versions.reconciled = '8.7.0'

        mock_apps = Mock()
        mock_apps.items = [mock_app]

        mock_app_resource = Mock()
        mock_app_resource.get.return_value = mock_apps

        mock_resources = Mock()
        mock_resources.get.return_value = mock_app_resource

        mock_client = Mock()
        mock_client.resources = mock_resources

        # Act
        with patch('verify_app_version.get_api_client', return_value=mock_client):
            result = action_module.run()

        # Assert
        assert result['failed'] is False
        assert result['changed'] is False
        assert result['message'] == "MAS manage version is matched"
        assert result['version'] == '8.7.0'

    def test_manage_app_version_matches_after_retry(self, action_module, mock_display):
        """Test when manage app version matches after retry."""
        # Arrange
        action_module._task.args = {
            'mas_instance_id': 'inst1',
            'mas_app_id': 'manage',
            'mas_app_version': '8.7.0',
            'retries': 3,
            'delay': 1
        }

        mock_app_first = Mock()
        mock_app_first.metadata.namespace = 'mas-inst1-manage'
        mock_app_first.metadata.name = 'inst1'
        mock_app_first.status.versions.reconciled = '8.6.0'

        mock_apps_first = Mock()
        mock_apps_first.items = [mock_app_first]

        mock_app_second = Mock()
        mock_app_second.metadata.namespace = 'mas-inst1-manage'
        mock_app_second.metadata.name = 'inst1'
        mock_app_second.status.versions.reconciled = '8.7.0'

        mock_apps_second = Mock()
        mock_apps_second.items = [mock_app_second]

        mock_app_resource = Mock()
        mock_app_resource.get.side_effect = [mock_apps_first, mock_apps_second]

        mock_resources = Mock()
        mock_resources.get.return_value = mock_app_resource

        mock_client = Mock()
        mock_client.resources = mock_resources

        # Act
        with patch('verify_app_version.get_api_client', return_value=mock_client):
            with patch('verify_app_version.time.sleep') as mock_sleep:
                result = action_module.run()

        # Assert
        assert result['failed'] is False
        assert result['version'] == '8.7.0'
        mock_sleep.assert_called_once_with(1)

    def test_app_version_not_matched_after_retries(self, action_module, mock_display):
        """Test when app version doesn't match after all retries."""
        # Arrange
        action_module._task.args = {
            'mas_instance_id': 'inst1',
            'mas_app_id': 'manage',
            'mas_app_version': '8.7.0',
            'retries': 2,
            'delay': 1
        }

        mock_app = Mock()
        mock_app.metadata.namespace = 'mas-inst1-manage'
        mock_app.metadata.name = 'inst1'
        mock_app.status.versions.reconciled = '8.6.0'

        mock_apps = Mock()
        mock_apps.items = [mock_app]

        mock_app_resource = Mock()
        mock_app_resource.get.return_value = mock_apps

        mock_resources = Mock()
        mock_resources.get.return_value = mock_app_resource

        mock_client = Mock()
        mock_client.resources = mock_resources

        # Act & Assert
        with patch('verify_app_version.get_api_client', return_value=mock_client):
            with patch('verify_app_version.time.sleep'):
                with pytest.raises(AnsibleError, match="MAS manage version is not matched"):
                    action_module.run()

    def test_unsupported_app_id_raises_error(self, action_module, mock_display):
        """Test when unsupported app_id is provided."""
        # Arrange
        action_module._task.args = {
            'mas_instance_id': 'inst1',
            'mas_app_id': 'monitor',
            'mas_app_version': '8.7.0',
            'retries': 1,
            'delay': 1
        }

        mock_client = Mock()

        # Act & Assert
        with patch('verify_app_version.get_api_client', return_value=mock_client):
            with pytest.raises(AnsibleError, match="MAS \\(monitor\\) instance doesn't exist"):
                action_module.run()

    def test_multiple_apps_finds_correct_instance(self, action_module, mock_display):
        """Test with multiple apps, finds the correct instance."""
        # Arrange
        action_module._task.args = {
            'mas_instance_id': 'inst2',
            'mas_app_id': 'manage',
            'mas_app_version': '8.7.0',
            'retries': 1,
            'delay': 1
        }

        mock_app1 = Mock()
        mock_app1.metadata.namespace = 'mas-inst1-manage'
        mock_app1.metadata.name = 'inst1'
        mock_app1.status.versions.reconciled = '8.6.0'

        mock_app2 = Mock()
        mock_app2.metadata.namespace = 'mas-inst2-manage'
        mock_app2.metadata.name = 'inst2'
        mock_app2.status.versions.reconciled = '8.7.0'

        mock_apps = Mock()
        mock_apps.items = [mock_app1, mock_app2]

        mock_app_resource = Mock()
        mock_app_resource.get.return_value = mock_apps

        mock_resources = Mock()
        mock_resources.get.return_value = mock_app_resource

        mock_client = Mock()
        mock_client.resources = mock_resources

        # Act
        with patch('verify_app_version.get_api_client', return_value=mock_client):
            result = action_module.run()

        # Assert
        assert result['failed'] is False
        assert result['version'] == '8.7.0'

    def test_no_apps_found(self, action_module, mock_display):
        """Test when no apps are found."""
        # Arrange
        action_module._task.args = {
            'mas_instance_id': 'inst1',
            'mas_app_id': 'manage',
            'mas_app_version': '8.7.0',
            'retries': 1,
            'delay': 1
        }

        mock_apps = Mock()
        mock_apps.items = []

        mock_app_resource = Mock()
        mock_app_resource.get.return_value = mock_apps

        mock_resources = Mock()
        mock_resources.get.return_value = mock_app_resource

        mock_client = Mock()
        mock_client.resources = mock_resources

        # Act & Assert
        with patch('verify_app_version.get_api_client', return_value=mock_client):
            with pytest.raises(AnsibleError, match="MAS manage version is not matched"):
                action_module.run()

# Made with Bob
