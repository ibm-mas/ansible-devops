cp4d_db2wh
==========

This role expects a CP4D with DB2 Warehouse service enabled already exists. Use it after `install-cp4d`.

It can be used to create DB2 Warehouse instances against the same Cloud Pak for Data. It is useful if user wants to create a database for IoT and another for Manage. In additional, different from other DB2 Warehouse playbooks, this one uses REST APIs and not Operators to create the DB2 instance (operators are not working properly in CP4D 3.5). By using REST APIs internally, we have a bit more configuration possibilties here as well as the instance will be displayed in CP4D dashboard.

Role Variables
--------------

### Required Variables

- `CPD_ENTITLEMENT_KEY` An [IBM entitlement key](https://myibm.ibm.com/products-services/containerlibrary) that includes access to Cloud Pak for Data 3.5.0
- `CPD_NAMESPACE` Provide the namespace where Cloud Pak for Data is installed. CP4D playbooks create it, by default, in `cpd-meta-ops`
- `DB2WH_INSTANCE_NAME` Name of your database instance, visible in CP4D dashboard. Example: `db2w-iot`
- `MAS_INSTANCE_ID` Provide the MAS instance ID that will be used in any generated MAS configuration files
- `MAS_CONFIG` Provide the path of the folder where the JDBCCfg yaml containing the credentials of this database will be saved at the end of the process.

### Optional Variables

In addition to the above, these are the optional variables you can set before running the playbook:

- `DB2WH_META_STORAGE_SIZE_GB` size of configuration persistent volume, in gigabytes. Default is `20`
- `DB2WH_USER_STORAGE_SIZE_GB` size of user persistent volume, in gigabytes. Default is `100`
- `DB2WH_BACKUP_STORAGE_SIZE_GB` size of backup persistent volume, in gigabytes. Default is `100`
- `DB2WH_META_STORAGE_CLASS` store class used to create the configuration storage. Default is `ibmc-file-silver-gid`
- `DB2WH_USER_STORAGE_CLASS` store class used to create the user storage. Default is `ibmc-file-gold-gid`
- `DB2WH_BACKUP_STORAGE_CLASS` store class used to create the backup storage. Default is `ibmc-file-gold-gid`
- `DB2WH_ADMIN_USER` user in CP4D that can access the database. The user must exist, it is not created by this playbook. Default is `admin`
- `DB2WH_ADMIN_PASSWORD` password of the user identified above. Default is `password`
- `DB2WH_ADDON_VERSION` version of the DB2 Warehouse instance to be creared. Default is `11.5.5.1-cn3-x86_64`
- `DB2WH_TABLE_ORG` the way database tables will be organized. It can be either `ROW` or `COLUMN`. Default is `ROW`


Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    # DB2W-API settings
    cpd_meta_namespace: "{{ lookup('env', 'CPD_NAMESPACE') | default('cpd-meta-ops', true) }}"
    db2wh_instance_name: "{{ lookup('env', 'CPD_DB2WH_INSTANCE_NAME') }}" # e.g. db2w-iot or db2w-manage
    db2wh_meta_storage_size_gb: "{{ lookup('env', 'CPD_META_STORAGE_SIZE_GB') | default(20, true) }}"
    db2wh_user_storage_size_gb: "{{ lookup('env', 'CPD_USER_STORAGE_SIZE_GB') | default(100, true) }}"
    db2wh_backup_storage_size_gb: "{{ lookup('env', 'CPD_BACKUP_STORAGE_SIZE_GB') | default(100, true) }}"
    db2wh_meta_storage_class: "{{ lookup('env', 'CPD_META_STORAGE_CLASS') | default('ibmc-file-silver-gid', true) }}"
    db2wh_user_storage_class: "{{ lookup('env', 'CPD_USER_STORAGE_CLASS') | default('ibmc-file-gold-gid', true)  }}"
    db2wh_backup_storage_class: "{{ lookup('env', 'CPD_BACKUP_STORAGE_CLASS') | default('ibmc-file-gold-gid', true)  }}"
    db2wh_admin_username: "{{ lookup('env', 'CPD_ADMIN_USER')  | default('admin', true) }}"
    db2wh_admin_password: "{{ lookup('env', 'CPD_ADMIN_PASSWORD')  | default('password', true) }}"
    db2wh_addon_version: "{{ lookup('env', 'CPD_DB2WH_ADDON_VERSION') | default('11.5.5.1-cn3-x86_64', true) }}"
    db2wh_table_org: "{{ lookup('env', 'DB2WH_TABLE_ORG') | default('ROW', true) }}" # e.g ROW or COLUMN
    # Create the MAS JdbcCfg & Secret resource definitions
    mas_instance_id: "{{ lookup('env', 'MAS_INSTANCE_ID') }}"
    mas_config_dir: "{{ lookup('env', 'MAS_CONFIG_DIR') }}"
  roles:
    - ibm.mas_devops.cp4d_db2wh
```

License
-------

EPL-2.0
