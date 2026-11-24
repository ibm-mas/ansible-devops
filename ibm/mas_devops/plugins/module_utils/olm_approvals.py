#!/usr/bin/env python3

"""
Shared OLM manual install plan approval support for the collection's action
plugins.

Manual approval mode (OLM_APPROVAL_MODE=Manual) means a human approves every
InstallPlan: this module NEVER approves on the user's behalf -- it formats the
human-facing notices (what is pending, what it will change, how to approve it)
and waits for the approval to be given out-of-band, with a per-wait timeout.

The approval info contract is the python-devops one (mas.devops.olm):
    {installPlan, namespace, subscription, package, csvNames,
     currentCSV, targetCSV, created}
"""

import json
import os
from datetime import datetime, timezone

from mas.devops.olm import (
    OLMTimeoutError,
    getNamespaceApprovalStatus,
    waitForSubscriptionConvergence,
)

# Default per-wait budget for a human to grant approval (2 hours), in seconds
DEFAULT_APPROVAL_TIMEOUT = 7200

# How often (seconds) the "still waiting" status line is repeated while a
# wait is in progress -- the underlying poll is much faster than this
STATUS_INTERVAL = 300

VALID_APPROVAL_MODES = ("Automatic", "Manual")


def resolveApprovalMode(taskArg=None):
    """
    Resolve the effective install plan approval mode.

    Precedence: task argument > OLM_APPROVAL_MODE environment variable > None
    (None leaves the subscription's approval mode untouched, which is the
    collection's default behavior).

    Raises ValueError when a value is not "Automatic" or "Manual" (the
    environment variable is named in the message so the fix is obvious).
    """
    if taskArg is not None:
        if taskArg not in VALID_APPROVAL_MODES:
            raise ValueError(f"install_plan_approval must be one of: {', '.join(VALID_APPROVAL_MODES)} (found '{taskArg}')")
        return taskArg

    envMode = os.environ.get("OLM_APPROVAL_MODE")
    if envMode:
        if envMode not in VALID_APPROVAL_MODES:
            raise ValueError(f"OLM_APPROVAL_MODE must be one of: {', '.join(VALID_APPROVAL_MODES)} (found '{envMode}')")
        return envMode
    return None


def resolveApprovalTimeout(taskArg=None):
    """
    Resolve the per-wait approval timeout in seconds.

    Precedence: task argument > OLM_APPROVAL_TIMEOUT environment variable >
    DEFAULT_APPROVAL_TIMEOUT (7200 seconds = 2 hours).
    """
    if taskArg is not None:
        return int(taskArg)
    envTimeout = os.environ.get("OLM_APPROVAL_TIMEOUT")
    if envTimeout:
        return int(envTimeout)
    return DEFAULT_APPROVAL_TIMEOUT


def approveCommand(approval):
    """The oc command a human runs to grant approval for a pending install plan."""
    patch = json.dumps({"spec": {"approved": True}}, separators=(",", ":"))
    return f"oc patch installplan/{approval['installPlan']} -n {approval['namespace']} --type merge -p '{patch}'"


def formatApprovalNotice(approval):
    """
    Format the human-facing notice for one pending install plan.

    Returns a list of lines: what is waiting, a summary of what the plan will
    change, and how to grant approval.
    """
    currentCSV = approval.get("currentCSV") or "(not installed)"
    csvNames = ", ".join(approval.get("csvNames") or [])
    return [
        f"Waiting for manual approval of install plan {approval['installPlan']} in namespace {approval['namespace']}",
        f"Install plan contents: {approval['package']} (subscription {approval['subscription']}): {currentCSV} -> {approval['targetCSV']}",
        f"  CSVs to install: {csvNames} (plan created {approval.get('created')})",
        f'To grant approval run "{approveCommand(approval)}" or use the OpenShift Console',
    ]


