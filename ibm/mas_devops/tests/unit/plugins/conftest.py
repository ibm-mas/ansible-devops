"""
Shared fixtures for all tests in the MAS DevOps test suite.

This module provides common fixtures that can be used across all test modules,
including mock objects for Ansible tasks, Kubernetes clients, and display utilities.
"""
import os
import sys
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add the mocks directory to the path so we can import mock helpers
# Path: unit/plugins/conftest.py -> mocks/
mocks_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'mocks'))
if mocks_path not in sys.path:
    sys.path.insert(0, mocks_path)


# Make the collection importable as ansible_collections.ibm.mas_devops, so that
# the plugins under test can import shared helpers from plugins/module_utils
# the same way ansible's collection loader resolves them at runtime. The repo
# root (the directory containing ibm/) is added to the namespace package path:
# ansible_collections is a native namespace package, so it merges entries
# (site-packages holds kubernetes.core etc., the repo root holds ibm/).
import ansible_collections  # noqa: E402

# Note: ansible_collections.__path__ is a dynamic _NamespacePath that is
# recomputed (dropping manual appends) whenever sys.path is mutated, which
# pytest's prepend import mode does during collection. Replacing it with a
# plain list freezes the entries, so the repo root survives.
# From tests/unit/plugins the repo root is five levels up
# (plugins -> unit -> tests -> mas_devops -> ibm -> repo root).
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))
if repo_root not in list(ansible_collections.__path__):
    ansible_collections.__path__ = [*ansible_collections.__path__, repo_root]


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
