"""
Reusable Kubernetes mock objects for testing.

This module provides factory functions to create mock Kubernetes objects
including DynamicClient, resource APIs, and Kubernetes resources.
"""
from unittest.mock import Mock, MagicMock
from typing import List, Optional, Dict, Any


def create_mock_dynamic_client() -> MagicMock:
    """
    Create a mock Kubernetes DynamicClient.

    Returns:
        MagicMock: A mock DynamicClient with resources.get() method configured.
    """
    client = MagicMock()
    client.resources.get.return_value = create_mock_resource_api()
    return client


def create_mock_resource_api() -> Mock:
    """
    Create a mock Kubernetes resource API.

    Returns:
        Mock: A mock resource API with get, create, patch, delete methods.
    """
    api = Mock()
    api.get.return_value = create_mock_resource_list()
    api.create.return_value = create_mock_resource()
    api.patch.return_value = create_mock_resource()
    api.delete.return_value = Mock()
    return api


def create_mock_resource(
    name: str = "test-resource",
    namespace: str = "test-ns",
    status: str = "Ready",
    **kwargs
) -> Mock:
    """
    Create a mock Kubernetes resource.

    Args:
        name: Resource name
        namespace: Resource namespace
        status: Resource status
        **kwargs: Additional attributes to set on the resource

    Returns:
        Mock: A mock Kubernetes resource with metadata and status.
    """
    resource = Mock()
    resource.metadata.name = name
    resource.metadata.namespace = namespace
    resource.status.conditions = []

    # Set additional attributes
    for key, value in kwargs.items():
        setattr(resource, key, value)

    resource.to_dict.return_value = {
        'metadata': {
            'name': name,
            'namespace': namespace
        },
        'status': {}
    }
    return resource


def create_mock_resource_list(items: Optional[List[Mock]] = None) -> Mock:
    """
    Create a mock Kubernetes resource list.

    Args:
        items: List of mock resources to include

    Returns:
        Mock: A mock resource list with items attribute.
    """
    resource_list = Mock()
    resource_list.items = items or []
    return resource_list


def create_mock_subscription(
    name: str = "test-subscription",
    namespace: str = "test-ns",
    package_name: str = "test-package",
    channel: str = "stable",
    state: str = "AtLatestKnown"
) -> Mock:
    """
    Create a mock OLM Subscription resource.

    Args:
        name: Subscription name
        namespace: Subscription namespace
        package_name: Package name
        channel: Subscription channel
        state: Subscription state

    Returns:
        Mock: A mock Subscription resource.
    """
    subscription = create_mock_resource(name, namespace)
    subscription.spec.name = package_name
    subscription.spec.channel = channel
    subscription.status.state = state
    subscription.status.installedCSV = f"{package_name}.v1.0.0"
    return subscription


def create_mock_catalog_source(
    name: str = "ibm-operator-catalog",
    namespace: str = "openshift-marketplace",
    connection_state: str = "READY"
) -> Mock:
    """
    Create a mock CatalogSource resource.

    Args:
        name: CatalogSource name
        namespace: CatalogSource namespace
        connection_state: Connection state (READY, CONNECTING, etc.)

    Returns:
        Mock: A mock CatalogSource resource.
    """
    catalog = create_mock_resource(name, namespace)
    catalog.status.connectionState.lastObservedState = connection_state
    return catalog


def create_mock_deployment(
    name: str = "test-deployment",
    namespace: str = "test-ns",
    replicas: int = 1,
    ready_replicas: Optional[int] = None,
    updated_replicas: Optional[int] = None,
    available_replicas: Optional[int] = None
) -> Mock:
    """
    Create a mock Deployment resource.

    Args:
        name: Deployment name
        namespace: Deployment namespace
        replicas: Desired replicas
        ready_replicas: Ready replicas (defaults to replicas)
        updated_replicas: Updated replicas (defaults to replicas)
        available_replicas: Available replicas (defaults to replicas)

    Returns:
        Mock: A mock Deployment resource.
    """
    deployment = create_mock_resource(name, namespace)
    deployment.status.replicas = replicas
    deployment.status.readyReplicas = ready_replicas if ready_replicas is not None else replicas
    deployment.status.updatedReplicas = updated_replicas if updated_replicas is not None else replicas
    deployment.status.availableReplicas = available_replicas if available_replicas is not None else replicas
    return deployment


def create_mock_statefulset(
    name: str = "test-statefulset",
    namespace: str = "test-ns",
    replicas: int = 1,
    ready_replicas: Optional[int] = None,
    updated_replicas: Optional[int] = None,
    available_replicas: Optional[int] = None
) -> Mock:
    """
    Create a mock StatefulSet resource.

    Args:
        name: StatefulSet name
        namespace: StatefulSet namespace
        replicas: Desired replicas
        ready_replicas: Ready replicas (defaults to replicas)
        updated_replicas: Updated replicas (defaults to replicas)
        available_replicas: Available replicas (defaults to replicas)

    Returns:
        Mock: A mock StatefulSet resource.
    """
    sts = create_mock_resource(name, namespace)
    sts.status.replicas = replicas
    sts.status.readyReplicas = ready_replicas if ready_replicas is not None else replicas
    sts.status.updatedReplicas = updated_replicas if updated_replicas is not None else replicas
    sts.status.availableReplicas = available_replicas if available_replicas is not None else replicas
    return sts


def create_mock_mas_suite(
    name: str = "test-instance",
    namespace: str = "mas-test-core",
    version: str = "9.0.0",
    conditions: Optional[List[Dict[str, Any]]] = None
) -> Mock:
    """
    Create a mock MAS Suite resource.

    Args:
        name: Suite instance name
        namespace: Suite namespace
        version: MAS version
        conditions: List of condition dictionaries

    Returns:
        Mock: A mock Suite resource.
    """
    suite = create_mock_resource(name, namespace)
    suite.status.versions.reconciled = version

    if conditions:
        suite.status.conditions = []
        for cond in conditions:
            condition = Mock()
            condition.type = cond.get('type', 'Ready')
            condition.status = cond.get('status', 'True')
            condition.reason = cond.get('reason', 'Ready')
            condition.message = cond.get('message', 'Suite is ready')
            suite.status.conditions.append(condition)

    return suite


def create_mock_mas_app(
    instance_id: str = "test-instance",
    app_id: str = "manage",
    namespace: str = "mas-test-manage",
    version: str = "9.0.0",
    conditions: Optional[List[Dict[str, Any]]] = None
) -> Mock:
    """
    Create a mock MAS Application resource.

    Args:
        instance_id: MAS instance ID
        app_id: Application ID
        namespace: Application namespace
        version: Application version
        conditions: List of condition dictionaries

    Returns:
        Mock: A mock MAS Application resource.
    """
    app = create_mock_resource(instance_id, namespace)
    app.status.versions.reconciled = version

    if conditions:
        app.status.conditions = []
        for cond in conditions:
            condition = Mock()
            condition.type = cond.get('type', 'Ready')
            condition.status = cond.get('status', 'True')
            condition.reason = cond.get('reason', 'Ready')
            condition.message = cond.get('message', 'Application is ready')
            app.status.conditions.append(condition)

    return app

# Made with Bob
