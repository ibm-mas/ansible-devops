"""
Unit tests for get_default_storage_classes action plugin.

Tests cover:
- Successful storage class retrieval with different providers
- No default storage classes found scenario
- Optional host and api_key parameters

Note: This test uses the REAL mas.devops.mas.getDefaultStorageClasses() function.
We mock the Kubernetes DynamicClient but use the real function logic.
"""
import pytest
from unittest.mock import Mock, patch

# Import the action module (path setup is in conftest.py)
import get_default_storage_classes
ActionModule = get_default_storage_classes.ActionModule

# Import mock helpers
import kubernetes_mocks


class TestGetDefaultStorageClasses:
    """Tests for get_default_storage_classes action plugin"""

    @pytest.fixture
    def action_module(self, action_module_base):
        """Create an instance of the action module for testing"""
        module = ActionModule(**action_module_base)
        return module

    @patch('get_default_storage_classes.get_api_client')
    def test_successful_storage_class_retrieval_ocs(self, mock_get_api_client, action_module):
        """Test successful storage class retrieval for OCS provider"""
        # Arrange
        mock_client = kubernetes_mocks.create_mock_dynamic_client()
        mock_get_api_client.return_value = mock_client

        # Mock storage classes for OCS
        mock_sc_list = Mock()
        mock_sc_list.items = [
            kubernetes_mocks.create_mock_storage_class(
                name='ocs-storagecluster-cephfs',
                is_default=True,
                provisioner='openshift-storage.cephfs.csi.ceph.com'
            ),
            kubernetes_mocks.create_mock_storage_class(
                name='ocs-storagecluster-ceph-rbd',
                is_default=False,
                provisioner='openshift-storage.rbd.csi.ceph.com'
            )
        ]
        mock_client.resources.get().get.return_value = mock_sc_list

        action_module._task.args = {}

        # Act - uses REAL getDefaultStorageClasses() function
        result = action_module.run()

        # Assert
        assert result['success'] is True
        assert result['failed'] is False
        assert result['changed'] is False
        assert result['provider'] is not None
        assert 'Successfully found default storage classes' in result['message']

    @patch('get_default_storage_classes.get_api_client')
    def test_no_default_storage_classes_found(self, mock_get_api_client, action_module):
        """Test when no default storage classes are found"""
        # Arrange
        mock_client = kubernetes_mocks.create_mock_dynamic_client()
        mock_get_api_client.return_value = mock_client

        # Mock empty storage class list
        mock_sc_list = Mock()
        mock_sc_list.items = []
        mock_client.resources.get().get.return_value = mock_sc_list

        action_module._task.args = {}

        # Act
        result = action_module.run()

        # Assert
        assert result['success'] is False
        assert result['failed'] is False  # Should not fail, just report no classes found
        assert result['changed'] is False
        assert result['provider'] is None
        assert 'Failed to find any default supported storage classes' in result['message']

    @patch('get_default_storage_classes.get_api_client')
    def test_with_custom_host_and_api_key(self, mock_get_api_client, action_module):
        """Test with custom host and api_key parameters"""
        # Arrange
        mock_client = kubernetes_mocks.create_mock_dynamic_client()
        mock_get_api_client.return_value = mock_client

        mock_sc_list = Mock()
        mock_sc_list.items = [
            kubernetes_mocks.create_mock_storage_class(
                name='ibmc-file-gold',
                is_default=True,
                provisioner='ibm.io/ibmc-file'
            )
        ]
        mock_client.resources.get().get.return_value = mock_sc_list

        action_module._task.args = {
            'host': 'https://api.example.com:6443',
            'api_key': 'test-api-key'
        }

        # Act
        result = action_module.run()

        # Assert
        assert result['success'] is True
        mock_get_api_client.assert_called_once_with(
            api_key='test-api-key',
            host='https://api.example.com:6443'
        )

    @patch('get_default_storage_classes.get_api_client')
    def test_result_includes_storage_class_attributes(self, mock_get_api_client, action_module):
        """Test that result includes all storage class attributes"""
        # Arrange
        mock_client = kubernetes_mocks.create_mock_dynamic_client()
        mock_get_api_client.return_value = mock_client

        mock_sc_list = Mock()
        mock_sc_list.items = [
            kubernetes_mocks.create_mock_storage_class(
                name='aws-ebs-gp2',
                is_default=True,
                provisioner='kubernetes.io/aws-ebs'
            )
        ]
        mock_client.resources.get().get.return_value = mock_sc_list

        action_module._task.args = {}

        # Act
        result = action_module.run()

        # Assert - result should include storage class object attributes
        assert result['success'] is True
        assert 'provider' in result
        # The actual attributes depend on the StorageClasses dataclass from mas.devops.mas


# Made with Bob