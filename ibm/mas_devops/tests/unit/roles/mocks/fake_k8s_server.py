"""
Minimal fake Kubernetes API server for Ansible role unit testing.

This module contains the HTTP engine and server lifecycle only. Resource-specific
state, routing, and developer-facing add_* methods live in the mixin modules:

  operators.py  -- OLM resources (Subscription, ClusterServiceVersion, InstallPlan)
  workloads.py  -- Core v1 and RBAC resources (ServiceAccount, ConfigMap, Secret,
                   Role, RoleBinding)

Usage::

    from fake_k8s_server import FakeKubernetesServer

    with FakeKubernetesServer() as server:
        server.add_subscription("test-ns", "ibm-truststore-mgr", "ibm-truststore-mgr.v1.0.0")
        server.add_install_plan("test-ns", "install-plan-abc", ["ibm-truststore-mgr.v1.0.0"])

        result = run_playbook(server.kubeconfig_path, "test-ns")

        assert "ibm-truststore-mgr" in server.get_deleted("Subscription")

To extend the server with new resource types, add a new mixin module following
the pattern in operators.py or workloads.py, then inherit from it in
FakeKubernetesServer and call its _init_* method from __init__.
"""

import json
import os
import tempfile
import textwrap
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Dict, List, Optional
from urllib.parse import urlparse

import operators
import rbac
import workloads


# ---------------------------------------------------------------------------
# API discovery response bodies
# ---------------------------------------------------------------------------

_API_VERSIONS = {
    "kind": "APIVersions",
    "apiVersion": "v1",
    "versions": ["v1"],
    "serverAddressByClientCIDRs": [{"clientCIDR": "0.0.0.0/0", "serverAddress": ""}],
}

_API_GROUPS = {
    "kind": "APIGroupList",
    "apiVersion": "v1",
    "groups": [
        operators.API_GROUP_LIST_ENTRY,
        rbac.API_GROUP_LIST_ENTRY,
    ],
}


# ---------------------------------------------------------------------------
# HTTP handler
# ---------------------------------------------------------------------------


class _Handler(BaseHTTPRequestHandler):
    """Route HTTP requests to FakeKubernetesServer state."""

    def log_message(self, fmt, *args):
        self._srv()._request_log.append(self.path)

    def _srv(self) -> "FakeKubernetesServer":
        return self.server.fake  # type: ignore[attr-defined]

    def _send_json(self, status: int, body: dict):
        encoded = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self):  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        # Fixed discovery routes
        if path == "/version":
            self._send_json(200, {"major": "1", "minor": "27", "gitVersion": "v1.27.0", "platform": "linux/amd64"})
        elif path == "/api":
            self._send_json(200, _API_VERSIONS)
        elif path == "/api/v1":
            self._send_json(200, workloads.CORE_V1_RESOURCE_LIST)
        elif path == "/apis":
            self._send_json(200, _API_GROUPS)
        elif path == "/apis/operators.coreos.com":
            self._send_json(200, operators.API_GROUP)
        elif path == "/apis/operators.coreos.com/v1alpha1":
            self._send_json(200, operators.RESOURCE_LIST)
        elif path == "/apis/rbac.authorization.k8s.io":
            self._send_json(200, rbac.API_GROUP)
        elif path == "/apis/rbac.authorization.k8s.io/v1":
            self._send_json(200, rbac.RESOURCE_LIST)
        else:
            self._route_resource_get(path)

    def do_DELETE(self):  # noqa: N802
        parsed = urlparse(self.path)
        self._route_resource_delete(parsed.path.rstrip("/"))

    # ------------------------------------------------------------------
    # Resource routing
    # ------------------------------------------------------------------

    def _route_resource_get(self, path: str):
        srv = self._srv()
        parts = path.lstrip("/").split("/")

        # /api/v1/namespaces/{ns}/{resource}[/{name}]  — core group only
        if len(parts) >= 5 and parts[0] == "api" and parts[1] == "v1" and parts[2] == "namespaces":
            ns, resource = parts[3], parts[4]
            name = parts[5] if len(parts) > 5 else None
            status, body = srv._handle_core_get(ns, resource, name)
            self._send_json(status, body)
            return

        # /apis/{group}/{version}/namespaces/{ns}/{resource}[/{name}]
        if len(parts) >= 6 and parts[0] == "apis" and parts[3] == "namespaces":
            ns, resource = parts[4], parts[5]
            name = parts[6] if len(parts) > 6 else None
            for mixin in type(srv).__mro__:
                handler = getattr(mixin, "_handle_apis_get", None)
                if handler:
                    result = handler(srv, ns, resource, name)
                    if result is not None:
                        self._send_json(*result)
                        return
            self._send_json(404, {"kind": "Status", "status": "Failure", "reason": "NotFound", "code": 404})
            return

        self._send_json(404, {"kind": "Status", "status": "Failure", "reason": "NotFound", "code": 404})

    def _route_resource_delete(self, path: str):
        srv = self._srv()
        parts = path.lstrip("/").split("/")

        # /api/v1/namespaces/{ns}/{resource}/{name}  — core group only
        if len(parts) >= 6 and parts[0] == "api" and parts[1] == "v1" and parts[2] == "namespaces":
            ns, resource, name = parts[3], parts[4], parts[5]
            status, body = srv._handle_core_delete(ns, resource, name)
            self._send_json(status, body)
            return

        # /apis/{group}/{version}/namespaces/{ns}/{resource}/{name}
        if len(parts) >= 7 and parts[0] == "apis" and parts[3] == "namespaces":
            ns, resource, name = parts[4], parts[5], parts[6]
            for mixin in type(srv).__mro__:
                handler = getattr(mixin, "_handle_apis_delete", None)
                if handler:
                    result = handler(srv, ns, resource, name)
                    if result is not None:
                        self._send_json(*result)
                        return
            self._send_json(404, {"kind": "Status", "status": "Failure", "reason": "NotFound", "code": 404})
            return

        self._send_json(404, {"kind": "Status", "status": "Failure", "reason": "NotFound", "code": 404})


