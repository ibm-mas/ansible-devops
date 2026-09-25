"""
RBAC resource mixin for FakeKubernetesServer.

Provides the API discovery constants, resource factory functions, HTTP routing
logic, and developer-facing add_* methods for RBAC resources:

  rbac.authorization.k8s.io/v1:
  - Role
  - RoleBinding

By default, GET requests return empty lists, which is sufficient for tasks that
perform label-selector deletes and expect no results. Use add_role() and
add_role_binding() to seed specific objects when a test needs to assert on
their presence or deletion.
"""

from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# API discovery constants
# ---------------------------------------------------------------------------

API_GROUP = {
    "kind": "APIGroup",
    "apiVersion": "v1",
    "name": "rbac.authorization.k8s.io",
    "versions": [{"groupVersion": "rbac.authorization.k8s.io/v1", "version": "v1"}],
    "preferredVersion": {"groupVersion": "rbac.authorization.k8s.io/v1", "version": "v1"},
}

API_GROUP_LIST_ENTRY = {
    "name": "rbac.authorization.k8s.io",
    "versions": [{"groupVersion": "rbac.authorization.k8s.io/v1", "version": "v1"}],
    "preferredVersion": {"groupVersion": "rbac.authorization.k8s.io/v1", "version": "v1"},
}

RESOURCE_LIST = {
    "kind": "APIResourceList",
    "apiVersion": "v1",
    "groupVersion": "rbac.authorization.k8s.io/v1",
    "resources": [
        {"name": "roles", "singularName": "role", "namespaced": True, "kind": "Role", "verbs": ["delete", "get", "list"]},
        {"name": "rolebindings", "singularName": "rolebinding", "namespaced": True, "kind": "RoleBinding", "verbs": ["delete", "get", "list"]},
    ],
}

_KIND_MAP = {
    "roles": "Role",
    "rolebindings": "RoleBinding",
}


# ---------------------------------------------------------------------------
# Resource factories
# ---------------------------------------------------------------------------


def make_role(namespace: str, name: str, rules: List[dict] = None) -> dict:
    """Return a minimal Role object.

    Args:
        namespace (str): Kubernetes namespace
        name (str): Role name
        rules (List[dict], optional): Policy rules. Defaults to empty list.

    Returns:
        dict: Role resource body
    """
    return {
        "apiVersion": "rbac.authorization.k8s.io/v1",
        "kind": "Role",
        "metadata": {"name": name, "namespace": namespace},
        "rules": rules or [],
    }


def make_role_binding(namespace: str, name: str, role_name: str, subjects: List[dict] = None) -> dict:
    """Return a minimal RoleBinding object.

    Args:
        namespace (str): Kubernetes namespace
        name (str): RoleBinding name
        role_name (str): Name of the Role this binding references
        subjects (List[dict], optional): Subjects list. Defaults to empty list.

    Returns:
        dict: RoleBinding resource body
    """
    return {
        "apiVersion": "rbac.authorization.k8s.io/v1",
        "kind": "RoleBinding",
        "metadata": {"name": name, "namespace": namespace},
        "roleRef": {"apiGroup": "rbac.authorization.k8s.io", "kind": "Role", "name": role_name},
        "subjects": subjects or [],
    }


# ---------------------------------------------------------------------------
# Mixin
# ---------------------------------------------------------------------------


class RbacMixin:
    """Mixin for FakeKubernetesServer — adds RBAC resource state and routing.

    Attributes:
        _roles: In-memory store of Role resources keyed by (namespace, name).
        _role_bindings: In-memory store of RoleBinding resources keyed by (namespace, name).
    """

    def _init_rbac(self):
        """Initialise the RBAC resource stores. Called by FakeKubernetesServer.__init__."""
        self._roles: Dict[tuple, dict] = {}
        self._role_bindings: Dict[tuple, dict] = {}

    # ------------------------------------------------------------------
    # Developer-facing API
    # ------------------------------------------------------------------

    def add_role(self, namespace: str, name: str, rules: List[dict] = None):
        """Register a Role in the fake server.

        Args:
            namespace (str): Kubernetes namespace
            name (str): Role name
            rules (List[dict], optional): Policy rules. Defaults to empty list.
        """
        self._roles[(namespace, name)] = make_role(namespace, name, rules)

    def add_role_binding(self, namespace: str, name: str, role_name: str, subjects: List[dict] = None):
        """Register a RoleBinding in the fake server.

        Args:
            namespace (str): Kubernetes namespace
            name (str): RoleBinding name
            role_name (str): Name of the Role this binding references
            subjects (List[dict], optional): Subjects list. Defaults to empty list.
        """
        self._role_bindings[(namespace, name)] = make_role_binding(namespace, name, role_name, subjects)

    # ------------------------------------------------------------------
    # Internal routing (called by _Handler via generic dispatch)
    # ------------------------------------------------------------------

    def _handle_apis_get(self, ns: str, resource: str, name: Optional[str]) -> Optional[tuple]:
        """Handle a GET for an RBAC namespaced resource.

        Returns None if the resource name is not owned by this mixin, allowing
        the handler to try the next mixin.

        Args:
            ns (str): Namespace
            resource (str): Plural resource name (e.g. "roles")
            name (str, optional): Resource name, or None for a list request

        Returns:
            tuple: (http_status, response_body_dict), or None if not handled
        """
        store_map = {
            "roles": self._roles,
            "rolebindings": self._role_bindings,
        }
        if resource not in _KIND_MAP:
            return None

        kind = _KIND_MAP[resource]
        store = store_map[resource]

        if name:
            obj = store.get((ns, name))
            if obj:
                return 200, obj
            return 404, {"kind": "Status", "apiVersion": "v1", "status": "Failure",
                         "message": f'{kind} "{name}" not found', "reason": "NotFound", "code": 404}

        items = [v for (n, _), v in store.items() if n == ns]
        return 200, {"apiVersion": "rbac.authorization.k8s.io/v1", "kind": f"{kind}List", "metadata": {}, "items": items}

    def _handle_apis_delete(self, ns: str, resource: str, name: Optional[str]) -> Optional[tuple]:
        """Handle a DELETE for an RBAC namespaced resource.

        Returns None if the resource name is not owned by this mixin.

        Args:
            ns (str): Namespace
            resource (str): Plural resource name
            name (str, optional): Resource name

        Returns:
            tuple: (http_status, response_body_dict), or None if not handled
        """
        store_map = {
            "roles": self._roles,
            "rolebindings": self._role_bindings,
        }
        if resource not in _KIND_MAP:
            return None

        kind = _KIND_MAP[resource]
        store_map[resource].pop((ns, name), None)
        self._deleted.setdefault(kind, []).append((ns, name))  # type: ignore[attr-defined]
        return 200, {"kind": "Status", "apiVersion": "v1", "status": "Success",
                     "details": {"name": name, "kind": kind.lower() + "s"}, "code": 200}
