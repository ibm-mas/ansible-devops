# suite_certs

This role manages TLS certificates for Maximo Application Suite core platform and applications. It processes certificate files organized in a directory structure and creates TLS secrets in the appropriate namespaces. The role supports manual certificate management and optional integration with IBM Cloud Internet Services (CIS) for DNS management.

!!! important "Certificate Directory Structure"
    Certificates must be organized in subdirectories named after the MAS component (`core`, `monitor`, `manage`, `iot`, etc.). Each subdirectory must contain three mandatory files: `tls.crt`, `tls.key`, and `ca.crt`.

## What This Role Does

- Iterates through certificate subdirectories in `$MAS_CONFIG_DIR/certs`
- Validates presence of required certificate files (`tls.crt`, `tls.key`, `ca.crt`)
- Creates TLS secrets in appropriate MAS namespaces
- Optionally manages DNS CNAME records in IBM Cloud Internet Services
- Supports GitOps mode for generating configurations without applying them

## Certificate Directory Structure

### Required Structure
```plaintext
$MAS_CONFIG_DIR/certs/
├── core/
│   ├── tls.crt
│   ├── tls.key
│   └── ca.crt
├── monitor/
│   ├── tls.crt
│   ├── tls.key
│   └── ca.crt
├── manage/
│   ├── tls.crt
│   ├── tls.key
│   └── ca.crt
└── <app>/
    ├── tls.crt
    ├── tls.key
    └── ca.crt
```

### Supported Applications
- `core` - MAS core platform
- `iot` - IoT application
- `monitor` - Monitor application
- `manage` - Manage application
- `health` - Health application
- `predict` - Predict application
- `assist` - Assist application
- `optimizer` - Optimizer application
- `visualinspection` - Visual Inspection application
- `facilities` - Facilities application
- `add` - Add application
- `arcgis` - ArcGIS integration

!!! warning
    All three certificate files (`tls.crt`, `tls.key`, `ca.crt`) are **mandatory** in each subdirectory. The role will fail if a subdirectory is empty or missing any required file.

!!! note "Secret Names"
    TLS secret names for each application are defined in `suite_certs/defaults/main.yml`. Changes to secret names or adding new applications requires updating this file.

## Role Variables - General

### mas_instance_id
MAS instance identifier for certificate management.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

**Purpose**: Identifies which MAS instance the certificates are for. Used to construct namespace names and secret names.

**When to use**:
- Always required for certificate management
- Must match the instance ID from MAS installation
- Used in namespace and secret name construction

**Valid values**: Lowercase alphanumeric string, 3-12 characters (e.g., `prod`, `dev`, `masinst1`)

**Impact**: Determines target namespaces for certificate secrets. Namespace format is `mas-{instance_id}-{app}` (e.g., `mas-prod-core`, `mas-prod-monitor`).

**Related variables**:
- `mas_config_dir`: Root directory containing certificate subdirectories
- `mas_workspace_id`: Required for workspace-specific apps (manage, health, facilities)

**Note**: The instance ID is used to construct both namespace names and TLS secret names according to MAS naming conventions.

### mas_manual_cert_mgmt
Enable manual certificate management mode.

- **Optional**
- Environment Variable: `MAS_MANUAL_CERT_MGMT`
- Default: `false`

**Purpose**: Enables manual certificate management mode, allowing you to provide custom certificates instead of using cert-manager generated certificates.

**When to use**:
- Set to `true` when using custom/purchased certificates
- Required for environments without cert-manager
- Use when corporate policy requires specific certificate authorities
- Necessary for custom domain certificates

**Valid values**: `true`, `false`

**Impact**:
- `true`: Uses certificates from `$MAS_CONFIG_DIR/certs` directories
- `false`: Relies on cert-manager for automatic certificate generation (default)

**Related variables**:
- `mas_config_dir`: Directory containing certificate files
- `dns_provider`: Optional DNS management integration

**Note**: When enabled, you must provide all required certificate files in the correct directory structure. This mode is essential for production environments with specific certificate requirements.

