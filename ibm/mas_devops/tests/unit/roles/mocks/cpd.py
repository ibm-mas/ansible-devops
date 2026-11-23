"""
CP4D resource mixin for FakeKubernetesServer.

Provides the API discovery constants, resource factory functions, HTTP routing
logic, and developer-facing add_* methods for Cloud Pak for Data custom
resources:

  cpd.ibm.com/v1:
  - Ibmcpd

  ws.cpd.ibm.com/v1beta1:
  - WS

  wml.cpd.ibm.com/v1beta1:
  - WmlBase

  ae.cpd.ibm.com/v1:
  - AnalyticsEngine
"""


# ---------------------------------------------------------------------------
# API discovery constants
# ---------------------------------------------------------------------------

_CPD_GROUP_VERSIONS = {
    "cpd.ibm.com": ["v1"],
    "ws.cpd.ibm.com": ["v1beta1"],
    "wml.cpd.ibm.com": ["v1beta1"],
    "ae.cpd.ibm.com": ["v1"],
}

# kind -> (plural, api_version)
_CPD_RESOURCES = {
    "Ibmcpd": ("ibmcpds", "cpd.ibm.com/v1"),
    "WS": ("ws", "ws.cpd.ibm.com/v1beta1"),
    "WmlBase": ("wmlbases", "wml.cpd.ibm.com/v1beta1"),
    "AnalyticsEngine": ("analyticsengines", "ae.cpd.ibm.com/v1"),
}

API_GROUP_LIST_ENTRIES = [
    {
        "name": group,
        "versions": [
            {"groupVersion": f"{group}/{version}", "version": version} for version in versions
        ],
        "preferredVersion": {"groupVersion": f"{group}/{versions[0]}", "version": versions[0]},
    }
    for group, versions in _CPD_GROUP_VERSIONS.items()
]

DISCOVERY_ROUTES = {}
for _group, _versions in _CPD_GROUP_VERSIONS.items():
    _group_body = {
        "kind": "APIGroup",
        "apiVersion": "v1",
        "name": _group,
        "versions": [
            {"groupVersion": f"{_group}/{_v}", "version": _v} for _v in _versions
        ],
        "preferredVersion": {"groupVersion": f"{_group}/{_versions[0]}", "version": _versions[0]},
    }
    DISCOVERY_ROUTES[f"/apis/{_group}"] = _group_body
    for _v in _versions:
        _plural_by_version = {
            plural: kind for kind, (plural, api_version) in _CPD_RESOURCES.items()
            if api_version == f"{_group}/{_v}"
        }
        DISCOVERY_ROUTES[f"/apis/{_group}/{_v}"] = {
            "kind": "APIResourceList",
            "apiVersion": "v1",
            "groupVersion": f"{_group}/{_v}",
            "resources": [
                {
                    "name": plural,
                    "namespaced": True,
                    "kind": kind,
                    "verbs": ["get", "list"],
                }
                for plural, kind in _plural_by_version.items()
            ],
        }

_CPD_PLURALS = {plural for plural, _ in _CPD_RESOURCES.values()}


# ---------------------------------------------------------------------------
# Resource factory
# ---------------------------------------------------------------------------


def make_cpd_cr(kind: str, namespace: str, name: str, spec: dict | None = None) -> dict:
    """Return a minimal Cloud Pak for Data custom resource.

    Args:
        kind (str): Resource kind — one of "Ibmcpd", "WS", "WmlBase", "AnalyticsEngine"
        namespace (str): Kubernetes namespace
        name (str): Resource name
        spec (dict, optional): Resource spec. Defaults to an empty spec.

    Returns:
        dict: CR resource body
    """
    plural, api_version = _CPD_RESOURCES[kind]
    return {
        "apiVersion": api_version,
        "kind": kind,
        "metadata": {"name": name, "namespace": namespace},
        "spec": spec if spec is not None else {},
    }


# ---------------------------------------------------------------------------
# Mixin
# ---------------------------------------------------------------------------


