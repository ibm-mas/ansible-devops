
from utils import run_task, task_path

_TASK_FILE = task_path("cp4d", "read-existing-storage-classes.yml")

_NAMESPACE = "ibm-cpd"

_BASE_VARS = {
    "cpd_instance_namespace": _NAMESPACE,
    "cpd_platform_cr_name": "ibmcpd-cr",
    "cpd_primary_storage_class": "",
    "cpd_metadata_storage_class": "",
}


class TestReadExistingStorageClasses:

    def test_read_new_field_names(self, fake_k8s):
        fake_k8s.add_ibmcpd(_NAMESPACE, "ibmcpd-cr", {
            "storageClass": "cpd-file-sc",
            "zenCoreMetadbStorageClass": "cpd-block-sc",
        })
        result = run_task(_TASK_FILE, fake_k8s, _BASE_VARS)
        assert result.returncode == 0, (
            f"ansible-playbook failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
        assert "cpd-file-sc" in result.stdout
        assert "cpd-block-sc" in result.stdout

    def test_read_legacy_field_names(self, fake_k8s):
        fake_k8s.add_ibmcpd(_NAMESPACE, "ibmcpd-cr", {
            "fileStorageClass": "legacy-file-sc",
            "blockStorageClass": "legacy-block-sc",
        })
        result = run_task(_TASK_FILE, fake_k8s, _BASE_VARS)
        assert result.returncode == 0, (
            f"ansible-playbook failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
        assert "legacy-file-sc" in result.stdout
        assert "legacy-block-sc" in result.stdout

    def test_empty_field_falls_through_chain(self, fake_k8s):
        fake_k8s.add_ibmcpd(_NAMESPACE, "ibmcpd-cr", {
            "storageClass": "",
            "fileStorageClass": "fallback-file-sc",
        })
        result = run_task(_TASK_FILE, fake_k8s, _BASE_VARS)
        assert result.returncode == 0, (
            f"ansible-playbook failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
        assert "fallback-file-sc" in result.stdout

    def test_explicit_param_wins(self, fake_k8s):
        fake_k8s.add_ibmcpd(_NAMESPACE, "ibmcpd-cr", {
            "storageClass": "cpd-file-sc",
            "zenCoreMetadbStorageClass": "cpd-block-sc",
        })
        result = run_task(_TASK_FILE, fake_k8s, {
            **_BASE_VARS,
            "cpd_primary_storage_class": "explicit-rwx",
            "cpd_metadata_storage_class": "explicit-rwo",
        })
        assert result.returncode == 0, (
            f"ansible-playbook failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
        assert "explicit-rwx" in result.stdout
        assert "explicit-rwo" in result.stdout
        assert "cpd-file-sc" not in result.stdout
        assert "cpd-block-sc" not in result.stdout

    def test_no_cr(self, fake_k8s):
        result = run_task(_TASK_FILE, fake_k8s, _BASE_VARS)
        assert result.returncode == 0, (
            f"ansible-playbook failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
        assert "<not set>" in result.stdout

    def test_cr_without_storage_fields(self, fake_k8s):
        fake_k8s.add_ibmcpd(_NAMESPACE, "ibmcpd-cr", {"version": "5.0.0"})
        result = run_task(_TASK_FILE, fake_k8s, _BASE_VARS)
        assert result.returncode == 0, (
            f"ansible-playbook failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
        assert "<not set>" in result.stdout

    def test_preferred_cr_name_selected(self, fake_k8s):
        fake_k8s.add_ibmcpd(_NAMESPACE, "ibmcpd-cr", {"storageClass": "preferred-sc"})
        fake_k8s.add_ibmcpd(_NAMESPACE, "other-cr", {"storageClass": "other-sc"})
        result = run_task(_TASK_FILE, fake_k8s, _BASE_VARS)
        assert result.returncode == 0, (
            f"ansible-playbook failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
        assert "preferred-sc" in result.stdout
        assert "other-sc" not in result.stdout

    def test_legacy_cr_name_selected(self, fake_k8s):
        fake_k8s.add_ibmcpd(_NAMESPACE, "ibmcpd", {"storageClass": "legacy-cr-sc"})
        result = run_task(_TASK_FILE, fake_k8s, _BASE_VARS)
        assert result.returncode == 0, (
            f"ansible-playbook failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
        assert "legacy-cr-sc" in result.stdout

    def test_single_unnamed_cr_selected(self, fake_k8s):
        fake_k8s.add_ibmcpd(_NAMESPACE, "custom-cr", {"storageClass": "custom-sc"})
        result = run_task(_TASK_FILE, fake_k8s, _BASE_VARS)
        assert result.returncode == 0, (
            f"ansible-playbook failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
        assert "custom-sc" in result.stdout

    def test_ambiguous_crs_ignored(self, fake_k8s):
        fake_k8s.add_ibmcpd(_NAMESPACE, "custom-a", {"storageClass": "sc-a"})
        fake_k8s.add_ibmcpd(_NAMESPACE, "custom-b", {"storageClass": "sc-b"})
        result = run_task(_TASK_FILE, fake_k8s, _BASE_VARS)
        assert result.returncode == 0, (
            f"ansible-playbook failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
        assert "<not set>" in result.stdout
        assert "sc-a" not in result.stdout
        assert "sc-b" not in result.stdout
