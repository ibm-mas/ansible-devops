# MAS DevOps Action Plugin Tests

This directory contains unit tests for the MAS DevOps Ansible action plugins.

## Overview

The test suite provides comprehensive coverage for all 15 action plugins in `ibm/mas_devops/plugins/action/`, using pytest as the testing framework and unittest.mock for mocking **external dependencies only**.

### Important: What We Mock

**✅ WE MOCK (External Dependencies)**:
- Kubernetes API (`get_api_client()`, `DynamicClient`)
- HTTP requests (`requests.get()`, `requests.post()`)
- Time functions (`time.sleep()`)
- Ansible internals (`Display`, `Task`)

**❌ WE DO NOT MOCK (Code Under Test)**:
- `mas.devops.data.*` - Catalog functions (getCatalog, getNewestCatalogTag)
- `mas.devops.olm.*` - OLM functions (applySubscription)
- `mas.devops.ocp.*` - OpenShift functions (createNamespace, updateGlobalPullSecret)
- `mas.devops.mas.*` - MAS functions (waitForAppReady, getDefaultStorageClasses)

**Why?** The action plugins are thin wrappers around `mas.devops` functions from the python-devops package. We test the real integration, only mocking external dependencies.

## Directory Structure

```
tests/
├── README.md                           # This file
├── pytest.ini                          # Pytest configuration
├── requirements-test.txt               # Test dependencies
├── conftest.py                         # Shared fixtures
├── unit/
│   └── plugins/
│       └── action/
│           ├── conftest.py             # Action-specific fixtures
│           ├── test_get_catalog_info.py
│           ├── test_get_newest_catalog_tag.py
│           ├── test_fyre_check_hostname.py
│           └── ... (12 more test files)
└── mocks/
    ├── __init__.py
    ├── kubernetes_mocks.py             # K8s mock helpers
    ├── mas_devops_mocks.py             # MAS DevOps mock helpers
    └── external_api_mocks.py           # HTTP/API mock helpers
```

## Prerequisites

### 1. Install python-devops Package (Editable Mode)

The tests require the `mas.devops` package from python-devops:

```bash
# From the ansible-devops directory
cd ../python-devops
pip install -e .
```

This installs the package in editable mode, so the tests can import `mas.devops` functions normally.

### 2. Install Test Dependencies

```bash
cd ../ansible-devops/ibm/mas_devops/tests
pip install -r requirements-test.txt
```

### Required Packages

- pytest >= 7.4.0
- pytest-cov >= 4.1.0
- pytest-mock >= 3.11.1
- responses >= 0.23.0
- freezegun >= 1.2.2

## Running Tests

### Run All Tests

```bash
cd ibm/mas_devops/tests
pytest
```

### Run Specific Test File

```bash
pytest unit/plugins/action/test_get_catalog_info.py
```

### Run Specific Test Class

```bash
pytest unit/plugins/action/test_get_catalog_info.py::TestGetCatalogInfo
```

### Run Specific Test Method

```bash
pytest unit/plugins/action/test_get_catalog_info.py::TestGetCatalogInfo::test_successful_catalog_retrieval
```

### Run Tests with Coverage

```bash
pytest --cov=../plugins/action --cov-report=html
```

This generates an HTML coverage report in `htmlcov/index.html`.

### Run Tests with Verbose Output

```bash
pytest -v
```

### Run Tests Matching Pattern

```bash
# Run all tests with "missing" in the name
pytest -k "missing"

# Run all tests for catalog-related actions
pytest -k "catalog"
```

### Run Tests by Marker

```bash
# Run only unit tests
pytest -m unit

# Run only Kubernetes-related tests
pytest -m k8s

# Run only external API tests
pytest -m external_api
```

## Test Categories

Tests are organized by the type of action plugin:

### 1. Data/Utility Actions (Simple)
- `test_get_catalog_info.py` - Catalog metadata retrieval
- `test_get_newest_catalog_tag.py` - Latest catalog tag lookup
- `test_get_default_storage_classes.py` - Storage class detection

