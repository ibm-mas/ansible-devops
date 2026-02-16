# suite_uninstall

This role removes Maximo Application Suite Core Platform. Note that it does not remove any data from MongoDB by default, and does not remove any applications from the MAS install. Generally it should be used after `suite_app_uninstall` to remove all installed Maximo Application Suite applications.

!!! warning
    This role performs destructive operations. Ensure you have backups before proceeding. Use `mas_wipe_mongo_data` carefully as it permanently deletes all MAS data.

## Role Variables

### mas_instance_id
MAS instance identifier to uninstall.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

**Purpose**: Identifies which MAS instance to remove from the cluster. The role deletes the Suite custom resource and associated core platform resources.

**When to use**:
- Always required for uninstall operations
- Must match the instance ID from MAS installation
- Used to target specific instance for removal

**Valid values**: Lowercase alphanumeric string, 3-12 characters (e.g., `prod`, `dev`, `masinst1`)

**Impact**: Determines which MAS instance is uninstalled. All core platform resources for this instance will be removed, but MongoDB data is preserved by default unless `mas_wipe_mongo_data` is enabled.

**Related variables**:
- `mas_wipe_mongo_data`: Controls whether MongoDB data is deleted

**Note**: This role only removes the MAS core platform. Applications must be uninstalled separately using `suite_app_uninstall` before running this role. MongoDB data is preserved by default for safety.

### mas_wipe_mongo_data
Delete MongoDB databases during uninstall.

- **Optional**
- Environment Variable: `MAS_WIPE_MONGO_DATA`
- Default: `false`

**Purpose**: Controls whether MongoDB databases containing MAS data are permanently deleted during uninstall. When disabled (default), only the MAS platform is removed while preserving all data.

**When to use**:
- Leave as `false` (default) to preserve data (recommended)
- Set to `true` only for complete removal including all data
- Use `true` for test/dev environments or when data is no longer needed
- **NEVER** use `true` in production without verified backups

**Valid values**: `true`, `false`

**Impact**:
- `false`: Removes MAS platform but preserves all MongoDB data (safe, allows reinstall)
- `true`: Removes MAS platform AND permanently deletes all MongoDB databases (destructive)

**Related variables**:
- `mas_instance_id`: Instance whose data may be deleted

**Note**: **CRITICAL** - Setting to `true` permanently deletes all MAS data including configurations, workspaces, and application data. This operation cannot be undone. Always ensure you have verified backups before enabling this option. The default `false` is strongly recommended for production environments.

## Example Playbook

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: "inst1"

  roles:
    - ibm.mas_devops.suite_uninstall
```

## License

EPL-2.0
