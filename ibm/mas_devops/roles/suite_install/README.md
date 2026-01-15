# suite_install

This role installs Maximo Application Suite. It internally resolves the namespace based on the `mas_instance_id` as `mas-{mas_instance_id}-core`.

## Role Variables

### Basic Install

#### mas_catalog_source
Specifies the OpenShift operator catalog source containing the MAS operator subscription.

- **Optional**
- Environment Variable: `MAS_CATALOG_SOURCE`
- Default: `ibm-operator-catalog`

**Purpose**: Controls which operator catalog is used to locate and install the MAS operator. This determines where OpenShift looks for the operator images and metadata during installation.

**When to use**:
- Use default `ibm-operator-catalog` for production installations with official IBM releases
- Use `ibm-operator-catalog` for development installations as well (supports both use cases)
- Only change if directed to use a custom catalog for specific testing or airgap scenarios

**Valid values**: Any valid CatalogSource name present in the `openshift-marketplace` namespace (typically `ibm-operator-catalog`)

**Impact**: Changing this value affects which operator versions are available for installation. An invalid catalog source will cause the subscription to fail.

**Related variables**: Works with `mas_channel` to determine the specific operator version installed.

#### mas_channel
Specifies the MAS operator subscription channel, which determines the version stream you'll receive updates from.

- **Required**
- Environment Variable: `MAS_CHANNEL`
- Default: None

**Purpose**: Controls which version of MAS will be installed and which updates will be automatically applied. The channel corresponds to major.minor version releases (e.g., `8.11.x`, `9.0.x`) and determines the feature set and compatibility level of your MAS installation.

**When to use**:
- Set to the latest stable channel for new production deployments to receive the newest features
- Use specific older channels when compatibility with existing applications or dependencies requires it
- Consult the MAS compatibility matrix before selecting a channel to ensure compatibility with your applications
- Change channels only during planned upgrade windows as this triggers version updates

**Valid values**: `8.9.x`, `8.10.x`, `8.11.x`, `9.0.x` (check the IBM Operator Catalog for currently available channels)

**Impact**: The channel determines which MAS version is installed and which automatic updates are applied. Changing channels after installation will trigger an upgrade to the latest version in that channel, which may require application reconfiguration and testing.

**Related variables**: Works with `mas_catalog_source` to determine available channels.

**Note**: Once installed, changing channels requires careful planning. Review the MAS upgrade documentation before changing this value.

### Basic Configuration

#### mas_domain
Specifies the custom domain name for accessing MAS web interfaces and APIs.

- **Optional**
- Environment Variable: `MAS_DOMAIN`
- Default: None (uses cluster default subdomain)

**Purpose**: Defines the base domain used to construct all MAS URLs (e.g., admin.{mas_domain}, home.{mas_domain}). This allows you to use a custom domain instead of the default OpenShift cluster subdomain, which is important for production environments with specific DNS requirements.

**When to use**:
- Set for production environments where you need branded or corporate domain names
- Set when integrating with external DNS providers (Cloudflare, Route53, IBM CIS)
- Set when using custom SSL certificates tied to specific domains
- Leave unset for development/testing to use the default cluster subdomain automatically

**Valid values**: Any valid DNS domain name (e.g., `mas.mycompany.com`, `prod-mas.example.org`)

**Impact**: When set, MAS will use this domain for all routes and certificates. You must ensure DNS is properly configured to resolve this domain to your cluster. When not set, MAS automatically uses the cluster's default ingress subdomain.

**Related variables**:
- Used by `suite_dns` role to configure DNS entries
- Affects certificate generation when using `mas_cluster_issuer`
- Must align with `mas_routing_mode` configuration

#### mas_instance_id
Unique identifier for this MAS installation within the cluster.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

**Purpose**: Provides a unique identifier that distinguishes this MAS installation from others that may exist in the same cluster. This ID is used to generate namespace names, resource names, and configuration identifiers throughout the installation.

