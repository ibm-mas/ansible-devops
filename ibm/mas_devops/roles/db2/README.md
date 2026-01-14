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

### mas_backup_dir
Local directory path where backups will be stored or restored from.

- **Required** for backup and restore operations
- Environment Variable: `MAS_BACKUP_DIR`
- Default: None
- Example: `/tmp/mas_backups`

### db2_backup_version
The backup version timestamp to restore from. This is automatically generated during backup in the format `YYMMDD-HHMMSS`.

- **Required** for restore operations
- Environment Variable: `DB2_BACKUP_VERSION`
- Default: Auto-generated for backup operations
- Example: `251212-021316`

### backup_type
Type of backup to perform. Online backups keep the database available during backup, while offline backups require database downtime but are faster.
If your DB2 instance has got circular logging enabled i.e `LOGARCHMETH1: OFF or/and LOGARCHMETH2: OFF`, you can only use `offline` backup type. 
If your DB2 instance has got circular logging disabled, you can use either `online` or `offline` backup type. 
If you are unsure, you can use default `online` backup type.

- Optional
- Environment Variable: `DB2_BACKUP_TYPE`
- Default: `online`
- Supported values: `online`, `offline`

### backup_vendor
Storage vendor for backup files. Use `disk` for local storage or `s3` for S3-compatible object storage.
*Note* : Only database backup is stored in S3, instance backup is always stored in local disk.

- Optional
- Environment Variable: `BACKUP_VENDOR`
- Default: `disk`
- Supported values: `disk`, `s3`

### br_skip_instance
When set to `false`, includes Db2 instance resources (secrets, certificates, custom resources) in the backup.

- Optional
- Environment Variable: `BR_SKIP_INSTANCE`
- Default: `true`

### backup_s3_endpoint
S3 endpoint URL for S3-compatible object storage.

- **Required** when `backup_vendor` is `s3`
- Environment Variable: `BACKUP_S3_ENDPOINT`
- Default: None
- Example: `https://s3.us-east.cloud-object-storage.appdomain.cloud`

### backup_s3_bucket
S3 bucket name where backups will be stored.

- **Required** when `backup_vendor` is `s3`
- Environment Variable: `BACKUP_S3_BUCKET`
- Default: None
- Example: `mas-db2-backups`

### backup_s3_access_key
S3 access key for authentication.

- **Required** when `backup_vendor` is `s3`
- Environment Variable: `BACKUP_S3_ACCESS_KEY`
- Default: None

### backup_s3_secret_key
S3 secret key for authentication.

- **Required** when `backup_vendor` is `s3`
- Environment Variable: `BACKUP_S3_SECRET_KEY`
- Default: None

### backup_s3_alias
S3 alias name used in Db2 configuration.

- Optional
- Environment Variable: `BACKUP_S3_ALIAS`
- Default: `S3DB2COS`


Example Usage - Backup and Restore
-------------------------------------------------------------------------------

### Backup Db2 Database to Disk
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_backup_dir: /tmp/masbr
    db2_action: backup
    db2_instance_name: db2u-manage
    db2_namespace: db2u
    backup_type: online
    backup_vendor: disk
  roles:
    - ibm.mas_devops.db2
```

### Backup Db2 Database to S3
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_backup_dir: /tmp/masbr
    db2_action: backup
    db2_instance_name: db2u-manage
    backup_type: online
    backup_vendor: s3
    backup_s3_endpoint: https://s3.us-east.cloud-object-storage.appdomain.cloud
    backup_s3_bucket: mas-db2-backups # your bucket name
    backup_s3_access_key: "{{ lookup('env', 'S3_ACCESS_KEY') }}"
    backup_s3_secret_key: "{{ lookup('env', 'S3_SECRET_KEY') }}"
  roles:
    - ibm.mas_devops.db2
```

### Backup with Instance Resources and Database to disk
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_backup_dir: /tmp/masbr
    db2_action: backup
    db2_instance_name: db2u-manage
    br_skip_instance: false  # Include instance resources
    backup_vendor: disk
  roles:
    - ibm.mas_devops.db2
```

### Restore Db2 Database from Disk
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    db2_action: restore_database
    mas_instance_id: masinst1
    db2_backup_version: 251212-021316
    mas_backup_dir: /tmp/masbr
    db2_instance_name: db2u-manage
    db2_namespace: db2u
    backup_vendor: disk
  roles:
    - ibm.mas_devops.db2
```

