"""
Shared fixtures for all tests in the MAS DevOps test suite.

This module provides common fixtures that can be used across all test modules,
including mock objects for Ansible tasks, Kubernetes clients, and display utilities.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
import sys
import os

# Add the mocks directory to the path so we can import mock helpers
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
