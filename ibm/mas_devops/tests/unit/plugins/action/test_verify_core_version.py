"""
Unit tests for verify_core_version action plugin.

Tests the verify_core_version action which checks if MAS core version matches
the expected version with retry logic.
"""

import pytest
from unittest.mock import Mock, patch
from ansible.errors import AnsibleError

import verify_core_version
ActionModule = verify_core_version.ActionModule


class TestVerifyCoreVersion:
    """Test cases for verify_core_version action plugin."""

    @pytest.fixture
    def action_module(self, action_module_base):
        """Create ActionModule instance"""
        module = ActionModule(**action_module_base)
        return module

    def test_core_version_matches_first_attempt(self, action_module, mock_display):
        """Test when core version matches on first attempt."""
        # Arrange
        action_module._task.args = {
            'host': 'https://api.example.com',
            'api_key': 'test-key',
            'mas_instance_id': 'inst1',
            'core_version': '8.11.0',
            'retries': 3,
            'delay': 5
        }

        mock_suite = Mock()
        mock_suite.metadata.namespace = 'mas-inst1-core'
        mock_suite.metadata.name = 'inst1'
        mock_suite.status.versions.reconciled = '8.11.0'

        mock_suites = Mock()
        mock_suites.items = [mock_suite]

        mock_suite_resource = Mock()
        mock_suite_resource.get.return_value = mock_suites

        mock_resources = Mock()
        mock_resources.get.return_value = mock_suite_resource

        mock_client = Mock()
        mock_client.resources = mock_resources

        # Act
        with patch('verify_core_version.get_api_client', return_value=mock_client):
            result = action_module.run()

        # Assert
        assert result['failed'] is False
        assert result['changed'] is False
        assert result['message'] == "MAS core version is matched"
        assert result['version'] == '8.11.0'

    def test_core_version_matches_after_retry(self, action_module, mock_display):
        """Test when core version matches after retry."""
        # Arrange
        action_module._task.args = {
            'host': 'https://api.example.com',
            'api_key': 'test-key',
            'mas_instance_id': 'inst1',
            'core_version': '8.11.0',
            'retries': 3,
            'delay': 1
        }

        # First attempt: wrong version
        mock_suite_first = Mock()
        mock_suite_first.metadata.namespace = 'mas-inst1-core'
        mock_suite_first.metadata.name = 'inst1'
        mock_suite_first.status.versions.reconciled = '8.10.0'

        mock_suites_first = Mock()
        mock_suites_first.items = [mock_suite_first]

        # Second attempt: correct version
        mock_suite_second = Mock()
        mock_suite_second.metadata.namespace = 'mas-inst1-core'
        mock_suite_second.metadata.name = 'inst1'
        mock_suite_second.status.versions.reconciled = '8.11.0'

        mock_suites_second = Mock()
        mock_suites_second.items = [mock_suite_second]

        mock_suite_resource = Mock()
        mock_suite_resource.get.side_effect = [mock_suites_first, mock_suites_second]

        mock_resources = Mock()
        mock_resources.get.return_value = mock_suite_resource

        mock_client = Mock()
        mock_client.resources = mock_resources

        # Act
        with patch('verify_core_version.get_api_client', return_value=mock_client):
            with patch('verify_core_version.time.sleep') as mock_sleep:
                result = action_module.run()

        # Assert
        assert result['failed'] is False
        assert result['message'] == "MAS core version is matched"
        assert result['version'] == '8.11.0'
        mock_sleep.assert_called_once_with(1)

    def test_core_version_not_matched_after_retries(self, action_module, mock_display):
        """Test when core version doesn't match after all retries."""
        # Arrange
        action_module._task.args = {
            'host': 'https://api.example.com',
            'api_key': 'test-key',
            'mas_instance_id': 'inst1',
            'core_version': '8.11.0',
            'retries': 2,
            'delay': 1
        }

        mock_suite = Mock()
        mock_suite.metadata.namespace = 'mas-inst1-core'
        mock_suite.metadata.name = 'inst1'
        mock_suite.status.versions.reconciled = '8.10.0'

        mock_suites = Mock()
        mock_suites.items = [mock_suite]

        mock_suite_resource = Mock()
        mock_suite_resource.get.return_value = mock_suites

        mock_resources = Mock()
        mock_resources.get.return_value = mock_suite_resource

        mock_client = Mock()
        mock_client.resources = mock_resources

        # Act & Assert
        with patch('verify_core_version.get_api_client', return_value=mock_client):
            with patch('verify_core_version.time.sleep'):
                with pytest.raises(AnsibleError, match="MAS core version is not matched"):
                    action_module.run()

    def test_multiple_suites_finds_correct_instance(self, action_module, mock_display):
        """Test with multiple suites, finds the correct instance."""
        # Arrange
        action_module._task.args = {
            'host': 'https://api.example.com',
            'api_key': 'test-key',
            'mas_instance_id': 'inst2',
            'core_version': '8.11.0',
            'retries': 1,
            'delay': 1
        }

        # Create multiple suites
        mock_suite1 = Mock()
        mock_suite1.metadata.namespace = 'mas-inst1-core'
        mock_suite1.metadata.name = 'inst1'
        mock_suite1.status.versions.reconciled = '8.10.0'

        mock_suite2 = Mock()
        mock_suite2.metadata.namespace = 'mas-inst2-core'
        mock_suite2.metadata.name = 'inst2'
        mock_suite2.status.versions.reconciled = '8.11.0'

        mock_suites = Mock()
        mock_suites.items = [mock_suite1, mock_suite2]

        mock_suite_resource = Mock()
        mock_suite_resource.get.return_value = mock_suites

        mock_resources = Mock()
        mock_resources.get.return_value = mock_suite_resource

        mock_client = Mock()
        mock_client.resources = mock_resources

        # Act
        with patch('verify_core_version.get_api_client', return_value=mock_client):
            result = action_module.run()

        # Assert
        assert result['failed'] is False
        assert result['version'] == '8.11.0'

    def test_no_suites_found(self, action_module, mock_display):
        """Test when no suites are found."""
        # Arrange
        action_module._task.args = {
            'host': 'https://api.example.com',
            'api_key': 'test-key',
            'mas_instance_id': 'inst1',
            'core_version': '8.11.0',
            'retries': 1,
            'delay': 1
        }

        mock_suites = Mock()
        mock_suites.items = []

        mock_suite_resource = Mock()
        mock_suite_resource.get.return_value = mock_suites

        mock_resources = Mock()
        mock_resources.get.return_value = mock_suite_resource

        mock_client = Mock()
        mock_client.resources = mock_resources

        # Act & Assert
        with patch('verify_core_version.get_api_client', return_value=mock_client):
            with pytest.raises(AnsibleError, match="MAS core version is not matched"):
                action_module.run()

    def test_with_custom_host_and_api_key(self, action_module, mock_display):
        """Test with custom Kubernetes host and API key."""
        # Arrange
        custom_host = 'https://custom.api.com:6443'
        custom_api_key = 'custom-key-123'

        action_module._task.args = {
            'host': custom_host,
            'api_key': custom_api_key,
            'mas_instance_id': 'inst1',
            'core_version': '8.11.0',
            'retries': 1,
            'delay': 1
        }

        mock_suite = Mock()
        mock_suite.metadata.namespace = 'mas-inst1-core'
        mock_suite.metadata.name = 'inst1'
        mock_suite.status.versions.reconciled = '8.11.0'

        mock_suites = Mock()
        mock_suites.items = [mock_suite]

        mock_suite_resource = Mock()
        mock_suite_resource.get.return_value = mock_suites

        mock_resources = Mock()
        mock_resources.get.return_value = mock_suite_resource

        mock_client = Mock()
        mock_client.resources = mock_resources

        # Act
        with patch('verify_core_version.get_api_client', return_value=mock_client) as mock_get_client:
            result = action_module.run()

        # Assert
        mock_get_client.assert_called_once_with(api_key=custom_api_key, host=custom_host)
        assert result['failed'] is False

    def test_wrong_instance_id(self, action_module, mock_display):
        """Test when suite exists but with different instance ID."""
        # Arrange
        action_module._task.args = {
            'host': 'https://api.example.com',
            'api_key': 'test-key',
            'mas_instance_id': 'inst2',
            'core_version': '8.11.0',
            'retries': 1,
            'delay': 1
        }

        mock_suite = Mock()
        mock_suite.metadata.namespace = 'mas-inst1-core'
        mock_suite.metadata.name = 'inst1'
        mock_suite.status.versions.reconciled = '8.11.0'

        mock_suites = Mock()
        mock_suites.items = [mock_suite]

        mock_suite_resource = Mock()
        mock_suite_resource.get.return_value = mock_suites

        mock_resources = Mock()
        mock_resources.get.return_value = mock_suite_resource

        mock_client = Mock()
        mock_client.resources = mock_resources

        # Act & Assert
        with patch('verify_core_version.get_api_client', return_value=mock_client):
            with pytest.raises(AnsibleError, match="MAS core version is not matched"):
                action_module.run()

# Made with Bob
