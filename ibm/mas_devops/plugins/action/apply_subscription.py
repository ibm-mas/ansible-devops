#!/usr/bin/env python3

import os

import urllib3
from ansible.errors import AnsibleError
from ansible.plugins.action import ActionBase
from ansible.utils.display import Display
from ansible_collections.kubernetes.core.plugins.module_utils.k8s.client import get_api_client
from mas.devops.olm import OLMException, OLMTimeoutError, applySubscription, getSubscription

from ansible_collections.ibm.mas_devops.plugins.module_utils.olm_approvals import (
    resolveTaskApprovalMode,
    resolveTaskApprovalTimeout,
    waitForSubscriptionApproval,
)

urllib3.disable_warnings()  # Disabling warnings will prevent InsecureRequestWarnings from dynClient


class ActionModule(ActionBase):
    """
    Usage Example
    -------------
    tasks:
      - name: "Apply Subscription"
        ibm.mas_devops.apply_subscription:
          namespace: test-namespace
          package_name: ibm-sls
          package_channel: 3.x
          install_mode: AllNamespaces (default is OwnNamespace)
          install_plan_approval: Manual (optional, defaults to the OLM_APPROVAL_MODE env var, or unset)
          starting_csv: ibm-sls.v3.8.0 (optional)
        register: subscription

    When the effective approval mode is Manual (from the install_plan_approval
    argument or the OLM_APPROVAL_MODE environment variable) and an install plan
    is awaiting approval, this module displays what is pending and how to
    approve it, then waits for the approval to be given out-of-band (never
    approving on your behalf) before returning. The wait budget is the
    OLM_APPROVAL_TIMEOUT environment variable (default 7200 seconds).

    The effective approval mode is resolved as task argument > OLM_APPROVAL_MODE
    environment variable > Automatic, and is always a concrete value. When the
    existing subscription for the package uses a different mode the mismatch
    check is asymmetric:

    - An explicit install_plan_approval argument fails on conflict in either
      direction (it is imposing)
    - A resolved Automatic mode (including the unset default) over an existing
      Manual subscription fails fast: the automation never turns off human
      gating
    - A resolved Manual mode over an existing Automatic subscription preserves
      the subscription's Automatic mode with a warning (it keeps rolling
      freely) -- this is what keeps mixed-approval clusters updatable, since
      mas update/upgrade pass Manual for their whole scope while some of the
      subscriptions they re-apply are Automatic
    """

    def run(self, tmp=None, task_vars=None):
        super().run(tmp, task_vars)
        display = Display()

        # Target subscription
        namespace = self._task.args.get("namespace", None)
        config = self._task.args.get("config", None)

        # From which package?
        packageName = self._task.args.get("package_name", None)
        packageChannel = self._task.args.get("package_channel", None)

        # From which catalog?
        catalogSource = self._task.args.get("catalog_source", None)
        catalogSourceNamespace = self._task.args.get("catalog_source_namespace", None)

        # Which install mode?
        installMode = self._task.args.get("install_mode", "OwnNamespace")

        # Install plan approval and starting CSV (optional). The effective
        # approval mode is resolved as task argument > OLM_APPROVAL_MODE env
        # var > Automatic: it is always a concrete value, and a mismatch with
        # an existing subscription fails fast rather than slow-failing later
        # in the operator readiness waits
        installPlanApprovalArg = self._task.args.get("install_plan_approval", None)
        startingCSV = self._task.args.get("starting_csv", None)

        if namespace is None:
            raise AnsibleError("Error: namespace argument was not provided")
        if not isinstance(packageName, str):
            raise AnsibleError("Error: packageName argument is not a string")

        try:
            installPlanApproval = resolveTaskApprovalMode(installPlanApprovalArg)
        except ValueError as e:
            raise AnsibleError(f"Error: {e}") from e
        if installPlanApproval is None:
            installPlanApproval = "Automatic"
        timeout = resolveTaskApprovalTimeout(self._task.args.get("approval_timeout", None))

        # Initialize DynamicClient
        host = self._task.args.get("host", None)
        api_key = self._task.args.get("api_key", None)

        dynClient = get_api_client(api_key=api_key, host=host)

        # Fail fast when the existing subscription for this package uses a
        # different approval mode than the effective one. This runs even when
        # no mode was requested (default Automatic): re-applying a Manual
        # subscription as Automatic used to slow-fail in the operator
        # readiness waits, and now fails immediately with instructions.
        #
        # The check is asymmetric (owner-confirmed semantics):
        # - An explicit install_plan_approval argument is imposing: it fails
        #   on conflict in either direction
        # - A requested Automatic mode (including the unset default) over an
        #   existing Manual subscription is fatal: the automation must never
        #   turn off human gating
        # - A requested Manual mode over an existing Automatic subscription
        #   preserves the subscription's Automatic mode with a warning (it
        #   keeps rolling freely). This is what keeps mixed-approval clusters
        #   updatable: mas update/upgrade pass Manual for their whole scope
        #   while some of the subscriptions they re-apply are Automatic
        #
        # Only the subscription this collection manages is checked: OLM
        # auto-creates dependency subscriptions with a different mode, and
        # mixed namespaces are valid (they behave the same as Manual)
        existingSubscription = getSubscription(dynClient, namespace, packageName)
        if existingSubscription is not None:
            existingMode = getattr(existingSubscription.spec, "installPlanApproval", None) or "Automatic"
            if existingMode != installPlanApproval:
                if installPlanApprovalArg is not None:
                    # An explicit task argument is imposing in both directions
                    raise AnsibleError(
                        f"Error: approval mode mismatch for {packageName} in {namespace}: the existing subscription "
                        f"{existingSubscription.metadata.name} uses '{existingMode}' but install_plan_approval is set to "
                        f"'{installPlanApproval}'. Set install_plan_approval={existingMode} to manage this subscription as '{existingMode}'"
                    )
                elif existingMode == "Manual":
                    # We cannot turn off human gating on an existing Manual
                    # subscription: fail fast with the remedy
                    if os.environ.get("OLM_APPROVAL_MODE"):
                        modeSource = f"the OLM_APPROVAL_MODE environment variable is set to '{installPlanApproval}'"
                    else:
                        modeSource = "the approval mode is not set (default 'Automatic')"
                    raise AnsibleError(
                        f"Error: approval mode mismatch for {packageName} in {namespace}: the existing subscription "
                        f"{existingSubscription.metadata.name} uses 'Manual' but {modeSource}. "
                        "Manual install plan approval cannot be disabled by the automation; "
                        "set OLM_APPROVAL_MODE=Manual so that the automation waits for the approvals instead"
                    )
                else:
                    # Requested Manual over an existing Automatic subscription:
                    # warn and preserve the existing mode rather than flipping
                    # it, so the subscription keeps rolling freely
                    display.warning(
                        f"Existing subscription {existingSubscription.metadata.name} for {packageName} in {namespace} is set to "
                        f"Automatic, but the OLM approval mode is Manual: preserving the subscription's Automatic approval mode"
                    )
                    installPlanApproval = existingMode

        try:
            if installPlanApproval == "Manual":
                # New-style approval handling: applySubscription releases as
                # soon as an install plan is awaiting approval, then we wait
                # for the human to approve it (never approving on their
                # behalf) and for the operator to finish installing
                result = applySubscription(
                    dynClient,
                    namespace,
                    packageName,
                    packageChannel,
                    catalogSource,
                    catalogSourceNamespace,
                    config,
                    installMode,
                    installPlanApproval=installPlanApproval,
                    startingCSV=startingCSV,
                    onApprovalRequired="return",
                    pollInterval=30,
                )
                if isinstance(result, tuple):
                    # applySubscription released with a pending approval: the
                    # gate prints the notices and waits for the human to
                    # approve it (never approving on their behalf)
                    subscription, _ = result
                    waitForSubscriptionApproval(dynClient, display, namespace, packageName=packageName, timeout=timeout, approvalMode="Manual")
                else:
                    subscription = result
            else:
                subscription = applySubscription(
                    dynClient,
                    namespace,
                    packageName,
                    packageChannel,
                    catalogSource,
                    catalogSourceNamespace,
                    config,
                    installMode,
                    installPlanApproval=installPlanApproval,
                    startingCSV=startingCSV,
                )
        except OLMTimeoutError as e:
            raise AnsibleError(f"Error applying subscription: {e}") from e
        except OLMException as e:
            raise AnsibleError(f"Error applying subscription: {e}") from e

        if subscription is None:
            return dict(message=f"Failed to apply subscription for {packageName} in {namespace} ({installMode})", success=False, failed=True, changed=False)

        return dict(
            message=f"Successfully applied subscription for {packageName} in {namespace}: {subscription.metadata.name} ({installMode})",
            success=True,
            failed=False,
            changed=False,
            **subscription.to_dict(),
        )