def _formatTimestamp(timestamp):
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def waitForSubscriptionApproval(dynClient, display, namespace, packageName=None, timeout=None, pollInterval=30, approvalMode=None):
    """
    Wait for every Subscription in a namespace to reach its channel head.

    The wait is deterministic: each Subscription's target (the currentCSV of
    its channel in the operator's PackageManifest) is known up front, so
    there is no timing window in which a just-created or just-patched
    Subscription can be mistaken for a settled one. A Subscription that has
    not converged is simply not done -- whether its InstallPlan has not been
    generated yet, is awaiting approval, or is still installing -- and
    InstallPlans being namespace-scoped, every Subscription in the namespace
    is considered, not just the one the calling role created.

    Both approval modes run the same convergence wait; the only difference
    is the messaging:

    1. Under Manual approval the pending InstallPlans are the human-facing
       notices (what is pending, what it will change, the oc command to
       approve it). They are displayed when first seen -- including plans
       that appear mid-wait, for example the second step of a multi-step
       upgrade path -- and a status line ("Waiting for install plan approval
       since <x>, approval deadline <y>") repeats every STATUS_INTERVAL
       seconds so it is clear the wait has not died.
    2. Under Automatic approval OLM issues the approvals itself; the wait
       is for the resulting rollout, with an equivalent status line.

    The timeout (resolved by the caller via resolveApprovalTimeout) budgets
    the approval however it is issued: a human under Manual, OLM under
    Automatic. On expiry it is fatal in both modes -- under Manual the
    approve commands are repeated in the error, under Automatic each
    non-converged Subscription is listed as installedCSV -> targetCSV.

    When install plans are pending in a namespace whose effective context is
    anything other than "Manual" (including unset, which is an Automatic
    context) this is an approval mode mismatch and a ValueError is raised
    with the approve commands and the OLM_APPROVAL_MODE=Manual remedy --
    both from the initial snapshot and for plans that appear mid-wait
    (pending install plans in an Automatic context used to slow-fail the
    calling role's readiness waits; now they fail fast with instructions).

    Subscriptions that cannot converge fail the wait immediately with an
    actionable error (ResolutionFailed condition or a Failed InstallPlan),
    in both modes, rather than burning the timeout.

    Mixed-mode namespaces (OLM auto-creates dependency subscriptions with
    default Automatic approval inside Manual namespaces) behave the same as
    Manual: reported, never fatal.

    packageName does not narrow the wait (and never did narrow the approval
    wait): it is echoed in the returned status as packageStatus so callers
    can confirm the Subscription they care about, while sibling
    subscriptions in the namespace are waited on equally.

    The returned status dict is the python-devops namespace convergence
    status with two added keys: waited (bool, True only when install plans
    were observed awaiting approval at some point, so callers can
    distinguish "approvals were granted" from "there was never anything to
    approve") and packageStatus (the per-Subscription status entry matching
    packageName, or None).

    Raises OLMTimeoutError when the timeout expires (with the approve
    commands repeated in the message under Manual) and ValueError on the
    Automatic mismatch. Both are translated by the action plugins.
    """
    status = getNamespaceApprovalStatus(dynClient, namespace)

    if status["blocking"] and approvalMode != "Manual":
        # Includes an unset (None) mode: pending install plans in an
        # Automatic context are a mode mismatch that must fail fast (with
        # instructions) rather than hang the calling role's readiness waits
        commands = "\n".join(f"  {approveCommand(approval)}" for approval in status["pendingApprovals"])
        raise ValueError(
            f"Install plans are waiting for manual approval in namespace {namespace}, but the effective "
            f"approval mode is '{approvalMode or 'Automatic'}'. Either grant approval:\n{commands}\n"
            "or set OLM_APPROVAL_MODE=Manual so that the automation waits for the approvals instead"
        )

    # Mixed namespaces (OLM auto-created dependency subscriptions) behave the
    # same as Manual: report, don't fail
    if status["approvalMode"] == "Mixed":
        display.display(
            f"Namespace {namespace} contains a mix of approval modes (OLM auto-creates dependency "
            "subscriptions with default Automatic approval); treating the namespace as Manual"
        )

    manualContext = approvalMode == "Manual"

    # The install plans already pending at entry get their notices up front;
    # plans that appear mid-wait get theirs from the onPending callback below
    seenPlanNames = set()
    for approval in status["pendingApprovals"]:
        seenPlanNames.add(approval["installPlan"])
        if manualContext:
            for line in formatApprovalNotice(approval):
                display.display(line)

    waited = status["blocking"]
    startTime = datetime.now(timezone.utc)
    startTs = startTime.timestamp()
    deadlineTs = startTs + timeout if timeout is not None else None
    lastStatusLog = [None]

    def onPending(pendingStatus, pollCount):
        nonlocal waited
        waited = waited or pendingStatus["blocking"]

        if not manualContext and pendingStatus["blocking"]:
            # A plan appeared after the initial snapshot (a just-created
            # Subscription's first plan, or a channel change's new plan):
            # the same mismatch as above, caught late
            commands = "\n".join(f"  {approveCommand(approval)}" for approval in pendingStatus["pendingApprovals"])
            raise ValueError(
                f"Install plans are waiting for manual approval in namespace {namespace}, but the effective "
                f"approval mode is '{approvalMode or 'Automatic'}'. Either grant approval:\n{commands}\n"
                "or set OLM_APPROVAL_MODE=Manual so that the automation waits for the approvals instead"
            )

        if manualContext:
            for approval in pendingStatus["pendingApprovals"]:
                if approval["installPlan"] not in seenPlanNames:
                    seenPlanNames.add(approval["installPlan"])
                    for line in formatApprovalNotice(approval):
                        display.display(line)

        now = datetime.now(timezone.utc).timestamp()
        if lastStatusLog[0] is None or now - lastStatusLog[0] >= STATUS_INTERVAL:
            lastStatusLog[0] = now
            if manualContext:
                if deadlineTs is not None:
                    display.display(
                        f"Waiting for install plan approval since {_formatTimestamp(startTs)}, " f"approval deadline {_formatTimestamp(deadlineTs)}"
                    )
                else:
                    display.display(f"Waiting for install plan approval since {_formatTimestamp(startTs)} (no timeout)")
            else:
                unconverged = [entry["name"] for entry in pendingStatus["subscriptions"] if entry["converged"] is False]
                if deadlineTs is not None:
                    display.display(
                        f"Waiting for {len(unconverged)} subscription(s) in {namespace} to reach their channel head "
                        f"({', '.join(unconverged)}), approval deadline {_formatTimestamp(deadlineTs)}"
                    )
                else:
                    display.display(
                        f"Waiting for {len(unconverged)} subscription(s) in {namespace} to reach their channel head ({', '.join(unconverged)}) (no timeout)"
                    )
        # Returning False aborts the wait; anything else keeps waiting
        return True

    try:
        finalStatus = waitForSubscriptionConvergence(dynClient, namespace, timeout=timeout, pollInterval=pollInterval, onPending=onPending)
    except OLMTimeoutError as e:
        if manualContext:
            # Re-raise with the approve commands so the failure is actionable
            # on its own: the notices have likely scrolled away by now
            current = getNamespaceApprovalStatus(dynClient, namespace)
            commands = "\n".join(f"  {approveCommand(approval)}" for approval in current["pendingApprovals"])
            raise OLMTimeoutError(
                f"Timed out after {timeout}s waiting for manual install plan approval in namespace {namespace}. " f"To grant approval run:\n{commands}"
            ) from e
        # Automatic: the underlying message already lists each Subscription
        # as installedCSV -> targetCSV
        raise

    finalStatus["waited"] = waited
    finalStatus["packageStatus"] = None
    if packageName is not None:
        for entry in finalStatus["subscriptions"]:
            if entry["package"] == packageName or entry["name"] == packageName:
                finalStatus["packageStatus"] = entry
                break
    return finalStatus
