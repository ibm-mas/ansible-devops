"""
Unit tests for get_catalog_info action plugin.

Tests cover:
- Successful catalog information retrieval
- Missing required parameters
- Catalog not found scenarios
- Parameter validation

Note: These tests use the REAL mas.devops.data.getCatalog() function,
not mocks. We only mock external dependencies like Kubernetes API.

Setup: Install mas.devops package in editable mode:
    pip install -e ../python-devops
"""
import pytest
from unittest.mock import Mock
from ansible.errors import AnsibleError

# Import the action module (path setup is in conftest.py)
import get_catalog_info
ActionModule = get_catalog_info.ActionModule


class TestGetCatalogInfo:
    """Tests for get_catalog_info action plugin"""

    @pytest.fixture
    def action_module(self, action_module_base):
        """Create ActionModule instance"""
        module = ActionModule(**action_module_base)
        return module

    def test_successful_catalog_retrieval(self, action_module):
        """Test successful catalog information retrieval with real catalog data"""
        # Arrange - use a real catalog that exists
        action_module._task.args = {
            'mas_catalog_version': 'v9-260129-amd64',
            'fail_if_catalog_does_not_exist': False
        }

        # Act - uses REAL getCatalog() function from mas.devops.data
        result = action_module.run()

        # Assert
        assert result['success'] is True
        assert result['failed'] is False
        assert result['id'] == 'v9-260129-amd64'
        assert 'catalog_digest' in result

    def test_missing_catalog_version_raises_error(self, action_module):
        """Test that missing mas_catalog_version raises AnsibleError"""
        # Arrange
        action_module._task.args = {}

        # Act & Assert
        with pytest.raises(AnsibleError, match="mas_catalog_version argument was not provided"):
            action_module.run()

    def test_invalid_catalog_version_type_raises_error(self, action_module):
        """Test that non-string mas_catalog_version raises AnsibleError"""
        # Arrange
        action_module._task.args = {
            'mas_catalog_version': 12345,  # Should be string
            'fail_if_catalog_does_not_exist': False
        }

        # Act & Assert
        with pytest.raises(AnsibleError, match="mas_catalog_version argument is not a string"):
            action_module.run()

    def test_invalid_fail_flag_type_raises_error(self, action_module):
        """Test that non-boolean fail_if_catalog_does_not_exist raises AnsibleError"""
        # Arrange
        action_module._task.args = {
            'mas_catalog_version': 'v9-240625-amd64',
            'fail_if_catalog_does_not_exist': 'yes'  # Should be boolean
        }

        # Act & Assert
        with pytest.raises(AnsibleError, match="fail_if_catalog_does_not_exist argument is not a boolean"):
            action_module.run()

    def test_catalog_not_found_without_fail_flag(self, action_module):
        """Test catalog not found with fail_if_catalog_does_not_exist=False"""
        # Arrange - use a catalog ID that doesn't exist
        action_module._task.args = {
            'mas_catalog_version': 'invalid-catalog-xyz-999',
            'fail_if_catalog_does_not_exist': False
        }

        # Act - uses REAL getCatalog() which will return None
        result = action_module.run()

        # Assert
        assert result['success'] is False
        assert result['failed'] is False  # Should not fail when flag is False
        assert 'invalid-catalog-xyz-999' in result['message']
        assert result['id'] == 'invalid-catalog-xyz-999'

    def test_catalog_not_found_with_fail_flag(self, action_module):
        """Test catalog not found with fail_if_catalog_does_not_exist=True"""
        # Arrange - use a catalog ID that doesn't exist
        action_module._task.args = {
            'mas_catalog_version': 'invalid-catalog-xyz-999',
            'fail_if_catalog_does_not_exist': True
        }

        # Act & Assert - should raise AnsibleError when flag is True
        with pytest.raises(AnsibleError, match="Catalog invalid-catalog-xyz-999 is unknown"):
            action_module.run()

# Made with Bob