### mas_config_dir
Configuration directory path.

- **Required**
- Environment Variable: `MAS_CONFIG_DIR`
- Default: None

**Purpose**: Specifies the root directory containing the `certs` subdirectory with certificate files organized by application.

**When to use**:
- Always required when using manual certificate management
- Should point to a directory containing a `certs` subdirectory
- Typically organized by instance ID

**Valid values**: Valid local filesystem path (e.g., `/home/user/masconfig`, `~/masconfig/inst1`)

**Impact**: The role looks for certificates in `$MAS_CONFIG_DIR/certs/{app}/` directories. All certificate processing is relative to this path.

**Related variables**:
- `mas_instance_id`: Instance these certificates are for
- `mas_manual_cert_mgmt`: Must be enabled to use certificates

**Note**: Organize by instance for clarity (e.g., `/masconfig/inst1/certs/`, `/masconfig/inst2/certs/`). The `certs` subdirectory is automatically appended to this path.

### gitops
Enable GitOps mode (generate only, no apply).

- **Optional**
- Environment Variable: `GITOPS`
- Default: `false`

**Purpose**: When enabled, generates certificate secret configurations without applying them to the cluster. Useful for GitOps workflows where configurations are committed to Git and applied separately.

**When to use**:
- Set to `true` for GitOps/declarative workflows
- Use when configurations should be reviewed before application
- Helpful for version-controlled infrastructure
- Required for environments with strict change control

**Valid values**: `true`, `false`

**Impact**:
- `true`: Generates YAML configurations but doesn't create resources on cluster
- `false`: Generates and applies configurations directly to cluster (default)

**Related variables**:
- `mas_config_dir`: Where generated configurations are saved

**Note**: In GitOps mode, generated YAML files can be committed to Git and applied through your GitOps tooling (ArgoCD, Flux, etc.).

## Role Variables - CIS DNS Provider (Optional)

Optional variables for users managing DNS with IBM Cloud Internet Services. When configured, this role automatically creates or updates CNAME records for MAS routes in your CIS instance.

### dns_provider
DNS provider type.

- **Optional**
- Environment Variable: `DNS_PROVIDER`
- Default: None

**Purpose**: Specifies the DNS provider for automatic DNS record management. Currently only supports IBM Cloud Internet Services (CIS).

**When to use**:
- Set to `cis` when using IBM Cloud Internet Services for DNS
- Leave unset if not using automatic DNS management
- Required for automatic CNAME creation

**Valid values**: `cis` (only supported value), or empty/unset

**Impact**: When set to `cis`, enables automatic CNAME record creation in IBM Cloud Internet Services for MAS routes.

**Related variables**:
- `cis_crn`: Required when this is `cis`
- `cis_apikey`: Required when this is `cis`
- `cis_subdomain`: Required when this is `cis`
- `mas_workspace_id`: Required when this is `cis`

**Note**: Any value other than `cis` or empty will result in an error. This feature is optional and only needed if you want automatic DNS management.

### mas_workspace_id
Workspace identifier for DNS records.

- **Required** (when `dns_provider=cis`)
- Environment Variable: `MAS_WORKSPACE_ID`
- Default: None

**Purpose**: Specifies the workspace ID used in CNAME record construction when using CIS as DNS provider. Required for workspace-specific applications.

**When to use**:
- Required when `dns_provider=cis`
- Used for workspace-specific apps (manage, health, facilities)
- Part of the DNS hostname construction

**Valid values**: Lowercase alphanumeric string, typically 3-12 characters (e.g., `prod`, `dev`, `masdev`)

**Impact**: Used to construct DNS CNAME records for workspace-specific applications. Format: `{workspace_id}.{subdomain}.{domain}`

**Related variables**:
- `dns_provider`: Must be `cis`
- `cis_subdomain`: Combined with workspace ID for DNS names
- `mas_instance_id`: Instance containing this workspace

**Note**: Only needed when using CIS DNS integration. Not required for basic certificate management.

### cis_crn
IBM Cloud Internet Services CRN.

