"""
Unit tests for get_newest_catalog_tag action plugin.

Tests cover:
- Successful catalog tag retrieval
- Missing required parameters
- No catalogs available for architecture

Note: These tests use the REAL mas.devops.data.getNewestCatalogTag() function,
not mocks. We only mock external dependencies like Kubernetes API.

Setup: Install mas.devops package in editable mode:
    pip install -e ../python-devops
"""
import pytest
from unittest.mock import Mock
from ansible.errors import AnsibleError

# Import the action module (path setup is in conftest.py)
import get_newest_catalog_tag
ActionModule = get_newest_catalog_tag.ActionModule


class TestGetNewestCatalogTag:
    """Tests for get_newest_catalog_tag action plugin"""

    @pytest.fixture
    def action_module(self, action_module_base):
        """Create ActionModule instance"""
        module = ActionModule(**action_module_base)
        return module

    def test_successful_catalog_tag_retrieval_amd64(self, action_module):
        """Test successful catalog tag retrieval for amd64"""
        # Arrange
        action_module._task.args = {'arch': 'amd64'}

        # Act - uses REAL getNewestCatalogTag() function from mas.devops.data
        result = action_module.run()

        # Assert
        assert result['failed'] is False
        assert result['changed'] is False
        assert result['arch'] == 'amd64'
        assert result['result'] is not None
        assert 'amd64' in result['result']  # Tag should contain architecture
        assert 'Successfully found newest catalog' in result['message']

    def test_successful_catalog_tag_retrieval_s390x(self, action_module):
        """Test successful catalog tag retrieval for s390x"""
        # Arrange
        action_module._task.args = {'arch': 's390x'}

        # Act - uses REAL getNewestCatalogTag() function
        result = action_module.run()

        # Assert
        assert result['failed'] is False
        assert result['arch'] == 's390x'
        assert result['result'] is not None
        assert 's390x' in result['result']  # Tag should contain architecture

    def test_successful_catalog_tag_retrieval_ppc64le(self, action_module):
        """Test successful catalog tag retrieval for ppc64le"""
        # Arrange
        action_module._task.args = {'arch': 'ppc64le'}

        # Act - uses REAL getNewestCatalogTag() function
        result = action_module.run()

        # Assert
        assert result['failed'] is False
        assert result['arch'] == 'ppc64le'
        assert result['result'] is not None
        assert 'ppc64le' in result['result']  # Tag should contain architecture

    def test_missing_arch_parameter_raises_key_error(self, action_module):
        """Test that missing arch parameter raises KeyError"""
        # Arrange
        action_module._task.args = {}

        # Act & Assert
        with pytest.raises(KeyError):
            action_module.run()

    def test_unsupported_architecture_returns_none(self, action_module):
        """Test that unsupported architecture raises error"""
        # Arrange - use an architecture that doesn't have catalogs
        action_module._task.args = {'arch': 'arm64'}

        # Act & Assert - REAL function will return None, causing AnsibleError
        with pytest.raises(AnsibleError, match="No catalogs available for arm64"):
            action_module.run()

    def test_result_format(self, action_module):
        """Test that result has expected format (vX-YYMMDD-arch)"""
        # Arrange
        action_module._task.args = {'arch': 'amd64'}

        # Act - uses REAL getNewestCatalogTag() function
        result = action_module.run()

        # Assert - verify format
        assert result['result'] is not None
        tag = result['result']
        # Should be in format like "v9-260129-amd64"
        assert tag.startswith('v')
        assert '-' in tag
        parts = tag.split('-')
        assert len(parts) == 3  # v9, date, arch
        assert parts[2] == 'amd64'

# Made with Bob
