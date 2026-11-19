# cos
This role provides support for:

- Provisioning and Configuring Cloud Object Storage in MAS. It currently supports two providers:
    - In-cluster Ceph Object Storage leveraging OpenShift Container Storage
    - IBM Cloud Object Storage
- Deprovision Cloud Object Store. It currently supports one provider:
    - IBM Cloud Object Storage

Currently this role only supports generating a system-scoped ObjectStorageCfg resource, but the generated file can be modified if you wish to use other scopes.

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`cos_type`](#cos_type) | Yes | None |
| [`cos_action`](#cos_action) | No | `provision` |
| [`custom_labels`](#custom_labels) | No | None |
| [`cos_instance_name`](#cos_instance_name) | No | `Object Storage for MAS` |
| [`cos_location_info`](#cos_location_info) | No | `global` |
| [`cos_plan_type`](#cos_plan_type) | No | `standard` |
| [`cos_region`](#cos_region) | No | `us-standard` |
| [`cos_url`](#cos_url) | No | `https://s3.us.cloud-object-storage.appdomain.cloud` |
| [`cos_resource_key_iam_role`](#cos_resource_key_iam_role) | No | `Manager` |
| [`cos_use_hmac`](#cos_use_hmac) | No | `true` |
| [`cos_apikey`](#cos_apikey) | No | Falls back to `ibmcloud_apikey` |
| [`ibmcloud_apikey`](#ibmcloud_apikey) | Conditional | None |
| [`cos_resourcegroup`](#cos_resourcegroup) | No | Falls back to `ibmcloud_resourcegroup` |
| [`ibmcloud_resourcegroup`](#ibmcloud_resourcegroup) | No | `Default` |
| [`ocp_ingress_tls_secret_name`](#ocp_ingress_tls_secret_name) | No | `router-certs-default` |
| [`include_cluster_ingress_cert_chain`](#include_cluster_ingress_cert_chain) | No | `False` |
| [`cos_include_isrg_root_cert`](#cos_include_isrg_root_cert) | No | `true` |
| [`mas_instance_id`](#mas_instance_id) | No | None |
| [`mas_config_dir`](#mas_config_dir) | No | None |

Variables marked Conditional are required only when `cos_type` is `ibm` (`ibmcloud_apikey`, unless `cos_apikey` is provided instead). Additionally, both `mas_instance_id` and `mas_config_dir` must be set for the role to generate an ObjectStorageCfg resource — if either is missing, the role only provisions the storage.

### COS Provider and Action

#### cos_type

The Cloud Object Storage provider to use for MAS — `ibm` (IBM Cloud Object Storage, a managed cloud service) or `ocs` (in-cluster Ceph object storage via OpenShift Container Storage / OpenShift Data Foundation).

- **Required**
- Environment Variable: `COS_TYPE`
- Default: None

`ibm` provisions an IBM Cloud COS instance (requires an IBM Cloud account and API key, incurs cloud costs, provides unlimited scalability, and is recommended for production deployments requiring high availability and separation of storage from compute), while `ocs` creates a Ceph object store within the OpenShift cluster (requires the OCS/ODF operator and sufficient cluster storage capacity, with no external costs — suitable for on-premises or air-gapped deployments). The choice also affects the generated ObjectStorageCfg resource format; consider data residency and compliance requirements when choosing.

#### cos_action

The action to perform on the Cloud Object Storage instance — `provision` (create and configure the COS instance, generate credentials, and create the ObjectStorageCfg resource) or `deprovision` (delete the COS instance; IBM COS only, not supported for OCS).

- **Optional**
- Environment Variable: `COS_ACTION`
- Default: `provision`

!!! warning
    Deprovisioning permanently deletes the IBM Cloud COS instance and all data — this is irreversible. Ensure all data is backed up first and verify no applications are using the instance before deprovisioning. IBM Cloud COS deprovisioning may fail if buckets contain data; for OCS, deprovisioning must be done manually through the OpenShift console.

#### custom_labels

Custom key=value labels to apply to provisioned resources, as a comma-separated list (e.g. `environment=production,team=platform,cost-center=engineering`).

- **Optional**
- Environment Variable: `CUSTOM_LABELS`
- Default: None

Labels are metadata only and do not affect resource behavior; they are useful for cost tracking, resource organization, and automation-driven resource discovery (IBM Cloud supports label-based cost allocation and reporting).

### IBM Cloud Object Storage

#### cos_instance_name

The name for the IBM Cloud Object Storage instance — any string following IBM Cloud resource naming conventions (e.g. `prod-mas-cos`, `dev-maximo-cos`).

- **Optional** (IBM COS only)
- Environment Variable: `COS_INSTANCE_NAME`
- Default: `Object Storage for MAS`, or `Object Storage for MAS - <mas_instance_id>` when `mas_instance_id` is set

Used as the display name in the IBM Cloud console, to locate the instance during deprovisioning, and to identify the instance among other cloud resources; IBM Cloud allows renaming instances after creation.

#### cos_location_info

The geographic location where the IBM Cloud COS instance will be available — `global` (maximum flexibility and automatic failover), a specific region code (`us-south`, `us-east`, `eu-gb`, `eu-de`, `jp-tok`, `au-syd`), or a cross-region (`us`, `eu`, `ap`) for multi-region redundancy.

- **Optional** (IBM COS only)
- Environment Variable: `COS_LOCATION`
- Default: `global`

`global` is recommended for most deployments unless data residency is required; regional instances ensure data stays within specific geographic boundaries and may have lower latency for local access. Cannot be changed after instance creation, and `cos_url` should match the location for optimal performance.

#### cos_plan_type

The IBM Cloud COS service plan tier — `standard` (pay-as-you-go pricing with unlimited capacity; suitable for most MAS deployments) or `lite` (free tier with limited capacity, not suitable for production).

- **Optional** (IBM COS only, for provisioning)
- Environment Variable: `COS_PLAN`
- Default: `standard`

Only used when `cos_action` is `provision`; the plan cannot be changed after provisioning (it requires recreation). Pricing is based on storage capacity, requests, and data transfer.

#### cos_region

The IBM Cloud COS region identifier — e.g. `us-south`, `eu-de`, `us-east`.

- **Optional** (IBM COS only)
- Environment Variable: `COS_REGION`
- Default: `us-standard`

When set to a non-empty value, the region is included in the generated secret and `ObjectStorageCfg` resource; it is omitted when empty.

#### cos_url

The IBM Cloud COS regional endpoint URL for S3 API access — e.g. `https://s3.us.cloud-object-storage.appdomain.cloud` (US), `https://s3.eu.cloud-object-storage.appdomain.cloud` (EU), `https://s3.ap.cloud-object-storage.appdomain.cloud` (AP), or private/direct endpoints (`https://s3.private.<region>.cloud-object-storage.appdomain.cloud`, `https://s3.direct.<region>.cloud-object-storage.appdomain.cloud`).

- **Optional** (IBM COS only)
- Environment Variable: `COS_REGION_LOCATION_URL`
- Default: `https://s3.us.cloud-object-storage.appdomain.cloud`

Used in the generated ObjectStorageCfg resource for MAS to connect to COS; it must be accessible from the OpenShift cluster. Private endpoints provide better security and lower costs for in-cloud access (recommended for OpenShift clusters running in IBM Cloud), and direct endpoints provide better performance for high-throughput workloads.

#### cos_resource_key_iam_role

The IAM role to assign to the COS service credentials — `Manager` (full access to buckets and objects; default), `Writer` (read and write access to objects with limited bucket operations), `Reader` (read-only access to objects), or `Content Reader` (read-only without listing capabilities).

- **Optional** (IBM COS only)
- Environment Variable: `COS_RESOURCE_KEY_IAM_ROLE`
- Default: `Manager`

Always use the `Manager` role for MAS deployments — lower privilege roles are not sufficient for MAS to create and manage buckets and will cause MAS functionality to fail. The role is assigned to the service credentials, not the instance itself.

#### cos_use_hmac

Controls whether to use HMAC-style credentials for COS access — `true` generates AWS S3-compatible access key ID and secret access key credentials; `false` uses IAM API key authentication (not compatible with MAS).

- **Optional** (IBM COS only)
- Environment Variable: `COS_USE_HMAC`
- Default: `true`

!!! important
    Always use `true` for MAS deployments — MAS requires HMAC credentials for S3 API compatibility, and setting this to `false` will cause MAS object storage configuration to fail. The credential format cannot be changed after credential creation (it requires new credentials).

#### cos_apikey

The IBM Cloud API key specifically for COS operations — a 44-character alphanumeric key with COS service management permissions.

- **Optional** (IBM COS only)
- Environment Variable: `COS_APIKEY`
- Default: Falls back to `ibmcloud_apikey` if not set

When set, this key is used instead of `ibmcloud_apikey` for COS operations, allowing a less privileged dedicated key for COS management following the principle of least privilege.

#### ibmcloud_apikey

The default IBM Cloud API key for all IBM Cloud operations — a 44-character alphanumeric key with Editor or Administrator role on the COS service and access to the specified resource group.

- **Required** when `cos_type` is `ibm` (unless `cos_apikey` is set)
- Environment Variable: `IBMCLOUD_APIKEY`
- Default: None

Used for all IBM Cloud operations unless `cos_apikey` is specified; it determines which IBM Cloud account owns the COS instance (and is billed for usage). Store API keys securely and never commit them to version control.

#### cos_resourcegroup

The IBM Cloud resource group for the COS instance — any existing, case-sensitive resource group name (e.g. `Default`, `Storage`, `MAS-Resources`).

- **Optional** (IBM COS only)
- Environment Variable: `COS_RESOURCEGROUP`
- Default: Falls back to `ibmcloud_resourcegroup` if not set

Determines billing, cost allocation, and IAM access policies for the COS instance, and cannot be changed after instance creation; set it to organize COS separately from other IBM Cloud resources. The API key must have access to the specified resource group.

#### ibmcloud_resourcegroup

The default IBM Cloud resource group for all IBM Cloud resources — any existing, case-sensitive resource group name (e.g. `Default`, `Production`, `Development`).

- **Optional** (IBM COS only)
- Environment Variable: `IBMCLOUD_RESOURCEGROUP`
- Default: `Default`

Used as the default resource group for COS and other IBM Cloud resources across multiple roles in the collection; can be overridden by `cos_resourcegroup` for COS-specific placement.

### Ingress Certificate Chain

#### ocp_ingress_tls_secret_name

The name of the OpenShift cluster's default router certificate secret — must be a valid secret containing a TLS certificate and key in the `openshift-ingress` namespace.

- **Optional** (OCS only)
- Environment Variable: `OCP_INGRESS_TLS_SECRET_NAME`
- Default: `router-certs-default`

Only relevant when `cos_type` is `ocs`: this secret is the source of the cluster's ingress certificate used in the ObjectStorageCfg. The default works for standard OpenShift installations — override only if you have customized your cluster's ingress certificates; an incorrect value will cause certificate validation failures when accessing OCS.

#### include_cluster_ingress_cert_chain

Controls whether to include the complete certificate chain from the cluster's ingress in the ObjectStorageCfg — `True` includes the full chain, `False` only the leaf certificate.

- **Optional**
- Environment Variable: `INCLUDE_CLUSTER_INGRESS_CERT_CHAIN`
- Default: `False`

Primarily relevant for OCS with custom certificates: enable when your cluster's ingress uses certificates signed by a trusted CA and you experience certificate validation issues in environments with intermediate CAs. Not typically needed for IBM Cloud COS.

#### cos_include_isrg_root_cert

Controls whether to append the ISRG Root X1 certificate (the default root certificate used by Let's Encrypt) to the ObjectStorageCfg certificate chain.

- **Optional** (OCS only)
- Environment Variable: `COS_INCLUDE_ISRG_ROOT_CERT`
- Default: `true`

Only applied when OCS ingress certificates are present; mainly needed for IBM Cloud hosted services.

### MAS Configuration

#### mas_instance_id

The MAS instance ID that the ObjectStorageCfg will target — an alphanumeric string, typically 3-12 lowercase characters (e.g. `prod`, `dev`, `test`, `masinst1`), matching the MAS instance ID used throughout your deployment.

- **Optional**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

Required (together with `mas_config_dir`) for the role to generate an ObjectStorageCfg resource — if either is missing, the role only provisions the storage. The ObjectStorageCfg is created in the `mas-<instance-id>-core` namespace.

#### mas_config_dir

Local directory where the ObjectStorageCfg resource will be saved — any valid local filesystem path (e.g. `~/masconfig`, `/opt/mas/config`); the directory is created if it doesn't exist.

- **Optional**
- Environment Variable: `MAS_CONFIG_DIR`
- Default: None

Required (together with `mas_instance_id`) for the role to generate an ObjectStorageCfg resource. The generated file can be applied manually with `oc apply -f` or used as input to the `suite_config` role for automated configuration.

## Example Playbook

Create the Ceph Object store on the existing OCS cluster and prepare the objectstorageCfg yaml to mas_config_dir. The `ocs` provider is not supported when ODF is deployed in external mode (`StorageCluster` `spec.externalStorage.enable: true`), because the Ceph object store and user cannot be reconciled; the role fails immediately in that case. The only exception is an existing `CephObjectStoreUser` named `object` in `openshift-storage` that is already `Ready`, so setups where this previously worked continue to work.

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    cos_type: ocs
    mas_instance_id: masinst1
    mas_config_dir: ~/masconfig
  roles:
    - ibm.mas_devops.cos
```

Create the IBM Cloud Object storage Instance and prepare the objectstorageCfg yaml to mas_config_dir.

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    cos_type: ibm
    ibmcloud_apikey: <Your IBM Cloud API Key>
    mas_instance_id: masinst1
    mas_config_dir: ~/masconfig
  roles:
    - ibm.mas_devops.cos
```

## License

EPL-2.0
