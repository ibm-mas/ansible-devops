# mongodb

This role currently supports provisioning of mongodb in four different providers:
 - community
 - aws (documentdb)
 - ibm
 - atlas (MongoDB Atlas)

If the selected provider is `community` then the [MongoDB Community Kubernetes Operator](https://github.com/mongodb/mongodb-kubernetes-operator) will be configured and deployed into the specified namespace. By default a three member MongoDB replica set will be created.  The cluster will bind six PVCs, these provide persistence for the data and system logs across the three nodes.  Currently there is no support built-in for customizing the cluster beyond this configuration.

!!! tip
    The role will generate a yaml file containing the definition of a Secret and MongoCfg resource that can be used to configure the deployed instance as the MAS system MongoDb.

    This file can be directly applied using `oc apply -f $MAS_CONFIG_DIR/mongocfg-mongoce-system.yaml` or used in conjunction with the [suite_config](suite_config.md) role.


## Prerequisites
To run this role with providers as `ibm` or `aws` you must have already installed the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).
Also, you need to have AWS user credentials configured via `aws configure` command or simply export `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables with your corresponding AWS username credentials prior running this role when provider is either `ibm` or `aws`.

To run the `docdb_secret_rotate` MONGODB_ACTION when the provider is `aws` you must have already installed the [Mongo Shell](https://www.mongodb.com/docs/mongodb-shell/install/).

This role will install a GrafanaDashboard used for monitoring the MongoDB instance when the provided is `community` and you have run the [grafana role](https://ibm-mas.github.io/ansible-devops/roles/grafana/) previously. If you did not run the [grafana role](https://ibm-mas.github.io/ansible-devops/roles/grafana/) then the GrafanaDashboard won't be installed.


## Role Variables

### Common Variables

#### mas_instance_id
Unique identifier for the MAS instance that will use this MongoDB deployment.

- **Optional**
- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

**Purpose**: Identifies which MAS instance this MongoDB configuration targets. Used to generate the MongoCfg resource that connects MAS to the MongoDB instance.

**When to use**:
- Set when you want to automatically generate MongoCfg for MAS integration
- Must be set together with `mas_config_dir` for MongoCfg generation
- Leave unset if manually managing MongoDB configuration for MAS

**Valid values**: Lowercase alphanumeric string, 3-12 characters (e.g., `prod`, `dev`, `inst1`)

**Impact**: When set with `mas_config_dir`, generates a MongoCfg YAML file at `$MAS_CONFIG_DIR/mongocfg-mongoce-system.yaml`. Without this, no MAS configuration file is created.

**Related variables**: Must be set together with `mas_config_dir` for MongoCfg generation.

#### mas_config_dir
Local directory path where the generated MongoCfg resource file will be saved.

- **Optional**
- Environment Variable: `MAS_CONFIG_DIR`
- Default Value: None

**Purpose**: Specifies where to save the MongoCfg YAML file that configures MAS to connect to this MongoDB instance. This file can be applied manually or used with the `suite_config` role for automated MAS configuration.

**When to use**:
- Set when you want to automatically generate MongoCfg for MAS integration
- Must be set together with `mas_instance_id` for MongoCfg generation
- Use the same directory across multiple dependency roles (mongodb, db2, sls) to collect all configurations
- Leave unset if manually managing MongoDB configuration for MAS

**Valid values**: Any valid local filesystem path (e.g., `/home/user/masconfig`, `~/masconfig`, `./config`)

**Impact**: When set with `mas_instance_id`, creates file `mongocfg-mongoce-system.yaml` in this directory. The file contains Secret and MongoCfg resources ready to apply to MAS.

**Related variables**:
- Must be set together with `mas_instance_id` for MongoCfg generation
- Used by `suite_config` role to apply configurations

#### mongodb_provider
Selects which MongoDB deployment option to use for MAS database requirements.

- **Optional**
- Environment Variable: `MONGODB_PROVIDER`
- Default Value: `community`

**Purpose**: Determines the MongoDB infrastructure provider, which affects deployment architecture, management approach, operational requirements, and cost model. Each provider offers different trade-offs between control, convenience, and cost.

**When to use**:
- Use `community` for self-managed deployments on OpenShift with full control
- Use `ibm` for managed IBM Cloud Databases for MongoDB service
- Use `aws` for managed AWS DocumentDB service (MongoDB-compatible)
- Consider operational expertise, cloud platform, and management preferences

**Valid values**:
- `community` - MongoDB Community Edition Operator (self-managed on OpenShift)
- `ibm` - IBM Cloud Databases for MongoDB (managed service)
- `aws` - AWS DocumentDB (managed service, MongoDB-compatible)

**Impact**:
- `community`: Requires cluster storage, manual backup management, and operational overhead
- `ibm`: Requires IBM Cloud account, API key, and incurs IBM Cloud service charges
- `aws`: Requires AWS account, VPC configuration, and incurs AWS service charges

**Related variables**:
- When `community`: Requires `mongodb_storage_class` and related storage/resource variables
- When `ibm`: Requires `ibmcloud_apikey`, `ibm_mongo_region`, `ibm_mongo_resourcegroup`
- When `aws`: Requires `aws_access_key_id`, `aws_secret_access_key`, `vpc_id`, `docdb_*` variables
- Affects which `mongodb_action` values are supported

**Note**: Provider cannot be changed after initial deployment. Migration between providers requires backup and restore procedures.

#### mongodb_action
Specifies which operation to perform on the MongoDB instance.

- **Optional**
- Environment Variable: `MONGODB_ACTION`
- Default Value: `install`

**Purpose**: Controls what action the role executes against the MongoDB instance. Different providers support different sets of actions based on their capabilities and management model.

**When to use**:
- Use `install` for initial deployment or updates
- Use `uninstall` to remove MongoDB instance (use with caution)
- Use `backup` to create MongoDB backups (community/ibm only)
- Use `restore` to restore from backup (community/ibm only)
- Use `docdb_secret_rotate` to rotate DocumentDB credentials (aws only)
- Use `destroy-data` to delete all data from MongoDB (aws only)
- Use `create-mongo-service-credentials` to generate service credentials (ibm only)

**Valid values** (provider-specific):
- **community**: `install`, `uninstall`, `backup`, `restore`
- **aws**: `install`, `uninstall`, `docdb_secret_rotate`, `destroy-data`
- **ibm**: `install`, `uninstall`, `backup`, `restore`, `create-mongo-service-credentials`

**Impact**: The action determines what the role will do. Destructive actions like `uninstall` and `destroy-data` will permanently delete data. Backup/restore actions require additional variables to be set.

**Related variables**:
- `mongodb_provider` determines which actions are available
- Backup actions require `masbr_*` variables
- Restore actions require `masbr_restore_from_version`
- AWS secret rotation requires `docdb_*` credential variables

**Note**: Always backup data before performing destructive operations. Some actions are irreversible.

### CE Operator Variables

#### mongodb_namespace
OpenShift namespace where the MongoDB Community Operator and MongoDB cluster will be deployed.

- **Optional**
- Environment Variable: `MONGODB_NAMESPACE`
- Default Value: `mongoce`

**Purpose**: Defines the Kubernetes namespace for MongoDB resources, providing isolation and organization for the MongoDB deployment within the cluster.

**When to use**:
- Use default `mongoce` for standard deployments
- Change only if you need multiple MongoDB instances or have namespace naming requirements
- Ensure namespace doesn't conflict with existing deployments

**Valid values**: Any valid Kubernetes namespace name (lowercase alphanumeric and hyphens)

**Impact**: All MongoDB resources (operator, replica set pods, PVCs, secrets, services) will be created in this namespace. Changing this after deployment requires reinstallation.

**Related variables**: Used in MongoCfg generation to reference MongoDB service endpoints.

#### mongodb_version
Specifies the MongoDB version to deploy.

- **Optional**
- Environment Variable: `MONGODB_VERSION`
- Default Value: Automatically defined by the mongo version specified in the [latest MAS case bundle available](https://github.com/ibm-mas/python-devops/tree/stable/src/mas/devops/data/catalogs)

**Purpose**: Controls which MongoDB version is deployed, ensuring compatibility with MAS requirements and enabling version-specific features. The default aligns with the tested and supported version for your MAS release.

**When to use**:
- Leave as default for standard deployments (recommended)
- Override only when specific version requirements exist
- Use for testing compatibility with newer MongoDB versions
- Never use to downgrade an existing MongoDB instance

**Valid values**: `7.0.12`, `7.0.22`, `7.0.23`, `8.0.13`, `8.0.17` (check MAS compatibility matrix for supported versions)

**Impact**: Determines MongoDB feature set, performance characteristics, and compatibility. Changing versions may require data migration or compatibility testing.

**Related variables**:
- Version upgrades require corresponding `mongodb_v*_upgrade` flags
- Must be compatible with MAS version requirements

**Note**: **Never downgrade MongoDB versions**. Always create scheduled backups before version changes. Use `mongodb_v5_upgrade`, `mongodb_v6_upgrade`, `mongodb_v7_upgrade`, or `mongodb_v8_upgrade` flags when upgrading between major versions.

#### mongodb_override_spec
Forces the role to use environment variables instead of preserving existing MongoDB spec settings.

- **Optional**
- Environment Variable: `MONGODB_OVERRIDE_SPEC`
- Default Value: `false`

**Purpose**: Controls whether the role preserves existing MongoDB configuration during upgrades/reinstalls or applies new values from environment variables. This prevents accidental configuration changes during routine operations.

**When to use**:
- Leave as `false` (default) to preserve existing settings during upgrades
- Set to `true` only when intentionally changing MongoDB configuration
- Use with caution - requires setting all environment variables to match desired state

**Valid values**: `true`, `false`

**Impact**:
- When `false`: Existing CPU, memory, storage, and replica settings are preserved during reinstall/upgrade
- When `true`: All settings are taken from environment variables; unset variables revert to defaults

**Related variables**: When set to `true`, affects these settings:
- `mongodb_cpu_limits`
- `mongodb_mem_limits`
- `mongodb_cpu_requests`
- `mongodb_mem_requests`
- `mongodb_storage_class`
- `mongodb_storage_capacity_data`
- `mongodb_storage_capacity_logs`
- `mongodb_replicas`

**Note**: **Check existing MongoDB installation before enabling**. If environment variables don't match current spec, resources may be reset to defaults, potentially causing disruption. Unknown settings are not preserved.

#### mongodb_storage_class
Name of the Kubernetes storage class for MongoDB persistent volumes.

- **Required** when `mongodb_provider=community`
- Environment Variable: `MONGODB_STORAGE_CLASS`
- Default Value: None

**Purpose**: Specifies which storage class provides persistent volumes for MongoDB data and logs. The storage class determines performance characteristics, availability, and cost of MongoDB storage.

**When to use**:
- Always required for Community Edition deployments
- Choose based on performance requirements (SSD vs HDD)
- Consider backup and snapshot capabilities of the storage class
- Verify storage class exists in your cluster before deployment

**Valid values**: Any valid storage class name in your cluster that supports ReadWriteOnce (RWO) access mode

**Impact**: Affects MongoDB performance, reliability, and cost. Six PVCs will be created (data + logs for each of 3 replicas by default). Storage class cannot be changed after deployment without data migration.

**Related variables**:
- `mongodb_storage_capacity_data` - Size of data PVCs
- `mongodb_storage_capacity_logs` - Size of log PVCs
- `mongodb_replicas` - Number of replica sets (affects total PVC count)

**Note**: Storage class must support ReadWriteOnce (RWO) access mode. Verify with `oc get storageclass` before deployment.

#### mongodb_storage_capacity_data
Size of the persistent volume claim (PVC) for MongoDB data storage on each replica set member.

- **Optional**
- Environment Variable: `MONGODB_STORAGE_CAPACITY_DATA`
- Default Value: `20Gi`

**Purpose**: Determines disk space allocated for storing MongoDB databases, collections, and indexes on each replica. Proper sizing prevents storage exhaustion and ensures adequate space for data growth.

**When to use**:
- Increase from default for production environments with large data volumes
- Increase for environments with high data growth rates
- Use default (20Gi) for development, testing, or small deployments
- Consider backup strategy when sizing (larger volumes take longer to backup)

**Valid values**: Any valid Kubernetes storage size (e.g., `20Gi`, `100Gi`, `500Gi`, `1Ti`)

**Impact**:
- Larger values consume more cluster storage resources
- Cannot be decreased after deployment (PVC expansion only)
- Total storage = this value × number of replicas
- Affects backup and restore duration

**Related variables**:
- `mongodb_replicas`: Total storage = capacity × replicas
- `mongodb_storage_class`: Must support volume expansion if you plan to increase size later
- `mongodb_storage_capacity_logs`: Consider balancing data and log storage

**Note**: PVCs can be expanded but not shrunk. Plan for growth when setting initial size. Monitor storage usage to avoid running out of space.

#### mongodb_storage_capacity_logs
Size of the persistent volume claim (PVC) for MongoDB log storage on each replica set member.

- **Optional**
- Environment Variable: `MONGODB_STORAGE_CAPACITY_LOGS`
- Default Value: `20Gi`

**Purpose**: Determines disk space allocated for MongoDB operational logs on each replica. Logs are essential for troubleshooting, auditing, and monitoring MongoDB operations.

**When to use**:
- Increase for production environments with verbose logging requirements
- Increase if log retention policies require longer history
- Use default (20Gi) for standard deployments
- Consider log rotation and retention policies when sizing

**Valid values**: Any valid Kubernetes storage size (e.g., `10Gi`, `20Gi`, `50Gi`)

**Impact**:
- Larger values consume more cluster storage resources
- Cannot be decreased after deployment (PVC expansion only)
- Total log storage = this value × number of replicas
- Insufficient log space can cause MongoDB operational issues

**Related variables**:
- `mongodb_replicas`: Total log storage = capacity × replicas
- `mongodb_storage_class`: Must support volume expansion
- `mongodb_storage_capacity_data`: Consider balancing data and log storage

**Note**: Monitor log usage and implement log rotation to prevent filling log volumes. PVCs can be expanded but not shrunk.

#### mongodb_cpu_limits
Maximum CPU cores allocated to each MongoDB container.

- **Optional**
- Environment Variable: `MONGODB_CPU_LIMITS`
- Default Value: `1`

**Purpose**: Sets the upper bound on CPU usage for MongoDB containers, preventing any single MongoDB instance from consuming excessive cluster CPU resources.

**When to use**:
- Increase for production workloads with high query volumes
- Increase for large datasets requiring more processing power
- Use default (1 core) for development or light workloads
- Set higher than `mongodb_cpu_requests` to allow burst capacity

**Valid values**: CPU units as decimal (e.g., `0.5`, `1`, `2`, `4`) or millicores (e.g., `500m`, `1000m`, `2000m`)

**Impact**:
- Higher limits allow better performance under load but consume more cluster resources
- Limits prevent MongoDB from starving other workloads of CPU
- Total CPU limit = this value × number of replicas
- Setting too low can cause performance degradation

**Related variables**:
- `mongodb_cpu_requests`: Should be set lower than limits for burst capacity
- `mongodb_replicas`: Total CPU = limits × replicas
- `mongodb_mem_limits`: Balance CPU and memory allocation

**Note**: Ensure cluster has sufficient CPU capacity for all replicas. Monitor actual CPU usage to right-size limits.

#### mongodb_mem_limits
Maximum memory allocated to each MongoDB container.

- **Optional**
- Environment Variable: `MONGODB_MEM_LIMITS`
- Default Value: `1Gi`

**Purpose**: Sets the upper bound on memory usage for MongoDB containers. MongoDB uses memory for caching data and indexes, so adequate memory is critical for performance.

**When to use**:
- Increase significantly for production workloads (4Gi-8Gi recommended)
- Increase for large datasets to improve cache hit rates
- Default (1Gi) is only suitable for development/testing
- Set higher than `mongodb_mem_requests` to allow burst capacity

**Valid values**: Memory size (e.g., `1Gi`, `2Gi`, `4Gi`, `8Gi`, `16Gi`)

**Impact**:
- Higher limits improve performance through better caching
- Limits prevent MongoDB from consuming all cluster memory
- Total memory limit = this value × number of replicas
- Setting too low causes frequent cache evictions and poor performance

**Related variables**:
- `mongodb_mem_requests`: Should be set lower than limits
- `mongodb_replicas`: Total memory = limits × replicas
- `mongodb_cpu_limits`: Balance CPU and memory allocation

**Note**: MongoDB performance heavily depends on available memory. Production deployments typically need 4Gi-8Gi per replica. Monitor memory usage and adjust accordingly.

#### mongodb_cpu_requests
Guaranteed CPU cores reserved for each MongoDB container.

- **Optional**
- Environment Variable: `MONGODB_CPU_REQUESTS`
- Default Value: `500m`

**Purpose**: Defines the minimum CPU resources guaranteed to MongoDB containers. Kubernetes scheduler uses this to place pods on nodes with sufficient available CPU.

**When to use**:
- Increase for production workloads requiring consistent performance
- Set to match expected baseline CPU usage
- Use default (500m) for development or light workloads
- Set lower than `mongodb_cpu_limits` to allow burst capacity

**Valid values**: CPU units as decimal (e.g., `0.5`, `1`, `2`) or millicores (e.g., `500m`, `1000m`, `2000m`)

**Impact**:
- Higher requests guarantee more CPU but may limit pod scheduling if cluster capacity is constrained
- Requests ensure MongoDB has minimum CPU even under cluster load
- Total CPU request = this value × number of replicas
- Affects pod Quality of Service (QoS) class

**Related variables**:
- `mongodb_cpu_limits`: Requests should be lower than limits
- `mongodb_replicas`: Total CPU requests = this value × replicas
- `mongodb_mem_requests`: Balance CPU and memory requests

**Note**: Set requests based on baseline usage, not peak. The difference between requests and limits provides burst capacity.

#### mongodb_mem_requests
Guaranteed memory reserved for each MongoDB container.

- **Optional**
- Environment Variable: `MONGODB_MEM_REQUESTS`
- Default Value: `1Gi`

**Purpose**: Defines the minimum memory resources guaranteed to MongoDB containers. Kubernetes scheduler uses this to place pods on nodes with sufficient available memory.

**When to use**:
- Increase for production workloads (2Gi-4Gi recommended)
- Set to match expected baseline memory usage
- Default (1Gi) is only suitable for development/testing
- Set lower than `mongodb_mem_limits` to allow burst capacity

**Valid values**: Memory size (e.g., `1Gi`, `2Gi`, `4Gi`, `8Gi`)

**Impact**:
- Higher requests guarantee more memory but may limit pod scheduling if cluster capacity is constrained
- Requests ensure MongoDB has minimum memory even under cluster load
- Total memory request = this value × number of replicas
- Affects pod Quality of Service (QoS) class

**Related variables**:
- `mongodb_mem_limits`: Requests should be lower than limits
- `mongodb_replicas`: Total memory requests = this value × replicas
- `mongodb_cpu_requests`: Balance CPU and memory requests

**Note**: MongoDB needs adequate memory for good performance. Production deployments typically need 2Gi-4Gi requests. Set based on baseline usage, not peak.

#### mongodb_replicas
Number of MongoDB replica set members to deploy.

- **Optional**
- Environment Variable: `MONGODB_REPLICAS`
- Default Value: `3`

**Purpose**: Determines the size of the MongoDB replica set, which affects high availability, read scalability, and resource consumption. Replica sets provide data redundancy and automatic failover.

**When to use**:
- Use default (3) for production deployments with high availability requirements
- Set to 1 only for Single Node OpenShift (SNO) clusters or development environments
- Use 5 or more for critical production workloads requiring higher availability
- Odd numbers (1, 3, 5) are recommended for proper election quorum

**Valid values**: Positive integers, typically 1, 3, or 5

**Impact**:
- More replicas = higher availability but more resource consumption
- Each replica requires its own data and log PVCs
- Total resources = (CPU + memory + storage) × replicas
- Affects election behavior and write acknowledgment

**Related variables**:
- `mongodb_storage_capacity_data`: Total data storage = capacity × replicas
- `mongodb_storage_capacity_logs`: Total log storage = capacity × replicas
- `mongodb_cpu_limits` and `mongodb_mem_limits`: Total resources = limits × replicas

**Note**: Set to 1 for SNO clusters. Production deployments should use 3 or more for high availability. Changing replica count after deployment requires careful planning.

#### custom_labels
Comma-separated list of key=value labels to apply to MongoDB resources.

- **Optional**
- Environment Variable: `CUSTOM_LABELS`
- Default Value: None

**Purpose**: Adds Kubernetes labels to MongoDB resources for organization, selection, and filtering. Labels enable resource tracking, cost allocation, and custom automation.

**When to use**:
- Use to add organizational metadata (e.g., `cost-center=engineering`, `environment=production`)
- Use to enable resource tracking and cost allocation
- Use to support custom automation or monitoring tools
- Use to comply with organizational labeling standards

**Valid values**: Comma-separated list of `key=value` pairs (e.g., `env=prod,team=platform,app=mongodb`)

**Impact**: Labels are applied to MongoDB resources and can be used for filtering with `oc get` commands, monitoring queries, and automation scripts. Labels do not affect MongoDB functionality.

**Related variables**: Works alongside Kubernetes resource labels for comprehensive resource management.

#### mongodb_v5_upgrade
Confirmation flag to upgrade MongoDB from version 4.x to version 5.

- **Optional**
- Environment Variable: `MONGODB_V5_UPGRADE`
- Default Value: `false`

**Purpose**: Acts as a safety confirmation to prevent accidental MongoDB major version upgrades. Upgrading MongoDB major versions requires careful planning and testing.

**When to use**:
- Set to `true` only when intentionally upgrading from MongoDB 4.2 or 4.4 to version 5
- Must be explicitly set to perform the upgrade
- Leave as `false` for all other operations

**Valid values**: `true`, `false`

**Impact**: When `true` and `mongodb_version` is set to a 5.x version, triggers MongoDB upgrade from 4.x to 5.x. This is a one-way operation that cannot be reversed without restoring from backup.

**Related variables**:
- `mongodb_version`: Must be set to a 5.x version for upgrade to proceed
- Other upgrade flags: `mongodb_v6_upgrade`, `mongodb_v7_upgrade`, `mongodb_v8_upgrade`

**Note**: **Always backup before upgrading**. Test upgrades in non-production environments first. Review MongoDB 5.0 release notes for breaking changes and new requirements (e.g., AVX instruction set).

#### mongodb_v6_upgrade
Confirmation flag to upgrade MongoDB from version 5 to version 6.

- **Optional**
- Environment Variable: `MONGODB_V6_UPGRADE`
- Default Value: `false`

**Purpose**: Acts as a safety confirmation to prevent accidental MongoDB major version upgrades from version 5 to 6.

**When to use**:
- Set to `true` only when intentionally upgrading from MongoDB 5 to version 6
- Must be explicitly set to perform the upgrade
- Leave as `false` for all other operations

**Valid values**: `true`, `false`

**Impact**: When `true` and `mongodb_version` is set to a 6.x version, triggers MongoDB upgrade from 5.x to 6.x. This is a one-way operation that cannot be reversed without restoring from backup.

**Related variables**:
- `mongodb_version`: Must be set to a 6.x version for upgrade to proceed
- Other upgrade flags: `mongodb_v5_upgrade`, `mongodb_v7_upgrade`, `mongodb_v8_upgrade`

**Note**: **Always backup before upgrading**. Test upgrades in non-production environments first. Review MongoDB 6.0 release notes for breaking changes.

#### mongodb_v7_upgrade
Confirmation flag to upgrade MongoDB from version 6 to version 7.

- **Optional**
- Environment Variable: `MONGODB_V7_UPGRADE`
- Default Value: `false`

**Purpose**: Acts as a safety confirmation to prevent accidental MongoDB major version upgrades from version 6 to 7.

**When to use**:
- Set to `true` only when intentionally upgrading from MongoDB 6 to version 7
- Must be explicitly set to perform the upgrade
- Leave as `false` for all other operations

**Valid values**: `true`, `false`

**Impact**: When `true` and `mongodb_version` is set to a 7.x version, triggers MongoDB upgrade from 6.x to 7.x. This is a one-way operation that cannot be reversed without restoring from backup.

**Related variables**:
- `mongodb_version`: Must be set to a 7.x version for upgrade to proceed
- Other upgrade flags: `mongodb_v5_upgrade`, `mongodb_v6_upgrade`, `mongodb_v8_upgrade`

**Note**: **Always backup before upgrading**. Test upgrades in non-production environments first. Review MongoDB 7.0 release notes for breaking changes.

#### mongodb_v8_upgrade
Confirmation flag to upgrade MongoDB from version 7 to version 8.

- **Optional**
- Environment Variable: `MONGODB_V8_UPGRADE`
- Default Value: `false`

**Purpose**: Acts as a safety confirmation to prevent accidental MongoDB major version upgrades from version 7 to 8.

**When to use**:
- Set to `true` only when intentionally upgrading from MongoDB 7 to version 8
- Must be explicitly set to perform the upgrade
- Leave as `false` for all other operations

**Valid values**: `true`, `false`

**Impact**: When `true` and `mongodb_version` is set to an 8.x version, triggers MongoDB upgrade from 7.x to 8.x. This is a one-way operation that cannot be reversed without restoring from backup.

**Related variables**:
- `mongodb_version`: Must be set to an 8.x version for upgrade to proceed
- Other upgrade flags: `mongodb_v5_upgrade`, `mongodb_v6_upgrade`, `mongodb_v7_upgrade`

**Note**: **Always backup before upgrading**. Test upgrades in non-production environments first. Review MongoDB 8.0 release notes for breaking changes.

#### masbr_confirm_cluster
Enables cluster confirmation prompt before executing backup or restore operations.

- **Optional**
- Environment Variable: `MASBR_CONFIRM_CLUSTER`
- Default: `false`

**Purpose**: Provides a safety check to confirm you're connected to the correct cluster before performing backup or restore operations, preventing accidental operations on wrong clusters.

**When to use**:
- Set to `true` in environments with multiple clusters to prevent mistakes
- Set to `true` for production environments as an additional safety measure
- Leave as `false` for automated pipelines where confirmation isn't possible

**Valid values**: `true`, `false`

**Impact**: When `true`, the role will prompt for confirmation of the cluster before proceeding with backup/restore. This adds a manual step but prevents costly mistakes.

**Related variables**: Used with `mongodb_action` when set to `backup` or `restore`.

#### masbr_copy_timeout_sec
Timeout in seconds for backup/restore file transfer operations.

- **Optional**
- Environment Variable: `MASBR_COPY_TIMEOUT_SEC`
- Default: `43200` (12 hours)

**Purpose**: Sets the maximum time allowed for copying backup files to/from storage. Prevents operations from hanging indefinitely on slow networks or large datasets.

**When to use**:
- Increase for very large databases or slow network connections
- Decrease for smaller databases to fail faster on issues
- Use default (12 hours) for most deployments

**Valid values**: Positive integer representing seconds (e.g., `3600` = 1 hour, `43200` = 12 hours, `86400` = 24 hours)

**Impact**: Operations exceeding this timeout will fail. Setting too low causes failures on legitimate long-running transfers. Setting too high delays detection of stuck operations.

**Related variables**: Used with `mongodb_action` when set to `backup` or `restore`.

**Note**: Consider database size and network speed when setting timeout. Monitor actual transfer times to optimize this value.

#### masbr_job_timezone
Time zone for scheduled backup job execution.

- **Optional**
- Environment Variable: `MASBR_JOB_TIMEZONE`
- Default: None (uses UTC)

**Purpose**: Specifies the time zone for scheduled backup CronJobs, ensuring backups run at the intended local time rather than UTC.

**When to use**:
- Set when scheduling backups to run at specific local times
- Use for compliance with backup windows in specific time zones
- Leave unset to use UTC (recommended for global deployments)

**Valid values**: Any valid [tz database time zone](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) (e.g., `America/New_York`, `Europe/London`, `Asia/Tokyo`)

**Impact**: Affects when scheduled backups execute. Incorrect time zone can cause backups to run during business hours or miss backup windows.

**Related variables**:
- `masbr_backup_schedule`: Defines the cron schedule
- Only applies when `masbr_backup_schedule` is set

**Note**: When not set, CronJobs use UTC time zone. Consider daylight saving time changes when scheduling backups.

#### masbr_storage_local_folder
Local filesystem path where backup files will be stored or retrieved from.

- **Required** when `mongodb_action` is `backup` or `restore`
- Environment Variable: `MASBR_STORAGE_LOCAL_FOLDER`
- Default: None

**Purpose**: Specifies the directory for storing MongoDB backup files. This location must have sufficient space and appropriate permissions for backup operations.

**When to use**:
- Always required for backup and restore operations
- Use a path with adequate storage space for full database backups
- Consider using network-attached storage for backup retention
- Ensure path is accessible and has proper permissions

**Valid values**: Any valid local filesystem path (e.g., `/backup/mongodb`, `/mnt/nfs/backups`, `/tmp/masbr`)

**Impact**: Backup files are written to this location. Insufficient space causes backup failures. Path must be accessible during restore operations.

**Related variables**:
- `masbr_backup_type`: Determines if full or incremental backups are stored here
- `masbr_restore_from_version`: Specifies which backup version to restore from this location

**Note**: Ensure adequate disk space (at least 2x database size for full backups). Implement backup retention policies to manage storage usage.

#### masbr_backup_type
Type of backup to create: full or incremental.

- **Optional**
- Environment Variable: `MASBR_BACKUP_TYPE`
- Default: `full`

**Purpose**: Determines whether to create a complete database backup or an incremental backup containing only changes since the last full backup. Incremental backups save time and storage.

**When to use**:
- Use `full` for initial backups or periodic complete backups
- Use `incr` for frequent backups between full backups to save time and space
- Implement a strategy like weekly full + daily incremental backups

**Valid values**: `full`, `incr`

**Impact**:
- `full`: Creates complete backup, takes longer, uses more storage
- `incr`: Creates incremental backup, faster, uses less storage, requires base full backup

**Related variables**:
- `masbr_backup_from_version`: Required when `incr` is used to specify base full backup
- `mongodb_action`: Must be set to `backup`

**Note**: Incremental backups require a full backup as base. Restore operations may need to apply multiple incremental backups sequentially.

#### masbr_backup_from_version
Timestamp of the full backup to use as base for incremental backup.

- **Optional**
- Environment Variable: `MASBR_BACKUP_FROM_VERSION`
- Default: None (automatically uses latest full backup)

**Purpose**: Specifies which full backup serves as the base for an incremental backup. This links the incremental backup to a specific full backup version.

**When to use**:
- Set when creating incremental backups and you want to specify a particular full backup
- Leave unset to automatically use the most recent full backup
- Only valid when `masbr_backup_type=incr`

**Valid values**: Timestamp in format `YYYYMMDDHHMMSS` (e.g., `20240621021316`)

**Impact**: Incremental backup will contain only changes since the specified full backup. Incorrect version can cause backup chain issues.

**Related variables**:
- `masbr_backup_type`: Must be set to `incr`
- `masbr_storage_local_folder`: Location where full backup exists

**Note**: If not specified, role automatically finds the latest full backup. Ensure the specified full backup exists in the storage location.

#### masbr_backup_schedule
Cron expression for scheduling automated backups.

- **Optional**
- Environment Variable: `MASBR_BACKUP_SCHEDULE`
- Default: None (creates on-demand backup)

**Purpose**: Defines when automated backups should run using standard cron syntax. Enables regular, unattended backup operations.

**When to use**:
- Set to schedule regular automated backups (e.g., daily, weekly)
- Leave unset for manual, on-demand backups
- Consider backup windows and system load when scheduling

**Valid values**: Standard [cron expression](https://en.wikipedia.org/wiki/Cron) (e.g., `0 2 * * *` for daily at 2 AM, `0 2 * * 0` for weekly on Sunday at 2 AM)

**Impact**: When set, creates a Kubernetes CronJob that automatically runs backups on schedule. Without this, backups only run when role is manually executed.

**Related variables**:
- `masbr_job_timezone`: Specifies time zone for schedule
- `masbr_backup_type`: Determines if scheduled backups are full or incremental

**Note**: Test cron expressions before deploying. Consider backup duration when scheduling to avoid overlapping backup jobs.

#### masbr_restore_from_version
Timestamp of the backup version to restore.

- **Required** when `mongodb_action=restore`
- Environment Variable: `MASBR_RESTORE_FROM_VERSION`
- Default: None

**Purpose**: Specifies which backup version to restore from. This allows point-in-time recovery to a specific backup.

**When to use**:
- Always required when performing restore operations
- Use to restore to a specific point in time
- Verify backup version exists before attempting restore

**Valid values**: Timestamp in format `YYYYMMDDHHMMSS` (e.g., `20240621021316`)

**Impact**: Restores MongoDB to the state captured in the specified backup. All data after this backup will be lost. This is a destructive operation.

**Related variables**:
- `mongodb_action`: Must be set to `restore`
- `masbr_storage_local_folder`: Location where backup exists

**Note**: **Verify backup version before restoring**. List available backups in storage location first. Restore is destructive and cannot be undone without another backup.


Role Variables - IBM Cloud
-------------------------------------------------------------------------------
#### ibm_mongo_name
Name for the IBM Cloud Databases for MongoDB instance.

- **Required** when `mongodb_provider=ibm`
- Environment Variable: `IBM_MONGO_NAME`
- Default Value: `mongo-${MAS_INSTANCE_ID}`

**Purpose**: Identifies the MongoDB database instance in IBM Cloud. This name is used for resource identification, billing, and management within IBM Cloud.

**When to use**:
- Always required when using IBM Cloud as the MongoDB provider
- Use default naming convention for consistency across MAS instances
- Customize only if organizational naming standards require it

**Valid values**: Valid IBM Cloud resource name (alphanumeric, hyphens allowed, must start with letter)

**Impact**: This name appears in IBM Cloud console, billing reports, and resource lists. Changing it after creation requires recreating the database instance.

**Related variables**:
- `mas_instance_id`: Default name includes this value
- `mongodb_provider`: Must be set to `ibm`

**Note**: Choose a descriptive name that identifies the MAS instance and environment. The name cannot be changed after creation.

#### ibm_mongo_admin_password
Administrator password for the IBM Cloud MongoDB instance.

- **Optional**
- Environment Variable: `IBM_MONGO_ADMIN_PASSWORD`
- Default Value: Auto-generated 20-character string

**Purpose**: Sets the password for the MongoDB administrator user. If not provided, a secure random password is automatically generated.

**When to use**:
- Set explicitly if you need to know the password in advance
- Leave unset to use auto-generated secure password (recommended)
- Set if integrating with external password management systems

**Valid values**: String meeting IBM Cloud password requirements (minimum length, complexity)

**Impact**: This password is used for administrative access to the MongoDB instance. Auto-generated passwords are stored in Kubernetes secrets.

**Related variables**:
- `ibm_mongo_admin_credentials_secret_name`: Secret where credentials are stored

**Note**: Auto-generated passwords are more secure. If setting manually, ensure password meets security requirements and is stored securely.

#### ibm_mongo_admin_credentials_secret_name
Name of the Kubernetes secret containing MongoDB admin credentials.

- **Optional**
- Environment Variable: `IBM_MONGO_ADMIN_CREDENTIALS_SECRET_NAME`
- Default Value: `<mongo-name>-admin-credentials`

**Purpose**: Specifies the Kubernetes secret name where MongoDB administrator credentials are stored. This secret is created automatically by the role.

**When to use**:
- Customize if organizational standards require specific secret naming
- Use default for standard deployments
- Reference this secret name in other automation

**Valid values**: Valid Kubernetes secret name

**Impact**: The secret contains admin username and password for MongoDB access. Other roles and applications reference this secret for database connectivity.

**Related variables**:
- `ibm_mongo_name`: Default secret name includes this value
- `ibm_mongo_admin_password`: Password stored in this secret

#### ibm_mongo_service_credentials_secret_name
Name of the Kubernetes secret containing MongoDB service credentials.

- **Optional**
- Environment Variable: `IBM_MONGO_SERVICE_CREDENTIALS_SECRET_NAME`
- Default Value: `<mongo-name>-service-credentials`

**Purpose**: Specifies the Kubernetes secret name where MongoDB service-level credentials are stored. These credentials are used by MAS applications to connect to MongoDB.

**When to use**:
- Customize if organizational standards require specific secret naming
- Use default for standard deployments
- Reference this secret name when configuring MAS applications

**Valid values**: Valid Kubernetes secret name

**Impact**: The secret contains connection strings and credentials for application-level MongoDB access. MAS applications use this secret to connect to the database.

**Related variables**:
- `ibm_mongo_name`: Default secret name includes this value

#### ibm_mongo_resourcegroup
IBM Cloud resource group for MongoDB instance placement.

- **Required** when `mongodb_provider=ibm`
- Environment Variable: `IBM_MONGO_RESOURCEGROUP`
- Default Value: `Default`

**Purpose**: Specifies which IBM Cloud resource group will contain the MongoDB instance. Resource groups organize IBM Cloud resources for access control and billing.

**When to use**:
- Always required when using IBM Cloud provider
- Use `Default` for simple deployments
- Specify custom resource group for organizational resource management
- Align with IBM Cloud IAM and billing structure

**Valid values**: Name of an existing IBM Cloud resource group in your account

**Impact**: Determines access control, billing allocation, and resource organization. Users need appropriate IAM permissions for the specified resource group.

**Related variables**:
- `ibmcloud_apikey`: API key must have access to the specified resource group

**Note**: Ensure the resource group exists and your API key has permissions to create resources in it.

#### ibm_mongo_region
IBM Cloud region where MongoDB instance will be deployed.

- **Required** when `mongodb_provider=ibm`
- Environment Variable: `IBM_MONGO_REGION`
- Default Value: `us-east`

**Purpose**: Specifies the geographic region for MongoDB deployment. Region selection affects latency, data residency, and availability.

**When to use**:
- Always required when using IBM Cloud provider
- Choose region closest to your OpenShift cluster for lowest latency
- Consider data residency requirements for compliance
- Use default (`us-east`) if no specific requirements

**Valid values**: Valid IBM Cloud region (e.g., `us-east`, `us-south`, `eu-gb`, `eu-de`, `jp-tok`, `au-syd`)

**Impact**: Affects network latency between OpenShift and MongoDB, data residency compliance, and regional pricing. Cannot be changed after creation.

**Related variables**:
- `ibmcloud_apikey`: API key must have access to the specified region

**Note**: Choose region carefully as it cannot be changed. Consider deploying MongoDB in the same region as your OpenShift cluster for best performance.

#### ibmcloud_apikey
IBM Cloud API key for authentication and resource management.

- **Required** when `mongodb_provider=ibm`
- Environment Variable: `IBMCLOUD_APIKEY`
- Default Value: None

**Purpose**: Provides authentication credentials for creating and managing IBM Cloud resources. The API key must have sufficient permissions to create and manage Databases for MongoDB instances.

**When to use**:
- Always required when using IBM Cloud provider
- Must have permissions for the target resource group and region
- Should be stored securely (e.g., in Ansible Vault or external secret management)

**Valid values**: Valid IBM Cloud API key string

**Impact**: This key is used to authenticate all IBM Cloud API calls. Insufficient permissions will cause deployment failures.

**Related variables**:
- `ibm_mongo_resourcegroup`: API key must have access to this resource group
- `ibm_mongo_region`: API key must have access to this region

**Note**: **Never commit API keys to source control**. Use secure secret management. Ensure the API key has appropriate IAM permissions for Databases for MongoDB service.

#### ibm_mongo_plan
IBM Cloud service plan for MongoDB instance.

- **Optional**
- Environment Variable: `IBM_MONGO_PLAN`
- Default Value: `standard`

**Purpose**: Specifies the IBM Cloud service plan tier for MongoDB. Different plans offer different performance, availability, and pricing characteristics.

**When to use**:
- Use `standard` (default) for most production deployments
- Consider `enterprise` plan for critical workloads requiring higher SLA
- Review IBM Cloud pricing and plan features before selecting

**Valid values**: `standard`, `enterprise` (check IBM Cloud documentation for current plan options)

**Impact**: Affects pricing, performance characteristics, SLA, and available features. Plan cannot be changed after creation without recreating the instance.

**Related variables**:
- `ibm_mongo_memory`, `ibm_mongo_disk`, `ibm_mongo_cpu`: Resource allocations vary by plan

**Note**: Review IBM Cloud Databases for MongoDB plan documentation for current offerings and pricing.

#### ibm_mongo_service
IBM Cloud service type identifier for MongoDB.

- **Read-only**
- Value: `databases-for-mongodb`

**Purpose**: Identifies the IBM Cloud service type. This is a fixed value used internally by the role.

**When to use**: This is set automatically by the role and should not be modified.

**Valid values**: `databases-for-mongodb`

**Impact**: Used in IBM Cloud API calls to specify the service type.

**Note**: This is a constant value and does not need to be set by users.

#### ibm_mongo_service_endpoints
Network endpoint type for MongoDB connectivity.

- **Optional**
- Environment Variable: `IBM_MONGO_SERVICE_ENDPOINTS`
- Default Value: `public`

**Purpose**: Determines whether MongoDB is accessible via public internet or private network only. Private endpoints provide better security and performance for cluster-to-database communication.

**When to use**:
- Use `public` for simple deployments or when OpenShift cluster lacks private network connectivity
- Use `private` for production deployments with private network connectivity (recommended)
- Private endpoints require IBM Cloud private network configuration

**Valid values**: `public`, `private`

**Impact**:
- `public`: MongoDB accessible over internet (requires firewall rules)
- `private`: MongoDB accessible only via IBM Cloud private network (more secure, lower latency)

**Related variables**: Network configuration must support the chosen endpoint type

**Note**: Private endpoints are recommended for production. Ensure your OpenShift cluster can reach IBM Cloud private network if using `private`.

#### ibm_mongo_version
MongoDB version to deploy in IBM Cloud.

- **Optional**
- Environment Variable: `IBM_MONGO_VERSION`
- Default Value: `4.2`

**Purpose**: Specifies which MongoDB version to deploy. Version selection affects available features, performance, and compatibility.

**When to use**:
- Use default (`4.2`) for compatibility with older MAS versions
- Specify newer version (e.g., `5.0`, `6.0`) for new deployments
- Check MAS compatibility matrix before selecting version

**Valid values**: MongoDB versions supported by IBM Cloud Databases (e.g., `4.2`, `4.4`, `5.0`, `6.0`)

**Impact**: Affects available MongoDB features, performance characteristics, and MAS compatibility. Version cannot be easily downgraded.

**Related variables**:
- Check MAS compatibility requirements before selecting version

**Note**: Verify version compatibility with your MAS version. Newer MongoDB versions may require MAS updates.

#### ibm_mongo_memory
Memory allocation per MongoDB member in MB.

- **Optional**
- Environment Variable: `IBM_MONGO_MEMORY`
- Default Value: `3840` (3.75 GB)

**Purpose**: Specifies memory allocation for each MongoDB replica set member. Memory affects caching performance and query execution.

**When to use**:
- Use default (3840 MB) for development or small deployments
- Increase for production workloads (8192 MB or higher recommended)
- Increase for large datasets to improve cache hit rates

**Valid values**: Integer in MB, minimum varies by plan (typically 1024 MB minimum)

**Impact**: Higher memory improves performance through better caching but increases costs. Total cost = memory × number of members.

**Related variables**:
- `ibm_mongo_plan`: Available memory ranges vary by plan
- `ibm_mongo_disk`: Balance memory and disk allocation

**Note**: IBM Cloud charges based on allocated memory. Production deployments typically need 8GB+ per member.

#### ibm_mongo_disk
Disk storage allocation per MongoDB member in MB.

- **Optional**
- Environment Variable: `IBM_MONGO_DISK`
- Default Value: `30720` (30 GB)

**Purpose**: Specifies disk storage for each MongoDB replica set member. Storage holds databases, indexes, and operational logs.

**When to use**:
- Use default (30 GB) for development or small datasets
- Increase for production workloads based on data volume
- Plan for data growth and backup storage needs

**Valid values**: Integer in MB, minimum varies by plan (typically 5120 MB minimum)

**Impact**: Affects storage capacity and costs. Disk can be expanded but not shrunk. Total storage = disk × number of members.

**Related variables**:
- `ibm_mongo_plan`: Available disk ranges vary by plan
- `ibm_mongo_memory`: Balance memory and disk allocation

**Note**: Plan for data growth. Disk can be expanded online but cannot be reduced. Monitor storage usage to avoid running out of space.

#### ibm_mongo_cpu
Dedicated CPU cores per MongoDB member.

- **Optional**
- Environment Variable: `IBM_MONGO_CPU`
- Default Value: `0` (shared CPU)

**Purpose**: Specifies dedicated CPU cores for each MongoDB member. Dedicated CPUs provide consistent performance but increase costs.

**When to use**:
- Use `0` (default) for shared CPU, suitable for development and light workloads
- Set to `3` or higher for production workloads requiring consistent performance
- Dedicated CPUs recommended for production environments

**Valid values**: `0` (shared), or integer ≥ 3 for dedicated CPUs

**Impact**:
- `0`: Shared CPU, lower cost, variable performance
- `≥3`: Dedicated CPUs, higher cost, consistent performance

**Related variables**:
- `ibm_mongo_plan`: CPU options vary by plan
- `ibm_mongo_memory`: Balance CPU and memory allocation

**Note**: Dedicated CPUs significantly increase costs but provide predictable performance. Production workloads typically need dedicated CPUs.

#### ibm_mongo_backup_id
IBM Cloud backup CRN (Cloud Resource Name) for restore operations.

- **Required** when `is_restore=true`
- Environment Variable: `IBM_MONGO_BACKUP_ID`
- Default Value: None

**Purpose**: Specifies the IBM Cloud backup resource to restore from. The CRN uniquely identifies a specific backup in IBM Cloud.

**When to use**:
- Required only when restoring from an IBM Cloud backup
- Obtain CRN from IBM Cloud console or CLI
- Leave unset for new deployments

**Valid values**: Valid IBM Cloud CRN for a MongoDB backup (format: `crn:v1:...`)

**Impact**: Restores MongoDB to the state captured in the specified backup. All current data will be replaced.

**Related variables**:
- `is_restore`: Must be set to `true`
- `restored_mongodb_service_name`: Name for the restored service

**Note**: **Verify backup CRN before restoring**. Restore is destructive and replaces all current data. Test restore procedures in non-production first.

#### is_restore
Flag to enable restore from IBM Cloud backup.

- **Optional**
- Environment Variable: `IS_RESTORE`
- Default Value: `false`

**Purpose**: Controls whether to create a new MongoDB instance or restore from an existing backup. Acts as a safety flag to prevent accidental restores.

**When to use**:
- Set to `true` only when intentionally restoring from backup
- Leave as `false` (default) for new deployments
- Must be explicitly set to perform restore

**Valid values**: `true`, `false`

**Impact**: When `true`, creates MongoDB instance from backup instead of fresh deployment. Requires `ibm_mongo_backup_id` and `restored_mongodb_service_name`.

**Related variables**:
- `ibm_mongo_backup_id`: Required when `true`
- `restored_mongodb_service_name`: Required when `true`

**Note**: **Always verify backup details before setting to `true`**. Restore operations cannot be undone without another backup.

#### restored_mongodb_service_name
Name for the MongoDB service when restoring from backup.

- **Required** when `is_restore=true`
- Environment Variable: `RESTORED_MONGODB_SERVICE_NAME`
- Default Value: None

**Purpose**: Specifies the name for the new MongoDB service created from backup. This allows restoring to a different service name than the original.

**When to use**:
- Required only when `is_restore=true`
- Can be same as or different from original service name
- Use different name to restore alongside existing instance for testing

**Valid values**: Valid IBM Cloud resource name

**Impact**: The restored MongoDB instance will have this name in IBM Cloud. Choose carefully as it affects resource identification and billing.

**Related variables**:
- `is_restore`: Must be set to `true`
- `ibm_mongo_backup_id`: Backup to restore from
- `ibm_mongo_name`: Original service name (can be different)

**Note**: Using a different name allows side-by-side comparison of restored and current instances before switching over.


Role Variables - AWS DocumentDB
-------------------------------------------------------------------------------

#### aws_access_key_id
AWS account access key ID for authentication.

- **Required** when `mongodb_provider=aws`
- Environment Variable: `AWS_ACCESS_KEY_ID`
- Default Value: None

**Purpose**: Provides AWS authentication credentials for creating and managing DocumentDB resources. The access key must have sufficient IAM permissions for DocumentDB, VPC, and related services.

**When to use**:
- Always required when using AWS DocumentDB provider
- Must have IAM permissions for DocumentDB, EC2 (VPC/subnets/security groups)
- Should be stored securely (e.g., in Ansible Vault or external secret management)

**Valid values**: Valid AWS access key ID string

**Impact**: This key is used to authenticate all AWS API calls. Insufficient permissions will cause deployment failures.

**Related variables**:
- `aws_secret_access_key`: Must be provided together
- `aws_region`: Access key must have permissions in the target region

**Note**: **Never commit AWS credentials to source control**. Use secure secret management. Ensure the IAM user/role has appropriate permissions for DocumentDB and VPC operations.

#### aws_secret_access_key
AWS account secret access key for authentication.

- **Required** when `mongodb_provider=aws`
- Environment Variable: `AWS_SECRET_ACCESS_KEY`
- Default Value: None

**Purpose**: Provides the secret component of AWS authentication credentials. Works together with `aws_access_key_id` to authenticate AWS API requests.

**When to use**:
- Always required when using AWS DocumentDB provider
- Must correspond to the provided `aws_access_key_id`
- Should be stored securely

**Valid values**: Valid AWS secret access key string

**Impact**: Used with access key ID to authenticate AWS API calls. Invalid or mismatched credentials will cause authentication failures.

**Related variables**:
- `aws_access_key_id`: Must be provided together

**Note**: **Store securely and never commit to source control**. Rotate credentials regularly following AWS security best practices.

#### aws_region
AWS region where DocumentDB cluster will be deployed.

- **Required** when `mongodb_provider=aws`
- Environment Variable: `AWS_REGION`
- Default Value: `us-east-2`

**Purpose**: Specifies the geographic AWS region for DocumentDB deployment. Region selection affects latency, data residency, availability zones, and pricing.

**When to use**:
- Always required when using AWS DocumentDB provider
- Choose region closest to your OpenShift cluster for lowest latency
- Consider data residency requirements for compliance
- Use default (`us-east-2`) if no specific requirements

**Valid values**: Valid AWS region code (e.g., `us-east-1`, `us-east-2`, `us-west-2`, `eu-west-1`, `ap-southeast-1`)

**Impact**: Affects network latency, data residency compliance, available availability zones, and regional pricing. Cannot be changed after creation.

**Related variables**:
- `vpc_id`: VPC must exist in the specified region
- `aws_access_key_id`: Credentials must have permissions in this region

**Note**: Choose region carefully as it cannot be changed. Deploy DocumentDB in the same region as your OpenShift cluster for best performance.

#### vpc_id
AWS VPC ID where DocumentDB resources will be created.

- **Required** when `mongodb_provider=aws`
- Environment Variable: `VPC_ID`
- Default Value: None

**Purpose**: Specifies the AWS Virtual Private Cloud where DocumentDB cluster, subnets, and security groups will be created. The VPC provides network isolation and connectivity.

**When to use**:
- Always required when using AWS DocumentDB provider
- Use the same VPC as your OpenShift cluster for direct connectivity
- VPC must exist in the specified `aws_region`

**Valid values**: Valid AWS VPC ID (format: `vpc-xxxxxxxxxxxxxxxxx`)

**Impact**: Determines network connectivity and security boundaries. DocumentDB will only be accessible from resources within this VPC or connected networks.

**Related variables**:
- `aws_region`: VPC must exist in this region
- `docdb_cidr_az1`, `docdb_cidr_az2`, `docdb_cidr_az3`: Subnets created within this VPC
- `docdb_ingress_cidr`, `docdb_egress_cidr`: Should match VPC CIDR ranges

**Note**: Ensure the VPC has sufficient available IP addresses and appropriate routing for DocumentDB connectivity.

#### docdb_cluster_name
Name for the AWS DocumentDB cluster.

- **Required** when `mongodb_provider=aws`
- Environment Variable: `DOCDB_CLUSTER_NAME`
- Default Value: None

**Purpose**: Identifies the DocumentDB cluster in AWS. This name is used for resource identification, tagging, and as a prefix for related resources.

**When to use**:
- Always required when using AWS DocumentDB provider
- Choose a descriptive name that identifies the MAS instance and environment
- Name is used as prefix for subnet groups and security groups

**Valid values**: Valid AWS DocumentDB cluster identifier (lowercase, alphanumeric, hyphens, must start with letter)

**Impact**: This name appears in AWS console, CloudWatch metrics, and billing. Related resources (subnet group, security group) are named based on this value.

**Related variables**:
- `docdb_subnet_group_name`: Defaults to `docdb-{cluster_name}`
- `docdb_security_group_name`: Defaults to `docdb-{cluster_name}`
- `docdb_admin_credentials_secret_name`: Defaults to `{cluster_name}-admin-credentials`

**Note**: Choose a meaningful name as it cannot be easily changed. The name must be unique within your AWS account and region.

#### docdb_subnet_group_name
Name for the DocumentDB subnet group.

- **Optional**
- Default Value: `docdb-{{ docdb_cluster_name }}`

**Purpose**: Specifies the name for the DocumentDB subnet group that defines which subnets the cluster can use. The role creates this subnet group automatically.

**When to use**:
- Use default naming for standard deployments
- Customize only if organizational naming standards require it

**Valid values**: Valid AWS subnet group name

**Impact**: The subnet group associates the DocumentDB cluster with specific subnets across availability zones.

**Related variables**:
- `docdb_cluster_name`: Default name includes this value
- `docdb_cidr_az1`, `docdb_cidr_az2`, `docdb_cidr_az3`: Subnets included in this group

**Note**: This is automatically created by the role. Default naming is recommended for consistency.

#### docdb_security_group_name
Name for the DocumentDB security group.

- **Optional**
- Default Value: `docdb-{{ docdb_cluster_name }}`

**Purpose**: Specifies the name for the security group that controls network access to the DocumentDB cluster. The role creates this security group automatically.

**When to use**:
- Use default naming for standard deployments
- Customize only if organizational naming standards require it

**Valid values**: Valid AWS security group name

**Impact**: The security group defines firewall rules for DocumentDB access based on `docdb_ingress_cidr` and `docdb_egress_cidr`.

**Related variables**:
- `docdb_cluster_name`: Default name includes this value
- `docdb_ingress_cidr`: Allowed source CIDR for inbound traffic
- `docdb_egress_cidr`: Allowed destination CIDR for outbound traffic

**Note**: This is automatically created by the role. Default naming is recommended for consistency.

#### docdb_admin_credentials_secret_name
Name of the Kubernetes secret containing DocumentDB admin credentials.

- **Optional**
- Default Value: `{{ docdb_cluster_name }}-admin-credentials`

**Purpose**: Specifies the Kubernetes secret name where DocumentDB administrator credentials are stored. This secret is created automatically by the role.

**When to use**:
- Use default naming for standard deployments
- Customize only if organizational naming standards require it

**Valid values**: Valid Kubernetes secret name

**Impact**: The secret contains admin username and password for DocumentDB access. MAS and other applications reference this secret for database connectivity.

**Related variables**:
- `docdb_cluster_name`: Default name includes this value
- `docdb_master_username`: Username stored in this secret

**Note**: This secret is created in the MAS core namespace. Default naming is recommended for consistency.

#### docdb_engine_version
DocumentDB engine version to deploy.

- **Optional**
- Environment Variable: `DOCDB_ENGINE_VERSION`
- Default Value: `5.0.0`

**Purpose**: Specifies the DocumentDB engine version. MAS requires DocumentDB 5.0.0 for MongoDB compatibility.

**When to use**:
- Use default (`5.0.0`) for MAS deployments (required)
- Do not change unless specifically required by MAS version

**Valid values**: `5.0.0` (only version supported by MAS)

**Impact**: Determines MongoDB compatibility and available features. MAS is only certified with DocumentDB 5.0.0.

**Related variables**: None

**Note**: **MAS only supports DocumentDB 5.0.0**. Do not change this value unless MAS documentation explicitly supports other versions.

#### docdb_master_username
Master username for DocumentDB cluster administration.

- **Optional**
- Environment Variable: `DOCDB_MASTER_USERNAME`
- Default Value: `docdbadmin`

**Purpose**: Specifies the master administrator username for the DocumentDB cluster. This user has full administrative privileges.

**When to use**:
- Use default (`docdbadmin`) for standard deployments
- Customize if organizational security policies require specific usernames

**Valid values**: Valid DocumentDB username (alphanumeric, must start with letter, 1-63 characters)

**Impact**: This username is used for administrative access and is stored in the Kubernetes secret specified by `docdb_admin_credentials_secret_name`.

**Related variables**:
- `docdb_admin_credentials_secret_name`: Secret where credentials are stored

**Note**: Choose carefully as the master username cannot be changed after cluster creation.

#### docdb_instance_class
AWS instance class for DocumentDB instances.

- **Optional**
- Environment Variable: `DOCDB_INSTANCE_CLASS`
- Default Value: `db.t3.medium`

**Purpose**: Specifies the compute and memory capacity for each DocumentDB instance. Instance class affects performance, availability, and cost.

**When to use**:
- Use `db.t3.medium` (default) for development or small deployments
- Use `db.r5.large` or larger for production workloads
- Consider `db.r6g` instances for better price/performance (ARM-based)

**Valid values**: Valid DocumentDB instance class (e.g., `db.t3.medium`, `db.r5.large`, `db.r5.xlarge`, `db.r6g.large`)

**Impact**: Affects CPU, memory, network performance, and cost. Larger instances provide better performance but cost more.

**Related variables**:
- `docdb_instance_number`: Total cost = instance class cost × number of instances

**Note**: Production deployments typically need `db.r5.large` or larger. Review AWS DocumentDB pricing and instance specifications.

#### docdb_instance_number
Number of DocumentDB instances in the cluster.

- **Optional**
- Environment Variable: `DOCDB_INSTANCE_NUMBER`
- Default Value: `3`

**Purpose**: Determines the number of instances in the DocumentDB cluster. More instances provide higher availability and read scalability.

**When to use**:
- Use default (`3`) for production deployments with high availability
- Use `1` only for development or testing (no high availability)
- Use `5` or more for critical workloads requiring higher availability

**Valid values**: Integer from 1 to 16

**Impact**:
- More instances = higher availability and read capacity but higher cost
- Instances are distributed across availability zones for fault tolerance
- Total cost = instance class cost × number of instances

**Related variables**:
- `docdb_instance_class`: Determines per-instance cost and performance
- `docdb_cidr_az1`, `docdb_cidr_az2`, `docdb_cidr_az3`: Instances distributed across these AZs

**Note**: Production deployments should use 3 or more instances for high availability. Single instance has no failover capability.

#### docdb_instance_identifier_prefix
Prefix for DocumentDB instance identifiers.

- **Required** when `mongodb_provider=aws`
- Environment Variable: `DOCDB_INSTANCE_IDENTIFIER_PREFIX`
- Default Value: None

**Purpose**: Specifies the prefix used to name individual DocumentDB instances. Instance names are formed as `{prefix}-{number}`.

**When to use**:
- Always required when using AWS DocumentDB provider
- Use a descriptive prefix that identifies the cluster and environment
- Typically matches or relates to `docdb_cluster_name`

**Valid values**: Valid AWS instance identifier prefix (lowercase, alphanumeric, hyphens)

**Impact**: Instance names appear in AWS console and CloudWatch metrics. Choose a meaningful prefix for easy identification.

**Related variables**:
- `docdb_cluster_name`: Typically related to cluster name

**Note**: Instance identifiers are formed as `{prefix}-1`, `{prefix}-2`, etc. Choose a clear, descriptive prefix.

#### docdb_ingress_cidr
CIDR block allowed to connect to DocumentDB cluster.

- **Required** when `mongodb_provider=aws`
- Environment Variable: `DOCDB_INGRESS_CIDR`
- Default Value: None

**Purpose**: Specifies the IPv4 CIDR range from which incoming connections to DocumentDB are allowed. This is used in security group ingress rules.

**When to use**:
- Always required when using AWS DocumentDB provider
- Typically set to the CIDR of your OpenShift cluster's VPC
- Can be set to specific subnet CIDRs for tighter security

**Valid values**: Valid IPv4 CIDR notation (e.g., `10.0.0.0/16`, `172.31.0.0/16`)

**Impact**: Only traffic from this CIDR range can connect to DocumentDB. Too restrictive blocks legitimate traffic; too permissive reduces security.

**Related variables**:
- `vpc_id`: Should match VPC CIDR or subnet CIDRs within the VPC
- `docdb_egress_cidr`: Typically set to same value

**Note**: Set to your OpenShift cluster's VPC CIDR for proper connectivity. Verify CIDR ranges before deployment.

#### docdb_egress_cidr
CIDR block for outbound connections from DocumentDB cluster.

- **Required** when `mongodb_provider=aws`
- Environment Variable: `DOCDB_EGRESS_CIDR`
- Default Value: None

**Purpose**: Specifies the IPv4 CIDR range to which DocumentDB can send outbound connections. This is used in security group egress rules.

**When to use**:
- Always required when using AWS DocumentDB provider
- Typically set to the same value as `docdb_ingress_cidr`
- Set to VPC CIDR for standard deployments

**Valid values**: Valid IPv4 CIDR notation (e.g., `10.0.0.0/16`, `172.31.0.0/16`)

**Impact**: DocumentDB can only send traffic to this CIDR range. Affects ability to respond to client connections.

**Related variables**:
- `docdb_ingress_cidr`: Typically set to same value
- `vpc_id`: Should match VPC CIDR

**Note**: Usually set to the same value as `docdb_ingress_cidr`. Verify CIDR ranges match your network configuration.

#### docdb_cidr_az1
CIDR block for DocumentDB subnet in availability zone 1.

- **Required** when `mongodb_provider=aws`
- Environment Variable: `DOCDB_CIDR_AZ1`
- Default Value: None

**Purpose**: Specifies the IPv4 CIDR for the subnet in the first availability zone. If the subnet exists with tag `Name: {{ docdb_cluster_name }}`, it's used; otherwise, a new subnet is created.

**When to use**:
- Always required when using AWS DocumentDB provider
- Must be within the VPC CIDR range
- Must not overlap with other subnets in the VPC

**Valid values**: Valid IPv4 CIDR notation within VPC range (e.g., `10.0.1.0/24`)

**Impact**: Defines the IP address range for DocumentDB instances in AZ1. Subnet size affects number of available IP addresses.

**Related variables**:
- `vpc_id`: CIDR must be within this VPC's range
- `docdb_cidr_az2`, `docdb_cidr_az3`: Must not overlap with these subnets

**Note**: Plan subnet sizes carefully. Each DocumentDB instance needs an IP address. Use /24 or larger subnets for flexibility.

#### docdb_cidr_az2
CIDR block for DocumentDB subnet in availability zone 2.

- **Required** when `mongodb_provider=aws`
- Environment Variable: `DOCDB_CIDR_AZ2`
- Default Value: None

**Purpose**: Specifies the IPv4 CIDR for the subnet in the second availability zone. If the subnet exists with tag `Name: {{ docdb_cluster_name }}`, it's used; otherwise, a new subnet is created.

**When to use**:
- Always required when using AWS DocumentDB provider
- Must be within the VPC CIDR range
- Must not overlap with other subnets in the VPC

**Valid values**: Valid IPv4 CIDR notation within VPC range (e.g., `10.0.2.0/24`)

**Impact**: Defines the IP address range for DocumentDB instances in AZ2. Required for multi-AZ high availability.

**Related variables**:
- `vpc_id`: CIDR must be within this VPC's range
- `docdb_cidr_az1`, `docdb_cidr_az3`: Must not overlap with these subnets

**Note**: Use different availability zones for AZ1, AZ2, and AZ3 to ensure high availability across zones.

#### docdb_cidr_az3
CIDR block for DocumentDB subnet in availability zone 3.

- **Required** when `mongodb_provider=aws`
- Environment Variable: `DOCDB_CIDR_AZ3`
- Default Value: None

**Purpose**: Specifies the IPv4 CIDR for the subnet in the third availability zone. If the subnet exists with tag `Name: {{ docdb_cluster_name }}`, it's used; otherwise, a new subnet is created.

**When to use**:
- Always required when using AWS DocumentDB provider
- Must be within the VPC CIDR range
- Must not overlap with other subnets in the VPC

**Valid values**: Valid IPv4 CIDR notation within VPC range (e.g., `10.0.3.0/24`)

**Impact**: Defines the IP address range for DocumentDB instances in AZ3. Provides third availability zone for maximum fault tolerance.

**Related variables**:
- `vpc_id`: CIDR must be within this VPC's range
- `docdb_cidr_az1`, `docdb_cidr_az2`: Must not overlap with these subnets

**Note**: Three availability zones provide best fault tolerance. Ensure subnets are in different AZs for proper distribution.

### AWS DocumentDB Secret Rotation Variables

The following variables are used for rotating DocumentDB credentials. These are typically used with `mongodb_action=rotate-secret`.

#### docdb_mongo_instance_name
DocumentDB instance name for secret rotation.

- **Required** when rotating secrets
- Environment Variable: `DOCDB_MONGO_INSTANCE_NAME`
- Default Value: None

**Purpose**: Identifies the specific DocumentDB instance for credential rotation operations.

**When to use**:
- Required when performing secret rotation (`mongodb_action=rotate-secret`)
- Must match an existing DocumentDB instance name

**Valid values**: Valid DocumentDB instance identifier

**Impact**: Specifies which DocumentDB instance's credentials will be rotated.

**Related variables**:
- `docdb_cluster_name`: Instance belongs to this cluster
- `docdb_host`: Host address of this instance

**Note**: Verify instance name before rotation to avoid affecting wrong instance.

#### docdb_host
DocumentDB instance host address for connection.

- **Required** when rotating secrets
- Environment Variable: `DOCDB_HOST`
- Default Value: None

**Purpose**: Specifies the host address of a DocumentDB instance for establishing connection during secret rotation.

**When to use**:
- Required when performing secret rotation
- Use any one host address from the DocumentDB cluster
- Obtain from AWS console or DocumentDB cluster endpoint

**Valid values**: Valid DocumentDB instance hostname or endpoint

**Impact**: Used to connect to DocumentDB for credential rotation operations.

**Related variables**:
- `docdb_port`: Port for this host
- `docdb_mongo_instance_name`: Instance identifier

**Note**: Any instance host from the cluster can be used for rotation operations.

#### docdb_port
DocumentDB instance port number.

- **Required** when rotating secrets
- Environment Variable: `DOCDB_PORT`
- Default Value: None (typically `27017`)

**Purpose**: Specifies the port number for connecting to the DocumentDB instance during secret rotation.

**When to use**:
- Required when performing secret rotation
- Typically `27017` (default DocumentDB port)

**Valid values**: Valid port number (typically `27017`)

**Impact**: Used with `docdb_host` to establish connection for credential rotation.

**Related variables**:
- `docdb_host`: Host address for this port

**Note**: DocumentDB uses port 27017 by default unless customized during cluster creation.

#### docdb_instance_username
Username for which password is being rotated.

- **Required** when rotating secrets
- Environment Variable: `DOCDB_INSTANCE_USERNAME`
- Default Value: None

**Purpose**: Specifies the DocumentDB username whose password will be changed during rotation.

**When to use**:
- Required when performing secret rotation
- Typically the application user or admin user
- Must be an existing DocumentDB user

**Valid values**: Valid DocumentDB username

**Impact**: This user's password will be changed. Applications using this username must be updated with the new password.

**Related variables**:
- `docdb_instance_password_old`: Current password for this user
- `docdb_master_username`: Master user for performing rotation

**Note**: Ensure applications can handle password rotation. Consider using connection pooling with reconnection logic.

#### docdb_instance_password_old
Current password for the user being rotated.

- **Required** when rotating secrets
- Environment Variable: `DOCDB_PASSWORD_OLD`
- Default Value: None

**Purpose**: Provides the current password for authentication before rotation. Used to verify current credentials.

**When to use**:
- Required when performing secret rotation
- Must be the current valid password

**Valid values**: Current password string

**Impact**: Used to authenticate before changing password. Incorrect password will cause rotation to fail.

**Related variables**:
- `docdb_instance_username`: User for this password

**Note**: Store securely. After rotation, this password will no longer be valid.

#### docdb_master_password
DocumentDB master user password for administrative operations.

- **Required** when rotating secrets
- Environment Variable: `DOCDB_MASTER_PASSWORD`
- Default Value: None

**Purpose**: Provides master user credentials for performing password rotation operations. Master user has privileges to change other users' passwords.

**When to use**:
- Required when performing secret rotation
- Must be the current master password

**Valid values**: Valid master password string

**Impact**: Used to authenticate as master user to perform credential rotation.

**Related variables**:
- `docdb_master_username`: Master username for this password

**Note**: **Store master credentials securely**. Never commit to source control.

#### docdb_master_username
DocumentDB master username for administrative operations.

- **Required** when rotating secrets
- Environment Variable: `DOCDB_MASTER_USERNAME`
- Default Value: None

**Purpose**: Specifies the master username for performing password rotation operations. Master user has administrative privileges.

**When to use**:
- Required when performing secret rotation
- Typically `docdbadmin` or the value set during cluster creation

**Valid values**: Valid DocumentDB master username

**Impact**: Used with `docdb_master_password` to authenticate for credential rotation.

**Related variables**:
- `docdb_master_password`: Password for this master user

**Note**: This should match the master username set during DocumentDB cluster creation.

AWS DocumentDB destroy-data action Variables
----------------------------------
### mas_instance_id
The specified MAS instance ID

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### mongo_username
Mongo Username

- Environment Variable: `MONGO_USERNAME`
- Default Value: None

### mongo_password
Mongo password

- Environment Variable: `MONGO_PASSWORD`
- Default Value: None

### config
Mongo Config, please refer to the below example playbook section for details

- **Required**
- Environment Variable: `CONFIG`
- Default Value: None

### certificates
Mongo Certificates, please refer to the below example playbook section for details

- **Required**
- Environment Variable: `CERTIFICATES`
- Default Value: None



## Example Playbook

### Install (CE Operator)
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mongodb_storage_class: ibmc-block-gold
    mas_instance_id: masinst1
    mas_config_dir: ~/masconfig
  roles:
    - ibm.mas_devops.mongodb
```

