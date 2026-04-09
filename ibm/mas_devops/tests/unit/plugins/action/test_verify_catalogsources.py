"""
Unit tests for verify_catalogsources action plugin.

This module tests the verify_catalogsources action which checks if CatalogSources
are ready with retry logic.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from ansible.errors import AnsibleError

# Import the action module
import verify_catalogsources
ActionModule = verify_catalogsources.ActionModule


class TestVerifyCatalogSources:
    """Test cases for verify_catalogsources action plugin."""

    @pytest.fixture
    def action_module(self, action_module_base):
        """Create ActionModule instance"""
        module = ActionModule(**action_module_base)
        return module

    def test_all_catalogsources_ready_first_attempt(self, action_module, mock_display):
        """Test when all CatalogSources are ready on first attempt."""
        # Arrange
        action_module._task.args = {
            'host': 'https://api.example.com',
            'api_key': 'test-key',
            'retries': 3,
            'delay': 5
        }

        # Create mock catalog sources
        mock_catalog1 = Mock()
        mock_catalog1.metadata.namespace = 'openshift-marketplace'
        mock_catalog1.metadata.name = 'ibm-operator-catalog'
        mock_catalog1.status.connectionState.lastObservedState = 'READY'

        mock_catalog2 = Mock()
        mock_catalog2.metadata.namespace = 'openshift-marketplace'
        mock_catalog2.metadata.name = 'certified-operators'
        mock_catalog2.status.connectionState.lastObservedState = 'READY'

        mock_catalogs = Mock()
        mock_catalogs.items = [mock_catalog1, mock_catalog2]

        mock_catalog_resource = Mock()
        mock_catalog_resource.get.return_value = mock_catalogs

        mock_resources = Mock()
        mock_resources.get.return_value = mock_catalog_resource

        mock_client = Mock()
        mock_client.resources = mock_resources

        # Act
        with patch('verify_catalogsources.get_api_client', return_value=mock_client):
            result = action_module.run()

        # Assert
        assert result['failed'] is False
        assert result['changed'] is False
        assert result['message'] == "All CatalogSources are ready"
        assert len(result['ready']) == 2
        assert len(result['notReady']) == 0
        assert 'openshift-marketplace/ibm-operator-catalog = READY' in result['ready']
        assert 'openshift-marketplace/certified-operators = READY' in result['ready']

    def test_catalogsources_ready_after_retry(self, action_module, mock_display):
        """Test when CatalogSources become ready after retry."""
        # Arrange
        action_module._task.args = {
            'host': 'https://api.example.com',
            'api_key': 'test-key',
            'retries': 3,
            'delay': 1
        }

        # Create mock catalog that transitions from CONNECTING to READY
        mock_catalog = Mock()
        mock_catalog.metadata.namespace = 'openshift-marketplace'
        mock_catalog.metadata.name = 'ibm-operator-catalog'

        # First call: CONNECTING, second call: READY
        mock_catalog.status.connectionState.lastObservedState = 'CONNECTING'

        mock_catalogs_first = Mock()
        mock_catalogs_first.items = [mock_catalog]

        # Create second catalog state
        mock_catalog_ready = Mock()
        mock_catalog_ready.metadata.namespace = 'openshift-marketplace'
        mock_catalog_ready.metadata.name = 'ibm-operator-catalog'
        mock_catalog_ready.status.connectionState.lastObservedState = 'READY'

        mock_catalogs_second = Mock()
        mock_catalogs_second.items = [mock_catalog_ready]

        mock_catalog_resource = Mock()
        mock_catalog_resource.get.side_effect = [mock_catalogs_first, mock_catalogs_second]

        mock_resources = Mock()
        mock_resources.get.return_value = mock_catalog_resource

        mock_client = Mock()
        mock_client.resources = mock_resources

        # Act
        with patch('verify_catalogsources.get_api_client', return_value=mock_client):
            with patch('verify_catalogsources.time.sleep') as mock_sleep:
                result = action_module.run()

        # Assert
        assert result['failed'] is False
        assert result['changed'] is False
        assert result['message'] == "All CatalogSources are ready"
        assert len(result['ready']) == 1
        assert len(result['notReady']) == 0
        mock_sleep.assert_called_once_with(1)

    def test_catalogsources_not_ready_after_retries(self, action_module, mock_display):
        """Test when CatalogSources remain not ready after all retries."""
        # Arrange
        action_module._task.args = {
            'host': 'https://api.example.com',
            'api_key': 'test-key',
            'retries': 2,
            'delay': 1
        }

        # Create mock catalog that stays CONNECTING
        mock_catalog = Mock()
        mock_catalog.metadata.namespace = 'openshift-marketplace'
        mock_catalog.metadata.name = 'ibm-operator-catalog'
        mock_catalog.status.connectionState.lastObservedState = 'CONNECTING'

        mock_catalogs = Mock()
        mock_catalogs.items = [mock_catalog]

        mock_catalog_resource = Mock()
        mock_catalog_resource.get.return_value = mock_catalogs

        mock_resources = Mock()
        mock_resources.get.return_value = mock_catalog_resource

        mock_client = Mock()
        mock_client.resources = mock_resources

        # Act & Assert
        with patch('verify_catalogsources.get_api_client', return_value=mock_client):
            with patch('verify_catalogsources.time.sleep'):
                with pytest.raises(AnsibleError, match="One or more CatalogSources are not ready"):
                    action_module.run()

    def test_mixed_catalogsources_states(self, action_module, mock_display):
        """Test with mix of ready and not ready CatalogSources."""
        # Arrange
        action_module._task.args = {
            'host': 'https://api.example.com',
            'api_key': 'test-key',
            'retries': 1,
            'delay': 1
        }

        # Create ready catalog
        mock_catalog1 = Mock()
        mock_catalog1.metadata.namespace = 'openshift-marketplace'
        mock_catalog1.metadata.name = 'certified-operators'
        mock_catalog1.status.connectionState.lastObservedState = 'READY'

        # Create not ready catalog
        mock_catalog2 = Mock()
        mock_catalog2.metadata.namespace = 'openshift-marketplace'
        mock_catalog2.metadata.name = 'ibm-operator-catalog'
        mock_catalog2.status.connectionState.lastObservedState = 'CONNECTING'

        mock_catalogs = Mock()
        mock_catalogs.items = [mock_catalog1, mock_catalog2]

        mock_catalog_resource = Mock()
        mock_catalog_resource.get.return_value = mock_catalogs

        mock_resources = Mock()
        mock_resources.get.return_value = mock_catalog_resource

        mock_client = Mock()
        mock_client.resources = mock_resources

        # Act & Assert
        with patch('verify_catalogsources.get_api_client', return_value=mock_client):
            with patch('verify_catalogsources.time.sleep'):
                with pytest.raises(AnsibleError, match="One or more CatalogSources are not ready"):
                    action_module.run()

    def test_no_catalogsources_found(self, action_module, mock_display):
        """Test when no CatalogSources are found."""
        # Arrange
        action_module._task.args = {
            'host': 'https://api.example.com',
            'api_key': 'test-key',
            'retries': 1,
            'delay': 1
        }

        mock_catalogs = Mock()
        mock_catalogs.items = []

        mock_catalog_resource = Mock()
        mock_catalog_resource.get.return_value = mock_catalogs

        mock_resources = Mock()
        mock_resources.get.return_value = mock_catalog_resource

        mock_client = Mock()
        mock_client.resources = mock_resources

        # Act
        with patch('verify_catalogsources.get_api_client', return_value=mock_client):
            result = action_module.run()

        # Assert
        assert result['failed'] is False
        assert result['changed'] is False
        assert result['message'] == "All CatalogSources are ready"
        assert len(result['ready']) == 0
        assert len(result['notReady']) == 0

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

        mock_catalog = Mock()
        mock_catalog.metadata.namespace = 'openshift-marketplace'
        mock_catalog.metadata.name = 'test-catalog'
        mock_catalog.status.connectionState.lastObservedState = 'READY'

        mock_catalogs = Mock()
        mock_catalogs.items = [mock_catalog]

        mock_catalog_resource = Mock()
        mock_catalog_resource.get.return_value = mock_catalogs

        mock_resources = Mock()
        mock_resources.get.return_value = mock_catalog_resource

        mock_client = Mock()
        mock_client.resources = mock_resources

        # Act
        with patch('verify_catalogsources.get_api_client', return_value=mock_client) as mock_get_client:
            result = action_module.run()

        # Assert
        mock_get_client.assert_called_once_with(api_key=custom_api_key, host=custom_host)
        assert result['failed'] is False

    def test_catalogsource_with_different_states(self, action_module, mock_display):
        """Test CatalogSources with various connection states."""
        # Arrange
        action_module._task.args = {
            'host': 'https://api.example.com',
            'api_key': 'test-key',
            'retries': 1,
            'delay': 1
        }

        # Create catalogs with different states
        states = ['READY', 'CONNECTING', 'TRANSIENT_FAILURE', 'IDLE']
        mock_catalogs_list = []

        for i, state in enumerate(states):
            mock_catalog = Mock()
            mock_catalog.metadata.namespace = 'openshift-marketplace'
            mock_catalog.metadata.name = f'catalog-{i}'
            mock_catalog.status.connectionState.lastObservedState = state
            mock_catalogs_list.append(mock_catalog)

        mock_catalogs = Mock()
        mock_catalogs.items = mock_catalogs_list

        mock_catalog_resource = Mock()
        mock_catalog_resource.get.return_value = mock_catalogs

        mock_resources = Mock()
        mock_resources.get.return_value = mock_catalog_resource

        mock_client = Mock()
        mock_client.resources = mock_resources

        # Act & Assert
        with patch('verify_catalogsources.get_api_client', return_value=mock_client):
            with patch('verify_catalogsources.time.sleep'):
                with pytest.raises(AnsibleError, match="One or more CatalogSources are not ready"):
                    action_module.run()

# Made with Bob
