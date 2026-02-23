# sls

Install **IBM Suite License Service** and generate a configuration that can be directly applied to IBM Maximo Application Suite.

The role assumes that you have already installed the Certificate Manager in the target cluster.  This action is performed by the [cert_manager](cert_manager.md) role if you want to use this collection to install the cert-manager operator.

## Role Variables - General

### General Variables

#### sls_action
Specifies which operation to perform on the Suite License Service (SLS) instance.

- **Optional**
- Environment Variable: `SLS_ACTION`
- Default: `install`

**Purpose**: Controls what action the role executes against the SLS instance. This allows the same role to handle installation, configuration generation, and removal of SLS.

**When to use**:
- Use `install` for initial SLS deployment or updates
- Use `gencfg` to generate SLS configuration for MAS without installing SLS (when using existing SLS)
- Use `uninstall` to remove SLS instance (use with caution)

**Valid values**: `install`, `gencfg`, `uninstall`

**Impact**: 
- `install`: Deploys or updates SLS operator and instance
- `gencfg`: Only generates SLSCfg resource for MAS integration
- `uninstall`: Removes SLS instance and operator (destructive operation)

**Related variables**: When using `gencfg`, requires `sls_url` to be set to point to existing SLS instance.

**Note**: Always backup license data before using `uninstall`. The `gencfg` action is useful when SLS is shared across multiple MAS instances.


## Role Variables - Installation
If `sls_url` is set then the role will skip the installation of an SLS instance and simply generate the SLSCfg resource for the SLS instance defined.

#### artifactory_username
Username for authenticating to IBM Artifactory to access development builds of SLS.

- **Optional**
- Environment Variable: `ARTIFACTORY_USERNAME`
- Default: None

**Purpose**: Provides authentication credentials to pull development/pre-release SLS operator images from IBM's Artifactory registry. Required only when installing development builds for testing or early access.

**When to use**:
- Required when `sls_catalog_source` is set to `ibm-sls-operators` (development catalog)
- Not needed for production installations using `ibm-operator-catalog`
- Use your IBM w3Id username for development builds

**Valid values**: Valid IBM Artifactory username (typically your w3Id)

**Impact**: Without valid credentials, development catalog subscriptions will fail to pull operator images. This variable is ignored when using production catalogs.

**Related variables**:
- `artifactory_token`: Must be set together with this username
- `sls_catalog_source`: Determines if Artifactory credentials are needed

**Note**: Only required for development/pre-release builds. Production installations use `ibm_entitlement_key` instead (for SLS 3.7.0 and earlier).

#### artifactory_token
API token for authenticating to IBM Artifactory to access development builds of SLS.

- **Optional**
- Environment Variable: `ARTIFACTORY_TOKEN`
- Default: None

**Purpose**: Provides the API token/password credential to authenticate with IBM's Artifactory registry when pulling development/pre-release SLS operator images.

**When to use**:
- Required when `sls_catalog_source` is set to `ibm-sls-operators` (development catalog)
- Not needed for production installations using `ibm-operator-catalog`
- Use your IBM Artifactory API key for development builds

**Valid values**: Valid IBM Artifactory API token

**Impact**: Without a valid token, development catalog subscriptions will fail to pull operator images. This variable is ignored when using production catalogs.

**Related variables**:
- `artifactory_username`: Must be set together with this token
- `sls_catalog_source`: Determines if Artifactory credentials are needed

**Note**: Only required for development/pre-release builds. Keep this token secure and do not commit to source control.

#### sls_catalog_source
Specifies the OpenShift operator catalog source containing the SLS operator subscription.

- **Optional**
- Environment Variable: `SLS_CATALOG_SOURCE`
- Default: `ibm-operator-catalog`

**Purpose**: Controls which operator catalog is used to locate and install the SLS operator. This determines where OpenShift looks for the operator images and metadata during installation.

**When to use**:
- Use default `ibm-operator-catalog` for production installations with official IBM releases
- Use `ibm-sls-operators` for development builds from Artifactory
- Only change if directed to use a custom catalog for specific testing or airgap scenarios

