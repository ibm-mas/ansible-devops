"""
Unit tests for verify_subscriptions action plugin.

This module tests the verify_subscriptions action which checks if Subscriptions
are at the latest known operator version with retry logic.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from ansible.errors import AnsibleError

# Import the action module
import verify_subscriptions
ActionModule = verify_subscriptions.ActionModule


class TestVerifySubscriptions:
    """Test cases for verify_subscriptions action plugin."""

    @pytest.fixture
    def action_module(self, action_module_base):
        """Create ActionModule instance"""
        module = ActionModule(**action_module_base)
        return module

    def test_all_subscriptions_at_latest_first_attempt(self, action_module, mock_display):
        """Test when all Subscriptions are at latest on first attempt."""
        # Arrange
        action_module._task.args = {
            'host': 'https://api.example.com',
            'api_key': 'test-key',
            'retries': 3,
            'delay': 5
        }

        # Create mock subscriptions
        mock_sub1 = Mock()
        mock_sub1.metadata.namespace = 'openshift-operators'
        mock_sub1.metadata.name = 'ibm-mas-operator'
        mock_sub1.status.state = 'AtLatestKnown'

        mock_sub2 = Mock()
        mock_sub2.metadata.namespace = 'openshift-operators'
        mock_sub2.metadata.name = 'ibm-sls-operator'
        mock_sub2.status.state = 'AtLatestKnown'

        mock_subs = Mock()
        mock_subs.items = [mock_sub1, mock_sub2]

        mock_sub_resource = Mock()
        mock_sub_resource.get.return_value = mock_subs

        mock_resources = Mock()
        mock_resources.get.return_value = mock_sub_resource

        mock_client = Mock()
        mock_client.resources = mock_resources

        # Act
        with patch('verify_subscriptions.get_api_client', return_value=mock_client):
            result = action_module.run()

        # Assert
        assert result['failed'] is False
        assert result['changed'] is False
        assert result['message'] == "All Subscriptions are at the latest known operator version"
        assert len(result['atLatest']) == 2
        assert len(result['notAtLatest']) == 0
        assert 'openshift-operators/ibm-mas-operator = AtLatestKnown' in result['atLatest']
        assert 'openshift-operators/ibm-sls-operator = AtLatestKnown' in result['atLatest']

    def test_subscriptions_at_latest_after_retry(self, action_module, mock_display):
        """Test when Subscriptions reach latest after retry."""
        # Arrange
        action_module._task.args = {
            'host': 'https://api.example.com',
            'api_key': 'test-key',
            'retries': 3,
            'delay': 1
        }

        # Create mock subscription that transitions from UpgradePending to AtLatestKnown
        mock_sub = Mock()
        mock_sub.metadata.namespace = 'openshift-operators'
        mock_sub.metadata.name = 'ibm-mas-operator'

        # First call: UpgradePending
        mock_subs_first = Mock()
        mock_sub.status.state = 'UpgradePending'
        mock_subs_first.items = [mock_sub]

        # Second call: AtLatestKnown
        mock_sub_ready = Mock()
        mock_sub_ready.metadata.namespace = 'openshift-operators'
        mock_sub_ready.metadata.name = 'ibm-mas-operator'
        mock_sub_ready.status.state = 'AtLatestKnown'

        mock_subs_second = Mock()
        mock_subs_second.items = [mock_sub_ready]

        mock_sub_resource = Mock()
        mock_sub_resource.get.side_effect = [mock_subs_first, mock_subs_second]

        mock_resources = Mock()
        mock_resources.get.return_value = mock_sub_resource

        mock_client = Mock()
        mock_client.resources = mock_resources

        # Act
        with patch('verify_subscriptions.get_api_client', return_value=mock_client):
            with patch('verify_subscriptions.time.sleep') as mock_sleep:
                result = action_module.run()

        # Assert
        assert result['failed'] is False
        assert result['changed'] is False
        assert result['message'] == "All Subscriptions are at the latest known operator version"
        assert len(result['atLatest']) == 1
        assert len(result['notAtLatest']) == 0
        mock_sleep.assert_called_once_with(1)

    def test_subscriptions_not_at_latest_after_retries(self, action_module, mock_display):
        """Test when Subscriptions remain not at latest after all retries."""
        # Arrange
        action_module._task.args = {
            'host': 'https://api.example.com',
            'api_key': 'test-key',
            'retries': 2,
            'delay': 1
        }

        # Create mock subscription that stays UpgradePending
        mock_sub = Mock()
        mock_sub.metadata.namespace = 'openshift-operators'
        mock_sub.metadata.name = 'ibm-mas-operator'
        mock_sub.status.state = 'UpgradePending'

        mock_subs = Mock()
        mock_subs.items = [mock_sub]

        mock_sub_resource = Mock()
        mock_sub_resource.get.return_value = mock_subs

        mock_resources = Mock()
        mock_resources.get.return_value = mock_sub_resource

        mock_client = Mock()
        mock_client.resources = mock_resources

        # Act & Assert
        with patch('verify_subscriptions.get_api_client', return_value=mock_client):
            with patch('verify_subscriptions.time.sleep'):
                with pytest.raises(AnsibleError, match="One or more subscriptions did not update"):
                    action_module.run()

    def test_mixed_subscription_states(self, action_module, mock_display):
        """Test with mix of at latest and not at latest Subscriptions."""
        # Arrange
        action_module._task.args = {
            'host': 'https://api.example.com',
            'api_key': 'test-key',
            'retries': 1,
            'delay': 1
        }

        # Create at latest subscription
        mock_sub1 = Mock()
        mock_sub1.metadata.namespace = 'openshift-operators'
        mock_sub1.metadata.name = 'ibm-sls-operator'
        mock_sub1.status.state = 'AtLatestKnown'

        # Create not at latest subscription
        mock_sub2 = Mock()
        mock_sub2.metadata.namespace = 'openshift-operators'
        mock_sub2.metadata.name = 'ibm-mas-operator'
        mock_sub2.status.state = 'UpgradePending'

        mock_subs = Mock()
        mock_subs.items = [mock_sub1, mock_sub2]

        mock_sub_resource = Mock()
        mock_sub_resource.get.return_value = mock_subs

        mock_resources = Mock()
        mock_resources.get.return_value = mock_sub_resource

        mock_client = Mock()
        mock_client.resources = mock_resources

        # Act & Assert
        with patch('verify_subscriptions.get_api_client', return_value=mock_client):
            with patch('verify_subscriptions.time.sleep'):
                with pytest.raises(AnsibleError, match="One or more subscriptions did not update"):
                    action_module.run()

    def test_no_subscriptions_found(self, action_module, mock_display):
        """Test when no Subscriptions are found."""
        # Arrange
        action_module._task.args = {
            'host': 'https://api.example.com',
            'api_key': 'test-key',
            'retries': 1,
            'delay': 1
        }

        mock_subs = Mock()
        mock_subs.items = []

        mock_sub_resource = Mock()
        mock_sub_resource.get.return_value = mock_subs

        mock_resources = Mock()
        mock_resources.get.return_value = mock_sub_resource

        mock_client = Mock()
        mock_client.resources = mock_resources

        # Act
        with patch('verify_subscriptions.get_api_client', return_value=mock_client):
            result = action_module.run()

        # Assert
        assert result['failed'] is False
        assert result['changed'] is False
        assert result['message'] == "All Subscriptions are at the latest known operator version"
        assert len(result['atLatest']) == 0
        assert len(result['notAtLatest']) == 0

    def test_with_custom_host_and_api_key(self, action_module, mock_display):
        """Test with custom host and API key."""
        # Arrange
        custom_host = 'https://custom.api.com:6443'
        custom_api_key = 'custom-key-123'

        action_module._task.args = {
            'host': custom_host,
            'api_key': custom_api_key,
            'retries': 1,
            'delay': 1
        }

        mock_sub = Mock()
        mock_sub.metadata.namespace = 'openshift-operators'
        mock_sub.metadata.name = 'test-operator'
        mock_sub.status.state = 'AtLatestKnown'

        mock_subs = Mock()
        mock_subs.items = [mock_sub]

        mock_sub_resource = Mock()
        mock_sub_resource.get.return_value = mock_subs

        mock_resources = Mock()
        mock_resources.get.return_value = mock_sub_resource

        mock_client = Mock()
        mock_client.resources = mock_resources

        # Act
        with patch('verify_subscriptions.get_api_client', return_value=mock_client) as mock_get_client:
            result = action_module.run()

        # Assert
        mock_get_client.assert_called_once_with(api_key=custom_api_key, host=custom_host)
        assert result['failed'] is False

    def test_subscription_with_different_states(self, action_module, mock_display):
        """Test Subscriptions with various states."""
        # Arrange
        action_module._task.args = {
            'host': 'https://api.example.com',
            'api_key': 'test-key',
            'retries': 1,
            'delay': 1
        }

        # Create subscriptions with different states
        states = ['AtLatestKnown', 'UpgradePending', 'UpgradeAvailable', 'Installing']
        mock_subs_list = []

        for i, state in enumerate(states):
            mock_sub = Mock()
            mock_sub.metadata.namespace = 'openshift-operators'
            mock_sub.metadata.name = f'operator-{i}'
            mock_sub.status.state = state
            mock_subs_list.append(mock_sub)

        mock_subs = Mock()
        mock_subs.items = mock_subs_list

        mock_sub_resource = Mock()
        mock_sub_resource.get.return_value = mock_subs

        mock_resources = Mock()
        mock_resources.get.return_value = mock_sub_resource

        mock_client = Mock()
        mock_client.resources = mock_resources

        # Act & Assert
        with patch('verify_subscriptions.get_api_client', return_value=mock_client):
            with patch('verify_subscriptions.time.sleep'):
                with pytest.raises(AnsibleError, match="One or more subscriptions did not update"):
                    action_module.run()

# Made with Bob
