db2u
==========

This role creates a Db2 Warehouse instance using the Db2u Operator. A namespace called `db2u` will be created and the db2u operator will be installed into the `ibm-common-services` namespace to service the `db2ucluster` requests in `db2u` namespace. A self-signed certificate is created and a Db2 Warehouse cluster will be created along with a public TLS encrypted route is configured to allow external access to the cluster (access is via port 443 on the route).

The certificates are available from the `db2u-ca` and `db2u-certificate` secrets in the `db2u` namespace.  The default user is `db2inst1` and the password is available in the `instancepassword` secret in the same namespace.  You can examine the deployed resources in the `db2u` namespace:

```bash
oc -n db2u get db2ucluster

NAME        STATE   MAINTENANCESTATE   AGE
db2u-db01   Ready   None               29m
```

It typically takes 20-30 minutes from the db2ucluster being created till it is ready. If the db2ucluster is not ready after that period then check that all the PersistentVolumeClaims in the `db2u` namespace are ready and that the pods in the namespace are not stuck in init state. If the `c-<db2u_instance_name>-db2u-0` pod is running then you can exec into the pod and check the `/var/log/db2u.log` for any issue.

If the `db2u_node_label` and `db2u_dedicated_node` variables are defined then role will taint and drain the dedicated node before labeling it using `database={{ db2u_node_label }}`. The node is then uncordoned.

Role Variables
--------------

### [required] db2u_instance_name
Required.  Name of the database instance, note that this is the instance **name**, which is different from the instance **ID**.

- Environment Variable: `DB2U_INSTANCE_NAME`
- Default: None

### [optional] db2u_dbname
Name of the database within the instance.

- Environment Variable: `DB2U_DBNAME`
- Default: `BLUDB`

### [optional] db2u_version
Version of the DB2U operator instance to be created.

- Environment Variable: `DB2U_VERSION`
- Default: `11.5.7.0-cn2`

### [optional] db2u_4k_device_support
Whether 4K device support is turned on or not.

- Environment Variable: `DB2U_4K_DEVICE_SUPPORT`
- Default: `ON`

### [optional] db2u_table_org
The way database tables will be organized. It can be set to either `ROW` or `COLUMN`.

- Environment Variable: `DB2U_TABLE_ORG`
- Default: `ROW`

### [required] db2u_meta_storage_class
Storage class used for metadata. This must support ReadWriteMany

- Environment Variable: `DB2U_META_STORAGE_CLASS`
- Default: None

### [optional] db2u_meta_storage_size_gb
Size of the metadata persistent volume, in gigabytes

- Environment Variable: `DB2U_META_STORAGE_SIZE_GB`
- Default: `20`

### [required] db2u_data_storage_class
Storage class used for user data. This must support ReadWriteOnce

- Environment Variable: `DB2U_USER_STORAGE_CLASS`
- Default: None

### [optional] db2u_user_storage_size_gb
Size of user persistent volume, in gigabytes.

- Environment Variable: `DB2U_USER_STORAGE_SIZE_GB`
- Default: `100`

### [optional] db2u_backup_storage_class
Storage class used for backup. This must support ReadWriteMany

- Environment Variable: `DB2U_BACKUP_STORAGE_CLASS`
- Default: None

### [optional] db2u_backup_storage_size_gb
Size of backup persistent volume, in gigabytes.

- Environment Variable: `DB2U_BACKUP_STORAGE_SIZE_GB`
- Default: `100`

### [optional] db2u_logs_storage_class
Storage class used for transaction logs. This must support ReadWriteOnce

- Environment Variable: `DB2U_LOGS_STORAGE_CLASS`
- Default: None

### [optional] db2u_logs_storage_size_gb
Size (in gigabytes) of transaction logs persistent volume.

- Environment Variable: `DB2U_LOGS_STORAGE_SIZE_GB`
- Default: `100`

### [optional] db2u_temp_storage_class
Storage class used for temporary data. This must support ReadWriteOnce

- Environment Variable: `DB2U_TEMP_STORAGE_CLASS`
- Default: None

### [optional] db2u_temp_storage_size_gb
Size (in gigabytes) of temporary persistent volume.

- Environment Variable: `DB2U_TEMP_STORAGE_SIZE_GB`
- Default: `100`

### [optional] db2u_cpu_requests
Define the Kubernetes CPU request for the Db2 pod.

- Environment Variable: `DB2U_CPU_REQUESTS`
- Default: `2000m`

### [optional] db2u_cpu_limits
Define the Kubernetes CPU limit for the Db2 pod.

- Environment Variable: `DB2U_CPU_LIMITS`
- Default: `4000m`

### [optional] db2u_memory_requests
Define the Kubernetes memory request for the Db2 pod.

- Environment Variable: `DB2U_MEMORY_REQUESTS`
- Default: `6Gi`

### [optional] db2u_memory_limits
Define the Kubernetes memory limit for the Db2 pod.

- Environment Variable: `DB2U_MEMORY_LIMITS`
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

### [optional] db2u_workload
The workload profile of the db2 instance, possible values are 'PUREDATA_OLAP' or 'ANALYTICS'

- Environment Variable: `'DB2U_WORKLOAD`
- Default: 'ANALYTICS'

### db2u_node_label
The label used to specify node affinity and tolerations in the db2ucluster CR.

- Environment Variable: `'DB2U_NODE_LABEL`
- Default: None

### db2u_dedicated_node
The name of the worker node to apply the {{ db2u_node_label }} taint and label to.

- Environment Variable: `'DB2U_DEDICATED_NODE`
- Default: None

### db2u_mln_count
The number of logical nodes (i.e. database partitions to create).

- Environment Variable: `'DB2U_MLN_COUNT`
- Default: 1

### db2u_num_pods
The number of Db2 pods to create in the instance. Note that `db2u_num_pods` must be less than or equal to `db2u_mln_count`.  A single db2u pod can contain multiple logical nodes. So be sure to avoid specifying a large number for `db2u_mln_count` while specifying a small number for `db2u_num_pods`. If in doubt, make `db2u_mln_count = db2u_num_pods`. For more information refer to the [Db2 documentation](https://www.ibm.com/docs/en/db2-warehouse?topic=SSCJDQ/com.ibm.swg.im.dashdb.ucontainer.doc/doc/db2w-mempernode-new.html).

- Environment Variable: `'DB2U_NUM_PODS`
- Default: 1

Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    # Configuration for the Db2 cluster
    db2u_version: 11.5.7.0-cn2
    db2u_instance_name: db2u-db01
    db2u_dbname: BLUDB

    db2u_meta_storage_class: "ibmc-file-gold"
    db2u_data_storage_class: "ibmc-block-gold"
    db2u_backup_storage_class: "ibmc-file-gold"
    db2u_logs_storage_class: "ibmc-block-gold"
    db2u_temp_storage_class: "ibmc-block-gold"

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
