aws_policy
===============================================================================

Create AWS IAM policies from JSON policy documents in your AWS account. This role automates IAM policy creation, enabling you to define fine-grained permissions for AWS resources and services used by MAS deployments.

IAM policies define permissions for AWS identities (users, groups, roles) to access AWS resources. This role creates customer-managed policies that can be attached to IAM users or roles.

**Prerequisites**:
- AWS CLI must be installed
- AWS credentials configured via `aws configure` or environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
- IAM permissions to create policies


Role Variables
-------------------------------------------------------------------------------

### aws_policy_name
Name for the IAM policy to be created.

- **Required**
- Environment Variable: `AWS_POLICY_NAME`
- Default: None

**Purpose**: Provides a unique identifier for the IAM policy within your AWS account.

**When to use**: Always required. Use descriptive names that reflect the policy's purpose (e.g., `MAS-S3-ReadOnly`, `DocumentDB-Access-Policy`).

**Valid values**: Valid IAM policy name (alphanumeric characters, plus `+=,.@-_` symbols, 1-128 characters).

**Impact**: Policy name is used in the policy ARN and for attaching to IAM users/roles.

**Related variables**: `aws_policy_json_file_path_local`

**Notes**:
- Must be unique within the AWS account
- Cannot be changed after creation
- Use naming conventions for easier management (e.g., `<service>-<purpose>-Policy`)
- Policy ARN format: `arn:aws:iam::<account-id>:policy/<policy-name>`

### aws_policy_json_file_path_local
Local file path to the IAM policy JSON document.

- **Required**
- Environment Variable: `AWS_POLICY_JSON_FILE_PATH_LOCAL`
- Default: None

**Purpose**: Specifies the location of the JSON file containing the IAM policy document that defines permissions.

**When to use**: Always required. Must point to a valid JSON file with proper IAM policy syntax.

**Valid values**: Absolute or relative file path to a valid JSON policy document (e.g., `/tmp/my-policy.json`, `./policies/s3-access.json`).

**Impact**: The policy document defines what actions are allowed or denied on which AWS resources.

**Related variables**: `aws_policy_name`

**Notes**:
- File must be accessible from the Ansible controller
- Must follow AWS IAM policy JSON syntax
- Sample template available in role's `/files/policy-template-sample.json`
- Validate policy syntax before applying: `aws iam validate-policy-document --policy-document file://policy.json`
- Policy document structure:
  ```json
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": ["s3:GetObject", "s3:ListBucket"],
        "Resource": ["arn:aws:s3:::my-bucket/*"]
      }
    ]
  }
  ```
- Common policy elements:
  - `Version`: Policy language version (always `2012-10-17`)
  - `Statement`: Array of permission statements
  - `Effect`: `Allow` or `Deny`
  - `Action`: AWS service actions (e.g., `s3:GetObject`)
  - `Resource`: ARNs of resources the policy applies to
  - `Condition`: Optional conditions for when policy applies

## Example Playbook
After installing the Ansible Collection you can include this role in your own custom playbooks.

```yaml
- hosts: localhost
  vars:
    aws_policy: "{{ lookup('env', 'AWS_POLICY_NAME') }}"
    aws_policy_json_file_path_local: "{{ lookup('env', 'AWS_POLICY_JSON_FILE_PATH_LOCAL') }}"
  roles:
    - ibm.mas_devops.aws_policy
```

## Run Role Playbook
After installing the Ansible Collection you can easily run the role standalone using the `run_role` playbook provided.

```bash
export AWS_POLICY_NAME=my-aws-policy
export AWS_POLICY_JSON_FILE_PATH_LOCAL=/tmp/local/my-aws-policy.json
ROLE_NAME=aws_policy ansible-playbook ibm.mas_devops.run_role
```

## License
EPL-2.0
