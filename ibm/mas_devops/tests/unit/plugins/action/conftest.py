"""
Action plugin specific fixtures.

This module provides fixtures specifically for testing action plugins,
including common setup for ActionModule instantiation.
"""
import pytest
from unittest.mock import Mock
import sys
import os

# This code runs when conftest.py is loaded, BEFORE test collection
# Path structure: ibm/mas_devops/tests/unit/plugins/action/conftest.py
# Navigate: ../../../ (to tests/) then ../.. (to ibm/mas_devops/) then plugins/action
plugins_action_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../plugins/action'))

if plugins_action_path not in sys.path:
    sys.path.insert(0, plugins_action_path)


# Make the collection's module_utils importable under their collection path
# (ansible_collections.ibm.mas_devops.plugins.module_utils.<name>) as action plugins import them.
def _register_module_utils(name):
    import importlib.util
    import types
    full_name = f'ansible_collections.ibm.mas_devops.plugins.module_utils.{name}'
    if full_name in sys.modules:
        return
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), f'../../../../plugins/module_utils/{name}.py'))
    parts = full_name.split('.')
    for i in range(1, len(parts)):
        parent = '.'.join(parts[:i])
        if parent not in sys.modules:
            pkg = types.ModuleType(parent)
            pkg.__path__ = []
            sys.modules[parent] = pkg
    spec = importlib.util.spec_from_file_location(full_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[full_name] = module
    spec.loader.exec_module(module)


_register_module_utils('saas_backup_encryption')


@pytest.fixture
def action_module_base(mock_task):
    """
    Base setup for ActionModule tests.

    Provides common dependencies needed to instantiate any ActionModule.

    Args:
        mock_task: Mock task fixture from root conftest

    Returns:
        dict: Dictionary with all dependencies for ActionModule instantiation.
    """
    return {
        'task': mock_task,
        'connection': Mock(),
        'play_context': Mock(),
        'loader': Mock(),
        'templar': Mock(),
        'shared_loader_obj': Mock()
    }


@pytest.fixture
def mock_k8s_resource():
    """
    Mock Kubernetes resource object.

    Returns:
        Mock: A basic mock Kubernetes resource with metadata and status.
    """
    resource = Mock()
    resource.metadata.name = "test-resource"
    resource.metadata.namespace = "test-namespace"
    resource.status.conditions = []
    resource.to_dict.return_value = {
        'metadata': {
            'name': 'test-resource',
            'namespace': 'test-namespace'
        }
    }
    return resource


@pytest.fixture
def mock_k8s_resource_list(mock_k8s_resource):
    """
    Mock Kubernetes resource list.

    Args:
        mock_k8s_resource: Mock resource fixture

    Returns:
        Mock: A mock resource list containing one resource.
    """
    resource_list = Mock()
    resource_list.items = [mock_k8s_resource]
    return resource_list

# Made with Bob
