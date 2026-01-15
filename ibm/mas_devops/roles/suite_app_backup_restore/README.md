# suite_app_backup_restore

## Overview

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

## Role Variables

### General Variables

#### masbr_action
Action to perform on MAS application data.

- **Required**
- Environment Variable: `MAS_BR_ACTION`
- Default: None

**Purpose**: Specifies whether to create a backup of MAS application data or restore from a previous backup.

**When to use**:
- Set to `backup` to create a backup of application data
- Set to `restore` to restore application data from a backup
- Always required to indicate the operation type

**Valid values**: `backup`, `restore`

**Impact**: 
- `backup`: Creates backup job (on-demand or scheduled) for application data
- `restore`: Restores application data from specified backup version

**Related variables**:
- `masbr_restore_from_version`: Required when action is `restore`
- `masbr_backup_schedule`: Optional for scheduled backups
- `mas_app_id`: Application to backup/restore

**Note**: **IMPORTANT** - This role handles application-specific data (namespace resources, PV data, Watson Studio assets). Database data (Db2, MongoDB) must be backed up/restored separately. An application backup can only be restored to an instance with the same MAS instance ID.

#### mas_app_id
MAS application identifier for backup/restore operations.

- **Required**
- Environment Variable: `MAS_APP_ID`
- Default: None

**Purpose**: Identifies which MAS application to backup or restore. Different applications support different data types (namespace, PV, Watson Studio).

**When to use**:
- Always required for application backup/restore operations
- Must match an installed application in the instance
- Determines which data types are available for backup

**Valid values**: `manage`, `iot`, `monitor`, `health`, `optimizer`, `visualinspection`

**Impact**: Determines which application's data will be backed up or restored. Each application supports different data types:
- `manage`: namespace, pv (attachments)
- `iot`: namespace
- `monitor`: namespace
- `health`: namespace, wsl (Watson Studio)
- `optimizer`: namespace
- `visualinspection`: namespace, pv (datasets, models)

**Related variables**:
- `masbr_backup_data`/`masbr_restore_data`: Data types to backup/restore
- `mas_instance_id`: Instance containing this application
- `mas_workspace_id`: Workspace containing this application

**Note**: Database data (Db2, MongoDB) is not included in application backups and must be backed up separately using dedicated roles.

#### mas_instance_id
MAS instance identifier for application backup/restore.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

**Purpose**: Identifies which MAS instance contains the application to backup or restore. Used to locate application resources and ensure restore compatibility.

**When to use**:
- Always required for application backup and restore operations
- Must match the instance ID from MAS installation
- Critical for restore operations (must match original backup instance ID)

**Valid values**: Lowercase alphanumeric string, 3-12 characters (e.g., `prod`, `dev`, `main`)

**Impact**: Determines which MAS instance's application will be backed up or restored. **CRITICAL** - An application backup can only be restored to an instance with the same MAS instance ID.

**Related variables**:
- `mas_app_id`: Application within this instance
- `mas_workspace_id`: Workspace within this instance
- `masbr_restore_from_version`: Backup version to restore (for restore action)

**Note**: **IMPORTANT** - The instance ID must match between backup and restore operations. Attempting to restore a backup to an instance with a different ID will fail.

#### mas_workspace_id
Workspace identifier for application backup/restore.

- **Required**
- Environment Variable: `MAS_WORKSPACE_ID`
- Default: None

**Purpose**: Identifies which workspace within the MAS instance contains the application to backup or restore. Used to locate application resources.

**When to use**:
- Always required for application backup and restore operations
- Must match the workspace ID from application installation
- Used to construct resource names and locate application data

**Valid values**: Lowercase alphanumeric string (e.g., `ws1`, `prod`, `test`)

**Impact**: Determines which workspace's application data will be backed up or restored. Incorrect workspace ID will cause operations to fail.

**Related variables**:
- `mas_instance_id`: Instance containing this workspace
- `mas_app_id`: Application within this workspace

**Note**: The workspace must contain the specified application. Application data is workspace-specific and cannot be restored to a different workspace.

#### masbr_storage_local_folder
Local filesystem path for backup storage.

- **Required**
- Environment Variable: `MASBR_STORAGE_LOCAL_FOLDER`
- Default: None

**Purpose**: Specifies the local filesystem path where application backup files are stored (for backups) or retrieved from (for restores). This is the persistent storage location for backup data.

