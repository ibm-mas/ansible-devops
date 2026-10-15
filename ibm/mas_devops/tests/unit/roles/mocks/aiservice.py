"""
AIService resource mixin for FakeKubernetesServer.

Provides the API discovery constants, resource factory functions, HTTP routing
logic, and developer-facing add_* methods for AIService custom resources:

  aiservice.ibm.com/v1:
  - AIServiceTenant
"""

from typing import Dict, Optional


# ---------------------------------------------------------------------------
# API discovery constants
# ---------------------------------------------------------------------------

API_GROUP = {
    "kind": "APIGroup",
    "apiVersion": "v1",
    "name": "aiservice.ibm.com",
    "versions": [{"groupVersion": "aiservice.ibm.com/v1", "version": "v1"}],
    "preferredVersion": {"groupVersion": "aiservice.ibm.com/v1", "version": "v1"},
}

API_GROUP_LIST_ENTRY = {
    "name": "aiservice.ibm.com",
    "versions": [{"groupVersion": "aiservice.ibm.com/v1", "version": "v1"}],
    "preferredVersion": {"groupVersion": "aiservice.ibm.com/v1", "version": "v1"},
}

RESOURCE_LIST = {
    "kind": "APIResourceList",
    "apiVersion": "v1",
    "groupVersion": "aiservice.ibm.com/v1",
    "resources": [
        {
            "name": "aiservicetenants",
            "singularName": "aiservicetenant",
            "namespaced": True,
            "kind": "AIServiceTenant",
            "verbs": ["get", "list"],
        },
    ],
}

_API_VERSION = "aiservice.ibm.com/v1"


# ---------------------------------------------------------------------------
# Resource factory
# ---------------------------------------------------------------------------


def make_aiservice_tenant(namespace: str, name: str, reconciled_version: str) -> dict:
    """Return a minimal AIServiceTenant object.

    Args:
        namespace (str): Kubernetes namespace
        name (str): AIServiceTenant name
        reconciled_version (str): Version string in status.versions.reconciled
            (e.g. "9.1.2")

    Returns:
        dict: AIServiceTenant resource body
    """
    return {
        "apiVersion": _API_VERSION,
        "kind": "AIServiceTenant",
        "metadata": {"name": name, "namespace": namespace},
        "spec": {},
        "status": {
            "conditions": [{"type": "Ready", "status": "True", "reason": "Ready"}],
            "versions": {"reconciled": reconciled_version},
        },
    }


# ---------------------------------------------------------------------------
# Mixin
# ---------------------------------------------------------------------------


class AIServiceMixin:
    """Mixin for FakeKubernetesServer — adds AIService custom resource state and routing.

    Attributes:
        _aiservice_tenants: In-memory store of AIServiceTenant resources keyed by (namespace, name).
    """

    def _init_aiservice(self):
        """Initialise the AIService resource stores. Called by FakeKubernetesServer.__init__."""
        self._aiservice_tenants: Dict[tuple, dict] = {}

    # ------------------------------------------------------------------
    # Developer-facing API
    # ------------------------------------------------------------------

    def add_aiservice_tenant(self, namespace: str, name: str, reconciled_version: str):
        """Register an AIServiceTenant in the fake server.

        Args:
            namespace (str): Kubernetes namespace
            name (str): AIServiceTenant name
            reconciled_version (str): Version in status.versions.reconciled (e.g. "9.1.2")
        """
        self._aiservice_tenants[(namespace, name)] = make_aiservice_tenant(namespace, name, reconciled_version)

    # ------------------------------------------------------------------
    # Internal routing (called by _Handler via generic dispatch)
    # ------------------------------------------------------------------

    def _handle_apis_get(self, ns: str, resource: str, name: Optional[str]) -> Optional[tuple]:
        """Handle a GET for an AIService namespaced resource.

        Returns None if the resource is not owned by this mixin.

        Args:
            ns (str): Namespace
            resource (str): Plural resource name
            name (str, optional): Resource name, or None for a list request

        Returns:
            tuple: (http_status, response_body_dict), or None if not handled
        """
        if resource != "aiservicetenants":
            return None

        if name:
            obj = self._aiservice_tenants.get((ns, name))
            if obj:
                return 200, obj
            return 404, {
                "kind": "Status", "apiVersion": "v1", "status": "Failure",
                "message": f'AIServiceTenant "{name}" not found', "reason": "NotFound", "code": 404,
            }

        items = [v for (n, _), v in self._aiservice_tenants.items() if n == ns]
        return 200, {"apiVersion": _API_VERSION, "kind": "AIServiceTenantList", "metadata": {}, "items": items}
