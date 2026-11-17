# sls

Install **IBM Suite License Service** and generate a configuration that can be directly applied to IBM Maximo Application Suite.

The role assumes that you have already installed the Certificate Manager in the target cluster.  This action is performed by the [cert_manager](cert_manager.md) role if you want to use this collection to install the cert-manager operator.

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`sls_action`](#sls_action) | No | `install` |
| [`artifactory_username`](#artifactory_username) | Conditional | None |
| [`artifactory_token`](#artifactory_token) | Conditional | None |
| [`sls_catalog_source`](#sls_catalog_source) | No | `ibm-operator-catalog` |
| [`sls_channel`](#sls_channel) | No | `3.x` |
| [`sls_namespace`](#sls_namespace) | No | `ibm-sls` |
| [`sls_icr_cpopen`](#sls_icr_cpopen) | No | `icr.io/cpopen` |
| [`sls_instance_name`](#sls_instance_name) | No | `sls` |
| [`sls_icr_cp`](#sls_icr_cp) | No | `cp.icr.io/cp` |
| [`ibm_entitlement_key`](#ibm_entitlement_key) | Conditional | None |
| [`sls_entitlement_username`](#sls_entitlement_username) | No | `cp` |
| [`sls_entitlement_key`](#sls_entitlement_key) | No | `ibm_entitlement_key` |
| [`sls_domain`](#sls_domain) | No | None |
| [`sls_auth_enforce`](#sls_auth_enforce) | No | `True` |
| [`sls_mongo_retrywrites`](#sls_mongo_retrywrites) | No | `true` |
| [`sls_compliance_enforce`](#sls_compliance_enforce) | No | `True` |
| [`sls_registration_open`](#sls_registration_open) | No | `True` |
| [`sls_mongodb_cfg_file`](#sls_mongodb_cfg_file) | Conditional | None |
| [`sls_mongodb.hosts`](#sls_mongodbhosts) | Conditional | None |
| [`sls_mongodb.certificates`](#sls_mongodbcertificates) | Conditional | None |
| [`sls_mongodb.username`](#sls_mongodbusername) | Conditional | None |
| [`sls_mongodb.password`](#sls_mongodbpassword) | Conditional | None |
| [`mas_pod_templates_dir`](#mas_pod_templates_dir) | No | None |
| [`entitlement_file`](#entitlement_file) | No | `''` |
| [`bootstrap.license_file`](#bootstraplicense_file) | No | `''` |
| [`bootstrap.license_id`](#bootstraplicense_id) | Conditional | `''` |
| [`bootstrap.registration_key`](#bootstrapregistration_key) | No | `''` |
| [`mas_instance_id`](#mas_instance_id) | No | None |
| [`mas_config_dir`](#mas_config_dir) | No | None |
| [`sls_url`](#sls_url) | No | None |
| [`mas_license_sync_frequency`](#mas_license_sync_frequency) | No | `*/30 * * * *` |
| [`sls_tls_crt`](#sls_tls_crt) | No | None |
| [`sls_tls_crt_local_file_path`](#sls_tls_crt_local_file_path) | No | None |
| [`sls_registration_key`](#sls_registration_key) | No | None |
| [`custom_labels`](#custom_labels) | No | None |
| [`mas_backup_dir`](#mas_backup_dir) | Conditional | None |
| [`sls_backup_version`](#sls_backup_version) | Conditional | Auto-generated (`YYYYMMDD-HHMMSS`) |

Variables marked as Conditional are only required in specific circumstances: the Artifactory credentials when using the development catalog, `ibm_entitlement_key` for SLS 3.7.0 and earlier (unless `sls_url` is set), `sls_mongodb_cfg_file` or the `sls_mongodb` object to install SLS, `bootstrap.license_id` when `bootstrap.license_file` is set, and the backup variables for the backup and restore actions.

### Actions

#### sls_action

Operation to perform on the Suite License Service (SLS) instance — `install`, `gencfg`, `backup`, `restore`, or `uninstall`.

- **Optional**
- Environment Variable: `SLS_ACTION`
- Default: `install`

What each action does:

- `install` — deploys or updates the SLS operator and instance
- `gencfg` — only generates the SLSCfg resource for MAS integration, without installing SLS; requires `sls_url` to point to an existing SLS instance. Useful when SLS is shared across multiple MAS instances
- `backup` — creates a backup of all SLS resources, secrets, and registration data; requires `mas_backup_dir` and optionally `sls_backup_version`
- `restore` — restores SLS from a previously created backup; requires `mas_backup_dir` and `sls_backup_version`
- `uninstall` — removes the SLS instance and operator (destructive operation)

Always back up license data before using `uninstall`.

### Installation

If `sls_url` is set then the role will skip the installation of an SLS instance and simply generate the SLSCfg resource for the SLS instance defined.

#### artifactory_username

Username for authenticating to IBM Artifactory to access development builds of SLS — typically your IBM w3Id.

- **Required** when `sls_catalog_source` is set to `ibm-sls-operators` (development catalog)
- Environment Variable: `ARTIFACTORY_USERNAME`
- Default: None

Not needed for production installations using `ibm-operator-catalog`, which use `ibm_entitlement_key` instead (SLS 3.7.0 and earlier). Must be set together with `artifactory_token` — without valid credentials, development catalog subscriptions will fail to pull operator images.

#### artifactory_token

API token for authenticating to IBM Artifactory to access development builds of SLS.

- **Required** when `sls_catalog_source` is set to `ibm-sls-operators` (development catalog)
- Environment Variable: `ARTIFACTORY_TOKEN`
- Default: None

Must be set together with `artifactory_username`; ignored when using production catalogs. Keep this token secure and do not commit it to source control.

#### sls_catalog_source

OpenShift operator catalog source containing the SLS operator subscription — any valid CatalogSource name present in the `openshift-marketplace` namespace (typically `ibm-operator-catalog` or `ibm-sls-operators`).

- **Optional**
- Environment Variable: `SLS_CATALOG_SOURCE`
- Default: `ibm-operator-catalog`

Use the default for production installations with official IBM releases; use `ibm-sls-operators` for development builds from Artifactory, which also requires `artifactory_username` and `artifactory_token`. Works with `sls_channel` to determine the specific operator version installed — an invalid catalog source will cause the subscription to fail.

#### sls_channel

SLS operator subscription channel, which determines the version stream you'll receive updates from — `3.x` (check the IBM Operator Catalog for currently available channels).

- **Optional**
- Environment Variable: `SLS_CHANNEL`
- Default: `3.x`

The default `3.x` provides the latest SLS 3.x releases (recommended for most deployments); use specific older channels only if required for compatibility with older MAS versions — consult the MAS compatibility matrix before selecting. Changing channels after installation will trigger an upgrade to the latest version in the new channel. SLS 3.8.0+ no longer requires IBM entitlement keys, as images moved to the public registry.

#### sls_namespace

OpenShift namespace where the SLS operator and instance will be deployed — any valid Kubernetes namespace name (lowercase alphanumeric and hyphens).

- **Optional**
- Environment Variable: `SLS_NAMESPACE`
- Default: `ibm-sls`

All SLS resources (operator, pods, secrets, services, ConfigMaps) are created in this namespace, and it is also used in SLSCfg generation to reference SLS service endpoints. The namespace is created if it doesn't exist — ensure you have permissions to create namespaces in the cluster. Changing it after deployment requires reinstallation.

#### sls_icr_cpopen

Container registry source for SLS operator and component images — any valid container registry URL (e.g. `icr.io/cpopen`, `my-registry.com/sls`).

- **Optional**
- Environment Variable: `SLS_ICR_CPOPEN`
- Default: `icr.io/cpopen`

From SLS 3.8.0 onwards this is the primary registry variable, as images moved to the public IBM Container Registry — the default requires no entitlement key. Override only for development images or airgap/mirror scenarios; an incorrect or inaccessible registry will cause image pull failures.

#### sls_instance_name

Unique identifier for this SLS installation within the cluster — a lowercase alphanumeric string (e.g. `sls`, `sls-prod`, `sls-dev`).

- **Optional**
- Environment Variable: `SLS_INSTANCE_NAME`
- Default: `sls`

Distinguishes this SLS installation from others in the same cluster (must be unique if running multiple SLS instances) and is embedded in many SLS resource names. It cannot be changed after installation without reinstalling, so most deployments use the default.

#### sls_icr_cp

Container registry source for SLS images (SLS 3.7.0 and earlier only) — any valid container registry URL (e.g. `cp.icr.io/cp`, `my-registry.com/sls`).

- **Optional**
- Environment Variable: `SLS_ICR_CP`
- Default: `cp.icr.io/cp`

Deprecated in SLS 3.8.0 — SLS images moved to the public registry (`icr.io/cpopen`); for SLS 3.8.0+ use `sls_icr_cpopen` instead (no entitlement key needed). For SLS 3.7.0 and earlier, all SLS images are pulled from this registry and it requires `ibm_entitlement_key` for authentication.

#### ibm_entitlement_key

IBM entitlement key for accessing IBM Container Registry images (SLS 3.7.0 and earlier only) — obtain it from the [IBM Container Library](https://myibm.ibm.com/products-services/containerlibrary).

- **Required** for SLS 3.7.0 and earlier, unless `sls_url` is provided
- Environment Variable: `IBM_ENTITLEMENT_KEY`
- Default: None

Deprecated in SLS 3.8.0 — SLS images moved to the public registry (`icr.io/cpopen`) and no entitlement key is needed. The key is tied to your IBM Cloud account and product entitlements, and is stored in a Kubernetes secret in the SLS namespace; invalid or expired keys will cause image pull failures.

#### sls_entitlement_username

Username for authenticating to IBM Container Registry (SLS 3.7.0 and earlier only) — `cp` for production installations with an IBM entitlement key.

- **Optional**
- Environment Variable: `SLS_ENTITLEMENT_USERNAME`
- Default: `cp`

Used together with `ibm_entitlement_key` to create image pull secrets for the SLS namespace; an incorrect username will cause image pull authentication failures. Deprecated in SLS 3.8.0 — SLS images moved to the public registry and no authentication is needed.

#### sls_entitlement_key

SLS-specific IBM entitlement key override (SLS 3.7.0 and earlier only).

- **Optional**
- Environment Variable: `SLS_ENTITLEMENT_KEY`
- Default: Value of `ibm_entitlement_key`

When set, this key is used instead of `ibm_entitlement_key` for SLS image authentication — primarily used in development scenarios where different keys are needed for different components. Invalid keys will cause image pull failures. Deprecated in SLS 3.8.0 — no entitlement key is needed.

### Configuration

#### sls_domain

Custom domain name for external access to SLS via OpenShift routes — any valid DNS domain name (e.g. `sls.mycompany.com`, `license.example.org`).

- **Optional**
- Environment Variable: `SLS_DOMAIN`
- Default: None (SLS is only accessible within the cluster)

Required when SLS serves MAS instances deployed in separate OpenShift clusters (multi-cluster SLS deployments); leave unset for single-cluster deployments where SLS and MAS are in the same cluster. When set, SLS creates an external route at the specified domain — ensure DNS is properly configured to resolve the domain to your cluster, with appropriate SSL certificates and network security controls.

#### sls_auth_enforce

Whether SLS enforces client authentication via mutual TLS (mTLS) — `True` or `False`.

- **Optional**
- Environment Variable: `SLS_AUTH_ENFORCE`
- Default: `True`

When `True`, clients must register with SLS and use mTLS certificates for API calls (secure). Setting to `False` removes authentication requirements, allowing unauthenticated API access — use only in development/testing environments; production deployments should always enforce authentication. Works with `sls_registration_open` to control client registration and access.

#### sls_mongo_retrywrites

Whether SLS uses the MongoDB retryable writes feature — `true` or `false`.

- **Optional**
- Environment Variable: `SLS_MONGO_RETRYWRITES`
- Default: `true`

When `true`, failed write operations are automatically retried (improves reliability with MongoDB Community Edition or IBM Cloud Databases for MongoDB). Set to `false` when using AWS DocumentDB or any MongoDB-compatible database that doesn't support retryable writes — DocumentDB does not support them, and leaving this enabled causes connection errors. Must align with the capabilities of the MongoDB provider configured via `sls_mongodb_cfg_file` or the `sls_mongodb` object.

#### sls_compliance_enforce

Whether SLS enforces license token compliance — `True` or `False`.

- **Optional**
- Environment Variable: `SLS_COMPLIANCE_ENFORCE`
- Default: `True`

When `True`, license checkout requests are denied when insufficient tokens are available (enforces compliance and prevents over-consumption). When `False`, checkout requests succeed even without available tokens (tracks but doesn't enforce) — this allows operation beyond licensed capacity and may result in license compliance issues; use only in non-production environments or with explicit approval.

#### sls_registration_open

Whether SLS allows new client self-registration — `True` or `False`.

- **Optional**
- Environment Variable: `SLS_REGISTRATION_OPEN`
- Default: `True`

When `True`, clients such as MAS instances can register themselves and obtain mTLS certificates for SLS API access. For production environments, consider setting to `False` after all legitimate clients are registered to prevent unauthorized registrations — only pre-registered clients can then access SLS. Works with `sls_auth_enforce` to control the authentication and registration flow.

#### sls_mongodb_cfg_file

Local file path to a MongoCfg YAML file for SLS MongoDB configuration (e.g. `/home/user/masconfig/mongocfg-mongoce-system.yaml`).

- **Required** (either `sls_mongodb_cfg_file` or the `sls_mongodb` object are required to install SLS)
- Environment Variable: `SLS_MONGODB_CFG_FILE`
- Default: None

Preferred method when you've deployed MongoDB using the `mongodb` role (which generates this file, in `mas_config_dir`), as it ensures consistency with the MongoDB deployment. The role extracts the MongoDB connection details (hosts, certificates, credentials) from this file; an invalid or missing file will cause installation to fail.

#### sls_mongodb.hosts

List of MongoDB `host:port` pairs for the SLS database connection (e.g. `["mongo-0.mongo:27017", "mongo-1.mongo:27017", "mongo-2.mongo:27017"]`).

- **Required** (either `sls_mongodb_cfg_file` or the `sls_mongodb` object are required to install SLS)
- Environment Variable: None
- Default: None

Specifies the MongoDB replica set members SLS connects to for license data storage — provide all replica set members for high availability and automatic failover. Part of the `sls_mongodb` object; all `sls_mongodb.*` variables must be provided together when not using `sls_mongodb_cfg_file`.

#### sls_mongodb.certificates

List of TLS/SSL certificates for secure MongoDB connections, as an array of certificate strings in PEM format.

- **Required** (either `sls_mongodb_cfg_file` or the `sls_mongodb` object are required to install SLS)
- Environment Variable: None
- Default: None

Obtain the CA or server certificate from your MongoDB deployment; the certificates must match the deployment's TLS configuration. Without valid certificates, SLS cannot establish secure connections to MongoDB. Part of the `sls_mongodb` object; all `sls_mongodb.*` variables must be provided together when not using `sls_mongodb_cfg_file`.

#### sls_mongodb.username

MongoDB username for SLS database authentication — must correspond to a valid MongoDB user with permission to read and write the SLS database.

- **Required** (either `sls_mongodb_cfg_file` or the `sls_mongodb` object are required to install SLS)
- Environment Variable: None
- Default: None

Part of the `sls_mongodb` object; all `sls_mongodb.*` variables must be provided together when not using `sls_mongodb_cfg_file`.

#### sls_mongodb.password

MongoDB password for SLS database authentication — must correspond to the specified MongoDB username.

- **Required** (either `sls_mongodb_cfg_file` or the `sls_mongodb` object are required to install SLS)
- Environment Variable: None
- Default: None

Keep this password secure and do not commit it to source control. Part of the `sls_mongodb` object; all `sls_mongodb.*` variables must be provided together when not using `sls_mongodb_cfg_file`.

#### mas_pod_templates_dir

Local directory path containing pod template customization files for SLS workloads, enabling control over resource limits, node affinity, tolerations, and other Kubernetes pod settings.

- **Optional**
- Environment Variable: `MAS_POD_TEMPLATES_DIR`
- Default: None

The role looks for the following files in the named directory; the file content should be the YAML block to insert under a `podTemplates: {object}` element:

- `ibm-sls-licenseservice.yml` — applied to the LicenseService custom resource under `spec.podTemplates` during installation. See the [BestEfforts reference configuration](https://github.com/ibm-mas/cli/blob/master/image/cli/mascli/templates/pod-templates/best-effort/ibm-sls-licenseservice.yml) and [Customizing Pod Templates](https://www.ibm.com/docs/en/mas-cd/continuous-delivery?topic=sls-supported-pods-workload-customization-in-suite-license-service)
- `ibm-mas-slscfg.yml` — inserted into the SlsCfg spec under a top-level `podTemplates` element during SLSCfg generation. See the [BestEfforts reference configuration](https://github.com/ibm-mas/cli/blob/master/image/cli/mascli/templates/pod-templates/best-effort/ibm-mas-slscfg.yml) and [Customizing Pod Templates](https://www.ibm.com/docs/en/mas-cd/continuous-delivery?topic=configuring-customizing-workloads)

Invalid templates can cause pod scheduling failures.

### Bootstrap Variables (SLS 3.7.0 and higher)

#### entitlement_file

Local file path to the IBM license entitlement file for bootstrapping SLS (e.g. `/home/user/licenses/entitlement.dat`).

- **Optional**
- Environment Variable: `SLS_ENTITLEMENT_FILE`
- Default: `''`

When provided, SLS is automatically configured with the license entitlements from this file during installation; without it, you must manually upload license entitlements through the SLS UI or API after installation. Supported in SLS 3.7.0 and higher — this is the new mechanism replacing the old bootstrap. The license file is obtained from IBM and contains your MAS product entitlements; keep it secure as it represents your license rights.

### Bootstrap [Partly deprecated in SLS 3.7.0]

#### bootstrap.license_file

Local path to the License File to be used to bootstrap SLS — deprecated in SLS 3.7.0; use only for versions up to 3.6.0.

- **Optional**
- Environment Variable: `SLS_LICENSE_FILE`
- Default: `''`

Don't set if you wish to set up entitlement later on. This variable used to be called `bootstrap.entitlement_file` and defaulted to `{{ mas_config_dir }}/entitlement.lic` — this is no longer the case, and `SLS_LICENSE_FILE` has to be set in order to bootstrap. For SLS 3.7.0 and higher, use `entitlement_file` instead.

#### bootstrap.license_id

License Id to be used to bootstrap SLS — deprecated in SLS 3.7.0; use only for versions up to 3.6.0.

- **Required** when `bootstrap.license_file` is set (should match the licenseId from the license file)
- Environment Variable: `SLS_LICENSE_ID`
- Default: `''`

Don't set if you wish to set up entitlement later on.

#### bootstrap.registration_key

Registration Key to be used to bootstrap SLS.

- **Optional**
- Environment Variable: `SLS_REGISTRATION_KEY`
- Default: `''`

Don't set if you wish to set up entitlement later on.

### SLSCfg Variables

#### mas_instance_id

The instance ID of Maximo Application Suite that the SlsCfg configuration will target.

- **Optional** (if neither this nor `mas_config_dir` are set then the role will not generate a SlsCfg template)
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

#### mas_config_dir

Local directory to save the generated SlsCfg resource definition.

- **Optional** (if neither this nor `mas_instance_id` are set then the role will not generate a SlsCfg template)
- Environment Variable: `MAS_CONFIG_DIR`
- Default: None

Can be used to manually configure a MAS instance to connect to the SLS instance, or used as an input to the [suite_config](suite_config.md) role.

#### sls_url

The URL of the LicenseService to be called when the Maximo Application Suite is registered with SLS.

- **Optional** (used to instruct the role to set up MAS for an existing SLS instance)
- Environment Variable: `SLS_URL`
- Default: None

#### mas_license_sync_frequency

The sync frequency of the user license sync cronjob between Maximo Application Suite and SLS.

- **Optional**
- Environment Variable: `MAS_LICENSE_SYNC_FREQUENCY`
- Default: `*/30 * * * *`

#### sls_tls_crt

The TLS CA certificate of the LicenseService to be used when the Maximo Application Suite is registered with SLS. Takes precedence over `sls_tls_crt_local_file_path`.

- **Optional** (used to instruct the role to set up MAS for an existing SLS instance)
- Environment Variable: `SLS_TLS_CERT`
- Default: None

#### sls_tls_crt_local_file_path

The path on the local system to a file containing the TLS CA certificate of the LicenseService to be used when the Maximo Application Suite is registered with SLS. This variable is only used if `sls_tls_crt` has not been set.

- **Optional** (used to instruct the role to set up MAS for an existing SLS instance)
- Environment Variable: `SLS_TLS_CERT_LOCAL_FILE_PATH`
- Default: None

#### sls_registration_key

The Registration key of the LicenseService instance to be used when the Maximo Application Suite is registered with SLS.

- **Optional**
- Environment Variable: `SLS_REGISTRATION_KEY`
- Default: None

#### custom_labels

List of comma-separated `key=value` pairs for setting custom labels on instance-specific resources.

- **Optional**
- Environment Variable: `CUSTOM_LABELS`
- Default: None

### Backup and Restore Variables

#### mas_backup_dir

Directory path where SLS backup files will be stored (e.g. `/backup/mas`, `/home/user/sls-backups`).

- **Required** for backup and restore operations
- Environment Variable: `MAS_BACKUP_DIR`
- Default: None

Required when `sls_action` is set to `backup` or `restore`. Backups are written to (for backup) or read from (for restore) a timestamped directory structure under this path: `{mas_backup_dir}/backup-{version}-sls/`. Use a persistent location with sufficient storage space and appropriate permissions, and back it up to external storage for disaster recovery. Works with `sls_backup_version` to create unique backup directories.

#### sls_backup_version

Version identifier for the backup, used to create unique backup directories — any string suitable for directory names (alphanumeric, hyphens, underscores).

- **Optional** for backup (auto-generated if not provided), **Required** for restore
- Environment Variable: `SLS_BACKUP_VERSION`
- Default: Auto-generated timestamp in `YYYYMMDD-HHMMSS` format (e.g. `20260122-131500`)

For backup, creates directory `{mas_backup_dir}/backup-{version}-sls/`; for restore, looks for the backup in `{mas_backup_dir}/backup-{version}-sls/` — when restoring, you must know the exact backup version identifier (list the contents of `mas_backup_dir` to see available backups).

## Backup and Restore Operations

The SLS role supports backup and restore operations to protect your license service configuration and data. This is essential for disaster recovery, migration, and upgrade scenarios.

### What Gets Backed Up

The SLS backup operation captures all critical resources needed to restore a complete SLS instance:

**Kubernetes Resources:**

- **Project/Namespace**: The SLS namespace configuration
- **Secrets**:
  - IBM entitlement credentials (`ibm-entitlement`)
  - MongoDB connection credentials (`ibm-sls-mongo-credentials`)
  - Bootstrap configuration (`{instance-name}-bootstrap`)
  - License entitlement data (`ibm-sls-{instance-name}-entitlement`)
  - All referenced secrets (auto-discovered)
- **ConfigMaps**: Suite registration configuration
- **Operator Resources**:
  - Subscription (`ibm-sls`)
  - OperatorGroup
- **SLS Custom Resources**:
  - LicenseService CR (the main SLS instance)
- **Certificate Manager Resources**:
  - Issuers (self-signed and CA issuers)
  - Certificates (CA certificate)

**Registration Data:**

- License ID
- Registration key
- Suite registration information

### Backup Process

The backup operation performs the following steps:

1. **Validation**: Verifies required variables (`mas_backup_dir`, `sls_namespace`, `sls_instance_name`)
2. **Version Generation**: Creates or uses provided backup version identifier
3. **Resource Discovery**: Identifies all SLS resources and auto-discovers referenced secrets
4. **Backup Execution**: Exports all resources to YAML files in the backup directory
5. **Registration Capture**: Saves SLS registration details for restore
6. **Verification**: Reports backup statistics and any failures

**Backup Directory Structure:**

```text
{mas_backup_dir}/
└── backup-{version}-sls/
    ├── resources/
    │   ├── projects/
    │   ├── secrets/
    │   ├── configmaps/
    │   ├── subscriptions/
    │   ├── operatorgroups/
    │   ├── licenseservices/
    │   ├── issuers/
    │   └── certificates/
    └── sls-registration.yaml
```

### Restore Process

The restore operation performs the following steps:

1. **Validation**: Verifies required variables and backup existence
2. **Backup Verification**: Checks for valid backup structure and required files
3. **Certificate Manager Check**: Ensures cert-manager is installed in the cluster
4. **Sequential Restoration**:
   - Projects/Namespaces
   - Secrets and ConfigMaps
   - OperatorGroups
   - Subscriptions (triggers operator installation)
   - Certificate Manager resources
   - Bootstrap secret (recreated from registration data)
   - LicenseService CR (with optional domain override)
5. **Verification**: Waits for SLS to become ready and reports restore statistics

**Important Restore Considerations:**

- The target cluster must have Certificate Manager installed
- MongoDB must be available and accessible (not restored by this role)
- The restore can optionally override the `sls_domain` if deploying to a different cluster
- All secrets and credentials are restored exactly as backed up

### Backup Example

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    sls_action: backup
    mas_backup_dir: /backup/mas
    sls_namespace: ibm-sls
    sls_instance_name: sls
    # Optional: specify custom backup version
    # sls_backup_version: "pre-upgrade-backup"

  roles:
    - ibm.mas_devops.sls
```

**Using environment variables:**

```bash
export SLS_ACTION=backup
export MAS_BACKUP_DIR=/backup/mas
export SLS_NAMESPACE=ibm-sls
export SLS_INSTANCE_NAME=sls
# Optional: export SLS_BACKUP_VERSION=pre-upgrade-backup

ansible-playbook ibm.mas_devops.run_role
```

### Restore Example

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    sls_action: restore
    mas_backup_dir: /backup/mas
    sls_backup_version: "20260122-131500"
    # Optional: override domain for different cluster
    # sls_domain: sls.newcluster.example.com

  roles:
    - ibm.mas_devops.sls
```

**Using environment variables:**

```bash
export SLS_ACTION=restore
export MAS_BACKUP_DIR=/backup/mas
export SLS_BACKUP_VERSION=20260122-131500
# Optional: export SLS_DOMAIN=sls.newcluster.example.com

ansible-playbook ibm.mas_devops.run_role
```

### Best Practices

1. **Regular Backups**: Schedule regular backups before:
   - SLS upgrades
   - License entitlement changes
   - Cluster maintenance
   - MAS upgrades

2. **Backup Storage**:
   - Store backups in a location separate from the cluster
   - Implement backup retention policies
   - Test restore procedures regularly

3. **MongoDB Backup**:
   - SLS backup does NOT include MongoDB data
   - Ensure MongoDB is backed up separately using the `mongodb` role backup functionality
   - Coordinate SLS and MongoDB backups for consistency

4. **Pre-Restore Checklist**:
   - Verify Certificate Manager is installed
   - Ensure MongoDB is available and accessible
   - Confirm backup version exists and is complete
   - Review and adjust `sls_domain` if restoring to different cluster

5. **Disaster Recovery**:
   - Document backup locations and procedures
   - Test restore process in non-production environment
   - Keep backup version identifiers in a safe location
   - Maintain MongoDB connection details separately

6. **Migration Scenarios**:
   - When migrating to a new cluster, restore MongoDB first
   - Update `sls_domain` if cluster ingress domain changed
   - Verify network connectivity between restored SLS and MAS instances

### Troubleshooting

**Backup Issues:**

- **"Required variables not provided"**: Ensure `mas_backup_dir`, `sls_namespace`, and `sls_instance_name` are set
- **"Resource not found"**: Some resources may not exist in your deployment (this is normal)
- **Permission errors**: Ensure write access to `mas_backup_dir`

**Restore Issues:**

- **"Backup archive not found"**: Verify `sls_backup_version` matches an existing backup directory
- **"Certificate Manager not found"**: Install cert-manager before restoring SLS
- **"LicenseService not ready"**: Check operator logs and ensure MongoDB is accessible
- **Domain mismatch**: Use `sls_domain` variable to override domain for new cluster

For more information on backup and restore, refer to the [IBM Documentation on Backing up and Restoring SLS](https://www.ibm.com/docs/en/masv-and-l/cd?topic=service-backing-up-restoring).

## Example Playbook

### Install and generate a configuration [up to SLS 3.6.0]

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    ibm_entitlement_key: xxxx
    mas_instance_id: inst1
    mas_config_dir: /home/me/masconfig
    sls_mongodb_cfg_file: "/etc/mas/mongodb.yml"

    bootstrap:
      license_id: "aa78dd65ef10"
      license_file: "/etc/mas/entitlement.lic"
      registration_key: xxxx

  roles:
    - ibm.mas_devops.sls
```

### Install and upload license file [SLS 3.7.0]

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    ibm_entitlement_key: xxxx
    mas_instance_id: inst1
    sls_mongodb_cfg_file: "/etc/mas/mongodb.yml"
    entitlement_file: "/etc/mas/entitlement.lic"

  roles:
    - ibm.mas_devops.sls
```

### Install and upload license file [from SLS 3.8.0]

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: inst1
    sls_mongodb_cfg_file: "/etc/mas/mongodb.yml"
    entitlement_file: "/etc/mas/entitlement.lic"

  roles:
    - ibm.mas_devops.sls
```

### Generate a configuration for an existing installation

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: inst1
    mas_config_dir: /home/me/masconfig

    sls_action: gencfg
    sls_tls_crt_local_file_path: "/home/me/sls.crt"
    slscfg_url: "https://xxx"
    slscfg_registration_key: "xxx"

  roles:
    - ibm.mas_devops.sls
```

## Run Role Playbook

```bash
export SLS_MONGODB_CFG_FILE=/etc/mas/mongodb.yml
export SLS_ENTITLEMENT_FILE=/etc/mas/entitlement.lic
export MAS_INSTANCE_ID=inst1
ansible-playbook ibm.mas_devops.run_role
```

## License

EPL-2.0
