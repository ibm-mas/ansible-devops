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
  differs from the effective one, the task **fails fast** with an error naming the
  subscription, both modes, and the remedy — instead of slow-failing later in the
  operator readiness waits. This includes the default: re-applying a `Manual`
  subscription with no mode set (Automatic) fails immediately.
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

## Support matrix

- **All roles using the `apply_subscription` module** (suite_install,
  suite_app_install, sls, db2, cert_manager, grafana, cp4d_service, aiservice,
  arcgis, servicemesh, ...): full support — subscriptions are created with the
  effective approval mode and every wait in the flow handles pending approvals.
- **Template-based dependency roles** (cp4d, dro, eck, kafka, nvidia_gpu,
  ocp_efs, ocs, turbonomic): subscriptions are rendered with the effective
  approval mode and each role waits for approvals before waiting for the
  operator to be ready.
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