class CpdMixin:
    """Mixin for FakeKubernetesServer — adds Cloud Pak for Data custom resource state and routing.

    Attributes:
        _cpd_crs: In-memory store of CP4D CRs keyed by (plural, namespace, name).
    """

    def _init_cpd(self):
        """Initialise the CP4D resource stores. Called by FakeKubernetesServer.__init__."""
        self._cpd_crs: dict[tuple, dict] = {}

    # ------------------------------------------------------------------
    # Developer-facing API
    # ------------------------------------------------------------------

    def add_cpd_cr(self, kind: str, namespace: str, name: str, spec: dict | None = None):
        """Register a Cloud Pak for Data CR in the fake server.

        Args:
            kind (str): Resource kind — one of "Ibmcpd", "WS", "WmlBase", "AnalyticsEngine"
            namespace (str): Kubernetes namespace
            name (str): Resource name
            spec (dict, optional): Resource spec. Defaults to an empty spec.
        """
        plural, _ = _CPD_RESOURCES[kind]
        self._cpd_crs[(plural, namespace, name)] = make_cpd_cr(kind, namespace, name, spec)

    def add_ibmcpd(self, namespace: str, name: str, spec: dict | None = None):
        """Register an Ibmcpd CR in the fake server.

        Args:
            namespace (str): Kubernetes namespace
            name (str): Ibmcpd CR name (e.g. "ibmcpd-cr" or legacy "ibmcpd")
            spec (dict, optional): Ibmcpd spec (e.g. {"storageClass": "..."}).
        """
        self.add_cpd_cr("Ibmcpd", namespace, name, spec)

    def add_ws(self, namespace: str, name: str, spec: dict | None = None):
        """Register a Watson Studio (WS) CR in the fake server.

        Args:
            namespace (str): Kubernetes namespace
            name (str): WS CR name (e.g. "ws-cr")
            spec (dict, optional): WS spec (e.g. {"fileStorageClass": "..."}).
        """
        self.add_cpd_cr("WS", namespace, name, spec)

    def add_wmlbase(self, namespace: str, name: str, spec: dict | None = None):
        """Register a Watson Machine Learning (WmlBase) CR in the fake server.

        Args:
            namespace (str): Kubernetes namespace
            name (str): WmlBase CR name (e.g. "wml-cr")
            spec (dict, optional): WmlBase spec (e.g. {"blockStorageClass": "..."}).
        """
        self.add_cpd_cr("WmlBase", namespace, name, spec)

    def add_analyticsengine(self, namespace: str, name: str, spec: dict | None = None):
        """Register an AnalyticsEngine (Spark) CR in the fake server.

        Args:
            namespace (str): Kubernetes namespace
            name (str): AnalyticsEngine CR name (e.g. "analyticsengine-sample")
            spec (dict, optional): AnalyticsEngine spec.
        """
        self.add_cpd_cr("AnalyticsEngine", namespace, name, spec)

    # ------------------------------------------------------------------
    # Internal routing (called by _Handler via generic dispatch)
    # ------------------------------------------------------------------

    def _handle_apis_get(self, ns: str, resource: str, name: str | None) -> tuple | None:
        """Handle a GET for a Cloud Pak for Data namespaced resource.

        Returns None if the resource is not owned by this mixin.

        Args:
            ns (str): Namespace
            resource (str): Plural resource name
            name (str, optional): Resource name, or None for a list request

        Returns:
            tuple: (http_status, response_body_dict), or None if not handled
        """
        if resource not in _CPD_PLURALS:
            return None

        kind = next(k for k, (plural, _) in _CPD_RESOURCES.items() if plural == resource)

        if name:
            obj = self._cpd_crs.get((resource, ns, name))
            if obj:
                return 200, obj
            return 404, {
                "kind": "Status", "apiVersion": "v1", "status": "Failure",
                "message": f'{kind} "{name}" not found', "reason": "NotFound", "code": 404,
            }

        items = [v for (plural, n, _), v in self._cpd_crs.items() if plural == resource and n == ns]
        return 200, {"apiVersion": "v1", "kind": f"{kind}List", "metadata": {}, "items": items}