# ---------------------------------------------------------------------------
# Public server class
# ---------------------------------------------------------------------------


class FakeKubernetesServer(operators.OperatorsMixin, workloads.WorkloadsMixin, rbac.RbacMixin):
    """
    A lightweight fake Kubernetes API server for Ansible role unit testing.

    Inherits developer-facing add_* methods from:
      - operators.OperatorsMixin  (Subscription, ClusterServiceVersion, InstallPlan)
      - workloads.WorkloadsMixin  (ServiceAccount, ConfigMap, Secret)
      - rbac.RbacMixin            (Role, RoleBinding)

    Intended to be used as a context manager::

        with FakeKubernetesServer() as server:
            server.add_subscription("ns", "ibm-truststore-mgr", "ibm-truststore-mgr.v1.0.0")
            # run ansible-playbook subprocess pointed at server.kubeconfig_path
            assert "ibm-truststore-mgr" in server.get_deleted("Subscription")
    """

    def __init__(self, port: int = 0):
        self._init_operators()
        self._init_workloads()
        self._init_rbac()
        self._deleted: Dict[str, List[tuple]] = {}
        self._request_log: List[str] = []

        self._httpd = HTTPServer(("127.0.0.1", port), _Handler)
        self._httpd.fake = self  # back-reference for handler
        self._thread: Optional[threading.Thread] = None
        self._kubeconfig_file = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self):
        """Start the HTTP server in a background daemon thread."""
        self._thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)
        self._thread.start()
        self._kubeconfig_file = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False)
        self._kubeconfig_file.write(self._build_kubeconfig())
        self._kubeconfig_file.flush()

    def stop(self):
        """Shut down the HTTP server and clean up the temporary kubeconfig."""
        self._httpd.shutdown()
        if self._thread:
            self._thread.join(timeout=5)
        if self._kubeconfig_file:
            try:
                os.unlink(self._kubeconfig_file.name)
            except OSError:
                pass

    def __enter__(self) -> "FakeKubernetesServer":
        self.start()
        return self

    def __exit__(self, *_):
        self.stop()

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def port(self) -> int:
        return self._httpd.server_address[1]

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self.port}"

    @property
    def kubeconfig_path(self) -> str:
        """Path to a temporary kubeconfig that points at this server."""
        return self._kubeconfig_file.name

    # ------------------------------------------------------------------
    # Test assertion API
    # ------------------------------------------------------------------

    def get_deleted(self, kind: str, name: Optional[str] = None, namespace: Optional[str] = None) -> List[tuple]:
        """Return (namespace, name) tuples for resources deleted for a given kind.

        Optionally filter by name and/or namespace.

        Args:
            kind (str): Kubernetes resource kind (e.g. "Subscription", "ConfigMap")
            name (str, optional): Filter to a specific resource name. Defaults to None.
            namespace (str, optional): Filter to a specific namespace. Defaults to None.

        Returns:
            List[tuple]: (namespace, name) tuples of resources deleted during the test run
        """
        entries = self._deleted.get(kind, [])
        if name is not None:
            entries = [e for e in entries if e[1] == name]
        if namespace is not None:
            entries = [e for e in entries if e[0] == namespace]
        return entries

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_kubeconfig(self) -> str:
        return textwrap.dedent(f"""\
            apiVersion: v1
            kind: Config
            clusters:
            - cluster:
                server: {self.url}
                insecure-skip-tls-verify: true
              name: fake
            contexts:
            - context:
                cluster: fake
                user: fake
              name: fake
            current-context: fake
            users:
            - name: fake
              user: {{}}
            """)
