# suite_app_rollback

Roll back Maximo Application Suite applications to earlier versions when issues are encountered after upgrades. This role provides a safe rollback mechanism with built-in compatibility validation to ensure the target version is supported for rollback from the current version and compatible with the running MAS core platform.

**Important**: Currently designed for Manage application only. Rollback capability is available in MAS 8.7 and later versions. Each version defines a set of supported rollback targets (e.g., from 8.7.x to 8.7.0).

The role performs comprehensive validation before rollback and monitors the reconciliation process to ensure successful completion at the target version.


## Role Variables

### mas_instance_id
MAS instance identifier where the application rollback will be performed.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

**Purpose**: Identifies the target MAS instance containing the application to be rolled back.

**When to use**: Always required. Must match an existing MAS instance with the application installed.

**Valid values**: Valid MAS instance ID (typically 3-12 lowercase alphanumeric characters).

**Impact**: The rollback operation will target the application in the `mas-<instance-id>-<app-id>` namespace. Incorrect instance ID will cause the role to fail.

**Related variables**: `mas_app_id`, `mas_app_version`

**Notes**:
- Must match the instance ID used during MAS installation
- Case-sensitive value
- Ensure you have proper backups before performing rollback operations

### mas_app_id
MAS application identifier to be rolled back.

- **Required**
- Environment Variable: `MAS_APP_ID`
- Default: None

**Purpose**: Specifies which MAS application will be rolled back to an earlier version.

**When to use**: Always required. Currently only `manage` is supported.

**Valid values**:
- `manage` - Maximo Manage application (only supported value currently)

**Impact**: Determines which application namespace and resources will be targeted for rollback. Only Manage application rollback is currently implemented.

**Related variables**: `mas_instance_id`, `mas_app_version`

**Notes**:
- **Critical**: Only `manage` is supported in current implementation
- Future versions may support additional applications
- Application must be installed and running before rollback
- Rollback capability requires MAS 8.7 or later

### mas_app_version
Target version to roll back to.

- **Required** when `rollback_mas_app` or `verify_app_version` is `true`
- Environment Variable: `MAS_APP_VERSION`
- Default: None

**Purpose**: Specifies the exact version to which the application should be rolled back.

**When to use**: Required for rollback operations or version verification. Must be a version that is supported for rollback from the current version.

**Valid values**: Valid MAS application version string (e.g., `8.7.0`, `8.7.1`, `8.8.0`). Must be:
- A version supported for rollback from the current version
- Compatible with the running MAS core platform version
- Available in the configured catalog source

**Impact**: The application will be rolled back to this specific version. Built-in validation prevents unsupported rollback paths.

**Related variables**: `mas_app_id`, `rollback_mas_app`, `skip_compatibility_check`

**Notes**:
- Each MAS version defines supported rollback targets
- Cannot roll back across major version boundaries in most cases
- Verify rollback compatibility in IBM documentation before proceeding
- Consider database schema compatibility when rolling back
- **Always backup before rollback operations**

### rollback_mas_app
Enable or disable the actual rollback operation.

- Optional
- Environment Variable: `ROLLBACK_MAS_APP`
- Default: `true`

**Purpose**: Controls whether the role performs the actual rollback operation or just validation checks.

**When to use**: Set to `true` to perform rollback, `false` to only validate without making changes.

**Valid values**:
- `true` - Perform the rollback operation (default)
- `false` - Validation only, no changes made

**Impact**: When `false`, the role will validate compatibility but not modify the application. Useful for testing rollback feasibility before execution.

**Related variables**: `verify_app_version`, `mas_app_version`

**Notes**:
- Default `true` means rollback will execute if validation passes
- Set to `false` for dry-run validation before actual rollback
- Combine with `verify_app_version` for post-rollback verification
- Validation includes compatibility checks and version availability

### verify_app_version
Enable verification that the application is at the specified version.

- Optional
- Environment Variable: `VERIFY_APP_VERSION`
- Default: `false`

**Purpose**: Checks whether the current application version matches the specified target version, useful for post-rollback verification.

**When to use**: Set to `true` to verify the application version without performing rollback. Useful after rollback to confirm success.

**Valid values**:
- `true` - Verify current version matches `mas_app_version`
- `false` - Skip version verification (default)

**Impact**: When `true`, the role will check if the application is at the specified version and report success or failure. No changes are made to the application.

**Related variables**: `mas_app_version`, `rollback_mas_app`

**Notes**:
- Useful for post-rollback validation in automation pipelines
- Can be used independently of rollback operation
- Set `rollback_mas_app=false` and `verify_app_version=true` for verification-only mode
- Helps confirm rollback completed successfully

### mas_rollback_dryrun
Enable dry-run mode for rollback operations.

- Optional
- Environment Variable: `MAS_ROLLBACK_DRYRUN`
- Default: `false`

**Purpose**: Performs all validation checks without actually executing the rollback, allowing you to test the rollback process safely.

**When to use**: Set to `true` when you want to validate rollback feasibility without making any changes to the system.

**Valid values**:
- `true` - Dry-run mode, validation only
- `false` - Normal operation (default)

**Impact**: When `true`, all compatibility checks and validations are performed, but no changes are made to the application or cluster.

**Related variables**: `rollback_mas_app`, `skip_compatibility_check`

**Notes**:
- Recommended to run in dry-run mode first before actual rollback
- Helps identify potential issues before committing to rollback
- All validation errors will be reported without risk
- Does not affect the running application

### skip_compatibility_check
Bypass compatibility validation checks.

- Optional
- Environment Variable: `SKIP_COMPATIBILITY_CHECK`
- Default: `false`

**Purpose**: Allows skipping the built-in compatibility validation between the target rollback version and the current MAS core platform version.

**When to use**: **Use with extreme caution**. Only skip checks when you have verified compatibility through other means or are following IBM support guidance.

**Valid values**:
- `true` - Skip compatibility validation (dangerous)
- `false` - Perform all compatibility checks (default, recommended)

**Impact**: When `true`, the role will not validate version compatibility, potentially allowing unsupported rollback operations that could cause system instability or data corruption.

**Related variables**: `mas_app_version`, `rollback_mas_app`

**Notes**:
- **Warning**: Skipping compatibility checks can lead to unsupported configurations
- Only use when explicitly instructed by IBM support
- May result in application failures or data issues
- Default `false` is strongly recommended for production environments
- Compatibility checks protect against unsupported rollback paths

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