### Restore Db2 Database from S3
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    db2_action: restore_database
    mas_instance_id: masinst1
    db2_backup_version: 251212-021316
    mas_backup_dir: /tmp/masbr
    db2_instance_name: db2u-manage
    backup_vendor: s3
    backup_s3_endpoint: https://s3.us-east.cloud-object-storage.appdomain.cloud
    backup_s3_bucket: mas-db2-backups # your bucket name
    backup_s3_access_key: "{{ lookup('env', 'S3_ACCESS_KEY') }}"
    backup_s3_secret_key: "{{ lookup('env', 'S3_SECRET_KEY') }}"
  roles:
    - ibm.mas_devops.db2
```

### Install Db2 from Backup (Instance + Database)
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    db2_action: install
    mas_instance_id: masinst1
    db2_backup_version: 251212-021316
    mas_backup_dir: /tmp/masbr
    backup_vendor: disk
  roles:
    - ibm.mas_devops.db2
```

### Install Db2 from Backup (Instance + Database(S3))
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    db2_action: install
    mas_instance_id: masinst1
    db2_backup_version: 251212-021316
    mas_backup_dir: /tmp/masbr
    backup_vendor: s3
    backup_s3_endpoint: https://s3.us-east.cloud-object-storage.appdomain.cloud
    backup_s3_bucket: mas-db2-backups # your bucket name
    backup_s3_access_key: "{{ lookup('env', 'S3_ACCESS_KEY') }}"
    backup_s3_secret_key: "{{ lookup('env', 'S3_SECRET_KEY') }}"
  roles:
    - ibm.mas_devops.db2
```

Backup and Restore Details
-------------------------------------------------------------------------------

### Backup Process
1. Validates Db2 instance is running
2. Prepares backup scripts and copies them to the Db2 pod
3. Configures S3 storage access (if using S3)
4. Executes Db2 backup command (online or offline)
5. Compresses and transfers backup files (for disk storage)
6. Creates metadata file (`db2-backup-info.yaml`) with backup details

### Database Restore Process
1. Validates backup files and Db2 version compatibility
2. Prepares restore scripts and copies them to the Db2 pod
3. Configures S3 storage access (if restoring from S3)
4. Copies backup files to the Db2 pod (for disk restores)
5. Executes Db2 restore command
6. Verifies restore completion

### Install From Backup Process
1. Validates backup files
2. Creates namespace and copies resources to namespace
3. Gets Db2 instance details from backup metadata
4. Installs Db2 instance using the backup details
5. Waits for Db2 instance to be ready
6. Performs post deployment actions like restoring instance password
7. Performs Database restore process as mentioned above

### Backup Directory Structure (Disk)
```
/tmp/masbr/
└── backup-<YYMMDD-HHMMSS>-db2u/
    ├── data/
    │   ├── db2-BLUDB-backup-<YYMMDD-HHMMSS>.tar.gz
    │   └── db2-backup-info.yaml
    └── resources/
        ├── cr.yaml
        ├── secrets/
        ├── certificates/
        └── issuers/
