# suite_install

This role installs Maximo Application Suite. It internally resolves the namespace based on the `mas_instance_id` as `mas-{mas_instance_id}-core`.

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`mas_catalog_source`](#mas_catalog_source) | No | `ibm-operator-catalog` |
| [`mas_channel`](#mas_channel) | Yes | None |
| [`mas_domain`](#mas_domain) | No | None |
| [`mas_instance_id`](#mas_instance_id) | Yes | None |
| [`mas_entitlement_key`](#mas_entitlement_key) | Yes | Value of `IBM_ENTITLEMENT_KEY` |
| [`mas_config_dir`](#mas_config_dir) | No | None |
| [`mas_annotations`](#mas_annotations) | No | None |
| [`mas_img_pull_policy`](#mas_img_pull_policy) | No | None |
| [`custom_labels`](#custom_labels) | No | None |
| [`mas_manual_cert_mgmt`](#mas_manual_cert_mgmt) | No | `false` |
| [`mas_routing_mode`](#mas_routing_mode) | No | None |
| [`mas_manual_route_mgmt`](#mas_manual_route_mgmt) | No | `false` |
| [`mas_trust_default_cas`](#mas_trust_default_cas) | No | None |
| [`mas_pod_templates_dir`](#mas_pod_templates_dir) | No | None |
| [`mas_cluster_issuer`](#mas_cluster_issuer) | Conditional | None |
| [`mas_issuer_kind`](#mas_issuer_kind) | No | None |
| [`mas_certificate_duration`](#mas_certificate_duration) | No | `8760h0m0s` |
| [`mas_certificate_renew_before`](#mas_certificate_renew_before) | No | `720h0m0s` |
| [`mas_superuser_username`](#mas_superuser_username) | Conditional | None |
| [`mas_superuser_password`](#mas_superuser_password) | Conditional | None |
| [`artifactory_username`](#artifactory_username) | Conditional | None |
| [`artifactory_token`](#artifactory_token) | Conditional | None |

`mas_cluster_issuer` is required when automatic certificate management is enabled (`mas_manual_cert_mgmt` is `false`). The superuser and Artifactory credentials only apply in the specific scenarios described in their sections.

### Basic Install

#### mas_catalog_source

OpenShift operator catalog source containing the MAS operator subscription — any valid CatalogSource name in the `openshift-marketplace` namespace, typically `ibm-operator-catalog`.

- **Optional**
- Environment Variable: `MAS_CATALOG_SOURCE`
- Default: `ibm-operator-catalog`

Controls where OpenShift looks for the MAS operator images and metadata, and works with `mas_channel` to determine the version installed. Only change it when directed to use a custom catalog for specific testing or airgap scenarios — an invalid catalog source causes the subscription to fail.

#### mas_channel

MAS operator subscription channel, which determines the version stream installed and the updates applied automatically — for example `8.9.x`, `8.10.x`, `8.11.x`, or `9.0.x` (check the IBM Operator Catalog for currently available channels).

- **Required**
- Environment Variable: `MAS_CHANNEL`
- Default: None

The channel corresponds to major.minor version releases and determines the feature set and compatibility level of the installation. Changing channels after installation triggers an upgrade to the latest version in the new channel, which may require application reconfiguration and testing — consult the MAS compatibility matrix and upgrade documentation before changing it.

### Basic Configuration

#### mas_domain

Custom domain name used to construct all MAS URLs (for example `admin.{mas_domain}`, `home.{mas_domain}`) — any valid DNS domain such as `mas.mycompany.com` or `prod-mas.example.org`.

- **Optional**
- Environment Variable: `MAS_DOMAIN`
- Default: None (auto-generated as `{mas_instance_id}.{cluster ingress domain}`)

Set it for production environments that need branded or corporate domain names, integration with external DNS providers (Cloudflare, Route53, IBM CIS), or custom SSL certificates tied to a specific domain; leave unset for development and testing. DNS must resolve the domain to the cluster, and the value must align with `mas_routing_mode`. The `suite_dns` role uses it to configure DNS entries and certificates.

#### mas_instance_id

Unique identifier for this MAS installation within the cluster — a string of 3-12 characters using lowercase letters, numbers, and hyphens, starting with a lowercase letter and ending with a lowercase letter or number (for example `prod`, `dev01`, `mastest`).

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

This ID becomes the core namespace name (`mas-{mas_instance_id}-core`) and is embedded in resource names and configuration identifiers across all MAS configuration, application, and backup/restore roles. It must be unique within the cluster when running multiple instances and cannot be changed after installation without reinstalling — use consistent naming across environments (for example `dev`, `test`, `prod`).

#### mas_entitlement_key

IBM entitlement key authenticating image pulls from IBM Container Registry — for development builds on Artifactory, use your Artifactory API key instead.

- **Required**
- Environment Variable: `MAS_ENTITLEMENT_KEY`
- Default: Value of `IBM_ENTITLEMENT_KEY` if set

Obtain the key from the IBM Container Library at <https://myibm.ibm.com/products-services/containerlibrary>. The key is stored in a Kubernetes secret and used to create image pull secrets for all MAS pods — invalid or expired keys cause image pull failures and the installation cannot proceed. Keep the key secure and do not commit it to source control.

#### mas_config_dir

Local directory containing Kubernetes configuration files that are applied to the cluster during MAS installation.

- **Optional**
- Environment Variable: `MAS_CONFIG_DIR`
- Default: None

All `*.yaml` and `*.yml` files in the directory are applied with `oc apply` in alphabetical order — typically MAS configuration resources (MongoCfg, BASCfg, JdbcCfg, etc.) generated by dependency roles such as `mongodb`, `db2`, and `sls`, which the `suite_config` role applies after this role. Files must be valid Kubernetes resources; the role does not validate their contents before applying, and invalid resources cause it to fail.

### Advanced Configuration

#### mas_annotations

Comma-separated list of `key=value` annotations applied to all MAS resources — for example `mas.ibm.com/operationalMode=nonproduction` or `key1=value1,key2=value2`.

- **Optional**
- Environment Variable: `MAS_ANNOTATIONS`
- Default: None

The role validates annotation values and combinations (including the `mas.ibm.com/hyperscaler*` annotations) and fails the installation on invalid input. Works alongside `custom_labels` for resource metadata.

!!! warning
    The `mas.ibm.com/operationalMode=nonproduction` annotation significantly reduces CPU and memory requirements and must only be used in development and test environments — it reduces resource allocations below production requirements.

#### mas_img_pull_policy

Image pull policy for all MAS container images: `Always`, `IfNotPresent`, or `Never`.

- **Optional**
- Environment Variable: `MAS_IMG_PULL_POLICY`
- Default: None (operator default)

`Always` pulls the latest image on every pod restart (useful in development, at the cost of slower starts and higher network usage), `IfNotPresent` uses cached images for faster starts (typical for production), and `Never` requires images to be pre-loaded (airgap environments). When unset, `imagePullPolicy` is omitted from the Suite CR and the operator default (typically `IfNotPresent`) applies.

#### custom_labels

Comma-separated list of `key=value` labels applied to all MAS resources — for example `env=prod,team=platform,cost-center=12345`.

- **Optional**
- Environment Variable: `CUSTOM_LABELS`
- Default: None

Labels enable resource organization, selection, and filtering with standard Kubernetes tooling (`oc get -l`, monitoring queries, automation scripts) and support cost allocation and labeling standards. They do not affect MAS functionality. Works alongside `mas_annotations` for resource metadata.

#### mas_manual_cert_mgmt

Enables manual certificate management, disabling automatic certificate generation by cert-manager.

- **Optional**
- Environment Variable: `MAS_MANUAL_CERT_MGMT`
- Default: `false`

When `true`, you must manually create and manage all certificates required by MAS, including renewal before expiry, and the `suite_dns` role will not configure automatic certificate issuers. When `false` (default), cert-manager generates and renews certificates and `mas_cluster_issuer` must be set. Manual certificate management carries significant operational overhead — use automatic management unless you have specific requirements.

#### mas_routing_mode

URL routing strategy for MAS applications and services: `subdomain` (for example `admin.mas.example.com`) or `path` (for example `mas.example.com/admin`).

- **Optional**
- Environment Variable: `MAS_ROUTING_MODE`
- Default: None (MAS default: `subdomain`)

`subdomain` creates separate DNS entries for each service (requires wildcard DNS or multiple entries) and is recommended for production; `path` uses a single DNS entry with path-based routing, which is simpler for DNS but produces more complex URLs. The choice affects DNS configuration in the `suite_dns` role and certificate requirements (wildcard vs single certificate), and must align with `mas_domain`. It cannot be changed after installation without reinstalling.

#### mas_manual_route_mgmt

Enables manual route management, disabling automatic route creation and management by MAS.

- **Optional**
- Environment Variable: `MAS_MANUAL_ROUTE_MGMT`
- Default: `false`

Set to `true` only when alternative routing is required — you must then manually create and manage all routes required by MAS yourself.

#### mas_trust_default_cas

Controls whether default system Certificate Authorities (such as Let's Encrypt and DigiCert) are included in MAS trust stores.

- **Optional**
- Environment Variable: `MAS_TRUST_DEFAULT_CAS`
- Default: None (MAS default: `true`)

Leave unset for most installations so MAS can connect to services using certificates from well-known public CAs. Set to `false` only in highly restricted or airgap environments where external connections are not permitted — MAS will then only trust explicitly configured custom CAs, which may break connections to external services. Only available in MAS 8.11 and above; it has no effect in earlier versions.

#### mas_pod_templates_dir

Directory containing pod template customization files for MAS workloads — for example `ibm-mas-suite.yml` (core suite workloads), `ibm-mas-coreidp.yml` (identity provider workloads), or `ibm-data-dictionary-assetdatadictionary.yml` (data dictionary workloads).

- **Optional**
- Environment Variable: `MAS_POD_TEMPLATES_DIR`
- Default: None

Pod templates customize resource requests and limits, node selectors, tolerations, and QoS classes for MAS workloads — incorrect configurations can cause pods to fail scheduling or perform poorly. See the [MAS CLI pod templates](https://github.com/ibm-mas/cli/blob/master/image/cli/mascli/templates/pod-templates/best-effort/ibm-mas-suite.yml) for examples and the [product documentation](https://www.ibm.com/docs/en/mas-cd/continuous-delivery?topic=configuring-customizing-workloads) for full details. Similar pod template configuration is available in other roles (SLS, applications).

### Certificate Management

#### mas_cluster_issuer

Name of the cert-manager ClusterIssuer used for automatic certificate generation — for example `{mas_instance_id}-cloudflare-le-prod`, as created by the `suite_dns` role.

- **Required** when `mas_manual_cert_mgmt` is `false`
- Environment Variable: `MAS_CLUSTER_ISSUER`
- Default: None

The ClusterIssuer defines the Certificate Authority and authentication method used for all MAS certificates. Ensure it is created and functional before installing MAS (test certificate generation with a test Certificate resource first) — if it is misconfigured or lacks necessary credentials, certificate generation fails and MAS will not be accessible.

#### mas_issuer_kind

Issuer kind written to `spec.settings.issuerKind` of the MAS Suite custom resource: `Issuer` (namespace-scoped) or `ClusterIssuer` (cluster-scoped).

- **Optional**
- Environment Variable: `MAS_ISSUER_KIND`
- Default: None (automatically set to `ClusterIssuer` when installing MAS 9.2 or later)

`Issuer` certificate references remain namespace-scoped and can be used in all permission modes (`cluster`, `namespaced`, and `minimal`), while `ClusterIssuer` references a cluster-scoped issuer and should only be used when MAS is installed in `cluster` permission mode.

#### mas_certificate_duration

Validity period for MAS certificates, as a duration string in `{hours}h{minutes}m{seconds}s` format — for example `8760h0m0s` (1 year, default), `2160h0m0s` (90 days), or `17520h0m0s` (2 years).

- **Optional**
- Environment Variable: `MAS_CERTIFICATE_DURATION`
- Default: `8760h0m0s` (1 year)

Must be longer than `mas_certificate_renew_before` and only applies when automatic certificate management is in use. Shorter durations increase security but require more frequent renewals; cert-manager renews certificates automatically before they expire.

#### mas_certificate_renew_before

How far in advance of expiry cert-manager renews certificates, as a duration string in `{hours}h{minutes}m{seconds}s` format — for example `720h0m0s` (30 days, default), `1440h0m0s` (60 days), or `168h0m0s` (7 days).

- **Optional**
- Environment Variable: `MAS_CERTIFICATE_RENEW_BEFORE`
- Default: `720h0m0s` (30 days)

Must be shorter than `mas_certificate_duration` and only applies when automatic certificate management is in use. Longer renewal windows provide more time to resolve renewal issues but result in more frequent certificate changes.

### Superuser Account

The MAS Superuser account username and password can be customized during the install by setting **both** of these variables.

#### mas_superuser_username

Custom username for the MAS superuser administrator account — any valid username string (alphanumeric, may include underscores and hyphens).

- **Optional** — must be set together with `mas_superuser_password`
- Environment Variable: `MAS_SUPERUSER_USERNAME`
- Default: None (uses MAS default superuser)

The superuser has full administrative access to all MAS functions and applications. If only one of username/password is set, both are ignored and the default account is used.

#### mas_superuser_password

Custom password for the MAS superuser administrator account — any string meeting MAS password requirements (minimum length, complexity).

- **Optional** — must be set together with `mas_superuser_username`
- Environment Variable: `MAS_SUPERUSER_PASSWORD`
- Default: None (auto-generated)

Setting the password in advance lets you know the superuser credentials and comply with organizational password policies. If only one of username/password is set, both are ignored and the default account is used with an auto-generated password. Keep the password secure and do not commit it to source control.

### Developer Mode

#### artifactory_username

Username for authenticating to Artifactory for development builds — your IBM w3Id username.

- **Optional** — only required when installing development builds from Artifactory
- Environment Variable: `ARTIFACTORY_USERNAME`
- Default: None

Must be set together with `artifactory_token`; the credentials are used to create image pull secrets for Artifactory registries when `mas_icr_cp` and `mas_icr_cpopen` are pointed at Artifactory. Not needed for production installations using IBM Container Registry with an entitlement key.

#### artifactory_token

API token for authenticating to Artifactory for development builds.

- **Optional** — only required when installing development builds from Artifactory
- Environment Variable: `ARTIFACTORY_TOKEN`
- Default: None

Must be set together with `artifactory_username` and can serve as the `mas_entitlement_key` equivalent for development builds. Only for internal development and testing — keep tokens secure, and use IBM Container Registry with entitlement keys for production.

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
