# mongodb

This role currently supports provisioning of mongodb in four different providers:
 - community
 - aws (documentdb)
 - ibm
 - atlas (MongoDB Atlas)
**Important Notice**
Support for the **atlas (MongoDB Atlas)** provider is currently in **Proof of Concept (PoC)** stage. It is intended for **testing and development purposes only** and **is not recommended for production deployments** at this time.

If the selected provider is `community` then the [MongoDB Community Kubernetes Operator](https://github.com/mongodb/mongodb-kubernetes-operator) will be configured and deployed into the specified namespace. By default a three member MongoDB replica set will be created.  The cluster will bind six PVCs, these provide persistence for the data and system logs across the three nodes.  Currently there is no support built-in for customizing the cluster beyond this configuration.

!!! tip
    The role will generate a yaml file containing the definition of a Secret and MongoCfg resource that can be used to configure the deployed instance as the MAS system MongoDB.

    This file can be directly applied using `oc apply -f $MAS_CONFIG_DIR/mongocfg-mongoce-system.yaml` or used in conjunction with the [suite_config](suite_config.md) role.

## Prerequisites

### General Prerequisites
To run this role with providers as `ibm` or `aws` you must have already installed the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).
Also, you need to have AWS user credentials configured via `aws configure` command or simply export `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables with your corresponding AWS username credentials prior running this role when provider is either `ibm` or `aws` or `atlas`.

To run the `docdb_secret_rotate` MONGODB_ACTION when the provider is `aws` you must have already installed the [Mongo Shell](https://www.mongodb.com/docs/mongodb-shell/install/).

This role will install a GrafanaDashboard used for monitoring the MongoDB instance when the provider is `community` and you have run the [grafana role](https://ibm-mas.github.io/ansible-devops/roles/grafana/) previously. If you did not run the [grafana role](https://ibm-mas.github.io/ansible-devops/roles/grafana/) then the GrafanaDashboard won't be installed.

### MongoDB Atlas Prerequisites
When using `mongodb_provider=atlas`, you must complete the following prerequisites:

### 1. Create AWS Secrets Manager Secret (Required)
Create a secret in AWS Secrets Manager to store your Atlas API credentials. The secret must follow this naming convention:

**Secret Name**: `<atlas_account_id>/mongodb-atlas`

Where `<atlas_account_id>` is your AWS account ID (e.g., `123456789012/mongodb-atlas`).

**Secret Format**: The secret must contain a JSON object with these exact field names:
```json
{
  "mongodb_atlas_api_pub_key": "your-atlas-public-key",
  "mongodb_atlas_api_pri_key": "your-atlas-private-key"
}
```

**How to create the secret**:
```bash
# Replace 123456789012 with your AWS account ID
export ACCOUNT_ID="123456789012"
export SECRET_NAME="${ACCOUNT_ID}/mongodb-atlas"

# Create the secret with Atlas API credentials
aws secretsmanager create-secret \
  --name "${SECRET_NAME}" \
  --description "MongoDB Atlas API credentials for account ${ACCOUNT_ID}" \
  --secret-string '{"mongodb_atlas_api_pub_key":"YOUR_PUBLIC_KEY","mongodb_atlas_api_pri_key":"YOUR_PRIVATE_KEY"}' \
  --region us-east-1

# Or update an existing secret
aws secretsmanager put-secret-value \
  --secret-id "${SECRET_NAME}" \
  --secret-string '{"mongodb_atlas_api_pub_key":"YOUR_PUBLIC_KEY","mongodb_atlas_api_pri_key":"YOUR_PRIVATE_KEY"}' \
  --region us-east-1