### 2. External API Actions
- `test_fyre_check_hostname.py` - Fyre hostname availability
- `test_fyre_watch_provision.py` - Fyre cluster provisioning

### 3. Kubernetes Client Actions
- `test_apply_subscription.py` - OLM subscription management
- `test_verify_catalogsources.py` - CatalogSource health checks
- `test_verify_subscriptions.py` - Subscription status verification
- `test_update_ibm_entitlement.py` - Entitlement secret management
- `test_update_global_pull_secret.py` - Global pull secret updates

### 4. Complex Kubernetes Actions
- `test_wait_for_app_ready.py` - MAS application readiness
- `test_verify_app_version.py` - Application version verification
- `test_verify_core_version.py` - Core version verification
- `test_verify_workloads.py` - Deployment/StatefulSet health
- `test_wait_for_conditions.py` - Resource condition polling

## Writing New Tests

### Test File Template

```python
"""
Unit tests for <action_name> action plugin.

Tests cover:
- Successful execution scenarios
- Error handling
- Parameter validation
"""
import pytest
from unittest.mock import patch, Mock
from ansible.errors import AnsibleError

# Import the action module
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../../../plugins/action')))
from <action_name> import ActionModule


class Test<ActionName>:
    """Tests for <action_name> action plugin"""

    @pytest.fixture
    def action_module(self, action_module_base):
        """Create ActionModule instance"""
        module = ActionModule(**action_module_base)
        return module

    def test_successful_execution(self, action_module):
        """Test successful execution with valid inputs"""
        # Arrange
        action_module._task.args = {'param': 'value'}

        # Act
        result = action_module.run()

        # Assert
        assert result['success'] is True
        assert result['failed'] is False
```

### Test Naming Conventions

- **Test files**: `test_<action_name>.py`
- **Test classes**: `Test<ActionName>`
- **Test methods**: `test_<scenario>_<expected_outcome>`

Examples:
- `test_missing_namespace_raises_error`
- `test_successful_subscription_creation`
- `test_catalog_becomes_ready_after_retry`

### AAA Pattern (Arrange-Act-Assert)

Always structure tests using the AAA pattern:

```python
def test_example(self, action_module):
    # Arrange: Set up test data and mocks
    action_module._task.args = {'param': 'value'}
    mock_function.return_value = expected_value

    # Act: Execute the code under test
    result = action_module.run()

    # Assert: Verify the outcome
    assert result['success'] is True
    mock_function.assert_called_once()
```

## Using Mock Helpers

The `mocks/` directory provides reusable mock factories:

### Kubernetes Mocks

```python
from mocks.kubernetes_mocks import (
    create_mock_dynamic_client,
    create_mock_subscription,
    create_mock_catalog_source,
    create_mock_deployment
)

# Create a mock Kubernetes client
mock_client = create_mock_dynamic_client()

# Create a mock subscription
subscription = create_mock_subscription(
    name="test-sub",
    namespace="test-ns",
    state="AtLatestKnown"
)
```

### MAS DevOps Mocks

```python
from mocks.mas_devops_mocks import (
    create_mock_catalog_data,
    create_mock_storage_classes
)

# Create mock catalog data
catalog = create_mock_catalog_data(
    catalog_id="v9-240625-amd64",
    version="9.0.0"
)
```

### External API Mocks

```python
from mocks.external_api_mocks import (
    create_mock_fyre_response,
    create_mock_http_error_response
)

# Create mock Fyre API response
response = create_mock_fyre_response(
    status="success",
    deployed_status="deployed"
)
```

## Using Real mas.devops Functions

**IMPORTANT**: Tests should use the REAL `mas.devops` functions, not mocks.

### Setup

Install the `mas.devops` package in editable mode (see Prerequisites above). Once installed, the action plugins will automatically import and use the real functions.

