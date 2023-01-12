aws_vpc
----------
This role will create VPC with specified CIDR IP 

## Prerequisites
To run this role successfully you must have already installed the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).
Also, you need to have AWS user credentials configured via `aws configure` command or simply export `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables with your corresponding AWS username credentials prior running this role.

## Role Variables

### mas_config_dir
Generate k8 resources like username and password Secret for created user will be saved in this directory

- Required
- Environment Variable: `MAS_CONFIG_DIR`
- Default Value: None.
### aws_region
Specify AWS Region where vpc will be created

- Optional
- Environment Variable: `AWS_REGION`
- Default Value: `us-east-1`
### vpc_action
Specify action(provision/deprovision) to performed by the role

- Optional
- Environment Variable: `VPC_ACTION`
- Default Value: `provision`


### vpc_cidr
Specify IP Address CIDR range for VPC

- Required
- Environment Variable: `VPC_CIDR`
- Default Value: None

### vpc_name
Specify Name for VPC

- Required
- Environment Variable: `VPC_NAME`
- Default Value: None
## Example Playbook

```yaml
- hosts: localhost
  vars:
    mas_config_dir: ~/masconfig
    vpc_name: test-vpc
    vpc_cidr: 10.0.0.0/16
    vpc_action: provision
  roles:
    - ibm.mas_devops.aws_vpc
```

## Run Role Playbook
After installing the Ansible Collection you can easily run the role standalone using the `run_role` playbook provided.

```bash
export VPC_NAME=test-vpc
export VPC_CIDR='10.0.0.0/16'
export VPC_ACTION=provision
export MAS_CONFIG_DIR=/pathtoconfig
ROLE_NAME=aws_vpc ansible-playbook ibm.mas_devops.run_role
```

## License
EPL-2.0
