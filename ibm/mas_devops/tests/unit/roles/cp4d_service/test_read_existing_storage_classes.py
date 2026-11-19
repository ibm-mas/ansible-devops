
from utils import run_task, task_path

_TASK_FILE = task_path("cp4d_service", "read-existing-storage-classes.yml")

_NAMESPACE = "ibm-cpd"

_BASE_VARS = {
    "cpd_instance_namespace": _NAMESPACE,
    "cpd_platform_cr_name": "ibmcpd-cr",
    "cpd_service_name": "wsl",
    "cpd_service_info": {
        "wsl": {
            "api_version": "ws.cpd.ibm.com/v1beta1",
            "crd_kind": "WS",
            "cr_name": "ws-cr",
        },
    },
    "cpd_service_storage_class": "",
    "cpd_service_block_storage_class": "",
}


class TestReadExistingStorageClasses:

    def test_read_from_service_cr(self, fake_k8s):
        fake_k8s.add_ws(_NAMESPACE, "ws-cr", {
            "fileStorageClass": "ws-file-sc",
            "blockStorageClass": "ws-block-sc",
        })
        result = run_task(_TASK_FILE, fake_k8s, _BASE_VARS)
        assert result.returncode == 0, (
            f"ansible-playbook failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
        assert "ws-file-sc" in result.stdout
        assert "ws-block-sc" in result.stdout

    def test_fallback_to_platform_cr(self, fake_k8s):
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

    def test_service_cr_without_storage_fields_falls_back_to_platform_cr(self, fake_k8s):
        fake_k8s.add_ws(_NAMESPACE, "ws-cr", {"version": "5.0.0"})
        fake_k8s.add_ibmcpd(_NAMESPACE, "ibmcpd-cr", {
            "fileStorageClass": "platform-file-sc",
            "blockStorageClass": "platform-block-sc",
        })
        result = run_task(_TASK_FILE, fake_k8s, _BASE_VARS)
        assert result.returncode == 0, (
            f"ansible-playbook failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
        assert "platform-file-sc" in result.stdout
        assert "platform-block-sc" in result.stdout

    def test_explicit_param_wins(self, fake_k8s):
        fake_k8s.add_ws(_NAMESPACE, "ws-cr", {
            "fileStorageClass": "ws-file-sc",
            "blockStorageClass": "ws-block-sc",
        })
        result = run_task(_TASK_FILE, fake_k8s, {
            **_BASE_VARS,
            "cpd_service_storage_class": "explicit-rwx",
            "cpd_service_block_storage_class": "explicit-rwo",
        })
        assert result.returncode == 0, (
            f"ansible-playbook failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
        assert "explicit-rwx" in result.stdout
        assert "explicit-rwo" in result.stdout
        assert "ws-file-sc" not in result.stdout
        assert "ws-block-sc" not in result.stdout

    def test_nothing_found(self, fake_k8s):
        result = run_task(_TASK_FILE, fake_k8s, _BASE_VARS)
        assert result.returncode == 0, (
            f"ansible-playbook failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
        assert "<not set>" in result.stdout

    def test_lookup_with_unrendered_sibling_keys(self, fake_k8s):
        """cpd_service_info entries contain keys referencing cpd_components_meta,
        which is not loaded when determine-storage-classes.yml runs. Accessing
        only the CR coordinate keys must not trigger templating of the siblings.
        """
        fake_k8s.add_ws(_NAMESPACE, "ws-cr", {
            "fileStorageClass": "ws-file-sc",
            "blockStorageClass": "ws-block-sc",
        })
        result = run_task(_TASK_FILE, fake_k8s, {
            **_BASE_VARS,
            "cpd_service_info": {
                "wsl": {
                    "api_version": "ws.cpd.ibm.com/v1beta1",
                    "crd_kind": "WS",
                    "cr_name": "ws-cr",
                    "case_version": "{{ cpd_components_meta.ws.case_version }}",
                },
            },
        })
        assert result.returncode == 0, (
            f"ansible-playbook failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
        assert "ws-file-sc" in result.stdout
        assert "ws-block-sc" in result.stdout
