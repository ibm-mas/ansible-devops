# aws_policy
This role will create an AWS IAM Policy from a JSON file in the targeted AWS account.

## Prerequisites
To run this role successfully you must have already installed the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).
Also, you need to have AWS user credentials configured via `aws configure` command or simply export `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables with your corresponding AWS username credentials prior running this role.

## Role Variables

### aws_policy_name
AWS Policy name.

- Required.
- Environment Variable: `AWS_POLICY_NAME`
- Default Value: None

### aws_policy_json_file_path_local
Local path for the AWS Policy json file. 
The AWS Policy json file should be structured as the sample found in `/files/policy-template-sample.json`

- Required.
- Environment Variable: `AWS_POLICY_JSON_FILE_PATH_LOCAL`
- Default Value: None

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
