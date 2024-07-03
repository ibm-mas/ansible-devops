Backup and Restore MAS Core
===============================================================================

Overview
-------------------------------------------------------------------------------
This role supports backing up and restoring MAS Core namespace resources; supports creating on-demand or scheduled backup jobs for taking full or incremental backups, and optionally creating Kubernetes jobs for running the backup/restore process.

!!! important
    A backup can only be restored to an instance with the same MAS instance ID.


Role Variables - General
-------------------------------------------------------------------------------
### masbr_action
Set `backup` or `restore` to indicate the role to create a backup or restore job

- **Required**
- Environment Variable: `MAS_BR_ACTION`
- Default: None

### mas_instance_id
Defines the instance ID for the backup or restore action

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

// TODO: Add all othe vars in the format above (role docs should be standalone from playbook docs)


Example Playbook
-------------------------------------------------------------------------------

### Backup
Backup MAS Core namespace resources, note that this does not include backup of any data in MongoDb, see the `backup` action in the[mongodb](mongodb.md) role.

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    masbr_action: backup
    mas_instance_id: main
  roles:
    - ibm.mas_devops.suite_backup_restore
```

### Restore
Restore MAS Core namespace resources, note that this does not include backup of any data in MongoDb, see the `restore` action in the [mongodb](mongodb.md) role.

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    masbr_action: restore
    masbr_restore_from_version: 20240621021316
    mas_instance_id: main
  roles:
    - ibm.mas_devops.suite_backup_restore
```


License
-------------------------------------------------------------------------------

EPL-2.0