```

### Database backup Metadata (db2-backup-info.yaml)
```yaml
source_db2_backup_version: "251212-021316"
source_db2_backup_timestamp: "20251212021316"
source_db2_instance_name: "db2u-manage"
source_db2_instance_version: "11.5.8.0-cn7"
database: "BLUDB"
backup_vendor: "disk"
vendor_backup_path: "/mnt/backup/251212-021316/data"
local_backup_path: "/tmp/masbr/backup-251212-021316-db2u/data/db2-BLUDB-backup-251212-021316.tar.gz"
status: "SUCCESS"
```

### Important Considerations

**Version Compatibility:**
- The restore operation requires the target Db2 version to match the backup version
- Always verify version compatibility before attempting a restore

**Backup Types:**
If your DB2 instance has got circular logging enabled i.e `LOGARCHMETH1: OFF or/and LOGARCHMETH2: OFF`, you can only use `offline` backup type. 
If your DB2 instance has got circular logging disabled, you can use either `online` or `offline` backup type. 
If you are unsure, you can use default `online` backup type.
- **Online Backup**: Database remains available during backup (recommended for production)
- **Offline Backup**: Database is taken offline during backup (faster but requires downtime)

**Storage Options:**
- **Disk Storage**: Backups stored locally and copied to backup directory
- **S3 Storage**: Backups stored directly to S3-compatible object storage (no local storage required)

**Security:**
- Backup files contain sensitive data and credentials
- Secure the backup directory with appropriate permissions
- Consider encrypting backup files for long-term storage

**Performance:**
- Online backups may impact Db2 performance during execution
- Schedule backups during low-usage periods
- Monitor Db2 resource utilization during backup


Backup and Restore Troubleshooting
-------------------------------------------------------------------------------

### Common Issues and Solutions

#### Backup Failures

- Check DB2 pod logs: `oc logs -n <namespace> <db2-pod-name> -c db2u`
- Review backup script logs in the pod: `/tmp/db2_backup.log`
- Verify S3 credentials and connectivity (for S3 backups)
- Ensure sufficient storage space in the backup PVC(/mnt/backup)

**Issue: Backup fails with "insufficient storage space"**
```
Error: SQL2062N  An error occurred while accessing media "backup_path"
```
**Solution:**
- Check available disk space on the Db2 pod: `oc exec -n <namespace> <db2-pod> -- df -h`
- Verify backup storage PVC has sufficient capacity
- For S3 backups, ensure bucket has adequate space and proper permissions
- Consider using compression or incremental backups to reduce storage requirements

**Issue: Backup fails with "database is in use"**
```
Error: SQL1035N  The database is currently in use. SQLSTATE=57019
```
**Solution:**
- For offline backups, ensure all applications are disconnected
- Use online backup instead: `export DB2_BACKUP_TYPE=online`
- Check active connections: `oc exec -n <namespace> <db2-pod> -- su - db2inst1 -c "db2 list applications"`
- Force disconnect if necessary: `db2 force applications all`

**Issue: S3 backup fails with authentication errors**
```
Error: Unable to authenticate with S3 endpoint
```
**Solution:**
- Verify S3 credentials are correct: `BACKUP_S3_ACCESS_KEY` and `BACKUP_S3_SECRET_KEY`
- Test S3 connectivity from the Db2 pod
- Ensure S3 endpoint URL is correct and accessible
- Check firewall rules and network policies allow S3 access
- Verify bucket exists and credentials have write permissions

**Issue: Backup script execution timeout**
```
Error: Backup operation timed out after 3600 seconds
```
**Solution:**
- Large databases may require extended timeout periods
- Monitor backup progress: `oc logs -n <namespace> <db2-pod> -f`
- Check Db2 performance and resource utilization
- Consider scheduling backups during low-usage periods
- For very large databases, use incremental backups

#### Restore Failures

- Verify backup version exists and is complete
- Check DB2 version compatibility
- Review restore script logs: `/tmp/db2_restore_disk.log` or `/tmp/db2_restore_s3.log`
- Ensure DB2 instance is running and healthy before database restore
- For S3 restores, verify S3 connectivity and credentials

**Issue: Restore fails with version mismatch**
```
Error: DB2 version mismatch. Backup version: 11.5.8.0, Target version: 11.5.9.0
```
**Solution:**
- Ensure target Db2 version matches backup version
- Check backup metadata: `cat <backup_dir>/data/db2-backup-info.yaml`
- Install matching Db2 version: `export DB2_VERSION=11.5.8.0-cn7`
- Alternatively, upgrade backup to target version (requires manual intervention)

**Issue: Restore fails with "database already exists"**
```
Error: SQL1005N  The database alias "BLUDB" already exists
```
**Solution:**
- Drop existing database before restore:
  ```bash
  oc exec -n <namespace> <db2-pod> -- su - db2inst1 -c "db2 drop database BLUDB"
  ```
- Or use a different database name during restore
- Verify database state: `db2 list database directory`

**Issue: Restore fails with corrupted backup files**
```
Error: SQL2025N  The database cannot be restored from backup image
```
**Solution:**
- Verify backup file integrity:
  ```bash
  tar -tzf <backup-file>.tar.gz > /dev/null
  ```
- Check backup metadata for status: `status: SUCCESS`
- Re-run backup if corruption detected
- For S3 restores, verify file was completely uploaded
- Check storage system for hardware errors

**Issue: Restore fails with insufficient permissions**
```
Error: SQL0551N  User does not have required authorization
```
**Solution:**
- Verify db2inst1 user has proper permissions
- Check pod security context and service account
- Ensure restore scripts have execute permissions
- Review OpenShift security policies (SCC)

**Issue: S3 restore fails to download backup files**
```
Error: Failed to download backup from S3 bucket
```
**Solution:**
- Verify S3 credentials have read permissions
- Check S3 bucket name and path are correct
- Test S3 connectivity: `aws s3 ls s3://<bucket-name>/`
- Ensure network policies allow outbound S3 access
- Verify backup files exist in S3 bucket