**Valid values**: Any valid CatalogSource name present in the `openshift-marketplace` namespace (typically `ibm-operator-catalog` or `ibm-sls-operators`)

**Impact**: Changing this value affects which operator versions are available for installation. An invalid catalog source will cause the subscription to fail. Development catalogs require additional authentication via `artifactory_username` and `artifactory_token`.

**Related variables**:
- `sls_channel`: Works together to determine the specific operator version installed
- `artifactory_username` and `artifactory_token`: Required when using `ibm-sls-operators`

**Note**: For development catalogs, you must also provide Artifactory credentials.

#### sls_channel
Specifies the SLS operator subscription channel, which determines the version stream you'll receive updates from.

- **Optional**
- Environment Variable: `SLS_CHANNEL`
- Default: `3.x`

**Purpose**: Controls which version of SLS will be installed and which updates will be automatically applied. The channel corresponds to major version releases and determines the feature set and compatibility level of your SLS installation.

**When to use**:
- Use default `3.x` for latest SLS 3.x releases (recommended for most deployments)
- Use specific older channels only if required for compatibility with older MAS versions
- Consult the MAS compatibility matrix before selecting a channel

**Valid values**: `3.x` (check the IBM Operator Catalog for currently available channels)

**Impact**: The channel determines which SLS version is installed and which automatic updates are applied. Changing channels after installation will trigger an upgrade to the latest version in that channel.

**Related variables**: Works with `sls_catalog_source` to determine available channels.

**Note**: SLS 3.8.0+ no longer requires IBM entitlement keys as images moved to public registry. Review the SLS release notes before changing this value.

#### sls_namespace
OpenShift namespace where the SLS operator and instance will be deployed.

- **Optional**
- Environment Variable: `SLS_NAMESPACE`
- Default: `ibm-sls`

**Purpose**: Defines the Kubernetes namespace for SLS resources, providing isolation and organization for the SLS deployment within the cluster.

**When to use**:
- Use default `ibm-sls` for standard deployments
- Change only if you need multiple SLS instances or have namespace naming requirements
- Ensure namespace doesn't conflict with existing deployments

**Valid values**: Any valid Kubernetes namespace name (lowercase alphanumeric and hyphens)

**Impact**: All SLS resources (operator, pods, secrets, services, ConfigMaps) will be created in this namespace. Changing this after deployment requires reinstallation.

**Related variables**: Used in SLSCfg generation to reference SLS service endpoints.

**Note**: The namespace will be created if it doesn't exist. Ensure you have permissions to create namespaces in the cluster.

#### sls_icr_cpopen
Container registry source for SLS operator and component images.

- **Optional**
- Environment Variable: `SLS_ICR_CPOPEN`
- Default: `icr.io/cpopen`

**Purpose**: Specifies the container registry from which SLS pulls all operator and component images. From SLS 3.8.0 onwards, this is the primary registry variable as images moved to the public IBM Container Registry.

**When to use**:
- Use default `icr.io/cpopen` for production installations (SLS 3.8.0+)
- Override only for development images or airgap/mirror scenarios
- No authentication required for default public registry

**Valid values**: Any valid container registry URL (e.g., `icr.io/cpopen`, `my-registry.com/sls`)

**Impact**: All SLS images will be pulled from this registry. An incorrect or inaccessible registry will cause image pull failures. The default public registry requires no entitlement key (SLS 3.8.0+).

**Related variables**:
- `sls_icr_cp`: Deprecated in SLS 3.8.0, only needed for SLS 3.7.0 and earlier
- `ibm_entitlement_key`: Not required when using default public registry (SLS 3.8.0+)

**Note**: **SLS 3.8.0+ uses public registry** - no entitlement key needed. For SLS 3.7.0 and earlier, use `sls_icr_cp` and provide `ibm_entitlement_key`.

#### sls_instance_name
Unique identifier for this SLS installation within the cluster.

- **Optional**
- Environment Variable: `SLS_INSTANCE_NAME`
- Default: `sls`

