cp4d_db2wh
==========

This role expects a CP4D with DB2 Warehouse service enabled already exists. Use it after `install-cp4d`.

It can be used to create DB2 Warehouse instances against the same Cloud Pak for Data. It is useful if user wants to create a database for IoT and another for Manage. In additional, different from other DB2 Warehouse playbooks, this one uses REST APIs and not Operators to create the DB2 instance (operators are not working properly in CP4D 3.5). By using REST APIs internally, we have a bit more configuration possibilties here as well as the instance will be displayed in CP4D dashboard.

Role Variables
--------------

### db2wh_instance_name
Name of the database instance, note that this is the instance **name**, which is different from the instance **ID**.

- Environment Variable: `DB2WH_INSTANCE_NAME`
- Default: None

### db2wh_addon_version
Version of the DB2 Warehouse instance to be created.

- Environment Variable: `DB2WH_ADDON_VERSION`
- Default: `11.5.5.1-cn3-x86_64`

### db2wh_table_org
The way database tables will be organized. It can be set to either `ROW` or `COLUMN`.

- Environment Variable: `DB2WH_TABLE_ORG`
- Default: `ROW`

### db2wh_meta_storage_class
Required.  Storage class used for metadata.

- Environment Variable: `DB2WH_META_STORAGE_CLASS`
- Default: None

### db2wh_meta_storage_size_gb
Size of the metadata persistent volume, in gigabytes

- Environment Variable: `DB2WH_META_STORAGE_SIZE_GB`
- Default: `20`

### db2wh_user_storage_class
Required.  Storage class used for user data.

- Environment Variable: `DB2WH_USER_STORAGE_CLASS`
- Default: None

### db2wh_user_storage_size_gb
Size of user persistent volume, in gigabytes.

- Environment Variable: `DB2WH_USER_STORAGE_SIZE_GB`
- Default: `100`

### db2wh_backup_storage_class
Required.  Storage class used for backup.

- Environment Variable: `DB2WH_BACKUP_STORAGE_CLASS`
- Default: None

### db2wh_backup_storage_size_gb
Size of backup persistent volume, in gigabytes.

- Environment Variable: `DB2WH_BACKUP_STORAGE_SIZE_GB`
- Default: `100`

### db2wh_logs_storage_class
Required.  Storage class used for logs.

- Environment Variable: `DB2WH_LOGS_STORAGE_CLASS`
- Default: None

### db2wh_logs_storage_size_gb
Size of logs persistent volume, in gigabytes.

- Environment Variable: `DB2WH_LOGS_STORAGE_SIZE_GB`
- Default: `100`

### db2wh_temp_storage_class
Required.  Storage class used for temporary data.

- Environment Variable: `DB2WH_TEMP_STORAGE_CLASS`
- Default: None

### db2wh_temp_storage_size_gb
Size of temporary persistent volume, in gigabytes.

- Environment Variable: `DB2WH_TEMP_STORAGE_SIZE_GB`
- Default: `100`

### db2wh_admin_username
TODO: Provide details about this input

- Environment Variable: `DB2WH_ADMIN_USER`
- Default: `admin`

### db2wh_admin_password
TODO: Provide details about this input

- Environment Variable: `DB2WH_ADMIN_PASSWORD`
- Default: `password` (This will be fixed!!)

### mas_instance_id
Providing this and `mas_config_dir` will instruct the role to generate a JdbcCfg template that can be used to configure MAS to connect to this database.

- Environment Variable: `MAS_INSTANCE_ID') }}"
- Default: None

### mas_config_dir
Providing this and `mas_instance_id` will instruct the role to generate a JdbcCfg template that can be used to configure MAS to connect to this database.

- Environment Variable: `MAS_CONFIG_DIR') }}"
- Default: None

### mas_config_scope
Supported values are `system`, `ws`, `app`, or `wsapp`, this is only used when both `mas_config_dir` and `mas_instance_id` are set.

- Environment Variable: `MAS_CONFIG_SCOPE`
- Default: `system`

### mas_workspace_id
This is only used when both `mas_config_dir` and `mas_instance_id` are set, and `mas_config_scope` is set to either `ws` or `wsapp`

- Environment Variable: `MAS_WORKSPACE_ID') }}" # Necessary for ws and wsapp scopes
- Default: None

### mas_application_id
This is only used when both `mas_config_dir` and `mas_instance_id` are set, and `mas_config_scope` is set to either `app` or `wsapp`

- Environment Variable: `'MAS_APP_ID') }}" # Necessary for app and wsapp scopes
- Default: None


Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    db2wh_instance_name: db2wh-shared

    # Configure storage suitable for IBM Cloud ROKS
    db2wh_meta_storage_class: ibmc-file-silver-gid
    db2wh_user_storage_class: ibmc-file-gold-gid
    db2wh_backup_storage_class: ibmc-file-gold-gid
    db2wh_logs_storage_class: ibmc-file-silver-gid
    db2wh_temp_storage_class: ibmc-file-silver-gid

    db2wh_admin_password: "{{ lookup('env', 'CPD_ADMIN_PASSWORD') }}"

    # Create the MAS JdbcCfg & Secret resource definitions
    mas_instance_id: "{{ lookup('env', 'MAS_INSTANCE_ID') }}"
    mas_config_dir: "{{ lookup('env', 'MAS_CONFIG_DIR') }}"
  roles:
    - ibm.mas_devops.cp4d_db2wh
```

License
-------

EPL-2.0
