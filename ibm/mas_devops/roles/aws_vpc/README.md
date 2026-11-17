# aws_vpc
This role will create VPC with specified CIDR IP

## Prerequisites
To run this role successfully you must have already installed the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).
Also, you need to have AWS user credentials configured via `aws configure` command or simply export `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables with your corresponding AWS username credentials prior running this role.

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`mas_config_dir`](#mas_config_dir) | Yes | None |
| [`aws_region`](#aws_region) | No | `us-east-1` |
| [`vpc_action`](#vpc_action) | No | `provision` |
| [`vpc_cidr`](#vpc_cidr) | Conditional | None |
| [`vpc_name`](#vpc_name) | Yes | None |

`vpc_cidr` is only required when `vpc_action` is `provision`; it is ignored for deprovisioning.

### Configuration Storage

#### mas_config_dir

Local directory where generated Kubernetes resources, VPC configuration details, and any credentials or metadata related to the created VPC will be saved — for example `~/masconfig` or `/opt/mas/config`. The directory is created if it doesn't exist.

- **Required**
- Environment Variable: `MAS_CONFIG_DIR`
- Default: None

Use the same `mas_config_dir` across all MAS DevOps roles for consistency; it should be writable by the user running the playbook (an absolute path is recommended), and backed up since it contains important configuration data for subsequent MAS installation steps.

### AWS Settings

#### aws_region

The AWS region where the VPC will be created — for example `us-east-1`, `us-west-2`, `eu-west-1`, or `ap-southeast-1`. Must be a region your AWS account has access to.

- **Optional**
- Environment Variable: `AWS_REGION`
- Default: `us-east-1`

The VPC and all its associated resources (subnets, route tables, internet gateways) are created in this region. Choose a region close to your users, that supports all AWS services required by MAS (EFS, DocumentDB, etc.), and that meets compliance and data residency requirements. The region cannot be changed after VPC creation (recreation is required), and it should align with the region used in other AWS roles.

### VPC Settings

#### vpc_action

The action to perform on the VPC — `provision` to create a new VPC with the specified configuration (default), or `deprovision` to permanently delete the VPC identified by `vpc_name`.

- **Optional**
- Environment Variable: `VPC_ACTION`
- Default: `provision`

`provision` creates the VPC, subnets, route tables, internet gateway, and associated resources; `deprovision` deletes the VPC and cleans up all associated resources. Ensure all OpenShift clusters and MAS workloads are removed before deprovisioning — it will fail if EC2 instances, load balancers, or other resources are still using the VPC.

!!! warning
    Deprovisioning is irreversible — all data and configurations within the VPC will be lost. Consider taking backups before deprovisioning.

#### vpc_cidr

The CIDR block (IP address range) for the VPC — a valid IPv4 CIDR between /16 and /28 netmask from the private ranges `10.0.0.0/8`, `172.16.0.0/12`, or `192.168.0.0/16`, for example `10.0.0.0/16` (65,536 IP addresses) or `192.168.0.0/20` (4,096 IP addresses).

- **Required** for provisioning
- Environment Variable: `VPC_CIDR`
- Default: None

Determines the maximum number of IP addresses available in the VPC and cannot be changed after VPC creation (recreation is required). For OpenShift on AWS (ROSA), a /16 CIDR is recommended for production. Reserve the first 4 and last 1 IP addresses in each subnet for AWS services, plan for future growth, and avoid overlapping with other VPCs (if peering is planned) or on-premises networks (if VPN connectivity is planned).

#### vpc_name

The name tag for the VPC — any string following AWS tag naming conventions, recommended format `<environment>-<purpose>-vpc` (e.g., `prod-mas-vpc`, `dev-maximo-vpc`), unique within your AWS account.

- **Required**
- Environment Variable: `VPC_NAME`
- Default: None

Used as the "Name" tag on the VPC in the AWS console, to identify the VPC in CLI and API operations, and to locate the VPC during deprovisioning. Include environment indicators (dev, test, prod) and consider including the region or purpose for multi-region deployments; the name is stored as a tag and can be changed after creation.

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
