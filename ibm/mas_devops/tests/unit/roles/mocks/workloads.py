"""
Workload resource mixin for FakeKubernetesServer.

Provides the API discovery constants, resource factory functions, HTTP routing
logic, and developer-facing add_* methods for core v1 workload resources:

  Core v1 (api/v1):
  - ServiceAccount
  - ConfigMap
  - Secret

These resources are registered with empty-list GET responses by default, which
is sufficient for tasks that only need the calls not to fail (e.g. label-selector
deletes that may find nothing). Use add_configmap(), add_secret() etc. to seed
specific objects when a test needs to assert on their presence or deletion.

RBAC resources (Role, RoleBinding) are in rbac.py.
"""

from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# API discovery constants
# ---------------------------------------------------------------------------

CORE_V1_RESOURCE_LIST = {
    "kind": "APIResourceList",
    "apiVersion": "v1",
    "groupVersion": "v1",
    "resources": [
        {"name": "serviceaccounts", "singularName": "serviceaccount", "namespaced": True, "kind": "ServiceAccount", "verbs": ["delete", "get", "list"]},
        {"name": "configmaps", "singularName": "configmap", "namespaced": True, "kind": "ConfigMap", "verbs": ["delete", "get", "list"]},
        {"name": "secrets", "singularName": "secret", "namespaced": True, "kind": "Secret", "verbs": ["delete", "get", "list"]},
    ],
}

_KIND_MAP = {
    "serviceaccounts": "ServiceAccount",
    "configmaps": "ConfigMap",
    "secrets": "Secret",
}


# ---------------------------------------------------------------------------
# Resource factories
# ---------------------------------------------------------------------------


def make_service_account(namespace: str, name: str) -> dict:
    """Return a minimal ServiceAccount object.

    Args:
        namespace (str): Kubernetes namespace
        name (str): ServiceAccount name

    Returns:
        dict: ServiceAccount resource body
    """
    return {
        "apiVersion": "v1",
        "kind": "ServiceAccount",
        "metadata": {"name": name, "namespace": namespace},
    }


def make_configmap(namespace: str, name: str, data: dict = None) -> dict:
    """Return a minimal ConfigMap object.

    Args:
        namespace (str): Kubernetes namespace
        name (str): ConfigMap name
        data (dict, optional): ConfigMap data. Defaults to empty dict.

    Returns:
        dict: ConfigMap resource body
    """
    return {
        "apiVersion": "v1",
        "kind": "ConfigMap",
        "metadata": {"name": name, "namespace": namespace},
        "data": data or {},
    }


def make_secret(namespace: str, name: str, data: dict = None) -> dict:
    """Return a minimal Secret object.

    Args:
        namespace (str): Kubernetes namespace
        name (str): Secret name
        data (dict, optional): Secret data (base64-encoded values). Defaults to empty dict.

    Returns:
        dict: Secret resource body
    """
    return {
        "apiVersion": "v1",
        "kind": "Secret",
        "metadata": {"name": name, "namespace": namespace},
        "data": data or {},
    }


# ---------------------------------------------------------------------------
# Mixin
# ---------------------------------------------------------------------------


class WorkloadsMixin:
    """Mixin for FakeKubernetesServer — adds core v1 resource state and routing.

    By default, GET requests return empty lists, which satisfies tasks that perform
    label-selector deletes and expect no results. Seed specific resources with
    add_configmap(), add_secret() etc. when a test needs to assert on their
    presence or deletion.

    Attributes:
        _service_accounts: In-memory store keyed by (namespace, name).
        _configmaps: In-memory store keyed by (namespace, name).
        _secrets: In-memory store keyed by (namespace, name).
    """

    def _init_workloads(self):
        """Initialise the workload resource stores. Called by FakeKubernetesServer.__init__."""
        self._service_accounts: Dict[tuple, dict] = {}
        self._configmaps: Dict[tuple, dict] = {}
        self._secrets: Dict[tuple, dict] = {}

    # ------------------------------------------------------------------
    # Developer-facing API
    # ------------------------------------------------------------------

    def add_service_account(self, namespace: str, name: str):
        """Register a ServiceAccount in the fake server.

        Args:
            namespace (str): Kubernetes namespace
            name (str): ServiceAccount name
        """
        self._service_accounts[(namespace, name)] = make_service_account(namespace, name)

    def add_configmap(self, namespace: str, name: str, data: dict = None):
        """Register a ConfigMap in the fake server.

        Args:
            namespace (str): Kubernetes namespace
            name (str): ConfigMap name
            data (dict, optional): ConfigMap data key/value pairs. Defaults to empty dict.
        """
        self._configmaps[(namespace, name)] = make_configmap(namespace, name, data)

    def add_secret(self, namespace: str, name: str, data: dict = None):
        """Register a Secret in the fake server.

        Args:
            namespace (str): Kubernetes namespace
            name (str): Secret name
            data (dict, optional): Secret data (base64-encoded values). Defaults to empty dict.
        """
        self._secrets[(namespace, name)] = make_secret(namespace, name, data)

    # ------------------------------------------------------------------
    # Internal routing helpers (called by _Handler)
    # ------------------------------------------------------------------

    def _handle_core_get(self, ns: str, resource: str, name: Optional[str]) -> tuple:
        """Handle a GET for a core v1 namespaced resource.

        Args:
            ns (str): Namespace
            resource (str): Plural resource name (e.g. "configmaps")
            name (str, optional): Resource name, or None for a list request

        Returns:
            tuple: (http_status, response_body_dict)
        """
        store_map = {
            "serviceaccounts": self._service_accounts,
            "configmaps": self._configmaps,
            "secrets": self._secrets,
        }
        if resource not in _KIND_MAP:
            return 404, {"kind": "Status", "status": "Failure", "reason": "NotFound", "code": 404}

        kind = _KIND_MAP[resource]
        store = store_map[resource]

        if name:
            obj = store.get((ns, name))
            if obj:
                return 200, obj
            return 404, {"kind": "Status", "apiVersion": "v1", "status": "Failure",
                         "message": f'{kind} "{name}" not found', "reason": "NotFound", "code": 404}

        items = [v for (n, _), v in store.items() if n == ns]
        return 200, {"apiVersion": "v1", "kind": f"{kind}List", "metadata": {}, "items": items}

    def _handle_core_delete(self, ns: str, resource: str, name: Optional[str]) -> tuple:
        """Handle a DELETE for a core v1 namespaced resource.

        Args:
            ns (str): Namespace
            resource (str): Plural resource name
            name (str, optional): Resource name

        Returns:
            tuple: (http_status, response_body_dict)
        """
        store_map = {
            "serviceaccounts": self._service_accounts,
            "configmaps": self._configmaps,
            "secrets": self._secrets,
        }
        if resource not in _KIND_MAP:
            return 404, {"kind": "Status", "status": "Failure", "reason": "NotFound", "code": 404}

        kind = _KIND_MAP[resource]
        store_map[resource].pop((ns, name), None)
        self._deleted.setdefault(kind, []).append((ns, name))  # type: ignore[attr-defined]
        return 200, {"kind": "Status", "apiVersion": "v1", "status": "Success",
                     "details": {"name": name, "kind": kind.lower() + "s"}, "code": 200}
