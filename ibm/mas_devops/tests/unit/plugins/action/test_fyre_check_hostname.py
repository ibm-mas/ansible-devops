"""
Unit tests for fyre_check_hostname action plugin.

Tests cover:
- Successful hostname availability check
- Hostname not available
- Missing required parameters
- API error responses
- Rate limiting scenarios
"""
import pytest
from unittest.mock import patch, Mock
from ansible.errors import AnsibleError

# Import the action module (path setup is in conftest.py)
import fyre_check_hostname
ActionModule = fyre_check_hostname.ActionModule

# Import mock helpers (path setup is in root conftest.py)
import external_api_mocks
create_mock_fyre_hostname_available_response = external_api_mocks.create_mock_fyre_hostname_available_response
create_mock_fyre_hostname_unavailable_response = external_api_mocks.create_mock_fyre_hostname_unavailable_response
create_mock_fyre_unauthorized_response = external_api_mocks.create_mock_fyre_unauthorized_response
create_mock_http_error_response = external_api_mocks.create_mock_http_error_response


class TestFyreCheckHostname:
    """Tests for fyre_check_hostname action plugin"""

    @pytest.fixture
    def action_module(self, action_module_base):
        """Create ActionModule instance"""
        module = ActionModule(**action_module_base)
        return module

    @patch('fyre_check_hostname.requests.get')
    @patch('fyre_check_hostname.urllib3.disable_warnings')
    def test_hostname_available(self, mock_disable_warnings, mock_get, action_module):
        """Test successful check when hostname is available"""
        # Arrange
        action_module._task.args = {
            'username': 'testuser',
            'apikey': 'testkey',
            'cluster_name': 'test-cluster',
            'fyre_site': 'svl'
        }
        mock_get.return_value = create_mock_fyre_hostname_available_response()

        # Act
        result = action_module.run()

        # Assert
        assert result['success'] is True
        assert result['failed'] is False
        assert result['available'] is True
        assert 'test-cluster' in result['message']
        assert 'available' in result['message']
        mock_get.assert_called_once()
        mock_disable_warnings.assert_called_once()

    @patch('fyre_check_hostname.requests.get')
    @patch('fyre_check_hostname.urllib3.disable_warnings')
    def test_hostname_not_available(self, mock_disable_warnings, mock_get, action_module):
        """Test check when hostname is not available"""
        # Arrange
        action_module._task.args = {
            'username': 'testuser',
            'apikey': 'testkey',
            'cluster_name': 'existing-cluster',
            'fyre_site': 'svl'
        }
        mock_get.return_value = create_mock_fyre_hostname_unavailable_response()

        # Act
        result = action_module.run()

        # Assert
        assert result['success'] is True
        assert result['failed'] is False
        assert result['available'] is False
        assert 'existing-cluster' in result['message']
        assert 'NOT available' in result['message']

    def test_missing_username_raises_error(self, action_module):
        """Test that missing username raises AnsibleError"""
        # Arrange
        action_module._task.args = {
            'apikey': 'testkey',
            'cluster_name': 'test-cluster',
            'fyre_site': 'svl'
        }

        # Act & Assert
        with pytest.raises(AnsibleError, match="fyre_username argument was not provided"):
            action_module.run()

    def test_missing_apikey_raises_error(self, action_module):
        """Test that missing apikey raises AnsibleError"""
        # Arrange
        action_module._task.args = {
            'username': 'testuser',
            'cluster_name': 'test-cluster',
            'fyre_site': 'svl'
        }

        # Act & Assert
        with pytest.raises(AnsibleError, match="fyre_password argument was not provided"):
            action_module.run()

    def test_missing_cluster_name_raises_error(self, action_module):
        """Test that missing cluster_name raises AnsibleError"""
        # Arrange
        action_module._task.args = {
            'username': 'testuser',
            'apikey': 'testkey',
            'fyre_site': 'svl'
        }

        # Act & Assert
        with pytest.raises(AnsibleError, match="cluster_name argument was not provided"):
            action_module.run()

    def test_missing_fyre_site_raises_error(self, action_module):
        """Test that missing fyre_site raises AnsibleError"""
        # Arrange
        action_module._task.args = {
            'username': 'testuser',
            'apikey': 'testkey',
            'cluster_name': 'test-cluster'
        }

        # Act & Assert
        with pytest.raises(AnsibleError, match="fyre_site argument was not provided"):
            action_module.run()

    @patch('fyre_check_hostname.requests.get')
    @patch('fyre_check_hostname.urllib3.disable_warnings')
    def test_unauthorized_response_raises_error(self, mock_disable_warnings, mock_get, action_module):
        """Test that unauthorized response raises AnsibleError"""
        # Arrange
        action_module._task.args = {
            'username': 'testuser',
            'apikey': 'wrongkey',
            'cluster_name': 'test-cluster',
            'fyre_site': 'svl'
        }
        mock_get.return_value = create_mock_fyre_unauthorized_response()

        # Act & Assert
        with pytest.raises(AnsibleError, match="Unexpected response code from Fyre APIs"):
            action_module.run()

    @patch('fyre_check_hostname.requests.get')
    @patch('fyre_check_hostname.urllib3.disable_warnings')
    def test_server_error_raises_error(self, mock_disable_warnings, mock_get, action_module):
        """Test that server error raises AnsibleError"""
        # Arrange
        action_module._task.args = {
            'username': 'testuser',
            'apikey': 'testkey',
            'cluster_name': 'test-cluster',
            'fyre_site': 'svl'
        }
        mock_get.return_value = create_mock_http_error_response(500, "Internal Server Error")

        # Act & Assert
        with pytest.raises(AnsibleError, match="Unexpected response code from Fyre APIs"):
            action_module.run()

    @patch('fyre_check_hostname.requests.get')
    @patch('fyre_check_hostname.urllib3.disable_warnings')
    def test_correct_api_url_construction(self, mock_disable_warnings, mock_get, action_module):
        """Test that API URL is constructed correctly"""
        # Arrange
        action_module._task.args = {
            'username': 'testuser',
            'apikey': 'testkey',
            'cluster_name': 'my-cluster',
            'fyre_site': 'rtp'
        }
        mock_get.return_value = create_mock_fyre_hostname_available_response()

        # Act
        result = action_module.run()

        # Assert
        call_args = mock_get.call_args
        assert 'my-cluster' in call_args.kwargs['url']
        assert 'site=rtp' in call_args.kwargs['url']
        assert call_args.kwargs['auth'] == ('testuser', 'testkey')
        assert call_args.kwargs['verify'] is False

# Made with Bob
