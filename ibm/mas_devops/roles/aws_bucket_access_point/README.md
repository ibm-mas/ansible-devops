# aws_bucket_access_point

Create AWS S3 bucket access points with controlled permissions for secure, isolated access to S3 buckets. Access points simplify managing data access at scale by providing dedicated endpoints with specific permissions, enabling fine-grained access control without modifying bucket policies.

This role creates an access point associated with an existing S3 bucket and configures a read-only access policy for a specified AWS user or account.

## Prerequisites

- AWS CLI must be installed
- AWS credentials configured via `aws configure` or environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
- Target S3 bucket must already exist

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`aws_access_point_name`](#aws_access_point_name) | No | `access-point-c1` |
| [`aws_access_point_bucket_name`](#aws_access_point_bucket_name) | Yes | None |
| [`aws_access_point_region`](#aws_access_point_region) | No | `us-east-2` |
| [`aws_access_point_username`](#aws_access_point_username) | Yes | None |
| [`aws_access_point_policy_actions`](#aws_access_point_policy_actions) | No | `s3:GetObject`, `s3:ListBucket` |

### Access Point Configuration

#### aws_access_point_name
Name for the S3 bucket access point — a valid access point name (3-50 characters, lowercase letters, numbers, hyphens) that is unique within your AWS account and region. Customize it to reflect the purpose or user of the access point, for example `mas-readonly-access` or `backup-access-point`.

- **Optional**
- Environment Variable: `AWS_ACCESS_POINT_NAME`
- Default: `access-point-c1`

The name cannot be changed after creation and is used in the access point ARN and alias. The access point alias format is `<access-point-name>-<account-id>.s3-accesspoint.<region>.amazonaws.com`.

#### aws_access_point_bucket_name
Name of the existing S3 bucket to associate with the access point — the access point provides controlled access to this bucket's objects based on the access point policy.

- **Required**
- Environment Variable: `COS_BUCKET_NAME`
- Default: None

The bucket must exist in the same AWS account and region before creating the access point, and multiple access points can be created for the same bucket. Verify the bucket with `aws s3 ls s3://<bucket-name>`.

#### aws_access_point_region
AWS region where the bucket and access point are located — a valid AWS region code such as `us-east-1`, `us-east-2`, `us-west-2`, or `eu-west-1`.

- **Optional**
- Environment Variable: `AWS_REGION`
- Default: `us-east-2`

!!! important
    The region must match the bucket's region exactly — cross-region access points are not supported. Verify the bucket's region with `aws s3api get-bucket-location --bucket <bucket-name>`.

The access point ARN includes the region, and network latency depends on the region's proximity to your users.

#### aws_access_point_username
AWS IAM user or account ID granted access through the access point — either an IAM username (e.g. `backup-user`, `readonly-service`) or a 12-digit AWS account ID for cross-account access.

- **Required**
- Environment Variable: `AWS_ACCESS_POINT_USERNAME`
- Default: None

The specified user or account receives read-only permissions (`s3:GetObject`, `s3:ListBucket`) to bucket objects through the access point. The user must exist in the AWS account, the access point policy is separate from the bucket policy, and the user still needs IAM permissions to use the access point.

### Access Policy

#### aws_access_point_policy_actions
List of S3 actions allowed through the access point policy — the default `s3:GetObject` (read object data) and `s3:ListBucket` (list bucket contents) provide read-only access.

- **Optional**
- Environment Variable: None (hardcoded in defaults)
- Default: `["s3:GetObject", "s3:ListBucket"]`

To grant write access, add actions such as `s3:PutObject` and `s3:DeleteObject` by modifying `defaults/main.yml`. The access point policy works in conjunction with IAM and bucket policies, and the most restrictive policy applies.

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
