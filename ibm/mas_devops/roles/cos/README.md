# cos
This role provides support for:

- Provisioning and Configuring Cloud Object Storage in MAS. It currently supports two providers:
    - In-cluster Ceph Object Storage leveraging OpenShift Container Storage
    - IBM Cloud Object Storage
- Deprovision Cloud Object Store. It currently supports one provider:
    - IBM Cloud Object Storage

Currently this role only supports generating a system-scoped ObjectStorageCfg resource, but the generated file can be modified if you wish to use other scopes.


## Role Variables - General
## Role Variables - General

### cos_type
The Cloud Object Storage provider to use for MAS.

- **Required**
- Environment Variable: `COS_TYPE`
- Default Value: None

**Purpose**: Determines which object storage backend will be provisioned and configured for MAS. Different providers have different capabilities, costs, and operational characteristics.

**When to use**: Always required when provisioning object storage. Choose based on your deployment platform, cost requirements, and operational preferences.

**Valid values**:
- `ibm` - IBM Cloud Object Storage (managed cloud service)
- `ocs` - OpenShift Container Storage / OpenShift Data Foundation (in-cluster Ceph-based storage)

**Impact**:
- **`ibm`**: Provisions IBM Cloud COS instance, requires IBM Cloud account and API key, incurs cloud costs, provides unlimited scalability
- **`ocs`**: Creates Ceph object store within OpenShift cluster, requires OCS/ODF operator installed, uses cluster storage capacity, no external costs
- Determines which set of configuration variables are required
- Affects the generated ObjectStorageCfg resource format

