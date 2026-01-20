Restore MAS Core
===============================================================================

Overview
-------------------------------------------------------------------------------
This role supports restoring the MAS Core namespace resources when provided the
backup arhive generated from `suite_backup` role.

!!! important
    Restore can only be made to the an instance with the same MAS instance ID as the backup.


Role Variables
-------------------------------------------------------------------------------

### mas_instance_id
The instance ID of the Maximo Application Suite installation to restore.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### mas_backup_dir
The local directory path where backup files to restore are stored.

- **Required**
- Environment Varia`
- Default: None
- Example: `/tmp/mas_backups`

### suite_backup_version
The version of the backup file located in the `MAS_BACKUP_DIR` to be used
in the restore

- **Required**
- Default: None
- Environment Variable: `SUITE_BACKUP_VERSION`
- Example: `260116-130937`

### mas_domain
The domain to use for the MAS Suite instance. If not provided, the domain from the backup will be used.

- Optional
- Environment Variable: `MAS_DOMAIN`
- Default: `NO_OVERRIDE` (uses value from backup)
- Example: `mydomain.example.com`

### sls_url
The URL for the Suite License Service (SLS). If not provided, the URL from the backup will be used.

- Optional
- Environment Variable: `SLS_URL`
- Default: `NO_OVERRIDE` (uses value from backup)
- Example: `https://sls.example.com`

### bas_url
The URL for the Behavior Analytics Service (BAS). If not provided, the URL from the backup will be used.

- Optional
- Environment Variable: `BAS_URL`
- Default: `NO_OVERRIDE` (uses value from backup)
- Example: `https://bas.example.com`
