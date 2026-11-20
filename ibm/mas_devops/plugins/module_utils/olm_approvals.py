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
    waitForInstallPlanComplete,
    waitForNamespaceApprovals,
    waitForSubscriptionStable,
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


def waitForSubscriptionApproval(dynClient, display, namespace, packageName=None, targetCSV=None, timeout=None, pollInterval=30, approvalMode=None):
    """
    Wait for the install plans in a namespace to be approved by a human.

    A cheap no-op when nothing is pending: the namespace approval status is
    fetched once and the function returns immediately when nothing is
    blocking. When install plans are waiting:

    1. If approvalMode is "Automatic" this is an approval mode mismatch and a
       ValueError is raised (install plans awaiting approval make no sense in
       a namespace the collection is managing as Automatic).
    2. The human-facing notices (what is pending, what it will change, the oc
       command to approve it) are displayed, then the wait begins. A status
       line ("Waiting for install plan approval since <x>, approval deadline
       <y>") is displayed on the first poll and every STATUS_INTERVAL seconds
       after that, so it is clear the wait has not died.
    3. Once the approvals are given, the install plan for packageName (when
       provided) is waited to Complete and the subscription to settle at
       targetCSV (AtLatestKnown, or UpgradePending with installedCSV ==
       targetCSV under Manual approval).

    Mixed-mode namespaces (OLM auto-creates dependency subscriptions with
    default Automatic approval inside Manual namespaces) behave the same as
    Manual: reported, never fatal.

    Raises OLMTimeoutError (with the approve commands repeated in the
    message) when the timeout expires, and ValueError on the Automatic
    mismatch. Both are translated by the action plugins.
    """
    status = getNamespaceApprovalStatus(dynClient, namespace)
    if not status["blocking"]:
        return status

    if approvalMode == "Automatic":
        pending = ", ".join(approval["installPlan"] for approval in status["pendingApprovals"])
        raise ValueError(
            f"Install plans are waiting for manual approval in namespace {namespace} ({pending}) "
            "but the effective approval mode is 'Automatic'. This is a mismatch between OLM_APPROVAL_MODE "
            "(or the install_plan_approval argument) and the state of the cluster"
        )

    # Mixed namespaces (OLM auto-created dependency subscriptions) behave the
    # same as Manual: report, don't fail
    if status["approvalMode"] == "Mixed":
        display.display(
            f"Namespace {namespace} contains a mix of approval modes (OLM auto-creates dependency "
            "subscriptions with default Automatic approval); treating the namespace as Manual"
        )

    for approval in status["pendingApprovals"]:
        for line in formatApprovalNotice(approval):
            display.display(line)

    startTime = datetime.now(timezone.utc)
    startTs = startTime.timestamp()
    deadlineTs = startTs + timeout if timeout is not None else None
    lastStatusLog = [None]

    def onPending(pendingStatus, pollCount):
        now = datetime.now(timezone.utc).timestamp()
        if lastStatusLog[0] is None or now - lastStatusLog[0] >= STATUS_INTERVAL:
            lastStatusLog[0] = now
            if deadlineTs is not None:
                display.display(
                    f"Waiting for install plan approval since {_formatTimestamp(startTs)}, "
                    f"approval deadline {_formatTimestamp(deadlineTs)}"
                )
            else:
                display.display(f"Waiting for install plan approval since {_formatTimestamp(startTs)} (no timeout)")
        # Returning False aborts the wait; anything else keeps waiting
        return True

    try:
        waitForNamespaceApprovals(dynClient, namespace, timeout=timeout, pollInterval=pollInterval, onPending=onPending)
    except OLMTimeoutError as e:
        # Re-raise with the approve commands so the failure is actionable on
        # its own: the notices have likely scrolled away by now
        current = getNamespaceApprovalStatus(dynClient, namespace)
        commands = "\n".join(f"  {approveCommand(approval)}" for approval in current["pendingApprovals"])
        raise OLMTimeoutError(
            f"Timed out after {timeout}s waiting for manual install plan approval in namespace {namespace}. "
            f"To grant approval run:\n{commands}"
        ) from e

    # The approvals have been given: wait for the install plan to complete
    # and the subscription to settle before handing control back to the role
    if packageName is not None:
        for approval in status["pendingApprovals"]:
            if approval.get("package") == packageName or approval.get("subscription") == packageName:
                waitForInstallPlanComplete(dynClient, namespace, approval["installPlan"], timeout=timeout, pollInterval=pollInterval)
                break
        waitForSubscriptionStable(dynClient, namespace, packageName, timeout=timeout, pollInterval=pollInterval, targetCSV=targetCSV)

    return getNamespaceApprovalStatus(dynClient, namespace)
