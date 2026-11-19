"""Unit tests for the cos role's OCS provider provision.yml task file.

Regression tests for ibm-mas/cli#1596, where the cos role created a CephObjectStore and
CephObjectStoreUser on an ODF external-mode cluster. Rook cannot reconcile these in external
mode, so the role waited 10 minutes and then failed, leaving Data Foundation degraded.
"""

from utils import run_task, task_path

_TASK_FILE = task_path("cos", "providers", "ocs", "provision.yml")
_GUARD_TASK = "Fail if OCS Cluster is running in external mode"
_NEXT_TASK = "Print If there's OCS cluster"


def _run(fake_k8s):
    return run_task(_TASK_FILE, fake_k8s, {"cos_type": "ocs", "cos_action": "provision"})


def _output(result):
    return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"


class TestOcsProvisionExternalModeGuard:
    """Tests for the external mode guard in the OCS provider provision task."""

    def test_external_mode_fails_fast(self, fake_k8s):
        """Test the role fails immediately when ODF is in external mode (cli#1596).

        GIVEN a Ready StorageCluster with spec.externalStorage.enable=true
        WHEN the provision task runs
        THEN it fails with the external mode message before any Ceph resources are created.
        """
        fake_k8s.add_storage_cluster("openshift-storage", "ocs-external-storagecluster", external=True)
        result = _run(fake_k8s)
        assert result.returncode != 0, _output(result)
        assert "not supported when ODF is deployed in external mode" in result.stdout
        assert _NEXT_TASK not in result.stdout, _output(result)

    def test_internal_mode_without_external_storage_key_passes_guard(self, fake_k8s):
        """Test the guard passes when spec.externalStorage is absent.

        GIVEN a Ready StorageCluster with no spec.externalStorage key (typical internal mode)
        WHEN the provision task runs
        THEN the external mode guard does not fail and the task continues past it.
        """
        fake_k8s.add_storage_cluster("openshift-storage", "ocs-storagecluster", external=None)
        result = _run(fake_k8s)
        assert "not supported when ODF is deployed in external mode" not in result.stdout, _output(result)
        assert _NEXT_TASK in result.stdout, _output(result)

    def test_external_storage_disabled_passes_guard(self, fake_k8s):
        """Test the guard passes when spec.externalStorage.enable is false.

        GIVEN a Ready StorageCluster with spec.externalStorage.enable=false
        WHEN the provision task runs
        THEN the external mode guard does not fail and the task continues past it.
        """
        fake_k8s.add_storage_cluster("openshift-storage", "ocs-storagecluster", external=False)
        result = _run(fake_k8s)
        assert "not supported when ODF is deployed in external mode" not in result.stdout, _output(result)
        assert _NEXT_TASK in result.stdout, _output(result)

    def test_external_mode_with_ready_object_user_passes_guard(self, fake_k8s):
        """Test existing working external mode setups are not broken.

        GIVEN an external mode StorageCluster and a CephObjectStoreUser "object" that is already Ready
        WHEN the provision task runs
        THEN the external mode guard does not fail and the task continues past it.
        """
        fake_k8s.add_storage_cluster("openshift-storage", "ocs-external-storagecluster", external=True)
        fake_k8s.add_ceph_object_store_user("openshift-storage", "object", phase="Ready")
        result = _run(fake_k8s)
        assert "not supported when ODF is deployed in external mode" not in result.stdout, _output(result)
        assert _NEXT_TASK in result.stdout, _output(result)

    def test_external_mode_with_failed_object_user_fails_fast(self, fake_k8s):
        """Test a leftover failed object user from a previous run does not bypass the guard.

        GIVEN an external mode StorageCluster and a CephObjectStoreUser "object" in ReconcileFailed
        WHEN the provision task runs
        THEN it fails with the external mode message.
        """
        fake_k8s.add_storage_cluster("openshift-storage", "ocs-external-storagecluster", external=True)
        fake_k8s.add_ceph_object_store_user("openshift-storage", "object", phase="ReconcileFailed")
        result = _run(fake_k8s)
        assert result.returncode != 0, _output(result)
        assert "not supported when ODF is deployed in external mode" in result.stdout
        assert _NEXT_TASK not in result.stdout, _output(result)

    def test_cluster_not_ready_fails_before_guard(self, fake_k8s):
        """Test the existing readiness check still runs first.

        GIVEN a StorageCluster that is not Ready
        WHEN the provision task runs
        THEN it fails with the not ready message and never reaches the external mode guard.
        """
        fake_k8s.add_storage_cluster("openshift-storage", "ocs-storagecluster", phase="Progressing")
        result = _run(fake_k8s)
        assert result.returncode != 0
        assert "OCS Cluster is not ready" in result.stdout
        assert _GUARD_TASK not in result.stdout