**When to use**:
- Always required for backup and restore operations
- Must be accessible from the system running the role
- Should have sufficient space for application data backups
- Must be persistent across operations for restore capability

**Valid values**: Absolute filesystem path (e.g., `/tmp/masbr`, `/backup/mas-apps`, `/mnt/backup`)

**Impact**: Backup files are written to or read from this location. Insufficient space will cause backup failures. Path must exist and be writable.

**Related variables**:
- `masbr_copy_timeout_sec`: Timeout for transferring files to/from this location
- `masbr_restore_from_version`: Backup version stored in this location

**Note**: Ensure the path has sufficient disk space for application backups (especially for Manage attachments and Visual Inspection datasets). For production, use a dedicated backup volume with appropriate retention policies.

#### masbr_confirm_cluster
Confirm cluster connection before backup/restore.

- **Optional**
- Environment Variable: `MASBR_CONFIRM_CLUSTER`
- Default: `false`

**Purpose**: Controls whether the role prompts for confirmation of the currently connected cluster before executing backup or restore operations. Safety feature to prevent accidental operations on wrong cluster.

**When to use**:
- Set to `true` for interactive confirmation (recommended for production)
- Leave as `false` (default) for automated/non-interactive operations
- Use `true` when manually running backup/restore to verify correct cluster

**Valid values**: `true`, `false`

**Impact**: 
- `true`: Role prompts for cluster confirmation before proceeding
- `false`: Role proceeds without confirmation (suitable for automation)

**Related variables**:
- `masbr_action`: Operation requiring cluster confirmation

**Note**: Enabling cluster confirmation is recommended for manual operations, especially in production environments, to prevent accidental backup/restore on the wrong cluster.

#### masbr_copy_timeout_sec
File transfer timeout in seconds.

- **Optional**
- Environment Variable: `MASBR_COPY_TIMEOUT_SEC`
- Default: `43200` (12 hours)

**Purpose**: Specifies the maximum time allowed for transferring application backup files between cluster and local storage. Prevents operations from hanging indefinitely.

**When to use**:
- Use default (12 hours) for most deployments
- Increase for very large backups (e.g., Manage attachments, Visual Inspection datasets)
- Decrease for smaller backups to fail faster on issues

**Valid values**: Positive integer (seconds), e.g., `3600` (1 hour), `43200` (12 hours), `86400` (24 hours)

**Impact**: Operations exceeding this timeout will fail. Insufficient timeout for large backups will cause failures. Excessive timeout delays error detection.

**Related variables**:
- `masbr_storage_local_folder`: Destination for file transfers

**Note**: The default 12 hours is suitable for most deployments. Adjust based on backup size (especially for Manage attachments and Visual Inspection datasets) and network speed.

#### masbr_job_timezone
Time zone for scheduled backup jobs.

- **Optional**
- Environment Variable: `MASBR_JOB_TIMEZONE`
- Default: UTC

**Purpose**: Specifies the time zone for scheduled backup CronJobs. Ensures backups run at the intended local time rather than UTC.

**When to use**:
- Leave unset to use UTC (default)
- Set when you need backups to run at specific local times
- Only applies to scheduled backups (when `masbr_backup_schedule` is set)

**Valid values**: Valid [tz database time zone](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) (e.g., `America/New_York`, `Europe/London`, `Asia/Tokyo`)

**Impact**: Determines when scheduled backups execute. Incorrect time zone may cause backups to run at unexpected times.

**Related variables**:
- `masbr_backup_schedule`: Cron expression interpreted in this time zone

**Note**: Only relevant for scheduled backups. On-demand backups ignore this setting. Use standard tz database names (e.g., `America/New_York`, not `EST`).

### Backup Variables

#### masbr_backup_type
Backup type: full or incremental.

- **Optional**
- Environment Variable: `MASBR_BACKUP_TYPE`
- Default: `full`

**Purpose**: Specifies whether to create a full backup or incremental backup. Incremental backups only capture changes since the last full backup, reducing backup time and storage.

**When to use**:
- Use `full` (default) for complete backups
- Use `incr` for incremental backups of persistent volume data
- Incremental backups require a previous full backup

**Valid values**: `full`, `incr`

**Impact**: 
- `full`: Creates complete backup of all data
- `incr`: Creates incremental backup of PV data only (namespace data is always full)

**Related variables**:
- `masbr_backup_from_version`: Full backup version for incremental backup
- `masbr_backup_data`: Data types to backup

