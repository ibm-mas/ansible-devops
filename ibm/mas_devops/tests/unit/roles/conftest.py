"""
Shared fixtures for role unit tests.

Provides a started FakeKubernetesServer for each test and ensures the mocks
package is on sys.path so all role test modules can import from it directly.
"""

import sys
import os

import pytest

# Ensure the mocks package and utils module are importable from any role test module
_roles_tests_path = os.path.abspath(os.path.dirname(__file__))
_mocks_path = os.path.join(_roles_tests_path, "mocks")
for _p in (_roles_tests_path, _mocks_path):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from fake_k8s_server import FakeKubernetesServer  # noqa: E402


@pytest.fixture
def fake_k8s():
    """Start a FakeKubernetesServer and yield it for the duration of the test.

    Yields:
        FakeKubernetesServer: A running fake Kubernetes API server. Tests use
            the add_* methods to seed state before running a playbook and
            get_deleted() to assert on what was removed.
    """
    with FakeKubernetesServer() as server:
        yield server
