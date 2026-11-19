# aws_policy

Create AWS IAM policies from JSON policy documents in your AWS account. This role automates IAM policy creation, enabling you to define fine-grained permissions for AWS resources and services used by MAS deployments.

IAM policies define permissions for AWS identities (users, groups, roles) to access AWS resources. This role creates customer-managed policies that can be attached to IAM users or roles.

## Prerequisites

- AWS CLI must be installed
- AWS credentials configured via `aws configure` or environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
- IAM permissions to create policies

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`aws_policy_name`](#aws_policy_name) | Yes | None |
| [`aws_policy_json_file_path_local`](#aws_policy_json_file_path_local) | Yes | None |

### IAM Policy

#### aws_policy_name

Name for the IAM policy to be created (valid IAM policy name: alphanumeric characters plus `+=,.@-_`, 1-128 characters).

- **Required**
- Environment Variable: `AWS_POLICY_NAME`
- Default: None

Must be unique within the AWS account and cannot be changed after creation. The name forms part of the policy ARN (`arn:aws:iam::<account-id>:policy/<policy-name>`) and is used when attaching the policy to IAM users or roles.

#### aws_policy_json_file_path_local

Local file path to the IAM policy JSON document.

- **Required**
- Environment Variable: `AWS_POLICY_JSON_FILE_PATH_LOCAL`
- Default: None

Must point to a valid JSON file (accessible from the Ansible controller) following AWS IAM policy syntax. A sample template is available in the role's `/files/policy-template-sample.json`. The document uses the standard structure:

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

Common policy elements: `Version` (always `2012-10-17`), `Statement` (array of permission statements), `Effect` (`Allow` or `Deny`), `Action` (AWS service actions, e.g. `s3:GetObject`), `Resource` (ARNs the policy applies to), and `Condition` (optional conditions for when the policy applies).

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
