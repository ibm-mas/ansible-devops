cp4d_db2wh
==========

This role creates a Db2 Warehouse instance in Cloud Pak for Data.  A Db2 Warehouse cluster will be created and a public TLS encrypted route is configured to allow external access to the cluster.

### CloudPak for Data 3.5
The certificates are available from the `internal-tls` secret in the `cpd-meta-ops` namespace.  The default user is `db2inst1` and the password is available in the `instancepassword` secret in the same namespace.  You can examine the deployed resources in the `cpd-meta-ops` namespace:

```bash
oc -n cpd-meta-ops get cpdservice,db2ucluster

NAME                                                       MESSAGE                 REASON   STATUS       LASTACTION   PHASE        CODE
cpdservice.metaoperator.cpd.ibm.com/cpdservice-db2wh       Completed                        Ready        CPDInstall   Ready        0
cpdservice.metaoperator.cpd.ibm.com/cpdservice-db2wh-dmc   CPD binary is running            Installing   CPDInstall   Installing   1

NAME                                            STATE      AGE
db2ucluster.db2u.databases.ibm.com/db2u-bludb   NotReady   8m44s
```

#### Debugging Db2 install problems
The following command may come in handy:

```bash
oc -n cpd-meta-ops get formations.db2u.databases.ibm.com db2wh-db01 -o go-template='{{range .status.components}}{{printf "%s,%s,%s\n" .kind .name .status.state}}{{end}}' | column -s, -t
```


!!! tip
    The role will generate a yaml file containing the definition of a Secret and JdbcCfg resource that can be used to configure the deployed cluster as the MAS system JDBC datasource.

    This file can be directly applied using `oc apply -f /tmp/jdbccfg-cp4ddb2wh-system.yaml` or added to the `mas_config` list variable used by the `ibm.mas_devops.suite_install` role to deploy and configure MAS.


Role Variables
--------------

### db2wh_instance_name
Required.  Name of the database instance, note that this is the instance **name**, which is different from the instance **ID**.

- Environment Variable: `DB2WH_INSTANCE_NAME`
- Default: None

### db2wh_version
Version of the DB2 Warehouse instance to be created.

- Environment Variable: `DB2WH_VERSION`
- Default: `11.5.5.1-cn3-x86_64` (CloudPak for Data v3.5), `11.5.6.0-cn3` (CloudPak for Data v4)

### db2wh_table_org
The way database tables will be organized. It can be set to either `ROW` or `COLUMN`.

- Environment Variable: `DB2WH_TABLE_ORG`
- Default: `ROW`

### db2wh_meta_storage_class
Required for both CP4D v3.5 and CP4D v4.  Storage class used for metadata.

- Environment Variable: `DB2WH_META_STORAGE_CLASS`
- Default: None

### db2wh_meta_storage_size_gb
Size of the metadata persistent volume, in gigabytes

- Environment Variable: `DB2WH_META_STORAGE_SIZE_GB`
- Default: `20`

### db2wh_user_storage_class
Required for both CP4D v3.5 and CP4D v4.  Storage class used for user data.

- Environment Variable: `DB2WH_USER_STORAGE_CLASS`
- Default: None

### db2wh_user_storage_size_gb
Size of user persistent volume, in gigabytes.

- Environment Variable: `DB2WH_USER_STORAGE_SIZE_GB`
- Default: `100`

### db2wh_backup_storage_class
Required for both CP4D v3.5 and CP4D v4.  Storage class used for backup.

- Environment Variable: `DB2WH_BACKUP_STORAGE_CLASS`
- Default: None

### db2wh_backup_storage_size_gb
Size of backup persistent volume, in gigabytes.

- Environment Variable: `DB2WH_BACKUP_STORAGE_SIZE_GB`
- Default: `100`

### db2wh_logs_storage_class
Required for CP4D v4 only.  Storage class used for logs, not used with CP4D v3.5 databases.

- Environment Variable: `DB2WH_LOGS_STORAGE_CLASS`
- Default: None

### db2wh_logs_storage_size_gb
Size (in gigabytes) of logs persistent volume, not used with CP4D v3.5 databases.

- Environment Variable: `DB2WH_LOGS_STORAGE_SIZE_GB`
- Default: `100`

### db2wh_temp_storage_class
Required for CP4D v4 only.  Storage class used for temporary data, not used with CP4D v3.5 databases.

- Environment Variable: `DB2WH_TEMP_STORAGE_CLASS`
- Default: None

### db2wh_temp_storage_size_gb
Size (in gigabytes) of temporary persistent volume, not used with CP4D v3.5 databases.

- Environment Variable: `DB2WH_TEMP_STORAGE_SIZE_GB`
- Default: `100`

### db2wh_cpu_requests
Define the Kubernetes CPU request for the Db2 pod.  Only supported with CloudPak for Data v4.

