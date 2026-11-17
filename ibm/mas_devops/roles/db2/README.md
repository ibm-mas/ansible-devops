# db2

This role creates, upgrades, migrates, or manages Db2 instances using the Db2u Operator. When installing Db2, the Db2u operator will be installed into the same namespace as the Db2 instance.

**IMPORTANT:** The Db2uCluster resource is deprecated (replaced by Db2uInstance). This Ansible collection will retain support for Db2uCluster until its eventual EOL. Use the `db2u-migration` action to migrate existing Db2uCluster deployments to Db2uInstance.

If you already have the Db2 operator and Db2 instances running in separate namespaces, this role will migrate the Db2 **operators** (not the instances) from `ibm-common-services` to the namespace defined by the `db2_namespace` property (in case of a new role execution for a Db2 install or Db2 upgrade). A private root CA certificate is created and is used to secure the TLS connections to the database. A Db2 Warehouse cluster will be created along with a public TLS encrypted route to allow external access to the cluster (access is via the ssl-server nodeport port on the *-db2u-engn-svc service). Internal access is via the *-db2u-engn-svc service and port 50001. Both the external route and the internal service use the same server certificate.

The private root CA certificate and the server certificate are available from the `db2u-ca` and `db2u-certificate` secrets in the Db2 namespace.  The default user is `db2inst1` and the password is available in the `instancepassword` secret in the same namespace.  You can examine the deployed resources in the Db2 namespace. This example assumes the default namespace `db2u`:

```bash
oc -n db2u get db2uinstance

NAME        STATE   MAINTENANCESTATE   AGE
db2u-db01   Ready   None               29m
```

It typically takes 20-30 minutes from the Db2uCluster being created until it is ready. If the Db2uCluster is not ready after that period then check that all the PersistentVolumeClaims in the Db2 namespace are ready and that the pods in the namespace are not stuck in init state. If the `c-<db2_instance_name>-db2u-0` pod is running then you can exec into the pod and check the `/var/log/db2u.log` for any issue.

If the `mas_instance_id` and `mas_config_dir` are provided then the role will generate the JdbcCfg yaml that can be used to configure MAS to connect to this database. It does not apply the yaml to the cluster but does provide you with the yaml files to apply if needed.

