"""
Operator resource mixin for FakeKubernetesServer.

Provides the API discovery constants, resource factory functions, HTTP routing
logic, and developer-facing add_* methods for OLM resources:

  - Subscription       (operators.coreos.com/v1alpha1)
  - ClusterServiceVersion (operators.coreos.com/v1alpha1)
  - InstallPlan        (operators.coreos.com/v1alpha1)
"""

from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# API discovery constants
# ---------------------------------------------------------------------------

API_GROUP = {
    "kind": "APIGroup",
    "apiVersion": "v1",
    "name": "operators.coreos.com",
    "versions": [{"groupVersion": "operators.coreos.com/v1alpha1", "version": "v1alpha1"}],
    "preferredVersion": {"groupVersion": "operators.coreos.com/v1alpha1", "version": "v1alpha1"},
}

API_GROUP_LIST_ENTRY = {
    "name": "operators.coreos.com",
    "versions": [{"groupVersion": "operators.coreos.com/v1alpha1", "version": "v1alpha1"}],
    "preferredVersion": {"groupVersion": "operators.coreos.com/v1alpha1", "version": "v1alpha1"},
}

RESOURCE_LIST = {
    "kind": "APIResourceList",
    "apiVersion": "v1",
    "groupVersion": "operators.coreos.com/v1alpha1",
    "resources": [
        {
            "name": "subscriptions",
            "singularName": "subscription",
            "namespaced": True,
            "kind": "Subscription",
            "verbs": ["delete", "get", "list"],
        },
        {
            "name": "clusterserviceversions",
            "singularName": "clusterserviceversion",
            "namespaced": True,
            "kind": "ClusterServiceVersion",
            "verbs": ["delete", "get", "list"],
        },
        {
            "name": "installplans",
            "singularName": "installplan",
            "namespaced": True,
            "kind": "InstallPlan",
            "verbs": ["delete", "get", "list"],
        },
    ],
}


# ---------------------------------------------------------------------------
# Resource factories
# ---------------------------------------------------------------------------


def make_subscription(namespace: str, name: str, installed_csv: str, current_csv: Optional[str] = None) -> dict:
    """Return a minimal OLM Subscription object.

    Args:
        namespace (str): Kubernetes namespace
        name (str): Subscription name
        installed_csv (str): installedCSV field value
        current_csv (str, optional): currentCSV field value. Defaults to installed_csv.

    Returns:
        dict: Subscription resource body
    """
    return {
        "apiVersion": "operators.coreos.com/v1alpha1",
        "kind": "Subscription",
        "metadata": {"name": name, "namespace": namespace},
        "spec": {"name": name},
        "status": {
            "installedCSV": installed_csv,
            "currentCSV": current_csv or installed_csv,
            "state": "AtLatestKnown",
        },
    }


def make_csv(namespace: str, name: str) -> dict:
    """Return a minimal OLM ClusterServiceVersion object.

    Args:
        namespace (str): Kubernetes namespace
        name (str): CSV name

    Returns:
        dict: ClusterServiceVersion resource body
    """
    return {
        "apiVersion": "operators.coreos.com/v1alpha1",
        "kind": "ClusterServiceVersion",
        "metadata": {"name": name, "namespace": namespace},
        "spec": {},
        "status": {"phase": "Succeeded"},
    }


def make_install_plan(namespace: str, name: str, csv_names: List[str]) -> dict:
    """Return a minimal OLM InstallPlan object.

    Args:
        namespace (str): Kubernetes namespace
        name (str): InstallPlan name
        csv_names (List[str]): CSV names referenced by this InstallPlan

    Returns:
        dict: InstallPlan resource body
    """
    return {
        "apiVersion": "operators.coreos.com/v1alpha1",
        "kind": "InstallPlan",
        "metadata": {"name": name, "namespace": namespace},
        "spec": {"clusterServiceVersionNames": csv_names, "approved": True},
        "status": {"phase": "Complete"},
    }


# ---------------------------------------------------------------------------
# Shared response helpers
# ---------------------------------------------------------------------------


def _not_found(kind: str, name: str) -> dict:
    return {
        "kind": "Status", "apiVersion": "v1", "status": "Failure",
        "message": f'{kind} "{name}" not found', "reason": "NotFound", "code": 404,
    }


def _deleted(kind: str, name: Optional[str]) -> dict:
    return {
        "kind": "Status", "apiVersion": "v1", "status": "Success",
        "details": {"name": name, "kind": kind.lower() + "s"}, "code": 200,
    }


# ---------------------------------------------------------------------------
# Mixin
# ---------------------------------------------------------------------------

