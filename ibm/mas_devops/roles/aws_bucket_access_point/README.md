# aws_bucket_access_point

Create AWS S3 bucket access points with controlled permissions for secure, isolated access to S3 buckets. Access points simplify managing data access at scale by providing dedicated endpoints with specific permissions, enabling fine-grained access control without modifying bucket policies.

This role creates an access point associated with an existing S3 bucket and configures a read-only access policy for a specified AWS user or account.

**Prerequisites**:
- AWS CLI must be installed
- AWS credentials configured via `aws configure` or environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
- Target S3 bucket must already exist


## Role Variables

### aws_access_point_name
Name for the S3 bucket access point.

- Optional
- Environment Variable: `AWS_ACCESS_POINT_NAME`
- Default: `access-point-c1`

**Purpose**: Provides a unique identifier for the access point within your AWS account.

**When to use**: Customize to reflect the purpose or user of the access point (e.g., `mas-readonly-access`, `backup-access-point`).

**Valid values**: Valid S3 access point name (3-50 characters, lowercase letters, numbers, hyphens).

**Impact**: Access point name is used in the access point ARN and alias for connecting to the bucket.

**Related variables**: `aws_access_point_bucket_name`, `aws_access_point_username`

**Notes**:
- Must be unique within the AWS account and region
- Cannot be changed after creation
- Use descriptive names for easier management
- Access point alias format: `<access-point-name>-<account-id>.s3-accesspoint.<region>.amazonaws.com`

### aws_access_point_bucket_name
Name of the existing S3 bucket to associate with the access point.

- **Required**
- Environment Variable: `COS_BUCKET_NAME`
- Default: None

**Purpose**: Specifies which S3 bucket the access point will provide access to.

**When to use**: Always required. Must be an existing bucket in the same AWS account and region.

**Valid values**: Valid S3 bucket name that exists in your AWS account.

**Impact**: The access point will provide controlled access to this bucket's objects based on the access point policy.

**Related variables**: `aws_access_point_region`, `aws_access_point_name`

**Notes**:
- Bucket must exist before creating the access point
- Bucket and access point must be in the same region
- Multiple access points can be created for the same bucket
- Verify bucket name: `aws s3 ls s3://<bucket-name>`

### aws_access_point_region
AWS region where the bucket and access point are located.

- Optional
- Environment Variable: `AWS_REGION`
- Default: `us-east-2`

**Purpose**: Specifies the AWS region for the access point. Must match the bucket's region.

**When to use**: Set to match your S3 bucket's region. Default is suitable for US East deployments.

**Valid values**: Valid AWS region code (e.g., `us-east-1`, `us-east-2`, `us-west-2`, `eu-west-1`).

**Impact**: Access point must be in the same region as the bucket. Cross-region access points are not supported.

**Related variables**: `aws_access_point_bucket_name`

**Notes**:
- **Critical**: Must match the bucket's region exactly
- Verify bucket region: `aws s3api get-bucket-location --bucket <bucket-name>`
- Access point ARN includes the region
- Network latency depends on region proximity to users

### aws_access_point_username
AWS IAM user or account ID granted access through the access point.

- **Required**
- Environment Variable: `AWS_ACCESS_POINT_USERNAME`
- Default: None

**Purpose**: Specifies which AWS IAM user or account is allowed to access the bucket through this access point.

**When to use**: Always required. Provide the IAM username or AWS account ID that needs read-only access to the bucket.

**Valid values**:
- IAM username (e.g., `backup-user`, `readonly-service`)
- AWS account ID (12-digit number)

**Impact**: The specified user/account will have read-only permissions (`s3:GetObject`, `s3:ListBucket`) to bucket objects through the access point.

**Related variables**: `aws_access_point_policy_actions`

**Notes**:
- Default policy grants read-only access (`s3:GetObject`, `s3:ListBucket`)
- User must exist in the AWS account
- Access point policy is separate from bucket policy
- User still needs IAM permissions to use the access point
- For cross-account access, provide the account ID

### aws_access_point_policy_actions
List of S3 actions allowed through the access point.

- Optional (defined in defaults)
- Environment Variable: None (hardcoded in defaults)
- Default: `["s3:GetObject", "s3:ListBucket"]`

**Purpose**: Defines which S3 operations are permitted through the access point policy.

**When to use**: Default read-only actions are suitable for most use cases. Modify in defaults file if different permissions are needed.

**Valid values**: List of valid S3 action strings. Default actions:
- `s3:GetObject` - Read object data
- `s3:ListBucket` - List bucket contents

**Impact**: Controls what operations the specified user can perform on bucket objects through the access point.

**Related variables**: `aws_access_point_username`

**Notes**:
- Default provides read-only access
- To grant write access, add actions like `s3:PutObject`, `s3:DeleteObject`
- Access point policy works in conjunction with IAM and bucket policies
- Most restrictive policy applies
- Modify in `defaults/main.yml` if custom permissions needed

## Example Playbook
After installing the Ansible Collection you can include this role in your own custom playbooks.

```yaml
- hosts: localhost
  vars:
    aws_access_point_name: "{{ lookup('env', 'AWS_ACCESS_POINT_NAME') | default('access-point-c1', True) }}"
    aws_access_point_bucket_name: "{{ lookup('env', 'COS_BUCKET_NAME') }}"
    aws_access_point_region: "{{ lookup('env', 'AWS_REGION') | default('us-east-2', True) }}"
    aws_access_point_username: "{{ lookup('env', 'AWS_ACCESS_POINT_USERNAME') }}"
  roles:
    - ibm.mas_devops.aws_bucket_access_point
```

## Run Role Playbook
After installing the Ansible Collection you can easily run the role standalone using the `run_role` playbook provided.

```bash
export AWS_ACCESS_POINT_NAME=my-aws-access-point
export COS_BUCKET_NAME=my-aws-bucket
export AWS_ACCESS_POINT_USERNAME=my-aws-username
ROLE_NAME=aws_bucket_access_point ansible-playbook ibm.mas_devops.run_role
```

## License
EPL-2.0
