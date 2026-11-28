"""
Operator resource mixin for FakeKubernetesServer.

Provides the API discovery constants, resource factory functions, HTTP routing
logic, and developer-facing add_* methods for OLM resources:

  operators.coreos.com/v1alpha1:
  - Subscription
  - ClusterServiceVersion
  - InstallPlan

  operators.coreos.com/v2:
  - OperatorCondition

  packages.operators.coreos.com/v1:
  - PackageManifest
"""

# ---------------------------------------------------------------------------
# API discovery constants
# ---------------------------------------------------------------------------

API_GROUP = {
    "kind": "APIGroup",
    "apiVersion": "v1",
    "name": "operators.coreos.com",
    "versions": [
        {"groupVersion": "operators.coreos.com/v1alpha1", "version": "v1alpha1"},
        {"groupVersion": "operators.coreos.com/v2", "version": "v2"},
    ],
    "preferredVersion": {"groupVersion": "operators.coreos.com/v1alpha1", "version": "v1alpha1"},
}

API_GROUP_LIST_ENTRY = {
    "name": "operators.coreos.com",
    "versions": [
        {"groupVersion": "operators.coreos.com/v1alpha1", "version": "v1alpha1"},
        {"groupVersion": "operators.coreos.com/v2", "version": "v2"},
    ],
    "preferredVersion": {"groupVersion": "operators.coreos.com/v1alpha1", "version": "v1alpha1"},
}

PACKAGES_API_GROUP = {
    "kind": "APIGroup",
    "apiVersion": "v1",
    "name": "packages.operators.coreos.com",
    "versions": [
        {"groupVersion": "packages.operators.coreos.com/v1", "version": "v1"},
    ],
    "preferredVersion": {"groupVersion": "packages.operators.coreos.com/v1", "version": "v1"},
}