_API_VERSION = "operators.coreos.com/v1alpha1"


class OperatorsMixin:
    """Mixin for FakeKubernetesServer — adds OLM resource state and routing.

    Attributes:
        _subscriptions: In-memory store of Subscription resources keyed by (namespace, name).
        _csvs: In-memory store of ClusterServiceVersion resources keyed by (namespace, name).
        _install_plans: In-memory store of InstallPlan resources keyed by (namespace, name).
    """

    def _init_operators(self):
        """Initialise the OLM resource stores. Called by FakeKubernetesServer.__init__."""
        self._subscriptions: Dict[tuple, dict] = {}
        self._csvs: Dict[tuple, dict] = {}
        self._install_plans: Dict[tuple, dict] = {}

    # ------------------------------------------------------------------
    # Developer-facing API
    # ------------------------------------------------------------------

    def add_subscription(self, namespace: str, name: str, installed_csv: str, current_csv: Optional[str] = None):
        """Register an OLM Subscription in the fake server.

        Args:
            namespace (str): Kubernetes namespace
            name (str): Subscription name
            installed_csv (str): installedCSV field value
            current_csv (str, optional): currentCSV field value. Defaults to installed_csv.
        """
        self._subscriptions[(namespace, name)] = make_subscription(namespace, name, installed_csv, current_csv)

    def add_csv(self, namespace: str, name: str):
        """Register a ClusterServiceVersion in the fake server.

        Args:
            namespace (str): Kubernetes namespace
            name (str): CSV name
        """
        self._csvs[(namespace, name)] = make_csv(namespace, name)

    def add_install_plan(self, namespace: str, name: str, csv_names: List[str]):
        """Register an InstallPlan in the fake server.

        Args:
            namespace (str): Kubernetes namespace
            name (str): InstallPlan name
            csv_names (List[str]): List of CSV names referenced by this InstallPlan
        """
        self._install_plans[(namespace, name)] = make_install_plan(namespace, name, csv_names)

    # ------------------------------------------------------------------
    # Internal routing (called by _Handler via generic dispatch)
    # ------------------------------------------------------------------

    def _handle_apis_get(self, ns: str, resource: str, name: Optional[str]) -> Optional[tuple]:
        """Handle a GET for an OLM namespaced resource.

        Returns None if the resource name is not owned by this mixin, allowing
        the handler to try the next mixin.

        Args:
            ns (str): Namespace
            resource (str): Plural resource name
            name (str, optional): Resource name, or None for a list request

        Returns:
            tuple: (http_status, response_body_dict), or None if not handled
        """
        if resource == "subscriptions":
            obj = self._subscriptions.get((ns, name)) if name else None
            items = [obj] if obj else ([] if name else [v for (n, _), v in self._subscriptions.items() if n == ns])
            return 200, {"apiVersion": _API_VERSION, "kind": "SubscriptionList", "metadata": {}, "items": items}

        if resource == "clusterserviceversions":
            if name:
                obj = self._csvs.get((ns, name))
                return (200, obj) if obj else (404, _not_found("ClusterServiceVersion", name))
            items = [v for (n, _), v in self._csvs.items() if n == ns]
            return 200, {"apiVersion": _API_VERSION, "kind": "ClusterServiceVersionList", "metadata": {}, "items": items}

        if resource == "installplans":
            if name:
                obj = self._install_plans.get((ns, name))
                return (200, obj) if obj else (404, _not_found("InstallPlan", name))
            items = [v for (n, _), v in self._install_plans.items() if n == ns]
            return 200, {"apiVersion": _API_VERSION, "kind": "InstallPlanList", "metadata": {}, "items": items}

        return None

    def _handle_apis_delete(self, ns: str, resource: str, name: Optional[str]) -> Optional[tuple]:
        """Handle a DELETE for an OLM namespaced resource.

        Returns None if the resource name is not owned by this mixin.

        Args:
            ns (str): Namespace
            resource (str): Plural resource name
            name (str, optional): Resource name

        Returns:
            tuple: (http_status, response_body_dict), or None if not handled
        """
        store_map = {
            "subscriptions": ("Subscription", self._subscriptions),
            "clusterserviceversions": ("ClusterServiceVersion", self._csvs),
            "installplans": ("InstallPlan", self._install_plans),
        }
        if resource not in store_map:
            return None

        kind, store = store_map[resource]
        store.pop((ns, name), None)
        self._deleted.setdefault(kind, []).append((ns, name))  # type: ignore[attr-defined]
        return 200, _deleted(kind, name)
