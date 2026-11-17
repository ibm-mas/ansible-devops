# suite_uninstall

This role removes Maximo Application Suite Core Platform. Note that it does not remove any data from MongoDB by default, and does not remove any applications from the MAS install. Generally it should be used after `suite_app_uninstall` to remove all installed Maximo Application Suite applications.

!!! warning
    This role performs destructive operations. Ensure you have backups before proceeding. Use `mas_wipe_mongo_data` carefully as it permanently deletes all MAS data.

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`mas_instance_id`](#mas_instance_id) | Yes | None |
| [`mas_wipe_mongo_data`](#mas_wipe_mongo_data) | No | `false` |

### Uninstall Configuration

#### mas_instance_id

MAS instance identifier to uninstall (lowercase alphanumeric, 3-12 characters, e.g. `prod`, `dev`, `masinst1`).

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

Must match the instance ID from MAS installation. The role deletes the Suite custom resource and the associated core platform resources; MongoDB data is preserved unless `mas_wipe_mongo_data` is enabled. Applications must be uninstalled separately with `suite_app_uninstall` before running this role.

#### mas_wipe_mongo_data

Delete MongoDB databases during uninstall.

- **Optional**
- Environment Variable: `MAS_WIPE_MONGO_DATA`
- Default: `false`

!!! danger
    Setting this to `true` permanently deletes all MAS data, including configurations, workspaces, and application data. The operation cannot be undone — always verify you have backups before enabling it. The default `false` is strongly recommended for production environments.

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
