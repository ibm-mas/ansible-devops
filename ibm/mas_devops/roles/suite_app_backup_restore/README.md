Backup and Restore MAS Applications
===============================================================================

Overview
-------------------------------------------------------------------------------
This role supports backing up and restoring the data for below MAS applications:

- `manage`: Manage namespace resources, persistent volume data
- `iot`: IoT namespace resources
- `monitor`: Monitor namespace resources
- `health`: Health namespace resources
- `optimizer`: Optimizer namespace resources
- `visualinspection`: Visual Inspection namespace resources, persistent volume data


Supports creating on-demand or scheduled backup jobs for taking full or incremental backups, and optionally creating Kubernetes jobs for running the backup/restore process

!!! important
    An application backup can only be restored to an instance with the same MAS instance ID.


Role Variables - General
-------------------------------------------------------------------------------
### masbr_action
Set `backup` or `restore` to indicate the role to create a backup or restore job

- **Required**
- Environment Variable: `MAS_BR_ACTION`
- Default: None

### masbr_restore_from_version
Set the backup version to use in the restore, this will be in the format of a `YYYMMDDHHMMSS` timestamp (e.g. `20240621021316`)

- **Required**
- Environment Variable: `MASBR_RESTORE_FROM_VERSION`
- Default: None

### mas_instance_id
Defines the instance ID for the backup or restore action

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

### mas_app_id
Defines the MAS application ID for the backup or restore action (`manage`, `iot`, `monitor`, `optimizer`, or `visualinspection`):

- **Required**
- Environment Variable: `MAS_APP_ID`
- Default: None

### mas_workspace_id
Defines the MAS workspace ID for the backup or restore action:

- **Required**
- Environment Variable: `MAS_WORKSPACE_ID`
- Default: None


// TODO: Add all othe vars in the format above (role docs should be standalone from playbook docs)


Example Playbook
-------------------------------------------------------------------------------

### Backup
Backup Manage namespace resources, note that this does not include backup of any data in Db2, see the `backup` action of the [db2](db2.md) role.

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    masbr_action: backup
    mas_instance_id: main
    mas_workspace_id: ws1
    mas_app_id: manage
  roles:
    - ibm.mas_devops.suite_app_backup_restore
```

### Restore
Restore Manage namespace resources, note that this does not include restore of any data in Db2, see the `restore` action of the [db2](db2.md) role.

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    masbr_action: restore
    masbr_restore_from_version: 20240621021316
    mas_instance_id: main
    mas_workspace_id: ws1
    mas_app_id: manage
  roles:
    - ibm.mas_devops.suite_app_backup_restore
```


License
-------------------------------------------------------------------------------

EPL-2.0