#### Performance Issues

**Issue: Backup taking too long**
**Solution:**
- Use online backups to avoid database downtime
- Schedule backups during low-usage periods
- Increase Db2 pod resources (CPU/memory)
- Use compression to reduce backup size
- Consider incremental backups for large databases
- Check network bandwidth for S3 backups

**Issue: Restore taking too long**
**Solution:**
- Ensure adequate resources allocated to Db2 pod
- Monitor pod resource utilization during restore
- Check storage performance (IOPS, throughput)
- For S3 restores, verify network bandwidth
- Consider using faster storage classes

#### Validation and Verification

**Issue: How to verify backup completed successfully**
**Solution:**
1. Check backup metadata file:
   ```bash
   cat <backup_dir>/data/db2-backup-info.yaml
   ```
   Verify `status: SUCCESS`

2. Verify backup file exists and has reasonable size:
   ```bash
   ls -lh <backup_dir>/data/db2-*.tar.gz
   ```

3. For S3 backups, verify files in bucket:
   ```bash
   aws s3 ls s3://<bucket-name>/<backup-version>/
   ```

4. Check Db2 backup history:
   ```bash
   oc exec -n <namespace> <db2-pod> -- su - db2inst1 -c "db2 list history backup all for BLUDB"
   ```

**Issue: How to verify restore completed successfully**
**Solution:**
1. Check database is online:
   ```bash
   oc exec -n <namespace> <db2-pod> -- su - db2inst1 -c "db2 connect to BLUDB"
   ```

2. Verify table counts and data integrity:
   ```bash
   oc exec -n <namespace> <db2-pod> -- su - db2inst1 -c "db2 'select count(*) from <table_name>'"
   ```

3. Check database configuration:
   ```bash
   oc exec -n <namespace> <db2-pod> -- su - db2inst1 -c "db2 get db cfg for BLUDB"
   ```

4. Review restore logs for errors:
   ```bash
   oc logs -n <namespace> <db2-pod> | grep -i error
   ```

### Diagnostic Commands

**Check Db2 pod status:**
```bash
oc get pods -n <namespace> | grep db2
oc describe pod <db2-pod> -n <namespace>
```

**Check Db2 instance status:**
```bash
oc exec -n <namespace> <db2-pod> -- su - db2inst1 -c "db2pd -"
```

**Check database status:**
```bash
oc exec -n <namespace> <db2-pod> -- su - db2inst1 -c "db2 list active databases"
```

**Check backup storage:**
```bash
oc get pvc -n <namespace>
oc exec -n <namespace> <db2-pod> -- df -h /mnt/backup
```

**View Db2 diagnostic logs:**
```bash
oc exec -n <namespace> <db2-pod> -- tail -f /var/log/db2u.log
oc exec -n <namespace> <db2-pod> -- cat /database/config/db2inst1/sqllib/db2dump/db2diag.log
```

**Check S3 configuration (if using S3):**
```bash
oc exec -n <namespace> <db2-pod> -- su - db2inst1 -c "db2 list storage access"
```

### Getting Help

If you encounter issues not covered in this troubleshooting guide:

1. **Check Db2 logs**: Review `/var/log/db2u.log` and `db2diag.log` for detailed error messages
2. **Review backup metadata**: Check `db2-backup-info.yaml` for backup details and status
3. **Verify prerequisites**: Ensure all required variables are set correctly
4. **Test connectivity**: Verify network access to storage (S3 or PVC)
5. **Check resources**: Ensure adequate CPU, memory, and storage are available
6. **Open an issue**: Report problems at the project repository with logs and configuration details

License
-------------------------------------------------------------------------------

EPL-2.0
