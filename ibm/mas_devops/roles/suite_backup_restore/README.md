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
Set `backup` or `restore` to indicate the role to create a backup or restore job.

- **Required**
- Environment Variable: `MAS_BR_ACTION`
- Default: None

### mas_instance_id
Defines the MAS instance ID for the backup or restore action.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

### masbr_confirm_cluster
Set `true` or `false` to indicate the role whether to confirm the currently connected cluster before running the backup or restore job.

- Optional
- Environment Variable: `MASBR_CONFIRM_CLUSTER`
- Default: `false`

### masbr_copy_timeout_sec
Set the transfer files timeout in seconds.

- Optional
- Environment Variable: `MASBR_COPY_TIMEOUT_SEC`
- Default: `43200` (12 hours)

### masbr_job_timezone
Set the [time zone](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) for creating scheduled backup job. If not set a value for this variable, this role will use UTC time zone when creating a CronJob for running scheduled backup job.

- Optional
- Environment Variable: `MASBR_JOB_TIMEZONE`
- Default: None

### masbr_storage_local_folder
Set local path to save the backup files.

- **Required**
- Environment Variable: `MASBR_STORAGE_LOCAL_FOLDER`
- Default: None


Role Variables - Backup
-------------------------------------------------------------------------------
### masbr_backup_schedule
Set [Cron expression](ttps://en.wikipedia.org/wiki/Cron) to create a scheduled backup. If not set a value for this varialbe, this role will create an on-demand backup.

- Optional
- Environment Variable: `MASBR_BACKUP_SCHEDULE`
- Default: None


Role Variables - Restore
-------------------------------------------------------------------------------
### masbr_restore_from_version
Set the backup version to use in the restore, this will be in the format of a `YYYMMDDHHMMSS` timestamp (e.g. `20240621021316`)

- **Required** only when `MAS_BR_ACTION=restore`
- Environment Variable: `MASBR_RESTORE_FROM_VERSION`
- Default: None


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
    masbr_storage_local_folder: /tmp/masbr
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
    masbr_storage_local_folder: /tmp/masbr
  roles:
    - ibm.mas_devops.suite_backup_restore
```


License
-------------------------------------------------------------------------------

EPL-2.0
