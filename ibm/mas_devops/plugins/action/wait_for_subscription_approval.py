#!/usr/bin/env python3

import urllib3
from ansible.errors import AnsibleError
from ansible.plugins.action import ActionBase
from ansible.utils.display import Display
from ansible_collections.kubernetes.core.plugins.module_utils.k8s.client import get_api_client
from mas.devops.olm import OLMException, OLMTimeoutError

from ansible_collections.ibm.mas_devops.plugins.module_utils.olm_approvals import (
    resolveApprovalMode,
    resolveApprovalTimeout,
    waitForClusterApproval,
    waitForSubscriptionApproval,
)

urllib3.disable_warnings()  # Disabling warnings will prevent InsecureRequestWarnings from dynClient


class ActionModule(ActionBase):
    """
    Wait for install plan approvals and subscription convergence. This module
    never approves anything: under Manual approval it displays what is pending
    (and how to approve it with oc) and waits for the approval to be given
    out-of-band; under Automatic approval OLM issues the approvals itself. In
    both modes it then waits until every Subscription in the namespace has
    reached its channel head before returning.

    Usage Example
    -------------
    tasks:
      - name: "Wait for install plan approval"
        ibm.mas_devops.wait_for_subscription_approval:
          namespace: test-namespace
          package_name: ibm-sls (optional, echoed in the result as packageStatus)
          timeout: 7200 (optional, defaults to the OLM_APPROVAL_TIMEOUT env var or 7200)
          poll_interval: 30 (optional)

      - name: "Wait for install plan approval (all namespaces)"
        ibm.mas_devops.wait_for_subscription_approval:
          # The cluster-wide gate: the full scope of pending approvals is
          # disclosed up front (every plan across every namespace, with its oc
          # command) and the namespaces are waited on together -- approvals
          # may be granted in any order. Each namespace carries its own
          # timeout budget from when it is first observed.
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
                result = waitForSubscriptionApproval(
                    dynClient, display, namespace, packageName=packageName, timeout=timeout, pollInterval=pollInterval, approvalMode=approvalMode
                )
                waitedFor = [result["namespace"]] if result.get("waited") else []
                resultNamespaces = [result["namespace"]]
            else:
                # Cluster-wide gate: settle, disclose the full scope up front,
                # then wait on every namespace together (approvals may be
                # granted in any order). This is the gate for subscriptions
                # that roll implicitly, e.g. after a catalog digest update.
                result = waitForClusterApproval(dynClient, display, timeout=timeout, pollInterval=pollInterval, approvalMode=approvalMode)
                waitedFor = result["namespaces"] if result["waited"] else []
                resultNamespaces = result["namespaces"]
        except OLMTimeoutError as e:
            raise AnsibleError(f"Error: {e}") from e
        except OLMException as e:
            raise AnsibleError(f"Error waiting for install plan approval: {e}") from e
        except ValueError as e:
            raise AnsibleError(f"Error: {e}") from e

        # Only claim approvals were granted when the wait actually waited:
        # the status "waited" flag is False when there was never anything
        # pending (the honest message then is that nothing is waiting)
        if waitedFor:
            message = f"All install plan approvals have been granted in: {', '.join(waitedFor)} (and all subscriptions are at their channel head)"
        else:
            message = "No install plans are waiting for approval"

        return dict(message=message, success=True, failed=False, changed=False, namespaces=resultNamespaces)