### Backup (CE Operator)
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mongodb_action: backup
    mas_instance_id: masinst1
    masbr_storage_local_folder: /tmp/masbr
  roles:
    - ibm.mas_devops.mongodb
```

### Restore (CE Operator)
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mongodb_action: restore
    mas_instance_id: masinst1
    masbr_restore_from_version: 20240621021316
    masbr_storage_local_folder: /tmp/masbr
  roles:
    - ibm.mas_devops.mongodb
```

### Install (IBM Cloud)
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_config_dir: ~/masconfig
    mongodb_provider: ibm
    ibmcloud_apikey: apikey****
    ibmcloud_resource_group: mas-test
  roles:
    - ibm.mas_devops.mongodb
```

### Install (AWS DocumentDB)
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_config_dir: ~/masconfig
    mongodb_provider: aws
    mongodb_action: provision
    docdb_size: ~/docdb-config.yml
    docdb_cluster_name: test-db
    docdb_ingress_cidr: 10.0.0.0/16
    docdb_egress_cidr: 10.0.0.0/16
    docdb_cidr_az1: 10.0.0.0/26
    docdb_cidr_az2: 10.0.0.64/26
    docdb_cidr_az3: 10.0.0.128/26
    docdb_instance_identifier_prefix: test-db-instance
    vpc_id: test-vpc-id
    aws_access_key_id: aws-key
    aws_secret_access_key: aws-access-key

  roles:
    - ibm.mas_devops.mongodb
```

