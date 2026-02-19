# cis

This role provides support for Configuring IBM Cloud Internet Services. During CIS provisioning it performs four tasks during provisioning in given order:

1. Provision CIS Instance in customer account
2. Add customer domain to customer's CIS Instance
3. Configure Domain settings in customer CIS Instance
4. Add DNS Records of type `NS` for customer's Domain nameservers to Master CIS Account

During CIS Instance deprovisioning role will perform following tasks:

1. Delete DNS Record from Master Account
2. Delete Domain from Customer Account
3. Delete Customer CIS Instance

## Role Variables

### cis_action
The action to perform on the Cloud Internet Services instance.

- **Required**
- Environment Variable: `CIS_ACTION`
- Default Value: `provision`

**Purpose**: Controls whether to provision a new CIS instance with domain configuration or deprovision an existing one. This enables the same role to handle both lifecycle operations.

**When to use**:
- Use `provision` (default) when setting up DNS and CDN services for a new MAS deployment
- Use `deprovision` when cleaning up CIS resources after MAS uninstallation

**Valid values**:
- `provision` - Create CIS instance, add domain, configure settings, and add NS records to master account
- `deprovision` - Delete DNS records from master account, remove domain, and delete CIS instance

**Impact**:
- **Provision**: Creates a complete CIS setup with domain delegation from master account
- **Deprovision**: Permanently removes all CIS resources and DNS records (irreversible)
- Provisioning requires coordination between customer and master IBM Cloud accounts
- Deprovisioning must be done before removing the OpenShift cluster