**When to use**:
- Always required for any MAS installation
- Use short, descriptive names (e.g., `prod`, `dev`, `test`, `inst1`)
- Must be unique within the cluster if running multiple MAS instances
- Cannot be changed after installation without reinstalling

**Valid values**: Lowercase alphanumeric string, 3-12 characters, starting with a letter (e.g., `prod`, `dev01`, `mastest`)

**Impact**: This ID becomes part of the core namespace name (`mas-{mas_instance_id}-core`) and is embedded in many resource names. It cannot be changed after installation. All MAS configurations and applications will reference this instance ID.

**Related variables**:
- Used by all MAS configuration roles to target the correct instance
- Referenced in application installation roles
- Used in backup/restore operations to identify the instance

**Note**: Choose carefully as this cannot be changed after installation. Use consistent naming across environments (e.g., `dev`, `test`, `prod`).

#### mas_entitlement_key
IBM entitlement key for authenticating access to IBM Container Registry.

- **Required**
- Environment Variable: `MAS_ENTITLEMENT_KEY`
- Default: Value of `IBM_ENTITLEMENT_KEY` if set

**Purpose**: Provides authentication credentials to pull MAS container images from IBM's entitled registry. This key is tied to your IBM Cloud account and product entitlements, proving you have the right to use MAS software.

**When to use**:
- Required for all production installations using official IBM releases
- Obtain from IBM Container Library at https://myibm.ibm.com/products-services/containerlibrary
- For development builds on Artifactory, use your Artifactory API key instead
- Key must be valid and have active MAS entitlements

**Valid values**:
- IBM entitlement key string (typically starts with "eyJ...")
- Must be a valid, non-expired key with MAS product entitlements
- For development: Artifactory API key

**Impact**: Invalid or expired keys will cause image pull failures during installation. The key is stored in a Kubernetes secret and used to create image pull secrets for all MAS pods. Without a valid key, the installation cannot proceed.

**Related variables**:
- Falls back to `IBM_ENTITLEMENT_KEY` environment variable if not set
- Used with `mas_entitlement_username` for registry authentication
- Related to `mas_icr_cp` and `mas_icr_cpopen` registry settings

**Note**: Keep this key secure. Do not commit it to source control. Use environment variables or secure secret management.

#### mas_config_dir
Local directory path containing additional Kubernetes configuration files to apply during MAS installation.

- **Optional**
- Environment Variable: `MAS_CONFIG_DIR`
- Default: None

**Purpose**: Allows you to provide custom Kubernetes resources (YAML files) that will be automatically applied to the cluster during MAS installation. This enables advanced configuration scenarios and customization beyond the standard role variables.

**When to use**:
- Use to apply MAS configuration resources (MongoCfg, BASCfg, JdbcCfg, etc.) generated by other roles
- Use to apply custom ConfigMaps, Secrets, or other Kubernetes resources
- Use to pre-configure MAS settings before the suite becomes fully operational
- Leave unset if you plan to apply configurations manually after installation

**Valid values**: Any valid local filesystem path (e.g., `/home/user/masconfig`, `~/mas-configs`, `./config`)

**Impact**: All `*.yaml` and `*.yml` files in this directory will be applied to the cluster using `oc apply`. Files are processed in alphabetical order. Invalid YAML or resources will cause the role to fail.

**Related variables**:
- Used by `mongodb`, `db2`, `sls` and other dependency roles to output configuration files
- Used by `suite_config` role to apply configurations
- Must be set if using generated configuration files from dependency roles

**Note**: Ensure all files in this directory are valid Kubernetes resources. The role does not validate file contents before applying.

### Advanced Configuration

#### mas_annotations
Comma-separated list of key=value annotations to apply to all MAS resources.

- **Optional**
- Environment Variable: `MAS_ANNOTATIONS`
- Default: None

**Purpose**: Adds Kubernetes annotations to all resources created by the MAS operator. Annotations are used to attach metadata that can control operator behavior, enable specific features, or provide information to other tools and operators.