**Note**: **IMPORTANT** - Incremental backups only apply to persistent volume (PV) data. Namespace and Watson Studio data are always backed up in full regardless of this setting. Incremental backups require a previous full backup as a baseline.

#### masbr_backup_data
Data types to include in backup.

- **Optional**
- Environment Variable: `MASBR_BACKUP_DATA`
- Default: All supported data types for the application

**Purpose**: Specifies which types of data to backup. Allows selective backup of namespace resources, persistent volumes, or Watson Studio assets.

**When to use**:
- Leave unset to backup all supported data types (recommended)
- Set to backup specific data types only
- Use comma-separated list for multiple types (e.g., `namespace,pv`)

**Valid values**: Comma-separated list of: `namespace`, `pv`, `wsl`
- `namespace`: Kubernetes namespace resources
- `pv`: Persistent volume data (attachments, datasets, models)
- `wsl`: Watson Studio project assets (Health only)

**Impact**: Only specified data types are backed up. Unspecified types are excluded from backup.

**Related variables**:
- `mas_app_id`: Determines which data types are supported
- `masbr_backup_type`: Full or incremental (applies to PV data only)

**Note**: Supported data types vary by application:
- Manage: `namespace`, `pv`
- IoT/Monitor/Optimizer: `namespace` only
- Health: `namespace`, `wsl`
- Visual Inspection: `namespace`, `pv`

The data types supported by each MAS applications:

| MAS App Name      | MAS App ID          | Data types          |
| ----------------- | ------------------- | ------------------- |
| Manage            | `manage`            | `namespace`, `pv`   |
| IoT               | `iot`               | `namespace`         |
| Monitor           | `monitor`           | `namespace`         |
| Health            | `health`            | `namespace`, `wsl`  |
| Optimizer         | `optimizer`         | `namespace`         |
| Visual Inspection | `visualinspection`  | `namespace`, `pv`   |

#### masbr_backup_from_version
Base full backup version for incremental backups.

- **Optional** (when `masbr_backup_type=incr`)
- Environment Variable: `MASBR_BACKUP_FROM_VERSION`
- Default: Latest full backup (auto-detected)

**Purpose**: Specifies which full backup to use as the baseline for an incremental backup. Incremental backups capture only changes since this version.

**When to use**:
- Only applies when `masbr_backup_type=incr`
- Leave unset to automatically use the latest full backup (recommended)
- Set explicitly to use a specific full backup as baseline

**Valid values**: Timestamp in `YYYYMMDDHHMMSS` format (e.g., `20240621021316` for June 21, 2024 at 02:13:16)

**Impact**: Determines which full backup is used as the baseline. Incremental backup captures changes since this version. If not set, automatically uses the latest full backup.

**Related variables**:
- `masbr_backup_type`: Must be `incr` for this variable to be used
- `masbr_storage_local_folder`: Location where full backup versions are stored

**Note**: Only valid for incremental backups. The specified version must be a full backup (not incremental). Auto-detection finds the latest full backup in storage.

#### masbr_backup_schedule
Cron expression for scheduled backups.

- **Optional**
- Environment Variable: `MASBR_BACKUP_SCHEDULE`
- Default: None (on-demand backup)

**Purpose**: Defines a schedule for automatic recurring backups using Cron syntax. When set, creates a Kubernetes CronJob for automated backups.

**When to use**:
- Leave unset for on-demand backups (manual execution)
- Set to create scheduled/recurring backups
- Use for automated backup strategies

