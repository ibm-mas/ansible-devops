# db2

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


## Role Variables

### Installation Variables

#### common_services_namespace
OpenShift namespace where IBM Common Services is installed.

- **Optional**
- Environment Variable: `COMMON_SERVICES_NAMESPACE`
- Default Value: `ibm-common-services`

**Purpose**: Specifies the namespace containing IBM Common Services, which provides shared services used by Db2 operator. This is needed for the role to locate and interact with Common Services components.

**When to use**:
- Leave as default (`ibm-common-services`) for standard installations
- Set only if Common Services is installed in a non-standard namespace
- Required when Common Services namespace differs from default

**Valid values**: Any valid Kubernetes namespace name where IBM Common Services is installed

**Impact**: The role uses this to locate Common Services resources. Incorrect namespace will cause the role to fail when trying to access Common Services components.

**Related variables**: Works with `db2_namespace` to manage operator and instance placement.

**Note**: The default `ibm-common-services` is the standard namespace for Common Services. Only change if your installation uses a different namespace.

#### db2_action
Specifies which operation to perform on the Db2 database.

- **Optional**
- Environment Variable: `DB2_ACTION`
- Default: `install`

**Purpose**: Controls what action the role executes against Db2 instances. This allows the same role to handle installation, upgrades, backups, and restores of Db2 databases.

**When to use**:
- Use `install` (default) for initial Db2 deployment
- Use `upgrade` to upgrade all Db2 instances in the namespace to a new version
- Use `backup` to create a backup of Db2 instance and/or database
- Use `restore` to restore a backup of db2 instance and database
- Use `restore_database` to restore only the database to an existing Db2 instance

**Valid values**: `install`, `upgrade`, `backup`, `restore`, `restore_database`

**Impact**:
- `install`: Creates new Db2 operator and instance. When `db2_backup_version` is provided, installs from backup (instance + database)
- `upgrade`: Upgrades ALL instances in `db2_namespace` to `db2_version` (affects all instances in namespace)
- `backup`: Creates backup of Db2 instance resources and/or database data
- `restore`: Creates new Db2 operator and instance from the backup of Db2 instance resources and restores database data to the created instance
- `restore_database`: Restores database to an existing running Db2 instance (does not restore instance resources)

**Related variables**:
- `db2_version`: Required for upgrade action to specify target version
- `db2_namespace`: All instances in this namespace are affected by upgrade
- `db2_backup_version`: Required for restore/restore_database action; optional for backup, defaults to YYYYMMDD-HHMMSS
- `override_storageclass`: In Restore, controls whether storage classes are overridden

**Note**: **WARNING** - When using `upgrade`, ALL Db2 instances in the specified namespace will be upgraded. Plan accordingly and ensure `db2_version` matches the operator channel.

#### db2_namespace
OpenShift namespace where Db2 operator and instances will be deployed.

- **Optional**
- Environment Variable: `DB2_NAMESPACE`
- Default: `db2u`

**Purpose**: Specifies the namespace for deploying the Db2u operator and Db2 instances (Db2uCluster custom resources). Starting with recent versions, the operator is installed in the same namespace as the instances.

**When to use**:
- Use default (`db2u`) for standard single-instance deployments
- Set to a custom namespace when organizing multiple Db2 deployments
- Must match existing namespace when upgrading Db2 instances

**Valid values**: Any valid Kubernetes namespace name (e.g., `db2u`, `db2-prod`, `mas-db2`)

**Impact**: All Db2 resources (operator, instances, secrets, services) are created in this namespace. When upgrading, ALL instances in this namespace will be upgraded together.

**Related variables**:
- `db2_action`: When set to `upgrade`, affects all instances in this namespace
- `db2_instance_name`: Instance created within this namespace

**Note**: The role handles migration of operators from `ibm-common-services` to this namespace if needed. All instances in the namespace are upgraded together when using `db2_action=upgrade`.

#### db2_channel
Subscription channel for the Db2 Universal Operator.

- **Optional**
- Environment Variable: `DB2_CHANNEL`
- Default: The default channel from the operator package (automatically selected)

**Purpose**: Specifies which operator channel to subscribe to, determining which Db2 operator version stream you receive. Channels typically correspond to major Db2 versions (e.g., `v2.2`, `v3.0`).

**When to use**:
- Leave unset to use the default channel (recommended for new installations)
- Set explicitly when you need a specific operator version stream
- Must match `db2_version` when upgrading (version must be available in the channel)

**Valid values**: Valid Db2 operator channel names (e.g., `v2.2`, `v3.0`, `v3.1`)

**Impact**: Determines which operator version is installed and which Db2 engine versions are available. Changing channels may require operator migration.

**Related variables**:
- `db2_version`: Must be compatible with the selected channel
- When upgrading, version must match channel

**Note**: The operator channel determines available Db2 engine versions. Check the operator package for available channels and their supported versions.

#### db2_instance_name
Unique name for the Db2 instance (Db2uCluster resource).

- **Required**
- Environment Variable: `DB2_INSTANCE_NAME`
- Default: None

**Purpose**: Defines the name of the Db2uCluster custom resource that will be created. This name is used to identify the Db2 instance and is embedded in resource names (services, pods, secrets).

**When to use**:
- Always required for Db2 installation
- Use descriptive names that indicate purpose (e.g., `maximo-db`, `iot-db`, `manage-db`)
- Must be unique within the namespace

**Valid values**: Valid Kubernetes resource name (lowercase alphanumeric with hyphens, e.g., `db01`, `mas-db`, `manage-db`)

**Impact**: This name is used throughout the Db2 deployment:
- Db2uCluster resource name
- Service names (e.g., `{instance_name}-db2u-engn-svc`)
- Pod names (e.g., `c-{instance_name}-db2u-0`)
- Secret names

**Related variables**:
- `db2_dbname`: Name of the database within this instance
- Used in generated JdbcCfg when `mas_instance_id` is provided

**Note**: Choose a meaningful name as it appears in many resource names and cannot be easily changed after creation.

#### ibm_entitlement_key
IBM Container Library entitlement key for accessing Db2 container images.

