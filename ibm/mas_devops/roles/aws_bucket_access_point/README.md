# aws_bucket_access_point
This role will create an access point and associates it with the specified s3/aws bucket in the targeted AWS account.

## Prerequisites
To run this role successfully you must have already installed the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).
Also, you need to have AWS user credentials configured via `aws configure` command or simply export `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables with your corresponding AWS username credentials prior running this role.

## Role Variables

### aws_access_point_name
The name you want to assign to this access point.

- Required.
- Environment Variable: `AWS_ACCESS_POINT_NAME`
- Default Value: `access-point-c1`

### aws_access_point_bucket_name
The name of the bucket that you want to associate this access point with.

- Required.
- Environment Variable: `COS_BUCKET_NAME`
- Default Value: None

### aws_access_point_region
The region where the bucket is located.

- Required.
- Environment Variable: `AWS_REGION`
- Default Value: `us-east-2`

### aws_access_point_username
The AWS account or username who is allowed access to the actions defined in by the access point policy.
By default, the defined `aws_access_point_username` will have read-only permissions to the bucket objects through the created access point alias.

- Required.
- Environment Variable: `AWS_ACCESS_POINT_USERNAME`
- Default Value: None

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