PACKAGES_API_GROUP_LIST_ENTRY = {
    "name": "packages.operators.coreos.com",
    "versions": [
        {"groupVersion": "packages.operators.coreos.com/v1", "version": "v1"},
    ],
    "preferredVersion": {"groupVersion": "packages.operators.coreos.com/v1", "version": "v1"},
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
            "verbs": ["delete", "get", "list", "patch"],
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

RESOURCE_LIST_V2 = {
    "kind": "APIResourceList",
    "apiVersion": "v1",
    "groupVersion": "operators.coreos.com/v2",
    "resources": [
        {
            "name": "operatorconditions",
            "singularName": "operatorcondition",
            "namespaced": True,
            "kind": "OperatorCondition",
            "verbs": ["get", "list"],
        },
    ],
}

PACKAGES_RESOURCE_LIST = {
    "kind": "APIResourceList",
    "apiVersion": "v1",
    "groupVersion": "packages.operators.coreos.com/v1",
    "resources": [
        {
            "name": "packagemanifests",
            "singularName": "packagemanifest",
            "namespaced": True,
            "kind": "PackageManifest",
            "verbs": ["get", "list"],
        },
    ],
}


# ---------------------------------------------------------------------------
# Resource factories
# ---------------------------------------------------------------------------


def make_subscription(
    namespace: str,
    name: str,
    installed_csv: str,
    current_csv: str | None = None,
    install_plan_generation: int = 1,
    channel: str = "stable",
    source: str = "ibm-operator-catalog",
    source_namespace: str = "openshift-marketplace",
) -> dict:
    """Return a minimal OLM Subscription object.

    Args:
        namespace (str): Kubernetes namespace
        name (str): Subscription name
        installed_csv (str): installedCSV field value
        current_csv (str, optional): currentCSV field value. Defaults to installed_csv.
        install_plan_generation (int, optional): installPlanGeneration field value. Defaults to 1.
        channel (str, optional): Subscription channel. Defaults to "stable".
        source (str, optional): CatalogSource name. Defaults to "ibm-operator-catalog".
        source_namespace (str, optional): CatalogSource namespace. Defaults to "openshift-marketplace".

    Returns:
        dict: Subscription resource body
    """
    return {
        "apiVersion": "operators.coreos.com/v1alpha1",
        "kind": "Subscription",
        "metadata": {"name": name, "namespace": namespace},
        "spec": {
            "name": name,
            "channel": channel,
            "source": source,
            "sourceNamespace": source_namespace,
        },
        "status": {
            "installedCSV": installed_csv,
            "currentCSV": current_csv or installed_csv,
            "state": "AtLatestKnown",
            "installPlanGeneration": install_plan_generation,
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


def make_install_plan(namespace: str, name: str, csv_names: list[str]) -> dict:
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


def make_operator_condition(namespace: str, name: str) -> dict:
    """Return a minimal OLM OperatorCondition object.

    The name follows the OLM convention: {packageName}.{versionWithV} e.g.
    "ibm-aiservice-tenant.v9.1.2".

    Args:
        namespace (str): Kubernetes namespace
        name (str): OperatorCondition name

    Returns:
        dict: OperatorCondition resource body
    """
    return {
        "apiVersion": "operators.coreos.com/v2",
        "kind": "OperatorCondition",
        "metadata": {"name": name, "namespace": namespace},
        "spec": {},
        "status": {},
    }


def make_package_manifest(namespace: str, package: str, channels: dict[str, str], default_channel: str | None = None) -> dict:
    """Return a minimal PackageManifest object.

    Args:
        namespace (str): Catalog source namespace (usually "openshift-marketplace")
        package (str): Package name (the manifest's metadata.name)
        channels (dict): Channel name -> currentCSV (the channel head)
        default_channel (str, optional): Default channel. Defaults to the first channel.

    Returns:
        dict: PackageManifest resource body
    """
    return {
        "apiVersion": "packages.operators.coreos.com/v1",
        "kind": "PackageManifest",
        "metadata": {"name": package, "namespace": namespace},
        "status": {
            "packageName": package,
            "catalogSource": "ibm-operator-catalog",
            "catalogSourceNamespace": namespace,
            "defaultChannel": default_channel or next(iter(channels)),
            "channels": [{"name": channel, "currentCSV": current_csv} for channel, current_csv in channels.items()],
        },
    }


# ---------------------------------------------------------------------------
# Shared response helpers
# ---------------------------------------------------------------------------


def _not_found(kind: str, name: str) -> dict:
    return {
        "kind": "Status",
        "apiVersion": "v1",
        "status": "Failure",
        "message": f'{kind} "{name}" not found',
        "reason": "NotFound",
        "code": 404,
    }


def _deleted(kind: str, name: str | None) -> dict:
    return {
        "kind": "Status",
        "apiVersion": "v1",
        "status": "Success",
        "details": {"name": name, "kind": kind.lower() + "s"},
        "code": 200,
    }


# ---------------------------------------------------------------------------
# Mixin
# ---------------------------------------------------------------------------

_API_VERSION = "operators.coreos.com/v1alpha1"
_API_VERSION_V2 = "operators.coreos.com/v2"
_PACKAGES_API_VERSION = "packages.operators.coreos.com/v1"


class OperatorsMixin:
    """Mixin for FakeKubernetesServer — adds OLM resource state and routing.

    Attributes:
        _subscriptions: In-memory store of Subscription resources keyed by (namespace, name).
        _csvs: In-memory store of ClusterServiceVersion resources keyed by (namespace, name).
        _install_plans: In-memory store of InstallPlan resources keyed by (namespace, name).
        _operator_conditions: In-memory store of OperatorCondition resources keyed by (namespace, name).
        _package_manifests: In-memory store of PackageManifest resources keyed by (namespace, name).
    """

    def _init_operators(self):
        """Initialise the OLM resource stores. Called by FakeKubernetesServer.__init__."""
        self._subscriptions: dict[tuple, dict] = {}
        self._csvs: dict[tuple, dict] = {}
        self._install_plans: dict[tuple, dict] = {}
        self._operator_conditions: dict[tuple, dict] = {}
        self._package_manifests: dict[tuple, dict] = {}

    # ------------------------------------------------------------------
    # Developer-facing API
    # ------------------------------------------------------------------

    def add_subscription(
        self,
        namespace: str,
        name: str,
        installed_csv: str,
        current_csv: str | None = None,
        install_plan_generation: int = 1,
        channel: str = "stable",
        source: str = "ibm-operator-catalog",
        source_namespace: str = "openshift-marketplace",
    ):
        """Register an OLM Subscription in the fake server.

        Args:
            namespace (str): Kubernetes namespace
            name (str): Subscription name
            installed_csv (str): installedCSV field value
            current_csv (str, optional): currentCSV field value. Defaults to installed_csv.
            install_plan_generation (int, optional): installPlanGeneration counter. Defaults to 1.
            channel (str, optional): Subscription channel. Defaults to "stable".
            source (str, optional): CatalogSource name. Defaults to "ibm-operator-catalog".
            source_namespace (str, optional): CatalogSource namespace. Defaults to "openshift-marketplace".
        """
        self._subscriptions[(namespace, name)] = make_subscription(
            namespace, name, installed_csv, current_csv, install_plan_generation, channel, source, source_namespace
        )

    def add_csv(self, namespace: str, name: str):
        """Register a ClusterServiceVersion in the fake server.

        Args:
            namespace (str): Kubernetes namespace
            name (str): CSV name
        """
        self._csvs[(namespace, name)] = make_csv(namespace, name)

    def add_install_plan(self, namespace: str, name: str, csv_names: list[str]):
        """Register an InstallPlan in the fake server.

        Args:
            namespace (str): Kubernetes namespace
            name (str): InstallPlan name
            csv_names (List[str]): List of CSV names referenced by this InstallPlan
        """
        self._install_plans[(namespace, name)] = make_install_plan(namespace, name, csv_names)

    def add_operator_condition(self, namespace: str, name: str):
        """Register an OperatorCondition in the fake server.

        Args:
            namespace (str): Kubernetes namespace
            name (str): OperatorCondition name (e.g. "ibm-aiservice-tenant.v9.1.2")
        """
        self._operator_conditions[(namespace, name)] = make_operator_condition(namespace, name)

    def add_package_manifest(self, namespace: str, package: str, channels: dict[str, str], default_channel: str | None = None):
        """Register a PackageManifest in the fake server.

        The channel heads are what the subscription convergence gate resolves
        its targets from, so a test driving the approval gate registers the
        manifest whose channels match the subscription's channel.

        Args:
            namespace (str): Catalog source namespace (usually "openshift-marketplace")
            package (str): Package name
            channels (dict): Channel name -> currentCSV (the channel head)
            default_channel (str, optional): Default channel. Defaults to the first channel.
        """
        self._package_manifests[(namespace, package)] = make_package_manifest(namespace, package, channels, default_channel)

    # ------------------------------------------------------------------
    # Internal routing (called by _Handler via generic dispatch)
    # ------------------------------------------------------------------

    def _handle_apis_get(self, ns: str, resource: str, name: str | None) -> tuple | None:
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
            if name:
                obj = self._subscriptions.get((ns, name))
                return (200, obj) if obj else (404, _not_found("Subscription", name))
            items = [v for (n, _), v in self._subscriptions.items() if n == ns]
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

        if resource == "operatorconditions":
            items = [v for (n, _), v in self._operator_conditions.items() if n == ns]
            return 200, {"apiVersion": _API_VERSION_V2, "kind": "OperatorConditionList", "metadata": {}, "items": items}

        if resource == "packagemanifests":
            if name:
                obj = self._package_manifests.get((ns, name))
                return (200, obj) if obj else (404, _not_found("PackageManifest", name))
            items = [v for (n, _), v in self._package_manifests.items() if n == ns]
            return 200, {"apiVersion": _PACKAGES_API_VERSION, "kind": "PackageManifestList", "metadata": {}, "items": items}

        return None

    def _handle_apis_patch(self, ns: str, resource: str, name: str, body: dict) -> tuple | None:
        """Handle a PATCH for an OLM namespaced resource.

        For Subscriptions, bumps installPlanGeneration and merges the spec so
        that the upgrade.yml retry loop resolves on the first poll after the
        PATCH is applied.

        Returns None if the resource is not owned by this mixin.

        Args:
            ns (str): Namespace
            resource (str): Plural resource name
            name (str): Resource name
            body (dict): Patch body

        Returns:
            tuple: (http_status, response_body_dict), or None if not handled
        """
        if resource != "subscriptions":
            return None

        key = (ns, name)
        obj = self._subscriptions.get(key)
        if obj is None:
            return 404, _not_found("Subscription", name)

        # Merge spec from the patch body
        if "spec" in body:
            obj.setdefault("spec", {}).update(body["spec"])

        # Model the convergence the subscription approval gate waits for: the
        # channel change resolves (installPlanGeneration bumps, state returns
        # to AtLatestKnown) and the CSV rolls out to the channel's head
        # (installedCSV promotes to currentCSV). Tests that do not set
        # currentCSV ahead of installedCSV are unaffected by the promotion.
        obj.setdefault("status", {})
        obj["status"]["installPlanGeneration"] = obj["status"].get("installPlanGeneration", 1) + 1
        obj["status"]["state"] = "AtLatestKnown"
        if obj["status"].get("currentCSV"):
            obj["status"]["installedCSV"] = obj["status"]["currentCSV"]

        return 200, obj

    def _handle_apis_delete(self, ns: str, resource: str, name: str | None) -> tuple | None:
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