- **Required**
- Environment Variable: `IBM_ENTITLEMENT_KEY`
- Default: None

**Purpose**: Provides authentication credentials to pull Db2 container images from the IBM Container Registry. This key is associated with your IBM entitlement and grants access to licensed software.

**When to use**:
- Always required for Db2 installation
- Obtain from [IBM Container Library](https://myibm.ibm.com/products-services/containerlibrary)
- Same key used across all IBM MAS components

**Valid values**: Valid IBM entitlement key string

**Impact**: Without a valid key, Db2 container images cannot be pulled and installation will fail. The key is stored in an image pull secret in the Db2 namespace.

**Related variables**: Used across multiple roles for accessing IBM container images.

**Note**: Keep this key secure and do not commit to source control. The key is tied to your IBM entitlement and should be treated as a credential. Obtain from the IBM Container Library using your IBM ID.

#### db2_dbname
Name of the database to create within the Db2 instance.

- **Optional**
- Environment Variable: `DB2_DBNAME`
- Default: `BLUDB`

**Purpose**: Specifies the name of the database that will be created inside the Db2 instance. A Db2 instance can contain multiple databases, and this defines the primary database name.

**When to use**:
- Use default (`BLUDB`) for standard MAS deployments
- Set to a custom name when organizational standards require specific naming
- Must match the database name expected by applications connecting to Db2

**Valid values**: Valid Db2 database name (uppercase alphanumeric, up to 8 characters, e.g., `BLUDB`, `MAXDB`, `MASDB`)

**Impact**: This database name is used in connection strings and JDBC configurations. Applications must use this exact name to connect to the database.

**Related variables**:
- `db2_instance_name`: The instance containing this database
- Used in generated JdbcCfg for MAS configuration

**Note**: The default `BLUDB` is standard for Db2 Warehouse. Db2 database names are typically uppercase and limited to 8 characters.

#### db2_version
Db2 engine version to use for installation or upgrade.

- **Optional**
- Environment Variable: `DB2_VERSION`
- Default: Latest version supported by the installed Db2 operator (auto-detected from `db2u-release` configmap)

**Purpose**: Specifies which Db2 engine version to deploy or upgrade to. The version must be compatible with the installed operator channel.

**When to use**:
- Leave unset for new installations to use the latest supported version (recommended)
- Set explicitly when you need a specific Db2 version
- Required when upgrading to specify the target version
- Must match the operator channel capabilities

**Valid values**: Valid Db2 engine version supported by the operator (e.g., `11.5.8.0`, `11.5.9.0`)

**Impact**: Determines which Db2 engine version is deployed. When upgrading, ALL instances in `db2_namespace` will be upgraded to this version. Version must be available in the operator's supported versions list.

**Related variables**:
- `db2_channel`: Version must be compatible with the operator channel
- `db2_action`: When set to `upgrade`, this version is the target
- `db2_namespace`: All instances in namespace upgraded to this version

**Note**: Supported versions are listed in the `db2u-release` configmap in `ibm-common-services` namespace. Ensure the version matches your operator channel. When upgrading, all instances in the namespace are upgraded together.

#### db2_type
Db2 instance type optimized for specific workload patterns.

- **Optional**
- Environment Variable: `DB2_TYPE`
- Default: `db2wh`

**Purpose**: Determines the Db2 instance configuration optimized for either data warehouse (analytical) or online transaction processing workloads. This affects resource allocation and database tuning.

**When to use**:
- Use `db2wh` (default) for MAS Manage and analytical workloads
- Use `db2oltp` for high-transaction workloads requiring OLTP optimization
- Choose based on your primary use case

**Valid values**: `db2wh`, `db2oltp`

**Impact**: 
- `db2wh`: Optimized for data warehouse/analytical queries (recommended for MAS Manage)
- `db2oltp`: Optimized for online transaction processing with high concurrency

**Related variables**:
- `db2_workload`: Further refines workload optimization
- `db2_table_org`: Table organization should align with instance type

**Note**: MAS Manage typically uses `db2wh` for optimal performance with its analytical workload patterns.

#### db2_timezone
Server timezone for the Db2 instance.

- **Optional**
- Environment Variable: `DB2_TIMEZONE`
- Default: `GMT`

**Purpose**: Sets the timezone used by the Db2 server for timestamp operations and scheduling. This affects how Db2 interprets and stores timestamp data.

**When to use**:
- Use default (`GMT`) for globally distributed systems
- Set to local timezone when all users are in the same timezone
- Must match MAS Manage timezone if using Manage with this database

**Valid values**: Valid timezone codes (e.g., `GMT`, `EST`, `PST`, `CET`, `UTC`)

**Impact**: Affects timestamp interpretation and storage in the database. Mismatched timezones between Db2 and applications can cause data inconsistencies.

**Related variables**:
- `MAS_APP_SETTINGS_SERVER_TIMEZONE`: Must be set to the same value for MAS Manage
- Affects all timestamp operations in the database

**Note**: **IMPORTANT** - If using this Db2 instance with MAS Manage, you must also set `MAS_APP_SETTINGS_SERVER_TIMEZONE` to the same value to ensure consistent timestamp handling.

#### db2_4k_device_support
Controls 4K sector device support in Db2.

- **Optional**
- Environment Variable: `DB2_4K_DEVICE_SUPPORT`
- Default: `ON`

**Purpose**: Enables or disables support for storage devices with 4K sector sizes. Modern storage systems often use 4K sectors instead of traditional 512-byte sectors.

**When to use**:
- Leave as `ON` (default) for modern storage systems with 4K sectors
- Set to `OFF` only if using legacy storage with 512-byte sectors
- Check your storage specifications if unsure

**Valid values**: `ON`, `OFF`

**Impact**: 
- `ON`: Enables 4K sector support (required for most modern storage)
- `OFF`: Uses traditional 512-byte sector mode (legacy storage only)

**Related variables**: Works with storage class configuration to ensure compatibility.

**Note**: Most modern storage systems use 4K sectors. Keep this `ON` unless you have specific legacy storage requirements.

#### db2_workload
Workload profile for Db2 instance optimization.

- **Optional**
- Environment Variable: `DB2_WORKLOAD`
- Default: `ANALYTICS`

**Purpose**: Configures Db2 with predefined settings optimized for specific workload patterns. This affects memory allocation, query optimization, and other performance parameters.

**When to use**:
- Use `ANALYTICS` (default) for general analytical and MAS workloads
- Use `PUREDATA_OLAP` for pure data warehouse/OLAP workloads
- Choose based on your primary query patterns

**Valid values**: `ANALYTICS`, `PUREDATA_OLAP`

**Impact**: 
- `ANALYTICS`: Balanced optimization for mixed analytical workloads (recommended for MAS)
- `PUREDATA_OLAP`: Optimized specifically for OLAP/data warehouse queries

**Related variables**:
- `db2_type`: Should align with workload choice
- `db2_table_org`: Table organization should match workload pattern

**Note**: The default `ANALYTICS` is suitable for most MAS deployments. Only change if you have specific OLAP requirements.

#### db2_table_org
Default table organization for database tables.

- **Optional**
- Environment Variable: `DB2_TABLE_ORG`
- Default: `ROW`

**Purpose**: Determines the default storage organization for tables in the database. Row-organized tables are optimized for transactional workloads, while column-organized tables are optimized for analytical queries.

**When to use**:
- Use `ROW` (default) for MAS Manage and mixed workloads
- Use `COLUMN` only for pure analytical/reporting workloads
- Choose based on your primary query patterns

**Valid values**: `ROW`, `COLUMN`

**Impact**: 
- `ROW`: Tables stored row-by-row (better for OLTP, updates, and mixed workloads)
- `COLUMN`: Tables stored column-by-column (better for analytical queries and aggregations)

**Related variables**:
- `db2_type`: Should align with table organization choice
- `db2_workload`: Workload profile should match table organization

**Note**: MAS Manage requires `ROW` organization. Only use `COLUMN` for dedicated analytical databases. This sets the default; individual tables can override this setting.

#### db2_ldap_username
Username for Db2 LDAP authentication.

- **Optional**
- Environment Variable: `DB2_LDAP_USERNAME`
- Default: None (uses default `db2inst1` user)

**Purpose**: Defines a custom LDAP username for Db2 authentication instead of the default `db2inst1` user. When set, this user is configured in Db2's local LDAP registry and used in MAS JDBC configuration.

**When to use**:
- Set when you need a custom database user for MAS connections
- Set when organizational policies require specific usernames
- Leave unset to use the default `db2inst1` user
- Must be set together with `db2_ldap_password`

**Valid values**: Valid LDAP username string

**Impact**: When set, this user is created in Db2's LDAP registry and used in the generated JdbcCfg for MAS. The user will have necessary database permissions configured.

**Related variables**:
- `db2_ldap_password`: Required when this is set
- `db2_rotate_password`: Can auto-generate password for this user
- Used in generated JdbcCfg for MAS configuration

**Note**: If not set, MAS will use the default `db2inst1` user. When set, you must also provide `db2_ldap_password`.

#### db2_ldap_password
Password for the Db2 LDAP user.

- **Optional**
- Environment Variable: `DB2_LDAP_PASSWORD`
- Default: None

**Purpose**: Sets the password for the LDAP user specified in `db2_ldap_username`. This password is configured in Db2's local LDAP registry and used for database authentication.

**When to use**:
- Required when `db2_ldap_username` is set
- Set to a strong password meeting security requirements
- Can be omitted if using `db2_rotate_password` for auto-generation

**Valid values**: Strong password string meeting security requirements

**Impact**: This password is stored in Db2's LDAP registry and used for database authentication. It's also included in the generated JdbcCfg for MAS.

**Related variables**:
- `db2_ldap_username`: Must be set together with this password
- `db2_rotate_password`: Alternative to manually setting password

**Note**: Keep this password secure and do not commit to source control. If using `db2_rotate_password=true`, this password will be auto-generated and you don't need to provide it.

#### db2_rotate_password
Enables automatic password generation and rotation for Db2 LDAP user.

- **Optional**
- Environment Variable: `DB2_LDAP_ROTATE_PASSWORD`
- Default: `False`

**Purpose**: Automates password management by generating a new random password for the Db2 LDAP user and updating both Db2 and MAS configurations. This improves security by enabling regular password rotation.

**When to use**:
- Set to `True` for automated password management
- Set to `True` for regular password rotation as a security practice
- Leave as `False` when manually managing passwords
- Useful for automated deployments where manual password management is impractical

**Valid values**: `True`, `False`

**Impact**: 
- When `True`: Role generates a strong random password, configures it in Db2, and updates MAS JdbcCfg
- When `False`: You must provide `db2_ldap_password` manually

**Related variables**:
- `db2_ldap_username`: User whose password will be rotated
- `db2_ldap_password`: Not needed when rotation is enabled

**Note**: When enabled, the role handles all password management automatically. The generated password is stored securely in Kubernetes secrets and MAS configuration.

### Storage Variables
We recommend reviewing the Db2 documentation about the certified storage options for Db2 on Red Hat OpenShift. Please ensure your storage class meets the specified deployment requirements for Db2. [https://www.ibm.com/docs/en/db2/11.5?topic=storage-certified-options](https://www.ibm.com/docs/en/db2/11.5?topic=storage-certified-options)

#### db2_meta_storage_class
Storage class for Db2 metadata storage (must support ReadWriteMany).

- **Required**
- Environment Variable: `DB2_META_STORAGE_CLASS`
- Default: `ibmc-file-gold` (if available in cluster)

**Purpose**: Specifies the storage class for Db2 metadata storage, which requires ReadWriteMany (RWX) access mode for shared access across Db2 pods.

**When to use**:
- Always required for Db2 installation
- Must be a storage class supporting RWX access mode
- Typically file-based storage (NFS, IBM Cloud File Storage, etc.)

**Valid values**: Any storage class name supporting ReadWriteMany access mode

**Impact**: Metadata storage is critical for Db2 operation. Incorrect storage class or one not supporting RWX will cause Db2 deployment to fail.

**Related variables**:
- `db2_meta_storage_size`: Size of metadata volume
- `db2_meta_storage_accessmode`: Should be `ReadWriteMany`

**Note**: See [Db2 certified storage options](https://www.ibm.com/docs/en/db2/11.5?topic=storage-certified-options) for supported storage. File-based storage classes typically support RWX (e.g., `ibmc-file-gold`, `ocs-storagecluster-cephfs`).

#### db2_meta_storage_size
Size of the metadata persistent volume.

- **Optional**
- Environment Variable: `DB2_META_STORAGE_SIZE`
- Default: `10Gi`

**Purpose**: Specifies the size of the persistent volume for Db2 metadata storage. Metadata includes system catalogs, configuration files, and other operational data.

**When to use**:
- Use default (`10Gi`) for most deployments
- Increase for large-scale deployments with many databases or complex configurations
- Monitor usage and adjust if metadata volume fills up

**Valid values**: Kubernetes storage size format (e.g., `10Gi`, `20Gi`, `50Gi`)

**Impact**: Insufficient metadata storage can cause Db2 operational issues. The volume must have enough space for system catalogs and configuration data.

**Related variables**:
- `db2_meta_storage_class`: Storage class for this volume
- `db2_meta_storage_accessmode`: Access mode for this volume

**Note**: The default `10Gi` is sufficient for most deployments. Metadata storage requirements are typically much smaller than data storage.

#### db2_meta_storage_accessmode
Access mode for metadata storage volume.

- **Optional**
- Environment Variable: `DB2_META_STORAGE_ACCESSMODE`
- Default: `ReadWriteMany`

**Purpose**: Defines the Kubernetes access mode for the metadata persistent volume. ReadWriteMany (RWX) is required for Db2 metadata to be accessible from multiple pods.

**When to use**:
- Leave as default (`ReadWriteMany`) for standard Db2 deployments
- RWX is required for Db2 high availability and proper operation

**Valid values**: `ReadWriteMany` (RWX)

**Impact**: Db2 requires RWX access mode for metadata storage. Using a different access mode will cause deployment failures.

**Related variables**:
- `db2_meta_storage_class`: Must support the specified access mode
- `db2_meta_storage_size`: Size of this volume

**Note**: Do not change from the default `ReadWriteMany`. Db2 metadata requires RWX access mode for proper operation.

#### db2_data_storage_class
Storage class for Db2 user data storage (must support ReadWriteOnce).

- **Required**
- Environment Variable: `DB2_DATA_STORAGE_CLASS`
- Default: `ibmc-block-gold` (if available in cluster)

**Purpose**: Specifies the storage class for Db2 user data storage, which requires ReadWriteOnce (RWO) access mode. This is where database tables and user data are stored.

**When to use**:
- Always required for Db2 installation
- Must be a storage class supporting RWO access mode
- Typically block-based storage for performance (SAN, IBM Cloud Block Storage, etc.)

**Valid values**: Any storage class name supporting ReadWriteOnce access mode

**Impact**: Data storage is critical for Db2 performance and capacity. Choose high-performance storage for production workloads. Incorrect storage class or one not supporting RWO will cause Db2 deployment to fail.

**Related variables**:
- `db2_data_storage_size`: Size of data volume
- `db2_data_storage_accessmode`: Should be `ReadWriteOnce`

**Note**: See [Db2 certified storage options](https://www.ibm.com/docs/en/db2/11.5?topic=storage-certified-options) for supported storage. Block-based storage classes typically provide better performance for databases (e.g., `ibmc-block-gold`, `ocs-storagecluster-ceph-rbd`).

#### db2_data_storage_size
Size of the user data persistent volume.

- **Optional**
- Environment Variable: `DB2_DATA_STORAGE_SIZE`
- Default: `50Gi`

**Purpose**: Specifies the size of the persistent volume for Db2 user data storage. This is where database tables, indexes, and all user data are stored.

**When to use**:
- Use default (`50Gi`) for development/test environments
- Increase significantly for production based on data volume estimates
- Plan for data growth over time
- Monitor usage and expand as needed

**Valid values**: Kubernetes storage size format (e.g., `50Gi`, `100Gi`, `500Gi`, `1Ti`)

**Impact**: Insufficient data storage will cause database operations to fail when the volume fills up. Size appropriately for your data volume plus growth.

**Related variables**:
- `db2_data_storage_class`: Storage class for this volume
- `db2_data_storage_accessmode`: Access mode for this volume

**Note**: The default `50Gi` is suitable for small deployments only. Production MAS Manage deployments typically require 500Gi or more. Plan storage capacity based on expected data volume and growth.

#### db2_data_storage_accessmode
Access mode for user data storage volume.

- **Optional**
- Environment Variable: `DB2_DATA_STORAGE_ACCESSMODE`
- Default: `ReadWriteOnce`

**Purpose**: Defines the Kubernetes access mode for the user data persistent volume. ReadWriteOnce (RWO) is standard for Db2 data storage as it's accessed by a single pod at a time.

**When to use**:
- Leave as default (`ReadWriteOnce`) for standard Db2 deployments
- RWO is the correct mode for Db2 data storage

**Valid values**: `ReadWriteOnce` (RWO)

**Impact**: Db2 data storage uses RWO access mode. Using a different access mode may cause deployment issues or performance problems.

**Related variables**:
- `db2_data_storage_class`: Must support the specified access mode
- `db2_data_storage_size`: Size of this volume

**Note**: Do not change from the default `ReadWriteOnce`. Db2 data storage is designed for RWO access mode.

#### db2_backup_storage_class
Storage class for Db2 backup storage (must support ReadWriteMany).

- **Optional**
- Environment Variable: `DB2_BACKUP_STORAGE_CLASS`
- Default: `ibmc-file-gold` (if available in cluster)

**Purpose**: Specifies the storage class for Db2 backup storage, which requires ReadWriteMany (RWX) access mode for shared access during backup operations.

**When to use**:
- Use default for standard backup storage configuration
- Must be a storage class supporting RWX access mode
- Set to `None` to disable backup storage (not recommended for production)
- Typically file-based storage (NFS, IBM Cloud File Storage, etc.)

**Valid values**: Any storage class name supporting ReadWriteMany access mode, or `None` to disable

**Impact**: 
- When set: Backup storage is configured for Db2 backups
- When set to `None`: Backup storage is dropped from Db2uCluster CR (backups not possible)

**Related variables**:
- `db2_backup_storage_size`: Size of backup volume
- `db2_backup_storage_accessmode`: Should be `ReadWriteMany`

**Note**: **WARNING** - Setting to `None` disables backup capability. Only do this for non-production environments. Production systems should always have backup storage configured.

#### db2_backup_storage_size
Size of the backup persistent volume.

- **Optional**
- Environment Variable: `DB2_BACKUP_STORAGE_SIZE`
- Default: `50Gi`

**Purpose**: Specifies the size of the persistent volume for Db2 backup storage. This volume stores database backups for disaster recovery and point-in-time recovery.

**When to use**:
- Use default (`50Gi`) for small databases or development environments
- Increase based on database size and backup retention requirements
- Plan for multiple full backups plus transaction logs
- Monitor usage and expand as database grows

**Valid values**: Kubernetes storage size format (e.g., `50Gi`, `100Gi`, `500Gi`, `1Ti`)

**Impact**: Insufficient backup storage will cause backup operations to fail. Size should accommodate multiple full backups based on your retention policy.

**Related variables**:
- `db2_backup_storage_class`: Storage class for this volume
- `db2_backup_storage_accessmode`: Access mode for this volume
- `db2_data_storage_size`: Backup storage should be sized relative to data storage

**Note**: Plan backup storage as a multiple of your data storage size. A common practice is 2-3x the data storage size to accommodate multiple full backups and transaction logs.

#### db2_backup_storage_accessmode
Access mode for backup storage volume.

- **Optional**
- Environment Variable: `DB2_BACKUP_STORAGE_ACCESSMODE`
- Default: `ReadWriteMany`

**Purpose**: Defines the Kubernetes access mode for the backup persistent volume. ReadWriteMany (RWX) is required for Db2 backup operations to be accessible from multiple pods.

**When to use**:
- Leave as default (`ReadWriteMany`) for standard Db2 backup configuration
- RWX is required for Db2 backup operations

**Valid values**: `ReadWriteMany` (RWX)

**Impact**: Db2 backup storage requires RWX access mode. Using a different access mode will cause backup operations to fail.

**Related variables**:
- `db2_backup_storage_class`: Must support the specified access mode
- `db2_backup_storage_size`: Size of this volume

**Note**: Do not change from the default `ReadWriteMany`. Db2 backup operations require RWX access mode for proper operation.
- Default: `ReadWriteMany`

#### db2_logs_storage_class
Storage class used for transaction logs. This must support ReadWriteOnce(RWO) access mode.

- Optional
- Environment Variable: `DB2_LOGS_STORAGE_CLASS`
- Default: Defaults to `ibmc-block-gold` if the storage class is available in the cluster. Set to `None` will drop the logs storage on DB2ucluster CR.

#### db2_logs_storage_size
Size of transaction logs persistent volume.

- **Optional**
- Environment Variable: `DB2_LOGS_STORAGE_SIZE`
- Default: `10Gi`

#### db2_logs_storage_accessmode
The access mode for the storage.

- Optional
- Environment Variable: `DB2_LOGS_STORAGE_ACCESSMODE`
- Default: `ReadWriteOnce`

#### db2_temp_storage_class
Storage class used for temporary data. This must support ReadWriteMany(RWX) access mode.

- **Optional**
- Environment Variable: `DB2_TEMP_STORAGE_CLASS`
- Default: Defaults to `ibmc-block-gold` if the storage class is available in the cluster. Set to `None` will drop the tempts storage on DB2ucluster CR.

#### db2_temp_storage_size
Size of temporary persistent volume.

- Optional
- Environment Variable: `DB2_TEMP_STORAGE_SIZE`
- Default: `10Gi`

#### db2_temp_storage_accessmode
The access mode for the storage. This must support ReadWriteOnce(RWO) access mode.

- **Optional**
- Environment Variable: `DB2_TEMP_STORAGE_ACCESSMODE`
- Default: `ReadWriteOnce`

### Resource Request Variables
These variables allow you to customize the resources available to the Db2 pod in your cluster.  In most circumstances you will want to set these properties because it's impossible for us to provide a default value that will be appropriate for all users.  We have set defaults that are suitable for deploying Db2 onto a dedicated worker node with 4cpu and 16gb memory.

!!! tip
    Note that you must take into account the system overhead on any given node when setting these parameters, if you set the requests equal to the number of CPU or amount of memory on your node then the scheduler will not be able to schedule the Db2 pod because not 100% of the worker nodes' resource will be available to pod on that node, even if there's only a single pod on it.

    Db2 is sensitive to both CPU and memory issues, particularly memory, we recommend setting requests and limits to the same values, ensuring the scheduler always reserves the resources that Db2 expects to be available to it.

#### db2_cpu_requests
Define the Kubernetes CPU request for the Db2 pod.

- Optional
- Environment Variable: `DB2_CPU_REQUESTS`
- Default: `4000m`

#### db2_cpu_limits
Define the Kubernetes CPU limit for the Db2 pod.

- **Optional**
- Environment Variable: `DB2_CPU_LIMITS`
- Default: `6000m`

#### db2_memory_requests
Define the Kubernetes memory request for the Db2 pod.

- Optional
- Environment Variable: `DB2_MEMORY_REQUESTS`
- Default: `8Gi`

#### db2_memory_limits
Define the Kubernetes memory limit for the Db2 pod.

- **Optional**
- Environment Variable: `DB2_MEMORY_LIMITS`
- Default: `16Gi`

### Node Label Affinity Variables
Specify both `db2_affinity_key` and `db2_affinity_value` to configure `requiredDuringSchedulingIgnoredDuringExecution` affinity with appropriately labelled nodes.

#### db2_affinity_key
Specify the key of a node label to declare affinity with.

- Optional
- Environment Variable: `DB2_AFFINITY_KEY`
- Default: None

#### db2_affinity_value
Specify the value of a node label to declare affinity with.

- **Optional**
- Environment Variable: `DB2_AFFINITY_VALUE`
- Default: None

### Node Taint Toleration Variables
Specify `db2_tolerate_key`, `db2_tolerate_value`, and `db2_tolerate_effect` to configure a toleration policy to allow the db2 instance to be scheduled on nodes with the specified taint.

#### db2_tolerate_key
Specify the key of the taint that is to be tolerated.

- Optional
- Environment Variable: `DB2_TOLERATE_KEY`
- Default: None

#### db2_tolerate_value
Specify the value of the taint that is to be tolerated.

- **Optional**
- Environment Variable: `DB2_TOLERATE_VALUE`
- Default: None

#### db2_tolerate_effect
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

#### db2_database_db_config
Overwrites the db2ucluster database configuration settings under `spec.environment.database.dbConfig` section.

- **Optional**
- Environment Variable: `DB2_DATABASE_DB_CONFIG`
- Default: None

#### db2_instance_dbm_config
Overwrites the db2ucluster instance database configuration settings under `spec.environment.instance.dbmConfig` section.

!!! important
    Do not set [instance_memory](https://www.ibm.com/docs/en/db2/11.5?topic=parameters-instance-memory-instance-memory).  The Db2 engine does not know Db2 is running inside a container, setting `dbmConfig.INSTANCE_MEMORY: automatic` will cause it to read the cgroups of the node and potentially go beyond the pod memory limit.  Db2U has logic built in to use a normalized percentage that takes into account the memory limit and free memory of the node.

- Optional
- Environment Variable: `DB2_INSTANCE_DBM_CONFIG`
- Default: None

#### db2_instance_registry
Overwrites the db2ucluster instance database configuration settings under `spec.environment.instance.registry` section. You can define parameters to be included in this section using semicolon separated values.

- **Optional**
- Environment Variable: `DB2_INSTANCE_REGISTRY`
- Default: None

### MPP System Variables
!!! warning
    Do not use these variables if you intend to use the Db2 instance with IBM Maximo Application Suite; no MAS application supports Db2 MPP

#### db2_mln_count
The number of logical nodes (i.e. database partitions to create). Note: ensure that the application using this Db2 can support Db2 MPP (which is created when `DB2_MLN_COUNT` is greater than 1).

- Optional
- Environment Variable: `'DB2_MLN_COUNT`
- Default: 1

#### db2_num_pods
The number of Db2 pods to create in the instance. Note that `db2_num_pods` must be less than or equal to `db2_mln_count`.  A single db2u pod can contain multiple logical nodes. So be sure to avoid specifying a large number for `db2_mln_count` while specifying a small number for `db2_num_pods`. If in doubt, make `db2_mln_count = db2_num_pods`. For more information refer to the [Db2 documentation](https://www.ibm.com/docs/en/db2-warehouse?topic=SSCJDQ/com.ibm.swg.im.dashdb.ucontainer.doc/doc/db2w-mempernode-new.html).

- **Optional**
- Environment Variable: `DB2_NUM_PODS`
- Default: 1

### MAS Configuration Variables

#### mas_instance_id
Providing this and `mas_config_dir` will instruct the role to generate a JdbcCfg template that can be used to configure MAS to connect to this database.

- Optional
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

#### mas_config_dir
Providing this and `mas_instance_id` will instruct the role to generate a JdbcCfg template that can be used to configure MAS to connect to this database.

- **Optional**
- Environment Variable: `MAS_CONFIG_DIR`
- Default: None

#### mas_config_scope
Supported values are `system`, `ws`, `app`, or `wsapp`, this is only used when both `mas_config_dir` and `mas_instance_id` are set.

- Optional
- Environment Variable: `MAS_CONFIG_SCOPE`
- Default: `system`

#### mas_workspace_id
This is only used when both `mas_config_dir` and `mas_instance_id` are set, and `mas_config_scope` is set to either `ws` or `wsapp`

- **Optional**
- Environment Variable: `MAS_WORKSPACE_ID`
- Default: None

#### mas_application_id
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

**Purpose**: Specifies the local filesystem directory for storing Db2 backup files and metadata. This directory serves as the staging area for all backup and restore operations.

**When to use**:
- Always required when performing backup or restore operations
- Must be accessible from the system running the Ansible playbook
- Should have sufficient disk space for database backups

**Valid values**: Any valid local filesystem path (e.g., `/tmp/mas_backups`, `/backup/db2`)

**Impact**:
- Backup files and metadata are stored in subdirectories under this path
- Directory structure: `<mas_backup_dir>/backup-<version>-db2u/`
- Insufficient space will cause backup failures

**Related variables**:
- `db2_backup_version`: Used to create versioned backup subdirectories
- `backup_vendor`: When set to `s3`, database backups go to S3 but instance resources still use this directory

**Example**: `/tmp/masbr`

### db2_backup_version
The backup version timestamp identifier for backup and restore operations.

- **Required** for `restore` and `restore_database` actions
- **Auto-generated** for backup operations
- Environment Variable: `DB2_BACKUP_VERSION`
- Default: Auto-generated in format `YYYYMMDD-HHMMSS`

**Purpose**: Uniquely identifies a specific backup version using a timestamp. This allows multiple backups to coexist and enables point-in-time restore operations.

**When to use**:
- Automatically generated during backup (no need to set manually)
- Must be specified when restoring to identify which backup to use
- Must be specified when installing Db2 from an existing backup

**Valid values**: Timestamp string in format `YYYYMMDD-HHMMSS` (e.g., `20251212-021316` for December 12, 2025 at 02:13:16)

**Impact**:
- Determines the backup directory name: `backup-<version>-db2u`
- Used to locate backup files during restore operations
- Recorded in backup metadata file for verification

**Related variables**:
- `mas_backup_dir`: Parent directory containing versioned backups
- `db2_action`: Required when action is `restore_database` or `restore`(instance & database)

**Example**: `20251212-021316`

### override_storageclass
Controls whether to override storage classes during Db2 installation from backup.
Only used in Db2 instance restore.

- **Optional**
- Environment Variable: `OVERRIDE_STORAGECLASS`
- Default: `false`

**Purpose**: Allows changing storage classes when restoring Db2 to a different cluster or when the original storage classes are not available. When enabled, uses specified storage class variables or cluster defaults instead of backup metadata values.

**When to use**:
- Set to `true` when restoring to a cluster with different storage classes
- Set to `true` when original storage classes are not available in target cluster
- Leave as `false` to use the same storage classes as the original instance

**Valid values**: `true`, `false`

**Impact**:
- When `true`: Uses `DB2_META_STORAGE_CLASS`, `DB2_DATA_STORAGE_CLASS`, `DB2_BACKUP_STORAGE_CLASS`, `DB2_LOGS_STORAGE_CLASS`, `DB2_TEMP_STORAGE_CLASS` if set, otherwise uses cluster default storage classes
- When `false`: Uses storage classes from backup metadata (original instance configuration)

**Related variables**:
- `db2_meta_storage_class`: Override for metadata storage
- `db2_data_storage_class`: Override for data storage
- `db2_backup_storage_class`: Override for backup storage
- `db2_logs_storage_class`: Override for logs storage
- `db2_temp_storage_class`: Override for temp storage

### backup_type
Type of backup operation to perform on the Db2 database.

- **Optional**
- Environment Variable: `DB2_BACKUP_TYPE`
- Default: `online`

**Purpose**: Determines whether the database remains available during backup. Online backups allow continued database access but may impact performance, while offline backups require downtime but complete faster.

**When to use**:
- Use `online` (default) for production systems requiring high availability
- Use `offline` when downtime is acceptable and faster backup is desired
- **Must use `offline`** if circular logging is enabled (`LOGARCHMETH1: OFF` and/or `LOGARCHMETH2: OFF`)

**Valid values**: `online`, `offline`

**Impact**:
- `online`: Database remains accessible during backup; requires archive logging enabled; may impact performance
- `offline`: Database is unavailable during backup; faster completion; works with circular logging

**Related variables**:
- `db2_database_db_config`: Check `LOGARCHMETH1` and `LOGARCHMETH2` settings to determine if online backup is supported

**Important**: If your Db2 instance has circular logging enabled (default configuration), you can only use `offline` backup type. If archive logging is enabled, you can use either type.

### backup_vendor
Storage backend for database backup files only.

- **Optional**
- Environment Variable: `BACKUP_VENDOR`
- Default: `disk`

**Purpose**: Determines where database backup files are stored. Disk storage keeps backups locally, while S3 storage sends them directly to S3-compatible object storage.

**When to use**:
- Use `disk` (default) for local backups or when S3 is not available
- Use `s3` for cloud-based backups, long-term retention, or disaster recovery scenarios

**Valid values**: `disk`, `s3`

**Impact**:
- `disk`: Database Backup files stored locally and copied to `mas_backup_dir`; requires sufficient local storage
- `s3`: Database backup sent directly to S3 bucket; instance resources still stored locally; requires S3 credentials

**Related variables**:
- When `s3`: Requires `backup_s3_endpoint`, `backup_s3_bucket`, `backup_s3_access_key`, `backup_s3_secret_key`
- `mas_backup_dir`: Always required for metadata and instance resources

**Note**: Instance resources (secrets, certificates, CRs) are always stored locally in `mas_backup_dir`, regardless of vendor setting. Only database backup files go to S3.

**Purpose**: Determines if Kubernetes resources (secrets, certificates, Db2uCluster CR, etc.) are backed up along with the database. When `false`, enables full disaster recovery by backing up both instance configuration and data.

**When to use**:
- Set to `false` when you need complete disaster recovery capability (instance + database)
- Set to `false` when migrating Db2 to a new cluster
- Leave as `true` (default) for database-only backups when instance already exists

**Valid values**: `true`, `false`

**Impact**:
- `true`: Only database data is backed up; faster backup; requires existing Db2 instance for restore
- `false`: Both instance resources and database are backed up; enables full recovery; allows install from backup

**Note**: Instance resources include: Db2uCluster CR, secrets (passwords, certificates), ConfigMaps, and other Kubernetes resources needed to recreate the Db2 instance.

### backup_s3_endpoint
S3-compatible object storage endpoint URL.

- **Required** when `backup_vendor` is `s3`
- Environment Variable: `BACKUP_S3_ENDPOINT`
- Default: None

**Purpose**: Specifies the S3 API endpoint for storing database backups. Supports AWS S3, IBM Cloud Object Storage, MinIO, and other S3-compatible services.

**When to use**:
- Required when using S3 storage for backups (`backup_vendor: s3`)
- Must be accessible from the Db2 pod

**Valid values**: HTTPS URL to S3-compatible endpoint (e.g., `https://s3.us-east.cloud-object-storage.appdomain.cloud`, `https://s3.amazonaws.com`)

**Impact**: Db2 connects to this endpoint to upload/download backup files. Incorrect endpoint will cause backup/restore failures.

**Related variables**:
- `backup_vendor`: Must be set to `s3`
- `backup_s3_bucket`: Bucket at this endpoint
- `backup_s3_access_key`, `backup_s3_secret_key`: Credentials for this endpoint

**Example**: `https://s3.us-east.cloud-object-storage.appdomain.cloud`

### backup_s3_bucket
S3 bucket name for storing database backups.

- **Required** when `backup_vendor` is `s3`
- Environment Variable: `BACKUP_S3_BUCKET`
- Default: None

**Purpose**: Specifies the S3 bucket where database backup files will be stored. The bucket must exist and credentials must have read/write permissions.

**When to use**:
- Required when using S3 storage for backups (`backup_vendor: s3`)
- Bucket must be created before running backup

**Valid values**: Valid S3 bucket name following S3 naming conventions

**Impact**: Backup files are stored in this bucket under path `<backup_version>/`. Incorrect bucket name or insufficient permissions will cause failures.

**Related variables**:
- `backup_vendor`: Must be set to `s3`
- `backup_s3_endpoint`: S3 service hosting this bucket
- `backup_s3_access_key`, `backup_s3_secret_key`: Must have permissions for this bucket

**Example**: `mas-db2-backups`

### backup_s3_access_key
S3 access key ID for authentication.

- **Required** when `backup_vendor` is `s3`
- Environment Variable: `BACKUP_S3_ACCESS_KEY`
- Default: None

**Purpose**: Provides the access key ID for authenticating to S3-compatible object storage. Used together with secret key for S3 API authentication.

**When to use**:
- Required when using S3 storage for backups (`backup_vendor: s3`)
- Must have read/write permissions to the specified bucket

**Valid values**: Valid S3 access key ID from your S3 provider

**Impact**: Used for S3 authentication. Invalid credentials will cause backup/restore to fail with authentication errors.

**Related variables**:
- `backup_vendor`: Must be set to `s3`
- `backup_s3_secret_key`: Corresponding secret key
- `backup_s3_bucket`: Bucket these credentials can access

**Security**: Store securely using Ansible Vault or environment variables. Never commit to version control.

### backup_s3_secret_key
S3 secret access key for authentication.

- **Required** when `backup_vendor` is `s3`
- Environment Variable: `BACKUP_S3_SECRET_KEY`
- Default: None

**Purpose**: Provides the secret access key for authenticating to S3-compatible object storage. Used together with access key for S3 API authentication.

**When to use**:
- Required when using S3 storage for backups (`backup_vendor: s3`)
- Must correspond to the access key ID

**Valid values**: Valid S3 secret access key from your S3 provider

**Impact**: Used for S3 authentication. Invalid credentials will cause backup/restore to fail with authentication errors.

**Related variables**:
- `backup_vendor`: Must be set to `s3`
- `backup_s3_access_key`: Corresponding access key ID
- `backup_s3_bucket`: Bucket these credentials can access

**Security**: Store securely using Ansible Vault or environment variables. Never commit to version control.

### backup_s3_alias
Db2 storage access alias name for S3 configuration.

- **Optional**
- Environment Variable: `BACKUP_S3_ALIAS`
- Default: `S3DB2COS`

**Purpose**: Defines the alias name used in Db2's storage access configuration for S3. This is an internal Db2 identifier for the S3 connection.

**When to use**:
- Usually leave as default unless you have specific Db2 storage access naming requirements
- Change only if you need to match existing Db2 storage access configurations

**Valid values**: Valid Db2 storage access alias name (alphanumeric, no spaces)

**Impact**: Used internally by Db2 to reference the S3 storage configuration. Changing this is rarely necessary.

**Related variables**:
- `backup_vendor`: Only used when set to `s3`

**Default**: `S3DB2COS`


Example Usage - Backup and Restore
-------------------------------------------------------------------------------

### Backup Db2 Database to Disk
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_backup_dir: /tmp/masbr
    db2_action: backup_database
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
    db2_action: backup_database
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
    db2_namespace: db2u
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
    db2_backup_version: 20251212-021316
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
    db2_backup_version: 20251212-021316
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

### Restore Db2 from Backup (Instance + Database)
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    db2_action: restore
    mas_instance_id: masinst1
    db2_backup_version: 20251212-021316
    mas_backup_dir: /tmp/masbr
    backup_vendor: disk
  roles:
    - ibm.mas_devops.db2
```

### Restore Db2 from Backup (Instance + Database) w/ storage class override
# This will override the storage class for all Db2 PVCs
# If you want to override specific PVCs, use the following variables:
# db2_meta_storage_class, db2_data_storage_class, db2_backup_storage_class, db2_logs_storage_class, db2_temp_storage_class
# or cluster's default storage class will be used to override.
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    db2_action: restore
    mas_instance_id: masinst1
    db2_backup_version: 20251212-021316
    mas_backup_dir: /tmp/masbr
    backup_vendor: disk
    override_storageclass: true
    db2_meta_storage_class: nfs-client # optional 
    db2_data_storage_class: nfs-client # optional
    db2_backup_storage_class: nfs-client # optional
    db2_logs_storage_class: nfs-client # optional
    db2_temp_storage_class: nfs-client # optional
  roles:
    - ibm.mas_devops.db2
```

### Restore Db2 from Backup (Instance + Database(S3))
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    db2_action: restore
    mas_instance_id: masinst1
    db2_backup_version: 20251212-021316
    mas_backup_dir: /tmp/masbr
    backup_vendor: s3
    backup_s3_endpoint: https://s3.us-east.cloud-object-storage.appdomain.cloud
    backup_s3_bucket: mas-db2-backups # your bucket name
    backup_s3_access_key: "{{ lookup('env', 'S3_ACCESS_KEY') }}"
    backup_s3_secret_key: "{{ lookup('env', 'S3_SECRET_KEY') }}"
  roles:
    - ibm.mas_devops.db2
```

### Backup Directory Structure (Disk)
```
/tmp/masbr/
└── backup-<YYYYMMDD-HHMMSS>-db2u/
    ├── data/
    │   ├── db2-BLUDB-backup-<YYYYMMDD-HHMMSS>.tar.gz
    │   └── db2-backup-info.yaml
    └── resources/
        ├── db2uclusters/
        ├── secrets/
        ├── certificates/
        └── issuers/
        └── {kind}s/
```

### Database backup Metadata (db2-backup-info.yaml)
```yaml
source_db2_backup_version: "20251212-021316"
source_db2_backup_timestamp: "20251212021316"
source_db2_instance_name: "db2u-manage"
source_db2_instance_version: "11.5.8.0-cn7"
database: "BLUDB"
backup_vendor: "disk"
vendor_backup_path: "/mnt/backup/20251212-021316/data"
local_backup_path: "/tmp/masbr/backup-20251212-021316-db2u/data/db2-BLUDB-backup-20251212-021316.tar.gz"
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
