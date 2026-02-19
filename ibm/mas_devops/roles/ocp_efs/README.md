ocp_efs
===============================================================================

Provision and configure AWS Elastic File System (EFS) storage for Red Hat OpenShift Service on AWS (ROSA) clusters. This role automates the complete EFS setup including security group configuration, EFS instance creation, access points, mount targets, and StorageClass creation.

EFS provides ReadWriteMany (RWX) persistent storage essential for MAS applications that require shared file access across multiple pods, such as Manage attachments and customer files.

The role performs the following operations:
1. Configures security group inbound rules for NFS access
2. Creates EFS file system in the cluster's VPC
3. Establishes mount targets in all availability zones
4. Creates access points for isolated storage
5. Deploys EFS CSI driver and StorageClass


Role Variables
-------------------------------------------------------------------------------

### aws_access_key_id
AWS access key ID for authentication.

- **Required**
- Environment Variable: `AWS_ACCESS_KEY_ID`
- Default: None

**Purpose**: Provides AWS credentials for creating and configuring EFS resources via AWS CLI.

**When to use**: Always required. Must have permissions to create EFS, modify security groups, and manage VPC resources.

**Valid values**: Valid AWS access key ID (20-character alphanumeric string).

**Impact**: Used to authenticate all AWS API calls. Insufficient permissions will cause provisioning failures.

**Related variables**: `aws_secret_access_key`, `aws_region`

**Notes**:
- Requires IAM permissions for EFS, EC2, and VPC operations
- Consider using IAM roles instead of access keys for better security
- Store credentials securely, never commit to version control

### aws_secret_access_key
AWS secret access key for authentication.

- **Required**
- Environment Variable: `AWS_SECRET_ACCESS_KEY`
- Default: None

**Purpose**: Provides the secret key component of AWS credentials for API authentication.

**When to use**: Always required. Must correspond to the `aws_access_key_id`.

**Valid values**: Valid AWS secret access key (40-character alphanumeric string).

**Impact**: Used with access key ID to authenticate AWS API calls. Incorrect key will cause authentication failures.

**Related variables**: `aws_access_key_id`, `aws_region`

**Notes**:
- Keep secret key secure and never expose in logs or version control
- Rotate credentials regularly per security best practices
- Consider using AWS STS temporary credentials for enhanced security

### aws_region
AWS region where the EFS instance will be provisioned.

- Optional
- Environment Variable: `AWS_DEFAULT_REGION`
- Default: `eu-west-2`

**Purpose**: Specifies the AWS region for EFS provisioning. Must match the ROSA cluster's region.

**When to use**: Always set to match your ROSA cluster's region. Default is suitable for EU deployments.

**Valid values**: Valid AWS region code (e.g., `us-east-1`, `eu-west-2`, `ap-southeast-1`). Common values:
- `us-east-1` - US East (N. Virginia)
- `us-west-2` - US West (Oregon)
- `eu-west-1` - Europe (Ireland)
- `eu-west-2` - Europe (London)
- `ap-southeast-1` - Asia Pacific (Singapore)

**Impact**: EFS must be in the same region as the ROSA cluster. Cross-region access is not supported.

**Related variables**: `cluster_name`

**Notes**:
- **Critical**: Must match ROSA cluster region exactly
- Verify cluster region: `rosa describe cluster -c <cluster-name>`
- EFS pricing varies by region

### cluster_name
Name of the ROSA cluster to attach EFS storage.

- **Required**
- Environment Variable: `CLUSTER_NAME`
- Default: None

**Purpose**: Identifies the target ROSA cluster for EFS integration. Used to locate the cluster's VPC and configure security groups.

**When to use**: Always required. Must be the exact name of an existing ROSA cluster.

**Valid values**: Valid ROSA cluster name as shown in `rosa list clusters`.

**Impact**: The role uses this name to find the cluster's VPC ID and configure EFS mount targets in the correct network.

**Related variables**: `aws_region`, `efs_unique_id`

**Notes**:
- Cluster must exist before running this role
- Name is case-sensitive
- Verify cluster name: `rosa list clusters`
- Used to tag AWS resources for cost tracking

### efs_unique_id
Unique identifier for the EFS instance and StorageClass.

- Optional
- Environment Variable: `EFS_UNIQUE_ID`
- Default: Value of `cluster_name`

**Purpose**: Provides a unique identifier used in EFS resource naming and StorageClass creation. Enables multiple EFS instances per cluster.

**When to use**: Set when you need multiple EFS instances in the same cluster, or want a more descriptive name than the cluster name.

**Valid values**: Alphanumeric string, typically lowercase (e.g., `mas-prod`, `manage-storage`, `shared-files`).

**Impact**:
- StorageClass will be named `efs-<efs_unique_id>`
- EFS file system will be tagged with this identifier
- Creation tokens will include this identifier

**Related variables**: `cluster_name`, `creation_token_prefix`, `create_storage_class`

**Notes**:
- Defaults to cluster name if not specified
- Use descriptive names for multiple EFS instances (e.g., `mas-attachments`, `mas-logs`)
- Must be unique within the cluster if creating multiple EFS instances

### creation_token_prefix
Prefix for AWS resource creation tokens.

- Optional
- Environment Variable: `CREATION_TOKEN_PREFIX`
- Default: `mas_devops.`

**Purpose**: Provides a prefix for creation tokens used to ensure idempotency of AWS resource creation.

**When to use**: Customize to identify resources created by this automation or to avoid conflicts with other tools.

**Valid values**: String prefix, typically ending with a dot or dash (e.g., `mas_devops.`, `myorg-`, `prod_`).

**Impact**: Creation tokens are built by concatenating this prefix with `efs_unique_id`. Used for idempotent resource creation.

**Related variables**: `efs_unique_id`

**Notes**:
- Default `mas_devops.` identifies resources created by this collection
- Helps track resource provenance in AWS
- Change if you need to distinguish from other automation tools

### create_storage_class
Enable automatic StorageClass creation for the EFS instance.

- Optional
- Environment Variable: `CREATE_STORAGE_CLASS`
- Default: `true`

**Purpose**: Controls whether a Kubernetes StorageClass is automatically created for the EFS instance.

**When to use**: Set to `true` for normal operations. Set to `false` if you want to manually create the StorageClass or use a custom configuration.

**Valid values**:
- `true` - Automatically create StorageClass named `efs-<efs_unique_id>` (default)
- `false` - Skip StorageClass creation

**Impact**: When `true`, creates a StorageClass that applications can use to provision PVCs backed by EFS. When `false`, you must manually create the StorageClass.

**Related variables**: `efs_unique_id`

**Notes**:
- Default `true` is recommended for most deployments
- StorageClass name format: `efs-<efs_unique_id>`
- StorageClass supports dynamic provisioning with RWX access mode
- Set to `false` only if you need custom StorageClass parameters

License
-------

EPL-2.0
