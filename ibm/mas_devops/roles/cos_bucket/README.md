# cos_bucket
This role extends support to create or deprovision Cloud Object Storage buckets.

## Role Variables
### cos_type
The Cloud Object Storage provider for bucket operations.

- **Required**
- Environment Variable: `COS_TYPE`
- Default Value: None

**Purpose**: Determines which object storage provider will be used for bucket creation or deletion. Different providers have different capabilities, APIs, and operational characteristics.

**When to use**: Always required when creating or deleting buckets. Choose based on your deployment platform and where your COS instance is hosted.

**Valid values**:
- `ibm` - IBM Cloud Object Storage buckets
- `aws` - AWS S3 buckets

**Impact**:
- **`ibm`**: Creates buckets in IBM Cloud COS, requires IBM Cloud API key and COS instance name
- **`aws`**: Creates buckets in AWS S3, requires AWS credentials (access key and secret key)
- Determines which set of configuration variables are required
- Affects bucket naming conventions, storage classes, and lifecycle policies

**Related variables**:
- When `cos_type=ibm`: Requires [`ibmcloud_apikey`](#ibmcloud_apikey), [`cos_instance_name`](#cos_instance_name), [`cos_bucket_storage_class`](#cos_bucket_storage_class)
- When `cos_type=aws`: Requires AWS credentials via environment or AWS CLI configuration, [`aws_region`](#aws_region)
- [`cos_bucket_action`](#cos_bucket_action) - Whether to create or delete the bucket

**Notes**:
- IBM COS buckets support advanced storage classes (smart, vault, cold, flex)
- AWS S3 buckets support versioning and encryption configurations
- Bucket names must be globally unique within each provider
- Choose the provider that matches your COS instance location

### cos_bucket_action
The action to perform on the bucket.

- **Required**
- Environment Variable: `COS_BUCKET_ACTION`
- Default Value: `create`

**Purpose**: Controls whether to create a new bucket or delete an existing one. This allows the same role to handle both lifecycle operations.

**When to use**:
- Use `create` (default) when setting up storage buckets for MAS workspaces or applications
- Use `delete` when cleaning up buckets after workspace or application removal

**Valid values**:
- `create` - Create a new bucket with specified configuration
- `delete` - Delete an existing bucket

**Impact**:
- **Create**: Creates bucket with specified storage class, region, and lifecycle policies
- **Delete**: Permanently removes the bucket and potentially its contents (depending on force deletion settings)
- Deletion is irreversible - all data in the bucket will be lost
- For AWS, deletion behavior depends on `aws_bucket_force_deletion_flag`

**Related variables**:
- [`cos_type`](#cos_type) - Determines which provider's bucket to create/delete
- [`cos_bucket_name`](#cos_bucket_name) or [`aws_bucket_name`](#aws_bucket_name) - Identifies which bucket to operate on
- [`aws_bucket_force_deletion_flag`](#aws_bucket_force_deletion_flag) - Controls AWS deletion behavior

**Notes**:
- Always backup data before deleting buckets
- IBM COS bucket deletion may fail if the bucket contains objects
- AWS bucket deletion can force-delete objects if versioning is disabled
- Verify the bucket name before deletion to avoid removing the wrong bucket

## Role Variables - IBM Cloud Object Storage buckets
### cos_bucket_name
The name for the IBM Cloud Object Storage bucket.

- **Optional** (IBM COS only)
- Environment Variable: `COS_BUCKET_NAME`
- Default Value: `<mas_instance_id>-<mas_workspace_id>-bucket`

**Purpose**: Specifies a custom name for the IBM Cloud COS bucket. Bucket names must be globally unique across all IBM Cloud COS instances.

**When to use**: Only relevant when `cos_type=ibm`. Provide a descriptive name or use the default which includes MAS instance and workspace IDs for uniqueness.

**Valid values**:
- 3-63 characters
- Lowercase letters, numbers, hyphens, and periods only
- Must start and end with a letter or number
- Must be globally unique across all IBM Cloud COS
- Cannot contain consecutive periods or hyphens
- Examples: `prod-mas-workspace1-bucket`, `dev-maximo-data-bucket`

**Impact**:
- Bucket name must be globally unique or creation will fail
- Used to identify the bucket for all operations
- Cannot be changed after creation (requires recreation)
- Appears in S3 API endpoints and URLs

**Related variables**:
- [`cos_type`](#cos_type) - Must be `ibm` for this to be used
- [`mas_instance_id`](#mas_instance_id) - Used in default name
- [`mas_workspace_id`](#mas_workspace_id) - Used in default name

**Notes**:
- Default naming includes instance and workspace IDs for uniqueness
- Bucket names are globally visible - avoid including sensitive information
- Use consistent naming conventions across all buckets
- Not used for AWS buckets (see `aws_bucket_name`)

### cos_bucket_storage_class
The IBM Cloud COS storage class for the bucket.

- **Optional** (IBM COS only)
- Environment Variable: `COS_BUCKET_STORAGE_CLASS`
- Default Value: `smart`

**Purpose**: Specifies the storage class tier for the IBM Cloud COS bucket, which determines pricing, performance, and data retrieval characteristics.

**When to use**: Only relevant when `cos_type=ibm`. Choose based on your data access patterns and cost requirements.

**Valid values**:
- `smart` - Automatically transitions data between hot and cool tiers based on access patterns (recommended)
- `vault` - For data accessed less than once per month, lower storage cost, higher retrieval cost
- `cold` - For data accessed less than once per year, lowest storage cost, highest retrieval cost
- `flex` - For dynamic workloads with unpredictable access patterns

**Impact**:
- Determines storage pricing and data retrieval costs
- `smart` provides automatic cost optimization without manual intervention
- Lower-tier classes (vault, cold) have higher retrieval costs and latency
- Cannot be changed after bucket creation (requires data migration)

**Related variables**:
- [`cos_type`](#cos_type) - Must be `ibm` for this to be used
- [`cos_bucket_region_location_type`](#cos_bucket_region_location_type) - Storage class availability varies by location type

**Notes**:
- `smart` is recommended for most MAS workloads (default)
- Consider data access patterns when choosing storage class
- Vault and cold classes suitable for backup and archival data
- Review IBM Cloud COS pricing for cost implications
- Not applicable for AWS buckets

### cos_instance_name
The name of the IBM Cloud COS instance where the bucket will be created.

- **Required** (IBM COS only)
- Environment Variable: `COS_INSTANCE_NAME`
- Default Value: None

**Purpose**: Identifies the specific IBM Cloud COS instance where the bucket will be created or deleted. This must match an existing COS instance in your IBM Cloud account.

**When to use**: Always required when `cos_type=ibm`. Must match the name of a COS instance provisioned by the `cos` role or created manually.

**Valid values**:
- Any valid IBM Cloud COS instance name in your account
- Must exist in the specified resource group
- Case-sensitive
- Examples: `Object Storage for MAS prod`, `mas-cos-instance`

**Impact**:
- Determines which COS instance will contain the bucket
- Incorrect name will cause bucket creation to fail
- All buckets in the same instance share the same service credentials
- Used to locate the instance for bucket operations

**Related variables**:
- [`cos_type`](#cos_type) - Must be `ibm` for this to be used
- [`ibmcloud_resourcegroup`](#ibmcloud_resourcegroup) - Resource group containing the instance
- [`ibmcloud_apikey`](#ibmcloud_apikey) - Must have access to this instance

**Notes**:
- The COS instance must be created before running this role
- Use the `cos` role to provision the COS instance first
- Verify the instance name in IBM Cloud console if unsure
- Not applicable for AWS buckets

### cos_location_info
The geographic location of the IBM Cloud COS instance.

- **Required** (IBM COS only)
- Environment Variable: `COS_LOCATION`
- Default Value: `global`

**Purpose**: Specifies the geographic scope of the IBM Cloud COS instance. This should match the location used when the COS instance was created.

**When to use**: Only relevant when `cos_type=ibm`. Should match the `cos_location_info` used in the `cos` role.

**Valid values**:
- `global` - Instance available globally
- Specific region codes: `us-south`, `us-east`, `eu-gb`, `eu-de`, etc.
- Cross-region: `us`, `eu`, `ap`

**Impact**:
- Must match the actual COS instance location
- Used to locate the correct COS instance
- Mismatch will cause bucket creation to fail

**Related variables**:
- [`cos_instance_name`](#cos_instance_name) - Instance in this location
- [`cos_bucket_region_location`](#cos_bucket_region_location) - Bucket's specific region

**Notes**:
- Default `global` works for most deployments
- Must match the location used when creating the COS instance
- Not applicable for AWS buckets

### cos_bucket_region_location_type
The resiliency type for the IBM Cloud COS bucket.

- **Required** (IBM COS only)
- Environment Variable: `COS_BUCKET_REGION_LOCATION_TYPE`
- Default Value: `cross_region_location`

**Purpose**: Defines the geographic distribution and resiliency level of the bucket. This determines data redundancy and availability characteristics.

**When to use**: Only relevant when `cos_type=ibm`. Choose based on your availability requirements and performance needs.

**Valid values**:
- `cross_region_location` - Data replicated across multiple regions (highest availability, default)
- `region_location` - Data stored in a single region (best performance, lower cost)
- `single_site_location` - Data stored in a single data center (lowest cost, lowest availability)

**Impact**:
- **cross_region**: Highest availability (99.99%), data replicated across 3+ regions, higher cost
- **region**: High availability (99.95%), data replicated within one region, balanced cost/performance
- **single_site**: Standard availability, lowest cost, suitable for non-critical data
- Determines which values are valid for `cos_bucket_region_location`
- Cannot be changed after bucket creation

**Related variables**:
- [`cos_bucket_region_location`](#cos_bucket_region_location) - Specific region(s) for the bucket
- [`cos_bucket_storage_class`](#cos_bucket_storage_class) - Storage class within the location type

**Notes**:
- `cross_region_location` recommended for production MAS workloads (default)
- `region_location` suitable for performance-sensitive workloads
- Consider compliance and data residency requirements
- Not applicable for AWS buckets

### cos_bucket_region_location
The specific region(s) for the IBM Cloud COS bucket.

- **Required** (IBM COS only)
- Environment Variable: `COS_BUCKET_REGION_LOCATION`
- Default Value: Derived from `ibmcloud_region` (e.g., `us`, `eu`, `ap`)

**Purpose**: Specifies the exact geographic region(s) where the bucket data will be stored. Valid values depend on the `cos_bucket_region_location_type`.

**When to use**: Only relevant when `cos_type=ibm`. Choose based on data residency requirements and proximity to users.

**Valid values**:
- **For `cross_region_location`**: `us`, `eu`, `ap`
- **For `region_location`**: `us-south`, `us-east`, `eu-gb`, `eu-de`, `jp-tok`, `au-syd`, `ca-tor`, `jp-osa`, `br-sao`
- **For `single_site_location`**: Specific data center codes

**Impact**:
- Determines physical location of data storage
- Affects data residency compliance (GDPR, data sovereignty)
- Influences network latency for data access
- Cannot be changed after bucket creation
- Must be compatible with `cos_bucket_region_location_type`

**Related variables**:
- [`cos_bucket_region_location_type`](#cos_bucket_region_location_type) - Determines valid values
- [`ibmcloud_region`](#ibmcloud_region) - Used to derive default cross-region location
- [`cos_url`](#cos_url) - Should match the region for optimal performance

**Notes**:
- Default automatically selects cross-region based on `ibmcloud_region`
- For `cross_region_location`, `us` covers US regions, `eu` covers Europe, `ap` covers Asia-Pacific
- Consider compliance requirements when selecting region
- Not applicable for AWS buckets

### ibmcloud_region
The IBM Cloud region used to derive the default cross-region location.

- **Optional** (IBM COS only)
- Environment Variable: `IBMCLOUD_REGION`
- Default Value: `us-east`

**Purpose**: Provides a hint for automatically determining the appropriate cross-region location when `cos_bucket_region_location` is not explicitly set.

**When to use**: Only relevant when `cos_type=ibm` and using `cross_region_location` type without explicitly setting `cos_bucket_region_location`.

**Valid values**:
- Any valid IBM Cloud region identifier
- Examples: `us-east`, `us-south`, `eu-gb`, `eu-de`, `jp-tok`
- Used to derive cross-region: `us-*` → `us`, `eu-*` → `eu`, `jp-*` or `au-*` → `ap`

**Impact**:
- Automatically determines cross-region location if not explicitly set
- `us-*` regions default to `us` cross-region
- `eu-*` regions default to `eu` cross-region
- `jp-*` and `au-*` regions default to `ap` cross-region

**Related variables**:
- [`cos_bucket_region_location`](#cos_bucket_region_location) - Can override the derived value
- [`cos_bucket_region_location_type`](#cos_bucket_region_location_type) - Only used for cross-region type

**Notes**:
- Only used when `cos_bucket_region_location` is not explicitly set
- Provides convenience for cross-region bucket creation
- Not applicable for AWS buckets

### cos_url
The IBM Cloud COS S3 API endpoint URL.

- **Required** (IBM COS only, for bucket creation)
- Environment Variable: `COS_REGION_LOCATION_URL`
- Default Value: `https://s3.<region>.cloud-object-storage.appdomain.cloud`

**Purpose**: Specifies the S3-compatible API endpoint for accessing the IBM Cloud COS bucket. This URL is used for all bucket operations.

**When to use**: Only relevant when `cos_type=ibm`. Should match the bucket's region location for optimal performance.

**Valid values**:
- Regional endpoints: `https://s3.<region>.cloud-object-storage.appdomain.cloud`
- Cross-region endpoints: `https://s3.us.cloud-object-storage.appdomain.cloud`, `https://s3.eu.cloud-object-storage.appdomain.cloud`, `https://s3.ap.cloud-object-storage.appdomain.cloud`
- Private endpoints: `https://s3.private.<region>.cloud-object-storage.appdomain.cloud`
- Direct endpoints: `https://s3.direct.<region>.cloud-object-storage.appdomain.cloud`

**Impact**:
- Determines which IBM Cloud COS endpoint is used for bucket operations
- Affects network latency and data transfer costs
- Private endpoints provide better security and lower costs for in-cloud access
- Must be accessible from where the role is executed

**Related variables**:
- [`cos_bucket_region_location`](#cos_bucket_region_location) - Should align with the endpoint region
- [`cos_type`](#cos_type) - Must be `ibm` for this to be used

**Notes**:
- Default automatically constructed based on `cos_bucket_region_location`
- Use regional endpoints matching your bucket location for best performance
- Private endpoints recommended for OpenShift clusters in IBM Cloud
- Not applicable for AWS buckets (see `aws_url`)

### cos_resource_key_iam_role
The IAM role for COS service credentials created during bucket setup.

- **Optional** (IBM COS only)
- Environment Variable: `COS_RESOURCE_KEY_IAM_ROLE`
- Default Value: `Manager`

**Purpose**: Specifies the IAM role level for service credentials that may be created during bucket operations. This determines the permissions granted for accessing the bucket.

**When to use**: Only relevant when `cos_type=ibm`. The default `Manager` role provides full access required for bucket operations.

**Valid values**:
- `Manager` - Full access to buckets and objects (create/read/update/delete)
- `Writer` - Read and write access to objects
- `Reader` - Read-only access to objects

**Impact**:
- Determines permissions for any service credentials created
- `Manager` role required for full bucket management
- Lower privilege roles may limit functionality

**Related variables**:
- [`cos_type`](#cos_type) - Must be `ibm` for this to be used
- [`cos_instance_name`](#cos_instance_name) - Instance where credentials are created

**Notes**:
- Default `Manager` role is recommended
- Not applicable for AWS buckets

### ibmcloud_apikey
The IBM Cloud API key for bucket operations.

- **Required** (IBM COS only)
- Environment Variable: `IBMCLOUD_APIKEY`
- Default Value: None

**Purpose**: Provides authentication credentials for IBM Cloud to create and manage COS buckets.

**When to use**: Always required when `cos_type=ibm`. Must have permissions to manage buckets in the specified COS instance.

**Valid values**:
- A valid IBM Cloud API key with COS permissions
- Must have access to the COS instance and resource group
- Format: 44-character alphanumeric string

**Impact**:
- Authenticates all IBM Cloud COS operations
- Determines which account owns the bucket
- Required permissions: COS bucket management, resource group access

**Related variables**:
- [`cos_type`](#cos_type) - Must be `ibm` for this to be used
- [`ibmcloud_resourcegroup`](#ibmcloud_resourcegroup) - Must have access to this resource group
- [`cos_instance_name`](#cos_instance_name) - Must have access to this instance

**Notes**:
- Store API keys securely
- Never commit API keys to version control
- Not applicable for AWS buckets

### ibmcloud_resourcegroup
The IBM Cloud resource group containing the COS instance.

- **Optional** (IBM COS only)
- Environment Variable: `IBMCLOUD_RESOURCEGROUP`
- Default Value: `Default`

**Purpose**: Specifies the resource group where the COS instance is located.

**When to use**: Only relevant when `cos_type=ibm`. Should match the resource group used when creating the COS instance.

**Valid values**:
- Any existing resource group name in your IBM Cloud account
- Common examples: `Default`, `Production`, `MAS-Resources`
- Case-sensitive

**Impact**:
- Used to locate the COS instance
- Must match the actual resource group of the COS instance
- API key must have access to this resource group

**Related variables**:
- [`ibmcloud_apikey`](#ibmcloud_apikey) - Must have access to this resource group
- [`cos_instance_name`](#cos_instance_name) - Instance in this resource group

**Notes**:
- Defaults to `Default` resource group
- Must match the resource group used in the `cos` role
- Not applicable for AWS buckets

## Role Variables - AWS S3 Buckets

To run this role successfully for AWS s3 buckets, you must have already installed the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).
Also, you need to have AWS user credentials configured via `aws configure` command or simply export `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables with your corresponding AWS username credentials prior running this role.

### aws_bucket_name
The name for the AWS S3 bucket.

- **Optional** (AWS S3 only)
- Environment Variable: `COS_BUCKET_NAME`
- Default Value: `<mas_instance_id>-<mas_workspace_id>-bucket`

**Purpose**: Specifies a custom name for the AWS S3 bucket. Bucket names must be globally unique across all AWS S3 buckets worldwide.

**When to use**: Only relevant when `cos_type=aws`. Provide a descriptive name or use the default which includes MAS instance and workspace IDs for uniqueness.

**Valid values**:
- 3-63 characters
- Lowercase letters, numbers, hyphens, and periods only
- Must start and end with a letter or number
- Must be globally unique across all AWS S3
- Cannot contain consecutive periods or underscores
- Cannot be formatted as an IP address
- Examples: `prod-mas-workspace1-bucket`, `dev-maximo-data-bucket`

**Impact**:
- Bucket name must be globally unique or creation will fail
- Used to identify the bucket for all operations
- Cannot be changed after creation (requires recreation)
- Appears in S3 API endpoints and URLs

**Related variables**:
- [`cos_type`](#cos_type) - Must be `aws` for this to be used
- [`mas_instance_id`](#mas_instance_id) - Used in default name
- [`mas_workspace_id`](#mas_workspace_id) - Used in default name
- [`aws_region`](#aws_region) - Region where the bucket is created

**Notes**:
- Default naming includes instance and workspace IDs for uniqueness
- Bucket names are globally visible - avoid including sensitive information
- Use consistent naming conventions across all buckets
- Not used for IBM COS buckets (see `cos_bucket_name`)

### aws_region
The AWS region where the S3 bucket will be created.

- **Required** (AWS S3 only)
- Environment Variable: `AWS_REGION`
- Default Value: `us-east-2`

**Purpose**: Specifies the AWS region for S3 bucket creation. This determines the physical location of the bucket and affects latency and data residency.

**When to use**: Always required when `cos_type=aws`. Choose a region close to your OpenShift cluster and users for optimal performance.

**Valid values**:
- Any valid AWS region identifier
- Examples: `us-east-1`, `us-east-2`, `us-west-2`, `eu-west-1`, `eu-central-1`, `ap-southeast-1`
- Must be a region where your AWS account has access

**Impact**:
- Determines physical location of bucket storage
- Affects data residency compliance (GDPR, data sovereignty)
- Influences network latency for data access
- Cannot be changed after bucket creation (requires data migration)
- Affects pricing (varies by region)

**Related variables**:
- [`cos_type`](#cos_type) - Must be `aws` for this to be used
- [`aws_bucket_name`](#aws_bucket_name) - Bucket created in this region
- [`aws_url`](#aws_url) - Should match the region

**Notes**:
- Choose a region close to your OpenShift cluster for best performance
- Consider compliance and data residency requirements
- Some regions may have capacity constraints
- Not applicable for IBM COS buckets

### aws_bucket_versioning_flag
Controls whether to enable versioning for the AWS S3 bucket.

- **Optional** (AWS S3 only)
- Environment Variable: `COS_BUCKET_VERSIONING_FLAG`
- Default Value: `True`

**Purpose**: Determines if S3 versioning should be enabled for the bucket. Versioning keeps multiple variants of an object in the same bucket, providing protection against accidental deletion or overwrite.

**When to use**: Only relevant when `cos_type=aws`. Enable for production buckets to protect against accidental data loss.

**Valid values**:
- `True` - Enable versioning (recommended for production)
- `False` - Disable versioning

**Impact**:
- When `True`: All object versions are retained, providing rollback capability
- When `False`: Only the latest version of each object is kept
- Versioning increases storage costs (all versions consume space)
- Once enabled, versioning cannot be fully disabled (only suspended)
- Affects `aws_bucket_force_deletion_flag` behavior

**Related variables**:
- [`cos_type`](#cos_type) - Must be `aws` for this to be used
- [`aws_bucket_force_deletion_flag`](#aws_bucket_force_deletion_flag) - Cannot force-delete if versioning is enabled

**Notes**:
- Recommended to enable for production buckets
- Provides protection against accidental deletion
- Increases storage costs due to version retention
- Consider lifecycle policies to manage old versions
- Not applicable for IBM COS buckets

### aws_bucket_encryption
The encryption configuration for the AWS S3 bucket.

- **Optional** (AWS S3 only)
- Environment Variable: `COS_BUCKET_ENCRYPTION`
- Default Value: None

**Purpose**: Specifies the default server-side encryption configuration for objects stored in the S3 bucket. This ensures data is encrypted at rest.

**When to use**: Only relevant when `cos_type=aws`. Set this to enforce encryption for all objects in the bucket.

**Valid values**:
- JSON-formatted string defining encryption rules
- Example for AES256: `'{"Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]}'`
- Example for KMS: `'{"Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "aws:kms", "KMSMasterKeyID": "arn:aws:kms:region:account:key/key-id"}}]}'`
- Supported algorithms: `AES256` (S3-managed keys), `aws:kms` (KMS-managed keys)

**Impact**:
- When set: All objects uploaded to the bucket are automatically encrypted
- When not set: Encryption must be specified per-object or not used
- KMS encryption provides additional key management and audit capabilities
- KMS encryption incurs additional costs

**Related variables**:
- [`cos_type`](#cos_type) - Must be `aws` for this to be used
- [`aws_bucket_name`](#aws_bucket_name) - Bucket where encryption is applied

**Notes**:
- Recommended for production buckets containing sensitive data
- AES256 is simpler and has no additional cost
- KMS provides better key management and audit trails
- Encryption can be changed after bucket creation
- Not applicable for IBM COS buckets

### aws_bucket_force_deletion_flag
Controls whether to force-delete bucket contents before deleting the bucket.

- **Optional** (AWS S3 only)
- Environment Variable: `COS_BUCKET_FORCE_DELETION_FLAG`
- Default Value: `True`

**Purpose**: When deleting an AWS S3 bucket, this flag determines whether to automatically delete all objects in the bucket first. This only works if versioning is disabled.

**When to use**: Only relevant when `cos_type=aws` and `cos_bucket_action=delete`. Enable to automatically clean up bucket contents during deletion.

**Valid values**:
- `True` - Automatically delete all objects before deleting the bucket (default)
- `False` - Fail if bucket contains objects (safer, requires manual cleanup)

**Impact**:
- When `True`: All objects in the bucket are permanently deleted before bucket deletion
- When `False`: Bucket deletion fails if it contains any objects
- **Only works if versioning is disabled** - versioned buckets cannot be force-deleted
- Deletion is irreversible - all data will be lost

**Related variables**:
- [`cos_type`](#cos_type) - Must be `aws` for this to be used
- [`cos_bucket_action`](#cos_bucket_action) - Must be `delete` for this to take effect
- [`aws_bucket_versioning_flag`](#aws_bucket_versioning_flag) - Must be `False` for force deletion to work

**Notes**:
- **WARNING**: Force deletion permanently removes all data
- Does not work with versioned buckets - disable versioning first
- Consider backing up data before force deletion
- Setting to `False` is safer but requires manual object cleanup
- Not applicable for IBM COS buckets

## Example Playbook

Create the IBM Cloud Object storage bucket.
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    cos_type: ibm
    cos_bucket_action: create
    cos_bucket_name: my-ibm-bucket
    cos_instance_name: my-ibmcos-instance-name
    ibmcloud_apikey: my-ibm-cloud-apikey
  roles:
    - ibm.mas_devops.cos_bucket
```

Create the AWS S3 storage bucket.
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    cos_type: aws
    cos_bucket_action: create
    aws_bucket_name: my-aws-bucket
    aws_region: us-east-2
    aws_bucket_versioning_flag: True
    aws_bucket_encryption: '{"Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]}'
  roles:
    - ibm.mas_devops.cos_bucket
```

## License

EPL-2.0