**When to use**:
- Set to `mas.ibm.com/operationalMode=nonproduction` for non-production environments (reduces resource requirements)
- Use to add custom metadata for organizational tracking or automation
- Use to enable specific MAS features controlled by annotations
- Leave unset for default production configuration

**Valid values**: Comma-separated list of `key=value` pairs (e.g., `key1=value1,key2=value2`)

**Impact**: Annotations affect how the MAS operator configures resources. The `operationalMode=nonproduction` annotation significantly reduces CPU and memory requirements but is not suitable for production workloads.

**Related variables**: Works alongside `custom_labels` for resource metadata.

**Note**: The `operationalMode=nonproduction` annotation should only be used in development/test environments. It reduces resource allocations below production requirements.

#### mas_img_pull_policy
Controls the image pull policy for all MAS container images.

- **Optional**
- Environment Variable: `MAS_IMG_PULL_POLICY`
- Default: None (uses operator default)

**Purpose**: Determines when Kubernetes will pull container images from the registry. This affects deployment speed, network usage, and whether you get the latest image updates.

**When to use**:
- Use `Always` in development to ensure latest images are pulled on every pod restart
- Use `IfNotPresent` in production to reduce network traffic and improve pod startup time
- Use `Never` in airgap environments where images are pre-loaded
- Leave unset to use the operator's default policy (typically `IfNotPresent`)

**Valid values**: `Always`, `IfNotPresent`, `Never`

**Impact**:
- `Always`: Slower pod starts, higher network usage, always gets latest image
- `IfNotPresent`: Faster pod starts, uses cached images, may miss updates
- `Never`: Fastest starts, requires images pre-loaded, fails if image not present

**Related variables**: Affects all images pulled by MAS operator and workloads.

#### custom_labels
Comma-separated list of key=value labels to apply to all MAS resources.

- **Optional**
- Environment Variable: `CUSTOM_LABELS`
- Default: None

**Purpose**: Adds Kubernetes labels to all resources created by the MAS operator. Labels are used for resource organization, selection, and filtering. They enable you to query, group, and manage MAS resources using standard Kubernetes tools.

**When to use**:
- Use to add organizational metadata (e.g., `cost-center=engineering`, `environment=production`)
- Use to enable resource tracking and cost allocation
- Use to support custom automation or monitoring tools
- Use to comply with organizational labeling standards

**Valid values**: Comma-separated list of `key=value` pairs (e.g., `env=prod,team=platform,cost-center=12345`)

**Impact**: Labels are applied to all MAS resources and can be used for filtering with `oc get` commands, monitoring queries, and automation scripts. Labels do not affect MAS functionality but are essential for resource management.

**Related variables**: Works alongside `mas_annotations` for resource metadata.

#### mas_manual_cert_mgmt
Enables manual certificate management mode, disabling automatic certificate generation.

- **Optional**
- Environment Variable: `MAS_MANUAL_CERT_MGMT`
- Default: `false`

**Purpose**: Controls whether MAS uses automatic certificate management via cert-manager or requires manually provided certificates. This is critical for environments with specific certificate requirements or where cert-manager cannot be used.

**When to use**:
- Set to `true` when you must use certificates from a specific Certificate Authority
- Set to `true` in environments where cert-manager is not available or not permitted
- Set to `true` when organizational policy requires manual certificate management
- Leave as `false` (default) to use automatic certificate management with cert-manager

**Valid values**: `true`, `false`

**Impact**: When `true`, you must manually create and manage all certificates required by MAS. The `suite_dns` role will not configure automatic certificate issuers. You are responsible for certificate renewal before expiration. When `false`, cert-manager automatically generates and renews certificates.

**Related variables**:
- When `false`: Requires `mas_cluster_issuer` to be set for automatic certificate generation
- Affects behavior of `suite_dns` role
- Related to `mas_certificate_duration` and `mas_certificate_renew_before`

