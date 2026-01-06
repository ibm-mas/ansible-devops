db2
===============================================================================

This role creates or upgrades a Db2 instance using the Db2u Operator. When installing db2, the db2u operator will now be installed into the same namespace as the db2 instance (`db2ucluster`). If you already have db2 operator and db2 instances running in separate namespaces, this role will take care of migrating (by deleting & reinstalling) the db2 operators from `ibm-common-services` to the namespace defined by `db2_namespace` property (in case of a new role execution for a db2 install or db2 upgrade). A private root CA certificate is created and is used to secure the TLS connections to the database. A Db2 Warehouse cluster will be created along with a public TLS encrypted route to allow external access to the cluster (access is via the ssl-server nodeport port on the *-db2u-engn-svc service). Internal access is via the *-db2u-engn-svc service and port 50001. Both the external route and the internal service use the same server certificate.

The private root CA certificate and the server certificate are available from the `db2u-ca` and `db2u-certificate` secrets in the db2 namespace.  The default user is `db2inst1` and the password is available in the `instancepassword` secret in the same namespace.  You can examine the deployed resources in the db2 namespace. This example assumes the default namespace `db2u`:

```bash
oc -n db2u get db2ucluster

NAME        STATE   MAINTENANCESTATE   AGE
db2u-db01   Ready   None               29m
```

It typically takes 20-30 minutes from the db2ucluster being created till it is ready. If the db2ucluster is not ready after that period then check that all the PersistentVolumeClaims in the db2 namespace are ready and that the pods in the namespace are not stuck in init state. If the `c-<db2_instance_name>-db2u-0` pod is running then you can exec into the pod and check the `/var/log/db2u.log` for any issue.

If the `mas_instance_id` and `mas_config_dir` are provided then the role will generate the JdbcCfg yaml that can be used to configure MAS to connect to this database. It does not apply the yaml to the cluster but does provide you with the yaml files to apply if needed.

When upgrading db2, specify the existing namespace where the `db2uCluster` instances exist. All the instances under that namespace will be upgraded to the db2 version specified. The version of db2 **must** match the channel of db2 being used for the upgrade.


Role Variables - Installation
-------------------------------------------------------------------------------
### common_services_namespace
Namespace where IBM Common Services is installed.

- Optional
- Environment Variable: `COMMON_SERVICES_NAMESPACE`
- Default Value: `ibm-common-services`

### db2_action
Inform the role whether to perform an install, upgrade, backup or restore of DB2 Database. This can be set to `install`, `upgrade`, `backup` or `restore`. When `DB2_ACTION` is set to upgrade, then all instances in the `DB2_NAMESPACE` will be upgraded to the `DB2_VERSION`.

- Optional
- Environment Variable: `DB2_ACTION`
- Default: `install`

### db2_namespace
Name of the namespace where Db2 operators and Db2 instances (DB2UCluster custom resources) will be created

- Optional
- Environment Variable: `DB2_NAMESPACE`
- Default: `db2u`

### db2_channel
The subscription channel for the DB2 Universal Operator.

- Optional
- Environment Variable: `DB2_CHANNEL`
- Default: The default channel, as defined in the operator package, will be used if this is not set.

### db2_instance_name
Name of the database instance, note that this is the instance **name**.

- **Required**
- Environment Variable: `DB2_INSTANCE_NAME`
- Default: None

