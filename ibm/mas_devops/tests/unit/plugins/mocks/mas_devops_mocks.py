"""
Reusable MAS DevOps module mocks for testing.

This module provides factory functions to create mock objects for
MAS DevOps specific modules like catalog data and storage classes.
"""
from unittest.mock import Mock
from typing import Dict, Any, Optional


def create_mock_catalog_data(
    catalog_id: str = "v9-240625-amd64",
    version: str = "9.0.0",
    digest: str = "sha256:abc123def456",
    operators: Optional[list] = None
) -> Dict[str, Any]:
    """
    Create mock catalog data.

    Args:
        catalog_id: Catalog identifier
        version: MAS version
        digest: Image digest
        operators: List of operator names

    Returns:
        dict: Mock catalog data dictionary.
    """
    return {
        'id': catalog_id,
        'version': version,
        'digest': digest,
        'operators': operators or ['ibm-mas', 'ibm-sls', 'ibm-truststore-mgr'],
        'image': f'icr.io/cpopen/ibm-mas-operator-catalog:{catalog_id}',
        'architecture': catalog_id.split('-')[-1] if '-' in catalog_id else 'amd64'
    }


def create_mock_storage_classes(
    provider: str = "ocs",
    rwo: str = "ocs-storagecluster-ceph-rbd",
    rwx: str = "ocs-storagecluster-cephfs",
    file: Optional[str] = None,
    block: Optional[str] = None
) -> Mock:
    """
    Create mock storage classes object.

    Args:
        provider: Storage provider name
        rwo: ReadWriteOnce storage class
        rwx: ReadWriteMany storage class
        file: File storage class (optional)
        block: Block storage class (optional)

    Returns:
        Mock: Mock storage classes object with provider and class attributes.
    """
    storage = Mock()
    storage.provider = provider
    storage.rwo = rwo
    storage.rwx = rwx
    storage.file = file or rwx
    storage.block = block or rwo
    return storage


def create_mock_subscription_result(
    name: str = "test-subscription",
    namespace: str = "test-ns",
    package_name: str = "test-package",
    channel: str = "stable"
) -> Mock:
    """
    Create mock subscription result from applySubscription.

    Args:
        name: Subscription name
        namespace: Subscription namespace
        package_name: Package name
        channel: Subscription channel

    Returns:
        Mock: Mock subscription object.
    """
    subscription = Mock()
    subscription.metadata.name = name
    subscription.metadata.namespace = namespace
    subscription.spec.name = package_name
    subscription.spec.channel = channel
    subscription.to_dict.return_value = {
        'metadata': {'name': name, 'namespace': namespace},
        'spec': {'name': package_name, 'channel': channel}
    }
    return subscription


def create_mock_secret(
    name: str = "ibm-entitlement",
    namespace: str = "test-ns",
    data: Optional[Dict[str, str]] = None
) -> Mock:
    """
    Create mock Kubernetes secret.

    Args:
        name: Secret name
        namespace: Secret namespace
        data: Secret data dictionary

    Returns:
        Mock: Mock secret object.
    """
    secret = Mock()
    secret.metadata.name = name
    secret.metadata.namespace = namespace
    secret.data = data or {'.dockerconfigjson': 'base64encodeddata'}
    secret.to_dict.return_value = {
        'metadata': {'name': name, 'namespace': namespace},
        'data': secret.data
    }
    return secret


def create_mock_namespace(
    name: str = "test-ns",
    labels: Optional[Dict[str, str]] = None
) -> Mock:
    """
    Create mock Kubernetes namespace.

    Args:
        name: Namespace name
        labels: Namespace labels

    Returns:
        Mock: Mock namespace object.
    """
    namespace = Mock()
    namespace.metadata.name = name
    namespace.metadata.labels = labels or {}
    namespace.to_dict.return_value = {
        'metadata': {
            'name': name,
            'labels': namespace.metadata.labels
        }
    }
    return namespace


def create_mock_app_ready_result(
    is_ready: bool = True,
    instance_id: str = "test-instance",
    app_id: str = "manage",
    workspace_id: Optional[str] = None
) -> bool:
    """
    Create mock result from waitForAppReady.

    Args:
        is_ready: Whether the app is ready
        instance_id: MAS instance ID
        app_id: Application ID
        workspace_id: Workspace ID (optional)

    Returns:
        bool: Mock ready status.
    """
    return is_ready


def create_mock_global_pull_secret_result(
    changed: bool = True,
    name: str = "pull-secret",
    namespace: str = "openshift-config",
    registry: str = "cp.icr.io"
) -> Dict[str, Any]:
    """
    Create mock result from updateGlobalPullSecret.

    Args:
        changed: Whether the secret was changed
        name: Secret name
        namespace: Secret namespace
        registry: Registry URL

    Returns:
        dict: Mock result dictionary.
    """
    return {
        'changed': changed,
        'name': name,
        'namespace': namespace,
        'registry': registry
    }

# Made with Bob