- **Required** (when `dns_provider=cis`)
- Environment Variable: `CIS_CRN`
- Default: None

**Purpose**: Provides the Cloud Resource Name (CRN) that uniquely identifies your CIS instance in IBM Cloud. Used for API authentication and resource targeting.

**When to use**:
- Required when `dns_provider=cis`
- Found in your CIS instance details page in IBM Cloud
- Used to target the correct CIS instance

**Valid values**: Valid IBM Cloud CRN string (format: `crn:v1:bluemix:public:internet-svcs:...`)

**Impact**: Identifies which CIS instance to manage DNS records in. All CNAME operations target this CIS instance.

**Related variables**:
- `dns_provider`: Must be `cis`
- `cis_apikey`: Required for authentication
- `cis_subdomain`: Domain managed in this CIS instance

**Note**: **SECURITY** - The CRN is not sensitive but should be kept with your infrastructure configuration. Find it in IBM Cloud Console under your CIS instance details.

### cis_apikey
IBM Cloud API key for CIS access.

- **Required** (when `dns_provider=cis`)
- Environment Variable: `CIS_APIKEY`
- Default: None

**Purpose**: Provides IBM Cloud API key for authenticating with CIS to manage DNS records.

**When to use**:
- Required when `dns_provider=cis`
- Must have permissions to manage DNS in the CIS instance
- Used for all CIS API operations

**Valid values**: Valid IBM Cloud API key string

**Impact**: Used to authenticate with IBM Cloud and manage DNS records in the specified CIS instance. Must have appropriate IAM permissions.

**Related variables**:
- `dns_provider`: Must be `cis`
- `cis_crn`: CIS instance to manage
- `cis_subdomain`: Domain to manage records in

**Note**: **SECURITY** - API key should be kept secure and not committed to version control. Requires IAM permissions for DNS management in CIS. Obtain from IBM Cloud IAM.

### cis_subdomain
CIS subdomain for CNAME records.

- **Required** (when `dns_provider=cis`)
- Environment Variable: `CIS_SUBDOMAIN`
- Default: None

**Purpose**: Specifies the subdomain within your CIS-managed domain where MAS CNAME records will be created.

**When to use**:
- Required when `dns_provider=cis`
- Should match your MAS deployment subdomain
- Part of the full DNS hostname

**Valid values**: Valid subdomain string (e.g., `mas`, `maximo`, `apps`)

**Impact**: Used to construct full DNS names for MAS routes. Format: `{component}.{subdomain}.{domain}` or `{workspace}.{subdomain}.{domain}`

**Related variables**:
- `dns_provider`: Must be `cis`
- `mas_workspace_id`: Combined with subdomain for workspace apps
- `cis_crn`: CIS instance managing this subdomain

**Note**: The subdomain should already exist in your CIS domain. This role creates CNAME records within the subdomain, not the subdomain itself.

### cis_proxy
Enable CIS proxy for CNAME records.

- **Optional**
- Environment Variable: `CIS_PROXY`
- Default: `false`

**Purpose**: Enables IBM Cloud Internet Services proxy mode for created CNAME records, allowing CIS security features (WAF, DDoS protection, rate limiting) to be applied.

**When to use**:
- Set to `true` to enable CIS security features
- Use for production environments requiring additional protection
- Only applies when `dns_provider=cis`
- Requires CIS security features to be configured

**Valid values**: `true`, `false`

**Impact**:
- `true`: CNAME records are proxied through CIS, enabling security features
- `false`: CNAME records are DNS-only (default)

**Related variables**:
- `dns_provider`: Must be `cis`
- `cis_crn`: CIS instance with security features

**Note**: When enabled, traffic flows through CIS infrastructure, allowing WAF rules, DDoS protection, and other security features to be applied. May add latency but provides additional security layers.

## Example Playbook

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_manual_cert_mgmt: true
    mas_config_dir: /home/user/masconfig
  roles:
    - ibm.mas_devops.suite_certs
```

## License

EPL-2.0
