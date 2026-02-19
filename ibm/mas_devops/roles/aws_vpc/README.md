# aws_vpc
This role will create VPC with specified CIDR IP

## Prerequisites
To run this role successfully you must have already installed the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).
Also, you need to have AWS user credentials configured via `aws configure` command or simply export `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables with your corresponding AWS username credentials prior running this role.

## Role Variables

### mas_config_dir
Directory where generated Kubernetes resources and VPC configuration will be saved.

- **Required**
- Environment Variable: `MAS_CONFIG_DIR`
- Default Value: None

**Purpose**: Specifies the local directory path where the role will save generated Kubernetes resources, VPC configuration details, and any credentials or metadata related to the created VPC.

**When to use**: Always required when provisioning a VPC. This directory serves as the central location for all MAS configuration artifacts and should be consistent across all roles.

**Valid values**:
- Any valid local filesystem path (e.g., `~/masconfig`, `/opt/mas/config`)
- Directory will be created if it doesn't exist
- Should have write permissions for the user running the playbook
- Recommended to use an absolute path for consistency

**Impact**:
- All VPC-related configuration files will be stored in this directory
- Kubernetes secrets and resources will be generated here for later use
- Required for subsequent MAS installation and configuration steps
- Should be backed up as it contains important configuration data

**Related variables**:
- Used by all MAS DevOps roles for consistent configuration storage
- [`vpc_name`](#vpc_name) - Used in naming generated configuration files

**Notes**:
- Use the same `mas_config_dir` across all MAS DevOps roles for consistency
- Ensure the directory is accessible and has sufficient storage space
- Consider using version control for the configuration directory (excluding sensitive data)
- The directory structure follows MAS configuration conventions

### aws_region
The AWS region where the VPC will be created.

- **Optional**
- Environment Variable: `AWS_REGION`
- Default Value: `us-east-1`

**Purpose**: Specifies the AWS region for VPC creation. The VPC and all its associated resources (subnets, route tables, internet gateways) will be created in this region.

**When to use**: Should match the region where you plan to deploy your OpenShift cluster and MAS workloads. Consider data residency requirements and proximity to users.

**Valid values**:
- Any valid AWS region identifier (e.g., `us-east-1`, `us-west-2`, `eu-west-1`, `ap-southeast-1`)
- Must be a region where your AWS account has access
- Consider regions with availability zone requirements for high availability

**Impact**:
- Determines the geographic location of your VPC and all network resources
- Affects network latency for resources accessing the VPC
- Some AWS services may have different availability or pricing in different regions
- Cannot be changed after VPC creation (requires recreation)

**Related variables**:
- Should align with the region used in other AWS roles (DocumentDB, EFS, S3)
- [`vpc_name`](#vpc_name) - VPC identifier within the region

**Notes**:
- Choose a region close to your users for better performance
- Ensure the region supports all AWS services required by MAS (EFS, DocumentDB, etc.)
- Consider compliance and data residency requirements
- Some regions may have capacity constraints for certain instance types

### vpc_action
The action to perform on the VPC (provision or deprovision).

- **Optional**
- Environment Variable: `VPC_ACTION`
- Default Value: `provision`

**Purpose**: Controls whether the role should create a new VPC or delete an existing one. This allows the same role to handle both lifecycle operations.

**When to use**:
- Use `provision` (default) when creating a new VPC for MAS deployment
- Use `deprovision` when cleaning up and removing the VPC after MAS uninstallation

**Valid values**:
- `provision` - Create a new VPC with the specified configuration
- `deprovision` - Delete the VPC identified by `vpc_name`

**Impact**:
- `provision`: Creates VPC, subnets, route tables, internet gateway, and associated resources
- `deprovision`: Permanently deletes the VPC and all associated resources
- Deprovisioning is irreversible and will fail if resources are still attached to the VPC
- All data and configurations within the VPC will be lost during deprovisioning

**Related variables**:
- [`vpc_name`](#vpc_name) - Identifies which VPC to provision or deprovision
- [`vpc_cidr`](#vpc_cidr) - Required for provisioning, ignored for deprovisioning

**Notes**:
- Before deprovisioning, ensure all OpenShift clusters and MAS workloads are removed
- Deprovisioning will fail if EC2 instances, load balancers, or other resources are still using the VPC
- Consider taking backups before deprovisioning
- The role will clean up associated resources (subnets, route tables, internet gateways)

### vpc_cidr
The CIDR block (IP address range) for the VPC.

- **Required** (for provisioning)
- Environment Variable: `VPC_CIDR`
- Default Value: None

**Purpose**: Defines the IP address range for the VPC using CIDR notation. This determines the total number of IP addresses available within the VPC for subnets, instances, and other resources.

**When to use**: Required when provisioning a new VPC. The CIDR block should be large enough to accommodate all planned subnets and resources while avoiding conflicts with existing networks.

**Valid values**:
- Valid IPv4 CIDR block between /16 and /28 netmask
- Must be from private IP ranges:
  - `10.0.0.0/8` (10.0.0.0 - 10.255.255.255)
  - `172.16.0.0/12` (172.16.0.0 - 172.31.255.255)
  - `192.168.0.0/16` (192.168.0.0 - 192.168.255.255)
- Common examples:
  - `10.0.0.0/16` - Provides 65,536 IP addresses
  - `172.31.0.0/16` - Provides 65,536 IP addresses
  - `192.168.0.0/20` - Provides 4,096 IP addresses

**Impact**:
- Determines the maximum number of IP addresses available in the VPC
- Cannot be changed after VPC creation (requires recreation)
- Affects subnet design and IP address allocation strategy
- Must not overlap with other VPCs if VPC peering is planned
- Smaller CIDR blocks (/24, /28) limit scalability

**Related variables**:
- [`vpc_name`](#vpc_name) - Identifies the VPC using this CIDR block
- [`aws_region`](#aws_region) - Region where the VPC with this CIDR is created

**Notes**:
- Plan for future growth when selecting CIDR block size
- Reserve IP addresses for AWS services (first 4 and last 1 in each subnet)
- For OpenShift on AWS (ROSA), a /16 CIDR is recommended for production
- Avoid overlapping with on-premises networks if VPN connectivity is planned
- Document your CIDR allocation strategy for network management

### vpc_name
The name tag for the VPC.

- **Required**
- Environment Variable: `VPC_NAME`
- Default Value: None

**Purpose**: Assigns a human-readable name to the VPC for identification and management purposes. This name appears in the AWS console and is used to identify the VPC in subsequent operations.

**When to use**: Always required for both provisioning and deprovisioning operations. The name should be descriptive and follow your organization's naming conventions.

**Valid values**:
- Any string that follows AWS tag naming conventions
- Recommended format: `<environment>-<purpose>-vpc` (e.g., `prod-mas-vpc`, `dev-maximo-vpc`)
- Should be unique within your AWS account for clarity
- Alphanumeric characters, hyphens, and underscores are recommended

**Impact**:
- Used as the "Name" tag on the VPC in AWS console
- Helps identify the VPC in AWS CLI and API operations
- Used by the role to locate the VPC during deprovisioning
- Appears in AWS cost allocation reports if cost tags are enabled

**Related variables**:
- [`vpc_cidr`](#vpc_cidr) - The IP range for this named VPC
- [`vpc_action`](#vpc_action) - Whether to provision or deprovision this VPC
- [`mas_config_dir`](#mas_config_dir) - Where configuration for this VPC is stored

**Notes**:
- Use consistent naming conventions across all AWS resources
- Include environment indicators (dev, test, prod) in the name
- The name is stored as a tag and can be changed after creation
- Consider including the region or purpose in the name for multi-region deployments
- Document your VPC naming strategy for team consistency
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