**Valid values**: Valid [Cron expression](https://en.wikipedia.org/wiki/Cron) (e.g., `0 2 * * *` for daily at 2 AM, `0 2 * * 0` for weekly on Sunday at 2 AM)

**Impact**: 
- When set: Creates a Kubernetes CronJob that runs backups automatically on schedule
- When unset: Creates an on-demand backup job that runs immediately

**Related variables**:
- `masbr_job_timezone`: Time zone for interpreting the cron schedule
- `masbr_action`: Must be `backup` for scheduled backups

**Note**: Scheduled backups only apply when `masbr_action=backup`. The cron expression is interpreted in the time zone specified by `masbr_job_timezone` (defaults to UTC). Common patterns: `0 2 * * *` (daily 2 AM), `0 2 * * 0` (weekly Sunday 2 AM), `0 2 1 * *` (monthly 1st at 2 AM).

### Restore Variables

#### masbr_restore_from_version
Backup version timestamp for restore operations.

- **Required** (when `masbr_action=restore`)
- Environment Variable: `MASBR_RESTORE_FROM_VERSION`
- Default: None

**Purpose**: Specifies which backup version to restore from. The version is a timestamp identifying a specific backup.

**When to use**:
- Required when `masbr_action=restore`
- Not used for backup operations
- Must match an existing backup version in storage

**Valid values**: Timestamp in `YYYYMMDDHHMMSS` format (e.g., `20240621021316` for June 21, 2024 at 02:13:16)

**Impact**: Determines which backup is restored. Incorrect or non-existent version will cause restore to fail.

**Related variables**:
- `masbr_action`: Must be `restore` for this variable to be used
- `masbr_storage_local_folder`: Location where backup versions are stored
- `mas_instance_id`: Must match the instance ID from the backup

**Note**: The backup version timestamp is generated automatically during backup creation. List available backups in `masbr_storage_local_folder` to find valid version timestamps. **IMPORTANT** - The backup can only be restored to an instance with the same MAS instance ID as the original backup.

#### masbr_restore_data
Data types to include in restore.

- **Optional**
- Environment Variable: `MASBR_RESTORE_DATA`
- Default: All supported data types for the application

**Purpose**: Specifies which types of data to restore. Allows selective restore of namespace resources, persistent volumes, or Watson Studio assets.

**When to use**:
- Leave unset to restore all supported data types (recommended)
- Set to restore specific data types only
- Use comma-separated list for multiple types (e.g., `namespace,pv`)

**Valid values**: Comma-separated list of: `namespace`, `pv`, `wsl`
- `namespace`: Kubernetes namespace resources
- `pv`: Persistent volume data (attachments, datasets, models)
- `wsl`: Watson Studio project assets (Health only)

**Impact**: Only specified data types are restored. Unspecified types remain unchanged.

**Related variables**:
- `mas_app_id`: Determines which data types are supported
- `masbr_restore_from_version`: Backup version containing the data

**Note**: Supported data types vary by application:
- Manage: `namespace`, `pv`
- IoT/Monitor/Optimizer: `namespace` only
- Health: `namespace`, `wsl`
- Visual Inspection: `namespace`, `pv`

The data types supported by each MAS applications:

| MAS App Name      | MAS App ID          | Data types          |
| ----------------- | ------------------- | ------------------- |
| Manage            | `manage`            | `namespace`, `pv`   |
| IoT               | `iot`               | `namespace`         |
| Monitor           | `monitor`           | `namespace`         |
| Health            | `health`            | `namespace`, `wsl`  |
| Optimizer         | `optimizer`         | `namespace`         |
| Visual Inspection | `visualinspection`  | `namespace`, `pv`   |

### Manage Variables

#### masbr_manage_pvc_paths
Manage PVC paths for backup/restore (Manage only).

- **Optional**
- Environment Variable: `MASBR_MANAGE_PVC_PATHS`
- Default: None

**Purpose**: Specifies which Manage persistent volumes to backup/restore. Defines PVC names, mount paths, and optional subpaths for Manage attachments and custom files.

**When to use**:
- Only applies to Manage application (`mas_app_id=manage`)
- Required when backing up/restoring Manage PV data
- Leave unset to skip Manage PV backup/restore
- Set to backup specific Manage PVCs (e.g., attachments, custom files)

**Valid values**: Comma-separated list in format `<pvcName>:<mountPath>/<subPath>`
- Example: `manage-doclinks1-pvc:/mnt/doclinks1/attachments`
- Multiple: `manage-doclinks1-pvc:/mnt/doclinks1,manage-doclinks2-pvc:/mnt/doclinks2`

**Impact**: Only specified PVCs are backed up/restored. Unspecified PVCs are excluded.

**Related variables**:
- `mas_app_id`: Must be `manage` for this variable to apply
- `masbr_backup_data`/`masbr_restore_data`: Must include `pv` data type

**Note**: PVC names and mount paths are defined in the ManageWorkspace CR `spec.settings.deployment.persistentVolumes`. Subpath is optional. If not set, no Manage PV data is backed up/restored.

The `<pvcName>` and `<mountPath>` are defined in the `ManageWorkspace` CRD instance `spec.settings.deployment.persistentVolumes`:

```yaml
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

If not set a value for this variable, this role will not backup and restore persistent volume data for Manage.

## Example Playbook

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

## License

EPL-2.0
