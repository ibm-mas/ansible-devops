Backup and Restore MAS Applications
===============================================================================

Overview
-------------------------------------------------------------------------------
This role supports backing up and restoring the data for below MAS applications:

- `manage`: Manage namespace resources, persistent volume data (e.g. attachments)
- `iot`: IoT namespace resources
- `monitor`: Monitor namespace resources
- `health`: Health namespace resources, Watson Studio project asset
- `optimizer`: Optimizer namespace resources
- `visualinspection`: Visual Inspection namespace resources, persistent volume data (e.g. image datasets, models)


Supports creating on-demand or scheduled backup jobs for taking full or incremental backups, and optionally creating Kubernetes jobs for running the backup/restore process.

!!! important
    An application backup can only be restored to an instance with the same MAS instance ID.


Role Variables - General
-------------------------------------------------------------------------------
### masbr_action
Set `backup` or `restore` to indicate the role to create a backup or restore job.

- **Required**
- Environment Variable: `MAS_BR_ACTION`
- Default: None

### mas_app_id
Defines the MAS application ID (`manage`, `iot`, `monitor`, `health`, `optimizer`, or `visualinspection`) for the backup or restore action.

- **Required**
- Environment Variable: `MAS_APP_ID`
- Default: None

### mas_instance_id
Defines the MAS instance ID for the backup or restore action.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

### mas_workspace_id
Defines the MAS workspace ID for the backup or restore action.

- **Required**
- Environment Variable: `MAS_WORKSPACE_ID`
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
### masbr_backup_type
Set `full` or `incr` to indicate the role to create a full backup or incremental backup. Only supports creating incremental backup for persistent volume data, this role will always create a full backup for other type of data regardless of whether this variable be set to `incr`.

- Optional
- Environment Variable: `MASBR_BACKUP_TYPE`
- Default: `full`

### masbr_backup_data
Set the types of data to be backed up, multiple data types are separated by commas (e.g. `namespace,pv`). If not set a value for this variable, this role will back up all types of data that supported by the specified MAS application. The data types supported by each MAS applications:

| MAS App Name      | MAS App ID          | Data types          |
| ----------------- | ------------------- | ------------------- |
| Manage            | `manage`            | `namespace`, `pv`   |
| IoT               | `iot`               | `namespace`         |
| Monitor           | `monitor`           | `namespace`         |
| Health            | `health`            | `namespace`, `wsl`  |
| Optimizer         | `optimizer`         | `namespace`         |
| Visual Inspection | `visualinspection`  | `namespace`, `pv`   |

- Optional
- Environment Variable: `MASBR_BACKUP_DATA`
- Default: None

### masbr_backup_from_version
Set the full backup version to use in the incremental backup, this will be in the format of a `YYYMMDDHHMMSS` timestamp (e.g. `20240621021316`). This variable is only valid when `MASBR_BACKUP_TYPE=incr`. If not set a value for this variable, this role will try to find the latest full backup version from the specified storage location.

- Optional
- Environment Variable: `MASBR_BACKUP_FROM_VERSION`
- Default: None

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

### masbr_restore_data
Set the types of data to be restored, multiple data types are separated by commas (e.g. `namespace,pv`). If not set a value for this variable, this role will restore all types of data that supported by the specified MAS application. The data types supported by each MAS applications:

| MAS App Name      | MAS App ID          | Data types          |
| ----------------- | ------------------- | ------------------- |
| Manage            | `manage`            | `namespace`, `pv`   |
| IoT               | `iot`               | `namespace`         |
| Monitor           | `monitor`           | `namespace`         |
| Health            | `health`            | `namespace`, `wsl`  |
| Optimizer         | `optimizer`         | `namespace`         |
| Visual Inspection | `visualinspection`  | `namespace`, `pv`   |

- Optional
- Environment Variable: `MASBR_RESTORE_DATA`
- Default: None


Role Variables - Manage
-------------------------------------------------------------------------------
### masbr_manage_pvc_paths
Set the Manage PVC paths to use in backup and restore. The PVC path is in the format of `<pvcName>:<mountPath>/<subPath>`. Multiple PVC paths are separated by commas (e.g. `manage-doclinks1-pvc:/mnt/doclinks1/attachments,manage-doclinks2-pvc:/mnt/doclinks2`).

The `<pvcName>` and `<mountPath>` are defined in the `ManageWorkspace` CRD instance `spec.settings.deployment.persistentVolumes`:
```
persistentVolumes:
  - accessModes:
      - ReadWriteMany
    mountPath: /mnt/doclinks1
    pvcName: manage-doclinks1-pvc
    size: '20'
    storageClassName: ocs-storagecluster-cephfs
    volumeName: ''
  - accessModes:
      - ReadWriteMany
    mountPath: /mnt/doclinks2
    pvcName: manage-doclinks2-pvc
    size: '20'
    storageClassName: ocs-storagecluster-cephfs
    volumeName: ''
```

If not set a value for this variable, this role will not backup and restore persistent valumne data for Manage.


- Optional
- Environment Variable: `MASBR_MANAGE_PVC_PATHS`
- Default: None


Example Playbook
-------------------------------------------------------------------------------

### Backup
Backup Manage attachments, note that this does not include backup of any data in Db2, see the `backup` action in the [db2](db2.md) role.

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    masbr_action: backup
    mas_instance_id: main
    mas_workspace_id: ws1
    mas_app_id: manage
    masbr_backup_data: pv
    masbr_manage_pvc_paths: "manage-doclinks1-pvc:/mnt/doclinks1"
    masbr_storage_local_folder: /tmp/masbr
  roles:
    - ibm.mas_devops.suite_app_backup_restore
```

### Restore
Restore Manage attachments, note that this does not include restore of any data in Db2, see the `restore` action in the [db2](db2.md) role.

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    masbr_action: restore
    masbr_restore_from_version: 20240621021316
    mas_instance_id: main
    mas_workspace_id: ws1
    mas_app_id: manage
    masbr_backup_data: pv
    masbr_manage_pvc_paths: "manage-doclinks1-pvc:/mnt/doclinks1"
    masbr_storage_local_folder: /tmp/masbr
  roles:
    - ibm.mas_devops.suite_app_backup_restore
```


License
-------------------------------------------------------------------------------

EPL-2.0
