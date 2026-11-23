# OLM Manual Install Plan Approvals

By default, all subscriptions the collection creates use `Automatic` install
plan approval: OLM approves and applies every install plan as soon as it is
generated. With **manual approval mode** every install plan waits in
`RequiresApproval` until a human approves it — this is the deliberate choice to
review (and gate) every operator install and update before it is applied to the
cluster.

Manual approval mode is controlled with two environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `OLM_APPROVAL_MODE` | `Automatic` | `Automatic` (no behavior change) or `Manual` |
| `OLM_APPROVAL_TIMEOUT` | `7200` | Seconds to wait for each approval before failing (2 hours) |

!!! note
    These variables are read directly by the `apply_subscription` and
    `wait_for_subscription_approval` modules (task arguments override the
    environment, the environment overrides the default) and, for the
    template-based dependency roles, via the `olm_approval_mode` /
    `olm_approval_timeout` role variables. This is a deliberate deviation from
    the collection's usual per-role environment variable convention: approval
    mode applies globally to everything the collection does with subscriptions.

## What it looks like

When a subscription's progress is gated on an approval, the role logs what is
pending, what the install plan is going to change, and how to approve it:

```
Waiting for manual approval of install plan install-abcde in namespace mas-inst1-core
Install plan contents: ibm-mas (subscription ibm-mas): ibm-mas.v9.0.0 -> ibm-mas.v9.1.0
  CSVs to install: ibm-mas.v9.1.0 (plan created 2026-11-15T10:00:00Z)
To grant approval run "oc patch installplan/install-abcde -n mas-inst1-core --type merge -p '{"spec":{"approved":true}}'" or use the OpenShift Console

Waiting for install plan approval since 2026-11-20 14:02:11 UTC, approval deadline 2026-11-20 16:02:11 UTC
Waiting for install plan approval since 2026-11-20 14:07:11 UTC, approval deadline 2026-11-20 16:02:11 UTC
...
```

The status line repeats every 5 minutes (so it is clear the wait has not died)
until either the approval is granted — the role then waits for the install plan
to complete and the operator to finish installing before resuming — or
`OLM_APPROVAL_TIMEOUT` expires, in which case the task fails with the approve
commands repeated in the error message so the failure is actionable on its own.
Each approval wait gets its own timeout budget.

## The collection never approves on your behalf

The entire point of manual approvals is that a human reviews and approves them.
The collection will display what is pending and how to approve it, and it will
wait — it will **never** approve an install plan automatically. Approve with
the `oc patch` command shown in the messages, or via the OpenShift Console
(Installed Operators → the operator → Subscription → Approval required).

## Approval mode mismatches

The effective approval mode (task argument > `OLM_APPROVAL_MODE` > `Automatic`) is a
contract with the cluster, and it is always a concrete value:

- When the collection is asked to manage a subscription whose existing approval mode
  differs from the effective one, the mismatch check is **asymmetric**
  (owner-confirmed semantics):
  - An explicit `install_plan_approval` task argument is imposing: it fails fast on
    conflict in either direction, with an error naming the subscription, both modes,
    and the remedy.
  - A resolved `Automatic` mode (including the default, when no mode is set) over an
    existing `Manual` subscription **fails fast**: the automation never turns off
    human gating. Re-applying a `Manual` subscription with no mode set fails
    immediately with the `OLM_APPROVAL_MODE=Manual` remedy, instead of slow-failing
    later in the operator readiness waits.
  - A resolved `Manual` mode over an existing `Automatic` subscription **warns and
    preserves** the subscription's `Automatic` mode — it keeps rolling freely. This
    is what keeps mixed-approval clusters updatable: `mas update` / `mas upgrade`
    pass `Manual` for their whole scope while some of the subscriptions they
    re-apply are `Automatic`.
- When install plans are pending in a namespace the collection is verifying as
  Automatic (including with no mode set), `ocp_verify` fails fast with the approve
  commands and the `OLM_APPROVAL_MODE=Manual` remedy — under Manual mode it waits
  for the approvals instead.