- Environment Variable: `DB2WH_CPU_REQUESTS`
- Default: `2000m`

### db2wh_cpu_limits
Define the Kubernetes CPU limit for the Db2 pod.  Only supported with CloudPak for Data v4.

- Environment Variable: `DB2WH_CPU_LIMITS`
- Default: `4000m`

### db2wh_memory_requests
Define the Kubernetes memory request for the Db2 pod.  Only supported with CloudPak for Data v4.

- Environment Variable: `DB2WH_MEMORY_REQUESTS`
- Default: `6Gi`

### db2wh_memory_limits
Define the Kubernetes memory limit for the Db2 pod.  Only supported with CloudPak for Data v4.

- Environment Variable: `DB2WH_MEMORY_LIMITS`
- Default: `12Gi`

### cpd_api_username
Required for CP4D v3.5 only.  These credentials are used to call the REST API to create the database because CP4D v3.5 Kubernetes API is broken.  Yes, the default admin account for CP4D v3.5 really is set up as admin/password.

- Environment Variable: `CPD_API_USERNAME`
- Default: `admin`

### cpd_api_password
Required for CP4D v3.5 only.  These credentials are used to call the REST API to create the database because CP4D v3.5 Kubernetes API is broken.  Yes, the default admin account for CP4D v3.5 really is set up as admin/password.

- Environment Variable: `CPD_API_PASSWORD`
- Default: `password`

### mas_instance_id
Providing this and `mas_config_dir` will instruct the role to generate a JdbcCfg template that can be used to configure MAS to connect to this database.

- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

### mas_config_dir
Providing this and `mas_instance_id` will instruct the role to generate a JdbcCfg template that can be used to configure MAS to connect to this database.

- Environment Variable: `MAS_CONFIG_DIR`
- Default: None

### mas_config_scope
Supported values are `system`, `ws`, `app`, or `wsapp`, this is only used when both `mas_config_dir` and `mas_instance_id` are set.

- Environment Variable: `MAS_CONFIG_SCOPE`
- Default: `system`

### mas_workspace_id
This is only used when both `mas_config_dir` and `mas_instance_id` are set, and `mas_config_scope` is set to either `ws` or `wsapp`

- Environment Variable: `MAS_WORKSPACE_ID`
- Default: None

### mas_application_id
This is only used when both `mas_config_dir` and `mas_instance_id` are set, and `mas_config_scope` is set to either `app` or `wsapp`

- Environment Variable: `'MAS_APP_ID`
- Default: None

### db2wh_workload
The workload profile of the db2wh instance, possible values are 'PUREDATA_OLAP' or 'ANALYTICS'

- Environment Variable: `'DB2WH_WORKLOAD`
- Default: 'ANALYTICS'

### db2wh_node_label
The label used to specify node affinity and tolerations in the db2ucluster CR.

- Environment Variable: `'DB2WH_NODE_LABEL`
- Default: None

### db2wh_dedicated_node
The name of the worker node to apply the {{ db2wh_node_label }} taint and label to.

- Environment Variable: `'DB2WH_DEDICATED_NODE`
- Default: None

### db2wh_mln_count
The number of logical nodes (i.e. database partitions to create).

- Environment Variable: `'DB2WH_MLN_COUNT`
- Default: 1

### db2wh_num_pods
The number of db2 pods to create in the instance. Note that db2wh_num_pods must be less than or equal to db2wh_mln_count.
A single db2u pod can contain multiple logical nodes. So be sure to avoid specifying a large number for db2wh_mln_count while 
specifying a small number for db2wh_num_pods. If in doubt, make db2wh_mln_count = db2wh_num_pods. A slightly out of date reference
but still decent: https://www.ibm.com/docs/en/db2-warehouse?topic=SSCJDQ/com.ibm.swg.im.dashdb.ucontainer.doc/doc/db2w-mempernode-new.html

- Environment Variable: `'DB2WH_NUM_PODS`
- Default: 1

Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    # Create a Db2 instance in CPD v4.0
    db2wh_instance_name: db2wh-shared

    # Configure storage suitable for IBM Cloud ROKS
    db2wh_meta_storage_class: ibmc-file-silver-gid
    db2wh_user_storage_class: ibmc-file-gold-gid
    db2wh_backup_storage_class: ibmc-file-gold-gid
    db2wh_logs_storage_class: ibmc-file-silver-gid
    db2wh_temp_storage_class: ibmc-file-silver-gid

    # Create the MAS JdbcCfg & Secret resource definitions
    mas_instance_id: "{{ lookup('env', 'MAS_INSTANCE_ID') }}"
    mas_config_dir: "{{ lookup('env', 'MAS_CONFIG_DIR') }}"
  roles:
    - ibm.mas_devops.cp4d_db2wh
```

License
-------

EPL-2.0