### Example: Testing with Real Functions

```python
def test_get_catalog_info(self, action_module):
    """Test using REAL getCatalog() function"""
    # Arrange - use a real catalog ID
    action_module._task.args = {
        'mas_catalog_version': 'v9-260129-amd64',
        'fail_if_catalog_does_not_exist': False
    }

    # Act - action plugin calls REAL getCatalog() from mas.devops.data
    result = action_module.run()

    # Assert - verify real catalog data
    assert result['success'] is True
    assert 'digest' in result  # Real data from catalog files
    assert 'operators' in result  # Real operator list
```

**How it works:**
1. Action plugin imports: `from mas.devops.data import getCatalog`
2. Since `mas.devops` is installed via `pip install -e`, it's available normally
3. Test calls `action_module.run()` which uses the real function
4. No mocking needed - tests validate against real catalog data

### When to Mock vs Use Real

| Component | Mock? | Reason |
|-----------|-------|--------|
| `mas.devops.*` functions | ❌ No | Part of codebase under test |
| Kubernetes API | ✅ Yes | External dependency |
| HTTP requests | ✅ Yes | External dependency |
| File system | ✅ Yes | External dependency |
| Time functions | ✅ Yes | Makes tests faster |

## Common Fixtures

### From Root conftest.py

- `mock_task` - Mock Ansible task object
- `mock_dynamic_client` - Mock Kubernetes DynamicClient
- `mock_display` - Mock Ansible Display for logging
- `mock_get_api_client` - Patched get_api_client function

### From Action conftest.py

- `action_module_base` - Base dependencies for ActionModule
- `mock_k8s_resource` - Basic Kubernetes resource
- `mock_k8s_resource_list` - List of Kubernetes resources

## Test Markers

Use pytest markers to categorize tests:

```python
@pytest.mark.unit
def test_something():
    pass

@pytest.mark.k8s
def test_kubernetes_interaction():
    pass

@pytest.mark.external_api
def test_api_call():
    pass

@pytest.mark.slow
def test_long_running():
    pass
```

## Coverage Goals

- **Overall**: ≥80% line coverage
- **Per file**: ≥75% line coverage
- **Critical paths**: 100% coverage

View current coverage:

```bash
pytest --cov=../plugins/action --cov-report=term-missing
```

## Continuous Integration

Tests run automatically on:
- Push to main/develop branches
- Pull requests
- Changes to action plugins or tests

See `.github/workflows/test-action-plugins.yml` for CI configuration.

## Troubleshooting

### Import Errors

If you see import errors for pytest or ansible:

```bash
pip install -r requirements-test.txt
```

### Path Issues

Tests use relative imports. Run pytest from the `tests/` directory:

```bash
cd ibm/mas_devops/tests
pytest
```

### Mock Not Working

Ensure you're patching at the right level:

```python
# ✅ Correct - patch where it's used
@patch('action_module_name.function_name')

# ❌ Wrong - patching the original module
@patch('mas.devops.module.function_name')
```

## Best Practices

1. **Test Independence**: Each test should be independent
2. **Clear Names**: Use descriptive test names
3. **One Assertion Focus**: Test one thing per test method
4. **Mock External Dependencies**: Never make real API calls
5. **Use Fixtures**: Reduce duplication with fixtures
6. **Document Tests**: Add docstrings explaining what's tested

## Contributing

When adding new action plugins:

1. Create corresponding test file
2. Aim for ≥80% coverage
3. Test happy path and error cases
4. Use existing test files as templates
5. Run tests locally before committing

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [unittest.mock Guide](https://docs.python.org/3/library/unittest.mock.html)
- [Ansible Testing Guide](https://docs.ansible.com/ansible/latest/dev_guide/testing.html)
- [Test Plan](../TEST_PLAN.md)

## Support

For questions or issues:
- Check existing test files for examples
- Review the [Test Plan](../TEST_PLAN.md)
- Open an issue in the repository