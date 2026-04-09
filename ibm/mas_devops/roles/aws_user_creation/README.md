# aws_user_creation
This role will create an AWS IAM Username and corresponding IAM Access Key ID and Secret Access Key in the targeted AWS account.

## Prerequisites
To run this role successfully you must have already installed the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).
Also, you need to have AWS user credentials configured via `aws configure` command or simply export `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables with your corresponding AWS username credentials prior running this role.

## Role Variables

### aws_username
The IAM username to create in AWS.

- **Required**
- Environment Variable: `AWS_USERNAME`
- Default Value: None

**Purpose**: Specifies the name of the IAM user to be created in your AWS account. This user will be used for programmatic access to AWS services required by MAS.

**When to use**: Always required when creating a new IAM user. The username should follow your organization's naming conventions and clearly identify its purpose (e.g., `mas-service-user`, `maximo-automation`).

**Valid values**:
- 1-64 characters
- Alphanumeric characters, plus signs (+), equals signs (=), commas (,), periods (.), at signs (@), underscores (_), and hyphens (-)
- Must be unique within your AWS account
- Case-sensitive

**Impact**:
- Creates a new IAM user with this name in your AWS account
- The user can be assigned policies and access keys for authentication
- Username cannot be changed after creation (requires deletion and recreation)
- Will appear in AWS CloudTrail logs for audit purposes

**Related variables**:
- [`aws_username_create_access_key_flag`](#aws_username_create_access_key_flag) - Controls access key creation
- [`aws_policy_arn`](#aws_policy_arn) - Policy to attach to the user
- [`aws_username_access_key_id`](#aws_username_access_key_id) - Existing access key (optional)
- [`aws_username_secret_access_key`](#aws_username_secret_access_key) - Existing secret key (optional)

**Notes**:
- Follow the principle of least privilege when assigning permissions
- Consider using a descriptive name that indicates the user's purpose
- IAM users incur no direct costs but their actions may incur AWS service charges
- For production, consider using IAM roles with temporary credentials instead of long-lived access keys

### aws_username_create_access_key_flag
Controls whether to create new IAM access keys for the user.

- **Optional**
- Environment Variable: `AWS_USERNAME_CREATE_ACCESS_KEY_FLAG`
- Default Value: `True`

**Purpose**: Determines if the role should generate a new IAM Access Key ID and Secret Access Key pair for the created user. Access keys enable programmatic access to AWS services.

**When to use**:
- Set to `True` (default) when creating a new user that needs programmatic access
- Set to `False` when you only need to create the user identity without immediate access keys
- Automatically set to `False` if both `aws_username_access_key_id` and `aws_username_secret_access_key` are provided

**Valid values**:
- `True` - Create new access key pair
- `False` - Do not create access keys

**Impact**:
- When `True`: Generates new access key credentials that must be securely stored
- When `False`: User is created but cannot authenticate programmatically until keys are added
- Access keys are displayed only once during creation and cannot be retrieved later
- Each IAM user can have a maximum of 2 active access keys

**Related variables**:
- [`aws_username`](#aws_username) - The user for which keys are created
- [`aws_username_access_key_id`](#aws_username_access_key_id) - Overrides key creation if provided
- [`aws_username_secret_access_key`](#aws_username_secret_access_key) - Overrides key creation if provided

**Notes**:
- Store generated access keys securely (e.g., in a secrets manager)
- Rotate access keys regularly for security best practices
- If you provide existing credentials via `aws_username_access_key_id` and `aws_username_secret_access_key`, this flag is automatically set to `False`
- Consider using temporary credentials (STS) for enhanced security in production

### aws_username_access_key_id
An existing IAM Access Key ID to use instead of creating a new one.

- **Optional**
- Environment Variable: `AWS_USERNAME_ACCESS_KEY_ID`
- Default Value: None

**Purpose**: Allows you to specify an existing IAM Access Key ID for the user instead of generating a new one. This is useful when you already have credentials and want to reuse them.

**When to use**:
- When you have pre-existing access keys that you want to associate with the user
- When rotating credentials and you want to use a specific key pair
- Must be used together with `aws_username_secret_access_key`

**Valid values**:
- A valid AWS IAM Access Key ID (20 characters, alphanumeric, starting with "AKIA" for long-term credentials)
- Must be a key that exists and is associated with the specified username
- Example format: `AKIAIOSFODNN7EXAMPLE`

**Impact**:
- When provided (along with secret key), automatically sets `aws_username_create_access_key_flag` to `False`
- No new access keys will be generated
- The role will use these existing credentials for validation
- Does not modify or rotate the existing access key

**Related variables**:
- [`aws_username_secret_access_key`](#aws_username_secret_access_key) - Must be provided together with this variable
- [`aws_username_create_access_key_flag`](#aws_username_create_access_key_flag) - Automatically set to `False` when this is provided
- [`aws_username`](#aws_username) - The user these credentials belong to

**Notes**:
- Both access key ID and secret access key must be provided together
- Ensure the credentials are valid and not expired
- The access key must belong to the user specified in `aws_username`
- Do not set this variable if you want to generate new credentials

### aws_username_secret_access_key
An existing IAM Secret Access Key to use instead of creating a new one.

- **Optional**
- Environment Variable: `AWS_USERNAME_SECRET_ACCESS_KEY`
- Default Value: None

**Purpose**: Allows you to specify an existing IAM Secret Access Key for the user instead of generating a new one. This must be used in conjunction with `aws_username_access_key_id`.

**When to use**:
- When you have pre-existing access keys that you want to associate with the user
- When you need to use specific credentials for compliance or security reasons
- Must be used together with `aws_username_access_key_id`

**Valid values**:
- A valid AWS IAM Secret Access Key (40 characters, alphanumeric with special characters)
- Must correspond to the Access Key ID provided in `aws_username_access_key_id`
- Example format: `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`

**Impact**:
- When provided (along with access key ID), automatically sets `aws_username_create_access_key_flag` to `False`
- No new access keys will be generated
- The role will use these existing credentials for validation
- Does not modify or rotate the existing secret key

**Related variables**:
- [`aws_username_access_key_id`](#aws_username_access_key_id) - Must be provided together with this variable
- [`aws_username_create_access_key_flag`](#aws_username_create_access_key_flag) - Automatically set to `False` when this is provided
- [`aws_username`](#aws_username) - The user these credentials belong to

**Notes**:
- Both access key ID and secret access key must be provided together
- Secret keys are sensitive credentials and should never be committed to version control
- Store secret keys securely using environment variables or secrets management systems
- The secret key must correspond to the access key ID provided
- Do not set this variable if you want to generate new credentials

### aws_policy_arn
The ARN of an IAM policy to attach to the created user.

- **Optional**
- Environment Variable: `AWS_POLICY_ARN`
- Default Value: None

**Purpose**: Specifies an IAM policy to attach to the user, granting specific permissions required for MAS operations. This allows you to control what AWS resources and actions the user can access.

**When to use**:
- When the user needs specific permissions to AWS services (S3, DocumentDB, EFS, etc.)
- After creating a custom policy using the `aws_policy` role
- When attaching AWS managed policies (e.g., `arn:aws:iam::aws:policy/AmazonS3FullAccess`)

**Valid values**:
- A valid IAM policy ARN in the format: `arn:aws:iam::<account-id>:policy/<policy-name>`
- Can be a customer-managed policy or AWS managed policy
- The policy must exist in your AWS account before attaching
- Examples:
  - Custom policy: `arn:aws:iam::123456789012:policy/MASServicePolicy`
  - AWS managed: `arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess`

**Impact**:
- Grants the user permissions defined in the specified policy
- Multiple policies can be attached by running the role multiple times with different ARNs
- Policy changes take effect immediately
- User actions will be constrained by the policy's permissions

**Related variables**:
- [`aws_username`](#aws_username) - The user to which the policy is attached
- Can be used with policies created by the `aws_policy` role

**Notes**:
- Follow the principle of least privilege - only grant necessary permissions
- Consider using customer-managed policies for better control and auditability
- You can attach up to 10 managed policies per IAM user
- Policy attachment is idempotent - attaching the same policy multiple times has no effect
- For MAS deployments, typical policies include S3 access, DocumentDB access, and EFS permissions

## Example Playbook
After installing the Ansible Collection you can include this role in your own custom playbooks.

```yaml
- hosts: localhost
  vars:
    aws_username: "{{ lookup('env', 'AWS_USERNAME') }}"
    aws_username_create_access_key_flag: "{{ lookup('env', 'AWS_USERNAME_CREATE_ACCESS_KEY_FLAG') }}"
    aws_policy_arn: "{{ lookup('env', 'AWS_POLICY_ARN') }}"
  roles:
    - ibm.mas_devops.aws_policy
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
