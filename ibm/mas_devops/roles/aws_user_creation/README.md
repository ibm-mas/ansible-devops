# aws_user_creation

This role will create an AWS IAM Username and corresponding IAM Access Key ID and Secret Access Key in the targeted AWS account.

## Prerequisites

To run this role successfully you must have already installed the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).
Also, you need to have AWS user credentials configured via `aws configure` command or simply export `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables with your corresponding AWS username credentials prior running this role.

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`aws_username`](#aws_username) | Yes | None |
| [`aws_username_create_access_key_flag`](#aws_username_create_access_key_flag) | No | `True` |
| [`aws_username_access_key_id`](#aws_username_access_key_id) | No | None |
| [`aws_username_secret_access_key`](#aws_username_secret_access_key) | No | None |
| [`aws_policy_arn`](#aws_policy_arn) | No | None |

### IAM User

#### aws_username

The IAM username to create in AWS — 1-64 characters of alphanumeric characters plus `+ = , . @ _ -`, unique within your AWS account and case-sensitive. Use a descriptive name that identifies the user's purpose, for example `mas-service-user` or `maximo-automation`.

- **Required**
- Environment Variable: `AWS_USERNAME`
- Default: None

Creates a new IAM user with this name in your AWS account; the user can then be assigned policies and access keys for programmatic access to the AWS services required by MAS. The username cannot be changed after creation (it requires deletion and recreation) and will appear in AWS CloudTrail logs for audit purposes. Follow the principle of least privilege when assigning permissions — for production, consider using IAM roles with temporary credentials instead of long-lived access keys.

### Access Keys

#### aws_username_create_access_key_flag

Controls whether to create new IAM access keys for the user — `True` (create a new access key pair, the default) or `False` (create the user identity only).

- **Optional**
- Environment Variable: `AWS_USERNAME_CREATE_ACCESS_KEY_FLAG`
- Default: `True`

Automatically set to `False` if both [`aws_username_access_key_id`](#aws_username_access_key_id) and [`aws_username_secret_access_key`](#aws_username_secret_access_key) are provided. When `True`, the generated credentials are displayed only once during creation and cannot be retrieved later — store them securely (e.g., in a secrets manager) and rotate them regularly. Each IAM user can have a maximum of 2 active access keys.

#### aws_username_access_key_id

An existing IAM Access Key ID to use instead of creating a new one — a valid 20-character AWS IAM Access Key ID associated with the specified username, for example `AKIAIOSFODNN7EXAMPLE`.

- **Optional**
- Environment Variable: `AWS_USERNAME_ACCESS_KEY_ID`
- Default: None

Must be provided together with [`aws_username_secret_access_key`](#aws_username_secret_access_key); when both are provided, [`aws_username_create_access_key_flag`](#aws_username_create_access_key_flag) is automatically set to `False`, no new keys are generated, and the role uses the existing credentials for validation without modifying or rotating them. Do not set this variable if you want to generate new credentials.

#### aws_username_secret_access_key

An existing IAM Secret Access Key to use instead of creating a new one — a valid 40-character AWS IAM Secret Access Key corresponding to the provided access key ID, for example `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`.

- **Optional**
- Environment Variable: `AWS_USERNAME_SECRET_ACCESS_KEY`
- Default: None

Must be provided together with [`aws_username_access_key_id`](#aws_username_access_key_id); when both are provided, [`aws_username_create_access_key_flag`](#aws_username_create_access_key_flag) is automatically set to `False` and the existing credentials are used for validation. Secret keys are sensitive credentials — never commit them to version control, and store them securely using environment variables or a secrets management system.

### IAM Policy

#### aws_policy_arn

The ARN of an IAM policy to attach to the created user — a valid customer-managed or AWS-managed policy ARN that exists in your AWS account, for example `arn:aws:iam::123456789012:policy/MASServicePolicy` (custom) or `arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess` (AWS managed).

- **Optional**
- Environment Variable: `AWS_POLICY_ARN`
- Default: None

Grants the user the permissions defined in the policy; use it when the user needs specific permissions to AWS services (S3, DocumentDB, EFS, etc.), for example with policies created by the `aws_policy` role. Policy attachment is idempotent, takes effect immediately, and you can attach up to 10 managed policies per IAM user (run the role multiple times with different ARNs to attach several). For MAS deployments, typical policies include S3 access, DocumentDB access, and EFS permissions.

## Example Playbook

After installing the Ansible Collection you can include this role in your own custom playbooks.

```yaml
- hosts: localhost
  vars:
    aws_username: "{{ lookup('env', 'AWS_USERNAME') }}"
    aws_username_create_access_key_flag: "{{ lookup('env', 'AWS_USERNAME_CREATE_ACCESS_KEY_FLAG') }}"
    aws_policy_arn: "{{ lookup('env', 'AWS_POLICY_ARN') }}"
  roles:
    - ibm.mas_devops.aws_user_creation
```

## Run Role Playbook

After installing the Ansible Collection you can easily run the role standalone using the `run_role` playbook provided.

```bash
export AWS_USERNAME=my-aws-username
export AWS_USERNAME_CREATE_ACCESS_KEY_FLAG=True
export AWS_POLICY_ARN=arn:aws:iam::my-id:policy/my-policy-name
ROLE_NAME=aws_user_creation ansible-playbook ibm.mas_devops.run_role
```

## License

EPL-2.0
