"""
Shared fixtures for all tests in the MAS DevOps test suite.

This module provides common fixtures that can be used across all test modules,
including mock objects for Ansible tasks, Kubernetes clients, and display utilities.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
import sys
import os
import types

# If ansible / ansible_collections are not installed in the current environment,
# stub them so unit tests can run standalone.
if 'ansible' not in sys.modules:
    try:
        __import__('ansible')
    except ModuleNotFoundError:
        ansible_mod = types.ModuleType('ansible')
        errors_mod = types.ModuleType('ansible.errors')

        class AnsibleError(Exception):
            pass

        errors_mod.AnsibleError = AnsibleError
        ansible_mod.errors = errors_mod

        plugins_mod = types.ModuleType('ansible.plugins')
        action_mod = types.ModuleType('ansible.plugins.action')

        class ActionBase:
            def __init__(self, task=None, connection=None, play_context=None, loader=None, templar=None, shared_loader_obj=None):
                self._task = task
                self._connection = connection
                self._play_context = play_context
                self._loader = loader
                self._templar = templar
                self._shared_loader_obj = shared_loader_obj

            def run(self, tmp=None, task_vars=None):
                return {}

        action_mod.ActionBase = ActionBase
        plugins_mod.action = action_mod
        ansible_mod.plugins = plugins_mod

        utils_mod = types.ModuleType('ansible.utils')
        display_mod = types.ModuleType('ansible.utils.display')

        class Display:
            def v(self, *args, **kwargs):
                pass

            def vv(self, *args, **kwargs):
                pass

            def vvv(self, *args, **kwargs):
                pass

            def error(self, *args, **kwargs):
                pass

            def warning(self, *args, **kwargs):
                pass

            def display(self, *args, **kwargs):
                pass

        display_mod.Display = Display
        utils_mod.display = display_mod
        ansible_mod.utils = utils_mod

        sys.modules['ansible'] = ansible_mod
        sys.modules['ansible.errors'] = errors_mod
        sys.modules['ansible.plugins'] = plugins_mod
        sys.modules['ansible.plugins.action'] = action_mod
        sys.modules['ansible.utils'] = utils_mod
        sys.modules['ansible.utils.display'] = display_mod

if 'ansible_collections' not in sys.modules:
    try:
        __import__('ansible_collections')
    except ModuleNotFoundError:
        ac_mod = types.ModuleType('ansible_collections')
        k8s_mod = types.ModuleType('ansible_collections.kubernetes.core.plugins.module_utils.k8s.client')
        k8s_mod.get_api_client = Mock()
        sys.modules['ansible_collections'] = ac_mod
        sys.modules['ansible_collections.kubernetes'] = types.ModuleType('ansible_collections.kubernetes')
        sys.modules['ansible_collections.kubernetes.core'] = types.ModuleType('ansible_collections.kubernetes.core')
        sys.modules['ansible_collections.kubernetes.core.plugins'] = types.ModuleType('ansible_collections.kubernetes.core.plugins')
        sys.modules['ansible_collections.kubernetes.core.plugins.module_utils'] = types.ModuleType(
            'ansible_collections.kubernetes.core.plugins.module_utils'
        )
        sys.modules['ansible_collections.kubernetes.core.plugins.module_utils.k8s'] = types.ModuleType(
            'ansible_collections.kubernetes.core.plugins.module_utils.k8s'
        )
        sys.modules['ansible_collections.kubernetes.core.plugins.module_utils.k8s.client'] = k8s_mod

# Add the mocks directory to the path so we can import mock helpers
# Path: unit/plugins/conftest.py -> mocks/
mocks_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'mocks'))
if mocks_path not in sys.path:
    sys.path.insert(0, mocks_path)


@pytest.fixture
def mock_task():
    """
    Mock Ansible task object.

    Returns:
        Mock: A mock task object with an empty args dictionary.
    """
    task = Mock()
    task.args = {}
    task.async_val = False  # Disable async to avoid ActionBase errors
    task.action = 'test_action'  # Set a default action name
    return task


@pytest.fixture
def mock_dynamic_client():
    """
    Mock Kubernetes DynamicClient.

    Returns:
        MagicMock: A mock DynamicClient with resources.get() method.
    """
    client = MagicMock()
    return client


@pytest.fixture
def mock_display():
    """
    Mock Ansible Display for logging.

    Yields:
        Mock: A mock Display object for capturing log output.
    """
    with patch('ansible.utils.display.Display') as mock:
        yield mock.return_value


@pytest.fixture
def mock_get_api_client(mock_dynamic_client):
    """
    Mock the get_api_client function from kubernetes.core.

    Args:
        mock_dynamic_client: The mock DynamicClient to return.

    Yields:
        Mock: A patched get_api_client function.
    """
    with patch('ansible_collections.kubernetes.core.plugins.module_utils.k8s.client.get_api_client') as mock:
        mock.return_value = mock_dynamic_client
        yield mock


@pytest.fixture
def action_module_dependencies():
    """
    Provide common dependencies for ActionModule instantiation.

    Returns:
        dict: Dictionary containing mock objects for ActionModule dependencies.
    """
    return {
        'connection': Mock(),
        'play_context': Mock(),
        'loader': Mock(),
        'templar': Mock(),
        'shared_loader_obj': Mock()
    }

# Made with Bob
