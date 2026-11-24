from utils import run_task, task_path

_TASK_FILE = task_path("aiservice_upgrade", "tenant", "upgrade.yml")

# Version constants — OperatorCondition name format is {pkg}.v{version}
_OLD_VERSION = "9.1.0"
_NEW_VERSION = "9.1.2"
_OPCON_NAME = f"ibm-aiservice-tenant.v{_NEW_VERSION}"


def _base_variables(namespace: str, channel: str = "v9.1.x") -> dict:
    return {
        # Complex dict — run_task embeds this as structured YAML
        "tenant_subscription": {
            "metadata": {"name": "ibm-aiservice-tenant", "namespace": namespace},
            "spec": {
                "name": "ibm-aiservice-tenant",
                "channel": "9.1.x",
                "source": "ibm-operator-catalog",
                "sourceNamespace": "openshift-marketplace",
            },
            "status": {
                "installedCSV": f"ibm-aiservice-tenant.v{_OLD_VERSION}",
                "currentCSV": f"ibm-aiservice-tenant.v{_OLD_VERSION}",
                "state": "AtLatestKnown",
                "installPlanGeneration": 1,
            },
        },
        "aiservice_tenant_channel": channel,
        # Pre-upgrade operator version (used only in a debug message)
        "opcon_version": _OLD_VERSION,
    }


class TestTenantUpgrade:

    def test_upgrade_succeeds(self, fake_k8s):
        namespace = "mas-test-aiservice"
        target_channel = "9.2.x"
        fake_k8s.add_subscription(
            namespace,
            "ibm-aiservice-tenant",
            f"ibm-aiservice-tenant.v{_OLD_VERSION}",
            # currentCSV is the channel head the subscription is rolling to;
            # the fake server promotes installedCSV to it when the channel
            # patch is applied (the rollout the convergence gate waits for)
            current_csv=f"ibm-aiservice-tenant.v{_NEW_VERSION}",
            install_plan_generation=1,
            channel="v9-1",
        )
        # The channel head the convergence gate resolves its target from
        fake_k8s.add_package_manifest(
            "openshift-marketplace",
            "ibm-aiservice-tenant",
            {"9.2.x": f"ibm-aiservice-tenant.v{_NEW_VERSION}"},
        )
        # OperatorCondition returned by the label-selector list — must be exactly 1
        fake_k8s.add_operator_condition(namespace, _OPCON_NAME)
        # AIServiceTenant with reconciled version matching the new opcon version
        fake_k8s.add_aiservice_tenant(namespace, namespace, _NEW_VERSION)

        result = run_task(_TASK_FILE, fake_k8s, _base_variables(namespace, channel=target_channel))

        assert result.returncode == 0, f"ansible-playbook failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"

        sub = fake_k8s._subscriptions.get((namespace, "ibm-aiservice-tenant"))
        assert sub is not None
        assert sub["spec"]["channel"] == target_channel
        assert sub["status"]["installPlanGeneration"] > 1

        # The convergence gate resolved the channel head from the PackageManifest
        # (a skipped target would have logged the warning instead)
        assert any("packagemanifests" in path for path in fake_k8s._request_log), "the approval gate did not consult the PackageManifest"
        assert (
            "Cannot determine the channel head" not in result.stdout
        ), "the approval gate skipped the subscription instead of converging on the manifest target"

        # Verify the delete_truststore_operator subtask was invoked (it always GETs this subscription)
        assert any("ibm-truststore-mgr" in path for path in fake_k8s._request_log), "delete_truststore_operator subtask was not called"