### AWS DocumentDb Secret Rotation
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_config_dir: ~/masconfig
    mongodb_provider: aws
    mongodb_action: docdb_secret_rotate
    docdb_mongo_instance_name: test-db-instance
    db_host: aws.test1.host7283-*****
    db_port: 27017
    docdb_master_username: admin
    docdb_master_password: pass***
    docdb_instance_password_old: oldpass****
    docdb_instance_username: testuser
    aws_access_key_id: aws-key
    aws_secret_access_key: aws-access-key

  roles:
    - ibm.mas_devops.mongodb
```

### AWS DocumentDb destroy-data action

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mongodb_provider: aws
    mongodb_action: destroy-data
    mongo_username: pqradmin
    mongo_password: xyzabc
    config:
      configDb: admin
      authMechanism: DEFAULT
      retryWrites: false
      hosts:
        - host: abc-0.pqr.databases.appdomain.cloud
          port: 32250
        - host: abc-1.pqr.databases.appdomain.cloud
          port: 32250
        - host: abc-2.pqr.databases.appdomain.cloud
          port: 32250
    certificates:
      - alias: ca
        crt: |
          -----BEGIN CERTIFICATE-----
          MIIDDzCCAfegAwIBAgIJANEH58y2/kzHMA0GCSqGSIb3DQEBCwUAMB4xHDAaBgNV
          BAMME0lCTSBDbG91ZCBEYXRhYmFzZXMwHhcNMTgwNjI1MTQyOTAwWhcNMjgwNjIy
          MTQyOTAwWjAeMRwwGgYDVQQDDBNJQk0gQ2xvdWQgRGF0YWJhc2VzMIIBIjANBgkq
          1eKI2FLzYKpoKBe5rcnrM7nHgNc/nCdEs5JecHb1dHv1QfPm6pzIxwIDAQABo1Aw
          TjAdBgNVHQ4EFgQUK3+XZo1wyKs+DEoYXbHruwSpXjgwHwYDVR0jBBgwFoAUK3+X
          Zo1wyKs+DEoYXbHruwSpXjgwDAYDVR0TBAUwAwEB/zANBgkqhkiG9w0BAQsFAAOC
          doqqgGIZ2nxCkp5/FXxF/TMb55vteTQwfgBy60jVVkbF7eVOWCv0KaNHPF5hrqbN
          i+3XjJ7/peF3xMvTMoy35DcT3E2ZeSVjouZs15O90kI3k2daS2OHJABW0vSj4nLz
          +PQzp/B9cQmOO8dCe049Q3oaUA==
          -----END CERTIFICATE-----
  roles:
    - ibm.mas_devops.mongodb

```

