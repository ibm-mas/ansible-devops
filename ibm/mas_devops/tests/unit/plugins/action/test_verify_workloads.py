"""
Unit tests for verify_workloads action plugin.
"""

import pytest
from unittest.mock import Mock, patch
from ansible.errors import AnsibleError

import verify_workloads
ActionModule = verify_workloads.ActionModule


class TestVerifyWorkloads:
    """Test cases for verify_workloads action plugin."""

    @pytest.fixture
    def action_module(self, action_module_base):
        """Create ActionModule instance"""
        module = ActionModule(**action_module_base)
        return module

    def test_all_workloads_healthy_first_attempt(self, action_module, mock_display):
        """Test when all workloads are healthy on first attempt."""
        # Arrange
        action_module._task.args = {
            'host': 'https://api.example.com',
            'api_key': 'test-key',
            'retries': 3,
            'delay': 5
        }

        # Create healthy deployment
        mock_dep = Mock()
        mock_dep.metadata.namespace = 'mas-inst1-core'
        mock_dep.metadata.name = 'mas-core-api'
        mock_dep.status.replicas = 2
        mock_dep.status.readyReplicas = 2
        mock_dep.status.updatedReplicas = 2
        mock_dep.status.availableReplicas = 2

        mock_deps = Mock()
        mock_deps.items = [mock_dep]

        # Create healthy statefulset
        mock_sts = Mock()
        mock_sts.metadata.namespace = 'mas-inst1-core'
        mock_sts.metadata.name = 'mas-core-db'
        mock_sts.status.replicas = 1
        mock_sts.status.readyReplicas = 1
        mock_sts.status.updatedReplicas = 1
        mock_sts.status.availableReplicas = 1

        mock_stss = Mock()
        mock_stss.items = [mock_sts]

        mock_dep_resource = Mock()
        mock_dep_resource.get.return_value = mock_deps

        mock_sts_resource = Mock()
        mock_sts_resource.get.return_value = mock_stss

        mock_resources = Mock()
        mock_resources.get.side_effect = [mock_dep_resource, mock_sts_resource]

        mock_client = Mock()
        mock_client.resources = mock_resources

        # Act
        with patch('verify_workloads.get_api_client', return_value=mock_client):
            result = action_module.run()

        # Assert
        assert result['failed'] is False
        assert result['changed'] is False
        assert 'All Deployments are healthy' in result['message']
        assert 'All StatefulSets are healthy' in result['message']

    def test_workloads_healthy_after_retry(self, action_module, mock_display):
        """Test when workloads become healthy after retry."""
        # Arrange
        action_module._task.args = {
            'retries': 3,
            'delay': 1
        }

        # First attempt: not ready
        mock_dep_first = Mock()
        mock_dep_first.metadata.namespace = 'mas-inst1-core'
        mock_dep_first.metadata.name = 'mas-core-api'
        mock_dep_first.status.replicas = 2
        mock_dep_first.status.readyReplicas = 1
        mock_dep_first.status.updatedReplicas = 2
        mock_dep_first.status.availableReplicas = 1

        mock_deps_first = Mock()
        mock_deps_first.items = [mock_dep_first]

        # Second attempt: ready
        mock_dep_second = Mock()
        mock_dep_second.metadata.namespace = 'mas-inst1-core'
        mock_dep_second.metadata.name = 'mas-core-api'
        mock_dep_second.status.replicas = 2
        mock_dep_second.status.readyReplicas = 2
        mock_dep_second.status.updatedReplicas = 2
        mock_dep_second.status.availableReplicas = 2

        mock_deps_second = Mock()
        mock_deps_second.items = [mock_dep_second]

        mock_dep_resource = Mock()
        mock_dep_resource.get.side_effect = [mock_deps_first, mock_deps_second]

        # StatefulSets always healthy
        mock_stss = Mock()
        mock_stss.items = []

        mock_sts_resource = Mock()
        mock_sts_resource.get.return_value = mock_stss

        mock_resources = Mock()
        mock_resources.get.side_effect = [mock_dep_resource, mock_sts_resource]

        mock_client = Mock()
        mock_client.resources = mock_resources

        # Act
        with patch('verify_workloads.get_api_client', return_value=mock_client):
            with patch('verify_workloads.time.sleep') as mock_sleep:
                result = action_module.run()

        # Assert
        assert result['failed'] is False
        mock_sleep.assert_called_once_with(1)

    def test_workloads_not_healthy_after_retries(self, action_module, mock_display):
        """Test when workloads remain unhealthy after all retries."""
        # Arrange
        action_module._task.args = {
            'retries': 2,
            'delay': 1
        }

        mock_dep = Mock()
        mock_dep.metadata.namespace = 'mas-inst1-core'
        mock_dep.metadata.name = 'mas-core-api'
        mock_dep.status.replicas = 2
        mock_dep.status.readyReplicas = 1
        mock_dep.status.updatedReplicas = 2
        mock_dep.status.availableReplicas = 1

        mock_deps = Mock()
        mock_deps.items = [mock_dep]

        mock_dep_resource = Mock()
        mock_dep_resource.get.return_value = mock_deps

        mock_resources = Mock()
        mock_resources.get.return_value = mock_dep_resource

        mock_client = Mock()
        mock_client.resources = mock_resources

        # Act & Assert
        with patch('verify_workloads.get_api_client', return_value=mock_client):
            with patch('verify_workloads.time.sleep'):
                with pytest.raises(AnsibleError, match="These Deployments are not healthy"):
                    action_module.run()

    def test_disabled_workloads_ignored(self, action_module, mock_display):
        """Test that disabled workloads (0 replicas) are ignored."""
        # Arrange
        action_module._task.args = {
            'retries': 1,
            'delay': 1
        }

        mock_dep = Mock()
        mock_dep.metadata.namespace = 'mas-inst1-core'
        mock_dep.metadata.name = 'mas-core-optional'
        mock_dep.status.replicas = 0
        mock_dep.status.readyReplicas = 0
        mock_dep.status.updatedReplicas = 0
        mock_dep.status.availableReplicas = 0

        mock_deps = Mock()
        mock_deps.items = [mock_dep]

        mock_dep_resource = Mock()
        mock_dep_resource.get.return_value = mock_deps

        mock_stss = Mock()
        mock_stss.items = []

        mock_sts_resource = Mock()
        mock_sts_resource.get.return_value = mock_stss

        mock_resources = Mock()
        mock_resources.get.side_effect = [mock_dep_resource, mock_sts_resource]

        mock_client = Mock()
        mock_client.resources = mock_resources

        # Act
        with patch('verify_workloads.get_api_client', return_value=mock_client):
            result = action_module.run()

        # Assert
        assert result['failed'] is False
        assert result['deployments']['resources']['disabled']

    def test_ignored_workloads_list(self, action_module, mock_display):
        """Test that specific workloads in ignore list are skipped."""
        # Arrange
        action_module._task.args = {
            'retries': 1,
            'delay': 1
        }

        # Create workload that should be ignored
        mock_dep = Mock()
        mock_dep.metadata.namespace = 'ibm-cpd'
        mock_dep.metadata.name = 'wd-discovery-ranker-rest'
        mock_dep.status.replicas = 1
        mock_dep.status.readyReplicas = None
        mock_dep.status.updatedReplicas = 1
        mock_dep.status.availableReplicas = None

        mock_deps = Mock()
        mock_deps.items = [mock_dep]

        mock_dep_resource = Mock()
        mock_dep_resource.get.return_value = mock_deps

        mock_stss = Mock()
        mock_stss.items = []

        mock_sts_resource = Mock()
        mock_sts_resource.get.return_value = mock_stss

        mock_resources = Mock()
        mock_resources.get.side_effect = [mock_dep_resource, mock_sts_resource]

        mock_client = Mock()
        mock_client.resources = mock_resources

        # Act
        with patch('verify_workloads.get_api_client', return_value=mock_client):
            result = action_module.run()

        # Assert
        assert result['failed'] is False
        assert result['deployments']['resources']['ignored']

    def test_mixed_healthy_and_unhealthy_workloads(self, action_module, mock_display):
        """Test with mix of healthy and unhealthy workloads."""
        # Arrange
        action_module._task.args = {
            'retries': 1,
            'delay': 1
        }

        # Healthy deployment
        mock_dep1 = Mock()
        mock_dep1.metadata.namespace = 'mas-inst1-core'
        mock_dep1.metadata.name = 'mas-core-api'
        mock_dep1.status.replicas = 2
        mock_dep1.status.readyReplicas = 2
        mock_dep1.status.updatedReplicas = 2
        mock_dep1.status.availableReplicas = 2

        # Unhealthy deployment
        mock_dep2 = Mock()
        mock_dep2.metadata.namespace = 'mas-inst1-core'
        mock_dep2.metadata.name = 'mas-core-worker'
        mock_dep2.status.replicas = 2
        mock_dep2.status.readyReplicas = 1
        mock_dep2.status.updatedReplicas = 2
        mock_dep2.status.availableReplicas = 1

        mock_deps = Mock()
        mock_deps.items = [mock_dep1, mock_dep2]

        mock_dep_resource = Mock()
        mock_dep_resource.get.return_value = mock_deps

        mock_resources = Mock()
        mock_resources.get.return_value = mock_dep_resource

        mock_client = Mock()
        mock_client.resources = mock_resources

        # Act & Assert
        with patch('verify_workloads.get_api_client', return_value=mock_client):
            with patch('verify_workloads.time.sleep'):
                with pytest.raises(AnsibleError, match="mas-inst1-core/mas-core-worker"):
                    action_module.run()

# Made with Bob
