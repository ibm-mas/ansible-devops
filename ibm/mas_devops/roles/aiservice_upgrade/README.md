# aiservice_upgrade
This role validates if a given AI SERVICE installation is ready to be upgraded to a specific subscription channel, and (as long as dry run mode is not enabled) will execute the upgrade.

- It will validate that the current subscription channel is able to be upgraded to the target channel.
- It will upgrade the AI SERVICE to the desired channel (as long as dry run is not enabled).
- It will validate that the AI Service has been successfully reconciled at the upgraded version.
- It will **not** validate that all AI Service services successfully deploy after the reconcile (but we will be working on this limitation).

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`aiservice_instance_id`](#aiservice_instance_id) | Yes | None |
| [`aiservice_channel`](#aiservice_channel) | No | Auto-selected |
| [`aiservice_tenant_channel`](#aiservice_tenant_channel) | No | Value of `aiservice_channel` |
| [`aiservice_upgrade_dryrun`](#aiservice_upgrade_dryrun) | No | `false` |
| [`olm_approval_mode`](#olm_approval_mode) | No | `Automatic` |
| [`olm_approval_timeout`](#olm_approval_timeout) | No | `7200` |

### OLM Install Plan Approval

#### olm_approval_mode

- **Optional**
- Environment Variable: `OLM_APPROVAL_MODE`
- Default: `Automatic`

When set to `Manual`, the subscription channel update this role performs generates install plans that wait for human approval: the role pauses with instructions whenever an install plan is waiting for approval, and never approves it automatically. See [OLM Manual Install Plan Approvals](https://ibm-mas.github.io/ansible-devops/olm-manual-approvals/) for the full details.

#### olm_approval_timeout

- **Optional**
- Environment Variable: `OLM_APPROVAL_TIMEOUT`
- Default: `7200`

Seconds to wait for each individual install plan approval before the role fails (2 hours by default).

### Upgrade Target

#### aiservice_instance_id
AI Service instance identifier to upgrade — a valid AI Service instance ID (typically lowercase alphanumeric), matching the instance ID from the AI Service installation.

- **Required**
- Environment Variable: `AISERVICE_INSTANCE_ID`
- Default: None

The value is case-sensitive; verify the instance exists before upgrading. An incorrect instance ID will cause the upgrade to fail.

#### aiservice_channel
Target subscription channel for the AI Service upgrade — a valid AI Service subscription channel such as `9.0.x` or `9.1.x`.

- **Optional**
- Environment Variable: `AISERVICE_CHANNEL`
- Default: None (auto-selected based on the installed version)

When unset, the role automatically selects the next release; if already on the latest release, no action is taken. Set it explicitly when you need a specific target version — the role validates that a supported upgrade path exists from the current version, and no upgrade is performed if validation fails. Review the release notes before changing channels; channel changes may trigger operator restarts.

#### aiservice_tenant_channel
Subscription channel for the AI Service tenant operator — a valid AI Service subscription channel such as `9.0.x` or `9.1.x`.

- **Optional**
- Environment Variable: `AISERVICE_TENANT_CHANNEL`
- Default: Value of `aiservice_channel`

Overriding the tenant operator channel is only for development purposes; normally it should match the `aiservice_channel` value.

### Upgrade Validation

#### aiservice_upgrade_dryrun
Dry-run mode, which performs all validation checks for upgrade compatibility without making any changes to the AI Service installation — `true` or `false`.

- **Optional**
- Environment Variable: `AISERVICE_UPGRADE_DRYRUN`
- Default: `false`

When `false`, validation runs and the upgrade is executed if validation passes. Dry-run mode is highly recommended before production upgrades — it helps ensure upgrade feasibility and identify potential issues before committing to the operation.

## Example Playbook

### Automatic Target Selection
Running this playbook will upgrade AI Service to the next release. If you run this playbook when you are already on the latest release then it will take no action.

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    aiservice_instance_id: instance1
    aiservice_upgrade_dryrun: False
  roles:
    - ibm.mas_devops.aiservice_upgrade
```

### Explicit Upgrade Target
Running this playbook will attempt to upgrade AI Service to the specified release. If the specified release cannot be upgraded to from the installed version of AI Service then no action will be taken.

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    aiservice_instance_id: instance1
    aiservice_channel: 9.1.x
    aiservice_upgrade_dryrun: False
  roles:
    - ibm.mas_devops.aiservice_upgrade
```

## License

EPL-2.0