```

**Note**: The field names must be exactly `mongodb_atlas_api_pub_key` and `mongodb_atlas_api_pri_key` as shown above.

### 2. Add IP Address to Atlas API Access List
Add your IP address to the Atlas API Access List before running this role:

1. Log in to [MongoDB Atlas Console](https://cloud.mongodb.com)
2. Navigate to your Organization → Access Manager → API Keys
3. Select your API key
4. Click "Edit" and add your current IP address to the Access List

**Note**: The role cannot automatically add IP addresses to the Atlas API Access List. If your IP is not whitelisted, API calls will fail with `403 IP_ADDRESS_NOT_ON_ACCESS_LIST` error.

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`mas_instance_id`](#mas_instance_id) | No | None |
| [`mas_config_dir`](#mas_config_dir) | No | None |
| [`mongodb_provider`](#mongodb_provider) | No | `community` |
| [`mongodb_action`](#mongodb_action) | No | `install` |
| [`mongodb_namespace`](#mongodb_namespace) | No | `mongoce` |
| [`mongodb_version`](#mongodb_version) | No | From MAS case bundle |
| [`mongodb_override_spec`](#mongodb_override_spec) | No | `false` |
| [`mongodb_storage_class`](#mongodb_storage_class) | Conditional | None |
| [`mongodb_storage_capacity_data`](#mongodb_storage_capacity_data) | No | `20Gi` |
| [`mongodb_storage_capacity_logs`](#mongodb_storage_capacity_logs) | No | `20Gi` |
| [`mongodb_cpu_limits`](#mongodb_cpu_limits) | No | `1` |
| [`mongodb_mem_limits`](#mongodb_mem_limits) | No | `1Gi` |
| [`mongodb_cpu_requests`](#mongodb_cpu_requests) | No | `500m` |
| [`mongodb_mem_requests`](#mongodb_mem_requests) | No | `1Gi` |
| [`mongodb_replicas`](#mongodb_replicas) | No | `3` |
| [`custom_labels`](#custom_labels) | No | None |
| [`mongodb_v5_upgrade`](#mongodb_v5_upgrade) | No | `false` |
| [`mongodb_v6_upgrade`](#mongodb_v6_upgrade) | No | `false` |
| [`mongodb_v7_upgrade`](#mongodb_v7_upgrade) | No | `false` |
| [`mongodb_v8_upgrade`](#mongodb_v8_upgrade) | No | `false` |
| [`mas_backup_dir`](#mas_backup_dir) | Conditional | None |
| [`mongodb_backup_version`](#mongodb_backup_version) | Conditional | None |
| [`mongodb_instance_name`](#mongodb_instance_name) | No | `mas-mongo-ce` |
| [`override_storageclass`](#override_storageclass) | No | `false` |
| [`mas_app_id`](#mas_app_id) | No | None |
| [`ibm_mongo_name`](#ibm_mongo_name) | No | `mongo-<mas_instance_id>` |
| [`ibm_mongo_admin_password`](#ibm_mongo_admin_password) | No | Auto-generated |
| [`ibm_mongo_admin_credentials_secret_name`](#ibm_mongo_admin_credentials_secret_name) | No | `<ibm_mongo_name>-admin-credentials` |
| [`ibm_mongo_service_credentials_secret_name`](#ibm_mongo_service_credentials_secret_name) | No | `<ibm_mongo_name>-service-credentials` |
| [`ibm_mongo_resourcegroup`](#ibm_mongo_resourcegroup) | No | `ibmcloud_resourcegroup` (`Default`) |
| [`ibm_mongo_region`](#ibm_mongo_region) | No | `ibmcloud_region` (`us-east`) |
| [`ibmcloud_apikey`](#ibmcloud_apikey) | Conditional | None |
| [`ibm_mongo_plan`](#ibm_mongo_plan) | No | `standard` |
| [`ibm_mongo_service`](#ibm_mongo_service) | No | `databases-for-mongodb` |
| [`ibm_mongo_service_endpoints`](#ibm_mongo_service_endpoints) | No | `public` |
| [`ibm_mongo_version`](#ibm_mongo_version) | No | `4.4` |
| [`ibm_mongo_memory`](#ibm_mongo_memory) | No | `3840` |
| [`ibm_mongo_disk`](#ibm_mongo_disk) | No | `30720` |
| [`ibm_mongo_cpu`](#ibm_mongo_cpu) | No | `0` |
| [`ibm_mongo_backup_id`](#ibm_mongo_backup_id) | Conditional | None |
| [`is_restore`](#is_restore) | No | `false` |
| [`restored_mongodb_service_name`](#restored_mongodb_service_name) | Conditional | None |
| [`aws_access_key_id`](#aws_access_key_id) | Conditional | None |
| [`aws_secret_access_key`](#aws_secret_access_key) | Conditional | None |
| [`aws_region`](#aws_region) | No | `us-east-2` |
| [`vpc_id`](#vpc_id) | Conditional | None |
| [`docdb_cluster_name`](#docdb_cluster_name) | Conditional | None |
| [`docdb_subnet_group_name`](#docdb_subnet_group_name) | No | `docdb-<docdb_cluster_name>` |
| [`docdb_security_group_name`](#docdb_security_group_name) | No | `docdb-<docdb_cluster_name>` |
| [`docdb_admin_credentials_secret_name`](#docdb_admin_credentials_secret_name) | No | `<docdb_cluster_name>-admin-credentials` |
| [`docdb_engine_version`](#docdb_engine_version) | No | `5.0.0` |
| [`docdb_master_username`](#docdb_master_username) | No | `docdbadmin` |
| [`docdb_instance_class`](#docdb_instance_class) | No | `db.t3.medium` |
| [`docdb_instance_number`](#docdb_instance_number) | No | `3` |
| [`docdb_instance_identifier_prefix`](#docdb_instance_identifier_prefix) | Conditional | None |
| [`docdb_ingress_cidr`](#docdb_ingress_cidr) | Conditional | None |
| [`docdb_egress_cidr`](#docdb_egress_cidr) | Conditional | None |
| [`docdb_cidr_az1`](#docdb_cidr_az1) | Conditional | None |
| [`docdb_cidr_az2`](#docdb_cidr_az2) | Conditional | None |
| [`docdb_cidr_az3`](#docdb_cidr_az3) | Conditional | None |
| [`docdb_mongo_instance_name`](#docdb_mongo_instance_name) | Conditional | None |
| [`docdb_host`](#docdb_host) | Conditional | None |
| [`docdb_port`](#docdb_port) | Conditional | None |
| [`docdb_instance_username`](#docdb_instance_username) | Conditional | None |
| [`docdb_instance_password_old`](#docdb_instance_password_old) | Conditional | None |
| [`docdb_master_password`](#docdb_master_password) | Conditional | None |
| [`mongo_username`](#mongo_username) | Conditional | None |
| [`mongo_password`](#mongo_password) | Conditional | None |
| [`config`](#config) | Conditional | None |
| [`certificates`](#certificates) | Conditional | None |
| [`atlas_org_id`](#atlas_org_id) | Conditional | None |
| [`atlas_project_name`](#atlas_project_name) | Conditional | None |
| [`atlas_project_id`](#atlas_project_id) | Conditional | None |
| [`atlas_account_id`](#atlas_account_id) | Conditional | None |
| [`atlas_cluster_name`](#atlas_cluster_name) | Conditional | None |
| [`atlas_cluster_provider`](#atlas_cluster_provider) | No | `AWS` |
| [`atlas_cluster_size`](#atlas_cluster_size) | Conditional | None |
| [`atlas_mongodb_version`](#atlas_mongodb_version) | No | `7.0` |
| [`atlas_backup_enabled`](#atlas_backup_enabled) | No | `false` |
| [`atlas_audit_enabled`](#atlas_audit_enabled) | No | `false` |
| [`atlas_audit_filter`](#atlas_audit_filter) | No | Auto-generated filter |
| [`atlas_audit_authorization_success`](#atlas_audit_authorization_success) | No | `true` |
| [`atlas_s3_audit_export_enabled`](#atlas_s3_audit_export_enabled) | No | `false` |
| [`atlas_s3_audit_bucket_prefix`](#atlas_s3_audit_bucket_prefix) | No | `mongodb-atlas-audit-logs` |
| [`atlas_s3_audit_log_retention_days`](#atlas_s3_audit_log_retention_days) | No | `365` |
| [`atlas_s3_audit_bucket_enable_versioning`](#atlas_s3_audit_bucket_enable_versioning) | No | `false` |
| [`atlas_s3_audit_glacier_transition_days`](#atlas_s3_audit_glacier_transition_days) | No | `90` |
| [`atlas_s3_audit_noncurrent_version_retention_days`](#atlas_s3_audit_noncurrent_version_retention_days) | No | `30` |
| [`atlas_enable_alerts`](#atlas_enable_alerts) | No | `false` |
| [`atlas_alert_notification_emails`](#atlas_alert_notification_emails) | Conditional | `[]` |
| [`atlas_enable_cluster_health_alerts`](#atlas_enable_cluster_health_alerts) | No | `false` |
| [`atlas_enable_performance_alerts`](#atlas_enable_performance_alerts) | No | `false` |
| [`atlas_enable_security_alerts`](#atlas_enable_security_alerts) | No | `false` |
| [`atlas_alert_cpu_thresholds`](#atlas_alert_cpu_thresholds) | No | `[70, 80]` |
| [`atlas_alert_memory_thresholds`](#atlas_alert_memory_thresholds) | No | `[70, 80]` |
| [`atlas_alert_connection_thresholds`](#atlas_alert_connection_thresholds) | No | `[70, 80]` |
| [`atlas_alert_interval_min`](#atlas_alert_interval_min) | No | `60` |
| [`atlas_backup_compliance_enabled`](#atlas_backup_compliance_enabled) | No | `false` |
| [`atlas_compliance_authorized_email`](#atlas_compliance_authorized_email) | No | `admin@example.com` |
| [`atlas_compliance_authorized_first_name`](#atlas_compliance_authorized_first_name) | No | `Admin` |
| [`atlas_compliance_authorized_last_name`](#atlas_compliance_authorized_last_name) | No | `User` |
| [`atlas_compliance_copy_protection`](#atlas_compliance_copy_protection) | No | `false` |
| [`atlas_compliance_encryption_at_rest`](#atlas_compliance_encryption_at_rest) | No | `false` |
| [`atlas_compliance_pit_enabled`](#atlas_compliance_pit_enabled) | No | `false` |
| [`atlas_compliance_restore_window_days`](#atlas_compliance_restore_window_days) | No | `7` |
| [`atlas_compliance_hourly_frequency_interval`](#atlas_compliance_hourly_frequency_interval) | No | `6` |
| [`atlas_compliance_hourly_retention_unit`](#atlas_compliance_hourly_retention_unit) | No | `days` |
| [`atlas_compliance_hourly_retention_value`](#atlas_compliance_hourly_retention_value) | No | `7` |
| [`atlas_compliance_daily_frequency_interval`](#atlas_compliance_daily_frequency_interval) | No | `1` |
| [`atlas_compliance_daily_retention_unit`](#atlas_compliance_daily_retention_unit) | No | `days` |
| [`atlas_compliance_daily_retention_value`](#atlas_compliance_daily_retention_value) | No | `7` |
| [`atlas_compliance_weekly_frequency_interval`](#atlas_compliance_weekly_frequency_interval) | No | `1` |
| [`atlas_compliance_weekly_retention_unit`](#atlas_compliance_weekly_retention_unit) | No | `weeks` |
| [`atlas_compliance_weekly_retention_value`](#atlas_compliance_weekly_retention_value) | No | `4` |
| [`atlas_compliance_monthly_frequency_interval`](#atlas_compliance_monthly_frequency_interval) | No | `1` |
| [`atlas_compliance_monthly_retention_unit`](#atlas_compliance_monthly_retention_unit) | No | `months` |
| [`atlas_compliance_monthly_retention_value`](#atlas_compliance_monthly_retention_value) | No | `12` |
| [`atlas_compliance_yearly_frequency_interval`](#atlas_compliance_yearly_frequency_interval) | No | `1` |
| [`atlas_compliance_yearly_retention_unit`](#atlas_compliance_yearly_retention_unit) | No | `years` |
| [`atlas_compliance_yearly_retention_value`](#atlas_compliance_yearly_retention_value) | No | `1` |
| [`atlas_mas_instances`](#atlas_mas_instances) | No | `[]` |
| [`atlas_database_users`](#atlas_database_users) | No | None |
| [`atlas_db_username`](#atlas_db_username) | No | None |
| [`atlas_db_password`](#atlas_db_password) | No | None |
| [`atlas_store_credentials_in_secret`](#atlas_store_credentials_in_secret) | No | `false` |
| [`atlas_privatelink_enabled`](#atlas_privatelink_enabled) | No | `false` |
| [`atlas_vpc_id`](#atlas_vpc_id) | Conditional | None |
| [`atlas_aws_region`](#atlas_aws_region) | Conditional | None |
| [`atlas_subnet_ids`](#atlas_subnet_ids) | No | `[]` |
| [`atlas_rosa_cidr_ranges`](#atlas_rosa_cidr_ranges) | No | `[]` |
| [`atlas_mongodb_host`](#atlas_mongodb_host) | Conditional | None |
| [`atlas_mongodb_username`](#atlas_mongodb_username) | Conditional | None |
| [`atlas_mongodb_password`](#atlas_mongodb_password) | Conditional | None |
| [`atlas_backup_archive_path`](#atlas_backup_archive_path) | Conditional | None |
| [`atlas_index_file_path`](#atlas_index_file_path) | Conditional | None |

Variables marked **Conditional** are only required for a specific provider or action — the exact condition is noted in each entry below. Most variables only apply to the provider selected in [`mongodb_provider`](#mongodb_provider).

### Instance Configuration Variables

#### mas_instance_id
Unique identifier for the MAS instance that will use this MongoDB deployment — a lowercase alphanumeric string of 3-12 characters (e.g. `prod`, `dev`, `inst1`).

- **Optional**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

When set together with [`mas_config_dir`](#mas_config_dir), the role generates a MongoCfg YAML file (containing a Secret and MongoCfg resource) at `$MAS_CONFIG_DIR/mongocfg-mongoce-system.yaml`, which can be applied with `oc apply -f` or used with the `suite_config` role to connect MAS to this MongoDB instance. Without it, no MAS configuration file is created.

#### mas_config_dir
Local directory path where the generated MongoCfg resource file will be saved — any valid filesystem path (e.g. `~/masconfig`, `./config`).

- **Optional**
- Environment Variable: `MAS_CONFIG_DIR`
- Default: None

Must be set together with [`mas_instance_id`](#mas_instance_id) for MongoCfg generation. Use the same directory across multiple dependency roles (mongodb, db2, sls) to collect all MAS configuration files in one place; the `suite_config` role applies them from there.

#### mongodb_provider
Selects which MongoDB deployment option to use: `community` (MongoDB Community Edition Operator, self-managed on OpenShift), `ibm` (IBM Cloud Databases for MongoDB managed service), `aws` (AWS DocumentDB, MongoDB-compatible managed service), or `atlas` (MongoDB Atlas).

- **Optional**
- Environment Variable: `MONGODB_PROVIDER`
- Default: `community`

Each provider has different requirements: `community` needs cluster storage ([`mongodb_storage_class`](#mongodb_storage_class) and related storage/resource variables); `ibm` needs [`ibmcloud_apikey`](#ibmcloud_apikey); `aws` needs [`aws_access_key_id`](#aws_access_key_id), [`aws_secret_access_key`](#aws_secret_access_key), [`vpc_id`](#vpc_id) and the `docdb_*` variables; `atlas` needs [`aws_access_key_id`](#aws_access_key_id), [`aws_secret_access_key`](#aws_secret_access_key) and [`atlas_account_id`](#atlas_account_id). The provider also determines which [`mongodb_action`](#mongodb_action) values are supported.

!!! warning
    The provider cannot be changed after initial deployment. Migration between providers requires backup and restore procedures.

#### mongodb_action
Specifies which operation to perform on the MongoDB instance; valid values are provider-specific (see below).

- **Optional**
- Environment Variable: `MONGODB_ACTION`
- Default: `install`

Valid values by provider:

- **community**: `install`, `uninstall`, `backup`, `backup-database`, `restore`, `restore-database`
- **aws**: `install`, `uninstall`, `docdb_secret_rotate`, `destroy-data`
- **ibm**: `install`, `uninstall`, `backup`, `restore`, `create-mongo-service-credentials`
- **atlas**: `install`, `uninstall`, `restore`, `restore-database`

Use `install` for initial deployment or updates, `uninstall` to remove the instance, `backup`/`restore` for backup operations (see [Backup and Restore Operations](#backup-and-restore-operations)), `docdb_secret_rotate` to rotate DocumentDB credentials (aws only), and `create-mongo-service-credentials` to generate service credentials (ibm only).

!!! warning
    Destructive actions like `uninstall` and `destroy-data` permanently delete data and cannot be undone. Always back up data before performing destructive operations.

### CE Operator Variables

#### mongodb_namespace
OpenShift namespace where the MongoDB Community Operator and MongoDB cluster will be deployed — any valid Kubernetes namespace name (lowercase alphanumeric and hyphens).

- **Optional**
- Environment Variable: `MONGODB_NAMESPACE`
- Default: `mongoce`

All MongoDB resources (operator, replica set pods, PVCs, secrets, services) are created in this namespace, and the namespace is referenced in MongoCfg generation for service endpoints. Change it only for multiple MongoDB instances or namespace naming requirements; changing it after deployment requires reinstallation.

#### mongodb_version
MongoDB version to deploy — for example `7.0.12`, `7.0.22`, `7.0.23`, `8.0.13`, `8.0.17`, `8.0.20`, or `8.0.23` (check the MAS compatibility matrix for supported versions).

- **Optional**
- Environment Variable: `MONGODB_VERSION`
- Default: Automatically defined by the mongo version specified in the [latest MAS case bundle available](https://github.com/ibm-mas/python-devops/tree/stable/src/mas/devops/data/catalogs)

Leave as default for standard deployments; the default aligns with the tested and supported version for your MAS release. Upgrades between major versions require the corresponding [`mongodb_v5_upgrade`](#mongodb_v5_upgrade), [`mongodb_v6_upgrade`](#mongodb_v6_upgrade), [`mongodb_v7_upgrade`](#mongodb_v7_upgrade), or [`mongodb_v8_upgrade`](#mongodb_v8_upgrade) confirmation flag.

!!! warning
    Never downgrade MongoDB versions, and always create scheduled backups before version changes. MongoDB 5.0+ requires the AVX instruction set — see [Troubleshooting](#troubleshooting) if replica set pods will not start after an upgrade.

#### mongodb_override_spec
Forces the role to use environment variables instead of preserving existing MongoDB spec settings (`true` or `false`).

- **Optional**
- Environment Variable: `MONGODB_OVERRIDE_SPEC`
- Default: `false`

When `false`, existing CPU, memory, storage, and replica settings ([`mongodb_cpu_limits`](#mongodb_cpu_limits), [`mongodb_mem_limits`](#mongodb_mem_limits), [`mongodb_cpu_requests`](#mongodb_cpu_requests), [`mongodb_mem_requests`](#mongodb_mem_requests), [`mongodb_storage_class`](#mongodb_storage_class), [`mongodb_storage_capacity_data`](#mongodb_storage_capacity_data), [`mongodb_storage_capacity_logs`](#mongodb_storage_capacity_logs), [`mongodb_replicas`](#mongodb_replicas)) are preserved during reinstall/upgrade. When `true`, all settings are taken from environment variables and unset variables revert to defaults.

!!! warning
    Check the existing MongoDB installation before enabling this. If environment variables don't match the current spec, resources may be reset to defaults, potentially causing disruption. Unknown settings are not preserved.

#### mongodb_storage_class
Kubernetes storage class for MongoDB persistent volumes — any storage class in your cluster that supports ReadWriteOnce (RWO) access mode.

- **Required** when `mongodb_provider=community`
- Environment Variable: `MONGODB_STORAGE_CLASS`
- Default: None

Six PVCs are created by default (data + logs for each of 3 replicas), so the storage class determines MongoDB performance, reliability, and cost. It cannot be changed after deployment without data migration.

!!! tip
    Verify available storage classes with `oc get storageclass` before deployment.

#### mongodb_storage_capacity_data
Size of the persistent volume claim (PVC) for MongoDB data storage on each replica set member — any valid Kubernetes storage size (e.g. `20Gi`, `100Gi`, `500Gi`, `1Ti`).

- **Optional**
- Environment Variable: `MONGODB_STORAGE_CAPACITY_DATA`
- Default: `20Gi`

Total data storage = this value × number of replicas. PVCs can be expanded (if the storage class supports volume expansion) but not shrunk, so plan for growth when setting the initial size; larger volumes also take longer to back up. Monitor usage to avoid running out of space.

#### mongodb_storage_capacity_logs
Size of the persistent volume claim (PVC) for MongoDB log storage on each replica set member — any valid Kubernetes storage size (e.g. `10Gi`, `20Gi`, `50Gi`).

- **Optional**
- Environment Variable: `MONGODB_STORAGE_CAPACITY_LOGS`
- Default: `20Gi`

Total log storage = this value × number of replicas. Insufficient log space can cause MongoDB operational issues; PVCs can be expanded but not shrunk, so monitor log usage and size for production logging volumes.

#### mongodb_cpu_limits
Maximum CPU cores allocated to each MongoDB container — CPU units as decimal (e.g. `0.5`, `1`, `2`, `4`) or millicores (e.g. `500m`, `1000m`, `2000m`).

- **Optional**
- Environment Variable: `MONGODB_CPU_LIMITS`
- Default: `1`

Set higher than [`mongodb_cpu_requests`](#mongodb_cpu_requests) to allow burst capacity; the default (1 core) suits development or light workloads, production workloads with high query volumes need more. Total CPU limit = this value × number of replicas.

#### mongodb_mem_limits
Maximum memory allocated to each MongoDB container (e.g. `1Gi`, `2Gi`, `4Gi`, `8Gi`, `16Gi`).

- **Optional**
- Environment Variable: `MONGODB_MEM_LIMITS`
- Default: `1Gi`

MongoDB uses memory for caching data and indexes, so performance depends heavily on it: the default (1Gi) is only suitable for development/testing, production deployments typically need 4Gi-8Gi per replica. Set higher than [`mongodb_mem_requests`](#mongodb_mem_requests) for burst capacity; total memory limit = this value × number of replicas.

#### mongodb_cpu_requests
Guaranteed CPU cores reserved for each MongoDB container — CPU units as decimal (e.g. `0.5`, `1`, `2`) or millicores (e.g. `500m`, `1000m`, `2000m`).

- **Optional**
- Environment Variable: `MONGODB_CPU_REQUESTS`
- Default: `500m`

The Kubernetes scheduler uses this to place pods on nodes with sufficient CPU. Set based on expected baseline usage (not peak) and lower than [`mongodb_cpu_limits`](#mongodb_cpu_limits) — the difference provides burst capacity. Also affects the pod Quality of Service (QoS) class; total CPU request = this value × number of replicas.

#### mongodb_mem_requests
Guaranteed memory reserved for each MongoDB container (e.g. `1Gi`, `2Gi`, `4Gi`, `8Gi`).

- **Optional**
- Environment Variable: `MONGODB_MEM_REQUESTS`
- Default: `1Gi`

The Kubernetes scheduler uses this to place pods on nodes with sufficient memory. Set based on expected baseline usage (not peak) and lower than [`mongodb_mem_limits`](#mongodb_mem_limits); production deployments typically need 2Gi-4Gi requests. Also affects the pod Quality of Service (QoS) class; total memory request = this value × number of replicas.

#### mongodb_replicas
Number of MongoDB replica set members to deploy — positive integers, typically 1, 3, or 5 (odd numbers are recommended for proper election quorum).

- **Optional**
- Environment Variable: `MONGODB_REPLICAS`
- Default: `3`

Use 3 (default) or more for production high availability, 5+ for critical workloads, and 1 only for Single Node OpenShift (SNO) clusters or development environments. Each replica requires its own data and log PVCs, and total resources = (CPU + memory + storage) × replicas. Changing the replica count after deployment requires careful planning.

#### custom_labels
Comma-separated list of `key=value` labels to apply to MongoDB resources (e.g. `env=prod,team=platform,app=mongodb`).

- **Optional**
- Environment Variable: `CUSTOM_LABELS`
- Default: None

Labels add organizational metadata for resource tracking, cost allocation, filtering with `oc get` commands, and custom automation. They do not affect MongoDB functionality.

#### mongodb_v5_upgrade
Confirmation flag (`true` or `false`) to upgrade MongoDB from version 4.x to version 5.

- **Optional**
- Environment Variable: `MONGODB_V5_UPGRADE`
- Default: `false`

When `true` and [`mongodb_version`](#mongodb_version) is set to a 5.x version, triggers the upgrade from 4.2/4.4 to 5.x — a one-way operation that cannot be reversed without restoring from backup.

!!! warning
    Always back up before upgrading and test in non-production environments first. Review the MongoDB 5.0 release notes for breaking changes and new requirements (e.g. the AVX instruction set).

#### mongodb_v6_upgrade
Confirmation flag (`true` or `false`) to upgrade MongoDB from version 5 to version 6.

- **Optional**
- Environment Variable: `MONGODB_V6_UPGRADE`
- Default: `false`

When `true` and [`mongodb_version`](#mongodb_version) is set to a 6.x version, triggers the upgrade from 5.x to 6.x — a one-way operation that cannot be reversed without restoring from backup. Always back up before upgrading and review the MongoDB 6.0 release notes for breaking changes.

#### mongodb_v7_upgrade
Confirmation flag (`true` or `false`) to upgrade MongoDB from version 6 to version 7.

- **Optional**
- Environment Variable: `MONGODB_V7_UPGRADE`
- Default: `false`

When `true` and [`mongodb_version`](#mongodb_version) is set to a 7.x version, triggers the upgrade from 6.x to 7.x — a one-way operation that cannot be reversed without restoring from backup. Always back up before upgrading and review the MongoDB 7.0 release notes for breaking changes.

#### mongodb_v8_upgrade
Confirmation flag (`true` or `false`) to upgrade MongoDB from version 7 to version 8.

- **Optional**
- Environment Variable: `MONGODB_V8_UPGRADE`
- Default: `false`

When `true` and [`mongodb_version`](#mongodb_version) is set to an 8.x version, triggers the upgrade from 7.x to 8.x — a one-way operation that cannot be reversed without restoring from backup. Always back up before upgrading and review the MongoDB 8.0 release notes for breaking changes.

### Backup and Restore (CE Operator)

For backup and restore operations, set [`mongodb_action`](#mongodb_action) to one of the following:

- `backup`: Creates a complete backup including database data and Kubernetes resources (secrets, certificates, CRs)
- `backup-database`: Creates a backup of database data only
- `restore`: Performs a full restore by recreating the MongoDB instance from backup resources and then restoring database data
- `restore-database`: Restores only the database data to an already running MongoDB instance without touching instance resources

See [Backup and Restore Operations](#backup-and-restore-operations) for the full process description, requirements, and troubleshooting.

#### mas_backup_dir
Local directory path where backup files will be stored or read from (e.g. `/tmp/masbr`).

- **Required** when performing backup or restore operations
- Environment Variable: `MAS_BACKUP_DIR`
- Default: None

#### mongodb_backup_version
The backup version timestamp to restore from, automatically generated during backup in the format `YYYYMMDD-HHMMSS` (e.g. `20251212-021316`).

- **Required** when performing restore operations
- Environment Variable: `MONGODB_BACKUP_VERSION`
- Default: None

#### mongodb_instance_name
The name of the MongoDB instance to back up or restore.

- **Optional**
- Environment Variable: `MONGODB_INSTANCE_NAME`
- Default: `mas-mongo-ce`

#### override_storageclass
Controls whether to override the storage class for the MongoDB instance during restore — set to `true` to override the storage class with the `MONGODB_STORAGE_CLASS` value or the cluster's default storage class.

- **Optional**
- Environment Variable: `OVERRIDE_STORAGECLASS`
- Default: `false`

#### mas_app_id
Specific MAS application ID for targeted backup/restore operations — when set, only that application's MongoDB databases are backed up; otherwise all MongoDB databases are backed up.

- **Optional**
- Environment Variable: `MAS_APP_ID`
- Default: None

### IBM Cloud

#### ibm_mongo_name
Name for the IBM Cloud Databases for MongoDB instance — a valid IBM Cloud resource name (alphanumeric and hyphens, must start with a letter).

- **Optional**
- Environment Variable: `IBM_MONGO_NAME`
- Default: `mongo-<mas_instance_id>`

The name identifies the instance in the IBM Cloud console, billing reports, and resource lists, and is used as the prefix for the credential secret names. It cannot be changed after creation without recreating the instance; the default derives from [`mas_instance_id`](#mas_instance_id).

#### ibm_mongo_admin_password
Administrator password for the IBM Cloud MongoDB instance — a string meeting IBM Cloud password requirements (minimum length, complexity).

- **Optional**
- Environment Variable: `IBM_MONGO_ADMIN_PASSWORD`
- Default: Auto-generated 20-character string

If not provided, a secure random password is generated and stored in the Kubernetes secret named by [`ibm_mongo_admin_credentials_secret_name`](#ibm_mongo_admin_credentials_secret_name). Auto-generated passwords are recommended; set explicitly only if you need to know the password in advance or integrate with external password management.

#### ibm_mongo_admin_credentials_secret_name
Name of the Kubernetes secret containing MongoDB admin credentials.

- **Optional**
- Environment Variable: None (derived from `ibm_mongo_name`)
- Default: `<ibm_mongo_name>-admin-credentials`

The secret (admin username and password) is created automatically by the role; other roles and applications reference it for database connectivity.

#### ibm_mongo_service_credentials_secret_name
Name of the Kubernetes secret containing MongoDB service credentials.

- **Optional**
- Environment Variable: None (derived from `ibm_mongo_name`)
- Default: `<ibm_mongo_name>-service-credentials`

The secret contains connection strings and credentials for application-level MongoDB access; MAS applications use it to connect to the database.

#### ibm_mongo_resourcegroup
IBM Cloud resource group for MongoDB instance placement — the name of an existing resource group in your account.

- **Optional**
- Environment Variable: `IBM_MONGO_RESOURCEGROUP`
- Default: Value of `ibmcloud_resourcegroup` (`Default`)

Determines access control and billing allocation. Users need appropriate IAM permissions to create resources in the specified resource group — ensure the group exists and your API key has access to it.

#### ibm_mongo_region
IBM Cloud region where the MongoDB instance will be deployed — for example `us-east`, `us-south`, `eu-gb`, `eu-de`, `jp-tok`, or `au-syd`.

- **Optional**
- Environment Variable: `IBM_MONGO_REGION`
- Default: Value of `ibmcloud_region` (`us-east`)

Choose the region closest to your OpenShift cluster for lowest latency, and consider data residency requirements. The region cannot be changed after creation.

#### ibmcloud_apikey
IBM Cloud API key for authentication and resource management — the key must have permissions to create and manage Databases for MongoDB instances in the target resource group and region.

- **Required** when `mongodb_provider=ibm`
- Environment Variable: `IBMCLOUD_APIKEY`
- Default: None

Insufficient permissions cause deployment failures. Store the key securely (e.g. Ansible Vault or an external secret manager) — never commit API keys to source control.

#### ibm_mongo_plan
IBM Cloud service plan for the MongoDB instance — `standard` or `enterprise` (check IBM Cloud documentation for current plan options).

- **Optional**
- Environment Variable: `IBM_MONGO_PLAN`
- Default: `standard`

The plan affects pricing, performance characteristics, SLA, and available features, and cannot be changed after creation without recreating the instance.

#### ibm_mongo_service
IBM Cloud service type identifier for MongoDB — a fixed value used internally by the role.

- **Required** (read-only constant)
- Environment Variable: None (internal constant)
- Default: `databases-for-mongodb`

This is set automatically by the role and used in IBM Cloud API calls to specify the service type; it does not need to be set by users.

#### ibm_mongo_service_endpoints
Network endpoint type for MongoDB connectivity — `public` (accessible over the internet) or `private` (accessible only via the IBM Cloud private network).

- **Optional**
- Environment Variable: `IBM_MONGO_SERVICE_ENDPOINTS`
- Default: `public`

`private` is recommended for production deployments: it is more secure and has lower latency, but requires the OpenShift cluster to reach the IBM Cloud private network. Use `public` when the cluster lacks private network connectivity (with appropriate firewall rules).

#### ibm_mongo_version
MongoDB version to deploy in IBM Cloud — versions supported by IBM Cloud Databases (e.g. `4.2`, `4.4`, `5.0`, `6.0`).

- **Optional**
- Environment Variable: `IBM_MONGO_VERSION`
- Default: `4.4`

The default (`4.4`) suits older MAS versions; check the MAS compatibility matrix before selecting a newer version. Versions cannot easily be downgraded, and newer MongoDB versions may require MAS updates.

#### ibm_mongo_memory
Memory allocation per MongoDB member in MB — integer, minimum varies by plan (typically 1024 MB).

- **Optional**
- Environment Variable: `IBM_MONGO_MEMORY`
- Default: `3840` (3.75 GB)

Memory affects caching performance and query execution; IBM Cloud charges based on the allocation. The default suits development or small deployments — production workloads typically need 8192 MB or more per member.

#### ibm_mongo_disk
Disk storage allocation per MongoDB member in MB — integer, minimum varies by plan (typically 5120 MB).

- **Optional**
- Environment Variable: `IBM_MONGO_DISK`
- Default: `30720` (30 GB)

Storage holds databases, indexes, and operational logs. Disk can be expanded online but not reduced, so plan for data growth and monitor storage usage; total storage = this value × number of members.

#### ibm_mongo_cpu
Dedicated CPU cores per MongoDB member — `0` (shared CPU) or an integer ≥ 3 for dedicated cores.

- **Optional**
- Environment Variable: `IBM_MONGO_CPU`
- Default: `0` (shared CPU)

`0` gives lower cost with variable performance (suitable for development and light workloads); dedicated CPUs (≥3) significantly increase cost but provide the consistent performance production workloads typically need. Available CPU ranges vary by plan.

#### ibm_mongo_backup_id
IBM Cloud backup CRN (Cloud Resource Name) to restore from — format `crn:v1:...`, obtained from the IBM Cloud console or CLI.

- **Required** when `is_restore=true`
- Environment Variable: `IBM_MONGO_BACKUP_ID`
- Default: None

Leave unset for new deployments. Restoring replaces all current data with the state captured in the specified backup — verify the backup CRN before restoring and test restore procedures in non-production first.

#### is_restore
Flag to enable restore from an IBM Cloud backup instead of creating a new MongoDB instance (`true` or `false`).

- **Optional**
- Environment Variable: `IS_RESTORE`
- Default: `false`

When `true`, requires [`ibm_mongo_backup_id`](#ibm_mongo_backup_id) and [`restored_mongodb_service_name`](#restored_mongodb_service_name). Always verify backup details before setting to `true` — restore operations cannot be undone without another backup.

#### restored_mongodb_service_name
Name for the MongoDB service created when restoring from backup — a valid IBM Cloud resource name, which can be the same as or different from the original.

- **Required** when `is_restore=true`
- Environment Variable: `RESTORED_MONGO_SERVICE_NAME`
- Default: None

Using a different name than [`ibm_mongo_name`](#ibm_mongo_name) allows restoring alongside the existing instance for side-by-side comparison before switching over.

### AWS DocumentDB

#### aws_access_key_id
AWS account access key ID for authentication — the key must have IAM permissions for DocumentDB, EC2 (VPC/subnets/security groups), and related services.

- **Required** when `mongodb_provider=aws`
- Environment Variable: `AWS_ACCESS_KEY_ID`
- Default: None

Used together with [`aws_secret_access_key`](#aws_secret_access_key) to authenticate all AWS API calls; insufficient permissions cause deployment failures.

!!! warning
    Never commit AWS credentials to source control. Store them securely (e.g. Ansible Vault or an external secret manager).

#### aws_secret_access_key
AWS account secret access key — must correspond to the provided [`aws_access_key_id`](#aws_access_key_id).

- **Required** when `mongodb_provider=aws`
- Environment Variable: `AWS_SECRET_ACCESS_KEY`
- Default: None

Invalid or mismatched credentials cause authentication failures. Rotate credentials regularly following AWS security best practices.

#### aws_region
AWS region where the DocumentDB cluster will be deployed — a valid AWS region code (e.g. `us-east-1`, `us-east-2`, `us-west-2`, `eu-west-1`, `ap-southeast-1`).

- **Optional**
- Environment Variable: `AWS_REGION`
- Default: `us-east-2`

Choose the region closest to your OpenShift cluster for lowest latency, and consider data residency requirements. The VPC must exist in this region and the region cannot be changed after creation.

#### vpc_id
AWS VPC ID where DocumentDB resources will be created (format `vpc-xxxxxxxxxxxxxxxxx`).

- **Required** when `mongodb_provider=aws`
- Environment Variable: `VPC_ID`
- Default: None

The DocumentDB cluster, subnets, and security groups are created in this VPC — use the same VPC as your OpenShift cluster for direct connectivity. The VPC must exist in [`aws_region`](#aws_region) and have sufficient available IP addresses and appropriate routing; DocumentDB is only accessible from resources within this VPC or connected networks. The [`docdb_cidr_az1`](#docdb_cidr_az1)/[`docdb_cidr_az2`](#docdb_cidr_az2)/[`docdb_cidr_az3`](#docdb_cidr_az3) subnets are created within it, and the ingress/egress CIDRs should match its ranges.

#### docdb_cluster_name
Name for the AWS DocumentDB cluster — a valid cluster identifier (lowercase, alphanumeric, hyphens, must start with a letter), unique within your AWS account and region.

- **Required** when `mongodb_provider=aws`
- Environment Variable: `DOCDB_CLUSTER_NAME`
- Default: None

The name appears in the AWS console, CloudWatch metrics, and billing, and is used as the prefix for related resources: the subnet group ([`docdb_subnet_group_name`](#docdb_subnet_group_name)), security group ([`docdb_security_group_name`](#docdb_security_group_name)), and admin credentials secret ([`docdb_admin_credentials_secret_name`](#docdb_admin_credentials_secret_name)). Choose a meaningful name as it cannot easily be changed.

#### docdb_subnet_group_name
Name for the DocumentDB subnet group, which associates the cluster with specific subnets across availability zones.

- **Optional**
- Environment Variable: None (derived from `docdb_cluster_name`)
- Default: `docdb-<docdb_cluster_name>`

The subnet group is created automatically by the role and includes the subnets defined by [`docdb_cidr_az1`](#docdb_cidr_az1), [`docdb_cidr_az2`](#docdb_cidr_az2), and [`docdb_cidr_az3`](#docdb_cidr_az3). Default naming is recommended for consistency.

#### docdb_security_group_name
Name for the DocumentDB security group, which controls network access to the cluster.

- **Optional**
- Environment Variable: None (derived from `docdb_cluster_name`)
- Default: `docdb-<docdb_cluster_name>`

The security group is created automatically by the role; its firewall rules are based on [`docdb_ingress_cidr`](#docdb_ingress_cidr) and [`docdb_egress_cidr`](#docdb_egress_cidr). Default naming is recommended for consistency.

#### docdb_admin_credentials_secret_name
Name of the Kubernetes secret containing DocumentDB admin credentials.

- **Optional**
- Environment Variable: None (derived from `docdb_cluster_name`)
- Default: `<docdb_cluster_name>-admin-credentials`

The secret is created automatically by the role in the MAS core namespace and contains the admin username and password ([`docdb_master_username`](#docdb_master_username)); MAS and other applications reference it for database connectivity.

#### docdb_engine_version
DocumentDB engine version to deploy.

- **Optional**
- Environment Variable: `DOCDB_ENGINE_VERSION`
- Default: `5.0.0`

Determines MongoDB compatibility and available features. MAS requires DocumentDB 5.0.0 — it is the only version MAS is certified with.

!!! warning
    Do not change this value unless MAS documentation explicitly supports other versions.

#### docdb_master_username
Master username for DocumentDB cluster administration — a valid DocumentDB username (alphanumeric, must start with a letter, 1-63 characters).

- **Optional**
- Environment Variable: `DOCDB_MASTER_USERNAME`
- Default: `docdbadmin`

This user has full administrative privileges; the username is stored in the Kubernetes secret specified by [`docdb_admin_credentials_secret_name`](#docdb_admin_credentials_secret_name). Choose carefully — it cannot be changed after cluster creation.

#### docdb_instance_class
AWS instance class for DocumentDB instances — e.g. `db.t3.medium`, `db.r5.large`, `db.r5.xlarge`, `db.r6g.large`.

- **Optional**
- Environment Variable: `DOCDB_INSTANCE_CLASS`
- Default: `db.t3.medium`

Determines compute and memory capacity per instance, affecting CPU, memory, network performance, and cost. Use `db.t3.medium` for development or small deployments, `db.r5.large` or larger for production (typical), and consider ARM-based `db.r6g` instances for better price/performance. Total cost = instance class cost × [`docdb_instance_number`](#docdb_instance_number).

#### docdb_instance_number
Number of DocumentDB instances in the cluster — an integer from 1 to 16.

- **Optional**
- Environment Variable: `DOCDB_INSTANCE_NUMBER`
- Default: `3`

Instances are distributed across the availability zones defined by the `docdb_cidr_az*` subnets for fault tolerance. Use 3 (default) or more for production high availability, 5+ for critical workloads, and 1 only for development/testing (a single instance has no failover capability). Total cost = instance class cost × this value.

#### docdb_instance_identifier_prefix
Prefix for DocumentDB instance identifiers — lowercase alphanumeric with hyphens; instance names are formed as `{prefix}-1`, `{prefix}-2`, etc.

- **Required** when `mongodb_provider=aws`
- Environment Variable: `DOCDB_INSTANCE_IDENTIFIER_PREFIX`
- Default: None

Instance identifiers appear in the AWS console and CloudWatch metrics; typically the prefix matches or relates to [`docdb_cluster_name`](#docdb_cluster_name).

#### docdb_ingress_cidr
IPv4 CIDR block allowed to connect to the DocumentDB cluster (e.g. `10.0.0.0/16`, `172.31.0.0/16`), used in security group ingress rules.

- **Required** when `mongodb_provider=aws`
- Environment Variable: `DOCDB_INGRESS_CIDR`
- Default: None

Typically set to the CIDR of your OpenShift cluster's VPC so applications in the VPC can reach DocumentDB; tighter subnet CIDRs improve security. Only traffic from this range can connect — too restrictive blocks legitimate traffic, too permissive reduces security.

#### docdb_egress_cidr
IPv4 CIDR block for outbound connections from the DocumentDB cluster (e.g. `10.0.0.0/16`, `172.31.0.0/16`), used in security group egress rules.

- **Required** when `mongodb_provider=aws`
- Environment Variable: `DOCDB_EGRESS_CIDR`
- Default: None

Usually set to the same value as [`docdb_ingress_cidr`](#docdb_ingress_cidr) (the VPC CIDR for standard deployments). DocumentDB can only send traffic to this range, which affects its ability to respond to client connections.

#### docdb_cidr_az1
IPv4 CIDR block for the DocumentDB subnet in availability zone 1 — valid IPv4 CIDR within the VPC range (e.g. `10.0.1.0/24`) that does not overlap other subnets in the VPC.

- **Required** when `mongodb_provider=aws`
- Environment Variable: `DOCDB_CIDR_AZ1`
- Default: None

If a subnet with the tag `Name: <docdb_cluster_name>` already exists it is reused; otherwise a new subnet is created. Each DocumentDB instance needs an IP address — use /24 or larger subnets for flexibility.

#### docdb_cidr_az2
IPv4 CIDR block for the DocumentDB subnet in availability zone 2 — valid IPv4 CIDR within the VPC range (e.g. `10.0.2.0/24`) that does not overlap other subnets in the VPC.

- **Required** when `mongodb_provider=aws`
- Environment Variable: `DOCDB_CIDR_AZ2`
- Default: None

If a subnet with the tag `Name: <docdb_cluster_name>` already exists it is reused; otherwise a new subnet is created. Use different availability zones for AZ1, AZ2, and AZ3 to ensure high availability across zones.

#### docdb_cidr_az3
IPv4 CIDR block for the DocumentDB subnet in availability zone 3 — valid IPv4 CIDR within the VPC range (e.g. `10.0.3.0/24`) that does not overlap other subnets in the VPC.

- **Required** when `mongodb_provider=aws`
- Environment Variable: `DOCDB_CIDR_AZ3`
- Default: None

If a subnet with the tag `Name: <docdb_cluster_name>` already exists it is reused; otherwise a new subnet is created. Three availability zones provide the best fault tolerance — ensure the subnets are in different AZs for proper distribution.

### AWS DocumentDB Secret Rotation Variables

The following variables are used for rotating DocumentDB credentials. These are typically used with `mongodb_action=docdb_secret_rotate`.

#### docdb_mongo_instance_name
DocumentDB instance name for secret rotation — must match an existing DocumentDB instance identifier.

- **Required** when rotating secrets (`mongodb_action=docdb_secret_rotate`)
- Environment Variable: `DOCDB_MONGO_INSTANCE_NAME`
- Default: None

Identifies the specific DocumentDB instance whose credentials will be rotated; it belongs to the cluster named by [`docdb_cluster_name`](#docdb_cluster_name) and is reachable at [`docdb_host`](#docdb_host). Verify the instance name before rotation to avoid affecting the wrong instance.

#### docdb_host
DocumentDB instance host address for the connection during secret rotation — any instance hostname or endpoint from the cluster, obtained from the AWS console or the DocumentDB cluster endpoint.

- **Required** when rotating secrets
- Environment Variable: `DOCDB_HOST`
- Default: None

Used with [`docdb_port`](#docdb_port) to connect to DocumentDB for the rotation operation; any instance host from the cluster can be used.

#### docdb_port
DocumentDB instance port number — typically `27017` (the default DocumentDB port unless customized during cluster creation).

- **Required** when rotating secrets
- Environment Variable: `DOCDB_PORT`
- Default: None (typically `27017`)

Used with [`docdb_host`](#docdb_host) to establish the connection for credential rotation.

#### docdb_instance_username
DocumentDB username whose password is being rotated — an existing DocumentDB user, typically the application user or admin user.

- **Required** when rotating secrets
- Environment Variable: `DOCDB_INSTANCE_USERNAME`
- Default: None

This user's password is changed during rotation; applications using this username must be able to handle the new password (e.g. connection pooling with reconnection logic). The current password is provided via [`docdb_instance_password_old`](#docdb_instance_password_old).

#### docdb_instance_password_old
Current password for the user being rotated.

- **Required** when rotating secrets
- Environment Variable: `DOCDB_PASSWORD_OLD`
- Default: None

Used to authenticate before changing the password — an incorrect password causes the rotation to fail. After rotation this password is no longer valid; store it securely.

#### docdb_master_password
DocumentDB master user password for administrative operations during rotation — the master user has the privileges to change other users' passwords.

- **Required** when rotating secrets
- Environment Variable: `DOCDB_MASTER_PASSWORD`
- Default: None

Must be the current master password, paired with [`docdb_master_username`](#docdb_master_username). Store master credentials securely and never commit them to source control.

#### docdb_master_username
DocumentDB master username used to authenticate the rotation — see [`docdb_master_username`](#docdb_master_username) in [AWS DocumentDB](#aws-documentdb) for the full entry.

- **Required** when rotating secrets
- Environment Variable: `DOCDB_MASTER_USERNAME`
- Default: None

Must match the master username set during DocumentDB cluster creation (typically `docdbadmin`, the default of the variable above).

### AWS DocumentDB destroy-data Action Variables

#### mas_instance_id
The specified MAS instance ID — see [`mas_instance_id`](#mas_instance_id) in [Instance Configuration Variables](#instance-configuration-variables) for the full entry.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

#### mongo_username
MongoDB username used to connect to the instance.

- **Required** when `mongodb_action=destroy-data`
- Environment Variable: `MONGO_USERNAME`
- Default: None

#### mongo_password
MongoDB password used to connect to the instance.

- **Required** when `mongodb_action=destroy-data`
- Environment Variable: `MONGO_PASSWORD`
- Default: None

#### config
MongoDB connection configuration (configDb, authMechanism, retryWrites, hosts) — refer to the [destroy-data example playbook](#aws-documentdb-destroy-data-action) for the structure.

- **Required**
- Environment Variable: `CONFIG`
- Default: None

#### certificates
MongoDB TLS certificates (list with `alias` and `crt` fields) — refer to the [destroy-data example playbook](#aws-documentdb-destroy-data-action) for the structure.

- **Required**
- Environment Variable: `CERTIFICATES`
- Default: None

### MongoDB Atlas

The MongoDB Atlas provider automates the complete lifecycle of Atlas cluster provisioning, including:

1. **Project Creation**: Creates or verifies an Atlas project within your organization
2. **Backup Compliance Policy**: Configures automated backup policies with compliance settings
3. **Cluster Provisioning**: Creates a MongoDB cluster with specified configuration
4. **Database Users**: Creates instance-specific database users with scoped permissions
5. **Secret Management**: Stores connection information in AWS Secrets Manager
   - **Cluster-level secret**: `<account_id>/<cluster_name>/mongo` (empty credentials for cluster metadata)
   - **Instance-level secrets**: `<account_id>/<cluster_name>/<instance_id>/mongo` (with user credentials)

### Atlas Project and Cluster Configuration

#### atlas_org_id
MongoDB Atlas organization ID where the project will be created — a 24-character hexadecimal string (e.g. `507f1f77bcf86cd799439011`).

- **Required** when creating a new project (when `atlas_project_id` is not provided)
- Environment Variable: `ATLAS_ORG_ID`
- Default: None

Determines which organization owns the project and its billing. Find it in the Atlas Console under Organization Settings → Organization ID.

#### atlas_project_name
Name for the Atlas project to create or find — alphanumeric string with spaces, hyphens, and underscores allowed.

- **Required** when `atlas_project_id` is not provided
- Environment Variable: `ATLAS_PROJECT_NAME`
- Default: None

If a project with this name exists in the organization it will be reused; otherwise a new project is created. Use instead of [`atlas_project_id`](#atlas_project_id) when you want the role to find or create a project by name; creating a new project also requires [`atlas_org_id`](#atlas_org_id).

#### atlas_project_id
MongoDB Atlas project ID where the cluster will be created — a 24-character hexadecimal string (e.g. `507f1f77bcf86cd799439011`).

- **Required** when `mongodb_provider=atlas`
- Environment Variable: `ATLAS_PROJECT_ID`
- Default: None

All Atlas resources are organized under projects; this determines billing, access control, and resource organization for the cluster. Obtain it from the Atlas console under Project Settings (not required for the `restore-database` action).

#### atlas_account_id
AWS account ID used to construct the AWS Secrets Manager secret name for Atlas API credentials — a 12-digit number (e.g. `123456789012`).

- **Required** when `mongodb_provider=atlas`
- Environment Variable: `ATLAS_ACCOUNT_ID`
- Default: None

The Atlas API credentials are only retrieved from the AWS Secrets Manager secret named `<atlas_account_id>/mongodb-atlas` (looked up in the region set by [`atlas_aws_region`](#atlas_aws_region)); the role fails if the secret does not exist or cannot be accessed. The secret must be created before running this role — see [Prerequisites](#mongodb-atlas-prerequisites) for the creation instructions.

#### atlas_cluster_name
Name of the MongoDB Atlas cluster to create or manage — alphanumeric string, 1-64 characters, can include hyphens.

- **Required** when `mongodb_provider=atlas`
- Environment Variable: `ATLAS_CLUSTER_NAME`
- Default: None

Identifies the cluster within the project for all cluster operations; the name appears in the Atlas console and connection strings and cannot be changed after cluster creation.

#### atlas_cluster_provider
Cloud provider where the Atlas cluster will be deployed.

- **Required** when `mongodb_provider=atlas`
- Environment Variable: `ATLAS_CLUSTER_PROVIDER`
- Default: `AWS`

Currently only `AWS` is supported; it determines the available regions, instance sizes, and pricing. The cluster region is set with [`atlas_aws_region`](#atlas_aws_region) and must be valid for the selected provider. VPC peering is only supported when using `AWS`.

#### atlas_cluster_size
Atlas cluster tier/instance size — `M10`, `M20`, `M30`, `M40`, `M50`, `M60`, `M80`, `M140`, `M200`, `M300`, `M400`, or `M700`.

- **Required** when `mongodb_provider=atlas`
- Environment Variable: `ATLAS_CLUSTER_SIZE`
- Default: None

Determines cluster compute and memory resources, affecting performance, storage capacity, and hourly cost. M10 is the minimum for production; the M0/M2/M5 free/shared tiers are not supported. The tier cannot be decreased, only increased.

#### atlas_mongodb_version
MongoDB version to deploy in the Atlas cluster — `6.0`, `7.0`, or `8.0` (check Atlas for currently supported versions).

- **Optional**
- Environment Variable: `ATLAS_MONGODB_VERSION`
- Default: `7.0`

Determines the available MongoDB features and compatibility. Version upgrades are supported but downgrades are not.

#### atlas_backup_enabled
Enable automated backups for the Atlas cluster (`true` or `false`).

- **Optional**
- Environment Variable: `ATLAS_BACKUP_ENABLED`
- Default: `false`

When enabled, Atlas creates continuous backups with point-in-time recovery (affects cluster cost). Enable for production clusters; disable only for temporary/test clusters. Must be `true` when [`atlas_backup_compliance_enabled`](#atlas_backup_compliance_enabled) is enabled.

### Atlas Audit Logging Configuration

MongoDB Atlas Auditing captures database operations for compliance and security monitoring. It records authentication events, authorization failures, and database operations, which is required for FedRAMP, HIPAA, and other regulatory compliance.

#### atlas_audit_enabled
Enable audit logging for the Atlas project (`true` or `false`).

- **Optional** when `mongodb_provider=atlas`
- Environment Variable: `ATLAS_AUDIT_ENABLED`
- Default: `false`

Captures audit events based on the configured filter; logs are accessible via the Atlas UI or API and additional costs may apply based on log volume. Audit logging is configured at the project level and applies to all clusters in the project. Enable for environments requiring regulatory compliance (FedRAMP, HIPAA, SOC 2, PCI-DSS) or security monitoring.

#### atlas_audit_filter
JSON filter defining which audit events to capture, following MongoDB query language syntax — for example `{"atype": "authenticate"}` (authentication only), `{"result": {"$ne": 0}}` (failed operations), `{"param.ns": {"$regex": "^mydb\\."}}` (specific database), `{"param.db": "admin"}` (admin database operations), or `{}` (all events).

- **Optional** when `atlas_audit_enabled=true`
- Environment Variable: `ATLAS_AUDIT_FILTER`
- Default: None — a default comprehensive filter is generated automatically

When not provided, the generated filter excludes MAS instance users (from [`atlas_mas_instances`](#atlas_mas_instances)) while capturing authentication events, authorization failures, and critical database operations (DDL, DML, user/role management). More specific filters reduce log volume and performance impact; the filter choice maps to common compliance needs (SOC 2 authentication/authorization tracking, HIPAA PHI access monitoring, PCI-DSS cardholder data logging, FedRAMP comprehensive audit trail).

!!! warning
    Invalid JSON will cause the configuration to fail.

#### atlas_audit_authorization_success
Log successful authorization events in addition to failures (`true` or `false`).

- **Optional** when `atlas_audit_enabled=true`
- Environment Variable: `ATLAS_AUDIT_AUTHORIZATION_SUCCESS`
- Default: `true`

Set to `true` for the comprehensive audit trails required by strict compliance frameworks (it significantly increases log volume); set to `false` to reduce log volume by only capturing authorization failures. Most compliance frameworks require logging of both successful and failed authorization attempts.

### Atlas S3 Audit Log Export Configuration

MongoDB Atlas can export audit logs to AWS S3 for long-term retention and compliance using the **Log Integrations API** (`/api/atlas/v2/groups/{groupId}/logIntegrations`). This provides a cost-effective way to store audit logs beyond Atlas's retention period and enables integration with external log analysis tools. The export covers both `MONGOD_AUDIT` and `MONGOS_AUDIT` log types, automatically creates and configures all required AWS infrastructure, and is fully idempotent (safe to run multiple times).

Prerequisites: [`atlas_audit_enabled`](#atlas_audit_enabled) must be set to `true`, AWS credentials must be configured (via AWS CLI or environment variables), and the credentials need sufficient IAM permissions to create S3 buckets and IAM roles.

#### atlas_s3_audit_export_enabled
Enable export of audit logs to AWS S3 (`true` or `false`).

- **Optional** when `mongodb_provider=atlas`
- Environment Variable: `ATLAS_S3_AUDIT_EXPORT_ENABLED`
- Default: `false`

When enabled, the role creates an encrypted S3 bucket (name auto-generated from the Atlas project name as `<project-name>-atlas-audit-logs`, with special characters replaced by hyphens and converted to lowercase), sets up an IAM role for MongoDB Atlas with cross-account access, configures cloud provider access in Atlas, creates the log integration via the Atlas Log Integrations API, and applies lifecycle policies for cost optimization. Enable for long-term audit log retention (beyond Atlas's retention period) and compliance archival.

#### atlas_s3_audit_bucket_prefix
Prefix (folder path) within the S3 bucket — a valid S3 object key prefix (e.g. `audit-logs/mongodb`, `compliance/atlas-audit`, `logs/production/mongodb`).

- **Optional** when `atlas_s3_audit_export_enabled=true`
- Environment Variable: `ATLAS_S3_AUDIT_BUCKET_PREFIX`
- Default: `mongodb-atlas-audit-logs`

Organizes audit logs within the bucket; logs are stored at `s3://<bucket_name>/<prefix>/<project_id>/...`.

