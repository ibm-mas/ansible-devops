# suite_backup_restore

This role supports backing up and restoring MAS Core namespace resources; supports creating on-demand or scheduled backup jobs for taking full or incremental backups, and optionally creating Kubernetes jobs for running the backup/restore process.

!!! important
    A backup can only be restored to an instance with the same MAS instance ID.

## Role Variables

### General

#### masbr_action
Action to perform on MAS Core namespace.

- **Required**
- Environment Variable: `MASBR_ACTION`
- Default: None

**Purpose**: Specifies whether to create a backup of MAS Core namespace resources or restore from a previous backup.

**When to use**:
- Set to `backup` to create a backup of MAS Core namespace resources
- Set to `restore` to restore MAS Core namespace from a backup
- Always required to indicate the operation type

**Valid values**: `backup`, `restore`

**Impact**: 
- `backup`: Creates backup job (on-demand or scheduled) for MAS Core namespace resources
- `restore`: Restores MAS Core namespace from specified backup version

**Related variables**:
- `masbr_restore_from_version`: Required when action is `restore`
- `masbr_backup_schedule`: Optional for scheduled backups
- `mas_instance_id`: Instance to backup/restore

**Note**: **IMPORTANT** - This role handles MAS Core namespace resources only. MongoDB data must be backed up/restored separately using the `mongodb` role. A backup can only be restored to an instance with the same MAS instance ID.

#### mas_instance_id
MAS instance identifier for backup/restore operations.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

**Purpose**: Identifies which MAS instance to backup or restore. Used to locate MAS Core namespace resources and ensure restore compatibility.

**When to use**:
- Always required for backup and restore operations
- Must match the instance ID from MAS installation
- Critical for restore operations (must match original backup instance ID)

**Valid values**: Lowercase alphanumeric string, 3-12 characters (e.g., `prod`, `dev`, `main`)

**Impact**: Determines which MAS instance's Core namespace will be backed up or restored. **CRITICAL** - A backup can only be restored to an instance with the same MAS instance ID.

**Related variables**:
- `masbr_action`: Whether backing up or restoring this instance
- `masbr_restore_from_version`: Backup version to restore (for restore action)

**Note**: **IMPORTANT** - The instance ID must match between backup and restore operations. Attempting to restore a backup to an instance with a different ID will fail.

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

**Purpose**: Specifies the maximum time allowed for transferring backup files between cluster and local storage. Prevents operations from hanging indefinitely.

**When to use**:
- Use default (12 hours) for most deployments
- Increase for very large backups or slow network connections
- Decrease for smaller backups to fail faster on issues

**Valid values**: Positive integer (seconds), e.g., `3600` (1 hour), `43200` (12 hours), `86400` (24 hours)

**Impact**: Operations exceeding this timeout will fail. Insufficient timeout for large backups will cause failures. Excessive timeout delays error detection.

**Related variables**:
- `masbr_storage_local_folder`: Destination for file transfers

**Note**: The default 12 hours is suitable for most deployments. Adjust based on backup size and network speed. Monitor actual transfer times to optimize this setting.

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

#### masbr_storage_local_folder
Local filesystem path for backup storage.

- **Required**
- Environment Variable: `MASBR_STORAGE_LOCAL_FOLDER`
- Default: None

**Purpose**: Specifies the local filesystem path where backup files are stored (for backups) or retrieved from (for restores). This is the persistent storage location for backup data.

**When to use**:
- Always required for backup and restore operations
- Must be accessible from the system running the role
- Should have sufficient space for backup files
- Must be persistent across operations for restore capability

**Valid values**: Absolute filesystem path (e.g., `/tmp/masbr`, `/backup/mas`, `/mnt/backup`)

**Impact**: Backup files are written to or read from this location. Insufficient space will cause backup failures. Path must exist and be writable.

**Related variables**:
- `masbr_copy_timeout_sec`: Timeout for transferring files to/from this location
- `masbr_restore_from_version`: Backup version stored in this location

**Note**: Ensure the path has sufficient disk space for backups. For production, use a dedicated backup volume with appropriate retention policies. The path must be accessible during both backup and restore operations.

### Backup

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

### Restore

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

## Example Playbook

### Backup
Backup MAS Core namespace resources, note that this does not include backup of any data in MongoDb, see the `backup` action in the [mongodb](mongodb.md) role.

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

## License

EPL-2.0
