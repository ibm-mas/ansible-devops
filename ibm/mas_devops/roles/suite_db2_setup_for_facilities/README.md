suite_db2_setup_for_facilities
==========================

This role shouldn't need to exist, it should be part of the Facilities operator, but is not so we have to do it as a separate step in the install flow for now.  The role will perform some initial setup on the Db2 instance that is needed to prepare it for use with the Real estate and Facilities application.

The role will copy scripts into the Db2 pod and execute it inside the container, this script will perform a number of configuration changes to the database as well as configuring the tablespaces for Maximo Real estate and facilities because the operator is not yet able to do this itself.

Pre-Requisites
--------------
The Db2 database needs to be created with set a of properties in the startup and can be invoked as follows: 

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    db2_action: restore
    db2_instance_name: db2u-db01
    masbr_restore_from_version: 20240621021316
    masbr_storage_local_folder: /tmp/masbr
    db2_instance_registry:
      DB2_COMPATIBILITY_VECTOR: ORA
      DB2AUTH: 'OSAUTHDB,ALLOW_LOCAL_FALLBACK,PLUGIN_AUTO_RELOAD'
      DB2_4K_DEVICE_SUPPORT: 'ON'
      DB2_FMP_RUN_AS_CONNECTED_USER: 'NO'
      DB2_WORKLOAD: 'PUREDATA_OLAP'
  roles:
    - ibm.mas_devops.db2
```
If the database is not created with these properties, Maximo Real Estate and Facilities will not be succesfully installed. In case of a deployment without these properties, a new instance will be required with the correct properties. Refer to `oneclick_add_facilities.yml` for an example of a complete installation.

Role Variables
--------------
### db2_instance_name
The name of the db2 instance to execute the setup in.

- **Required**
- Environment Variable: `DB2_INSTANCE_NAME`
- Default Value: None

### db2_namespace
The namespace where the Db2 instance is running.

- Optional
- Environment Variable: `DB2_NAMESPACE`
- Default Value: `db2u`

### db2_username
The username that will be used to connect to the database specified by `db2_dbname`.

- Optional
- Environment Variable: None
- Default Value: `db2inst1`

### db2_dbname
The name of the database in the instance to connect to when executing the setup script.

- Optional
- Environment Variable: None
- Default Value: `BLUDB`

### db2_schema
The name of the Manage schema where the hack should be targeted in.

- Optional
- Environment Variable: None
- Default Value: `tridata`

### db2_tablespace_data_size
The size of the tablespace data in the database.

- Optional
- Environment Variable: DB2_TABLESPACE_DATA_SIZE
- Default Value: `5000 M`

### db2_tablespace_index_size
The size of the tablespace indexes in the database.

- Optional
- Environment Variable: DB2_TABLESPACE_INDEX_SIZE
- Default Value: `5000 M`

### db2_config_version
Version of the enhanced DB2 parameters, currently support `1.0.0`

- **Required**
- Environment Variable: `DB2_CONFIG_VERSION`
- Default: `1.0.0`

### enforce_db2_config
Flag to indicate restart the DB2 instance or not, the enhanced DB2 parameters required restart DB2 instance, this will cause downtime, should execute during customer maintenance window or newly created DB2 instance if set to `True`

- **Required**
- Environment Variable: `ENFORCE_DB2_CONFIG`
- Default: `True`

Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:

    # Configuration for the Db2 cluster
    db2_namespace: db2u
    db2_instance_name: db2u-db01
    db2_dbname: BLUDB

  roles:
    - ibm.mas_devops.suite_db2_setup_for_facilities
```


License
-------

EPL-2.0
