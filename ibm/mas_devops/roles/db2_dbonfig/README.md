db2_dbconfig
===============================================================================

This role apply the enhanced DB2 parameters which reviewed by DBA on existing or newly created DB2 instance. It will use `merge` strategy for the parameters changes, that means it won't overwride existing DB2 configs/settings, but as follows:

- If the same parameter already existed, but value is different with new one, will updated.
- If the parameter didn't exist, will added.
- If the parameter already existed, but not in the enhanced parameters list, nothing need to be done.


Role Variables - Installation
-------------------------------------------------------------------------------
### db2_instance_name
Name of the database instance, note that this is the instance **name**.

- **Required**
- Environment Variable: `DB2_INSTANCE_NAME`
- Default: None

### db2_namespace
Name of the namespace where Db2 clusters created

- **Required**
- Environment Variable: `DB2_NAMESPACE`
- Default: `mas-cpd`

### db2_config_version
Version of the enhanced DB2 parameters, currently support `1.0.0`

- **Required**
- Environment Variable: `DB2_CONFIG_VERSION`
- Default: None

### enforce_db2_config
Flag to indicate restart the DB2 instance or not, the enhanced DB2 parameters required restart DB2 instance, this will cause downtime, should execute during customer maintenance window or newly created DB2 instance if set to `True`

- **Required**
- Environment Variable: `ENFORCE_DB2_CONFIG`
- Default: `True`

### sre_namespace
Name of the namespace where DB2 enforce ConfigMap created, the ConfigMap stored the applied version of the enhanced DB2 parameters, it means the DB2 instance already applied the version if the ConfigMap exists.

- Optional
- Environment Variable: `SRE_NAMESPACE`
- Default: `ibm-aiapps-sre-pipelines`


Example Playbook
-----------------------------------------------------------------------------------------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:

    db2_instance_name: db2u-db01
    db2_namespace: mas-cpd
    db2_config_version: "1.0.0"

    # It will cause downtime if set to true, please be careful.
    enforce_db2_config: true

  roles:
    - ibm.mas_devops.db2_dbconfig
```

License
-------------------------------------------------------------------------------

EPL-2.0
