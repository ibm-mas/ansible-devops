#!/usr/bin/env python3

"""
Shared OLM manual install plan approval support for the collection's action
plugins.

Thin ansible layer over the python-devops implementations (mas.devops.olm):
all policy and formatting live in the package -- the single-namespace and
cluster-wide convergence waits, the fail-fast on Subscriptions that can
never converge, the approval mode mismatch detection, the per-namespace
deadlines, the approve command and notice text. This module resolves task
arguments (the package owns the OLM_APPROVAL_MODE / OLM_APPROVAL_TIMEOUT
environment variable precedence) and owns the Display output: the
human-facing notices, heartbeats and full-scope reports, emitted from the
package's onPending callbacks.

The module NEVER approves anything on the user's behalf.

Two entry points: waitForSubscriptionApproval waits on a single namespace
(used by the roles that create/patch a subscription), and waitForClusterApproval
is the cluster-wide gate (used where subscriptions roll implicitly, e.g. after
a catalog digest update): it discloses the full scope of pending approvals up
front and waits on every namespace together, so the human may approve in any
order.

The approval info contract is the python-devops one (mas.devops.olm
getPendingInstallPlans):
    {installPlan, namespace, subscription, package, csvNames,
     currentCSV, targetCSV, created}
"""

from datetime import datetime, timezone

from mas.devops.olm import (
    DEFAULT_APPROVAL_TIMEOUT,
    VALID_APPROVAL_MODES,
    OLMTimeoutError,
    formatApproveCommands,
    formatInstallPlanApprovalNotice,
    formatUtcTimestamp,
    getNamespaceApprovalStatus,
    raiseIfApprovalModeMismatch,
    resolveApprovalMode,
    resolveApprovalTimeout,
    waitForClusterConvergence,
    waitForSubscriptionConvergence,
)

# How often (seconds) the "still waiting" status line is repeated while a
# wait is in progress -- the underlying poll is much faster than this
STATUS_INTERVAL = 300


def resolveTaskApprovalMode(taskArg=None):
    """
    Resolve the effective install plan approval mode for a task.

    Precedence: task argument > OLM_APPROVAL_MODE environment variable (the
    package's resolveApprovalMode) > None. None leaves the subscription's
    approval mode untouched, which is the collection's default behavior.

    Raises ValueError when a value is not "Automatic" or "Manual" (the task
    argument is named in the message; the environment variable is named by
    the package).
    """
    if taskArg is not None and taskArg not in VALID_APPROVAL_MODES:
        raise ValueError(f"install_plan_approval must be one of: {', '.join(VALID_APPROVAL_MODES)} (found '{taskArg}')")
    return resolveApprovalMode(explicit=taskArg)


def resolveTaskApprovalTimeout(taskArg=None):
    """
    Resolve the per-wait approval timeout in seconds.

    Precedence: task argument > OLM_APPROVAL_TIMEOUT environment variable (the
    package's resolveApprovalTimeout) > the package default (7200 seconds =
    2 hours).
    """
    if taskArg is not None:
        return int(taskArg)
    resolved = resolveApprovalTimeout()
    return DEFAULT_APPROVAL_TIMEOUT if resolved is None else resolved


