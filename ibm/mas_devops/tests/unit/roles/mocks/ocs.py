"""
OpenShift Data Foundation (OCS) resource mixin for FakeKubernetesServer.

Provides the API discovery constants, resource factory functions, HTTP routing
logic, and developer-facing add_* methods for OCS custom resources:

  ocs.openshift.io/v1:
  - StorageCluster

  ceph.rook.io/v1:
  - CephObjectStoreUser
"""


# ---------------------------------------------------------------------------
# API discovery constants
# ---------------------------------------------------------------------------

API_GROUP = {
    "kind": "APIGroup",
    "apiVersion": "v1",
    "name": "ocs.openshift.io",
    "versions": [{"groupVersion": "ocs.openshift.io/v1", "version": "v1"}],
    "preferredVersion": {"groupVersion": "ocs.openshift.io/v1", "version": "v1"},
}

API_GROUP_LIST_ENTRY = {
    "name": "ocs.openshift.io",
    "versions": [{"groupVersion": "ocs.openshift.io/v1", "version": "v1"}],
    "preferredVersion": {"groupVersion": "ocs.openshift.io/v1", "version": "v1"},
}

RESOURCE_LIST = {
    "kind": "APIResourceList",
    "apiVersion": "v1",
    "groupVersion": "ocs.openshift.io/v1",
    "resources": [
        {
            "name": "storageclusters",
            "singularName": "storagecluster",
            "namespaced": True,
            "kind": "StorageCluster",
            "verbs": ["get", "list"],
        },
    ],
}

CEPH_API_GROUP = {
    "kind": "APIGroup",
    "apiVersion": "v1",
    "name": "ceph.rook.io",
    "versions": [{"groupVersion": "ceph.rook.io/v1", "version": "v1"}],
    "preferredVersion": {"groupVersion": "ceph.rook.io/v1", "version": "v1"},
}

CEPH_API_GROUP_LIST_ENTRY = {
    "name": "ceph.rook.io",
    "versions": [{"groupVersion": "ceph.rook.io/v1", "version": "v1"}],
    "preferredVersion": {"groupVersion": "ceph.rook.io/v1", "version": "v1"},
}

CEPH_RESOURCE_LIST = {
    "kind": "APIResourceList",
    "apiVersion": "v1",
    "groupVersion": "ceph.rook.io/v1",
    "resources": [
        {
            "name": "cephobjectstoreusers",
            "singularName": "cephobjectstoreuser",
            "namespaced": True,
            "kind": "CephObjectStoreUser",
            "verbs": ["get", "list"],
        },
    ],
}

_API_VERSION = "ocs.openshift.io/v1"
_CEPH_API_VERSION = "ceph.rook.io/v1"


# ---------------------------------------------------------------------------
# Resource factory
# ---------------------------------------------------------------------------


def make_storage_cluster(namespace: str, name: str, phase: str = "Ready", external: bool | None = False) -> dict:
    """Return a minimal StorageCluster object.

    Args:
        namespace (str): Kubernetes namespace
        name (str): StorageCluster name
        phase (str, optional): Value of status.phase. Defaults to "Ready".
        external (bool, optional): Controls spec.externalStorage. True sets
            externalStorage.enable to true, False sets it to false, and None omits
            the externalStorage key entirely (as an internal-mode cluster usually does).
            Defaults to False.

    Returns:
        dict: StorageCluster resource body
    """
    spec: dict = {}
    if external is not None:
        spec["externalStorage"] = {"enable": external}
    return {
        "apiVersion": _API_VERSION,
        "kind": "StorageCluster",
        "metadata": {"name": name, "namespace": namespace},
        "spec": spec,
        "status": {"phase": phase},
    }


def make_ceph_object_store_user(namespace: str, name: str, phase: str = "Ready") -> dict:
    """Return a minimal CephObjectStoreUser object.

    Args:
        namespace (str): Kubernetes namespace
        name (str): CephObjectStoreUser name
        phase (str, optional): Value of status.phase (e.g. "Ready" or "ReconcileFailed"). Defaults to "Ready".

    Returns:
        dict: CephObjectStoreUser resource body
    """
    return {
        "apiVersion": _CEPH_API_VERSION,
        "kind": "CephObjectStoreUser",
        "metadata": {"name": name, "namespace": namespace},
        "spec": {"store": "object", "displayName": "s3-user3"},
        "status": {"phase": phase},
    }


# ---------------------------------------------------------------------------
# Mixin
# ---------------------------------------------------------------------------


class OcsMixin:
    """Mixin for FakeKubernetesServer — adds OCS custom resource state and routing.

    Attributes:
        _storage_clusters: In-memory store of StorageCluster resources keyed by (namespace, name).
        _ceph_object_store_users: In-memory store of CephObjectStoreUser resources keyed by (namespace, name).
    """

    def _init_ocs(self):
        """Initialise the OCS resource stores. Called by FakeKubernetesServer.__init__."""
        self._storage_clusters: dict[tuple, dict] = {}
        self._ceph_object_store_users: dict[tuple, dict] = {}

    # ------------------------------------------------------------------
    # Developer-facing API
    # ------------------------------------------------------------------

    def add_storage_cluster(self, namespace: str, name: str, phase: str = "Ready", external: bool | None = False):
        """Register a StorageCluster in the fake server.

        Args:
            namespace (str): Kubernetes namespace
            name (str): StorageCluster name
            phase (str, optional): Value of status.phase. Defaults to "Ready".
            external (bool, optional): True enables ODF external mode, False disables it,
                None omits spec.externalStorage entirely. Defaults to False.
        """
        self._storage_clusters[(namespace, name)] = make_storage_cluster(namespace, name, phase, external)

    def add_ceph_object_store_user(self, namespace: str, name: str, phase: str = "Ready"):
        """Register a CephObjectStoreUser in the fake server.

        Args:
            namespace (str): Kubernetes namespace
            name (str): CephObjectStoreUser name
            phase (str, optional): Value of status.phase. Defaults to "Ready".
        """
        self._ceph_object_store_users[(namespace, name)] = make_ceph_object_store_user(namespace, name, phase)

    # ------------------------------------------------------------------
    # Internal routing (called by _Handler via generic dispatch)
    # ------------------------------------------------------------------

    def _handle_apis_get(self, ns: str, resource: str, name: str | None) -> tuple | None:
        """Handle a GET for an OCS namespaced resource.

        Returns None if the resource is not owned by this mixin.

        Args:
            ns (str): Namespace
            resource (str): Plural resource name
            name (str, optional): Resource name, or None for a list request

        Returns:
            tuple: (http_status, response_body_dict), or None if not handled
        """
        if resource == "storageclusters":
            store, kind, api_version = self._storage_clusters, "StorageCluster", _API_VERSION
        elif resource == "cephobjectstoreusers":
            store, kind, api_version = self._ceph_object_store_users, "CephObjectStoreUser", _CEPH_API_VERSION
        else:
            return None

        if name:
            obj = store.get((ns, name))
            if obj:
                return 200, obj
            return 404, {
                "kind": "Status",
                "apiVersion": "v1",
                "status": "Failure",
                "message": f'{kind} "{name}" not found',
                "reason": "NotFound",
                "code": 404,
            }

        items = [v for (n, _), v in store.items() if n == ns]
        return 200, {"apiVersion": api_version, "kind": f"{kind}List", "metadata": {}, "items": items}
