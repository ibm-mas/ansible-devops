# suite_app_rollback

Roll back Maximo Application Suite applications to earlier versions when issues are encountered after upgrades. This role provides a safe rollback mechanism with built-in compatibility validation to ensure the target version is supported for rollback from the current version and compatible with the running MAS core platform.

**Important**: Currently designed for Manage application only. Rollback capability is available in MAS 8.7 and later versions. Each version defines a set of supported rollback targets (e.g., from 8.7.x to 8.7.0).

The role performs comprehensive validation before rollback and monitors the reconciliation process to ensure successful completion at the target version.

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`mas_instance_id`](#mas_instance_id) | Yes | None |
| [`mas_app_id`](#mas_app_id) | Yes | None |
| [`mas_app_version`](#mas_app_version) | Conditional | None |
| [`rollback_mas_app`](#rollback_mas_app) | No | `true` |
| [`verify_app_version`](#verify_app_version) | No | `false` |
| [`mas_rollback_dryrun`](#mas_rollback_dryrun) | No | `false` |
| [`skip_compatibility_check`](#skip_compatibility_check) | No | `false` |

`mas_app_version` is only required when `rollback_mas_app` or `verify_app_version` is `true`.

### Instance and Application

#### mas_instance_id

MAS instance identifier where the application rollback will be performed — typically 3-12 lowercase alphanumeric characters matching an existing MAS instance with the application installed.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

The rollback operation targets the application in the `mas-<instance-id>-<app-id>` namespace; the value is case-sensitive and must match the instance ID used during MAS installation.

#### mas_app_id

MAS application identifier to roll back. Currently only `manage` (Maximo Manage) is supported; future versions may support additional applications.

- **Required**
- Environment Variable: `MAS_APP_ID`
- Default: None

Determines which application namespace and resources are targeted for rollback. The application must be installed and running before rollback, and rollback capability requires MAS 8.7 or later.

#### mas_app_version

Target version to roll back to — for example `8.7.0`, `8.7.1`, or `8.8.0`.

- **Required** when `rollback_mas_app` or `verify_app_version` is `true`
- Environment Variable: `MAS_APP_VERSION`
- Default: None

The version must be a supported rollback target from the current version (each MAS version defines its own set), compatible with the running MAS core platform version, and available in the configured catalog source. Built-in validation prevents unsupported rollback paths — in most cases you cannot roll back across major version boundaries. Consider database schema compatibility when rolling back, and verify rollback compatibility in IBM documentation before proceeding.

!!! warning
    Always back up your data before performing rollback operations.

### Rollback Behavior

#### rollback_mas_app

Controls whether the role performs the actual rollback or only validation checks — `true` to perform the rollback (default), `false` for validation only with no changes made.

- **Optional**
- Environment Variable: `ROLLBACK_MAS_APP`
- Default: `true`

Set to `false` for a dry-run check of rollback feasibility before execution; validation includes compatibility checks and version availability. Combine with `verify_app_version` for post-rollback verification.

#### verify_app_version

Verify that the current application version matches the specified target version — `true` to check, `false` to skip (default). No changes are made to the application.

- **Optional**
- Environment Variable: `VERIFY_APP_VERSION`
- Default: `false`

Useful for post-rollback verification in automation pipelines, and can be used independently of the rollback operation: set `rollback_mas_app=false` and `verify_app_version=true` for verification-only mode.

#### mas_rollback_dryrun

Dry-run mode for rollback operations — `true` to run all validation checks without executing the rollback, `false` for normal operation (default).

- **Optional**
- Environment Variable: `MAS_ROLLBACK_DRYRUN`
- Default: `false`

Recommended before an actual rollback: all compatibility checks and validations are performed and any errors reported, with no changes made to the application or cluster.

#### skip_compatibility_check

Bypass the built-in compatibility validation between the target rollback version and the current MAS core platform version — `true` to skip the checks, `false` to perform them (default, recommended).

- **Optional**
- Environment Variable: `SKIP_COMPATIBILITY_CHECK`
- Default: `false`

!!! warning
    Skipping compatibility checks can allow unsupported rollback operations that may cause system instability, application failures, or data corruption. Only use this when you have verified compatibility through other means or are following IBM support guidance.

## Example Playbook

### Automatic Target Selection

Running this playbook will rollback Manage Application to the 8.7.1 version. If you run this playbook when you are already on the same version it will take no action.

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: instance1
    mas_app_id: manage
    mas_app_version: 8.7.1
  roles:
    - ibm.mas_devops.suite_app_rollback
```

### Verify Manage App Version

Running this playbook will attempt to verify the current version of Manage Application matches with the specified version.

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: instance1
    mas_app_id: manage
    mas_app_version: 8.7.1
    rollback_mas_app: False
    verify_app_version: True
  roles:
    - ibm.mas_devops.suite_app_rollback
```

## License

EPL-2.0