**Note**: Manual certificate management requires significant operational overhead. Use automatic management unless you have specific requirements.

#### mas_routing_mode
Defines the URL routing strategy for MAS applications and services.

- **Optional**
- Environment Variable: `MAS_ROUTING_MODE`
- Default: `subdomain`

**Purpose**: Controls how MAS constructs URLs for different applications and services. This affects the URL structure users see and how DNS must be configured.

**When to use**:
- Use `subdomain` (default) for cleaner URLs and better DNS organization (e.g., `admin.mas.example.com`, `home.mas.example.com`)
- Use `path` when subdomain routing is not possible due to DNS or certificate limitations (e.g., `mas.example.com/admin`, `mas.example.com/home`)
- Consider DNS provider capabilities and certificate management when choosing

**Valid values**: `subdomain`, `path`

**Impact**:
- `subdomain`: Creates separate DNS entries for each service (requires wildcard DNS or multiple DNS entries)
- `path`: Uses single DNS entry with path-based routing (simpler DNS, more complex URL structure)
- Cannot be changed after installation without reinstalling

**Related variables**:
- Affects DNS configuration in `suite_dns` role
- Impacts certificate requirements (wildcard vs single certificate)
- Must align with `mas_domain` configuration

**Note**: Choose carefully as this cannot be changed after installation. Subdomain routing is recommended for production environments.

#### mas_trust_default_cas
Controls whether default system Certificate Authorities are included in MAS trust stores.

- **Optional**
- Environment Variable: `MAS_TRUST_DEFAULT_CAS`
- Default: `true`

