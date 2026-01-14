Backup MAS Core
===============================================================================

Overview
-------------------------------------------------------------------------------
This role supports backing up MAS Core namespace resources; supports creating on-demand full backups.

!!! important
    Backup can only be restored to an instance with the same MAS instance ID.


Role Variables
-------------------------------------------------------------------------------

### mas_instance_id
The instance ID of the Maximo Application Suite installation to backup.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### mas_backup_dir
The local directory path where backup files will be stored (for backup).

- **Required**
- Environment Variable: `MAS_BACKUP_DIR`
- Default: None
- Example: `/tmp/mas_backups`

### suite_backup_version
Set version to override the default `YYMMDD-HHMMSS` timestamp version used in the name of the backup file.

- **Optional**
- Default: `YYMMDD-HHMMSS` timestamp.
- Environment Variable: `SUITE_BACKUP_VERSION`
