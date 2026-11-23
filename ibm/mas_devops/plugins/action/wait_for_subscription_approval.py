#!/usr/bin/env python3

import urllib3
from ansible.errors import AnsibleError
from ansible.plugins.action import ActionBase
from ansible.utils.display import Display
from ansible_collections.kubernetes.core.plugins.module_utils.k8s.client import get_api_client
from mas.devops.olm import OLMException, OLMTimeoutError, getPendingInstallPlans, waitForSubscriptionResolution

from ansible_collections.ibm.mas_devops.plugins.module_utils.olm_approvals import (
    resolveApprovalMode,
    resolveApprovalTimeout,
    waitForSubscriptionApproval,
)

urllib3.disable_warnings()  # Disabling warnings will prevent InsecureRequestWarnings from dynClient


class ActionModule(ActionBase):
    """
    Wait for manual install plan approvals. This module never approves
    anything: it displays what is pending (and how to approve it with oc) and
    waits for the approval to be given out-of-band, then waits for the
    affected operator to finish installing before returning.

    Usage Example
    -------------
    tasks:
      - name: "Wait for install plan approval"
        ibm.mas_devops.wait_for_subscription_approval:
          namespace: test-namespace
          package_name: ibm-sls (optional, waits for the operator to settle too)
          timeout: 7200 (optional, defaults to the OLM_APPROVAL_TIMEOUT env var or 7200)
          poll_interval: 30 (optional)

      - name: "Wait for install plan approval (all namespaces)"
        ibm.mas_devops.wait_for_subscription_approval:
    """

    def run(self, tmp=None, task_vars=None):
        super().run(tmp, task_vars)
        display = Display()

        namespace = self._task.args.get("namespace", None)
        packageName = self._task.args.get("package_name", None)
        timeoutArg = self._task.args.get("timeout", None)
        pollInterval = self._task.args.get("poll_interval", 30)

        try:
            approvalMode = resolveApprovalMode(self._task.args.get("approval_mode", None))
        except ValueError as e:
            raise AnsibleError(f"Error: {e}") from e

        try:
            timeout = resolveApprovalTimeout(timeoutArg)
        except ValueError as e:
            raise AnsibleError(f"Error: approval timeout must be an integer number of seconds: {e}") from e

        # Initialize DynamicClient
        host = self._task.args.get("host", None)
        api_key = self._task.args.get("api_key", None)
        dynClient = get_api_client(api_key=api_key, host=host)

        try:
            if namespace is not None:
                statuses = [
                    waitForSubscriptionApproval(
                        dynClient, display, namespace, packageName=packageName, timeout=timeout, pollInterval=pollInterval, approvalMode=approvalMode
                    )
                ]
            else:
                # Cluster-wide: settle first. Right after a catalog digest
                # update OLM may not have generated the new InstallPlans yet,
                # and a single snapshot cannot distinguish "not generated
                # yet" from "none coming" -- waitForSubscriptionResolution
                # returns once Subscription statuses have been stable for a
                # few polls (~1 minute), so the discovery below is not racing
                # OLM's re-resolution.
                waitForSubscriptionResolution(dynClient, namespace=None)

                # Discover every namespace with install plans awaiting
                # approval and wait for each in turn (each with its own
                # timeout budget). This is the gate for subscriptions that
                # roll implicitly, e.g. after a catalog digest update.
                pending = getPendingInstallPlans(dynClient, namespace=None)
                namespaces = sorted({approval["namespace"] for approval in pending})
                statuses = [
                    waitForSubscriptionApproval(dynClient, display, pendingNamespace, timeout=timeout, pollInterval=pollInterval, approvalMode=approvalMode)
                    for pendingNamespace in namespaces
                ]
        except OLMTimeoutError as e:
            raise AnsibleError(f"Error: {e}") from e
        except OLMException as e:
            raise AnsibleError(f"Error waiting for install plan approval: {e}") from e
        except ValueError as e:
            raise AnsibleError(f"Error: {e}") from e

        # Only claim approvals were granted when the wait actually waited:
        # the status "waited" flag is False when there was never anything
        # pending (the honest message then is that nothing is waiting)
        waitedFor = [status["namespace"] for status in statuses if status.get("waited")]
        if waitedFor:
            message = f"All install plan approvals have been granted in: {', '.join(waitedFor)}"
        else:
            message = "No install plans are waiting for approval"

        return dict(message=message, success=True, failed=False, changed=False, namespaces=[status["namespace"] for status in statuses])