## Run Role Playbook

```bash
export MONGODB_STORAGE_CLASS=ibmc-block-gold
export MAS_INSTANCE_ID=masinst1
export MAS_CONFIG_DIR=~/masconfig
ansible-playbook ibm.mas_devops.run_role
```

## Troubleshooting

!!! important
    Please be cautious while performing any of the troubleshooting steps outlined below. It is important to understand that the MongoDB Community operator persists data within Persistent Volume Claims. These claims should not be removed inadvertent deletion of the `mongoce` namespace could result in data loss.

### MongoDB Replica Set Pods Will Not Start

MongoDB 5 has introduced new platform specific requirements. Please consult the [Platform Support Notes](https://www.mongodb.com/docs/manual/administration/production-notes/#x86_64) for detailed information.

It is of particular importance to confirm that the AVX instruction set is exposed or available to the MongoDB workloads. This can easily be determined by entering any running pod on the same OpenShift cluster where MongoDB replica set members are failing to start. Once inside of a running pod the following command can be executed to confirm if the AVX instruction set is available:

```bash
cat /proc/cpuinfo | grep flags | grep avx
```

If `avx` is not found in the available `flags` then either the physical processor hosting the OpenShift cluster does not provide the AVX instruction set or the virtual host configuration is not exposing the AVX instruction set. If the latter is suspected the virtual hosting documentation should be referenced for details on how to expose the AVX instruction set.

### LDAP Authentication

If authenticating via LDAP with PLAIN specified for `authMechanism` then `configDb` must be set to `$external` in the MongoCfg. The field `configDb` in the MongoCfg refers to the authentication database.

### CA Certificate Renewal

!!! warning
    If the MongoDB CA Certificate expires the MongoDB replica set will become unusable. Replica set members will not be able to communicate with each other and client applications (i.e. Maximo Application Suite components) will not be to connect.


In order to renew the CA Certificate used by the MongoDB replica set the following steps must be taken:

- Delete the CA Certificate resource
- Delete the MongoDB server Certificate resource
- Delete the Secrets resources associated with both the CA Certificate and Server Certificate
- Delete the Secret resource which contains the MongoDB configuration parameters
- Delete the ConfigMap resources which contains the CA certificate
- Delete the Secret resource which contains the sever certificate and private key

The following steps illustrate the process required to renew the CA Certificate, sever certificate and reconfigure the MongoDB replica set with the new CA and server certificates.

The first step is to stop the Mongo replica set and MongoDb CE Operator pod.

```bash
oc project mongoce
oc delete deployment mongodb-kubernetes-operator
```

!!! important
    Make sure the MongoDB Community operator pod has terminated before proceeding.


```bash
oc delete statefulset mas-mongo-ce

```

!!! important
    Make sure all pods in the `mongoce` namespace have terminated before proceeding


Remove expired CA Certificate and Server Certificate resources. Clean up MongoDB Community configuration and then run the `mongodb` role.

```bash
oc delete certificate mongo-ca-crt
oc delete certificate mongo-server
oc delete secret mongo-ca-secret
oc delete secret mongo-server-cert

oc delete secret mas-mongo-ce-config
oc delete configmap  mas-mongo-ce-cert-map
oc delete secret mas-mongo-ce-server-certificate-key

export ROLE_NAME=mongodb
ansible-playbook ibm.mas_devops.run_role
```

Once the `mongodb` role has completed the MongoDb CE Operator pod and Mongo replica set should be configured.

After the CA and server Certificates have been renewed you must ensure that that MongoCfg Suite CR is updated with the new CA Certificate. First obtain the CA Certificate from the Secret resource `mongo-ca-secret`. Then edit the Suite MongoCfg CR in the Maximo Application Suite core namespace. This is done by updating the appropriate certificate under `.spec.certificates` in the MongoCfg CR:

```yaml
  spec:
    certificates:
    - alias: ca
      crt: |
        -----BEGIN CERTIFICATE-----

        -----END CERTIFICATE-----

```

If an IBM Suite Licensing Service (SLS) is also connecting to the MongoDB replica set the LicenseService CR must also be updated to reflect the new MongoDB CA. This can be added to the `.spec.mongo.certificates` section of the LicenseService CR.

```yaml
    mongo:
      certificates:
      - alias: mongoca
        crt: |
          -----BEGIN CERTIFICATE-----

          -----END CERTIFICATE-----
```

Once the CA certificate has been updated for the MongoCfg and LicenseService CRs several pods in the core and SLS namespaces might need to be restarted to pick up the changes. This would include but is not limited to coreidp, coreapi, api-licensing.


## License

EPL-2.0
