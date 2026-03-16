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

### mas_instance_id
MAS instance identifier to rollback.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

**Purpose**: Identifies which MAS instance to rollback. The role validates and executes rollback operations on this specific instance.

**When to use**:
- Always required for rollback operations
- Must match the instance ID from MAS installation
- Used to target specific instance for version rollback

**Valid values**: Lowercase alphanumeric string, 3-12 characters (e.g., `prod`, `dev`, `masinst1`)

**Impact**: Determines which MAS instance undergoes rollback. All validation and rollback operations target this instance.

**Related variables**:
- `mas_core_version`: Target version to rollback to
- `rollback_mas_core`: Controls whether rollback is executed

**Note**: Ensure the instance is in a stable state before initiating rollback. Applications should be stopped or in maintenance mode during rollback.

### mas_core_version
Target MAS core version for rollback or verification.

- **Required** (when `rollback_mas_core=true` or `verify_core_version=true`)
- Environment Variable: `MAS_CORE_VERSION`
- Default: None

**Purpose**: Specifies the MAS core version to rollback to or to verify against the current version. Must be a supported rollback target for the current version.

**When to use**:
- Required when performing rollback (`rollback_mas_core=true`)
- Required when verifying version (`verify_core_version=true`)
- Must be a version listed in the current version's supported rollback targets

**Valid values**: Valid MAS version string (e.g., `8.11.0`, `8.11.1`, `8.12.0`)

**Impact**: Determines the target version for rollback operations. The role validates this version is compatible before proceeding.

**Related variables**:
- `mas_instance_id`: Instance to rollback
- `rollback_mas_core`: Enables rollback execution
- `skip_compatibility_check`: Bypasses version compatibility validation

**Note**: Check the MAS documentation for supported rollback paths from your current version. Not all versions support rollback to all earlier versions.

### rollback_mas_core
Enable rollback execution.

- **Optional**
- Environment Variable: `ROLLBACK_MAS_CORE`
- Default: `true`

**Purpose**: Controls whether the role actually performs the rollback operation or only validates/verifies version information.

**When to use**:
- Leave as `true` (default) to execute rollback
- Set to `false` when only verifying current version
- Use with `mas_rollback_dryrun=true` for validation without changes

**Valid values**: `true`, `false`

**Impact**:
- `true`: Executes rollback to the specified version (default behavior)
- `false`: Skips rollback execution (use with `verify_core_version=true` for version checks)

**Related variables**:
- `mas_core_version`: Target version for rollback
- `verify_core_version`: Alternative mode for version verification
- `mas_rollback_dryrun`: Validation-only mode

**Note**: When `false`, typically used with `verify_core_version=true` to check current version without making changes.

### verify_core_version
Enable version verification mode.

- **Optional**
- Environment Variable: `VERIFY_CORE_VERSION`
- Default: `false`

**Purpose**: When enabled, verifies that the current MAS core version matches the specified `mas_core_version` without performing any rollback operations.

**When to use**:
- Set to `true` to verify current version matches expected version
- Use after rollback to confirm successful version change
- Helpful for validation in automation pipelines
- Typically used with `rollback_mas_core=false`

**Valid values**: `true`, `false`

**Impact**:
- `true`: Checks current version matches `mas_core_version`, fails if mismatch
- `false`: Skips version verification (default)

**Related variables**:
- `mas_core_version`: Expected version to verify against
- `rollback_mas_core`: Should be `false` when this is `true`

**Note**: Useful for post-rollback validation or confirming version before proceeding with other operations.

### mas_rollback_dryrun
Enable dry run mode (validation only).

- **Optional**
- Environment Variable: `MAS_ROLLBACK_DRYRUN`
- Default: `false`

**Purpose**: When enabled, performs all validation checks for rollback compatibility without making any actual changes to the MAS installation.

**When to use**:
- Set to `true` before actual rollback to validate compatibility
- Use to test rollback feasibility without risk
- Recommended first step before any rollback operation
- Helpful for planning and validation

**Valid values**: `true`, `false`

**Impact**:
- `true`: Validates rollback compatibility but makes no changes (safe)
- `false`: Executes actual rollback after validation (default)

**Related variables**:
- `rollback_mas_core`: Rollback must be enabled for dry run to be meaningful
- `mas_core_version`: Target version to validate

**Note**: **BEST PRACTICE** - Always run with `mas_rollback_dryrun=true` first to validate the rollback is possible before executing the actual rollback with `mas_rollback_dryrun=false`.

### skip_compatibility_check
Skip version compatibility validation.

- **Optional**
- Environment Variable: `SKIP_COMPATIBILITY_CHECK`
- Default: `false`

**Purpose**: Bypasses the compatibility check that validates the target version is in the list of supported rollback versions. Intended for development and testing scenarios only.

**When to use**:
- **Development/testing only** - for pre-release version testing
- Allows rollback between pre-built versions on same base (e.g., `8.11.0-pre.dev` to `8.11.0-pre.stable`)
- **NEVER use in production environments**

**Valid values**: `true`, `false`

**Impact**:
- `true`: Skips compatibility validation, allows unsupported rollback paths (dangerous)
- `false`: Enforces compatibility checks (safe, default)

**Related variables**:
- `mas_core_version`: Target version (may be unsupported if check skipped)
- `rollback_mas_core`: Rollback execution control

**Note**: **WARNING** - This option is for development purposes only. Skipping compatibility checks can result in failed rollbacks, data corruption, or unstable installations. Never use in production. The compatibility check exists to prevent unsupported rollback scenarios.

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
    mas_upgrade_dryrun: False
    rollback_mas_core: False
    verify_core_version: True
  roles:
    - ibm.mas_devops.suite_rollback
```

## License

EPL-2.0