**Purpose**: Provides a unique identifier that distinguishes this SLS installation from others that may exist in the same cluster. This ID is used to generate resource names throughout the installation.

**When to use**:
- Use default `sls` for standard single-SLS deployments
- Change only if you need multiple SLS instances in the same cluster
- Must be unique within the cluster if running multiple SLS instances

**Valid values**: Lowercase alphanumeric string (e.g., `sls`, `sls-prod`, `sls-dev`)

**Impact**: This ID becomes part of resource names and is embedded in many SLS resources. It cannot be changed after installation without reinstalling.

**Related variables**: Used in SLSCfg generation to identify the SLS instance.

**Note**: Choose carefully as this cannot be changed after installation. Most deployments use the default `sls` value.

#### sls_icr_cp
Container registry source for SLS images (SLS 3.7.0 and earlier only).

- **Optional**
- Environment Variable: `SLS_ICR_CP`
- Default: `cp.icr.io/cp`

**Purpose**: Specifies the container registry for SLS images in versions 3.7.0 and earlier. This registry required IBM entitlement key authentication.

**When to use**:
- Only required for SLS versions 3.7.0 and earlier
- Not needed for SLS 3.8.0+ (images moved to public registry)
- Override only for development images or airgap scenarios with older SLS versions

**Valid values**: Any valid container registry URL (e.g., `cp.icr.io/cp`, `my-registry.com/sls`)

**Impact**: For SLS 3.7.0 and earlier, all SLS images will be pulled from this registry. Requires `ibm_entitlement_key` for authentication.

**Related variables**:
- `sls_icr_cpopen`: Use this instead for SLS 3.8.0+
- `ibm_entitlement_key`: Required when using this registry (SLS 3.7.0 and earlier)

**Note**: **DEPRECATED in SLS 3.8.0** - SLS images moved to public registry (`icr.io/cpopen`). This variable is only required for SLS versions up to 3.7.0. For SLS 3.8.0+, use `sls_icr_cpopen` instead (no entitlement key needed).

#### ibm_entitlement_key
IBM entitlement key for accessing IBM Container Registry images (SLS 3.7.0 and earlier only).

- **Required** for SLS 3.7.0 and earlier (unless `sls_url` is provided)
- Environment Variable: `IBM_ENTITLEMENT_KEY`
- Default: None

**Purpose**: Authenticates access to IBM's entitled container registry to pull SLS operator and component images. This key is tied to your IBM Cloud account and product entitlements.

