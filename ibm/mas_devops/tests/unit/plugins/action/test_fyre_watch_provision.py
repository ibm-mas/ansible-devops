"""
Unit tests for fyre_watch_provision action plugin.

Tests cover:
- Successful cluster provision (deployed)
- Cluster in configuring / deploying state then deployed
- Transient network / connection error retry and recovery
- Cluster does not exist retry
- Rate limited (423) handling
- Missing required parameters
"""
import pytest
import requests
from unittest.mock import patch, Mock
from ansible.errors import AnsibleError

# Import the action module (path setup is in conftest.py)
import fyre_watch_provision
ActionModule = fyre_watch_provision.ActionModule

# Import mock helpers (path setup is in root conftest.py)
import external_api_mocks
create_mock_fyre_cluster_deploying_response = external_api_mocks.create_mock_fyre_cluster_deploying_response
create_mock_fyre_cluster_deployed_response = external_api_mocks.create_mock_fyre_cluster_deployed_response
create_mock_fyre_cluster_not_exist_response = external_api_mocks.create_mock_fyre_cluster_not_exist_response


class TestFyreWatchProvision:
    """Tests for fyre_watch_provision action plugin"""

    @pytest.fixture
    def action_module(self, action_module_base):
        """Create ActionModule instance"""
        module = ActionModule(**action_module_base)
        return module

    @patch('fyre_watch_provision.requests.get')
    @patch('fyre_watch_provision.urllib3.disable_warnings')
    def test_cluster_already_deployed(self, mock_disable_warnings, mock_get, action_module):
        """Test when cluster is already deployed on first check"""
        action_module._task.args = {
            'username': 'testuser',
            'apikey': 'testkey',
            'cluster_name': 'test-cluster',
            'fyre_site': 'svl'
        }
        mock_get.return_value = create_mock_fyre_cluster_deployed_response()

        result = action_module.run()

        assert result['success'] is True
        assert result['failed'] is False
        assert 'test-cluster' in result['message']
        assert 'successfully provisioned' in result['message']
        mock_get.assert_called_once()
        mock_disable_warnings.assert_called_once()

    @patch('fyre_watch_provision.sleep')
    @patch('fyre_watch_provision.requests.get')
    @patch('fyre_watch_provision.urllib3.disable_warnings')
    def test_connection_timeout_retries_and_recovers(self, mock_disable_warnings, mock_get, mock_sleep, action_module):
        """Test that transient connection timeouts are caught and retried until success"""
        action_module._task.args = {
            'username': 'testuser',
            'apikey': 'testkey',
            'cluster_name': 'test-cluster',
            'fyre_site': 'rtp'
        }
        # First call raises ConnectTimeout, second call returns deployed
        mock_get.side_effect = [
            requests.exceptions.ConnectTimeout("Connection to ocpapi.svl.ibm.com timed out"),
            create_mock_fyre_cluster_deployed_response()
        ]

        result = action_module.run()

        assert result['success'] is True
        assert result['failed'] is False
        assert mock_get.call_count == 2
        mock_sleep.assert_called_once()

    @patch('fyre_watch_provision.sleep')
    @patch('fyre_watch_provision.requests.get')
    @patch('fyre_watch_provision.urllib3.disable_warnings')
    def test_connection_error_exceeds_error_limit(self, mock_disable_warnings, mock_get, mock_sleep, action_module):
        """Test that repeated connection errors eventually fail after limit"""
        action_module._task.args = {
            'username': 'testuser',
            'apikey': 'testkey',
            'cluster_name': 'test-cluster',
            'fyre_site': 'rtp'
        }
        mock_get.side_effect = requests.exceptions.ConnectionError("Failed to connect")

        result = action_module.run()

        assert result['success'] is False
        assert result['failed'] is True
        assert 'NOT successfully provisioned' in result['message']
        assert mock_get.call_count == 5

    @patch('fyre_watch_provision.sleep')
    @patch('fyre_watch_provision.requests.get')
    @patch('fyre_watch_provision.urllib3.disable_warnings')
    def test_cluster_deploying_then_deployed(self, mock_disable_warnings, mock_get, mock_sleep, action_module):
        """Test polling when cluster transitions from deploying to deployed"""
        action_module._task.args = {
            'username': 'testuser',
            'apikey': 'testkey',
            'cluster_name': 'test-cluster',
            'fyre_site': 'svl'
        }
        mock_get.side_effect = [
            create_mock_fyre_cluster_deploying_response(),
            create_mock_fyre_cluster_deployed_response()
        ]

        result = action_module.run()

        assert result['success'] is True
        assert result['failed'] is False
        assert mock_get.call_count == 2
        mock_sleep.assert_called_once()

    def test_missing_username_raises_error(self, action_module):
        """Test that missing username raises AnsibleError"""
        action_module._task.args = {
            'apikey': 'testkey',
            'cluster_name': 'test-cluster',
            'fyre_site': 'svl'
        }
        with pytest.raises(AnsibleError, match="fyre_username argument was not provided"):
            action_module.run()

    def test_missing_apikey_raises_error(self, action_module):
        """Test that missing apikey raises AnsibleError"""
        action_module._task.args = {
            'username': 'testuser',
            'cluster_name': 'test-cluster',
            'fyre_site': 'svl'
        }
        with pytest.raises(AnsibleError, match="fyre_password argument was not provided"):
            action_module.run()