**Related variables**:
- [`cis_plan`](#cis_plan) - Service plan for provisioning
- [`master_cis_base_domain`](#master_cis_base_domain) - Master domain for NS record delegation
- [`ibmcloud_apikey`](#ibmcloud_apikey) - Customer account credentials
- [`master_ibmcloud_api_key`](#master_ibmcloud_api_key) - Master account credentials

**Notes**:
- Provisioning creates a multi-account DNS delegation architecture
- Deprovisioning removes DNS records that may still be in use - verify before proceeding
- The role performs operations in a specific order to maintain DNS consistency
- Failed provisioning may require manual cleanup in IBM Cloud console

### cis_plan
The IBM Cloud Internet Services plan type to provision.

- **Required**
- Environment Variable: `CIS_PLAN`
- Default Value: `standard`

**Purpose**: Specifies the CIS service plan tier, which determines available features, performance limits, and pricing for the CIS instance.

**When to use**: The default `standard` plan is suitable for most MAS deployments. Consider `enterprise` plan for production deployments requiring advanced features or higher limits.

**Valid values**:
- `standard` - Standard plan with basic CDN, DDoS protection, and DNS features
- `enterprise` - Enterprise plan with advanced security, performance, and support features
- Plan availability and features may vary by region

**Impact**:
- Determines available CIS features (WAF rules, rate limiting, page rules, etc.)
- Affects pricing and billing for the CIS instance
- Enterprise plan provides higher performance limits and SLA guarantees
- Cannot be changed after provisioning (requires recreation)

**Related variables**:
- [`cis_action`](#cis_action) - Must be `provision` for this to take effect
- [`ibmcloud_resourcegroup`](#ibmcloud_resourcegroup) - Resource group for billing

**Notes**:
- Standard plan is sufficient for most development and test environments
- Enterprise plan recommended for production deployments with high traffic
- Review IBM Cloud CIS pricing before selecting a plan
- Plan features include DNS, CDN, DDoS protection, WAF, and load balancing

### ibmcloud_apikey
The IBM Cloud API key for the customer account where CIS will be provisioned.

- **Required**
- Environment Variable: `IBMCLOUD_APIKEY`
- Default Value: None

**Purpose**: Provides authentication credentials for the customer's IBM Cloud account where the CIS instance will be created and managed.

**When to use**: Always required for both provisioning and deprovisioning operations. This API key must have permissions to create and manage CIS instances in the specified resource group.

**Valid values**:
- A valid IBM Cloud API key with CIS service permissions
- Must have Editor or Administrator role on the CIS service
- Must have access to the specified resource group
- Format: 44-character alphanumeric string

**Impact**:
- Authenticates all operations in the customer's IBM Cloud account
- Determines which account owns the CIS instance and incurs charges
- Required permissions: CIS service management, resource group access
- Invalid or expired keys will cause provisioning to fail

**Related variables**:
- [`ibmcloud_resourcegroup`](#ibmcloud_resourcegroup) - Resource group where CIS is created
- [`master_ibmcloud_api_key`](#master_ibmcloud_api_key) - Separate key for master account operations

**Notes**:
- Store API keys securely using environment variables or secrets management
- Never commit API keys to version control
- Consider using service IDs with restricted permissions instead of user API keys
- Rotate API keys regularly for security best practices
- The customer account will be billed for CIS usage

### ibmcloud_resourcegroup
The IBM Cloud resource group that will own the CIS instance.

- **Optional**
- Environment Variable: `IBMCLOUD_RESOURCEGROUP`
- Default Value: `Default`

**Purpose**: Specifies the resource group in the customer's IBM Cloud account where the CIS instance will be created. Resource groups are used for access control and billing organization.

**When to use**: Set this to organize CIS resources within a specific resource group, especially in accounts with multiple projects or teams. Use the default `Default` resource group for simple deployments.

**Valid values**:
- Any existing resource group name in your IBM Cloud account
- Common examples: `Default`, `Production`, `Development`, `MAS-Resources`
- Resource group must exist before provisioning
- Case-sensitive

**Impact**:
- Determines billing and cost allocation for the CIS instance
- Controls IAM access policies and permissions
- Affects resource organization in IBM Cloud console
- Cannot be changed after CIS instance creation

**Related variables**:
- [`ibmcloud_apikey`](#ibmcloud_apikey) - Must have access to this resource group
- [`master_cis_resource_group`](#master_cis_resource_group) - Resource group in master account

**Notes**:
- Ensure the API key has access to the specified resource group
- Use consistent resource groups across all MAS-related services
- Resource groups help with cost tracking and access management
- The `Default` resource group is created automatically in all IBM Cloud accounts

### master_ibmcloud_api_key
The IBM Cloud API key for the master account that hosts the base domain.

- **Required**
- Environment Variable: `MASTER_IBMCLOUD_APIKEY`
- Default Value: None

**Purpose**: Provides authentication credentials for the master IBM Cloud account where the base domain's CIS instance is hosted. This is required to create NS (nameserver) records that delegate the subdomain to the customer's CIS instance.

**When to use**: Always required for provisioning. The master account typically belongs to the organization managing the base domain (e.g., `mas.ibm.com`) and delegates subdomains to customer accounts.

**Valid values**:
- A valid IBM Cloud API key for the master account
- Must have permissions to manage DNS records in the master CIS instance
- Must have access to the master CIS resource group
- Format: 44-character alphanumeric string

**Impact**:
- Enables DNS delegation from master domain to customer subdomain
- Required to create NS records pointing to customer's CIS nameservers
- Without this, the customer's domain will not be resolvable
- Used only during provisioning and deprovisioning operations

**Related variables**:
- [`master_cis_resource_group`](#master_cis_resource_group) - Resource group in master account
- [`master_cis_resource_name`](#master_cis_resource_name) - Master CIS instance name
- [`master_cis_base_domain`](#master_cis_base_domain) - Base domain in master account
- [`ibmcloud_apikey`](#ibmcloud_apikey) - Customer account API key (separate)

**Notes**:
- This is a separate API key from the customer account key
- Typically provided by the organization managing the master domain
- Store securely as it has access to the master DNS infrastructure
- Only needs DNS record management permissions, not full CIS access
- Required for multi-tenant MAS deployments with domain delegation

### master_cis_resource_group
The resource group in the master account that owns the master CIS instance.

- **Required**
- Environment Variable: `MASTER_CIS_RESOURCE_GROUP`
- Default Value: `manager`

**Purpose**: Identifies the resource group in the master IBM Cloud account where the master CIS instance (hosting the base domain) is located.

**When to use**: Required when the master CIS instance is not in the default resource group. This is typically set by the organization managing the master domain infrastructure.

**Valid values**:
- Any valid resource group name in the master IBM Cloud account
- Common values: `manager`, `Default`, `DNS-Infrastructure`
- Must match the actual resource group of the master CIS instance
- Case-sensitive

**Impact**:
- Used to locate the master CIS instance for NS record creation
- Incorrect value will cause DNS delegation to fail
- Must match the resource group where `master_cis_resource_name` exists

**Related variables**:
- [`master_ibmcloud_api_key`](#master_ibmcloud_api_key) - Must have access to this resource group
- [`master_cis_resource_name`](#master_cis_resource_name) - CIS instance in this resource group
- [`master_cis_base_domain`](#master_cis_base_domain) - Domain hosted in this CIS instance

**Notes**:
- Default value `manager` is commonly used in IBM MAS deployments
- Verify the correct resource group with the master account administrator
- The master API key must have access to this resource group
- This is in the master account, not the customer account

### master_cis_resource_name
The name of the master CIS instance in the master account.

- **Required**
- Environment Variable: `MASTER_CIS_RESOURCE_NAME`
- Default Value: `<mas_instance_id>-cis`

**Purpose**: Identifies the specific CIS instance in the master account that hosts the base domain. This instance will receive the NS records for subdomain delegation.

**When to use**: The default value is usually sufficient, but can be overridden if the master CIS instance has a different naming convention.

**Valid values**:
- Any valid CIS instance name in the master account
- Default format: `<mas_instance_id>-cis` (e.g., `prod-cis`, `dev-cis`)
- Must match an existing CIS instance in the master account
- Case-sensitive

**Impact**:
- Used to locate the correct CIS instance for NS record creation
- Incorrect value will cause DNS delegation to fail
- Must exist in the `master_cis_resource_group`

**Related variables**:
- [`mas_instance_id`](#mas_instance_id) - Used to generate default name
- [`master_cis_resource_group`](#master_cis_resource_group) - Resource group containing this instance
- [`master_cis_base_domain`](#master_cis_base_domain) - Domain hosted in this instance

**Notes**:
- Verify the correct instance name with the master account administrator
- The default naming convention uses the MAS instance ID
- This instance must already exist in the master account
- Used only for NS record management, not for creating the instance

### master_cis_base_domain
The base domain hosted in the master CIS instance.

- **Required**
- Environment Variable: `MASTER_CIS_BASE_DOMAIN`
- Default Value: None

**Purpose**: Specifies the parent domain in the master CIS instance under which the customer's subdomain will be delegated. This is the domain that will contain the NS records pointing to the customer's CIS nameservers.

**When to use**: Always required for provisioning. This is typically a domain like `mas.ibm.com` or `maximo.company.com` that is managed centrally and delegates subdomains to individual deployments.

**Valid values**:
- A valid domain name hosted in the master CIS instance
- Must be a domain you control and have configured in the master CIS
- Examples: `mas.ibm.com`, `maximo.example.com`, `apps.company.com`
- Should not include protocol (http/https) or trailing slashes

**Impact**:
- Customer's domain will be created as a subdomain of this base domain
- NS records will be created in this domain to delegate to customer's CIS
- The full customer domain will be `<cluster_name>.<mas_instance_id>.<master_cis_base_domain>`
- Must be properly configured in the master CIS instance

**Related variables**:
- [`cluster_name`](#cluster_name) - First part of the subdomain
- [`mas_instance_id`](#mas_instance_id) - Second part of the subdomain
- [`master_cis_resource_name`](#master_cis_resource_name) - CIS instance hosting this domain

**Notes**:
- This domain must already exist and be active in the master CIS instance
- Verify DNS propagation of the base domain before provisioning
- The base domain typically belongs to the organization, not individual customers
- Example: If base domain is `mas.ibm.com`, customer domain might be `cluster1.prod.mas.ibm.com`

### mas_instance_id
The MAS instance identifier used in naming the CIS service and domain.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

**Purpose**: Provides a unique identifier for the MAS instance, used to generate the CIS service name and as part of the domain name structure. This ensures uniqueness across multiple MAS deployments.

**When to use**: Always required. Should match the MAS instance ID used throughout your MAS deployment for consistency.

**Valid values**:
- Alphanumeric string, typically 3-12 characters
- Common examples: `prod`, `dev`, `test`, `masinst1`, `mas-prod-01`
- Should be unique within your organization
- Lowercase recommended for DNS compatibility

**Impact**:
- Used to generate default CIS instance name: `<mas_instance_id>-cis`
- Forms part of the domain name: `<cluster_name>.<mas_instance_id>.<base_domain>`
- Appears in resource names and tags for identification
- Should remain consistent across all MAS components

**Related variables**:
- [`cluster_name`](#cluster_name) - Combined with this to form the full domain
- [`master_cis_resource_name`](#master_cis_resource_name) - Defaults to `<mas_instance_id>-cis`
- [`master_cis_base_domain`](#master_cis_base_domain) - Base domain for the subdomain

**Notes**:
- Use the same `mas_instance_id` across all MAS DevOps roles
- Choose a meaningful identifier that indicates the environment or purpose
- Cannot be changed after provisioning without recreating resources
- Appears in DNS names, so keep it short and DNS-compatible

### cluster_name
The OpenShift cluster name used as a prefix in the domain name.

- **Required**
- Environment Variable: `CLUSTER_NAME`
- Default Value: None

**Purpose**: Identifies the specific OpenShift cluster for this CIS configuration. Used as the first component of the subdomain name, allowing multiple clusters to share the same MAS instance ID.

**When to use**: Always required. Should match the OpenShift cluster name used in your deployment.

**Valid values**:
- Alphanumeric string with hyphens
- Common examples: `ocp-prod`, `rosa-cluster`, `roks-dev`, `cluster1`
- Should be unique within the MAS instance
- Lowercase recommended for DNS compatibility

**Impact**:
- Forms the first part of the domain: `<cluster_name>.<mas_instance_id>.<base_domain>`
- Used to generate the CIS service name
- Helps identify which cluster the CIS instance serves
- Appears in DNS records and resource names

**Related variables**:
- [`mas_instance_id`](#mas_instance_id) - Combined with this to form the full domain
- [`master_cis_base_domain`](#master_cis_base_domain) - Base domain for the subdomain

**Notes**:
- Should match your OpenShift cluster name for consistency
- Multiple clusters can use the same `mas_instance_id` with different `cluster_name` values
- Keep it short and DNS-compatible (no special characters except hyphens)
- Example: cluster_name=`rosa-prod`, mas_instance_id=`mas01`, base=`ibm.com` → `rosa-prod.mas01.ibm.com`

### mas_config_dir
Local directory where generated CIS configuration will be saved.

- **Required**
- Environment Variable: `MAS_CONFIG_DIR`
- Default Value: None

**Purpose**: Specifies the local directory path where the role will save generated Kubernetes ConfigMaps and CIS instance details for use by other MAS components.

**When to use**: Always required. This directory serves as the central location for all MAS configuration artifacts and should be consistent across all MAS DevOps roles.

**Valid values**:
- Any valid local filesystem path (e.g., `~/masconfig`, `/opt/mas/config`)
- Directory will be created if it doesn't exist
- Should have write permissions for the user running the playbook
- Recommended to use an absolute path for consistency

**Impact**:
- CIS instance details are saved as ConfigMap YAML files in this directory
- Required for subsequent MAS installation and configuration steps
- Other roles will read CIS configuration from this location
- Should be backed up as it contains important configuration data

**Related variables**:
- Used by all MAS DevOps roles for consistent configuration storage
- CIS-specific files will be created with identifiable names

**Notes**:
- Use the same `mas_config_dir` across all MAS DevOps roles for consistency
- Ensure the directory is accessible and has sufficient storage space
- Consider using version control for the configuration directory (excluding sensitive data)
- The directory structure follows MAS configuration conventions
- ConfigMaps generated here are applied to the OpenShift cluster during MAS installation

## Example Playbook
Create CIS Instance alongwith save Instance details in MAS_CONFIG_DIR path as ConfigMap

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    cis_action: provision
    mas_instance_id: masinst1
    mas_config_dir: ~/masconfig
    ibmcloud_apikey: "****"
    master_ibmcloud_api_key: "******"
    cluster_name: "test"
  roles:
    - ibm.mas_devops.cis
```

## License

EPL-2.0
