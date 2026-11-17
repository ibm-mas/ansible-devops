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

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`mas_instance_id`](#mas_instance_id) | Yes | None |
| [`mas_manual_cert_mgmt`](#mas_manual_cert_mgmt) | No | `false` |
| [`mas_config_dir`](#mas_config_dir) | Yes | None |
| [`mas_channel`](#mas_channel) | No | None |
| [`gitops`](#gitops) | No | `false` |
| [`dns_provider`](#dns_provider) | No | None |
| [`mas_routing_mode`](#mas_routing_mode) | No | None |
| [`mas_workspace_id`](#mas_workspace_id) | Conditional | None |
| [`cis_crn`](#cis_crn) | Conditional | None |
| [`cis_apikey`](#cis_apikey) | Conditional | None |
| [`cis_subdomain`](#cis_subdomain) | Conditional | None |
| [`cis_proxy`](#cis_proxy) | No | `false` |

The CIS variables (`mas_workspace_id`, `cis_crn`, `cis_apikey`, and `cis_subdomain`) are only required when `dns_provider` is set to `cis`.

### Certificate Management

#### mas_instance_id

MAS instance identifier the certificates belong to — a lowercase alphanumeric string of 3-12 characters (for example `prod`, `dev`, or `masinst1`).

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

Used to construct both the target namespaces (`mas-{instance_id}-{app}`, e.g. `mas-prod-core` or `mas-prod-monitor`) and the TLS secret names, following MAS naming conventions.

#### mas_manual_cert_mgmt

Enable manual certificate management mode, providing your own certificates instead of relying on cert-manager-generated ones — `true` or `false`.

- **Optional**
- Environment Variable: `MAS_MANUAL_CERT_MGMT`
- Default: `false`

When `true`, the role processes the certificate files under `$MAS_CONFIG_DIR/certs`. Enable this for custom or purchased certificates, environments without cert-manager, custom domains, or corporate policies requiring a specific certificate authority.

#### mas_config_dir

Root configuration directory containing the `certs` subdirectory with certificates organized by MAS component — a valid local filesystem path such as `/home/user/masconfig` or `~/masconfig/inst1`.

- **Required**
- Environment Variable: `MAS_CONFIG_DIR`
- Default: None

All certificate processing is relative to this path: certificates are read from `$MAS_CONFIG_DIR/certs/{app}/`, and in GitOps mode generated YAML is written to `$MAS_CONFIG_DIR/app/certs/{app}/`. The `certs` subdirectory is appended automatically (see `mas_suite_certs_dir` in the role defaults).

#### mas_channel

MAS channel (version) of the target instance, for example `9.1.x` or `9.2.x` — used to select version-appropriate naming conventions.

- **Optional**
- Environment Variable: `MAS_CHANNEL`
- Default: None

When set, the role detects whether the instance is running MAS earlier than 9.2 and adjusts the generated configuration accordingly; when unset, MAS earlier than 9.2 is assumed.

#### gitops

Generate the certificate secret configurations without applying them to the cluster — `true` or `false`.

- **Optional**
- Environment Variable: `GITOPS`
- Default: `false`

When `true`, generated YAML files can be committed to Git and applied through your GitOps tooling (ArgoCD, Flux, etc.); when `false`, resources are created directly on the cluster.

### CIS DNS Provider

Optional variables for users managing DNS with IBM Cloud Internet Services. When configured, this role automatically creates or updates CNAME records for MAS routes in your CIS instance.

#### dns_provider

DNS provider for automatic DNS record management — `cis` (IBM Cloud Internet Services) is the only supported value.

- **Optional**
- Environment Variable: `DNS_PROVIDER`
- Default: None

When set to `cis`, the role creates or updates CNAME records for MAS routes in your CIS instance. Leave unset when not using automatic DNS management; any value other than `cis` or empty is not supported.

#### mas_routing_mode

MAS routing mode controlling the shape of the DNS records created in CIS — `subdomain` (each MAS component gets its own subdomain) or `path` (components share a single hostname with path-based routing).

- **Optional**
- Environment Variable: `MAS_ROUTING_MODE`
- Default: None (treated as `subdomain`)

Only applies when `dns_provider` is `cis`.

#### mas_workspace_id

MAS workspace identifier used when constructing DNS CNAME records for workspace-scoped applications — a lowercase alphanumeric string, typically 3-12 characters (for example `prod`, `dev`, or `masdev`).

- **Required** when `dns_provider` is `cis`
- Environment Variable: `MAS_WORKSPACE_ID`
- Default: None

Also used in the TLS secret names for the workspace-scoped applications (`manage`, `health`, `facilities`). DNS names for workspace applications take the form `{workspace_id}.{subdomain}.{domain}`.

#### cis_crn

Cloud Resource Name (CRN) identifying the CIS instance in IBM Cloud where DNS records are managed — format `crn:v1:bluemix:public:internet-svcs:...`.

- **Required** when `dns_provider` is `cis`
- Environment Variable: `CIS_CRN`
- Default: None

Find it in the IBM Cloud console under your CIS instance details. All CNAME operations target this CIS instance.

#### cis_apikey

IBM Cloud API key used to authenticate with CIS — must have IAM permissions to manage DNS in the target CIS instance.

- **Required** when `dns_provider` is `cis`
- Environment Variable: `CIS_APIKEY`
- Default: None

!!! warning
    The API key grants access to your IBM Cloud account — keep it secure, obtain it from IBM Cloud IAM, and never commit it to version control.

#### cis_subdomain

Subdomain within your CIS-managed domain where MAS CNAME records are created — for example `mas`, `maximo`, or `apps`.

- **Required** when `dns_provider` is `cis`
- Environment Variable: `CIS_SUBDOMAIN`
- Default: None

The subdomain must already exist in your CIS domain; this role creates CNAME records within it, not the subdomain itself. Full DNS names take the form `{component}.{subdomain}.{domain}` or `{workspace}.{subdomain}.{domain}`.

#### cis_proxy

Enable CIS proxy mode for the created CNAME records — `true` or `false`.

- **Optional**
- Environment Variable: `CIS_PROXY`
- Default: `false`

When `true`, traffic flows through CIS infrastructure so security features such as WAF rules, DDoS protection, and rate limiting can be applied, at the cost of some added latency; when `false`, records are DNS-only. Only applies when `dns_provider` is `cis`.

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