def waitForSubscriptionApproval(dynClient, display, namespace, packageName=None, timeout=None, pollInterval=30, approvalMode=None):
    """
    Wait for every Subscription in a namespace to reach its channel head.

    Thin display layer over the package's waitForSubscriptionConvergence
    (which owns the wait, the deadline and the fail-fast on Subscriptions
    that cannot converge). This wrapper contributes:

    1. The approval mode mismatch check (the package's raiseIfApprovalModeMismatch):
       install plans pending in anything other than a Manual context (including
       unset) fail fast with the approve commands and the OLM_APPROVAL_MODE
       remedy, both at entry and for plans that appear mid-wait.
    2. The human-facing output under Manual approval: the pending
       InstallPlans are the notices (what is pending, what it will change,
       the oc command to approve it), displayed when first seen, with a
       status line ("Waiting for install plan approval since <x>, approval
       deadline <y>") repeating every STATUS_INTERVAL seconds so it is clear
       the wait has not died. Under Automatic approval an equivalent status
       line reports how many subscriptions are still rolling to their
       channel head.
    3. The Manual-context timeout re-raise: on expiry the approve commands
       are repeated in the error so the failure is actionable on its own.

    Mixed-mode namespaces (OLM auto-creates dependency subscriptions with
    default Automatic approval inside Manual namespaces) behave the same as
    Manual: reported, never fatal.

    packageName does not narrow the wait (and never did narrow the approval
    wait): it is echoed in the returned status as packageStatus so callers
    can confirm the Subscription they care about, while sibling
    subscriptions in the namespace are waited on equally.

    The returned status dict is the package's namespace convergence status
    with two added keys: waited (bool, True only when install plans were
    observed awaiting approval at some point, so callers can distinguish
    "approvals were granted" from "there was never anything to approve")
    and packageStatus (the per-Subscription status entry matching
    packageName, or None).

    Raises OLMTimeoutError when the timeout expires (with the approve
    commands repeated in the message under Manual) and OLMException on the
    approval mode mismatch and on Subscriptions that cannot converge. Both
    are translated by the action plugins.
    """
    status = getNamespaceApprovalStatus(dynClient, namespace)

    # Pending install plans in a non-Manual context (including unset, which
    # is an Automatic context) are a mode mismatch that must fail fast (with
    # instructions) rather than hang the calling role's readiness waits
    raiseIfApprovalModeMismatch(status["pendingApprovals"], approvalMode)

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
            for line in formatInstallPlanApprovalNotice(approval):
                display.display(line)

    waited = status["blocking"]
    startTime = datetime.now(timezone.utc)
    startTs = startTime.timestamp()
    deadlineTs = startTs + timeout if timeout is not None else None
    lastStatusLog = [None]

    def onPending(pendingStatus, pollCount):
        nonlocal waited
        waited = waited or pendingStatus["blocking"]

        # A plan appearing after the initial snapshot (a just-created
        # Subscription's first plan, or a channel change's new plan): the
        # same mismatch as above, caught late
        raiseIfApprovalModeMismatch(pendingStatus["pendingApprovals"], approvalMode)

        if manualContext:
            for approval in pendingStatus["pendingApprovals"]:
                if approval["installPlan"] not in seenPlanNames:
                    seenPlanNames.add(approval["installPlan"])
                    for line in formatInstallPlanApprovalNotice(approval):
                        display.display(line)

        now = datetime.now(timezone.utc).timestamp()
        if lastStatusLog[0] is None or now - lastStatusLog[0] >= STATUS_INTERVAL:
            lastStatusLog[0] = now
            if manualContext:
                if deadlineTs is not None:
                    display.display(
                        f"Waiting for install plan approval since {formatUtcTimestamp(startTs)}, " f"approval deadline {formatUtcTimestamp(deadlineTs)}"
                    )
                else:
                    display.display(f"Waiting for install plan approval since {formatUtcTimestamp(startTs)} (no timeout)")
            else:
                unconverged = [entry["name"] for entry in pendingStatus["subscriptions"] if entry["converged"] is False]
                if deadlineTs is not None:
                    display.display(
                        f"Waiting for {len(unconverged)} subscription(s) in {namespace} to reach their channel head "
                        f"({', '.join(unconverged)}), approval deadline {formatUtcTimestamp(deadlineTs)}"
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
            raise OLMTimeoutError(
                f"Timed out after {timeout}s waiting for manual install plan approval in namespace {namespace}. "
                f"To grant approval run:\n{formatApproveCommands(current['pendingApprovals'])}"
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


def waitForClusterApproval(dynClient, display, timeout=None, pollInterval=30, approvalMode=None):
    """
    Wait for install plan approvals and subscription convergence cluster-wide.

    Thin display layer over the package's waitForClusterConvergence (which
    owns the settle, the discovery, the late-entrant scope, the per-namespace
    deadlines, the mismatch policy and the fail-fast). This wrapper
    contributes the human-facing output under Manual approval:

    - The full-scope report, up front: every pending install plan across
      every namespace, with its oc command, so the human can plan an
      approval order (controlling the order of rollouts is one of the main
      reasons to run Manual approval).
    - Notices for plans that appear mid-wait (e.g. the second step of a
      multi-step upgrade path), each exactly once.
    - A first-seen Mixed-mode namespace report (never fatal).
    - A heartbeat line naming every outstanding namespace (with its plan
      count and deadline), repeating every STATUS_INTERVAL seconds so the
      full scope stays visible for the whole wait.

    Returns the package's result unchanged: waited (bool, True only when
    install plans were observed awaiting approval at some point),
    namespaces (sorted list of every namespace that was ever in scope) and
    statuses (namespace -> final convergence status).

    Raises OLMTimeoutError when a namespace's deadline expires, OLMException
    on the approval mode mismatch and on Subscriptions that cannot converge.
    Both are translated by the action plugins.
    """
    manualContext = approvalMode == "Manual"
    seenPlanNames = set()
    mixedNotified = set()
    lastStatusLog = [None]
    startTime = datetime.now(timezone.utc)
    startTs = startTime.timestamp()

    def onPending(clusterStatus, pollCount):
        if not manualContext:
            # Unreachable today: the package raises the mismatch itself
            # before the first callback; the guard keeps the invariant
            # explicit
            raiseIfApprovalModeMismatch(clusterStatus["pendingApprovals"], approvalMode)
            return True

        pending = clusterStatus["pendingApprovals"]

        # Poll 1 (fired by the package before any convergence snapshot) is
        # the full-scope report; later polls only notice plans that are new
        # since the last poll
        if pollCount == 1:
            namespaces = sorted({approval["namespace"] for approval in pending})
            display.display(f"{len(pending)} install plan(s) awaiting manual approval across {len(namespaces)} namespace(s) -- approve them in any order:")
            for approval in pending:
                seenPlanNames.add((approval["namespace"], approval["installPlan"]))
                for line in formatInstallPlanApprovalNotice(approval):
                    display.display(line)
        else:
            for approval in pending:
                key = (approval["namespace"], approval["installPlan"])
                if key not in seenPlanNames:
                    seenPlanNames.add(key)
                    for line in formatInstallPlanApprovalNotice(approval):
                        display.display(line)

        # A first-seen Mixed namespace is reported, never fatal
        for namespace, status in clusterStatus["statuses"].items():
            if status["approvalMode"] == "Mixed" and namespace not in mixedNotified:
                mixedNotified.add(namespace)
                display.display(
                    f"Namespace {namespace} contains a mix of approval modes (OLM auto-creates dependency "
                    "subscriptions with default Automatic approval); treating the namespace as Manual"
                )

        # Heartbeat (snapshot polls only, not the report poll): name every
        # outstanding namespace so the full scope stays visible for the
        # whole wait
        if pollCount > 1:
            now = datetime.now(timezone.utc).timestamp()
            if lastStatusLog[0] is None or now - lastStatusLog[0] >= STATUS_INTERVAL:
                lastStatusLog[0] = now
                summary = ", ".join(
                    f"{namespace} ({len(clusterStatus['statuses'][namespace]['pendingApprovals'])} plans, "
                    f"deadline {formatUtcTimestamp(deadline) if deadline is not None else 'none'})"
                    for namespace, deadline in clusterStatus["deadlines"].items()
                    if namespace in clusterStatus["outstanding"]
                )
                display.display(f"Waiting for install plan approval since {formatUtcTimestamp(startTs)} -- outstanding: {summary}")

        return True

    return waitForClusterConvergence(dynClient, timeout=timeout, pollInterval=pollInterval, approvalMode=approvalMode, onPending=onPending)
