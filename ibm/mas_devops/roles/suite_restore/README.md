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

- **Optional**
- Environment Variable: `MAS_DOMAIN`
- Default: `NO_OVERRIDE` (uses value from backup)
- Example: `mydomain.example.com`

### include_sls_from_backup
Controls whether to restore the Suite SLS (Suite License Service) configuration from the backup archive.

- **Optional**
- Default: `true`
- Environment Variable: `INCLUDE_SLS_FROM_BACKUP`

### sls_url
If `include_sls_from_backup` is true. The URL for the Suite License Service (SLS). If not provided, the URL from the backup will be used.
This is used when the domain has changed for SLS but SLS was restored from a backup and so the regristration key is the same.

- **Optional**
- Environment Variable: `SLS_URL`
- Default: `NO_OVERRIDE` (uses value from backup)
- Example: `https://sls.example.com`

### sls_cfg_file
If `include_sls_from_backup` is false. Path to the file containing external SLS configuration YAML file to apply.
This is used when you want to use SLS configuration from outside the backup archive (e.g., from a separate SLS role execution).

- **Optional**
- Environment Variable: `SLS_CFG_FILE`
- Default: None
- Example: `/tmp/sls_config/sls.yml`

### include_dro_from_backup
Controls whether to restore the Suite DRO configuration from the backup archive.

- **Optional**
- Default: `true`
- Environment Variable: `INCLUDE_DRO_FROM_BACKUP`

### bas_url
If `include_dro_from_backup` is true. The URL for the Behavior Analytics Service (BAS). If not provided, the URL from the backup will be used.
This is used when the domain has changed for DRO but DRO was restored from a backup and so the api key is the same.

- **Optional**
- Environment Variable: `BAS_URL`
- Default: `NO_OVERRIDE` (uses value from backup)
- Example: `https://bas.example.com`

### dro_cfg_file
If `include_dro_from_backup` is false. Path to the file containing external DRO (BAS) configuration YAML file to apply.
This is used when you want to use DRO configuration from outside the backup archive (e.g., from a separate DRO role execution).

- **Optional**
- Environment Variable: `DRO_CFG_FILE`
- Default: None
- Example: `/tmp/dro_config/dro.yml`
