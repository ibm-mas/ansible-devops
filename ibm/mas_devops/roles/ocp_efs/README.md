# ocp_efs

Provision and configure AWS Elastic File System (EFS) storage for Red Hat OpenShift Service on AWS (ROSA) clusters. This role automates the complete EFS setup including security group configuration, EFS instance creation, access points, mount targets, and StorageClass creation.

EFS provides ReadWriteMany (RWX) persistent storage essential for MAS applications that require shared file access across multiple pods, such as Manage attachments and customer files.

The role performs the following operations:

1. Configures security group inbound rules for NFS access
2. Creates EFS file system in the cluster's VPC
3. Establishes mount targets in all availability zones
4. Creates access points for isolated storage
5. Deploys EFS CSI driver and StorageClass

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`aws_access_key_id`](#aws_access_key_id) | Yes | None |
| [`aws_secret_access_key`](#aws_secret_access_key) | Yes | None |
| [`aws_region`](#aws_region) | No | `eu-west-2` |
| [`cluster_name`](#cluster_name) | Yes | None |
| [`efs_unique_id`](#efs_unique_id) | No | Value of `cluster_name` |
| [`creation_token_prefix`](#creation_token_prefix) | No | `mas_devops.` |
| [`create_storage_class`](#create_storage_class) | No | `true` |
| [`olm_approval_mode`](#olm_approval_mode) | No | `Automatic` |
| [`olm_approval_timeout`](#olm_approval_timeout) | No | `7200` |

### OLM Install Plan Approval

#### olm_approval_mode

- **Optional**
- Environment Variable: `OLM_APPROVAL_MODE`
- Default: `Automatic`

When set to `Manual`, the subscriptions this role creates use manual install plan approval: the role pauses with instructions whenever an install plan is waiting for approval, and never approves it automatically. See [OLM Manual Install Plan Approvals](https://ibm-mas.github.io/ansible-devops/olm-manual-approvals/) for the full details.

#### olm_approval_timeout

- **Optional**
- Environment Variable: `OLM_APPROVAL_TIMEOUT`
- Default: `7200`

Seconds to wait for each individual install plan approval before the role fails (2 hours by default).

### AWS Credentials

#### aws_access_key_id

AWS access key ID for authentication — a valid 20-character alphanumeric AWS access key ID.

- **Required**
- Environment Variable: `AWS_ACCESS_KEY_ID`
- Default: None

Must have IAM permissions for EFS, EC2, and VPC operations (creating EFS resources, modifying security groups, and managing VPC resources); insufficient permissions will cause provisioning failures. Consider using IAM roles instead of access keys for better security, and store credentials securely, never in version control.

#### aws_secret_access_key

AWS secret access key for authentication — a valid 40-character alphanumeric AWS secret access key corresponding to `aws_access_key_id`.

- **Required**
- Environment Variable: `AWS_SECRET_ACCESS_KEY`
- Default: None

Keep the secret key secure and never expose it in logs or version control; rotate credentials regularly per security best practices, and consider AWS STS temporary credentials for enhanced security.

### Cluster and Region

#### aws_region

AWS region where the EFS instance will be provisioned — a valid AWS region code, for example `us-east-1` (US East, N. Virginia), `us-west-2` (US West, Oregon), `eu-west-1` (Europe, Ireland), `eu-west-2` (Europe, London, default), or `ap-southeast-1` (Asia Pacific, Singapore).

- **Optional**
- Environment Variable: `AWS_DEFAULT_REGION`
- Default: `eu-west-2`

EFS must be in the same region as the ROSA cluster — cross-region access is not supported. Verify the cluster region with `rosa describe cluster -c <cluster-name>`; EFS pricing varies by region.

#### cluster_name

Name of the ROSA cluster to attach EFS storage — a valid ROSA cluster name as shown in `rosa list clusters`, case-sensitive.

- **Required**
- Environment Variable: `CLUSTER_NAME`
- Default: None

The cluster must exist before running this role. The role uses this name to find the cluster's VPC ID, configure EFS mount targets in the correct network, and tag AWS resources for cost tracking.

### EFS Configuration

#### efs_unique_id

Unique identifier for the EFS instance and StorageClass — an alphanumeric string, typically lowercase (e.g., `mas-prod`, `manage-storage`, `shared-files`).

- **Optional**
- Environment Variable: `EFS_UNIQUE_ID`
- Default: Value of `cluster_name`

The StorageClass is named `efs-<efs_unique_id>`, and the EFS file system and creation tokens are tagged with this identifier. Set it when you need multiple EFS instances in the same cluster (e.g., `mas-attachments`, `mas-logs`) or want a more descriptive name than the cluster name; it must be unique within the cluster when creating multiple instances.

#### creation_token_prefix

Prefix for AWS resource creation tokens — a string prefix, typically ending with a dot or dash (e.g., `mas_devops.`, `myorg-`, `prod_`).

- **Optional**
- Environment Variable: `CREATION_TOKEN_PREFIX`
- Default: `mas_devops.`

Creation tokens are built by concatenating this prefix with `efs_unique_id` to ensure idempotent resource creation. The default `mas_devops.` identifies resources created by this collection; change it to distinguish resources from other automation tools.

#### create_storage_class

Enable automatic StorageClass creation for the EFS instance — `true` to create a StorageClass named `efs-<efs_unique_id>` (default), `false` to skip creation.

- **Optional**
- Environment Variable: `CREATE_STORAGE_CLASS`
- Default: `true`

When `true`, the created StorageClass supports dynamic provisioning with RWX access mode for PVCs backed by EFS. Set to `false` only if you need custom StorageClass parameters — you must then create the StorageClass manually.

## Example Playbook

```yaml
- hosts: localhost
  vars:
    # Add required variables here
  roles:
    - ibm.mas_devops.ocp_efs
```

## License

EPL-2.0