Real namespaces can legitimately contain a **mix** of modes: OLM automatically
creates dependency subscriptions (for example `ibm-truststore-mgr` alongside
`ibm-sls`) with default `Automatic` approval inside `Manual` namespaces. Mixed
namespaces are reported (not treated as an error) and behave the same as
`Manual` for waiting semantics: install plans waiting for approval gate
processing regardless of which subscription generated them.

## Timeout semantics

`OLM_APPROVAL_TIMEOUT` budgets **each individual approval wait** (per
namespace / per subscription stage), not the whole run: a long installation
with several sequential approval gates can take longer in total. Set it to a
value that reflects how quickly a human is expected to respond.

## Install plan generation

The approval gate has to distinguish "no InstallPlan is pending **yet**" from
"no InstallPlan is **coming**" — a distinction a single namespace snapshot
cannot make in the moments after a Subscription is created (OLM takes a few
seconds to generate the first InstallPlan) or patched (the old InstallPlan is
replaced, not removed, only when the new one is generated). In Manual and
Mixed namespaces the gate closes this race before deciding that nothing is
pending:

- **Fresh Subscriptions** (no `status.installPlanRef`): the gate blocks until
  OLM generates their InstallPlans — normally seconds. If OLM has not
  resolved them after 10 minutes the gate fails naming the Subscriptions,
  with pointers at the Subscription status conditions and catalog health.
  When every Subscription in the namespace was fresh, this is all that is
  needed: the ref appearing is itself the resolution event.
- **Pre-existing Subscriptions** (an `installPlanRef` was already present —
  untouched, or patched moments ago; indistinguishable at the gate): the gate
  settles on **status stability** instead, waiting until the Subscriptions'
  resolution fields (state, installPlanRef, installedCSV,
  installPlanGeneration, currentCSV) have been unchanged for a few
  consecutive polls (~1 minute). An update that is coming churns these fields
  within seconds; no update leaves them quiet.

The cluster-wide gate (no `namespace`) uses the same settle poll before
discovering pending InstallPlans, so that right after a catalog digest update
it does not race OLM's re-resolution of every Subscription.

These waits are deliberately **not configurable**: they are failure ceilings
for unhealthy clusters (a stuck OLM fails loudly after 10 minutes instead of
silently hanging the calling role's readiness waits), not delays paid by
healthy runs — a fresh install pays seconds, and an update with nothing to
approve pays about a minute.

## Support matrix

- **All roles using the `apply_subscription` module** (suite_install,
  suite_app_install, sls, db2, cert_manager, grafana, cp4d_service, aiservice,
  arcgis, servicemesh, ...): full support — subscriptions are created with the
  effective approval mode and every wait in the flow handles pending approvals.
- **Template-based dependency roles** (cp4d, dro, eck, kafka, nvidia_gpu,
  ocp_efs, ocs, turbonomic): subscriptions are rendered with the effective
  approval mode and each role waits for approvals before waiting for the
  operator to be ready — including waiting for OLM to generate the install
  plans of just-created subscriptions (see [Install plan generation](#install-plan-generation)).
- **Update and upgrade flows**: channel changes under manual approval generate
  pending install plans that are waited on before the flow continues.
- **mongodb** is not OLM-based and is unaffected.

## Standalone wait

Roles that create subscriptions outside the collection's modules, or any
automation that needs to gate on pending approvals, can use the module
directly:

```yaml
- name: Wait for install plan approval
  ibm.mas_devops.wait_for_subscription_approval:
    namespace: mas-inst1-core
    package_name: ibm-mas   # optional: also waits for the operator to settle
    timeout: 7200           # optional: defaults to OLM_APPROVAL_TIMEOUT
```

With no `namespace`, the module discovers every namespace in the cluster with
install plans awaiting approval and waits for each in turn — this is the gate
used after a catalog digest update, where every subscription rolls implicitly.
