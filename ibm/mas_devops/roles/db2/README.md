db2u
==========

This role creates a Db2 Warehouse instance using the Db2u Operator. A namespace called `db2u` will be created and the db2u operator will be installed into the `ibm-common-services` namespace to service the `db2ucluster` requests in `db2u` namespace. A private root CA certificate is created and is used to secure the TLS connections to the database. A Db2 Warehouse cluster will be created along with a public TLS encrypted route to allow external access to the cluster (access is via the ssl-server nodeport port on the *-db2u-engn-svc service). Internal access is via the *-db2u-engn-svc service and port 50001. Both the external route and the internal service use the same server certificate.

The private root CA certificate and the server certificate are available from the `db2u-ca` and `db2u-certificate` secrets in the `db2u` namespace.  The default user is `db2inst1` and the password is available in the `instancepassword` secret in the same namespace.  You can examine the deployed resources in the `db2u` namespace:

```bash
oc -n db2u get db2ucluster

NAME        STATE   MAINTENANCESTATE   AGE
db2u-db01   Ready   None               29m
```

It typically takes 20-30 minutes from the db2ucluster being created till it is ready. If the db2ucluster is not ready after that period then check that all the PersistentVolumeClaims in the `db2u` namespace are ready and that the pods in the namespace are not stuck in init state. If the `c-<db2_instance_name>-db2u-0` pod is running then you can exec into the pod and check the `/var/log/db2u.log` for any issue.

If the `db2_node_label` and `db2_dedicated_node` variables are defined then role will taint and drain the dedicated node before labeling it using `database={{ db2_node_label }}`. The node is then uncordoned.

If the `mas_instance_id` and `mas_config_dir` are provided then the role will generate the JdbcCfg yaml that can be used to configure MAS to connect to this database. It does not apply the yaml to the cluster but does provide you with the yaml files to apply if needed.

Role Variables
--------------

### [required] db2_instance_name
Required.  Name of the database instance, note that this is the instance **name**.

- Environment Variable: `DB2_INSTANCE_NAME`
- Default: None

### [optional] db2_dbname
Name of the database within the instance.

- Environment Variable: `DB2_DBNAME`
- Default: `BLUDB`

### [optional] db2_version
Version of the DB2U operator instance to be created.

- Environment Variable: `DB2_VERSION`
- Default: `11.5.7.0-cn2`

### [optional] db2_4k_device_support
Whether 4K device support is turned on or not.

- Environment Variable: `DB2_4K_DEVICE_SUPPORT`
- Default: `ON`

### [optional] db2_table_org
The way database tables will be organized. It can be set to either `ROW` or `COLUMN`.

- Environment Variable: `DB2_TABLE_ORG`
- Default: `ROW`

### [required] db2_meta_storage_class
Storage class used for metadata. This must support ReadWriteMany

- Environment Variable: `DB2_META_STORAGE_CLASS`
- Default: Defaults to `ibmc-file-gold` if the storage class is available in the cluster.

### [optional] db2_meta_storage_size
Size of the metadata persistent volume, in gigabytes

- Environment Variable: `DB2_META_STORAGE_SIZE`
- Default: `20Gb`

### [required] db2_data_storage_class
Storage class used for user data. This must support ReadWriteOnce

- Environment Variable: `DB2_USER_STORAGE_CLASS`
- Default: Defaults to `ibmc-block-gold` if the storage class is available in the cluster.

### [optional] db2_data_storage_size
Size of data persistent volume.

- Environment Variable: `DB2_DATA_STORAGE_SIZE`
- Default: `100Gb`

### [optional] db2_backup_storage_class
Storage class used for backup. This must support ReadWriteMany

- Environment Variable: `DB2_BACKUP_STORAGE_CLASS`
- Default: Defaults to `ibmc-file-gold` if the storage class is available in the cluster.

### [optional] db2_backup_storage_size
Size of backup persistent volume.

- Environment Variable: `DB2_BACKUP_STORAGE_SIZE`
- Default: `100Gb`

### [optional] db2_logs_storage_class
Storage class used for transaction logs. This must support ReadWriteOnce

- Environment Variable: `DB2_LOGS_STORAGE_CLASS`
- Default: Defaults to `ibmc-block-gold` if the storage class is available in the cluster.

### [optional] db2_logs_storage_size
Size of transaction logs persistent volume.

- Environment Variable: `DB2_LOGS_STORAGE_SIZE`
- Default: `100Gb`

### [optional] db2_temp_storage_class
Storage class used for temporary data. This must support ReadWriteOnce

- Environment Variable: `DB2_TEMP_STORAGE_CLASS`
- Default: Defaults to `ibmc-block-gold` if the storage class is available in the cluster.

