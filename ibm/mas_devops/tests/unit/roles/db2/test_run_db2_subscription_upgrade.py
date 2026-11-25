"""
Structural tests for the db2 subscription upgrade task file.

The subscription channel upgrade must gate on manual install plan approvals
(wait_for_subscription_approval) immediately after the subscription is
patched: under Manual approval the channel change generates a pending
InstallPlan, and the gate is what discloses it (with its oc command) and
waits for the convergence the rest of the task file assumes.

A behavioral end-to-end test would need the fake Kubernetes server to grow
OperatorGroup, apps/v1 and resource-creation support (apply_subscription
creates the namespace and operator group before patching the subscription),
so these tests pin the task structure instead: the gate is present, in the
right position, and the pre-convergence hand-rolled waits it replaced (the
currentCSV == installedCSV poll and the settle pauses) are gone.
"""

from pathlib import Path

import yaml

_TASK_FILE = Path(__file__).resolve().parents[4] / "roles" / "db2" / "tasks" / "upgrade" / "run-db2-subscription-upgrade.yml"


def _load_tasks() -> list:
    with open(_TASK_FILE) as f:
        tasks = yaml.safe_load(f)
    assert isinstance(tasks, list), "the task file did not parse as a YAML list"
    return tasks


_META_KEYS = ("name", "when", "register", "tags", "loop", "vars", "until", "retries", "delay", "ignore_errors")


def _module_names(tasks: list) -> list:
    """The action module key of each task, in file order."""
    names = []
    for task in tasks:
        keys = [key for key in task if key not in _META_KEYS]
        assert len(keys) == 1, f"expected exactly one module per task, found {keys}"
        names.append(keys[0])
    return names


class TestRunDb2SubscriptionUpgrade:
    def test_approval_gate_present_and_positioned_after_the_channel_patch(self):
        tasks = _load_tasks()
        modules = _module_names(tasks)

        assert "ibm.mas_devops.wait_for_subscription_approval" in modules, (
            "the db2 subscription upgrade has no approval gate: under Manual approval the channel change generates a pending InstallPlan that nothing waits on"
        )

        # The gate must sit between the subscription patch and the deployment
        # readiness wait: apply_subscription's internal waits only cover the
        # initial install, not the upgrade plan
        patchIndex = modules.index("ibm.mas_devops.apply_subscription")
        gateIndex = modules.index("ibm.mas_devops.wait_for_subscription_approval")
        assert patchIndex < gateIndex, "the approval gate must come after the subscription channel patch"
        deploymentIndex = next(i for i, module in enumerate(modules) if module == "kubernetes.core.k8s_info" and tasks[i][module].get("kind") == "Deployment")
        assert gateIndex < deploymentIndex, "the approval gate must come before the operator deployment readiness wait"

        # The gate targets the namespace and package the channel patch changed
        gate = tasks[gateIndex]
        assert gate["ibm.mas_devops.wait_for_subscription_approval"]["namespace"] == "{{ db2_namespace }}"
        assert gate["ibm.mas_devops.wait_for_subscription_approval"]["package_name"] == "db2u-operator"

    def test_hand_rolled_convergence_waits_are_gone(self):
        """The gate performs the convergence wait, so the waits it replaced must not return."""
        tasks = _load_tasks()
        modules = _module_names(tasks)

        # The settle pauses around the (removed) subscription status poll
        assert "pause" not in modules, "settle pauses are dead weight around the convergence gate"

        # The hand-rolled currentCSV == installedCSV poll: exactly the wait
        # the gate now performs, and the thing that failed after ~10 minutes
        # under Manual approval with no disclosure of what to approve
        for task in tasks:
            if task.get("kind") == "Subscription":
                assert not any("currentCSV" in str(condition) for condition in task.get("until", [])), (
                    "a Subscription status poll survived: the approval gate performs this wait"
                )
