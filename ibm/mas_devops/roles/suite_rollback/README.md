# suite_rollback

This role rolls back Maximo Application Suite core platform to an earlier version. Rollback capability is available in MAS 8.11 and later versions. Each MAS version includes a list of supported rollback target versions. For example, you can roll back from MAS 8.11.x to 8.11.0.

!!! warning
    Rollback is a significant operation that should be carefully planned and tested. Always perform a dry run first and ensure you have backups before proceeding with actual rollback.

## What This Role Does

- Validates the specified target version is compatible for rollback from the current version
- Verifies the core platform is not already at the target version
- Executes the rollback to the desired version (unless dry run mode is enabled)
- Validates the core platform successfully reconciles at the rolled back version
- **Note**: Does not validate that all core services successfully deploy after reconcile (future enhancement)

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`mas_instance_id`](#mas_instance_id) | Yes | None |
| [`mas_core_version`](#mas_core_version) | Conditional | None |
| [`rollback_mas_core`](#rollback_mas_core) | No | `true` |
| [`verify_core_version`](#verify_core_version) | No | `false` |
| [`mas_rollback_dryrun`](#mas_rollback_dryrun) | No | `false` |
| [`skip_compatibility_check`](#skip_compatibility_check) | No | `false` |

`mas_core_version` is only required when `rollback_mas_core` or `verify_core_version` is `true`.

### Instance and Version

#### mas_instance_id

MAS instance identifier to rollback — a lowercase alphanumeric string, 3-12 characters (e.g., `prod`, `dev`, `masinst1`), matching the instance ID from MAS installation.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

All validation and rollback operations target this instance. Ensure the instance is in a stable state before initiating rollback, and that applications are stopped or in maintenance mode during rollback.

#### mas_core_version

Target MAS core version for rollback or verification — a valid MAS version string (e.g., `8.11.0`, `8.11.1`, `8.12.0`) that must be listed in the current version's supported rollback targets.

- **Required** when `rollback_mas_core=true` or `verify_core_version=true`
- Environment Variable: `MAS_CORE_VERSION`
- Default: None

The role validates this version is compatible before proceeding. Check the MAS documentation for supported rollback paths from your current version — not all versions support rollback to all earlier versions.

### Rollback Behavior

#### rollback_mas_core

Controls whether the role performs the rollback or only validates/verifies version information — `true` to execute the rollback to the specified version (default), `false` to skip rollback execution.

- **Optional**
- Environment Variable: `ROLLBACK_MAS_CORE`
- Default: `true`

When `false`, typically used with `verify_core_version=true` to check the current version without making changes; combine with `mas_rollback_dryrun=true` for validation without changes.

#### verify_core_version

Version verification mode — `true` to verify that the current MAS core version matches `mas_core_version` (failing on mismatch), `false` to skip verification (default). No rollback operations are performed.

- **Optional**
- Environment Variable: `VERIFY_CORE_VERSION`
- Default: `false`

Useful for post-rollback validation to confirm a successful version change, or for validation in automation pipelines; typically used with `rollback_mas_core=false`.

#### mas_rollback_dryrun

Dry run mode (validation only) — `true` to perform all rollback compatibility validation checks without making any changes, `false` to execute the actual rollback after validation (default).

- **Optional**
- Environment Variable: `MAS_ROLLBACK_DRYRUN`
- Default: `false`

!!! tip
    Best practice: always run with `mas_rollback_dryrun=true` first to validate the rollback is possible, then execute the actual rollback with `mas_rollback_dryrun=false`. Rollback must be enabled (`rollback_mas_core=true`) for a dry run to be meaningful.

#### skip_compatibility_check

Skip the version compatibility validation that confirms the target version is in the list of supported rollback versions — `true` to skip, `false` to enforce the check (default).

- **Optional**
- Environment Variable: `SKIP_COMPATIBILITY_CHECK`
- Default: `false`

Intended for development and testing scenarios only, allowing rollback between pre-built versions on the same base (e.g., `8.11.0-pre.dev` to `8.11.0-pre.stable`).

!!! warning
    Development purposes only — never use in production. Skipping compatibility checks can result in failed rollbacks, data corruption, or unstable installations; the check exists to prevent unsupported rollback scenarios.

## Example Playbook

### Rollback to Specified Version

Running this playbook will rollback MAS core to the specified version. If you run this playbook when you are already on the same version it will take no action.

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: instance1
    mas_core_version: 8.11.0
    mas_rollback_dryrun: False
  roles:
    - ibm.mas_devops.suite_rollback
```

### Verify MAS Core Version

Running this playbook will attempt to verify the current version of MAS core matches with the specified version.

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: instance1
    mas_core_version: 8.11.0
    mas_rollback_dryrun: False
    rollback_mas_core: False
    verify_core_version: True
  roles:
    - ibm.mas_devops.suite_rollback
```

## License

EPL-2.0