**Related variables**:
- When `cos_type=ibm`: Requires [`ibmcloud_apikey`](#ibmcloud_apikey), [`cos_instance_name`](#cos_instance_name), [`cos_url`](#cos_url)
- When `cos_type=ocs`: Requires OCS/ODF operator to be installed in the cluster
- [`cos_action`](#cos_action) - Whether to provision or deprovision

**Notes**:
- IBM COS is recommended for production deployments requiring high availability and unlimited capacity
- OCS is suitable for on-premises or air-gapped deployments where external cloud services are not available
- OCS requires sufficient cluster storage capacity and OCS/ODF operator installation
- IBM COS provides better separation of concerns (storage managed separately from compute)
- Consider data residency and compliance requirements when choosing provider

### cos_action
The action to perform on the Cloud Object Storage instance.

- **Required**
- Environment Variable: `COS_ACTION`
- Default Value: `provision`

**Purpose**: Controls whether to create a new COS instance or delete an existing one. This allows the same role to handle both lifecycle operations.

**When to use**:
- Use `provision` (default) when setting up object storage for a new MAS deployment
- Use `deprovision` when cleaning up COS resources after MAS uninstallation

**Valid values**:
- `provision` - Create and configure COS instance, generate ObjectStorageCfg
- `deprovision` - Delete COS instance (IBM COS only, not supported for OCS)

**Impact**:
- **Provision**: Creates COS instance, generates credentials, creates ObjectStorageCfg resource
- **Deprovision**: Permanently deletes IBM Cloud COS instance and all data (irreversible)
- Deprovisioning is only supported for `cos_type=ibm`, not for OCS
- All data stored in the COS instance will be lost during deprovisioning

**Related variables**:
- [`cos_type`](#cos_type) - Determines which provider to provision/deprovision
- [`cos_instance_name`](#cos_instance_name) - Identifies which instance to deprovision

**Notes**:
- Deprovisioning is irreversible - ensure all data is backed up first
- For OCS, deprovisioning must be done manually through OpenShift console
- Verify no applications are using the COS instance before deprovisioning
- IBM Cloud COS deprovisioning may fail if buckets contain data

### ocp_ingress_tls_secret_name
The name of the OpenShift cluster's default router certificate secret.

- **Optional**
- Environment Variable: `OCP_INGRESS_TLS_SECRET_NAME`
- Default Value: `router-certs-default`

**Purpose**: Specifies the secret containing the cluster's ingress TLS certificate. This is used when configuring OCS to ensure proper certificate validation for S3 API access.

**When to use**: Only needed in rare cases where the cluster uses a non-standard ingress certificate secret name, or when the role cannot automatically determine the correct secret name.

**Valid values**:
- Any valid secret name in the `openshift-ingress` namespace
- Default `router-certs-default` works for most OpenShift clusters
- Must contain TLS certificate and key

**Impact**:
- Used to extract the cluster's ingress certificate for OCS configuration
- Incorrect value will cause certificate validation failures when accessing OCS
- Only relevant when `cos_type=ocs`

**Related variables**:
- [`cos_type`](#cos_type) - Only used when set to `ocs`
- [`include_cluster_ingress_cert_chain`](#include_cluster_ingress_cert_chain) - Controls certificate chain inclusion

**Notes**:
- The default value works for standard OpenShift installations
- Only override if you have customized your cluster's ingress certificates
- The secret must exist in the `openshift-ingress` namespace
- Not used for IBM Cloud COS (`cos_type=ibm`)

### custom_labels
Custom key-value labels to apply to provisioned resources.

- **Optional**
- Environment Variable: `CUSTOM_LABELS`
- Default Value: None

**Purpose**: Allows adding custom labels to COS-related resources for organization, cost tracking, or automation purposes. Labels are applied to instance-specific resources.

**When to use**: When you need to tag resources for cost allocation, environment identification, team ownership, or integration with other automation tools.

**Valid values**:
- Comma-separated key=value pairs
- Example: `environment=production,team=platform,cost-center=engineering`
- Keys and values must follow Kubernetes label naming conventions
- Maximum 63 characters per key/value

**Impact**:
- Labels are applied to COS instance and related resources
- Useful for cost tracking and resource organization in IBM Cloud
- Can be used by automation tools for resource discovery
- Does not affect functionality, only metadata

**Related variables**:
- Applied to resources created by this role regardless of `cos_type`

**Notes**:
- Labels are metadata only and do not affect resource behavior
- Use consistent labeling across all MAS resources for better management
- IBM Cloud supports label-based cost allocation and reporting
- Labels can be modified after resource creation


## Role Variables - IBM COS
### cos_instance_name
The name for the IBM Cloud Object Storage instance.

- **Optional** (IBM COS only)
- Environment Variable: `COS_INSTANCE_NAME`
- Default Value: `Object Storage for MAS` (appended with MAS instance ID if set)

**Purpose**: Specifies a custom name for the IBM Cloud COS instance. This name appears in the IBM Cloud console and is used for identification and management.

**When to use**: Only relevant when `cos_type=ibm`. Provide a descriptive name that follows your organization's naming conventions.

**Valid values**:
- Any string following IBM Cloud resource naming conventions
- If not specified, defaults to `Object Storage for MAS` or `Object Storage for MAS <mas_instance_id>`
- Recommended format: `<environment>-<purpose>-cos` (e.g., `prod-mas-cos`, `dev-maximo-cos`)

**Impact**:
- Used as the display name in IBM Cloud console
- Helps identify the COS instance among other cloud resources
- Used during deprovisioning to locate the instance
- Does not affect functionality, only identification

**Related variables**:
- [`cos_type`](#cos_type) - Must be `ibm` for this to be used
- [`mas_instance_id`](#mas_instance_id) - Appended to default name if set
- [`cos_resourcegroup`](#cos_resourcegroup) - Resource group containing this instance

**Notes**:
- Not used for OCS (`cos_type=ocs`)
- Use descriptive names for easier management in multi-instance environments
- The name can include the MAS instance ID for clarity
- IBM Cloud allows renaming instances after creation

### cos_location_info
The geographic location where the IBM Cloud COS instance will be available.

- **Required** (IBM COS only)
- Environment Variable: `COS_LOCATION`
- Default Value: `global`

**Purpose**: Specifies the geographic scope of the IBM Cloud COS instance. This determines data residency and availability characteristics.

**When to use**: Only relevant when `cos_type=ibm`. Use `global` for maximum flexibility, or specify a region for data residency compliance.

**Valid values**:
- `global` - Instance available globally with automatic region selection
- Specific region codes: `us-south`, `us-east`, `eu-gb`, `eu-de`, `jp-tok`, `au-syd`, etc.
- Cross-region: `us`, `eu`, `ap` for multi-region redundancy

**Impact**:
- `global` provides maximum flexibility and automatic failover
- Regional instances ensure data stays within specific geographic boundaries
- Affects data residency compliance and latency
- Cannot be changed after instance creation

**Related variables**:
- [`cos_type`](#cos_type) - Must be `ibm` for this to be used
- [`cos_url`](#cos_url) - Should match the location for optimal performance

**Notes**:
- `global` is recommended for most deployments unless data residency is required
- Regional instances may have lower latency for local access
- Consider compliance requirements (GDPR, data sovereignty) when choosing location
- Not applicable for OCS (`cos_type=ocs`)

### cos_plan_type
The IBM Cloud COS service plan tier.

- **Required** (IBM COS only, for provisioning)
- Environment Variable: `COS_PLAN`
- Default Value: `standard`

**Purpose**: Specifies the IBM Cloud COS service plan, which determines pricing and available features.

**When to use**: Only relevant when `cos_type=ibm` and `cos_action=provision`. The standard plan is suitable for most MAS deployments.

**Valid values**:
- `standard` - Standard plan with pay-as-you-go pricing
- `lite` - Free tier with limited capacity (not recommended for production)

**Impact**:
- Determines pricing model and billing
- Standard plan provides unlimited capacity with usage-based pricing
- Lite plan has capacity limits and is not suitable for production MAS
- Cannot be changed after provisioning (requires recreation)

**Related variables**:
- [`cos_type`](#cos_type) - Must be `ibm` for this to be used
- [`cos_action`](#cos_action) - Only used during provisioning

**Notes**:
- Always use `standard` plan for production MAS deployments
- Lite plan is only suitable for development/testing with minimal data
- Pricing is based on storage capacity, requests, and data transfer
- Not applicable for OCS (`cos_type=ocs`)

### cos_url
The IBM Cloud COS regional endpoint URL for S3 API access.

- **Required** (IBM COS only, for provisioning)
- Environment Variable: `COS_REGION_LOCATION_URL`
- Default Value: `https://s3.us.cloud-object-storage.appdomain.cloud`

**Purpose**: Specifies the S3-compatible API endpoint URL for accessing the IBM Cloud COS instance. This URL is used in the generated ObjectStorageCfg resource for MAS to connect to COS.

**When to use**: Only relevant when `cos_type=ibm`. Should match the region where your COS instance is located for optimal performance.

**Valid values**:
- Regional endpoints: `https://s3.<region>.cloud-object-storage.appdomain.cloud`
- Examples:
  - US: `https://s3.us.cloud-object-storage.appdomain.cloud`
  - EU: `https://s3.eu.cloud-object-storage.appdomain.cloud`
  - AP: `https://s3.ap.cloud-object-storage.appdomain.cloud`
- Private endpoints: `https://s3.private.<region>.cloud-object-storage.appdomain.cloud`
- Direct endpoints: `https://s3.direct.<region>.cloud-object-storage.appdomain.cloud`

**Impact**:
- Determines which IBM Cloud COS endpoint MAS will use for object storage operations
- Affects network latency and data transfer costs
- Private endpoints provide better security and lower costs for in-cloud access
- Must be accessible from the OpenShift cluster

**Related variables**:
- [`cos_type`](#cos_type) - Must be `ibm` for this to be used
- [`cos_location_info`](#cos_location_info) - Should align with the endpoint region

**Notes**:
- Use regional endpoints matching your COS instance location for best performance
- Private endpoints recommended for OpenShift clusters running in IBM Cloud
- Direct endpoints provide better performance for high-throughput workloads
- Ensure network connectivity from OpenShift cluster to the endpoint
- Not applicable for OCS (`cos_type=ocs`)

### cos_resource_key_iam_role
The IAM role to assign to the COS service credentials.

- **Optional** (IBM COS only)
- Environment Variable: `COS_RESOURCE_KEY_IAM_ROLE`
- Default Value: `Manager`

**Purpose**: Specifies the IAM role level for the service credentials (resource key) created during COS provisioning. This determines the permissions granted to MAS for accessing the COS instance.

**When to use**: Only relevant when `cos_type=ibm`. The default `Manager` role provides full access required by MAS.

**Valid values**:
- `Manager` - Full access to COS instance (create/read/update/delete buckets and objects)
- `Writer` - Read and write access to objects, limited bucket operations
- `Reader` - Read-only access to objects
- `Content Reader` - Read-only access without listing capabilities

**Impact**:
- Determines what operations MAS can perform on the COS instance
- `Manager` role is required for MAS to create and manage buckets
- Lower privilege roles will cause MAS functionality to fail
- Credentials are generated with this role during provisioning

**Related variables**:
- [`cos_type`](#cos_type) - Must be `ibm` for this to be used
- [`cos_use_hmac`](#cos_use_hmac) - Controls credential format

**Notes**:
- Always use `Manager` role for MAS deployments (default)
- Lower privilege roles are not sufficient for MAS operations
- The role is assigned to the service credentials, not the instance itself
- Not applicable for OCS (`cos_type=ocs`)

### cos_use_hmac
Controls whether to use HMAC-style credentials for COS access.

- **Optional** (IBM COS only)
- Environment Variable: `COS_USE_HMAC`
- Default Value: `true`

**Purpose**: Determines whether to generate HMAC (AWS S3-compatible) credentials or IAM-based credentials for accessing IBM Cloud COS. MAS requires HMAC credentials for S3 API compatibility.

**When to use**: Should always be `true` for MAS deployments. Setting to `false` will prevent MAS from accessing the COS instance.

**Valid values**:
- `true` - Generate HMAC credentials (AWS S3-compatible access key and secret key)
- `false` - Use IAM API key authentication (not compatible with MAS)

**Impact**:
- When `true`: Generates S3-compatible access key ID and secret access key
- When `false`: MAS will not be able to access the COS instance
- HMAC credentials are required for S3 API compatibility
- Cannot be changed after credential creation (requires new credentials)

**Related variables**:
- [`cos_type`](#cos_type) - Must be `ibm` for this to be used
- [`cos_resource_key_iam_role`](#cos_resource_key_iam_role) - Role assigned to HMAC credentials

**Notes**:
- **Always use `true` for MAS deployments** - this is critical
- HMAC credentials provide S3 API compatibility required by MAS
- Setting to `false` will cause MAS object storage configuration to fail
- Not applicable for OCS (`cos_type=ocs`)

### cos_apikey
The IBM Cloud API key specifically for COS operations.

- **Required** (IBM COS only)
- Environment Variable: `COS_APIKEY`
- Default Value: Falls back to `ibmcloud_apikey` if not set

**Purpose**: Provides an optional dedicated API key for COS operations. This allows using a less privileged API key specifically for COS management, following the principle of least privilege.

**When to use**: Only relevant when `cos_type=ibm`. Set this if you want to use a different API key for COS than for other IBM Cloud operations.

**Valid values**:
- A valid IBM Cloud API key with COS service permissions
- Must have permissions to create and manage COS instances
- Format: 44-character alphanumeric string

**Impact**:
- If set, this API key is used instead of `ibmcloud_apikey` for COS operations
- Allows separation of permissions between COS and other IBM Cloud services
- Falls back to `ibmcloud_apikey` if not specified

**Related variables**:
- [`ibmcloud_apikey`](#ibmcloud_apikey) - Fallback if this is not set
- [`cos_type`](#cos_type) - Must be `ibm` for this to be used

**Notes**:
- Optional - defaults to `ibmcloud_apikey` if not provided
- Use a dedicated key for better security and permission isolation
- The key must have COS service management permissions
- Not applicable for OCS (`cos_type=ocs`)

### ibmcloud_apikey
The default IBM Cloud API key for all IBM Cloud operations.

- **Required** (IBM COS only)
- Environment Variable: `IBMCLOUD_APIKEY`
- Default Value: None

**Purpose**: Provides the primary IBM Cloud API key used across multiple roles in the collection. This is the default authentication method for IBM Cloud services.

**When to use**: Always required when `cos_type=ibm`. This API key must have permissions to create and manage COS instances.

**Valid values**:
- A valid IBM Cloud API key with appropriate permissions
- Must have Editor or Administrator role on COS service
- Must have access to the specified resource group
- Format: 44-character alphanumeric string

**Impact**:
- Used for all IBM Cloud operations unless `cos_apikey` is specified
- Determines which IBM Cloud account owns the COS instance
- Account will be billed for COS usage
- Required permissions: COS service management, resource group access

**Related variables**:
- [`cos_apikey`](#cos_apikey) - Can override this for COS-specific operations
- [`ibmcloud_resourcegroup`](#ibmcloud_resourcegroup) - Must have access to this resource group
- [`cos_type`](#cos_type) - Must be `ibm` for this to be used

**Notes**:
- Store API keys securely using environment variables or secrets management
- Never commit API keys to version control
- Consider using service IDs with restricted permissions
- Used by multiple roles in the collection for consistency
- Not applicable for OCS (`cos_type=ocs`)

### cos_resourcegroup
The IBM Cloud resource group for the COS instance.

- **Optional** (IBM COS only)
- Environment Variable: `COS_RESOURCEGROUP`
- Default Value: Falls back to `ibmcloud_resourcegroup`

**Purpose**: Specifies the resource group in IBM Cloud where the COS instance will be created. This allows using a different resource group for COS than for other IBM Cloud resources.

**When to use**: Only relevant when `cos_type=ibm`. Set this if you want to organize COS in a different resource group than other IBM Cloud resources.

**Valid values**:
- Any existing resource group name in your IBM Cloud account
- Common examples: `Default`, `Storage`, `MAS-Resources`
- Must exist before provisioning
- Case-sensitive

**Impact**:
- Determines billing and cost allocation for the COS instance
- Controls IAM access policies
- Falls back to `ibmcloud_resourcegroup` if not specified
- Cannot be changed after instance creation

**Related variables**:
- [`ibmcloud_resourcegroup`](#ibmcloud_resourcegroup) - Fallback if this is not set
- [`ibmcloud_apikey`](#ibmcloud_apikey) - Must have access to this resource group
- [`cos_type`](#cos_type) - Must be `ibm` for this to be used

**Notes**:
- Optional - defaults to `ibmcloud_resourcegroup` if not provided
- Use for organizing COS separately from other resources
- Ensure the API key has access to the specified resource group
- Not applicable for OCS (`cos_type=ocs`)

### ibmcloud_resourcegroup
The default IBM Cloud resource group for all IBM Cloud resources.

- **Optional** (IBM COS only)
- Environment Variable: `IBMCLOUD_RESOURCEGROUP`
- Default Value: `Default`

**Purpose**: Specifies the default resource group used across multiple roles in the collection. This provides consistency in resource organization.

**When to use**: Only relevant when `cos_type=ibm`. Set this to organize all IBM Cloud resources in a specific resource group.

**Valid values**:
- Any existing resource group name in your IBM Cloud account
- Common examples: `Default`, `Production`, `Development`
- Must exist before provisioning
- Case-sensitive

**Impact**:
- Used as the default resource group for COS and other IBM Cloud resources
- Determines billing and cost allocation
- Controls IAM access policies
- Can be overridden by `cos_resourcegroup` for COS-specific placement

**Related variables**:
- [`cos_resourcegroup`](#cos_resourcegroup) - Can override this for COS
- [`ibmcloud_apikey`](#ibmcloud_apikey) - Must have access to this resource group
- [`cos_type`](#cos_type) - Must be `ibm` for this to be used

**Notes**:
- Defaults to `Default` resource group if not specified
- Use consistent resource groups across all MAS-related services
- Helps with cost tracking and access management
- Not applicable for OCS (`cos_type=ocs`)


## Role Variables - MAS Configuration
### mas_instance_id
The MAS instance ID that the ObjectStorageCfg will target.

- **Optional**
- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

**Purpose**: Identifies the specific MAS instance for which the ObjectStorageCfg resource will be generated. This ensures the object storage configuration is associated with the correct MAS deployment.

**When to use**: Required if you want the role to generate an ObjectStorageCfg resource. If not set (along with `mas_config_dir`), the role will only provision the storage but not generate MAS configuration.

**Valid values**:
- Alphanumeric string, typically 3-12 characters
- Common examples: `prod`, `dev`, `test`, `masinst1`
- Should match the MAS instance ID used throughout your deployment
- Lowercase recommended

**Impact**:
- Used to generate the ObjectStorageCfg resource name and namespace
- If not set, no ObjectStorageCfg will be generated (storage only)
- Must match the actual MAS instance ID for configuration to work
- Both this and `mas_config_dir` must be set for config generation

**Related variables**:
- [`mas_config_dir`](#mas_config_dir) - Both must be set for config generation
- Used consistently across all MAS DevOps roles

**Notes**:
- Use the same `mas_instance_id` across all MAS components
- If you only want to provision storage without MAS config, leave this unset
- The ObjectStorageCfg will be created in the `mas-<instance-id>-core` namespace
- Required for automated MAS configuration via `suite_config` role

### mas_config_dir
Local directory where the ObjectStorageCfg resource will be saved.

- **Optional**
- Environment Variable: `MAS_CONFIG_DIR`
- Default Value: None

**Purpose**: Specifies the local directory path where the generated ObjectStorageCfg YAML file will be saved. This file can be used to manually configure MAS or as input to the `suite_config` role.

**When to use**: Required if you want the role to generate an ObjectStorageCfg resource. If not set (along with `mas_instance_id`), the role will only provision the storage but not generate MAS configuration.

**Valid values**:
- Any valid local filesystem path (e.g., `~/masconfig`, `/opt/mas/config`)
- Directory will be created if it doesn't exist
- Should have write permissions
- Recommended to use an absolute path

**Impact**:
- ObjectStorageCfg YAML file is saved in this directory
- If not set, no ObjectStorageCfg will be generated (storage only)
- Required for subsequent MAS configuration steps
- Both this and `mas_instance_id` must be set for config generation

**Related variables**:
- [`mas_instance_id`](#mas_instance_id) - Both must be set for config generation
- Used consistently across all MAS DevOps roles for configuration storage

**Notes**:
- Use the same `mas_config_dir` across all MAS DevOps roles
- The generated file can be applied manually with `oc apply -f`
- Can be used as input to the `suite_config` role for automated configuration
- If you only want to provision storage without MAS config, leave this unset

### include_cluster_ingress_cert_chain
Controls whether to include the complete certificate chain in the ObjectStorageCfg.

- **Optional**
- Environment Variable: `INCLUDE_CLUSTER_INGRESS_CERT_CHAIN`
- Default Value: `False`

**Purpose**: When enabled, includes the complete TLS certificate chain from the cluster's ingress in the generated ObjectStorageCfg resource. This is useful when the cluster uses certificates from a trusted certificate authority.

**When to use**: Set to `True` when your OpenShift cluster's ingress uses certificates signed by a trusted CA and you want MAS to validate the complete certificate chain when accessing OCS.

**Valid values**:
- `True` - Include complete certificate chain in ObjectStorageCfg
- `False` - Include only the leaf certificate (default)

**Impact**:
- When `True`: ObjectStorageCfg includes full certificate chain for proper validation
- When `False`: Only the leaf certificate is included
- Primarily relevant for OCS (`cos_type=ocs`) with custom certificates
- Helps with certificate validation in environments with intermediate CAs

**Related variables**:
- [`cos_type`](#cos_type) - Most relevant for `ocs`
- [`ocp_ingress_tls_secret_name`](#ocp_ingress_tls_secret_name) - Source of certificates

**Notes**:
- Default `False` is sufficient for most deployments
- Enable if you experience certificate validation issues with OCS
- Not typically needed for IBM Cloud COS (`cos_type=ibm`)
- The certificate chain is extracted from the cluster's ingress configuration


## Example Playbook

Create the Ceph Object store on the existing OCS cluster and prepare the objectstorageCfg yaml to mas_config_dir.

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
