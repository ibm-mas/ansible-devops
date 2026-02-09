"""
Unit tests for wait_for_conditions action plugin.
"""

import pytest
from unittest.mock import Mock, patch
from ansible.errors import AnsibleError

import wait_for_conditions
ActionModule = wait_for_conditions.ActionModule


class TestWaitForConditions:
    """Test cases for wait_for_conditions action plugin."""

    @pytest.fixture
    def action_module(self, action_module_base):
        """Create ActionModule instance"""
        module = ActionModule(**action_module_base)
        return module

    def test_conditions_ready_first_attempt(self, action_module, mock_display):
        """Test when all conditions are ready on first attempt."""
        # Arrange
        action_module._task.args = {
            'host': 'https://api.example.com',
            'api_key': 'test-key',
            'api_version': 'core.mas.ibm.com/v1',
            'kind': 'Suite',
            'namespace': 'mas-inst1-core',
            'name': 'inst1',
            'conditions': ['Ready', 'Deployed'],
            'retries': 50
        }

        mock_condition1 = Mock()
        mock_condition1.type = 'Ready'
        mock_condition1.status = 'True'
        mock_condition1.reason = 'Ready'
        mock_condition1.message = 'MAS is ready to use'

        mock_condition2 = Mock()
        mock_condition2.type = 'Deployed'
        mock_condition2.status = 'True'
        mock_condition2.reason = 'Deployed'
        mock_condition2.message = 'MAS is deployed'

        mock_resource = Mock()
        mock_resource.status.conditions = [mock_condition1, mock_condition2]
        mock_resource.to_dict.return_value = {'metadata': {'name': 'inst1'}}

        mock_resource_api = Mock()
        mock_resource_api.get.return_value = mock_resource

        mock_resources = Mock()
        mock_resources.get.return_value = mock_resource_api

        mock_client = Mock()
        mock_client.resources = mock_resources

        # Act
        with patch('wait_for_conditions.get_api_client', return_value=mock_client):
            result = action_module.run()

        # Assert
        assert result['success'] is True
        assert result['failed'] is False
        assert result['changed'] is False
        assert "Suite 'inst1' is ready" in result['message']

    def test_missing_api_version_raises_error(self, action_module, mock_display, mocker):
        """Test that missing api_version raises AnsibleError."""
        # Arrange
        mock_client = mocker.MagicMock()
        mocker.patch('wait_for_conditions.get_api_client', return_value=mock_client)

        action_module._task.args = {
            'kind': 'Suite',
            'namespace': 'mas-inst1-core',
            'name': 'inst1'
        }

        # Act & Assert
        with pytest.raises(AnsibleError, match="api_version argument was not provided"):
            action_module.run()

    def test_missing_kind_raises_error(self, action_module, mock_display, mocker):
        """Test that missing kind raises AnsibleError."""
        # Arrange
        mock_client = mocker.MagicMock()
        mocker.patch('wait_for_conditions.get_api_client', return_value=mock_client)

        action_module._task.args = {
            'api_version': 'core.mas.ibm.com/v1',
            'namespace': 'mas-inst1-core',
            'name': 'inst1'
        }

        # Act & Assert
        with pytest.raises(AnsibleError, match="kind argument was not provided"):
            action_module.run()

    def test_missing_namespace_raises_error(self, action_module, mock_display, mocker):
        """Test that missing namespace raises AnsibleError."""
        # Arrange
        mock_client = mocker.MagicMock()
        mocker.patch('wait_for_conditions.get_api_client', return_value=mock_client)

        action_module._task.args = {
            'api_version': 'core.mas.ibm.com/v1',
            'kind': 'Suite',
            'name': 'inst1'
        }

        # Act & Assert
        with pytest.raises(AnsibleError, match="namespace argument was not provided"):
            action_module.run()

    def test_missing_name_raises_error(self, action_module, mock_display, mocker):
        """Test that missing name raises AnsibleError."""
        # Arrange
        mock_client = mocker.MagicMock()
        mocker.patch('wait_for_conditions.get_api_client', return_value=mock_client)

        action_module._task.args = {
            'api_version': 'core.mas.ibm.com/v1',
            'kind': 'Suite',
            'namespace': 'mas-inst1-core'
        }

        # Act & Assert
        with pytest.raises(AnsibleError, match="name argument was not provided"):
            action_module.run()

    def test_conditions_ready_after_retry(self, action_module, mock_display):
        """Test when conditions become ready after retry."""
        # Arrange
        action_module._task.args = {
            'api_version': 'core.mas.ibm.com/v1',
            'kind': 'Suite',
            'namespace': 'mas-inst1-core',
            'name': 'inst1',
            'conditions': ['Ready'],
            'retries': 50
        }

        # First attempt: not ready
        mock_condition_first = Mock()
        mock_condition_first.type = 'Ready'
        mock_condition_first.status = 'False'
        mock_condition_first.reason = 'Deploying'
        mock_condition_first.message = 'MAS is deploying'

        mock_resource_first = Mock()
        mock_resource_first.status.conditions = [mock_condition_first]
        mock_resource_first.to_dict.return_value = {'metadata': {'name': 'inst1'}}

        # Second attempt: ready
        mock_condition_second = Mock()
        mock_condition_second.type = 'Ready'
        mock_condition_second.status = 'True'
        mock_condition_second.reason = 'Ready'
        mock_condition_second.message = 'MAS is ready'

        mock_resource_second = Mock()
        mock_resource_second.status.conditions = [mock_condition_second]
        mock_resource_second.to_dict.return_value = {'metadata': {'name': 'inst1'}}

        mock_resource_api = Mock()
        mock_resource_api.get.side_effect = [mock_resource_first, mock_resource_second]

        mock_resources = Mock()
        mock_resources.get.return_value = mock_resource_api

        mock_client = Mock()
        mock_client.resources = mock_resources

        # Act
        with patch('wait_for_conditions.get_api_client', return_value=mock_client):
            with patch('wait_for_conditions.time.sleep') as mock_sleep:
                result = action_module.run()

        # Assert
        assert result['success'] is True
        assert result['failed'] is False
        mock_sleep.assert_called_once_with(120)

    def test_conditions_not_ready_after_retries(self, action_module, mock_display):
        """Test when conditions don't become ready after all retries."""
        # Arrange
        action_module._task.args = {
            'api_version': 'core.mas.ibm.com/v1',
            'kind': 'Suite',
            'namespace': 'mas-inst1-core',
            'name': 'inst1',
            'conditions': ['Ready'],
            'retries': 2
        }

        mock_condition = Mock()
        mock_condition.type = 'Ready'
        mock_condition.status = 'False'
        mock_condition.reason = 'Deploying'
        mock_condition.message = 'MAS is deploying'

        mock_resource = Mock()
        mock_resource.status.conditions = [mock_condition]
        mock_resource.to_dict.return_value = {'metadata': {'name': 'inst1'}}

        mock_resource_api = Mock()
        mock_resource_api.get.return_value = mock_resource

        mock_resources = Mock()
        mock_resources.get.return_value = mock_resource_api

        mock_client = Mock()
        mock_client.resources = mock_resources

        # Act
        with patch('wait_for_conditions.get_api_client', return_value=mock_client):
            with patch('wait_for_conditions.time.sleep'):
                result = action_module.run()

        # Assert
        assert result['success'] is False
        assert result['failed'] is True
        assert "is NOT ready" in result['message']

    def test_default_retries_value(self, action_module, mock_display):
        """Test that default retries value is used when not provided."""
        # Arrange
        action_module._task.args = {
            'api_version': 'core.mas.ibm.com/v1',
            'kind': 'Suite',
            'namespace': 'mas-inst1-core',
            'name': 'inst1',
            'conditions': ['Ready']
            # retries not provided, should default to 50
        }

        mock_condition = Mock()
        mock_condition.type = 'Ready'
        mock_condition.status = 'True'
        mock_condition.reason = 'Ready'
        mock_condition.message = 'MAS is ready'

        mock_resource = Mock()
        mock_resource.status.conditions = [mock_condition]
        mock_resource.to_dict.return_value = {'metadata': {'name': 'inst1'}}

        mock_resource_api = Mock()
        mock_resource_api.get.return_value = mock_resource

        mock_resources = Mock()
        mock_resources.get.return_value = mock_resource_api

        mock_client = Mock()
        mock_client.resources = mock_resources

        # Act
        with patch('wait_for_conditions.get_api_client', return_value=mock_client):
            result = action_module.run()

        # Assert
        assert result['success'] is True

# Made with Bob