#### atlas_s3_audit_log_retention_days
Number of days to retain audit logs in S3 — positive integer (365 days / 1 year by default).

- **Optional** when `atlas_s3_audit_export_enabled=true`
- Environment Variable: `ATLAS_S3_AUDIT_LOG_RETENTION_DAYS`
- Default: `365`

Creates an S3 lifecycle policy that deletes logs after the retention period; logs transition to Glacier storage after [`atlas_s3_audit_glacier_transition_days`](#atlas_s3_audit_glacier_transition_days). This helps manage storage costs while meeting compliance requirements.

#### atlas_s3_audit_bucket_enable_versioning
Enable S3 bucket versioning for audit logs (`true` or `false`), protecting against accidental deletion or modification.

- **Optional** when `atlas_s3_audit_export_enabled=true`
- Environment Variable: `ATLAS_S3_AUDIT_BUCKET_ENABLE_VERSIONING`
- Default: `false`

When `true`, all versions of objects are retained (increasing storage costs) and noncurrent versions are deleted after [`atlas_s3_audit_noncurrent_version_retention_days`](#atlas_s3_audit_noncurrent_version_retention_days); total retention = [`atlas_s3_audit_log_retention_days`](#atlas_s3_audit_log_retention_days) + noncurrent retention. Enable for strict compliance requirements that mandate immutable audit logs.

#### atlas_s3_audit_glacier_transition_days
Days before transitioning audit logs to Glacier storage — integer ≥ 30 (AWS requirement); common values are 30, 60, 90, and 180 days.

- **Optional** when `atlas_s3_audit_export_enabled=true`
- Environment Variable: `ATLAS_S3_AUDIT_GLACIER_TRANSITION_DAYS`
- Default: `90`

Reduces storage costs: logs remain in Standard storage for faster access during this period, after which retrieval times increase but costs decrease significantly. Must be less than [`atlas_s3_audit_log_retention_days`](#atlas_s3_audit_log_retention_days).

#### atlas_s3_audit_noncurrent_version_retention_days
Days to retain noncurrent versions of audit logs when versioning is enabled — positive integer.

- **Optional** when `atlas_s3_audit_bucket_enable_versioning=true`
- Environment Variable: `ATLAS_S3_AUDIT_NONCURRENT_VERSION_RETENTION_DAYS`
- Default: `30`

Only applies when versioning is enabled; it extends total retention time — for example with 365 days retention and 30 days noncurrent retention, audit logs can be stored for up to 395 days total.

### Atlas Alert Monitoring Configuration

MongoDB Atlas Alert Monitoring provides proactive notifications for cluster health, performance, and security events. Alerts are configured per cluster using matchers that target [`atlas_cluster_name`](#atlas_cluster_name), so each alert configuration only applies to the specified cluster.

When `atlas_enable_alerts=true`, basic alerts (CPU, memory, and connection count — warning and critical thresholds) are automatically configured. Additional categories require explicit enablement: cluster health alerts ([`atlas_enable_cluster_health_alerts`](#atlas_enable_cluster_health_alerts)), performance alerts ([`atlas_enable_performance_alerts`](#atlas_enable_performance_alerts)), and security alerts ([`atlas_enable_security_alerts`](#atlas_enable_security_alerts)).

#### atlas_enable_alerts
Enable basic alert monitoring for the Atlas cluster (`true` or `false`).

- **Optional** when `mongodb_provider=atlas`
- Environment Variable: `ATLAS_ENABLE_ALERTS`
- Default: `false`

Automatically configures 6 basic alerts (CPU, memory, connections — warning and critical) with email notifications, helping prevent downtime by alerting before critical issues occur. Enable for production and staging environments; requires [`atlas_alert_notification_emails`](#atlas_alert_notification_emails) to be configured with at least one email address.

#### atlas_alert_notification_emails
List of email addresses to receive alert notifications — comma-separated list (e.g. `ocm-team@example.com,monitoring@example.com`) or JSON array (e.g. `["ocm-team@example.com", "monitoring@example.com"]`).

- **Required** when `atlas_enable_alerts=true`
- Environment Variable: `ATLAS_ALERT_NOTIFICATION_EMAILS`
- Default: `[]`

All specified addresses receive notifications for all configured alerts.

!!! important
    Use OCM (Operations Center Manager) email addresses only. OCM emails are integrated with incident management systems and ensure proper alert routing and escalation — do not configure generic or personal email addresses. At least one OCM email address is required when alerts are enabled.

#### atlas_enable_cluster_health_alerts
Enable alerts for cluster health issues (`true` or `false`).

- **Optional** when `atlas_enable_alerts=true`
- Environment Variable: `ATLAS_ENABLE_CLUSTER_HEALTH_ALERTS`
- Default: `false`

Configures alerts for replication oplog window running out (< 1 hour), primary elected (replica set election), no primary available, and cluster mongos missing. Enable for production and staging environments to monitor cluster stability.

#### atlas_enable_performance_alerts
Enable alerts for performance issues (`true` or `false`).

- **Optional** when `atlas_enable_alerts=true`
- Environment Variable: `ATLAS_ENABLE_PERFORMANCE_ALERTS`
- Default: `false`

Configures alerts for CPU usage, memory usage, disk usage, connection count (warning and critical thresholds, controlled by the `atlas_alert_*_thresholds` variables), and query performance (scanned objects per returned). Enable for production and staging environments to monitor resource utilization.

#### atlas_enable_security_alerts
Enable alerts for security events (`true` or `false`).

- **Optional** when `atlas_enable_alerts=true`
- Environment Variable: `ATLAS_ENABLE_SECURITY_ALERTS`
- Default: `false`

Configures alerts for too many unhealthy connections and users without multi-factor authentication. Enable for all environments to monitor security posture.

#### atlas_alert_cpu_thresholds
CPU utilization percentage thresholds for WARNING and CRITICAL alerts — JSON array of two integers between 0-100, as `[warning, critical]`.

- **Optional** when `atlas_enable_performance_alerts=true`
- Environment Variable: `ATLAS_ALERT_CPU_THRESHOLDS`
- Default: `[70, 80]`

The warning alert triggers at the first value and the critical alert at the second; lower values trigger alerts earlier, and the critical threshold should be higher than the warning for proper escalation.

```bash
export ATLAS_ALERT_CPU_THRESHOLDS='[70, 80]'
```

#### atlas_alert_memory_thresholds
Memory utilization percentage thresholds for WARNING and CRITICAL alerts — JSON array of two integers between 0-100, as `[warning, critical]`.

- **Optional** when `atlas_enable_performance_alerts=true`
- Environment Variable: `ATLAS_ALERT_MEMORY_THRESHOLDS`
- Default: `[70, 80]`

The warning alert triggers at the first value and the critical alert at the second; memory exhaustion can cause performance degradation and OOM errors.

```bash
export ATLAS_ALERT_MEMORY_THRESHOLDS='[70, 80]'
```

#### atlas_alert_connection_thresholds
Connection count thresholds, as a percentage of maximum, for WARNING and CRITICAL alerts — JSON array of two integers between 0-100, as `[warning, critical]`.

- **Optional** when `atlas_enable_performance_alerts=true`
- Environment Variable: `ATLAS_ALERT_CONNECTION_THRESHOLDS`
- Default: `[70, 80]`

The warning alert triggers at the first value and the critical alert at the second; connection exhaustion can prevent new connections and cause application failures.

```bash
export ATLAS_ALERT_CONNECTION_THRESHOLDS='[70, 80]'
```

#### atlas_alert_interval_min
Interval in minutes for metric threshold alert evaluation — positive integer.

- **Optional**
- Environment Variable: `ATLAS_ALERT_INTERVAL_MIN`
- Default: `60`

Defines how frequently Atlas evaluates metric thresholds for all performance alerts (CPU, memory, connections, query performance — all `OUTSIDE_METRIC_THRESHOLD` alert types). This is a required parameter for Atlas metric threshold alerts: lower values (e.g. 1-5 minutes) give faster detection but may increase alert noise; higher values (e.g. 10-15 minutes) reduce noise but delay detection. The default of 60 minutes balances responsiveness with stability.

### Atlas Backup Compliance Policy Configuration

The backup compliance policy enforces backup retention and protection rules at the project level. When enabled, it applies to all clusters in the project.

#### atlas_backup_compliance_enabled
Enable the backup compliance policy for the Atlas project (`true` or `false`).

- **Optional** when `mongodb_provider=atlas`
- Environment Variable: `ATLAS_BACKUP_COMPLIANCE_ENABLED`
- Default: `false`

Enforces backup retention policies, prevents unauthorized backup deletion, and enables compliance features. Requires [`atlas_backup_enabled`](#atlas_backup_enabled) set to `true` on the cluster, plus the `atlas_compliance_*` variables below for configuration. Enable for production environments requiring regulatory compliance or strict backup retention policies.

!!! warning
    Once enabled, the compliance policy cannot be disabled without contacting Atlas support.

#### atlas_compliance_authorized_email
Email address of the authorized user for compliance policy changes — a valid email address.

- **Required** when `atlas_backup_compliance_enabled=true`
- Environment Variable: `ATLAS_COMPLIANCE_AUTHORIZED_EMAIL`
- Default: `admin@example.com`

Used for the audit trail and authorization of compliance policy changes.

#### atlas_compliance_authorized_first_name
First name of the authorized user for compliance policy changes.

- **Required** when `atlas_backup_compliance_enabled=true`
- Environment Variable: `ATLAS_COMPLIANCE_AUTHORIZED_FIRST_NAME`
- Default: `Admin`

#### atlas_compliance_authorized_last_name
Last name of the authorized user for compliance policy changes.

- **Required** when `atlas_backup_compliance_enabled=true`
- Environment Variable: `ATLAS_COMPLIANCE_AUTHORIZED_LAST_NAME`
- Default: `User`

#### atlas_compliance_copy_protection
Enable copy protection for backups (`true` or `false`).

- **Optional** when `atlas_backup_compliance_enabled=true`
- Environment Variable: `ATLAS_COMPLIANCE_COPY_PROTECTION`
- Default: `false`

Prevents copying of backup snapshots to other regions or projects — when enabled, backups cannot be copied outside the configured region.

#### atlas_compliance_encryption_at_rest
Enable encryption at rest for backups (`true` or `false`).

- **Optional** when `atlas_backup_compliance_enabled=true`
- Environment Variable: `ATLAS_COMPLIANCE_ENCRYPTION_AT_REST`
- Default: `false`

Ensures all backup snapshots are encrypted at rest, adding an encryption layer to backup storage.

#### atlas_compliance_pit_enabled
Enable point-in-time restore for compliance backups (`true` or `false`).

- **Optional** when `atlas_backup_compliance_enabled=true`
- Environment Variable: `ATLAS_COMPLIANCE_PIT_ENABLED`
- Default: `false`

Enables continuous backup with point-in-time recovery capability — allows restore to any point in time within the retention window and increases backup storage costs.

#### atlas_compliance_restore_window_days
Number of days for the restore window — integer (1-365).

- **Optional** when `atlas_backup_compliance_enabled=true`
- Environment Variable: `ATLAS_COMPLIANCE_RESTORE_WINDOW_DAYS`
- Default: `7`

Defines how many days of continuous backup history are maintained for point-in-time restore; determines the maximum age of data that can be restored.

#### atlas_compliance_hourly_frequency_interval
Frequency interval for hourly backups, in hours — integer (1, 2, 4, 6, 8, or 12).

- **Optional** when `atlas_backup_compliance_enabled=true`
- Environment Variable: `ATLAS_COMPLIANCE_HOURLY_FREQUENCY_INTERVAL`
- Default: `6`

How often hourly snapshots are taken; more frequent backups provide finer recovery granularity but increase storage costs.

#### atlas_compliance_hourly_retention_unit
Retention unit for hourly backups — `days`, `weeks`, or `months`.

- **Optional** when `atlas_backup_compliance_enabled=true`
- Environment Variable: `ATLAS_COMPLIANCE_HOURLY_RETENTION_UNIT`
- Default: `days`

#### atlas_compliance_hourly_retention_value
Retention value for hourly backups — integer (1-365 for days, 1-52 for weeks, 1-36 for months).

- **Optional** when `atlas_backup_compliance_enabled=true`
- Environment Variable: `ATLAS_COMPLIANCE_HOURLY_RETENTION_VALUE`
- Default: `7`

How long hourly backups are retained; longer retention increases storage costs.

#### atlas_compliance_daily_frequency_interval
Frequency interval for daily backups, in days — integer (1-365).

- **Optional** when `atlas_backup_compliance_enabled=true`
- Environment Variable: `ATLAS_COMPLIANCE_DAILY_FREQUENCY_INTERVAL`
- Default: `1`

How often daily snapshots are taken.

#### atlas_compliance_daily_retention_unit
Retention unit for daily backups — `days`, `weeks`, or `months`.

- **Optional** when `atlas_backup_compliance_enabled=true`
- Environment Variable: `ATLAS_COMPLIANCE_DAILY_RETENTION_UNIT`
- Default: `days`

#### atlas_compliance_daily_retention_value
Retention value for daily backups — integer (1-365 for days, 1-52 for weeks, 1-36 for months).

- **Optional** when `atlas_backup_compliance_enabled=true`
- Environment Variable: `ATLAS_COMPLIANCE_DAILY_RETENTION_VALUE`
- Default: `7`

How long daily backups are retained.

#### atlas_compliance_weekly_frequency_interval
Frequency interval for weekly backups, in weeks — integer (1-52).

- **Optional** when `atlas_backup_compliance_enabled=true`
- Environment Variable: `ATLAS_COMPLIANCE_WEEKLY_FREQUENCY_INTERVAL`
- Default: `1`

How often weekly snapshots are taken.

#### atlas_compliance_weekly_retention_unit
Retention unit for weekly backups — `weeks`, `months`, or `years`.

- **Optional** when `atlas_backup_compliance_enabled=true`
- Environment Variable: `ATLAS_COMPLIANCE_WEEKLY_RETENTION_UNIT`
- Default: `weeks`

#### atlas_compliance_weekly_retention_value
Retention value for weekly backups — integer (1-52 for weeks, 1-36 for months, 1-10 for years).

- **Optional** when `atlas_backup_compliance_enabled=true`
- Environment Variable: `ATLAS_COMPLIANCE_WEEKLY_RETENTION_VALUE`
- Default: `4`

How long weekly backups are retained.

#### atlas_compliance_monthly_frequency_interval
Frequency interval for monthly backups, in months — integer (1-12).

- **Optional** when `atlas_backup_compliance_enabled=true`
- Environment Variable: `ATLAS_COMPLIANCE_MONTHLY_FREQUENCY_INTERVAL`
- Default: `1`

How often monthly snapshots are taken.

#### atlas_compliance_monthly_retention_unit
Retention unit for monthly backups — `months` or `years`.

- **Optional** when `atlas_backup_compliance_enabled=true`
- Environment Variable: `ATLAS_COMPLIANCE_MONTHLY_RETENTION_UNIT`
- Default: `months`

#### atlas_compliance_monthly_retention_value
Retention value for monthly backups — integer (1-36 for months, 1-10 for years).

- **Optional** when `atlas_backup_compliance_enabled=true`
- Environment Variable: `ATLAS_COMPLIANCE_MONTHLY_RETENTION_VALUE`
- Default: `12`

How long monthly backups are retained.

#### atlas_compliance_yearly_frequency_interval
Frequency interval for yearly backups, in years — integer (1-10).

- **Optional** when `atlas_backup_compliance_enabled=true`
- Environment Variable: `ATLAS_COMPLIANCE_YEARLY_FREQUENCY_INTERVAL`
- Default: `1`

How often yearly snapshots are taken.

#### atlas_compliance_yearly_retention_unit
Retention unit for yearly backups — `years`.

- **Optional** when `atlas_backup_compliance_enabled=true`
- Environment Variable: `ATLAS_COMPLIANCE_YEARLY_RETENTION_UNIT`
- Default: `years`

#### atlas_compliance_yearly_retention_value
Retention value for yearly backups — integer (1-10).

- **Optional** when `atlas_backup_compliance_enabled=true`
- Environment Variable: `ATLAS_COMPLIANCE_YEARLY_RETENTION_VALUE`
- Default: `1`

How long yearly backups are retained; longer retention increases storage costs significantly.

### Atlas Database Users Configuration

#### atlas_mas_instances
List of MAS instance names that will use this cluster — a list or comma-separated string (e.g. `["inst1", "inst2"]` or `"inst1,inst2"`).

- **Optional** when `mongodb_provider=atlas`
- Environment Variable: `ATLAS_MAS_INSTANCES`
- Default: `[]`

Each instance gets a dedicated database user with scoped permissions (username format `<instance_name>-user`). Used with [`atlas_store_credentials_in_secret`](#atlas_store_credentials_in_secret) to create instance-level secrets.

#### atlas_database_users
Multi-user database configuration for the Atlas cluster — a dictionary of user configurations with `username`, `auth_database_name`, and `roles`.

- **Optional** when `mongodb_provider=atlas` (alternative to `atlas_db_username`/`atlas_db_password`)
- Environment Variable: Not supported (use playbook vars)
- Default: None

Defines multiple database users with different roles and permissions, with auto-generated passwords stored in Atlas — the recommended approach for production deployments requiring multiple users with different access levels.

```yaml
atlas_database_users:
  user1:
    username: "app_user"
    auth_database_name: "admin"
    roles:
      - database_name: "admin"
        role_name: "readWriteAnyDatabase"
```

#### atlas_db_username
Legacy single database user username — a valid MongoDB username string.

- **Optional** when `mongodb_provider=atlas` (alternative to `atlas_database_users`)
- Environment Variable: `ATLAS_DB_USERNAME`
- Default: None

Creates a single database user; must be used with [`atlas_db_password`](#atlas_db_password). For simple deployments only — consider [`atlas_database_users`](#atlas_database_users) for production.

#### atlas_db_password
Legacy single database user password — a strong password string.

- **Optional** when `mongodb_provider=atlas` (alternative to `atlas_database_users`)
- Environment Variable: `ATLAS_DB_PASSWORD`
- Default: None

Sets the password for the single database user; must be used with [`atlas_db_username`](#atlas_db_username). Store securely and never commit to version control.

### Atlas Secret Management Configuration

#### atlas_account_id
AWS account ID for the secret naming convention — see [`atlas_account_id`](#atlas_account_id) in [Atlas Project and Cluster Configuration](#atlas-project-and-cluster-configuration) for the full entry.

- **Required** when `atlas_store_credentials_in_secret=true`
- Environment Variable: `ATLAS_ACCOUNT_ID`
- Default: None

Used to construct the secret names `<account_id>/<cluster_name>/mongo` and `<account_id>/<cluster_name>/<instance_id>/mongo` in AWS Secrets Manager.

#### atlas_store_credentials_in_secret
Store Atlas connection information in AWS Secrets Manager (`true` or `false`).

- **Optional** when `mongodb_provider=atlas`
- Environment Variable: `ATLAS_STORE_CREDENTIALS_IN_SECRET`
- Default: `false`

When enabled, the role creates/updates two types of secrets after provisioning: a **cluster-level secret** `<account_id>/<cluster_name>/mongo` containing cluster metadata (hosts, port, CA certificates) with empty username/password fields, and **instance-level secrets** `<account_id>/<cluster_name>/<instance_id>/mongo` containing instance-specific credentials plus the cluster metadata. Requires [`atlas_account_id`](#atlas_account_id), [`atlas_cluster_name`](#atlas_cluster_name), and [`atlas_aws_region`](#atlas_aws_region), plus the AWS CLI configured with appropriate IAM permissions; works with [`atlas_mas_instances`](#atlas_mas_instances) to create the instance-level secrets. Enable for production deployments to centralize credential management and let MAS retrieve connection information.

```json
{
  "info": "# YAML content with hosts, port, CA certificates",
  "username": "instance-user",
  "password": "generated-password"
}
```

The cluster-level secret has empty `username` and `password` fields (or `docdb_username`/`docdb_password` for compatibility), while instance-level secrets contain actual credentials.

### Atlas VPC/PrivateLink Configuration

#### atlas_privatelink_enabled
Enable AWS PrivateLink for secure, private connectivity between the Atlas cluster and your AWS VPC (`true` or `false`).

- **Optional** when `mongodb_provider=atlas`
- Environment Variable: `ATLAS_PRIVATELINK_ENABLED`
- Default: `false`

When enabled, PrivateLink configuration requires [`atlas_vpc_id`](#atlas_vpc_id), [`atlas_aws_region`](#atlas_aws_region), [`atlas_project_id`](#atlas_project_id), [`atlas_subnet_ids`](#atlas_subnet_ids), and [`atlas_rosa_cidr_ranges`](#atlas_rosa_cidr_ranges). Private connectivity is only supported for AWS deployments.

#### atlas_vpc_id
AWS VPC ID for the PrivateLink connection with the Atlas cluster (e.g. `vpc-0123456789abcdef0`).

- **Optional** when `mongodb_provider=atlas` and configuring PrivateLink
- Environment Variable: `ATLAS_VPC_ID`
- Default: None

Enables private network connectivity between the AWS VPC and the Atlas cluster; used together with [`atlas_aws_region`](#atlas_aws_region) and [`atlas_subnet_ids`](#atlas_subnet_ids).

#### atlas_aws_region
AWS region for the PrivateLink configuration, the Atlas credentials secret lookup, and the S3 audit export bucket — for example `US_EAST_1` or `us-east-1`.

- **Optional** when `mongodb_provider=atlas` and configuring PrivateLink
- Environment Variable: `ATLAS_AWS_REGION`
- Default: None

Must match the region of the AWS VPC. The role converts the region to Atlas format automatically (e.g. `us-east-1` → `US_EAST_1`), so either AWS or Atlas format works.

#### atlas_subnet_ids
AWS subnet IDs for VPC Endpoint placement (private connectivity edge subnets) — provided as a list or comma-separated string (e.g. `subnet-111,subnet-222,subnet-333`).

- **Optional** when `atlas_privatelink_enabled=true`
- Environment Variable: `ATLAS_SUBNET_IDS`
- Default: `[]`

Required when PrivateLink is enabled; the endpoints are placed in these subnets.

#### atlas_rosa_cidr_ranges
ROSA cluster CIDR ranges for the PrivateLink security group ingress rules — provided as a list or comma-separated string (e.g. `10.0.0.0/16`).

- **Optional** when `atlas_privatelink_enabled=true`
- Environment Variable: `ATLAS_ROSA_CIDR_RANGES`
- Default: `[]`

Required when PrivateLink is enabled; allows the ROSA cluster to reach the private endpoint.

### Atlas Restore (Data Migration)

MongoDB Atlas provides a fully managed backup service with automated backups, point-in-time recovery, and easy restore capabilities through the Atlas console and API — **for normal backup and restore operations, use the Atlas managed backup service** (enabled by default with [`atlas_backup_enabled`](#atlas_backup_enabled)). The manual restore functionality documented here is intended for **data migration from AWS DocumentDB scenarios only**.

#### atlas_mongodb_host
MongoDB Atlas cluster hostname for the restore connection (e.g. `cluster0.abc123.mongodb.net`).

- **Required** when `mongodb_provider=atlas` and `mongodb_action=restore|restore-database`
- Environment Variable: `ATLAS_MONGODB_HOST`
- Default: None

Used with [`atlas_mongodb_username`](#atlas_mongodb_username) and [`atlas_mongodb_password`](#atlas_mongodb_password) to build the MongoDB connection URI for the `mongorestore` command. Use the SRV hostname format without the `mongodb+srv://` prefix.

#### atlas_mongodb_username
MongoDB database username for the restore connection — must have `readWriteAnyDatabase` or equivalent write permissions.

- **Required** when `mongodb_provider=atlas` and `mongodb_action=restore|restore-database`
- Environment Variable: `ATLAS_MONGODB_USERNAME`
- Default: None

Used for authentication during the `mongorestore` operation.

#### atlas_mongodb_password
MongoDB database password for the restore connection — the password for the specified username.

- **Required** when `mongodb_provider=atlas` and `mongodb_action=restore|restore-database`
- Environment Variable: `ATLAS_MONGODB_PASSWORD`
- Default: None

Used for authentication during the `mongorestore` operation. Store securely and never commit to version control.

#### atlas_backup_archive_path
Local path to the MongoDB backup archive file (`.tar.gz`, e.g. `/path/to/mongodb-backup-20240621.tar.gz`).

- **Required** when `mongodb_provider=atlas` and `mongodb_action=restore|restore-database`
- Environment Variable: `ATLAS_BACKUP_ARCHIVE_PATH`
- Default: None

The role extracts this archive and restores the data to the Atlas cluster. Used with [`atlas_index_file_path`](#atlas_index_file_path) — this is for the `restore-database` action which uses local files, not the `restore` action which downloads from S3.

#### atlas_index_file_path
Local path to the MongoDB index backup JSON file (e.g. `/path/to/mongodb-indexes-20240621.json`).

- **Required** when `mongodb_provider=atlas` and `mongodb_action=restore|restore-database`
- Environment Variable: `ATLAS_INDEX_FILE_PATH`
- Default: None

The role reads this file and recreates the indexes after the data restore; the file must be valid JSON containing index definitions for each database and collection. Used with [`atlas_backup_archive_path`](#atlas_backup_archive_path) — this is for the `restore-database` action which uses local files, not the `restore` action which downloads from S3.

## Backup and Restore Operations

This section provides comprehensive information about MongoDB backup and restore operations for the Community Edition (CE) operator.

### Action Comparison

| Action | Purpose | Instance Resources | Database Data | Prerequisites | Use Case |
|--------|---------|-------------------|---------------|---------------|----------|
| `backup` | Create backup | Yes | Yes | Running MongoDB instance | Regular backups, disaster recovery preparation |
| `backup-database` | Database-only backup | No | Yes | Running MongoDB instance | Regular backups, disaster recovery preparation |
| `restore` | Full restore | Yes (recreates instance) | Yes | Backup with instance resources | Disaster recovery, cluster migration, complete restoration |
| `restore-database` | Database-only restore | No (preserves existing) | Yes | Running MongoDB instance with matching version | Data recovery, selective restore, testing |

### Backup Process

The MongoDB backup operation creates a backup of your MongoDB instance and databases associated with your MAS instance:

1. **Database Backup**: Uses `mongodump` to export databases with filter `"^(mas|iot|sls|ibm-sls)(_|-)({{ mas_instance_id }}|sls)_(?!.*monitor$)"` to match databases like `mas-<instance-id>_<app-id>` or `iot-<instance-id>_<app-id>` or `ibm-sls_sls_licensing` or `sls-<instance-id>_sls_licensing`.
2. **Instance Resources** : Backs up Kubernetes resources including:
   - CustomResourceDefinition (CRD)
   - MongoDBCommunity Custom Resource (CR)
   - Secrets (TLS certificates, credentials)
   - Certificate resources
   - Issuer resources
   - Mongodb operator deployment
   - service monitoring
   - grafana dashboards

**Backup Directory Structure:**
```text
/tmp/masbr/
└── backup-<YYYYMMDD-HHMMSS>-mongoce/
    ├── data/
    │   ├── mongodump-<YYYYMMDD-HHMMSS>.tar.gz
    │   └── mongodb-info.yaml
    └── resources/
        ├── mongodbcommunitys/
        ├── secrets/
        ├── certificates/
        └── issuers/
        └── {kind}s/
```

### Restore Process

The MongoDB role supports two types of restore operations:

### 1. Full Restore (`restore` action)
Performs a complete restoration of both the MongoDB instance and its databases:

**Steps:**

1. Validates backup files and required variables
2. Restores the namespace (Project)
3. Restores Secrets and ConfigMaps
4. Restores CustomResourceDefinitions (CRDs)
5. Restores RBAC resources (ServiceAccount, Role, RoleBinding)
6. Configures anyuid permissions for MongoDB service accounts
7. Restores the MongoDB Operator Deployment
8. Waits for MongoDB operator to be ready
9. Restores Certificate Manager resources (Issuer, Certificate)
10. Restores the MongoDBCommunity Custom Resource (Overrides storageclass if flag is set)
11. Waits for MongoDB StatefulSets to be ready
12. Restores ServiceMonitor and GrafanaDashboard resources
13. Restores database data using `mongorestore`

**When to use:**

- Disaster recovery scenarios
- Migrating MongoDB to a new cluster
- Recreating a deleted MongoDB instance
- Setting up a new environment from backup

**Requirements:**

- `mas_instance_id`: MAS instance identifier
- `mas_backup_dir`: Directory containing the backup
- `mongodb_backup_version`: Timestamp of the backup to restore
- `override_storageclass`: Set to `true` to override storage class during instance restore

### 2. Database-Only Restore (`restore-database` action)
Restores only the database data to an existing MongoDB instance:

**Steps:**

1. Validates backup files and required variables
2. Verifies existing MongoDB installation is running
3. Checks MongoDB version compatibility
4. Restores database data using `mongorestore`

**When to use:**

- Restoring data to an existing MongoDB instance
- Recovering from data corruption without recreating the instance
- Selective database restoration
- Testing data restoration without affecting instance configuration

**Requirements:**

- `mas_instance_id`: MAS instance identifier
- `mas_backup_dir`: Directory containing the backup
- `mongodb_backup_version`: Timestamp of the backup to restore
- `mongodb_namespace`: Namespace where MongoDB is running
- `mongodb_instance_name`: Name of the existing MongoDB instance
- MongoDB instance must already be running and accessible

### Important Considerations

**Version Compatibility:**

- Target MongoDB version must match the backup version exactly
- Version upgrades should be performed separately, not during restore
- The restore process validates version compatibility before proceeding
- For `restore-database` action, the existing MongoDB instance must be running the same version as the backup

**Storage Requirements:**

- Ensure sufficient storage in the backup directory
- Plan for at least 2x the database size for backup storage
- Backup directory structure: `/tmp/masbr/backup-<YYYYMMDD-HHMMSS>-mongoce/`
- Monitor disk space during backup operations

**Security:**

- Backup files contain sensitive data and credentials
- Secure backup directory with appropriate permissions (chmod 700 recommended)
- Consider encrypting backups for long-term storage
- Backup includes TLS certificates and admin credentials
- Restrict access to backup files to authorized personnel only

**Performance:**

- Backup operations may impact MongoDB performance
- Schedule backups during low-usage periods
- Monitor resource utilization during backup/restore
- Large databases may take significant time to backup/restore
- Network bandwidth may affect backup/restore speed

**Restore Action Differences:**

- **`restore` action**: Recreates the entire MongoDB instance from scratch, including all Kubernetes resources and restores database
- **`restore-database` action**: Only restores database data to an existing instance, preserving current configuration

### Backup and Restore Best Practices

1. **Regular Backups**: Schedule automated backups at regular intervals
2. **Test Restores**: Periodically test restore procedures in non-production environments
3. **Monitor Operations**: Implement monitoring and alerting for backup failures
4. **Backup Validation**: Verify backup integrity after completion
5. **Retention Policy**: Implement and document backup retention policies
6. **Disaster Recovery**: Include MongoDB backup/restore in your DR plan

### Backup and Restore Issues

**Backup Failures:**

- **Permission Errors**: Verify backup role and user creation succeeded. Check MongoDB pod logs with `oc logs -n mongoce <pod-name> -c mongod`
- **Disk Space Issues**: Ensure sufficient space in backup directory. Clean up old backups if needed like `/tmp/<mongodb_backup_version>`. Check with `df -h`.
- **Pod Access Issues**: Verify pod is running and accessible. Check network connectivity to the cluster

**Restore Failures:**

- **Version Mismatch**: Ensure target MongoDB version matches backup version. Deploy correct version before restoring
- **Authentication Errors**: Verify admin credentials are correct. Check MongoDB health status
- **Missing Backup Files**: Verify backup directory path and version. Ensure backup completed successfully
- **Data Inconsistency**: Verify backup integrity. Check restore logs for errors. Consider re-running restore

**General Issues:**

- **Pods Not Starting After Restore**: Check pod events with `oc describe pod -n mongoce <pod-name>`. Verify PVCs are bound. Check resource limits and node capacity
- **Connection Issues**: Verify network policies and service configurations. Check certificate validity

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
    mas_instance_id: masinst1
    mas_backup_dir: /tmp/masbr
    mongodb_action: backup
  roles:
    - ibm.mas_devops.mongodb
```

### Backup with Instance Resources (CE Operator)
Create a complete backup including both database data and instance resources (secrets, certificates, issuers).

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_backup_dir: /tmp/masbr
    mongodb_action: backup
  roles:
    - ibm.mas_devops.mongodb
```

### Backup Database (CE Operator)
Create a backup of database data.

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_backup_dir: /tmp/masbr
    mongodb_action: backup-database
  roles:
    - ibm.mas_devops.mongodb
```

### Restore Database (CE Operator)
Restore MongoDB databases from a backup to an existing MongoDB instance without recreating the instance resources.

**Use Case**: This action is ideal when you need to restore database data to an already running MongoDB instance, such as recovering from data corruption or restoring specific databases.

**Prerequisites**:

- MongoDB instance must already be installed and running
- MongoDB version must match the backup version
- Backup files must be available in the specified backup directory

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mongodb_action: restore-database
    mas_instance_id: masinst1
    mongodb_backup_version: 20251212-021316
    mas_backup_dir: /tmp/masbr
    mongodb_namespace: mongoce
    mongodb_instance_name: mas-mongo-ce
  roles:
    - ibm.mas_devops.mongodb
```

**What this does**:

1. Validates that the backup exists at the specified location
2. Verifies the MongoDB instance is running in the specified namespace
3. Checks version compatibility between backup and running instance
4. Restores database data using `mongorestore` command
5. Preserves all existing instance configuration and resources

**Note**: This action does NOT restore instance resources (secrets, certificates, CRs). Use the `restore` action for full instance restoration.

### Full Restore (CE Operator)
Perform a complete restoration of MongoDB instance including all Kubernetes resources and database data from a backup.

**Use Case**: This action is ideal for disaster recovery scenarios where you need to recreate the entire MongoDB instance from scratch, including all configuration, secrets, certificates, and data.

**Prerequisites**:

- Backup files must be available in the specified backup directory
- Backup must include instance resources (secrets, certificates, CRs)
- Target cluster must have cert-manager installed
- Sufficient storage and resources available

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mongodb_action: restore
    mas_instance_id: masinst1
    mongodb_backup_version: 20251212-021316
    mas_backup_dir: /tmp/masbr
  roles:
    - ibm.mas_devops.mongodb
```

**What this does**:

1. Validates backup files and required variables
2. Restores namespace, secrets, and ConfigMaps
3. Restores CRDs and RBAC resources
4. Restores MongoDB Operator deployment
5. Restores Certificate Manager resources
6. Restores MongoDBCommunity Custom Resource
7. Waits for MongoDB instance to be fully operational
8. Restores database data using `mongorestore`

**Note**: This is a complete restoration that recreates the MongoDB instance from scratch. Use `restore-database` action if you only need to restore data to an existing instance.

### Install from Backup (CE Operator)
Deploy a new MongoDB instance using configuration from a backup and restore data from a backup. This is useful for disaster recovery or migrating MongoDB to a new cluster.

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mongodb_action: install
    mas_instance_id: masinst1
    mongodb_backup_version: 20251212-021316
    mas_backup_dir: /tmp/masbr
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

### Install (MongoDB Atlas)
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mongodb_provider: atlas
    mongodb_action: install
    
    # Project configuration (creates project if it doesn't exist)
    atlas_org_id: "507f1f77bcf86cd799439011"
    atlas_project_name: "MAS Production"
    
    # Cluster configuration
    atlas_cluster_name: "mas-cluster"
    atlas_cluster_provider: "AWS"
    atlas_aws_region: "US_EAST_1"
    atlas_cluster_size: "M10"
    atlas_mongodb_version: "7.0"
    
    # Backup configuration
    atlas_backup_enabled: true
    atlas_backup_compliance_enabled: true
    atlas_compliance_authorized_email: "admin@example.com"
    atlas_compliance_authorized_first_name: "Admin"
    atlas_compliance_authorized_last_name: "User"
    
    # Audit logging configuration
    atlas_audit_enabled: true
    atlas_audit_filter: '{"atype": "authenticate"}'
    atlas_audit_authorization_success: false
    
    # Alert monitoring configuration
    # Basic alerts (CPU, memory, connections) are automatically enabled
    atlas_enable_alerts: true
    atlas_alert_notification_emails: "ocm-team@example.com,monitoring@example.com"
    
    # Optional: Enable additional alert categories
    atlas_enable_cluster_health_alerts: true
    atlas_enable_performance_alerts: true  # Disk and query performance
    
    # MAS instances (creates dedicated users for each)
    atlas_mas_instances: "inst1,inst2,inst3"
    
    # PrivateLink configuration
    atlas_privatelink_enabled: true
    atlas_vpc_id: "vpc-0123456789abcdef0"
    atlas_subnet_ids: "subnet-111,subnet-222,subnet-333"
    atlas_rosa_cidr_ranges: "10.0.0.0/16"
    
    # Secret management
    atlas_store_credentials_in_secret: true
    atlas_account_id: "123456789012"
    
  roles:
    - ibm.mas_devops.mongodb
```

### Install (MongoDB Atlas - Minimal Configuration)
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mongodb_provider: atlas
    
    # AWS account ID (used to retrieve credentials from AWS Secrets Manager)
    # Secret name will be: <atlas_account_id>/mongodb-atlas
    atlas_account_id: "123456789012"
    aws_region: "us-east-1"
    
    # Use existing project
    atlas_project_id: "507f1f77bcf86cd799439011"
    
    # Cluster configuration
    atlas_cluster_name: "mas-dev-cluster"
    atlas_aws_region: "US_EAST_1"
    atlas_cluster_size: "M10"
    
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

### AWS DocumentDB Secret Rotation
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_config_dir: ~/masconfig
    mongodb_provider: aws
    mongodb_action: docdb_secret_rotate
    docdb_mongo_instance_name: test-db-instance
    docdb_host: aws.test1.host7283-*****
    docdb_port: 27017
    docdb_master_username: admin
    docdb_master_password: pass***
    docdb_instance_password_old: oldpass****
    docdb_instance_username: testuser
    aws_access_key_id: aws-key
    aws_secret_access_key: aws-access-key

  roles:
    - ibm.mas_devops.mongodb
```

### Restore (MongoDB Atlas)
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mongodb_provider: atlas
    mongodb_action: restore-database
    atlas_backup_archive_path: /path/to/mongodb-backup-20240621.tar.gz
    atlas_index_file_path: /path/to/mongodb-indexes-20240621.json
    atlas_mongodb_host: cluster0.abc123.mongodb.net
    atlas_mongodb_username: admin
    atlas_mongodb_password: "{{ lookup('env', 'ATLAS_DB_PASSWORD') }}"
  roles:
    - ibm.mas_devops.mongodb
```

### Backup (AWS DocumentDB)

This example demonstrates how to backup an AWS DocumentDB cluster. The backup creates two files:

- `mongodb-backup.tar.gz` - Compressed database backup
- `collection-indexes.json` - Collection indexes for restore

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mongodb_provider: aws
    mongodb_action: backup-database
    docdb_cluster_name: massre-mas-cluster-8-mongo.cluster-cvwxreialrtj.us-east-1.docdb.amazonaws.com
    docdb_master_username: masinst_inst04
    docdb_master_password: "{{ lookup('env', 'DOCDB_MASTER_PASSWORD') }}"
    docdb_port: 27017
    aws_region: us-east-1
  roles:
    - ibm.mas_devops.mongodb
```

**Command Line Example:**
```bash
ansible-playbook ibm/mas_devops/playbooks/docdb_backup_simple.yml \
  -e "docdb_cluster_name=massre-mas-cluster-8-mongo.cluster-cvwxreialrtj.us-east-1.docdb.amazonaws.com" \
  -e "docdb_master_username=masinst_inst04" \
  -e "docdb_master_password=fn9Uh5wZ4KsZy4OZ0OXx" \
  -e "aws_region=us-east-1" \
  -e "mongodb_provider=aws" \
  -e "mongodb_action=backup-database" \
  -e "docdb_port=27017"
```

**Backup Output:**
The backup process creates the following files in `/tmp/docdb-backup-<timestamp>/`:

- `mongodb-backup.tar.gz` - Full database backup (compressed)
- `collection-indexes.json` - Collection indexes metadata

**Important Notes:**

- The backup does NOT upload to S3 automatically
- Both files are created locally in the backup directory
- Temporary files (logs, scripts, CA certificates) are automatically cleaned up after backup
- The backup uses `mongodump` with TLS/SSL connection to DocumentDB
- Collection indexes are extracted separately for easier restore operations

**Required Variables:**

- `docdb_cluster_name` - DocumentDB cluster endpoint
- `docdb_master_username` - Admin username
- `docdb_master_password` - Admin password (use environment variable or vault)
- `aws_region` - AWS region where DocumentDB is deployed
- `mongodb_provider` - Must be set to `aws`
- `mongodb_action` - Must be set to `backup-database` or `backup`

**Optional Variables:**

- `docdb_port` - DocumentDB port (default: 27017)
- `docdb_backup_dir` - Custom backup directory (default: `/tmp/docdb-backup-<timestamp>`)
- `docdb_ca_cert_url` - Custom CA certificate URL (default: AWS global bundle)

### AWS DocumentDB destroy-data action

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
    Please be cautious while performing any of the troubleshooting steps outlined below. It is important to understand that the MongoDB Community operator persists data within Persistent Volume Claims. These claims should not be removed. Inadvertent deletion of the `mongoce` namespace could result in data loss.

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
    If the MongoDB CA Certificate expires the MongoDB replica set will become unusable. Replica set members will not be able to communicate with each other and client applications (i.e. Maximo Application Suite components) will not be able to connect.

In order to renew the CA Certificate used by the MongoDB replica set the following steps must be taken:

- Delete the CA Certificate resource
- Delete the MongoDB server Certificate resource
- Delete the Secrets resources associated with both the CA Certificate and Server Certificate
- Delete the Secret resource which contains the MongoDB configuration parameters
- Delete the ConfigMap resources which contains the CA certificate
- Delete the Secret resource which contains the server certificate and private key

The following steps illustrate the process required to renew the CA Certificate, server certificate and reconfigure the MongoDB replica set with the new CA and server certificates.

The first step is to stop the Mongo replica set and MongoDB CE Operator pod.

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

Once the `mongodb` role has completed the MongoDB CE Operator pod and Mongo replica set should be configured.

After the CA and server Certificates have been renewed you must ensure that the MongoCfg Suite CR is updated with the new CA Certificate. First obtain the CA Certificate from the Secret resource `mongo-ca-secret`. Then edit the Suite MongoCfg CR in the Maximo Application Suite core namespace. This is done by updating the appropriate certificate under `.spec.certificates` in the MongoCfg CR:

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