**When to use**:
- Required for SLS versions 3.7.0 and earlier
- Not required for SLS 3.8.0 and later (images moved to public registry)
- Obtain from [IBM Container Library](https://myibm.ibm.com/products-services/containerlibrary)

**Valid values**: IBM entitlement key string (typically starts with "eyJ...")

**Impact**: Invalid or expired keys will cause image pull failures for SLS 3.7.0 and earlier. The key is stored in a Kubernetes secret in the SLS namespace.

**Related variables**:
- `sls_entitlement_username`: Username paired with this key (default: `cp`)
- `sls_icr_cp`: Registry requiring this authentication (SLS 3.7.0 and earlier)

**Note**: **DEPRECATED in SLS 3.8.0** - SLS images moved to public registry (`icr.io/cpopen`). This variable is only required for SLS versions up to 3.7.0. For SLS 3.8.0+, no entitlement key is needed.

#### sls_entitlement_username
Username for authenticating to IBM Container Registry (SLS 3.7.0 and earlier only).

- **Optional**
- Environment Variable: `SLS_ENTITLEMENT_USERNAME`
- Default: `cp`

**Purpose**: Provides the username credential for authenticating with IBM's entitled container registry when pulling SLS images for versions 3.7.0 and earlier.

**When to use**:
- Only needed for SLS versions 3.7.0 and earlier
- Not required for SLS 3.8.0+ (images moved to public registry)
- Usually can be left at default `cp` for production installations

**Valid values**: `cp` (for production installations with IBM entitlement key)

**Impact**: Used together with `ibm_entitlement_key` to create image pull secrets for the SLS namespace. Incorrect username will cause image pull authentication failures.

**Related variables**:
- `ibm_entitlement_key`: Must be set together with this username (SLS 3.7.0 and earlier)
- `sls_entitlement_key`: Alternative entitlement key specific for SLS

**Note**: **DEPRECATED in SLS 3.8.0** - SLS images moved to public registry. This variable is only required for SLS versions up to 3.7.0. For SLS 3.8.0+, no authentication is needed.

#### sls_entitlement_key
SLS-specific IBM entitlement key override (SLS 3.7.0 and earlier only).

- **Optional**
- Environment Variable: `SLS_ENTITLEMENT_KEY`
- Default: None (falls back to `ibm_entitlement_key`)

**Purpose**: Provides an SLS-specific IBM entitlement key that overrides the global `ibm_entitlement_key` variable. Primarily used in development scenarios where different keys are needed for different components.

**When to use**:
- Only needed for SLS versions 3.7.0 and earlier
- Use when you need a different entitlement key specifically for SLS
- Leave unset to use the global `ibm_entitlement_key` value
- Not required for SLS 3.8.0+ (images moved to public registry)

**Valid values**: IBM entitlement key string (typically starts with "eyJ...")

**Impact**: When set, this key is used instead of `ibm_entitlement_key` for SLS image authentication. Invalid keys will cause image pull failures.

**Related variables**:
- `ibm_entitlement_key`: Global entitlement key that this variable overrides
- `sls_entitlement_username`: Username paired with this key

**Note**: **DEPRECATED in SLS 3.8.0** - SLS images moved to public registry. This variable is only required for SLS versions up to 3.7.0. For SLS 3.8.0+, no entitlement key is needed.


## Role Variables - Configuration
#### sls_domain
Custom domain name for external access to SLS via OpenShift routes.

- **Optional**
- Environment Variable: `SLS_DOMAIN`
- Default: None (SLS is only accessible within the cluster)

**Purpose**: Enables external access to SLS through a custom domain route. This is essential when SLS needs to serve multiple MAS instances deployed in separate OpenShift clusters.

**When to use**:
- Required when SLS serves MAS instances in different OpenShift clusters
- Required for multi-cluster SLS deployments
- Leave unset for single-cluster deployments where SLS and MAS are in the same cluster

**Valid values**: Any valid DNS domain name (e.g., `sls.mycompany.com`, `license.example.org`)

**Impact**: When set, SLS creates an external route accessible at the specified domain. You must ensure DNS is properly configured to resolve this domain to your cluster. When not set, SLS is only accessible via internal cluster services.

**Related variables**: Affects how MAS instances connect to SLS (internal service vs external route).

**Note**: Ensure proper DNS configuration and SSL certificates for the domain. External access requires appropriate network security controls.

#### sls_auth_enforce
Controls whether SLS enforces client authentication via mutual TLS (mTLS).

- **Optional**
- Environment Variable: `SLS_AUTH_ENFORCE`
- Default: `True`

**Purpose**: Determines whether SLS requires clients to authenticate using mTLS certificates generated through the client registration flow. This provides secure authentication for SLS API access.

**When to use**:
- Use `True` (default) for production environments to enforce secure authentication
- Set to `False` only in development/testing environments where simplified access is needed
- Leave as default for standard secure deployments

**Valid values**: `True`, `False`

**Impact**: 
- When `True`: Clients must register with SLS and use mTLS certificates for API calls (secure)
- When `False`: Authentication is not enforced, allowing unauthenticated API access (insecure)

**Related variables**: Works with `sls_registration_open` to control client registration and access.

**Note**: Setting to `False` removes authentication requirements and should only be used in non-production environments. Production deployments should always enforce authentication.

#### sls_mongo_retrywrites
Controls whether SLS uses MongoDB retryable writes feature.

- **Optional**
- Environment Variable: `SLS_MONGO_RETRYWRITES`
- Default: `true`

**Purpose**: Determines whether SLS enables MongoDB's retryable writes feature, which automatically retries certain write operations that fail due to transient network errors or replica set elections.

**When to use**:
- Use `true` (default) when using MongoDB Community Edition or IBM Cloud Databases for MongoDB
- Set to `false` when using AWS DocumentDB (which doesn't support retryable writes)
- Set to `false` for any MongoDB-compatible database that doesn't support this feature

**Valid values**: `true`, `false`

**Impact**: 
- When `true`: Enables automatic retry of failed write operations (improves reliability)
- When `false`: Disables retryable writes (required for DocumentDB and similar services)

**Related variables**: 
- `sls_mongodb_cfg_file` or `sls_mongodb.*`: Determines which MongoDB service is used
- Must align with the capabilities of your MongoDB provider

**Note**: AWS DocumentDB does not support retryable writes. Set to `false` when using DocumentDB to avoid connection errors.

#### sls_compliance_enforce
Controls whether SLS enforces license token compliance.

- **Optional**
- Environment Variable: `SLS_COMPLIANCE_ENFORCE`
- Default: `True`

**Purpose**: Determines whether SLS blocks license checkout requests when insufficient tokens are available. This controls whether license limits are strictly enforced or merely tracked.

**When to use**:
- Use `True` (default) for production to enforce license compliance and prevent over-consumption
- Set to `False` only in development/testing environments or during grace periods
- Leave as default for standard compliant deployments

**Valid values**: `True`, `False`

**Impact**: 
- When `True`: License checkout requests are denied when insufficient tokens are available (enforces compliance)
- When `False`: License checkout requests succeed even without available tokens (tracks but doesn't enforce)

**Related variables**: Works with license entitlement configuration to control token availability.

**Note**: Setting to `False` allows operation beyond licensed capacity and may result in license compliance issues. Use only in non-production environments or with explicit approval.

#### sls_registration_open
Controls whether SLS allows new client self-registration.

- **Optional**
- Environment Variable: `SLS_REGISTRATION_OPEN`
- Default: `True`

**Purpose**: Determines whether clients can register themselves with SLS to obtain certificates for API access. This controls the initial onboarding process for new SLS clients.

**When to use**:
- Use `True` (default) to allow MAS instances and other clients to self-register
- Set to `False` after all clients are registered to prevent unauthorized registrations
- Leave as default for standard deployments where clients need to register

**Valid values**: `True`, `False`

**Impact**: 
- When `True`: Clients can register themselves and obtain mTLS certificates for SLS API access
- When `False`: New client registrations are blocked; only pre-registered clients can access SLS

**Related variables**: Works with `sls_auth_enforce` to control authentication and registration flow.

**Note**: For production environments, consider setting to `False` after all legitimate clients are registered to prevent unauthorized access.

#### sls_mongodb_cfg_file
Local file path to a MongoCfg YAML file for SLS MongoDB configuration.

- **Required** (Either `sls_mongodb_cfg_file` or the `sls_mongodb` object are required to install SLS)
- Environment Variable: `SLS_MONGODB_CFG_FILE`
- Default: None

**Purpose**: Provides MongoDB connection details to SLS by referencing a MongoCfg file generated by the `mongodb` role. This simplifies configuration by reusing existing MongoDB setup information.

**When to use**:
- Use when you've deployed MongoDB using the `mongodb` role (which generates this file)
- Preferred method as it ensures consistency with MongoDB deployment
- Alternative to manually specifying `sls_mongodb.*` variables

**Valid values**: Any valid local filesystem path to a MongoCfg YAML file (e.g., `/home/user/masconfig/mongocfg-mongoce-system.yaml`)

**Impact**: The role extracts MongoDB connection details (hosts, certificates, credentials) from this file to configure SLS. Invalid or missing file will cause installation to fail.

**Related variables**:
- `sls_mongodb.*`: Alternative method to specify MongoDB connection details
- `mas_config_dir`: Directory where `mongodb` role generates this file

**Note**: Either this variable or the `sls_mongodb` object must be provided. Using this file is recommended for consistency with MongoDB deployment.

#### sls_mongodb.hosts
List of MongoDB host:port pairs for SLS database connection.

- **Required** (Either `sls_mongodb_cfg_file` or the `sls_mongodb` object are required to install SLS)
- Environment Variable: None
- Default: None

**Purpose**: Specifies the MongoDB replica set members that SLS will connect to for license data storage. Multiple hosts provide high availability and failover capability.

**When to use**:
- Use when manually configuring MongoDB connection (not using `sls_mongodb_cfg_file`)
- Required for all MongoDB deployment types (Community, IBM Cloud, AWS DocumentDB)
- Provide all replica set members for high availability

**Valid values**: Array of strings in format `["host1:port1", "host2:port2", "host3:port3"]` (e.g., `["mongo-0.mongo:27017", "mongo-1.mongo:27017", "mongo-2.mongo:27017"]`)

**Impact**: SLS uses these hosts to establish database connections. Incorrect hosts will cause SLS installation to fail. Multiple hosts enable automatic failover.

**Related variables**:
- `sls_mongodb.certificates`: TLS certificates for secure connection
- `sls_mongodb.username` and `sls_mongodb.password`: Authentication credentials
- `sls_mongodb_cfg_file`: Alternative method to provide this information

**Note**: Part of the `sls_mongodb` object. All `sls_mongodb.*` variables must be provided together if not using `sls_mongodb_cfg_file`.

#### sls_mongodb.certificates
List of TLS/SSL certificates for secure MongoDB connections.

- **Required** (Either `sls_mongodb_cfg_file` or the `sls_mongodb` object are required to install SLS)
- Environment Variable: None
- Default: None

**Purpose**: Provides the TLS/SSL certificates needed to establish secure, encrypted connections between SLS and MongoDB. These certificates verify the MongoDB server's identity and enable encrypted communication.

**When to use**:
- Required when manually configuring MongoDB connection (not using `sls_mongodb_cfg_file`)
- Needed for all MongoDB deployments using TLS/SSL (recommended for production)
- Obtain from your MongoDB deployment (CA certificate or server certificate)

**Valid values**: Array of certificate strings in PEM format (e.g., `["-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----"]`)

**Impact**: Without valid certificates, SLS cannot establish secure connections to MongoDB. Invalid certificates will cause connection failures.

**Related variables**:
- `sls_mongodb.hosts`: MongoDB servers these certificates authenticate
- `sls_mongodb.username` and `sls_mongodb.password`: Used with certificates for authentication
- `sls_mongodb_cfg_file`: Alternative method to provide this information

**Note**: Part of the `sls_mongodb` object. All `sls_mongodb.*` variables must be provided together if not using `sls_mongodb_cfg_file`. Certificates must match the MongoDB deployment's TLS configuration.

#### sls_mongodb.username
MongoDB username for SLS database authentication.

- **Required** (Either `sls_mongodb_cfg_file` or the `sls_mongodb` object are required to install SLS)
- Environment Variable: None
- Default: None

**Purpose**: Provides the username credential for SLS to authenticate with MongoDB. This user must have appropriate permissions to read and write to the SLS database.

**When to use**:
- Required when manually configuring MongoDB connection (not using `sls_mongodb_cfg_file`)
- Must correspond to a valid MongoDB user with SLS database permissions
- Obtain from your MongoDB deployment configuration

**Valid values**: Valid MongoDB username string

**Impact**: SLS uses this username to authenticate with MongoDB. Invalid username will cause authentication failures and prevent SLS from accessing the database.

**Related variables**:
- `sls_mongodb.password`: Password for this username
- `sls_mongodb.hosts`: MongoDB servers to authenticate against
- `sls_mongodb.certificates`: TLS certificates for secure authentication
- `sls_mongodb_cfg_file`: Alternative method to provide this information

**Note**: Part of the `sls_mongodb` object. All `sls_mongodb.*` variables must be provided together if not using `sls_mongodb_cfg_file`. Ensure the user has appropriate database permissions.

#### sls_mongodb.password
MongoDB password for SLS database authentication.

- **Required** (Either `sls_mongodb_cfg_file` or the `sls_mongodb` object are required to install SLS)
- Environment Variable: None
- Default: None

**Purpose**: Provides the password credential for SLS to authenticate with MongoDB. Used together with the username to establish secure database connections.

**When to use**:
- Required when manually configuring MongoDB connection (not using `sls_mongodb_cfg_file`)
- Must correspond to the password for the specified MongoDB username
- Obtain from your MongoDB deployment configuration

**Valid values**: Valid MongoDB password string

**Impact**: SLS uses this password to authenticate with MongoDB. Invalid password will cause authentication failures and prevent SLS from accessing the database.

**Related variables**:
- `sls_mongodb.username`: Username for this password
- `sls_mongodb.hosts`: MongoDB servers to authenticate against
- `sls_mongodb.certificates`: TLS certificates for secure authentication
- `sls_mongodb_cfg_file`: Alternative method to provide this information

**Note**: Part of the `sls_mongodb` object. All `sls_mongodb.*` variables must be provided together if not using `sls_mongodb_cfg_file`. Keep this password secure and do not commit to source control.

#### mas_pod_templates_dir
Local directory path containing pod template customization files for SLS.

- **Optional**
- Environment Variable: `MAS_POD_TEMPLATES_DIR`
- Default: None

**Purpose**: Allows customization of pod specifications for SLS workloads, enabling control over resource limits, node affinity, tolerations, and other Kubernetes pod settings. This is essential for production deployments with specific infrastructure requirements.

**When to use**:
- Use to set custom resource limits (CPU, memory) for SLS pods
- Use to configure node affinity or anti-affinity rules
- Use to add tolerations for tainted nodes
- Use to apply custom security contexts or service accounts
- Leave unset for default pod configurations

**Valid values**: Any valid local filesystem path containing `ibm-sls-licenseservice.yml`

**Impact**: The pod template file will be applied to the LicenseService Custom Resource under `spec.podTemplates`. Invalid templates can cause pod scheduling failures.

**Related variables**: None

**Note**: This role looks for a file named `ibm-sls-licenseservice.yml` in the specified directory. The file content should be the YAML block to insert under `podTemplates: {object}`. For examples, see the [BestEfforts reference configuration](https://github.com/ibm-mas/cli/blob/master/image/cli/mascli/templates/pod-templates/best-effort/ibm-sls-licenseservice.yml). For full documentation, refer to [Customizing Pod Templates](https://www.ibm.com/docs/en/mas-cd/continuous-delivery?topic=sls-supported-pods-workload-customization-in-suite-license-service).

### Bootstrap Variables (SLS 3.7.0 and higher)

#### entitlement_file
Local file path to the IBM license entitlement file for bootstrapping SLS.

- **Optional**
- Environment Variable: `SLS_ENTITLEMENT_FILE`
- Default: None

**Purpose**: Provides the license entitlement file that defines the MAS product licenses and token allocations available in SLS. This file is obtained from IBM and contains your license entitlements.

**When to use**:
- Use to automatically bootstrap SLS with license entitlements during installation
- Leave unset if you plan to upload license entitlements manually after SLS installation
- Required for fully automated SLS deployments

**Valid values**: Any valid local filesystem path to an IBM license entitlement file (e.g., `/home/user/licenses/entitlement.dat`)

**Impact**: When provided, SLS is automatically configured with the license entitlements from this file. Without this, you must manually upload license entitlements through the SLS UI or API after installation.

**Related variables**: None

**Note**: **Application Support: SLS 3.7.0 and higher**. The license file is obtained from IBM and contains your MAS product entitlements. Keep this file secure as it represents your license rights.


## Role Variables - Bootstrap [Partly deprecated in SLS 3.7.0]
#### bootstrap.license_file
**Deprecated in SLS 3.7.0**

Defines the License File to be used to bootstrap SLS. Don't set if you wish to setup entitlement later on. Note: this variable used to be called bootstrap.entitlement_file and defaulted to `{{mas_config_dir}}/entitlement.lic`, this is no longer the case and `SLS_LICENSE_FILE` has to be set in order to bootstrap. This is now deprecated in SLS 3.7.0. Use this only for versions up to 3.6.0.

- **Optional**
- Environment Variable: `SLS_LICENSE_FILE`
- Default: None

#### bootstrap.license_id
**Deprecated in SLS 3.7.0**

Defines the License Id to be used to bootstrap SLS. This must be set when `bootstrap.license_file` is also set and should match the licenseId from the license file. Don't set if you wish to setup entitlement later on. Note: this is now deprecated in SLS 3.7.0. Use this only for versions up to 3.6.0.

- Optional unless `bootstrap.license_file` is set
- Environment Variable: `SLS_LICENSE_ID`
- Default: None

#### bootstrap.registration_key
Defines the Registration Key to be used to bootstrap SLS. Don't set if you wish to setup entitlement later on

- **Optional**
- Environment Variable: `SLS_REGISTRATION_KEY`
- Default: None

### SLSCfg Variables

#### mas_instance_id
The instance ID of Maximo Application Suite that the SlsCfg configuration will target.

- Optional, if this or `mas_config_dir` are not set then the role will not generate a SlsCfg template
- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

#### mas_config_dir
Local directory to save the generated SlsCfg resource definition.  This can be used to manually configure a MAS instance to connect to SLS instance, or used as an input to the [suite_config](suite_config.md) role. If this or `mas_instance_id` are not set then the role will not generate a SlsCfg template.

- **Optional** (if this or `mas_config_dir` are not set then the role will not generate a SlsCfg template)
- Environment Variable: `MAS_CONFIG_DIR`
- Default Value: None

#### sls_url
The URL of the LicenseService to be called when the Maximo Application Suite is registered with SLS.

- Optional, used to instruct the role to set up MAS for an existing SLS instance.
- Environment Variable: `SLS_URL`
- Default Value: None

#### mas_license_sync_frequency
The sync frequency of user license sync cronjob between Maximo Application Suite and SLS.

- **Optional**
- Environment Variable: `MAS_LICENSE_SYNC_FREQUENCY`
- Default Value: `*/30 * * * *`

#### sls_tls_crt
The TLS CA certificate of the LicenseService to be used when the Maximo Application Suite is registered with SLS.  Takes precedence over  `sls_tls_crt_local_file_path`.

- Optional, used to instruct the role to set up MAS for an existing SLS instance.
- Environment Variable: `SLS_TLS_CERT`
- Default Value: None

#### sls_tls_crt_local_file_path
The path on the local system to a file containing the TLS CA certificate of the LicenseService to be used when the Maximo Application Suite is registered with SLS.  This variable is only used if `sls_tls_crt` has not been set.

- **Optional** (used to instruct the role to set up MAS for an existing SLS instance)
- Environment Variable: `SLS_TLS_CERT_LOCAL_FILE_PATH`
- Default Value: None

#### sls_registration_key
The Registration key of the LicenseService instance to be used when the Maximo Application Suite is registered with SLS.

- Optional
- Environment Variable: `SLS_REGISTRATION_KEY`
- Default Value: None

#### custom_labels
List of comma separated key=value pairs for setting custom labels on instance specific resources.

- **Optional**
- Environment Variable: `CUSTOM_LABELS`
- Default Value: None

#### mas_pod_templates_dir
Provide the directory where supported pod templates configuration files are defined.  This role will look for a configuration file named `ibm-mas-slscfg.yml` in the named directory.  The content of the configuration file should be the yaml block that you wish to be inserted into the SlsCfg spec under a top level `podTemplates` element, e.g. `podTemplates: {object}`.

For examples refer to the [BestEfforts reference configuration in the MAS CLI](https://github.com/ibm-mas/cli/blob/master/image/cli/mascli/templates/pod-templates/best-effort/ibm-mas-slscfg.yml), for full documentation of the supported options refer to the [Customizing Pod Templates](https://www.ibm.com/docs/en/mas-cd/continuous-delivery?topic=configuring-customizing-workloads) in the product documentation.

- **Optional**
- Environment Variable: `MAS_POD_TEMPLATES_DIR`
- Default: None

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
