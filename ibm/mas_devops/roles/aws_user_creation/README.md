# aws_user_creation
This role will create an AWS IAM Username and corresponding IAM Access Key ID and Secret Access Key in the targeted AWS account.

## Prerequisites
To run this role successfully you must have already installed the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).
Also, you need to have AWS user credentials configured via `aws configure` command or simply export `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables with your corresponding AWS username credentials prior running this role.

## Role Variables

### aws_username
AWS Username.

- Required.
- Environment Variable: `AWS_USERNAME`
- Default Value: None

### aws_username_create_access_key_flag
Flag that defines if IAM Access Key ID and Secret Access Key should be created for the AWS Username.
If set to `False`, then only the AWS Username will be created but no IAM Access Key ID and Secret Access Key.

- Optional
- Environment Variable: `AWS_USERNAME_CREATE_ACCESS_KEY_FLAG`
- Default Value: `True`.

### aws_username_access_key_id
Defines an existing IAM Access Key ID for your AWS username.
If both `aws_username_access_key_id` and `aws_username_secret_access_key` are defined, then `aws_username_create_access_key_flag` will be automatically forced to `False`, therefore if you want to create new pair of credentials for the username, do not set this property.

- Optional
- Environment Variable: `AWS_USERNAME_ACCESS_KEY_ID`
- Default Value: None.

### aws_username_secret_access_key
Defines and existing IAM Secret Access Key for your AWS username.
If both `aws_username_access_key_id` and `aws_username_secret_access_key` are defined, then `aws_username_create_access_key_flag` will be automatically forced to `False`, therefore if you want to create new pair of credentials for the username, do not set this property.

- Optional
- Environment Variable: `AWS_USERNAME_SECRET_ACCESS_KEY`
- Default Value: None.

### aws_policy_arn
If set, then it will attach the corresponding policy to the AWS Username's permissions.

- Optional
- Environment Variable: `AWS_POLICY_ARN`
- Default Value: None.

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