When upgrading Db2, specify the existing namespace where the `Db2uInstance` instances exist. All the instances under that namespace will be upgraded to the Db2 version specified. The version of Db2 **must** match the channel of Db2 being used for the upgrade.

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`db2u_kind`](#db2u_kind) | No | `db2ucluster` |
| [`ibm_common_services_namespace`](#ibm_common_services_namespace) | No | `ibm-common-services` |
| [`db2_action`](#db2_action) | No | `install` |
| [`db2_namespace`](#db2_namespace) | No | `db2u` |
| [`db2_channel`](#db2_channel) | No | Operator default channel |
| [`db2_instance_name`](#db2_instance_name) | Yes | None |
| [`ibm_entitlement_key`](#ibm_entitlement_key) | Yes | None |
| [`db2_dbname`](#db2_dbname) | No | `BLUDB` |
| [`db2_version`](#db2_version) | Conditional | Latest supported by operator |
| [`db2_license_file`](#db2_license_file) | Conditional | None |
| [`db2_v12_upgrade`](#db2_v12_upgrade) | Conditional | `false` |
| [`db2_type`](#db2_type) | No | `db2wh` |
| [`db2_timezone`](#db2_timezone) | No | None (UTC) |
| [`db2_4k_device_support`](#db2_4k_device_support) | No | `ON` |
| [`db2_workload`](#db2_workload) | No | `ANALYTICS` |
| [`db2_table_org`](#db2_table_org) | No | `ROW` |
| [`db2_ldap_username`](#db2_ldap_username) | No | None (`db2inst1`) |
| [`db2_ldap_password`](#db2_ldap_password) | Conditional | None |
| [`db2_rotate_password`](#db2_rotate_password) | No | `False` |
| [`db2_meta_storage_class`](#db2_meta_storage_class) | Conditional | Cluster default (auto-detected) |
| [`db2_meta_storage_size`](#db2_meta_storage_size) | No | `10Gi` |
| [`db2_meta_storage_accessmode`](#db2_meta_storage_accessmode) | No | `ReadWriteMany` |
| [`db2_data_storage_class`](#db2_data_storage_class) | Conditional | Cluster default (auto-detected) |
| [`db2_data_storage_size`](#db2_data_storage_size) | No | `50Gi` |
| [`db2_data_storage_accessmode`](#db2_data_storage_accessmode) | No | `ReadWriteOnce` |
| [`db2_backup_storage_class`](#db2_backup_storage_class) | No | Cluster default (auto-detected) |
| [`db2_backup_storage_size`](#db2_backup_storage_size) | No | `50Gi` |
| [`db2_backup_storage_accessmode`](#db2_backup_storage_accessmode) | No | `ReadWriteMany` |
| [`db2_logs_storage_class`](#db2_logs_storage_class) | No | Cluster default (auto-detected) |
| [`db2_logs_storage_size`](#db2_logs_storage_size) | No | `30Gi` |
| [`db2_logs_storage_accessmode`](#db2_logs_storage_accessmode) | No | `ReadWriteOnce` |
| [`db2_temp_storage_class`](#db2_temp_storage_class) | No | Cluster default (auto-detected) |
| [`db2_temp_storage_size`](#db2_temp_storage_size) | No | `10Gi` |
| [`db2_temp_storage_accessmode`](#db2_temp_storage_accessmode) | No | `ReadWriteOnce` |
| [`db2_audit_logs_storage_class`](#db2_audit_logs_storage_class) | No | Cluster default (auto-detected) |
| [`db2_audit_logs_storage_size`](#db2_audit_logs_storage_size) | No | `30Gi` |
| [`db2_audit_logs_storage_accessmode`](#db2_audit_logs_storage_accessmode) | No | `ReadWriteOnce` |
| [`db2_archivelogs_storage_class`](#db2_archivelogs_storage_class) | No | Cluster default (auto-detected) |
| [`db2_archivelogs_storage_size`](#db2_archivelogs_storage_size) | No | `30Gi` |
| [`db2_archivelogs_storage_accessmode`](#db2_archivelogs_storage_accessmode) | No | Set by `db2u_kind` |
| [`db2_cpu_requests`](#db2_cpu_requests) | No | `4000m` |
| [`db2_cpu_limits`](#db2_cpu_limits) | No | `6000m` |
| [`db2_memory_requests`](#db2_memory_requests) | No | `8Gi` |
| [`db2_memory_limits`](#db2_memory_limits) | No | `16Gi` |
| [`db2_affinity_key`](#db2_affinity_key) | No | None |
| [`db2_affinity_value`](#db2_affinity_value) | No | None |
| [`db2_tolerate_key`](#db2_tolerate_key) | No | None |
| [`db2_tolerate_value`](#db2_tolerate_value) | No | None |
| [`db2_tolerate_effect`](#db2_tolerate_effect) | No | None |
| [`db2_database_db_config`](#db2_database_db_config) | No | Built-in defaults |
| [`db2_instance_dbm_config`](#db2_instance_dbm_config) | No | None |
| [`db2_instance_registry`](#db2_instance_registry) | No | Built-in defaults |
| [`db2_mln_count`](#db2_mln_count) | No | `1` |
| [`db2_num_pods`](#db2_num_pods) | No | `1` |
| [`db2_addons_audit_config`](#db2_addons_audit_config) | No | `""` |
| [`mas_instance_id`](#mas_instance_id) | Conditional | None |
| [`mas_config_dir`](#mas_config_dir) | No | None |
| [`mas_config_scope`](#mas_config_scope) | No | `system` |
| [`mas_workspace_id`](#mas_workspace_id) | No | None |
| [`mas_application_id`](#mas_application_id) | Conditional | None |
| [`mas_backup_dir`](#mas_backup_dir) | Conditional | None |
| [`db2_backup_version`](#db2_backup_version) | Conditional | Auto-generated (`YYYYMMDD-HHMMSS`) |
| [`override_storageclass`](#override_storageclass) | No | `false` |
| [`custom_storage_class_rwo`](#custom_storage_class_rwo) | No | None |
| [`custom_storage_class_rwx`](#custom_storage_class_rwx) | No | None |
| [`backup_type`](#backup_type) | No | `online` |
| [`backup_vendor`](#backup_vendor) | No | `disk` |
| [`backup_s3_endpoint`](#backup_s3_endpoint) | Conditional | None |
| [`backup_s3_bucket`](#backup_s3_bucket) | Conditional | None |
| [`backup_s3_access_key`](#backup_s3_access_key) | Conditional | None |
| [`backup_s3_secret_key`](#backup_s3_secret_key) | Conditional | None |
| [`backup_s3_alias`](#backup_s3_alias) | No | `S3DB2COS` |

Variables marked **Conditional** are only required in specific circumstances: `db2_version` (upgrade), `db2_license_file` and `db2_v12_upgrade` (upgrading from v11 to v12), `db2_ldap_password` (when `db2_ldap_username` is set), `db2_meta_storage_class` and `db2_data_storage_class` (when the cluster has no default storage classes), `mas_instance_id`, `mas_application_id`, `mas_backup_dir`, and `db2_backup_version` (backup and restore operations), and the `backup_s3_*` variables (when `backup_vendor` is `s3`).

### Installation and Upgrade

#### db2u_kind

Db2 deployment type — `db2ucluster` (deprecated Db2uCluster CR, for maintaining existing deployments only) or `db2uinstance` (current Db2uInstance CR, recommended for all new deployments). Both types use the same underlying configuration variables.

- **Optional**
- Environment Variable: `DB2U_KIND`
- Default: `db2ucluster`

The default of `db2ucluster` preserves backward compatibility with existing automation and scripts. Strict validation ensures `DB2U_KIND` matches the existing deployment type — the deployment type of an existing instance cannot be changed, and attempting to change it fails with a clear error message.

!!! warning
    Db2uCluster is deprecated. Use `db2uinstance` for all new deployments; existing Db2uCluster deployments continue to work but cannot be automatically converted — use the `db2u-migration` action to migrate them (see [Migrating from Db2uCluster to Db2uInstance](#migrating-from-db2ucluster-to-db2uinstance)).

#### ibm_common_services_namespace

OpenShift namespace where IBM Common Services is installed — leave as the default for standard installations, and set only when Common Services is installed in a non-standard namespace.

- **Optional**
- Environment Variable: `IBM_COMMON_SERVICES_NAMESPACE`
- Default: `ibm-common-services`

The role uses this namespace to locate the Common Services components shared by the Db2u operator; an incorrect namespace causes the role to fail when accessing them. Works with `db2_namespace` to manage operator and instance placement.

#### db2_action

Operation to perform on the Db2 database — one of `install`, `upgrade`, `backup`, `backup-database`, `restore`, `restore-database`, or `db2u-migration` (details below).

- **Optional**
- Environment Variable: `DB2_ACTION`
- Default: `install`

Valid actions:

- `install` (default) — creates a new Db2 operator and instance; when `db2_backup_version` is provided, installs from backup (instance + database)
- `upgrade` — upgrades ALL instances in `db2_namespace` to `db2_version`
- `backup` — backs up both the instance resources (secrets, certificates, Db2uCluster/Db2uInstance CR, ConfigMaps) and the database; enables full disaster recovery and install-from-backup, but is slower
- `backup-database` — backs up only the database data; faster, but restore requires an existing Db2 instance
- `restore` — creates a new Db2 operator and instance from the backup of the Db2 instance resources and restores the database data to the created instance
- `restore-database` — restores the database to an existing running Db2 instance (does not restore instance resources)
- `db2u-migration` — migrates an existing Db2uCluster to Db2uInstance using the `db2u_migrate` CLI tool (namespace-scoped, requires v12)

Related variables by action: `db2_version` is required for `upgrade` (and must match the operator channel); `db2_instance_name` is required for `db2u-migration` (which Db2uCluster to migrate); `db2_backup_version` is required for `restore`/`restore-database` and optional for backup (defaults to `YYYYMMDD-HHMMSS`); `override_storageclass` controls storage class handling during restore; `mas_instance_id` and `mas_config_dir` optionally update the MAS JdbcCfg during migration.

!!! warning
    The `upgrade` action upgrades **all** Db2 instances in `db2_namespace` — plan accordingly. The `db2u-migration` action requires the Db2uCluster to be running v12.x; the original Db2uCluster CR is not automatically deleted after migration (see the migration guide for optional cleanup steps).

#### db2_namespace

OpenShift namespace where the Db2u operator and Db2 instances will be deployed — use the default (`db2u`) for standard single-instance deployments, or a custom namespace (e.g. `db2u`, `db2-prod`, `mas-db2`) when organizing multiple Db2 deployments. Must match the existing namespace when upgrading Db2 instances.

- **Optional**
- Environment Variable: `DB2_NAMESPACE`
- Default: `db2u`

All Db2 resources (operator, instances, secrets, services) are created in this namespace. If the Db2 operator and instances already run in separate namespaces, the role migrates the Db2 **operators** (not the instances) from `ibm-common-services` to this namespace during a new install or upgrade. When `db2_action=upgrade`, all instances in this namespace are upgraded together.

#### db2_channel

Subscription channel for the Db2 Universal Operator, determining which operator version stream you receive and which Db2 engine versions are available — e.g. `v2.2`, `v3.0`, `v3.1`. Leave unset for new installations (the default channel is recommended); when upgrading, the channel must be compatible with `db2_version`.

- **Optional**
- Environment Variable: `DB2_CHANNEL`
- Default: Operator package default channel (automatically selected)

Channels typically correspond to major Db2 versions. Check the operator package for available channels and their supported versions; changing channels may require operator migration.

#### db2_instance_name

Unique name for the Db2 instance (the Db2uCluster/Db2uInstance resource) — a valid Kubernetes resource name, lowercase alphanumeric with hyphens (e.g. `db01`, `mas-db`, `manage-db`), unique within the namespace. Use a descriptive name indicating purpose (e.g. `maximo-db`, `iot-db`, `manage-db`).

- **Required**
- Environment Variable: `DB2_INSTANCE_NAME`
- Default: None

The name is embedded throughout the Db2 deployment — the CR name, service names (e.g. `{instance_name}-db2u-engn-svc`), pod names (e.g. `c-{instance_name}-db2u-0`), and secret names — and is used in the generated JdbcCfg when `mas_instance_id` is provided. It cannot easily be changed after creation. Also required for the `db2u-migration` action, to specify which Db2uCluster to migrate.

#### ibm_entitlement_key

IBM Container Library entitlement key for pulling Db2 container images from the IBM Container Registry — obtain it from the [IBM Container Library](https://myibm.ibm.com/products-services/containerlibrary) using your IBM ID.

- **Required**
- Environment Variable: `IBM_ENTITLEMENT_KEY`
- Default: None

Without a valid key, Db2 container images cannot be pulled and installation will fail; the key is stored in an image pull secret in the Db2 namespace. The same key is used across all IBM MAS components. Treat it as a credential — keep it secure and do not commit it to source control.

#### db2_dbname

Name of the database to create within the Db2 instance — a valid Db2 database name, uppercase alphanumeric up to 8 characters (e.g. `BLUDB`, `MAXDB`, `MASDB`).

- **Optional**
- Environment Variable: `DB2_DBNAME`
- Default: `BLUDB`

`BLUDB` is the standard database name for Db2 Warehouse and most MAS deployments; set a custom name only when organizational standards require it. The name is used in connection strings and the generated JdbcCfg — applications must use this exact name to connect.

#### db2_version

Db2 engine version to use for installation or upgrade — a valid Db2 engine version supported by the operator (e.g. `11.5.8.0`, `11.5.9.0`).

- **Required** when using `db2_action=upgrade` (specifies the target version)
- Environment Variable: `DB2_VERSION`
- Default: Latest version supported by the installed Db2 operator (auto-detected from the `db2u-release` configmap)

Leave unset for new installations to use the latest supported version. The version must be available in the operator's channel — when upgrading, ALL instances in `db2_namespace` are upgraded to this version. Supported versions are listed in the `db2u-release` configmap in the `ibm-common-services` namespace.

#### db2_license_file

Path to the Db2 Warehouse license file on the local filesystem — an absolute path to a valid license file in `.lic` format, e.g. `/path/to/db2wh.lic`.

- **Required** when upgrading from Db2 v11 to v12 (with `db2_v12_upgrade=true`)
- **Optional** for new Db2 installations (Db2 v12 uses a 30-day trial license when not provided)
- Environment Variable: `DB2_LICENSE_FILE`
- Default: None

IBM may refer to this file by different names — "Db2 Warehouse license", "Db2 activation key", `db2wh.lic`, or `db2ese.lic`; see [Upgrading Db2 from v11 to v12](#upgrading-db2-from-v11-to-v12) for an example of the expected file format. Must be combined with `db2_v12_upgrade=true` and a v12 channel (e.g. `v12.0.0-cn1`).

!!! warning
    Without a valid license, Db2 v12 operates under a 30-day trial license — when the trial expires the database becomes unavailable. This is especially critical for production systems.

#### db2_v12_upgrade

Explicit opt-in flag required to authorize a major version upgrade from Db2 v11 to v12 — a safety gate (`true`/`false`) preventing accidental major version upgrades, which are significant and irreversible operations requiring explicit user consent.

- **Required** when upgrading from Db2 v11 to v12
- Environment Variable: `DB2_V12_UPGRADE`
- Default: `false`

Must be combined with `db2_license_file` and a v12 `db2_channel` (e.g. `v12.0.0-cn1`). The upgrade fails if the license file is not provided — this is intentional, to prevent a silent downgrade from a full production license to a 30-day trial license.

### Instance Configuration

#### db2_type

Db2 instance type, optimized for specific workload patterns — `db2wh` (data warehouse/analytical queries, recommended for MAS Manage) or `db2oltp` (online transaction processing with high concurrency).

- **Optional**
- Environment Variable: `DB2_TYPE`
- Default: `db2wh`

Affects resource allocation and database tuning. Align with `db2_workload` and `db2_table_org`.

#### db2_timezone

Server timezone for the Db2 instance, used for timestamp operations and scheduling — a valid timezone code (e.g. `GMT`, `EST`, `PST`, `CET`, `UTC`).

- **Optional**
- Environment Variable: `DB2_TIMEZONE`
- Default: None (the Db2 engine defaults to UTC)

Set to the local timezone when all users are in the same timezone. Mismatched timezones between Db2 and applications can cause data inconsistencies.

!!! important
    If using this Db2 instance with MAS Manage, you must also set `MAS_APP_SETTINGS_SERVER_TIMEZONE` to the same value to ensure consistent timestamp handling.

#### db2_4k_device_support

Controls support for storage devices with 4K sector sizes — `ON` (required for most modern storage systems, including OCS and Portworx) or `OFF` (legacy storage with 512-byte sectors only).

- **Optional**
- Environment Variable: `DB2_4K_DEVICE_SUPPORT`
- Default: `ON`

Check your storage specifications if unsure; keep `ON` unless you have specific legacy storage requirements. Works with the storage class configuration to ensure compatibility.

#### db2_workload

Workload profile for Db2 instance optimization — `ANALYTICS` (balanced optimization for mixed analytical workloads, suitable for most MAS deployments) or `PUREDATA_OLAP` (pure data warehouse/OLAP query patterns).

- **Optional**
- Environment Variable: `DB2_WORKLOAD`
- Default: `ANALYTICS`

Affects memory allocation, query optimization, and other performance parameters. Align with `db2_type` and `db2_table_org`; change only if you have specific OLAP requirements.

#### db2_table_org

Default table organization for database tables — `ROW` (row-by-row storage, better for OLTP, updates, and mixed workloads; required by MAS Manage) or `COLUMN` (column-by-column storage, better for analytical queries and aggregations).

- **Optional**
- Environment Variable: `DB2_TABLE_ORG`
- Default: `ROW`

This sets the default — individual tables can override it. Align with `db2_type` and `db2_workload`; use `COLUMN` only for dedicated analytical/reporting databases.

### LDAP User Management

#### db2_ldap_username

Custom LDAP username for Db2 authentication, configured in Db2's local LDAP registry and used in the generated MAS JdbcCfg — leave unset to use the default `db2inst1` user.

- **Optional**
- Environment Variable: `DB2_LDAP_USERNAME`
- Default: None (uses the default `db2inst1` user)

Set when you need a custom database user for MAS connections or when organizational policies require specific usernames. When set, the user is created in Db2's LDAP registry with the necessary database permissions, and `db2_ldap_password` must also be provided.

#### db2_ldap_password

Password for the LDAP user specified in `db2_ldap_username` — a strong password string meeting security requirements.

- **Required** when `db2_ldap_username` is set for initial user creation
- Environment Variable: `DB2_LDAP_PASSWORD`
- Default: None

The password is stored in Db2's LDAP registry and included in the generated JdbcCfg for MAS. It is required at creation time because `db2_rotate_password` defaults to `false` and only works with existing users — it cannot create new users. Keep the password secure and do not commit it to source control.

#### db2_rotate_password

Rotate the password of an **existing** Db2 LDAP user (`true`/`false`) by generating a new strong random password and updating both Db2's LDAP registry and the MAS JdbcCfg.

- **Optional**
- Environment Variable: `DB2_LDAP_ROTATE_PASSWORD`
- Default: `False`

!!! warning
    This feature is **only for existing users** — it fails if the user does not already exist in Db2's LDAP registry, and cannot be used to create new users.

Typical workflow — first deployment creates the user with a known password (`db2_ldap_username` + `db2_ldap_password`, `db2_rotate_password: false`); subsequent deployments set only `db2_ldap_username` and `db2_rotate_password: true` to rotate to an auto-generated password (`db2_ldap_password` is not needed during rotation). The auto-generated password is stored securely in Kubernetes secrets and MAS configuration; `mas_instance_id` is required to update the MAS JDBC configuration.

### Storage Variables

We recommend reviewing the Db2 documentation about the certified storage options for Db2 on Red Hat OpenShift. Please ensure your storage class meets the specified deployment requirements for [Db2uInstance](https://www.ibm.com/docs/en/db2/11.5.x?topic=resource-deploying-db2-using-db2uinstance-custom) and for [Db2uCluster](https://www.ibm.com/docs/en/db2/11.5.x?topic=resource-deploying-db2-using-db2ucluster-custom).

#### db2_meta_storage_class

Storage class for the Db2 metadata persistent volume — must support ReadWriteMany (RWX) access mode for shared access across Db2 pods; typically file-based storage (e.g. `ibmc-file-gold`, `ocs-storagecluster-cephfs`).

- **Required** when the cluster has no default RWX storage class (auto-detection fails and the role exits with an error)
- Environment Variable: `DB2_META_STORAGE_CLASS`
- Default: Cluster default RWX storage class (auto-detected)

Metadata storage (system catalogs, configuration files, and other operational data) is critical for Db2 operation — a storage class that does not support RWX will cause the deployment to fail. See [Db2 certified storage options](https://www.ibm.com/docs/en/db2/11.5?topic=storage-certified-options) for supported storage.

#### db2_meta_storage_size

Size of the metadata persistent volume, in Kubernetes storage size format (e.g. `10Gi`, `20Gi`, `50Gi`).

- **Optional**
- Environment Variable: `DB2_META_STORAGE_SIZE`
- Default: `10Gi`

`10Gi` is sufficient for most deployments; increase for large-scale deployments with many databases or complex configurations. Metadata storage requirements are typically much smaller than data storage — monitor usage and adjust if the metadata volume fills up.

#### db2_meta_storage_accessmode

Access mode for the metadata storage volume — `ReadWriteMany` (RWX), required so Db2 metadata is accessible from multiple pods.

- **Optional**
- Environment Variable: `DB2_META_STORAGE_ACCESSMODE`
- Default: `ReadWriteMany`

Do not change from the default: Db2 requires RWX access mode for metadata storage, and `db2_meta_storage_class` must support it.

#### db2_data_storage_class

Storage class for the Db2 user data persistent volume (database tables, indexes, and all user data) — must support ReadWriteOnce (RWO) access mode; typically high-performance block storage (e.g. `ibmc-block-gold`, `ocs-storagecluster-ceph-rbd`).

- **Required** when the cluster has no default RWO storage class (auto-detection fails and the role exits with an error)
- Environment Variable: `DB2_DATA_STORAGE_CLASS`
- Default: Cluster default RWO storage class (auto-detected)

Choose high-performance storage for production workloads — a storage class that does not support RWO will cause the deployment to fail. See [Db2 certified storage options](https://www.ibm.com/docs/en/db2/11.5?topic=storage-certified-options) for supported storage.

#### db2_data_storage_size

Size of the user data persistent volume, in Kubernetes storage size format (e.g. `50Gi`, `100Gi`, `500Gi`, `1Ti`).

- **Optional**
- Environment Variable: `DB2_DATA_STORAGE_SIZE`
- Default: `50Gi`

`50Gi` is suitable for development/test environments and small deployments only — production MAS Manage deployments typically require 500Gi or more. Insufficient data storage causes database operations to fail when the volume fills up; size for expected data volume plus growth, monitor usage, and expand as needed.

#### db2_data_storage_accessmode

Access mode for the user data storage volume — `ReadWriteOnce` (RWO), the correct mode for Db2 data storage which is accessed by a single pod at a time.

- **Optional**
- Environment Variable: `DB2_DATA_STORAGE_ACCESSMODE`
- Default: `ReadWriteOnce`

Do not change from the default: Db2 data storage is designed for RWO access mode, and `db2_data_storage_class` must support it.

#### db2_backup_storage_class

Storage class for the Db2 backup persistent volume — must support ReadWriteMany (RWX) access mode for shared access during backup operations; typically file-based storage. Set to `None` to drop the backup storage from the Db2uCluster CR.

- **Optional**
- Environment Variable: `DB2_BACKUP_STORAGE_CLASS`
- Default: Cluster default RWX storage class (auto-detected)

!!! warning
    Setting this to `None` disables backup capability — only do this for non-production environments. Production systems should always have backup storage configured.

#### db2_backup_storage_size

Size of the backup persistent volume, in Kubernetes storage size format (e.g. `50Gi`, `100Gi`, `500Gi`, `1Ti`).

- **Optional**
- Environment Variable: `DB2_BACKUP_STORAGE_SIZE`
- Default: `50Gi`

The volume stores database backups for disaster recovery and point-in-time recovery. Insufficient backup storage causes backup operations to fail — a common practice is to size it at 2-3x the data storage size, to accommodate multiple full backups plus transaction logs per your retention policy.

#### db2_backup_storage_accessmode

Access mode for the backup storage volume — `ReadWriteMany` (RWX), required for Db2 backup operations to be accessible from multiple pods.

- **Optional**
- Environment Variable: `DB2_BACKUP_STORAGE_ACCESSMODE`
- Default: `ReadWriteMany`

Do not change from the default: Db2 backup operations require RWX access mode, and `db2_backup_storage_class` must support it.

#### db2_logs_storage_class

Storage class used for transaction logs — must support ReadWriteOnce (RWO) access mode. Set to `None` to drop the logs storage from the Db2uCluster CR.

- **Optional**
- Environment Variable: `DB2_LOGS_STORAGE_CLASS`
- Default: Cluster default RWO storage class (auto-detected)

#### db2_logs_storage_size

Size of the transaction logs persistent volume.

- **Optional**
- Environment Variable: `DB2_LOGS_STORAGE_SIZE`
- Default: `30Gi`

#### db2_logs_storage_accessmode

The access mode for the transaction logs storage — must support ReadWriteOnce (RWO) access mode.

- **Optional**
- Environment Variable: `DB2_LOGS_STORAGE_ACCESSMODE`
- Default: `ReadWriteOnce`

#### db2_temp_storage_class

Storage class used for temporary data — must support ReadWriteOnce (RWO) access mode. Set to `None` to drop the temp storage from the Db2uCluster CR.

- **Optional**
- Environment Variable: `DB2_TEMP_STORAGE_CLASS`
- Default: Cluster default RWO storage class (auto-detected)

#### db2_temp_storage_size

Size of the temporary persistent volume.

- **Optional**
- Environment Variable: `DB2_TEMP_STORAGE_SIZE`
- Default: `10Gi`

#### db2_temp_storage_accessmode

The access mode for the temporary storage — must support ReadWriteOnce (RWO) access mode.

- **Optional**
- Environment Variable: `DB2_TEMP_STORAGE_ACCESSMODE`
- Default: `ReadWriteOnce`

#### db2_audit_logs_storage_class

Storage class used for audit logs — must support ReadWriteOnce (RWO) access mode. Set to `None` to drop the audit logs storage from the Db2uInstance CR.

- **Optional**
- Environment Variable: `DB2_AUDIT_LOGS_STORAGE_CLASS`
- Default: Cluster default RWO storage class (auto-detected)

#### db2_audit_logs_storage_size

Size of the audit logs persistent volume.

- **Optional**
- Environment Variable: `DB2_AUDIT_LOGS_STORAGE_SIZE`
- Default: `30Gi`

#### db2_audit_logs_storage_accessmode

The access mode for the audit logs storage — must support ReadWriteOnce (RWO) access mode.

- **Optional**
- Environment Variable: `DB2_AUDIT_LOGS_STORAGE_ACCESSMODE`
- Default: `ReadWriteOnce`

#### db2_archivelogs_storage_class

Storage class used for archive logs — must support ReadWriteMany (RWX) access mode for `Db2uInstance` and ReadWriteOnce (RWO) access mode for `Db2uCluster`. Set to `None` to drop the archivelogs storage from the Db2uInstance CR.

- **Optional**
- Environment Variable: `DB2_ARCHIVELOGS_STORAGE_CLASS`
- Default: Cluster default storage class (auto-detected; RWX for `Db2uInstance`, RWO for `Db2uCluster`)

#### db2_archivelogs_storage_size

Size of the archive logs persistent volume.

- **Optional**
- Environment Variable: `DB2_ARCHIVELOGS_STORAGE_SIZE`
- Default: `30Gi`

#### db2_archivelogs_storage_accessmode

The access mode for the storage — must support ReadWriteMany (RWX) access mode for `Db2uInstance` and ReadWriteOnce (RWO) access mode for `Db2uCluster`.

- **Optional**
- Environment Variable: `DB2_ARCHIVELOGS_STORAGE_ACCESSMODE`
- Default: Dynamically set according to the kind of Db2 (`Db2uInstance` or `Db2uCluster`)

### Resource Requests

These variables allow you to customize the resources available to the Db2 pod in your cluster. In most circumstances you will want to set these properties because it is impossible for us to provide a default value that will be appropriate for all users. We have set defaults that are suitable for deploying Db2 onto a dedicated worker node with 4 CPU and 16GB memory.

!!! tip
    Note that you must take into account the system overhead on any given node when setting these parameters, if you set the requests equal to the number of CPU or amount of memory on your node then the scheduler will not be able to schedule the Db2 pod because not 100% of the worker nodes' resource will be available to pod on that node, even if there's only a single pod on it.

    Db2 is sensitive to both CPU and memory issues, particularly memory, we recommend setting requests and limits to the same values, ensuring the scheduler always reserves the resources that Db2 expects to be available to it.

#### db2_cpu_requests

Define the Kubernetes CPU request for the Db2 pod.

- **Optional**
- Environment Variable: `DB2_CPU_REQUESTS`
- Default: `4000m`

#### db2_cpu_limits

Define the Kubernetes CPU limit for the Db2 pod.

- **Optional**
- Environment Variable: `DB2_CPU_LIMITS`
- Default: `6000m`

#### db2_memory_requests

Define the Kubernetes memory request for the Db2 pod.

- **Optional**
- Environment Variable: `DB2_MEMORY_REQUESTS`
- Default: `8Gi`

#### db2_memory_limits

Define the Kubernetes memory limit for the Db2 pod.

- **Optional**
- Environment Variable: `DB2_MEMORY_LIMITS`
- Default: `16Gi`

### Node Label Affinity

Specify both `db2_affinity_key` and `db2_affinity_value` to configure `requiredDuringSchedulingIgnoredDuringExecution` affinity with appropriately labelled nodes.

#### db2_affinity_key

Specify the key of a node label to declare affinity with.

- **Optional**
- Environment Variable: `DB2_AFFINITY_KEY`
- Default: None

#### db2_affinity_value

Specify the value of a node label to declare affinity with.

- **Optional**
- Environment Variable: `DB2_AFFINITY_VALUE`
- Default: None

### Node Taint Toleration

Specify `db2_tolerate_key`, `db2_tolerate_value`, and `db2_tolerate_effect` to configure a toleration policy to allow the Db2 instance to be scheduled on nodes with the specified taint.

#### db2_tolerate_key

Specify the key of the taint that is to be tolerated.

- **Optional**
- Environment Variable: `DB2_TOLERATE_KEY`
- Default: None

#### db2_tolerate_value

Specify the value of the taint that is to be tolerated.

- **Optional**
- Environment Variable: `DB2_TOLERATE_VALUE`
- Default: None

#### db2_tolerate_effect

Specify the type of taint effect that will be tolerated (`NoSchedule`, `PreferNoSchedule`, or `NoExecute`).

- **Optional**
- Environment Variable: `DB2_TOLERATE_EFFECT`
- Default: None

### Database Configuration Overrides

The following variables overwrite the Db2uCluster default properties for the Db2 configuration sections:

- `spec.environment.database.dbConfig`
- `spec.environment.instance.dbmConfig`
- `spec.environment.instance.registry`

#### db2_database_db_config

Overwrites the Db2uCluster database configuration settings under the `spec.environment.database.dbConfig` section.

- **Optional**
- Environment Variable: `DB2_DATABASE_DB_CONFIG`
- Default: Built-in defaults (`db2_default_config.dbConfig`)

The built-in defaults set `APPLHEAPSZ: 8192 AUTOMATIC` and circular logging (`LOGARCHMETH1: OFF`, `LOGARCHMETH2: OFF`) — see the `backup_type` variable for how this affects online versus offline backups.

#### db2_instance_dbm_config

Overwrites the Db2uCluster instance database manager configuration settings under the `spec.environment.instance.dbmConfig` section.

- **Optional**
- Environment Variable: `DB2_INSTANCE_DBM_CONFIG`
- Default: None (Db2u built-in defaults are used)

!!! important
    Do not set [instance_memory](https://www.ibm.com/docs/en/db2/11.5?topic=parameters-instance-memory-instance-memory). The Db2 engine does not know Db2 is running inside a container, setting `dbmConfig.INSTANCE_MEMORY: automatic` will cause it to read the cgroups of the node and potentially go beyond the pod memory limit. Db2U has logic built in to use a normalized percentage that takes into account the memory limit and free memory of the node.

#### db2_instance_registry

Overwrites the Db2uCluster instance registry settings under the `spec.environment.instance.registry` section. You can define parameters to be included in this section using semicolon separated values.

- **Optional**
- Environment Variable: `DB2_INSTANCE_REGISTRY`
- Default: Built-in defaults (`db2_default_config.registry`)

The built-in defaults set `DB2AUTH: OSAUTHDB,ALLOW_LOCAL_FALLBACK,PLUGIN_AUTO_RELOAD`, `DB2_FMP_RUN_AS_CONNECTED_USER: NO`, and `DB2_4K_DEVICE_SUPPORT`/`DB2_WORKLOAD` (derived from the `db2_4k_device_support` and `db2_workload` variables).

### Db2 MPP Configuration

!!! warning
    Do not use these variables if you intend to use the Db2 instance with IBM Maximo Application Suite; no MAS application supports Db2 MPP

#### db2_mln_count

The number of logical nodes (i.e. database partitions) to create. Note: ensure that the application using this Db2 can support Db2 MPP (which is created when `DB2_MLN_COUNT` is greater than 1).

- **Optional**
- Environment Variable: `DB2_MLN_COUNT`
- Default: `1`

#### db2_num_pods

The number of Db2 pods to create in the instance. Note that `db2_num_pods` must be less than or equal to `db2_mln_count`. A single db2u pod can contain multiple logical nodes, so avoid specifying a large number for `db2_mln_count` while specifying a small number for `db2_num_pods`; if in doubt, make `db2_mln_count = db2_num_pods`. For more information refer to the [Db2 documentation](https://www.ibm.com/docs/en/db2-warehouse?topic=SSCJDQ/com.ibm.swg.im.dashdb.ucontainer.doc/doc/db2w-mempernode-new.html).

- **Optional**
- Environment Variable: `DB2_NUM_PODS`
- Default: `1`

### Db2 Add-ons

#### db2_addons_audit_config

Audit add-on configuration for the Db2 instance, provided as a YAML string. When set, the content is injected into the `spec.addOns.audit` section of the Db2uInstance custom resource, enabling configuration of the Db2 audit facility add-on.

- **Optional**
- Environment Variable: `DB2_ADDONS_AUDIT_CONFIG`
- Default: `""`

### MAS Configuration

When both `mas_instance_id` and `mas_config_dir` are provided the role generates the JdbcCfg YAML that can be used to configure MAS to connect to this database. It does not apply the YAML to the cluster but does provide you with the files to apply if needed.

#### mas_instance_id

MAS instance identifier (e.g. `inst1`, `masinst1`) — providing this together with `mas_config_dir` instructs the role to generate a JdbcCfg template for configuring MAS to connect to this database.

- **Optional** for JdbcCfg generation; **Required** for backup and restore operations (identifies the MAS instance associated with the Db2 backup, used for organizing backups and ensuring restore operations target the correct instance)
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

Also used by `db2_rotate_password` to update the MAS JDBC configuration, and optionally by the `db2u-migration` action to update the MAS JdbcCfg after migration.

#### mas_config_dir

Directory where the generated JdbcCfg YAML files are written — providing this together with `mas_instance_id` instructs the role to generate the JdbcCfg template for configuring MAS to connect to this database.

- **Optional**
- Environment Variable: `MAS_CONFIG_DIR`
- Default: None

The role does not apply the generated YAML to the cluster; it provides the files for you to apply if needed.

#### mas_config_scope

Scope for the generated MAS configuration — supported values are `system`, `ws`, `app`, or `wsapp`. This is only used when both `mas_config_dir` and `mas_instance_id` are set.

- **Optional**
- Environment Variable: `MAS_CONFIG_SCOPE`
- Default: `system`

#### mas_workspace_id

Workspace identifier — only used when both `mas_config_dir` and `mas_instance_id` are set, and `mas_config_scope` is set to either `ws` or `wsapp`.

- **Optional**
- Environment Variable: `MAS_WORKSPACE_ID`
- Default: None

#### mas_application_id

MAS application identifier (e.g. `manage`, `iot`, `monitor`) — used when `mas_config_scope` is set to either `app` or `wsapp`, and required for backup and restore operations (identifies the MAS application that uses this Db2 database, used for organizing backups and database-specific operations).

- **Optional** for JdbcCfg generation; **Required** for backup and restore operations
- Environment Variable: `MAS_APP_ID`
- Default: None

### Backup and Restore Variables

`mas_instance_id` and `mas_application_id` (see [MAS Configuration](#mas-configuration)) are also required for backup and restore operations.

#### mas_backup_dir

Local directory path where backups will be stored or restored from (e.g. `/tmp/mas_backups`, `/backup/db2`) — must be accessible from the system running the Ansible playbook and have sufficient disk space for database backups.

- **Required** for backup and restore operations
- Environment Variable: `MAS_BACKUP_DIR`
- Default: None

This directory serves as the staging area for all backup and restore operations. Backup files and metadata are stored in subdirectories structured `<mas_backup_dir>/backup-<version>-db2u-<app>/`. When `backup_vendor` is `s3`, database backups go to S3 but instance resources still use this directory.

#### db2_backup_version

The backup version timestamp identifier for backup and restore operations, in `YYYYMMDD-HHMMSS` format (e.g. `20251212-021316` for December 12, 2025 at 02:13:16).

- **Required** for the `restore` and `restore-database` actions, and when installing Db2 from an existing backup
- **Auto-generated** for backup operations
- Environment Variable: `DB2_BACKUP_VERSION`
- Default: Auto-generated in format `YYYYMMDD-HHMMSS`

Uniquely identifies a specific backup version, allowing multiple backups to coexist and enabling point-in-time restore operations. Determines the backup directory name (`backup-<version>-db2u-<app>`), is used to locate backup files during restore, and is recorded in the backup metadata file for verification.

#### override_storageclass

Controls whether to override storage classes during Db2 installation from backup (`true`/`false`). Only used in Db2 instance restore.

- **Optional**
- Environment Variable: `OVERRIDE_STORAGECLASS`
- Default: `false`

When `true`, uses `custom_storage_class_rwo` and `custom_storage_class_rwx` if set (otherwise cluster default storage classes) instead of the backup metadata values — useful when restoring to a different cluster or when the original storage classes are not available in the target cluster. When `false`, uses the storage classes from the backup metadata (original instance configuration).

#### custom_storage_class_rwo

Custom ReadWriteOnce (RWO) storage class for Db2 restore operations — a valid storage class name available in the target cluster, e.g. `ocs-storagecluster-ceph-rbd`.

- **Optional**
- Environment Variable: `CUSTOM_STORAGE_CLASS_RWO`
- Default: None

When set (with `override_storageclass: true`), provides a single storage class override for all RWO PVCs, simplifying configuration when all RWO volumes can use the same storage class. Applies to data, logs, temp, archivelogs, and audit_logs storage; specific Db2 storage class variables take precedence when also set.

#### custom_storage_class_rwx

Custom ReadWriteMany (RWX) storage class for Db2 restore operations — a valid storage class name available in the target cluster, e.g. `ocs-storagecluster-cephfs`.

- **Optional**
- Environment Variable: `CUSTOM_STORAGE_CLASS_RWX`
- Default: None

When set (with `override_storageclass: true`), provides a single storage class override for all RWX PVCs. Applies to meta and backup storage; specific Db2 storage class variables take precedence when also set.

#### backup_type

Type of backup operation to perform on the Db2 database — `online` (database remains available during backup; recommended for production systems requiring high availability) or `offline` (database is unavailable during backup; faster completion and works with circular logging).

- **Optional**
- Environment Variable: `DB2_BACKUP_TYPE`
- Default: `online`

!!! important
    If your Db2 instance has circular logging enabled (`LOGARCHMETH1: OFF` and/or `LOGARCHMETH2: OFF` — the default configuration), you can only use the `offline` backup type. If archive logging is enabled, you can use either type. Check the `LOGARCHMETH1`/`LOGARCHMETH2` settings in `db2_database_db_config` to determine whether online backup is supported.

#### backup_vendor

Storage backend for database backup files only — `disk` (backups stored locally and copied to `mas_backup_dir`) or `s3` (backups sent directly to an S3-compatible bucket for cloud-based backups, long-term retention, or disaster recovery).

- **Optional**
- Environment Variable: `BACKUP_VENDOR`
- Default: `disk`

Instance resources (secrets, certificates, CRs) are always stored locally in `mas_backup_dir`, regardless of this setting — only database backup files go to S3. When set to `s3`, requires `backup_s3_endpoint`, `backup_s3_bucket`, `backup_s3_access_key`, and `backup_s3_secret_key`.

#### backup_s3_endpoint

S3-compatible object storage endpoint URL — an HTTPS URL (e.g. `https://s3.us-east.cloud-object-storage.appdomain.cloud`, `https://s3.amazonaws.com`) that must be accessible from the Db2 pod.

- **Required** when `backup_vendor` is `s3`
- Environment Variable: `BACKUP_S3_ENDPOINT`
- Default: None

Supports AWS S3, IBM Cloud Object Storage, MinIO, and other S3-compatible services. Db2 connects to this endpoint to upload/download backup files, so an incorrect endpoint will cause backup/restore failures.

#### backup_s3_bucket

S3 bucket name for storing database backups — a valid S3 bucket name (e.g. `mas-db2-backups`). The bucket must exist before running the backup, and the credentials must have read/write permissions on it.

- **Required** when `backup_vendor` is `s3`
- Environment Variable: `BACKUP_S3_BUCKET`
- Default: None

Backup files are stored in this bucket under path `<backup_version>/`.

#### backup_s3_access_key

S3 access key ID for authentication, used together with `backup_s3_secret_key` — must have read/write permissions to `backup_s3_bucket`.

- **Required** when `backup_vendor` is `s3`
- Environment Variable: `BACKUP_S3_ACCESS_KEY`
- Default: None

Invalid credentials cause backup/restore to fail with authentication errors. Store securely using Ansible Vault or environment variables — never commit to version control.

#### backup_s3_secret_key

S3 secret access key for authentication, used together with `backup_s3_access_key` — must correspond to the access key ID.

- **Required** when `backup_vendor` is `s3`
- Environment Variable: `BACKUP_S3_SECRET_KEY`
- Default: None

Store securely using Ansible Vault or environment variables — never commit to version control.

#### backup_s3_alias

Db2 storage access alias name for the S3 configuration — an internal Db2 identifier for the S3 connection (alphanumeric, no spaces).

- **Optional**
- Environment Variable: `BACKUP_S3_ALIAS`
- Default: `S3DB2COS`

Only used when `backup_vendor` is `s3`. Usually leave as the default; change only if you need to match existing Db2 storage access configurations — changing this is rarely necessary.

## Migrating from Db2uCluster to Db2uInstance
The `db2u-migration` action enables migration of existing Db2uCluster deployments to the current Db2uInstance resource type. This migration is necessary as Db2uCluster is deprecated and will reach end-of-life in future releases.

### Migration Requirements
- **Version**: Db2uCluster must be running v12.x (migration will fail for v11 or earlier)
- **CLI Tool**: The `db2u_migrate` command-line tool must be available on the machine running the Ansible role
- **Namespace**: Migration is namespace-scoped; specify the namespace containing the Db2uCluster
- **No Conflicts**: No Db2uInstance with the same name should exist in the namespace

### Migration Behavior
- **Non-destructive**: The original Db2uCluster CR remains after migration and is not automatically deleted
- **Data Preservation**: Database data and configuration are preserved during migration
- **Service Continuity**: The migration creates a new Db2uInstance that maintains connectivity to the existing database
- **JdbcCfg Update**: Optionally updates MAS JdbcCfg if `mas_instance_id` and `mas_config_dir` are provided

### Migration Process
The migration action performs the following steps:

1. **Validation**:
   - Verifies namespace exists
   - Confirms Db2uCluster exists and is v12.x
   - Checks for Db2uInstance naming conflicts

2. **Execution**:
   - Runs `db2u_migrate --namespace <namespace> --name <name>`
   - Monitors command output and handles errors

3. **Verification**:
   - Waits for Db2uInstance to reach Ready state
   - Waits for Db2uEngine to reach Ready state
   - Optionally updates MAS JdbcCfg

4. **Post-Migration**:
   - Displays success status
   - Reminds user that Db2uCluster still exists
   - Provides guidance for optional cleanup

### Usage Example

**Basic Migration**
```bash
export DB2_ACTION=db2u-migration
export DB2_NAMESPACE=db2u
export DB2_INSTANCE_NAME=db2u-db01

ansible-playbook ibm.mas_devops.run_role
```

**Migration with MAS JdbcCfg Update**
```bash
export DB2_ACTION=db2u-migration
export DB2_NAMESPACE=db2u
export DB2_INSTANCE_NAME=db2u-manage
export MAS_INSTANCE_ID=inst1
export MAS_CONFIG_DIR=/tmp/masconfig

ansible-playbook ibm.mas_devops.run_role
```

### Post-Migration Steps

**Verify Migration Success**
```bash
# Check Db2uInstance status
oc get db2uinstance -n db2u

# Check Db2uEngine status
oc get db2uengine -n db2u

# Verify database connectivity
oc exec -n db2u c-db2u-db01-db2u-0 -- su - db2inst1 -c "db2 connect to BLUDB"
```

**Optional: Clean Up Db2uCluster**
After verifying the migration succeeded and the Db2uInstance is functioning correctly, you may optionally delete the original Db2uCluster:

```bash
# Delete the Db2uCluster CR (optional)
oc delete db2ucluster db2u-db01 -n db2u
```

**Note**: Only delete the Db2uCluster after thoroughly verifying the migrated Db2uInstance is working correctly.

### Troubleshooting Migration

**Migration Fails: Version Check**
```text
Error: Migration requires Db2uCluster to be v12.x
Current version: 11.5.8.0
```

**Resolution**: Upgrade your Db2uCluster to v12 before attempting migration:
```bash
export DB2_ACTION=upgrade
export DB2_VERSION=12.0.0.0
export DB2_CHANNEL=v12.0.0-cn1
ansible-playbook ibm.mas_devops.run_role
```

**Migration Fails: Db2uInstance Already Exists**
```text
Error: Db2uInstance 'db2u-db01' already exists in namespace 'db2u'
```

**Resolution**: Either delete the existing Db2uInstance or choose a different name:
```bash
# Option 1: Delete existing instance
oc delete db2uinstance db2u-db01 -n db2u

# Option 2: Use different name
export DB2_INSTANCE_NAME=db2u-db01-migrated
```

**Migration Fails: db2u_migrate Command Not Found**
```text
Error: db2u_migrate: command not found
```

**Resolution**: Install the `db2u_migrate` CLI tool on the machine running the Ansible role. Contact IBM support or refer to Db2 operator documentation for installation instructions.

## Example Usage - Backup and Restore

### Backup Db2 Database to Disk
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_application_id: manage
    mas_backup_dir: /tmp/masbr
    db2_action: backup-database
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
    mas_application_id: manage
    mas_backup_dir: /tmp/masbr
    db2_action: backup-database
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
    mas_application_id: manage
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
    db2_action: restore-database
    mas_instance_id: masinst1
    mas_application_id: manage
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
    db2_action: restore-database
    mas_instance_id: masinst1
    mas_application_id: manage
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
    mas_application_id: manage
    db2_backup_version: 20251212-021316
    mas_backup_dir: /tmp/masbr
    backup_vendor: disk
  roles:
    - ibm.mas_devops.db2
```

### Restore Db2 from Backup (Instance + Database) w/ storage class override using custom storage classes
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    db2_action: restore
    mas_instance_id: masinst1
    mas_application_id: manage
    db2_backup_version: 20251212-021316
    mas_backup_dir: /tmp/masbr
    backup_vendor: disk
    override_storageclass: true
    custom_storage_class_rwo: ocs-storagecluster-ceph-rbd  # For data, logs, temp, archivelogs, audit_logs
    custom_storage_class_rwx: ocs-storagecluster-cephfs    # For meta, backup
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
    mas_application_id: manage
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
```text
/tmp/masbr/
└── backup-<YYYYMMDD-HHMMSS>-db2u-<app_id>/
    ├── data/
    │   ├── db2-<app_id>-BLUDB-backup-<YYYYMMDD-HHMMSS>.tar.gz
    │   └── db2-backup-info.yaml
    └── resources/
        ├── db2uclusters/
        ├── secrets/
        ├── certificates/
        └── issuers/
        └── {kind}s/
```

### Database Backup Metadata (db2-backup-info.yaml)
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
If your Db2 instance has circular logging enabled (i.e. `LOGARCHMETH1: OFF` and/or `LOGARCHMETH2: OFF`), you can only use the `offline` backup type.
If your Db2 instance has circular logging disabled, you can use either the `online` or `offline` backup type.
If you are unsure, you can use the default `online` backup type.

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

## Backup and Restore Troubleshooting

### Backup Failures

- Check Db2 pod logs: `oc logs -n <namespace> <db2-pod-name> -c db2u`
- Review backup script logs in the pod: `/tmp/db2_backup.log`
- Verify S3 credentials and connectivity (for S3 backups)
- Ensure sufficient storage space in the backup PVC(/mnt/backup)

**Issue: Backup fails with "insufficient storage space"**
```text
Error: SQL2062N  An error occurred while accessing media "backup_path"
```
**Solution:**

- Check available disk space on the Db2 pod: `oc exec -n <namespace> <db2-pod> -- df -h`
- Verify backup storage PVC has sufficient capacity
- For S3 backups, ensure bucket has adequate space and proper permissions
- Consider using compression or incremental backups to reduce storage requirements

**Issue: Backup fails with "database is in use"**
```text
Error: SQL1035N  The database is currently in use. SQLSTATE=57019
```
**Solution:**

- For offline backups, ensure all applications are disconnected
- Use online backup instead: `export DB2_BACKUP_TYPE=online`
- Check active connections: `oc exec -n <namespace> <db2-pod> -- su - db2inst1 -c "db2 list applications"`
- Force disconnect if necessary: `db2 force applications all`

**Issue: S3 backup fails with authentication errors**
```text
Error: Unable to authenticate with S3 endpoint
```
**Solution:**

- Verify S3 credentials are correct: `BACKUP_S3_ACCESS_KEY` and `BACKUP_S3_SECRET_KEY`
- Test S3 connectivity from the Db2 pod
- Ensure S3 endpoint URL is correct and accessible
- Check firewall rules and network policies allow S3 access
- Verify bucket exists and credentials have write permissions

**Issue: Backup script execution timeout**
```text
Error: Backup operation timed out after 3600 seconds
```
**Solution:**

- Large databases may require extended timeout periods
- Monitor backup progress: `oc logs -n <namespace> <db2-pod> -f`
- Check Db2 performance and resource utilization
- Consider scheduling backups during low-usage periods
- For very large databases, use incremental backups

### Restore Failures

- Verify backup version exists and is complete
- Check Db2 version compatibility
- Review restore script logs: `/tmp/db2_restore_disk.log` or `/tmp/db2_restore_s3.log`
- Ensure the Db2 instance is running and healthy before database restore
- For S3 restores, verify S3 connectivity and credentials

**Issue: Restore fails with version mismatch**
```text
Error: DB2 version mismatch. Backup version: 11.5.8.0, Target version: 11.5.9.0
```
**Solution:**

- Ensure target Db2 version matches backup version
- Check backup metadata: `cat <backup_dir>/data/db2-backup-info.yaml`
- Install matching Db2 version: `export DB2_VERSION=11.5.8.0-cn7`
- Alternatively, upgrade backup to target version (requires manual intervention)

**Issue: Restore fails with "database already exists"**
```text
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
```text
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
```text
Error: SQL0551N  User does not have required authorization
```
**Solution:**

- Verify db2inst1 user has proper permissions
- Check pod security context and service account
- Ensure restore scripts have execute permissions
- Review OpenShift security policies (SCC)

**Issue: S3 restore fails to download backup files**
```text
Error: Failed to download backup from S3 bucket
```
**Solution:**

- Verify S3 credentials have read permissions
- Check S3 bucket name and path are correct
- Test S3 connectivity: `aws s3 ls s3://<bucket-name>/`
- Ensure network policies allow outbound S3 access
- Verify backup files exist in S3 bucket

### Performance Issues

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

### Validation and Verification

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

## Upgrading Db2 from v11 to v12

Upgrading from Db2 v11 to v12 is a major version change that requires explicit opt-in and a valid Db2 Warehouse license. Without a license, Db2 v12 will operate under a 30-day trial license — **this will cause your production system to go offline after expiry**.

### Prerequisites

- A valid Db2 Warehouse license file (`.lic` format) — see [Db2 v12 License File Format](#db2-v12-license-file-format) below
- The `db2_v12_upgrade` flag set to `true`
- A v12 target channel (e.g., `v12.0.0-cn1`)

### Required Variables

| Variable | Environment Variable | Description |
|---|---|---|
| `db2_v12_upgrade` | `DB2_V12_UPGRADE` | Must be `true` to authorize the upgrade |
| `db2_license_file` | `DB2_LICENSE_FILE` | Path to the Db2 v12 license file |
| `db2_channel` | `DB2_CHANNEL` | Target v12 channel (e.g., `v12.0.0-cn1`) |
| `db2_namespace` | `DB2_NAMESPACE` | Namespace containing the Db2 instances to upgrade |

### Example Usage

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    db2_action: upgrade
    db2_namespace: db2u
    db2_channel: v12.0.0-cn1
    db2_v12_upgrade: true
    db2_license_file: /path/to/db2wh.lic
  roles:
    - ibm.mas_devops.db2
```

Or using environment variables:

```bash
export DB2_ACTION=upgrade
export DB2_NAMESPACE=db2u
export DB2_CHANNEL=v12.0.0-cn1
export DB2_V12_UPGRADE=true
export DB2_LICENSE_FILE=/path/to/db2wh.lic
ansible-playbook ibm.mas_devops.oneclick_upgrade_db2
```

### Db2 v12 License File Format

IBM distributes the Db2 Warehouse license under several names — you may have received it as `db2wh.lic`, `db2ese.lic`, `db2aese.lic`, or simply as an "activation key" or "entitlement file". The file is a plain-text file with the following structure:

```text
[LicenseCertificate]
CheckSum=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
TimeStamp=YYYY-MM-DD HH:MM:SS
PasswordVersion=5
VendorName=IBM Corporation
VendorPassword=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
ProductName=IBM Db2 Warehouse
ProductID=5765-F41
ProductVersion=12.0
ProductAnnotation=
LicenseType=Permanent
...
```

!!! note
    This is a sample structure only — not a real license. Use it to verify that the file you have from IBM matches this format. The file should contain `[LicenseCertificate]` as the first line and include `ProductName=IBM Db2 Warehouse` or similar. If your file looks significantly different, you may have the wrong entitlement file.

### What Happens Without a License

If `db2_license_file` is not provided when upgrading to v12, the role will **fail immediately** with a clear error message. This is intentional — it prevents a silent downgrade from a full production license to a 30-day trial license, which would cause your database to go offline after the trial period expires.

!!! note
    New installations (`db2_action=install`) do not require a license file. Only upgrades from v11 to v12 enforce this requirement.

## Example Playbook

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    db2_action: install
    db2_instance_name: db2u-manage
    db2_namespace: db2u
    db2_meta_storage_class: ocs-storagecluster-cephfs
    db2_data_storage_class: ocs-storagecluster-ceph-rbd
    ibm_entitlement_key: "{{ lookup('env', 'IBM_ENTITLEMENT_KEY') }}"
  roles:
    - ibm.mas_devops.db2
```

## Run Role Playbook
After installing the Ansible Collection you can easily run the role standalone using the `run_role` playbook provided.

```bash
export DB2_ACTION=install
export DB2_INSTANCE_NAME=db2u-manage
export DB2_NAMESPACE=db2u
export DB2_META_STORAGE_CLASS=ocs-storagecluster-cephfs
export DB2_DATA_STORAGE_CLASS=ocs-storagecluster-ceph-rbd
export IBM_ENTITLEMENT_KEY=xxx
ROLE_NAME=db2 ansible-playbook ibm.mas_devops.run_role
```

## License

EPL-2.0
