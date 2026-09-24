import pytest

from utils import run_task, task_path

_TASK_FILE = task_path("aiservice_upgrade", "tenant", "delete_truststore_operator.yaml")


class TestDeleteTruststoreOperator:

    def test_deletion_when_subscription_found(self, fake_k8s):
        namespace = "mas-test-aiservice"
        csv_name = "ibm-truststore-mgr.v1.2.3"
        install_plan_name = "install-plan-abc"
        fake_k8s.add_subscription(namespace, "ibm-truststore-mgr", csv_name)
        fake_k8s.add_csv(namespace, csv_name)
        fake_k8s.add_install_plan(namespace, install_plan_name, [csv_name])
        fake_k8s.add_service_account(namespace, "ibm-truststore-mgr")
        fake_k8s.add_role(namespace, "ibm-truststore-mgr")
        fake_k8s.add_role_binding(namespace, "ibm-truststore-mgr", "ibm-truststore-mgr")
        fake_k8s.add_configmap(namespace, "ibm-truststore-mgr-config")
        fake_k8s.add_secret(namespace, "ibm-truststore-mgr-secret")

        result = run_task(_TASK_FILE, fake_k8s.kubeconfig_path, {"target_namespace": namespace})

        assert result.returncode == 0, (
            f"ansible-playbook failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
        assert (namespace, "ibm-truststore-mgr") in fake_k8s.get_deleted("Subscription")
        assert (namespace, csv_name) in fake_k8s.get_deleted("ClusterServiceVersion")
        assert (namespace, install_plan_name) in fake_k8s.get_deleted("InstallPlan")
        assert (namespace, "ibm-truststore-mgr") in fake_k8s.get_deleted("ServiceAccount")
        assert (namespace, "ibm-truststore-mgr") in fake_k8s.get_deleted("Role")
        assert (namespace, "ibm-truststore-mgr") in fake_k8s.get_deleted("RoleBinding")
        assert (namespace, "ibm-truststore-mgr-config") in fake_k8s.get_deleted("ConfigMap")
        assert (namespace, "ibm-truststore-mgr-secret") in fake_k8s.get_deleted("Secret")

    def test_skip_deletion_when_subscription_absent(self, fake_k8s):
        namespace = "mas-test-aiservice"
        result = run_task(_TASK_FILE, fake_k8s.kubeconfig_path, {"target_namespace": namespace})
        assert result.returncode == 0, (
            f"ansible-playbook failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
        assert fake_k8s.get_deleted("Subscription") == []
        assert fake_k8s.get_deleted("ClusterServiceVersion") == []
        assert fake_k8s.get_deleted("InstallPlan") == []