### ibm_entitlement_key
Provide your [IBM entitlement key](https://myibm.ibm.com/products-services/containerlibrary).

- **Required**
- Environment Variable: `IBM_ENTITLEMENT_KEY`
- Default: None

### db2_dbname
Name of the database within the instance.

- Optional
- Environment Variable: `DB2_DBNAME`
- Default: `BLUDB`

### db2_version
Version of the DB2 engine to be used while creating/upgrading the DB2 instances.

- Optional
- Environment Variable: `DB2_VERSION`
- Default: The default db2 engine version will be automatically defined to the latest version supported by the installed DB2 operator if this is not set. The DB2 engine versions supported by the installed DB2 operator are stored in `db2u-release` configmap under `ibm-common-services` namespace.

### db2_type
Type of the DB2 instance. Available options are `db2wh` and `db2oltp`.

- Optional
- Environment Variable: `DB2_TYPE`
- Default: `db2wh`

### db2_timezone
Server timezone code of the DB2 instance. If you want to align the same timezone with Manage's DB2 database, you also need to must also set `MAS_APP_SETTINGS_SERVER_TIMEZONE` variable to the same value.

- Optional
- Environment Variable: `DB2_TIMEZONE`
- Default: `GMT`

### db2_4k_device_support
Whether 4K device support is turned on or not.

- Optional
- Environment Variable: `DB2_4K_DEVICE_SUPPORT`
- Default: `ON`

### db2_workload
The workload profile of the db2 instance, possible values are `PUREDATA_OLAP` or `ANALYTICS`.

- Optional
- Environment Variable: `DB2_WORKLOAD`
- Default: `ANALYTICS`

### db2_table_org
The way database tables will be organized. It can be set to either `ROW` or `COLUMN`.

- Optional
- Environment Variable: `DB2_TABLE_ORG`
- Default: `ROW`

### db2_ldap_username
Define the username of db2 in the local LDAP registry. If this is defined, the LDAP user will be the user identity passed into the MAS JDBC configuration.

- Optional
- Environment Variable: `DB2_LDAP_USERNAME`
- Default: None

### db2_ldap_password
Define the password of above db2 user in the local LDAP registry. Must define when `db2_ldap_username` is used.

- Optional
- Environment Variable: `DB2_LDAP_PASSWORD`
- Default: None

### db2_rotate_password
Determines if the role should rotate the LDAP password for current LDAP user configured within Db2 for MAS. When using this capability, LDAP user password will auto generated by this role and configured with MAS.

- Optional
- Environment Variable: `DB2_LDAP_ROTATE_PASSWORD`
- Default: False


Role Variables - Storage
-------------------------------------------------------------------------------
We recommend reviewing the Db2 documentation about the certified storage options for Db2 on Red Hat OpenShift. Please ensure your storage class meets the specified deployment requirements for Db2. [https://www.ibm.com/docs/en/db2/11.5?topic=storage-certified-options](https://www.ibm.com/docs/en/db2/11.5?topic=storage-certified-options)

### db2_meta_storage_class
Storage class used for metadata. This must support ReadWriteMany(RWX) access mode.

- **Required**
- Environment Variable: `DB2_META_STORAGE_CLASS`
- Default: Defaults to `ibmc-file-gold` if the storage class is available in the cluster.

### db2_meta_storage_size
Size of the metadata persistent volume, in gigabytes

- Optional
- Environment Variable: `DB2_META_STORAGE_SIZE`
- Default: `10Gi`

### db2_meta_storage_accessmode
The access mode for the storage.

- Optional
- Environment Variable: `DB2_META_STORAGE_ACCESSMODE`
- Default: `ReadWriteMany`

### db2_data_storage_class
Storage class used for user data. This must support ReadWriteOnce(RWO) access mode.

- **Required**
- Environment Variable: `DB2_DATA_STORAGE_CLASS`
- Default: Defaults to `ibmc-block-gold` if the storage class is available in the cluster.

### db2_data_storage_size
Size of data persistent volume.

- Optional
- Environment Variable: `DB2_DATA_STORAGE_SIZE`
- Default: `50Gi`

### db2_data_storage_accessmode
The access mode for the storage.

- Optional
- Environment Variable: `DB2_DATA_STORAGE_ACCESSMODE`
- Default: `ReadWriteOnce`

### db2_backup_storage_class
Storage class used for backup. This must support ReadWriteMany(RWX) access mode.

- Optional
- Environment Variable: `DB2_BACKUP_STORAGE_CLASS`
- Default: Defaults to `ibmc-file-gold` if the storage class is available in the cluster. Set to `None` will drop the backup storage on DB2ucluster CR.

### db2_backup_storage_size
Size of backup persistent volume.

- Optional
- Environment Variable: `DB2_BACKUP_STORAGE_SIZE`
- Default: `50Gi`

### db2_backup_storage_accessmode
The access mode for the storage.

- Optional
- Environment Variable: `DB2_BACKUP_STORAGE_ACCESSMODE`
- Default: `ReadWriteMany`

### db2_logs_storage_class
Storage class used for transaction logs. This must support ReadWriteOnce(RWO) access mode.

- Optional
- Environment Variable: `DB2_LOGS_STORAGE_CLASS`
- Default: Defaults to `ibmc-block-gold` if the storage class is available in the cluster. Set to `None` will drop the logs storage on DB2ucluster CR.

### db2_logs_storage_size
Size of transaction logs persistent volume.

- Optional
- Environment Variable: `DB2_LOGS_STORAGE_SIZE`
- Default: `10Gi`

### db2_logs_storage_accessmode
The access mode for the storage.

- Optional
- Environment Variable: `DB2_LOGS_STORAGE_ACCESSMODE`
- Default: `ReadWriteOnce`

### db2_temp_storage_class
Storage class used for temporary data. This must support ReadWriteMany(RWX) access mode.

- Optional
- Environment Variable: `DB2_TEMP_STORAGE_CLASS`
- Default: Defaults to `ibmc-block-gold` if the storage class is available in the cluster. Set to `None` will drop the tempts storage on DB2ucluster CR.

### db2_temp_storage_size
Size of temporary persistent volume.

- Optional
- Environment Variable: `DB2_TEMP_STORAGE_SIZE`
- Default: `10Gi`

### db2_temp_storage_accessmode
The access mode for the storage. This must support ReadWriteOnce(RWO) access mode.

- Optional
- Environment Variable: `DB2_TEMP_STORAGE_ACCESSMODE`
- Default: `ReadWriteOnce`


Role Variables - Resource Requests
-----------------------------------------------------------------------------------------------------------------
These variables allow you to customize the resources available to the Db2 pod in your cluster.  In most circumstances you will want to set these properties because it's impossible for us to provide a default value that will be appropriate for all users.  We have set defaults that are suitable for deploying Db2 onto a dedicated worker node with 4cpu and 16gb memory.

!!! tip
    Note that you must take into account the system overhead on any given node when setting these parameters, if you set the requests equal to the number of CPU or amount of memory on your node then the scheduler will not be able to schedule the Db2 pod because not 100% of the worker nodes' resource will be available to pod on that node, even if there's only a single pod on it.

    Db2 is sensitive to both CPU and memory issues, particularly memory, we recommend setting requests and limits to the same values, ensuring the scheduler always reserves the resources that Db2 expects to be available to it.

### db2_cpu_requests
Define the Kubernetes CPU request for the Db2 pod.

- Optional
- Environment Variable: `DB2_CPU_REQUESTS`
- Default: `4000m`

### db2_cpu_limits
Define the Kubernetes CPU limit for the Db2 pod.

- Optional
- Environment Variable: `DB2_CPU_LIMITS`
- Default: `6000m`

### db2_memory_requests
Define the Kubernetes memory request for the Db2 pod.

- Optional
- Environment Variable: `DB2_MEMORY_REQUESTS`
- Default: `8Gi`

### db2_memory_limits
Define the Kubernetes memory limit for the Db2 pod.

- Optional
- Environment Variable: `DB2_MEMORY_LIMITS`
- Default: `16Gi`


Role Variables - Node Label Affinity
-----------------------------------------------------------------------------------------------------------------
Specify both `db2_affinity_key` and `db2_affinity_value` to configure `requiredDuringSchedulingIgnoredDuringExecution` affinity with appropriately labelled nodes.

### db2_affinity_key
Specify the key of a node label to declare affinity with.

- Optional
- Environment Variable: `DB2_AFFINITY_KEY`
- Default: None

### db2_affinity_value
Specify the value of a node label to declare affinity with.

- Optional
- Environment Variable: `DB2_AFFINITY_VALUE`
- Default: None


Role Variables - Node Taint Toleration
-----------------------------------------------------------------------------------------------------------------
Specify `db2_tolerate_key`, `db2_tolerate_value`, and `db2_tolerate_effect` to configure a toleration policy to allow the db2 instance to be scheduled on nodes with the specified taint.

### db2_tolerate_key
Specify the key of the taint that is to be tolerated.

- Optional
- Environment Variable: `DB2_TOLERATE_KEY`
- Default: None

### db2_tolerate_value
Specify the value of the taint that is to be tolerated.

- Optional
- Environment Variable: `DB2_TOLERATE_VALUE`
- Default: None

### db2_tolerate_effect
Specify the type of taint effect that will be tolerated (`NoSchedule`, `PreferNoSchedule`, or `NoExecute`).

- Optional
- Environment Variable: `DB2_TOLERATE_EFFECT`
- Default: None


Role Variables - DB2UCluster Database Configuration Settings
-----------------------------------------------------------------------------------------------------------------
The following variables will overwrite DB2UCluster default properties for the DB2 configuration sections:

- `spec.environment.database.dbConfig`
- `spec.environment.instance.dbmConfig`
- `spec.environment.instance.registry`

### db2_database_db_config
Overwrites the db2ucluster database configuration settings under `spec.environment.database.dbConfig` section.
- Optional
- Environment Variable: `DB2_DATABASE_DB_CONFIG`
- Default: None

### db2_instance_dbm_config
Overwrites the db2ucluster instance database configuration settings under `spec.environment.instance.dbmConfig` section.

!!! important
    Do not set [instance_memory](https://www.ibm.com/docs/en/db2/11.5?topic=parameters-instance-memory-instance-memory).  The Db2 engine does not know Db2 is running inside a container, setting `dbmConfig.INSTANCE_MEMORY: automatic` will cause it to read the cgroups of the node and potentially go beyond the pod memory limit.  Db2U has logic built in to use a normalized percentage that takes into account the memory limit and free memory of the node.

- Optional
- Environment Variable: `DB2_INSTANCE_DBM_CONFIG`
- Default: None

### db2_instance_registry
Overwrites the db2ucluster instance database configuration settings under `spec.environment.instance.registry` section.
You can define parameters to be included in this section using semicolon separated values.

- Optional
- Environment Variable: `DB2_INSTANCE_REGISTRY`
- Default: None


Role Variables - MPP System
----------------------------------------------------------------------------------------------------------
!!! warning
    Do not use these variables if you intend to use the Db2 instance with IBM Maximo Application Suite; no MAS application supports Db2 MPP

### db2_mln_count
The number of logical nodes (i.e. database partitions to create). Note: ensure that the application using this Db2 can support Db2 MPP (which is created when `DB2_MLN_COUNT` is greater than 1).

- Optional
- Environment Variable: `'DB2_MLN_COUNT`
- Default: 1

### db2_num_pods
The number of Db2 pods to create in the instance. Note that `db2_num_pods` must be less than or equal to `db2_mln_count`.  A single db2u pod can contain multiple logical nodes. So be sure to avoid specifying a large number for `db2_mln_count` while specifying a small number for `db2_num_pods`. If in doubt, make `db2_mln_count = db2_num_pods`. For more information refer to the [Db2 documentation](https://www.ibm.com/docs/en/db2-warehouse?topic=SSCJDQ/com.ibm.swg.im.dashdb.ucontainer.doc/doc/db2w-mempernode-new.html).

- Optional
- Environment Variable: `'DB2_NUM_PODS`
- Default: 1



Role Variables - MAS Configuration
-----------------------------------------------------------------------------------------------------------------
### mas_instance_id
Providing this and `mas_config_dir` will instruct the role to generate a JdbcCfg template that can be used to configure MAS to connect to this database.

- Optional
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

### mas_config_dir
Providing this and `mas_instance_id` will instruct the role to generate a JdbcCfg template that can be used to configure MAS to connect to this database.

- Optional
- Environment Variable: `MAS_CONFIG_DIR`
- Default: None

### mas_config_scope
Supported values are `system`, `ws`, `app`, or `wsapp`, this is only used when both `mas_config_dir` and `mas_instance_id` are set.

- Optional
- Environment Variable: `MAS_CONFIG_SCOPE`
- Default: `system`

### mas_workspace_id
This is only used when both `mas_config_dir` and `mas_instance_id` are set, and `mas_config_scope` is set to either `ws` or `wsapp`

- Optional
- Environment Variable: `MAS_WORKSPACE_ID`
- Default: None

### mas_application_id
This is only used when both `mas_config_dir` and `mas_instance_id` are set, and `mas_config_scope` is set to either `app` or `wsapp`

- Optional
- Environment Variable: `'MAS_APP_ID`
- Default: None


Role Variables - Backup and Restore
-------------------------------------------------------------------------------

### db2_action
When set to `backup` or `restore`, the role will perform backup or restore operations on the DB2 instance and database.

- Optional
- Environment Variable: `DB2_ACTION`
- Default: `install`
- Supported values: `install`, `upgrade`, `backup`, `restore`

### mas_backup_dir
The local directory path where backup files will be stored (for backup) or read from (for restore).

- **Required** for backup and restore operations
- Environment Variable: `MAS_BACKUP_DIR`
- Default: None
- Example: `/tmp/mas_backups`

### db2_backup_version
Version identifier for the backup. For backup operations, if not provided, it defaults to `YYMMDD-HHMMSS` format. For restore operations, this is required to identify which backup to restore.

- Optional for backup (auto-generated if not provided)
- **Required** for restore
- Environment Variable: `DB2_BACKUP_VERSION`
- Default: Auto-generated timestamp in `YYMMDD-HHMMSS` format for backup operations

### br_skip_instance
Set to `true` to skip backing up or restoring the DB2 instance Kubernetes resources (only backup/restore the database data).

- Optional
- Environment Variable: `BR_SKIP_INSTANCE`
- Default: `false`

### backup_vendor
Specifies where the database backup will be stored or retrieved from.

- Optional
- Environment Variable: `BACKUP_VENDOR`
- Default: `s3`
- Supported values: `s3`, `disk`

### backup_type
Type of database backup to perform.

- Optional
- Environment Variable: `DB2_BACKUP_TYPE`
- Default: `online`
- Supported values: `online`, `offline`

### backup_s3_alias
Alias name for the S3 storage configuration in DB2.

- **Required** when `backup_vendor=s3`
- Environment Variable: `BACKUP_S3_ALIAS`
- Default: `S3DB2COS`

### backup_s3_endpoint
S3-compatible storage endpoint URL.

- **Required** when `backup_vendor=s3`
- Environment Variable: `BACKUP_S3_ENDPOINT`
- Default: None
- Example: `https://s3.us-east.cloud-object-storage.appdomain.cloud`

### backup_s3_bucket
S3 bucket name where backups will be stored.

- **Required** when `backup_vendor=s3`
- Environment Variable: `BACKUP_S3_BUCKET`
- Default: None

### backup_s3_access_key
S3 access key for authentication.

- **Required** when `backup_vendor=s3`
- Environment Variable: `BACKUP_S3_ACCESS_KEY`
- Default: None

### backup_s3_secret_key
S3 secret key for authentication.

- **Required** when `backup_vendor=s3`
- Environment Variable: `BACKUP_S3_SECRET_KEY`
- Default: None


Backup and Restore Operations
-------------------------------------------------------------------------------

### Overview
The DB2 role supports comprehensive backup and restore operations for both DB2 instance configuration and database data. The backup process creates a complete snapshot that can be used to restore the DB2 instance to a previous state.

### Backup Components
The backup operation consists of two main components:

1. **Instance Backup**: Backs up Kubernetes resources including:
   - DB2UCluster custom resource
   - Secrets (instance password, LDAP credentials if configured)
   - ConfigMaps
   - Other DB2 instance metadata

2. **Database Backup**: Backs up the actual database data using DB2's native backup utilities

### Backup Process

#### Prerequisites
- DB2 instance must be running and healthy
- Sufficient storage space in the backup location
- For S3 backups: Valid S3 credentials and accessible S3 bucket
- For disk backups: Sufficient local disk space

#### Backup Workflow
1. **Validation**: Verifies all required variables are set
2. **Instance Backup** (unless `BR_SKIP_INSTANCE=true`):
   - Exports DB2UCluster CR and related Kubernetes resources
   - Saves instance configuration and secrets
3. **Database Backup**:
   - Prepares backup scripts and copies them to the DB2 pod
   - For S3: Configures S3 storage access in DB2
   - Executes DB2 backup command (online or offline)
   - For disk backups: Copies backup files to local storage
   - Creates `db2-backup-info.yaml` with backup metadata

#### Backup Storage Locations
- **S3**: `s3://<bucket>/backups-db2/<backup_version>/`
- **Disk**: `<mas_backup_dir>/backup-<backup_version>-db2u/data/`

### Restore Process

#### Prerequisites
- Valid backup files exist in the specified location
- For instance restore: DB2 operator must be installed
- For database restore: DB2 instance must be running with matching version
- For S3 restores: Valid S3 credentials and accessible S3 bucket

#### Restore Workflow
1. **Validation**: Verifies backup version and required variables
2. **Instance Restore** (unless `BR_SKIP_INSTANCE=true`):
   - Checks if DB2 instance exists and is healthy
   - If not present or unhealthy: Creates new instance from backup configuration
   - Restores secrets and configuration
3. **Database Restore**:
   - For disk: Validates DB2 version matches backup version
   - Prepares restore scripts
   - For S3: Configures S3 storage access
   - For disk: Copies backup archive to DB2 pod
   - Executes DB2 restore command
   - Validates restore completion

### Backup Metadata
Each backup creates a `db2-backup-info.yaml` file containing:
```yaml
source_db2_backup_version: "241225-143022"
source_db2_backup_timestamp: "20241225143022"
source_db2_instance_name: "db2u-manage"
source_db2_instance_version: "11.5.8.0-cn7"
database: "BLUDB"
backup_vendor: "s3"
vendor_backup_path: "DB2REMOTE://S3DB2COS/my-bucket/backups-db2/241225-143022"
status: "SUCCESS"
```

### Example: Backup to S3
```bash
export DB2_ACTION=backup
export MAS_INSTANCE_ID=inst1
export MAS_BACKUP_DIR=/tmp/mas_backups
export DB2_INSTANCE_NAME=db2u-manage
export DB2_NAMESPACE=db2u
export BACKUP_VENDOR=s3
export BACKUP_S3_ENDPOINT=https://s3.us-east.cloud-object-storage.appdomain.cloud
export BACKUP_S3_BUCKET=mas-db2-backups
export BACKUP_S3_ACCESS_KEY=<access_key>
export BACKUP_S3_SECRET_KEY=<secret_key>
export DB2_BACKUP_TYPE=online

ansible-playbook ibm.mas_devops.br_db2
```

### Example: Backup to Disk
```bash
export DB2_ACTION=backup
export MAS_INSTANCE_ID=inst1
export MAS_BACKUP_DIR=/tmp/mas_backups
export DB2_INSTANCE_NAME=db2u-manage
export DB2_NAMESPACE=db2u
export BACKUP_VENDOR=disk
export DB2_BACKUP_TYPE=online

ansible-playbook ibm.mas_devops.br_db2
```

### Example: Restore from S3
```bash
export DB2_ACTION=restore
export MAS_INSTANCE_ID=inst1
export MAS_BACKUP_DIR=/tmp/mas_backups
export DB2_INSTANCE_NAME=db2u-manage
export DB2_NAMESPACE=db2u
export DB2_BACKUP_VERSION=241225-143022
export BACKUP_VENDOR=s3
export BACKUP_S3_ENDPOINT=https://s3.us-east.cloud-object-storage.appdomain.cloud
export BACKUP_S3_BUCKET=mas-db2-backups
export BACKUP_S3_ACCESS_KEY=<access_key>
export BACKUP_S3_SECRET_KEY=<secret_key>

ansible-playbook ibm.mas_devops.br_db2
```

### Example: Restore from Disk
```bash
export DB2_ACTION=restore
export MAS_INSTANCE_ID=inst1
export MAS_BACKUP_DIR=/tmp/mas_backups
export DB2_INSTANCE_NAME=db2u-manage
export DB2_NAMESPACE=db2u
export DB2_BACKUP_VERSION=241225-143022
export BACKUP_VENDOR=disk

ansible-playbook ibm.mas_devops.br_db2
```

### Example: Database-Only Backup (Skip Instance)
```bash
export DB2_ACTION=backup
export MAS_INSTANCE_ID=inst1
export MAS_BACKUP_DIR=/tmp/mas_backups
export DB2_INSTANCE_NAME=db2u-manage
export DB2_NAMESPACE=db2u
export BR_SKIP_INSTANCE=true
export BACKUP_VENDOR=s3
export BACKUP_S3_ENDPOINT=https://s3.us-east.cloud-object-storage.appdomain.cloud
export BACKUP_S3_BUCKET=mas-db2-backups
export BACKUP_S3_ACCESS_KEY=<access_key>
export BACKUP_S3_SECRET_KEY=<secret_key>

ansible-playbook ibm.mas_devops.br_db2
```

### Backup Types

#### Online Backup
- Database remains available during backup
- Recommended for production environments
- Requires archive logging to be enabled
- Set `DB2_BACKUP_TYPE=online`

#### Offline Backup
- Database is taken offline during backup
- Faster than online backup
- Requires downtime
- Set `DB2_BACKUP_TYPE=offline`

### Important Notes

1. **Version Compatibility**: The DB2 version of the restore target must match the backup source version
2. **Storage Requirements**: Ensure sufficient storage space for backups (typically 1-2x database size)
3. **S3 Credentials**: Keep S3 credentials secure and use appropriate IAM policies
4. **Backup Retention**: Implement a backup retention policy to manage storage costs
5. **Testing**: Regularly test restore procedures to ensure backup integrity
6. **Archive Logging**: For online backups, ensure DB2 archive logging is properly configured
7. **Network Connectivity**: For S3 backups, ensure DB2 pod has network access to S3 endpoint

### Troubleshooting

#### Backup Failures
- Check DB2 pod logs: `oc logs -n <namespace> <db2-pod-name> -c db2u`
- Review backup script logs in the pod: `/tmp/db2_backup.log`
- Verify S3 credentials and connectivity (for S3 backups)
- Ensure sufficient storage space

#### Restore Failures
- Verify backup version exists and is complete
- Check DB2 version compatibility
- Review restore script logs: `/tmp/db2_restore_disk.log` or `/tmp/db2_restore_s3.log`
- Ensure DB2 instance is running and healthy before database restore
- For S3 restores, verify S3 connectivity and credentials


License
-------------------------------------------------------------------------------

EPL-2.0
