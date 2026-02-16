suite_db2_setup_for_manage
==========================

This role performs initial setup on Db2 instances for use with the Maximo Manage application. It supports both CP4D version 3.5 and 4.0, and **now supports both Db2uCluster (deprecated) and Db2uInstance (current) custom resources**.

The role will copy a bash script (setupdb.sh) into the Db2 pod and execute it inside the container, performing configuration changes to the database and configuring tablespaces for Maximo Manage.

## Supported Db2 Custom Resources

- **Db2uCluster** (deprecated, maintained for backward compatibility)
- **Db2uInstance** (current, recommended for new deployments)

The role automatically detects which CR type is deployed and applies the appropriate configuration. No changes to your playbooks are required.

Role Variables
--------------
### db2_instance_name
The name of the Db2 instance to execute the setup in.

- **Required**
- Environment Variable: `DB2_INSTANCE_NAME`
- Default Value: None
- **Note**: Works with both Db2uCluster and Db2uInstance

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
- Default Value: `maximo`

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
Version of the enhanced DB2 parameters.

- **Required**
- Environment Variable: `DB2_CONFIG_VERSION`
- Default: `1.0.0`
- Supported versions: `1.0.0`

### enforce_db2_config
Flag to indicate whether to restart the DB2 instance to apply configuration changes.

- **Required**
- Environment Variable: `ENFORCE_DB2_CONFIG`
- Default: `True`
- **Warning**: Setting to `True` will cause downtime. Execute during maintenance window.

## CR Type Detection

The role automatically:
1. Queries for both Db2uCluster and Db2uInstance resources
2. Validates that exactly one CR type exists
3. Applies configuration appropriate for the detected CR type
4. Fails with clear error messages if:
   - No CR is found
   - Both CR types exist (invalid state)
   - CR is not in Ready state

## Example Playbooks

### Example 1: With Db2uCluster (Legacy)
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    db2_instance_name: mydb2-cluster
    db2_namespace: db2u
    db2_config_version: "1.0.0"
    enforce_db2_config: true
  roles:
    - ibm.mas_devops.suite_db2_setup_for_manage
```

### Example 2: With Db2uInstance (Current)
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    db2_instance_name: mydb2-instance
    db2_namespace: db2u
    db2_config_version: "1.0.0"
    enforce_db2_config: true
  roles:
    - ibm.mas_devops.suite_db2_setup_for_manage
```

**Note**: The playbook syntax is identical for both CR types. The role handles the differences automatically.

## Troubleshooting

### Error: "Both Db2uCluster and Db2uInstance resources exist"
This indicates an invalid state. Ensure only one CR type exists:
```bash
oc get db2ucluster -n <namespace>
oc get db2uinstance -n <namespace>
```
Delete the unwanted CR (Db2uInstance is recommended for new deployments).

### Error: "No Db2 instance found"
Verify the instance name and namespace:
```bash
oc get db2ucluster,db2uinstance -n <namespace>
```

### Configuration Not Applied
Check the ConfigMap to see if configuration was already applied:
```bash
oc get configmap <instance-name>-enforce-config -n <namespace> -o yaml
```


License
-------

EPL-2.0