**Purpose**: Determines if MAS will trust certificates signed by standard public Certificate Authorities (like Let's Encrypt, DigiCert, etc.) in addition to any custom CAs you configure. This affects MAS's ability to connect to external services using standard SSL certificates.

**When to use**:
- Leave as `true` (default) for most installations to enable connections to public services
- Set to `false` only in highly restricted environments where you want to explicitly control all trusted CAs
- Set to `false` in airgap environments where external connections are not permitted

**Valid values**: `true`, `false`

**Impact**: When `true`, MAS can connect to any service using certificates from well-known public CAs. When `false`, MAS will only trust explicitly configured custom CAs, which may break connections to external services.

**Related variables**: Works with custom CA configuration in MAS.

**Note**: Only available in MAS 8.11 and above. Has no effect in earlier versions.

#### mas_pod_templates_dir
Directory containing pod template customization files for MAS workloads.

- **Optional**
- Environment Variable: `MAS_POD_TEMPLATES_DIR`
- Default: None

**Purpose**: Allows you to customize resource requests, limits, node selectors, tolerations, and other pod-level configurations for MAS workloads. This enables you to optimize MAS for your specific cluster configuration and resource availability.

**When to use**:
- Use to apply resource constraints in resource-limited environments
- Use to configure node affinity for specific hardware (e.g., GPU nodes)
- Use to apply tolerations for tainted nodes
- Use to implement best-effort or guaranteed QoS classes
- Leave unset to use default MAS pod configurations

**Valid values**: Path to directory containing pod template YAML files:
- `ibm-mas-suite.yml` - Core suite workloads
- `ibm-mas-coreidp.yml` - Identity provider workloads
- `ibm-data-dictionary-assetdatadictionary.yml` - Data dictionary workloads

**Impact**: Pod templates directly affect resource allocation, scheduling, and performance of MAS workloads. Incorrect configurations can cause pods to fail scheduling or perform poorly.

**Related variables**: Similar pod template configuration available in other roles (SLS, applications).

**Note**: See [MAS CLI pod templates](https://github.com/ibm-mas/cli/blob/master/image/cli/mascli/templates/pod-templates/best-effort/ibm-mas-suite.yml) for examples and [product documentation](https://www.ibm.com/docs/en/mas-cd/continuous-delivery?topic=configuring-customizing-workloads) for full details.

### Certificate Management

#### mas_cluster_issuer
Name of the cert-manager ClusterIssuer to use for automatic certificate generation.

- **Optional**
- Environment Variable: `MAS_CLUSTER_ISSUER`
- Default: None

**Purpose**: Specifies which cert-manager ClusterIssuer will generate and manage SSL/TLS certificates for MAS. The ClusterIssuer defines the Certificate Authority and authentication method used for certificate issuance.

**When to use**:
- Required when `mas_manual_cert_mgmt` is `false` (automatic certificate management)
- Set to the ClusterIssuer created by `suite_dns` role (e.g., `{mas_instance_id}-cloudflare-le-prod`)
- Set to a custom ClusterIssuer if you have specific certificate requirements
- Leave unset only when using manual certificate management

**Valid values**: Name of any valid ClusterIssuer resource in the cluster (e.g., `prod-le-issuer`, `{mas_instance_id}-cloudflare-le-prod`)

**Impact**: The specified ClusterIssuer will be used to generate all MAS certificates. If the ClusterIssuer is not properly configured or lacks necessary credentials, certificate generation will fail and MAS will not be accessible.

**Related variables**:
- Only used when `mas_manual_cert_mgmt` is `false`
- Created by `suite_dns` role for Let's Encrypt integration
- Works with `mas_certificate_duration` and `mas_certificate_renew_before`

**Note**: Ensure the ClusterIssuer is created and functional before installing MAS. Test certificate generation with a test Certificate resource first.

#### mas_certificate_duration
Specifies the validity period for MAS certificates.

- **Optional**
- Environment Variable: `MAS_CERTIFICATE_DURATION`
- Default: `8760h0m0s` (1 year)

**Purpose**: Defines how long certificates will be valid before they expire. This affects how often certificates need to be renewed and the security posture of your installation.

**When to use**:
- Use default (8760h = 1 year) for most installations
- Reduce for higher security environments requiring frequent rotation
- Increase only if certificate renewal is problematic in your environment
- Must be longer than `mas_certificate_renew_before`

**Valid values**: Duration string in format `{hours}h{minutes}m{seconds}s` (e.g., `8760h0m0s`, `2160h0m0s`, `17520h0m0s`)

**Impact**: Shorter durations increase security but require more frequent renewals. Longer durations reduce renewal frequency but increase risk if certificates are compromised. Cert-manager will automatically renew certificates before expiration.

**Related variables**:
- Must be greater than `mas_certificate_renew_before`
- Only applies when using automatic certificate management
- Affects all MAS certificates

#### mas_certificate_renew_before
Specifies when to renew certificates before they expire.

- **Optional**
- Environment Variable: `MAS_CERTIFICATE_RENEW_BEFORE`
- Default: `720h0m0s` (30 days)

**Purpose**: Defines the renewal window - how far in advance cert-manager will renew certificates before they expire. This ensures certificates are renewed with sufficient time to handle any renewal issues.

**When to use**:
- Use default (720h = 30 days) for most installations
- Increase in environments where certificate renewal may be slow or problematic
- Decrease only if you need to minimize the number of certificate changes
- Must be shorter than `mas_certificate_duration`

**Valid values**: Duration string in format `{hours}h{minutes}m{seconds}s` (e.g., `720h0m0s`, `1440h0m0s`, `168h0m0s`)

**Impact**: Longer renewal windows provide more time to resolve renewal issues but result in more frequent certificate changes. Shorter windows reduce certificate churn but increase risk of expiration if renewal fails.

**Related variables**:
- Must be less than `mas_certificate_duration`
- Only applies when using automatic certificate management
- Affects all MAS certificates

**Note**: Ensure this value provides adequate time to detect and resolve certificate renewal issues before expiration.

### Superuser Account

The MAS Superuser account username and password can be customized during the install by setting **both** of these variables.

#### mas_superuser_username
Custom username for the MAS superuser administrator account.

- **Optional**
- Environment Variable: `MAS_SUPERUSER_USERNAME`
- Default: None (uses MAS default superuser)

**Purpose**: Allows you to set a custom username for the MAS superuser account instead of using the default. The superuser has full administrative access to all MAS functions and applications.

**When to use**:
- Set both username and password to customize the superuser account
- Use in environments with specific account naming requirements
- Leave unset to use the default superuser account
- Must be set together with `mas_superuser_password`

**Valid values**: Any valid username string (alphanumeric, may include underscores and hyphens)

**Impact**: When set (along with password), creates a superuser account with the specified username. If only one of username/password is set, both are ignored and default account is used.

**Related variables**: Must be set together with `mas_superuser_password` to take effect.

**Note**: Both username and password must be set for customization to take effect. Setting only one has no effect.

#### mas_superuser_password
Custom password for the MAS superuser administrator account.

- **Optional**
- Environment Variable: `MAS_SUPERUSER_PASSWORD`
- Default: None (uses auto-generated password)

**Purpose**: Allows you to set a custom password for the MAS superuser account instead of using the auto-generated default. This enables you to control the initial superuser credentials.

**When to use**:
- Set both username and password to customize the superuser account
- Use when you need to know the superuser password in advance
- Use to comply with organizational password policies
- Must be set together with `mas_superuser_username`

**Valid values**: Any string meeting MAS password requirements (minimum length, complexity requirements)

**Impact**: When set (along with username), creates a superuser account with the specified password. If only one of username/password is set, both are ignored and default account is used with auto-generated password.

**Related variables**: Must be set together with `mas_superuser_username` to take effect.

**Note**: Both username and password must be set for customization to take effect. Keep the password secure and do not commit to source control.

### Developer Mode

#### artifactory_username
Username for authenticating to Artifactory for development builds.

- **Optional**
- Environment Variable: `ARTIFACTORY_USERNAME`
- Default: None

**Purpose**: Provides authentication credentials for accessing development builds of MAS stored in Artifactory. This is only used for internal development and testing, not for production installations.

**When to use**:
- Required only when installing development builds from Artifactory
- Not needed for production installations using IBM Container Registry
- Use your IBM w3Id username for Artifactory access
- Must be set together with `artifactory_token`

**Valid values**: Your IBM w3Id username

**Impact**: Used to create image pull secrets for accessing Artifactory registries. Without valid credentials, development image pulls will fail.

**Related variables**:
- Must be set with `artifactory_token`
- Used with `mas_icr_cp` and `mas_icr_cpopen` when pointing to Artifactory
- Related to `mas_entitlement_username` for registry authentication

**Note**: Only for development use. Production installations should use IBM Container Registry with entitlement keys.

#### artifactory_token
API token for authenticating to Artifactory for development builds.

- **Optional**
- Environment Variable: `ARTIFACTORY_TOKEN`
- Default: None

**Purpose**: Provides authentication token for accessing development builds of MAS stored in Artifactory. This is only used for internal development and testing, not for production installations.

**When to use**:
- Required only when installing development builds from Artifactory
- Not needed for production installations using IBM Container Registry
- Use your Artifactory API key
- Must be set together with `artifactory_username`

**Valid values**: Your Artifactory API key/token

**Impact**: Used to create image pull secrets for accessing Artifactory registries. Without valid credentials, development image pulls will fail.

**Related variables**:
- Must be set with `artifactory_username`
- Used with `mas_icr_cp` and `mas_icr_cpopen` when pointing to Artifactory
- Can be used as `mas_entitlement_key` for development builds

**Note**: Only for development use. Keep tokens secure. Production installations should use IBM Container Registry with entitlement keys.

## Example Playbook

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: "inst1"
    mas_config_dir: "/home/david/masconfig"
    mas_entitlement_key: "{{ lookup('env', 'IBM_ENTITLEMENT_KEY') }}"

  roles:
    - ibm.mas_devops.suite_install
    - ibm.mas_devops.suite_config
    - ibm.mas_devops.suite_verify
```

## License

EPL-2.0