### [optional] db2_temp_storage_size
Size of temporary persistent volume.

- Environment Variable: `DB2_TEMP_STORAGE_SIZE`
- Default: `100Gb`

### [optional] db2_cpu_requests
Define the Kubernetes CPU request for the Db2 pod.

- Environment Variable: `DB2_CPU_REQUESTS`
- Default: `2000m`

### [optional] db2_cpu_limits
Define the Kubernetes CPU limit for the Db2 pod.

- Environment Variable: `DB2_CPU_LIMITS`
- Default: `4000m`

### [optional] db2_memory_requests
Define the Kubernetes memory request for the Db2 pod.

- Environment Variable: `DB2_MEMORY_REQUESTS`
- Default: `6Gi`

### [optional] db2_memory_limits
Define the Kubernetes memory limit for the Db2 pod.

- Environment Variable: `DB2_MEMORY_LIMITS`
- Default: `12Gi`

### [required] entitlement_key
Required.  This is the entitlement key used to install the Db2u Operator and Db2 images. Holds your IBM Entitlement key.

- Environment Variable: `ENTITLEMENT_KEY`
- Default: None

### [optional] mas_instance_id
Providing this and `mas_config_dir` will instruct the role to generate a JdbcCfg template that can be used to configure MAS to connect to this database.

- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

### [optional] mas_config_dir
Providing this and `mas_instance_id` will instruct the role to generate a JdbcCfg template that can be used to configure MAS to connect to this database.

- Environment Variable: `MAS_CONFIG_DIR`
- Default: None

### [optional] mas_config_scope
Supported values are `system`, `ws`, `app`, or `wsapp`, this is only used when both `mas_config_dir` and `mas_instance_id` are set.

- Environment Variable: `MAS_CONFIG_SCOPE`
- Default: `system`

### [optional] mas_workspace_id
This is only used when both `mas_config_dir` and `mas_instance_id` are set, and `mas_config_scope` is set to either `ws` or `wsapp`

- Environment Variable: `MAS_WORKSPACE_ID`
- Default: None

### [optional] mas_application_id
This is only used when both `mas_config_dir` and `mas_instance_id` are set, and `mas_config_scope` is set to either `app` or `wsapp`

- Environment Variable: `'MAS_APP_ID`
- Default: None

### [optional] db2_workload
The workload profile of the db2 instance, possible values are 'PUREDATA_OLAP' or 'ANALYTICS'

- Environment Variable: `'DB2_WORKLOAD`
- Default: 'ANALYTICS'

### db2_node_label
The label used to specify node affinity and tolerations in the db2ucluster CR.

- Environment Variable: `'DB2_NODE_LABEL`
- Default: None

### db2_dedicated_node
The name of the worker node to apply the {{ db2_node_label }} taint and label to.

- Environment Variable: `'DB2_DEDICATED_NODE`
- Default: None

### db2_mln_count
The number of logical nodes (i.e. database partitions to create). Note: ensure that the application using this DB2 can support DB2 MPP (which is created when DB2_MLN_COUNT is > 1). As of MAS 8.7 no MAS application supports MPP.

- Environment Variable: `'DB2_MLN_COUNT`
- Default: 1

### db2_num_pods
The number of Db2 pods to create in the instance. Note that `db2_num_pods` must be less than or equal to `db2_mln_count`.  A single db2u pod can contain multiple logical nodes. So be sure to avoid specifying a large number for `db2_mln_count` while specifying a small number for `db2_num_pods`. If in doubt, make `db2_mln_count = db2_num_pods`. For more information refer to the [Db2 documentation](https://www.ibm.com/docs/en/db2-warehouse?topic=SSCJDQ/com.ibm.swg.im.dashdb.ucontainer.doc/doc/db2w-mempernode-new.html).

- Environment Variable: `'DB2_NUM_PODS`
- Default: 1

Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    # Configuration for the Db2 cluster
    db2_version: 11.5.7.0-cn2
    db2_instance_name: db2u-db01
    db2_dbname: BLUDB

    db2_meta_storage_class: "ibmc-file-gold"
    db2_data_storage_class: "ibmc-block-gold"
    db2_backup_storage_class: "ibmc-file-gold"
    db2_logs_storage_class: "ibmc-block-gold"
    db2_temp_storage_class: "ibmc-block-gold"

    entitlement_key: "{{ lookup('env', 'ENTITLEMENT_KEY') }}"

    # Create the MAS JdbcCfg & Secret resource definitions
    mas_instance_id: "{{ lookup('env', 'MAS_INSTANCE_ID') }}"
    mas_config_dir: "{{ lookup('env', 'MAS_CONFIG_DIR') }}"
  roles:
    - ibm.mas_devops.db2u
```

License
-------

EPL-2.0
