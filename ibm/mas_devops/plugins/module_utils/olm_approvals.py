#!/usr/bin/env python3

"""
Shared OLM manual install plan approval support for the collection's action
plugins.

Manual approval mode (OLM_APPROVAL_MODE=Manual) means a human approves every
InstallPlan: this module NEVER approves on the user's behalf -- it formats the
human-facing notices (what is pending, what it will change, how to approve it)
and waits for the approval to be given out-of-band, with a per-wait timeout.

Two entry points: waitForSubscriptionApproval waits on a single namespace
(used by the roles that create/patch a subscription), and waitForClusterApproval
is the cluster-wide gate (used where subscriptions roll implicitly, e.g. after
a catalog digest update): it discloses the full scope of pending approvals up
front and waits on every namespace together, so the human may approve in any
order.

The approval info contract is the python-devops one (mas.devops.olm):
    {installPlan, namespace, subscription, package, csvNames,
     currentCSV, targetCSV, created}
"""

import json
import os
import time
from datetime import datetime, timezone

from mas.devops.olm import (
    OLMException,
    OLMTimeoutError,
    getNamespaceApprovalStatus,
    getNamespaceConvergenceStatus,
    getPendingInstallPlans,
    waitForSubscriptionConvergence,
    waitForSubscriptionResolution,
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


def waitForClusterApproval(dynClient, display, timeout=None, pollInterval=30, approvalMode=None):
    """
    Wait for install plan approvals and subscription convergence cluster-wide.

    This is the gate for subscriptions that roll implicitly, e.g. after a
    catalog digest update in ``mas update``: every MAS installation's
    namespaces (and the shared namespaces) get new install plans at once, so
    the full scope is disclosed **up front** -- every pending install plan
    across every namespace, with its oc command -- and the human may approve
    in any order. Controlling the order of rollouts is one of the main
    reasons to run Manual approval, so the wait must not hide the scope
    behind serial per-namespace blocking.

    The flow:

    1. Settle Subscription statuses cluster-wide (``waitForSubscriptionResolution``)
       -- right after a catalog digest update OLM may not have generated the
       new install plans yet, and a single snapshot cannot distinguish "not
       generated yet" from "none coming".
    2. Discover namespaces with install plans awaiting approval
       (``getPendingInstallPlans``, pending-plan-based by design: unrelated
       converged subscriptions in shared namespaces must not enter the scope).
       Nothing pending -> no-op success.
    3. Under a non-Manual context (including unset) any pending plan is an
       approval mode mismatch: fail fast listing the approve commands from
       ALL namespaces at once, with the OLM_APPROVAL_MODE=Manual remedy.
       Under Manual, print the full-scope report and enter the unified wait.
    4. Unified multi-namespace poll loop: each poll re-runs pending-plan
       discovery (a namespace with a newly-pending plan joins the scope and
       gets its deadline assigned then -- the second step of a multi-step
       upgrade path lands here) and snapshots every in-scope namespace
       (``getNamespaceConvergenceStatus``). New plans get their notices when
       first seen; a heartbeat line naming every outstanding namespace
       repeats every STATUS_INTERVAL seconds. A namespace leaves the scope
       only when it has converged -- never merely because pending-plan
       discovery no longer lists it (an approved plan can still be rolling
       out).
    5. Fail-fast (both modes) on subscriptions that cannot converge:
       ResolutionFailed conditions and Failed install plans raise immediately
       rather than burning the deadline.

    Each namespace carries its own timeout budget, with the clock starting
    when the namespace is first observed (gate start for the initially
    discovered namespaces, first observation for late entrants): a namespace
    the human approves last does not get a fresh full budget after the gate
    spent hours on earlier ones. On expiry the error lists every
    still-outstanding namespace, each with its non-converged subscriptions
    (installedCSV -> targetCSV) and the repeated approve commands.

    Returns a dict with:

    - ``waited`` (bool): True only when install plans were observed awaiting
      approval at some point, so callers can distinguish "approvals were
      granted" from "there was never anything to approve"
    - ``namespaces`` (list): every namespace that was ever in scope, sorted
    - ``statuses`` (dict): namespace -> final convergence status

    Raises OLMTimeoutError when a namespace's deadline expires, ValueError on
    the Automatic mismatch (from the initial discovery and for plans that
    appear mid-wait), and OLMException on subscriptions that cannot converge.
    """
    # 1. Settle: discovery below must not race OLM's re-resolution after a
    # catalog digest update
    waitForSubscriptionResolution(dynClient, namespace=None)

    # 2. Discovery: pending-plan-based, never convergence-based
    pending = getPendingInstallPlans(dynClient, namespace=None)
    if len(pending) == 0:
        return {"waited": False, "namespaces": [], "statuses": {}}

    manualContext = approvalMode == "Manual"

    # 3. Approval mode mismatch: pending install plans in a non-Manual
    # context fail fast with the approve commands from every namespace
    if not manualContext:
        commands = "\n".join(f"  {approveCommand(approval)}" for approval in pending)
        namespaces = sorted({approval["namespace"] for approval in pending})
        raise ValueError(
            f"Install plans are waiting for manual approval in {len(namespaces)} namespace(s) ({', '.join(namespaces)}), but the effective "
            f"approval mode is '{approvalMode or 'Automatic'}'. Either grant approval:\n{commands}\n"
            "or set OLM_APPROVAL_MODE=Manual so that the automation waits for the approvals instead"
        )

    # 4. The full-scope report: every pending install plan across every
    # namespace, up front, so the human can plan an approval order
    namespaces = sorted({approval["namespace"] for approval in pending})
    display.display(f"{len(pending)} install plan(s) awaiting manual approval across {len(namespaces)} namespace(s) -- approve them in any order:")
    for namespace in namespaces:
        for approval in pending:
            if approval["namespace"] == namespace:
                for line in formatApprovalNotice(approval):
                    display.display(line)

    waited = True
    seenPlanNames = {(approval["namespace"], approval["installPlan"]) for approval in pending}

    # Per-namespace deadline bookkeeping: the clock starts when the namespace
    # is first observed (gate start for these, first observation for late
    # entrants). None means no timeout. firstSeen is never cleared -- a
    # namespace that converges and later regresses (a new plan appears) keeps
    # its original deadline -- while scope is the live set of namespaces still
    # being waited on.
    firstSeen = {}
    scope = set()

    def enterScope(namespace):
        if namespace not in firstSeen:
            firstSeen[namespace] = datetime.now(timezone.utc).timestamp() + timeout if timeout is not None else None
        scope.add(namespace)

    for namespace in namespaces:
        enterScope(namespace)

    statuses = {}
    mixedNotified = set()
    lastStatusLog = [None]
    startTime = datetime.now(timezone.utc)
    startTs = startTime.timestamp()

    def observePending(currentPending):
        """Late mismatch check, new-plan notices, and scope entry for one poll's discovery result."""
        nonlocal waited
        if len(currentPending) > 0:
            waited = True
            if not manualContext:
                # A plan appearing after the initial snapshot in a non-Manual
                # context is the same mismatch as step 3, caught late
                # (unreachable today: the loop only runs under Manual, but
                # the guard keeps the invariant explicit)
                commands = "\n".join(f"  {approveCommand(approval)}" for approval in currentPending)
                raise ValueError(
                    f"Install plans are waiting for manual approval, but the effective approval mode is "
                    f"'{approvalMode or 'Automatic'}'. Either grant approval:\n{commands}\n"
                    "or set OLM_APPROVAL_MODE=Manual so that the automation waits for the approvals instead"
                )
            for approval in currentPending:
                enterScope(approval["namespace"])
                key = (approval["namespace"], approval["installPlan"])
                if key not in seenPlanNames:
                    seenPlanNames.add(key)
                    for line in formatApprovalNotice(approval):
                        display.display(line)

    while True:
        # Re-discovery: namespaces with newly-pending plans join the scope
        # (e.g. the second step of a multi-step upgrade path)
        observePending(getPendingInstallPlans(dynClient, namespace=None))

        # Snapshot every in-scope namespace and fail fast on subscriptions
        # that cannot converge. A converged namespace leaves the live scope
        # (it is never removed merely because pending-plan discovery no
        # longer lists it -- an approved plan can still be rolling out).
        outstanding = []
        for namespace in sorted(scope):
            status = getNamespaceConvergenceStatus(dynClient, namespace)
            statuses[namespace] = status

            if status["approvalMode"] == "Mixed" and namespace not in mixedNotified:
                mixedNotified.add(namespace)
                display.display(
                    f"Namespace {namespace} contains a mix of approval modes (OLM auto-creates dependency "
                    "subscriptions with default Automatic approval); treating the namespace as Manual"
                )

            for entry in status["subscriptions"]:
                if entry.get("resolutionError"):
                    raise OLMException(
                        f"Subscription {entry['name']} in namespace {namespace} failed to resolve: {entry['resolutionError']} "
                        f"(check 'oc get subscription -n {namespace}' and the health of the catalog sources)"
                    )
            if status["failedInstallPlans"]:
                raise OLMException(
                    f"Install plan(s) {', '.join(status['failedInstallPlans'])} referenced by subscription(s) in namespace {namespace} "
                    f"have Failed: check 'oc get installplan -n {namespace}' for details"
                )

            if status["converged"]:
                scope.discard(namespace)
            else:
                outstanding.append(namespace)

        if len(outstanding) == 0:
            return {"waited": waited, "namespaces": sorted(firstSeen), "statuses": statuses}

        # Heartbeat: name every outstanding namespace so the full scope stays
        # visible for the whole wait
        now = datetime.now(timezone.utc).timestamp()
        if lastStatusLog[0] is None or now - lastStatusLog[0] >= STATUS_INTERVAL:
            lastStatusLog[0] = now
            summary = ", ".join(
                f"{namespace} ({len(statuses[namespace]['pendingApprovals'])} plans, "
                f"deadline {_formatTimestamp(firstSeen[namespace]) if firstSeen[namespace] is not None else 'none'})"
                for namespace in outstanding
            )
            display.display(f"Waiting for install plan approval since {_formatTimestamp(startTs)} -- outstanding: {summary}")

        # Deadline expiry: name every still-outstanding namespace, each with
        # its non-converged subscriptions and the repeated approve commands
        for namespace in outstanding:
            if firstSeen[namespace] is not None and now >= firstSeen[namespace]:
                current = getPendingInstallPlans(dynClient, namespace=namespace)
                commands = "\n".join(f"  {approveCommand(approval)}" for approval in current)
                deadline = _formatTimestamp(firstSeen[namespace])
                lines = [f"Timed out waiting for install plan approval in namespace {namespace} (deadline {deadline}). Still outstanding:"]
                for entry in statuses[namespace]["subscriptions"]:
                    if entry["converged"] is False:
                        lines.append(f"  {entry['name']}: {entry['installedCSV'] or '(not installed)'} -> {entry['targetCSV']} (state: {entry['state']})")
                    elif entry["skipped"]:
                        lines.append(f"  {entry['name']}: skipped ({entry['skipReason']})")
                if commands:
                    lines.append(f"To grant approval run:\n{commands}")
                raise OLMTimeoutError("\n".join(lines))

        time.sleep(pollInterval)
