# MongoDB Atlas - Subnet-Based Route Table Configuration Guide

## Overview

When provisioning MongoDB Atlas clusters with VPC peering, you can now specify subnet IDs where your worker nodes are located. The playbook will **automatically discover** the route tables associated with those subnets and configure them for MongoDB Atlas connectivity.

## Key Features

### Automatic Route Table Discovery

Instead of manually specifying route table IDs, you can provide subnet IDs and the playbook will:

1. **Validate** that each subnet exists in AWS
2. **Verify** that each subnet belongs to the specified VPC
3. **Discover** the route tables associated with those subnets
4. **Configure** routes in the discovered route tables for MongoDB Atlas VPC peering

### Flexible Configuration Options

You can use:
- **Subnet IDs only** - Playbook discovers route tables automatically
- **Route table IDs only** - Manual specification (original behavior)
- **Both** - Combines manual route tables with discovered ones (duplicates removed)

## New Parameter

### `atlas_aws_subnet_ids`

**Description:** Comma-separated list of AWS subnet IDs where your worker nodes are located. The playbook will automatically find and configure the route tables associated with these subnets.

**Format:** String (comma-separated) or List

**Required:** No (optional, but recommended for automatic discovery)

**Example Values:**
- String format: `"subnet-0123456789abcdef0,subnet-fedcba9876543210"`
- List format: `["subnet-0123456789abcdef0", "subnet-fedcba9876543210"]`

## How It Works

When you provide subnet IDs, the playbook will:

1. **Convert** the comma-separated string to a list (if provided as string)
2. **Validate** that each subnet exists in AWS
3. **Verify** that each subnet belongs to the specified VPC
4. **Query AWS** to find route tables associated with each subnet
5. **Combine** discovered route tables with any manually specified ones
6. **Remove duplicates** to create final list of route tables
7. **Configure routes** in all identified route tables for MongoDB Atlas

## Usage Examples

### Option 1: Subnet-Based (Recommended - Automatic Discovery)

Provide only subnet IDs - route tables are discovered automatically:

```bash
ansible-playbook --connection=local \
  playbooks/mongodb_atlas_provision_example.yml \
  -e mongodb_provider=atlas \
  -e mongodb_action=provision \
  -e atlas_project_id="68ffa9d908ff531136cef231" \
  -e atlas_cluster_name="mas-test-cluster-1" \
  -e atlas_cluster_provider="AWS" \
  -e atlas_cluster_region="US_EAST_1" \
  -e atlas_cluster_size="M10" \
  -e atlas_mongodb_version="7.0" \
  -e atlas_backup_enabled=true \
  -e atlas_aws_secret_name="/aws-dev/mongodb-atlas-cluster/apikeys" \
  -e atlas_aws_secret_region="us-east-1" \
  -e atlas_vpc_id="vpc-06570640e1cf7523a" \
  -e atlas_aws_subnet_ids="subnet-0123456789abcdef0,subnet-fedcba9876543210" \
  -e atlas_aws_region="US_EAST_1" \
  -e '{"atlas_database_users":{"user1":{"username":"user1","auth_database_name":"admin","roles":[{"database_name":"admin","role_name":"readWriteAnyDatabase"}]}}}' \
  -e atlas_mongodb_secret_user="user1" \
  -e atlas_store_credentials_in_secret=true \
  -e atlas_credentials_secret_prefix="/aws-dev" \
  -e atlas_mongodb_secret_name="mas-test-cluster-1" \
  -e atlas_credentials_secret_region="us-east-1" \
  -e '{"atlas_credentials_secret_tags":{"Environment":"development","Project":"MAS","Owner":"DevOps"}}' \
  -e atlas_configure_vpc_peering="true"
```

### Option 2: Manual Route Tables (Original Behavior)

Specify route table IDs directly:

```bash
ansible-playbook --connection=local \
  playbooks/mongodb_atlas_provision_example.yml \
  -e mongodb_provider=atlas \
  -e mongodb_action=provision \
  -e atlas_project_id="68ffa9d908ff531136cef231" \
  -e atlas_cluster_name="mas-test-cluster-1" \
  -e atlas_cluster_provider="AWS" \
  -e atlas_cluster_region="US_EAST_1" \
  -e atlas_cluster_size="M10" \
  -e atlas_mongodb_version="7.0" \
  -e atlas_backup_enabled=true \
  -e atlas_aws_secret_name="/aws-dev/mongodb-atlas-cluster/apikeys" \
  -e atlas_aws_secret_region="us-east-1" \
  -e atlas_vpc_id="vpc-06570640e1cf7523a" \
  -e atlas_aws_route_table_ids="rtb-02618f7cf5ce1c3a8,rtb-0e4c50359ab3dd35a" \
  -e atlas_aws_region="US_EAST_1" \
  -e '{"atlas_database_users":{"user1":{"username":"user1","auth_database_name":"admin","roles":[{"database_name":"admin","role_name":"readWriteAnyDatabase"}]}}}' \
  -e atlas_mongodb_secret_user="user1" \
  -e atlas_store_credentials_in_secret=true \
  -e atlas_credentials_secret_prefix="/aws-dev" \
  -e atlas_mongodb_secret_name="mas-test-cluster-1" \
  -e atlas_credentials_secret_region="us-east-1" \
  -e '{"atlas_credentials_secret_tags":{"Environment":"development","Project":"MAS","Owner":"DevOps"}}' \
  -e atlas_configure_vpc_peering="true"
```

### Option 3: Combined (Both Subnets and Manual Route Tables)

Combine automatic discovery with manual specification:

```bash
ansible-playbook --connection=local \
  playbooks/mongodb_atlas_provision_example.yml \
  -e mongodb_provider=atlas \
  -e mongodb_action=provision \
  -e atlas_project_id="68ffa9d908ff531136cef231" \
  -e atlas_cluster_name="mas-test-cluster-1" \
  -e atlas_cluster_provider="AWS" \
  -e atlas_cluster_region="US_EAST_1" \
  -e atlas_cluster_size="M10" \
  -e atlas_mongodb_version="7.0" \
  -e atlas_backup_enabled=true \
  -e atlas_aws_secret_name="/aws-dev/mongodb-atlas-cluster/apikeys" \
  -e atlas_aws_secret_region="us-east-1" \
  -e atlas_vpc_id="vpc-06570640e1cf7523a" \
  -e atlas_aws_subnet_ids="subnet-0123456789abcdef0,subnet-fedcba9876543210" \
  -e atlas_aws_route_table_ids="rtb-additional-table-id" \
  -e atlas_aws_region="US_EAST_1" \
  -e '{"atlas_database_users":{"user1":{"username":"user1","auth_database_name":"admin","roles":[{"database_name":"admin","role_name":"readWriteAnyDatabase"}]}}}' \
  -e atlas_mongodb_secret_user="user1" \
  -e atlas_store_credentials_in_secret=true \
  -e atlas_credentials_secret_prefix="/aws-dev" \
  -e atlas_mongodb_secret_name="mas-test-cluster-1" \
  -e atlas_credentials_secret_region="us-east-1" \
  -e '{"atlas_credentials_secret_tags":{"Environment":"development","Project":"MAS","Owner":"DevOps"}}' \
  -e atlas_configure_vpc_peering="true"
```

## Finding Your Subnet IDs

### Method 1: AWS CLI

List all subnets in your VPC:

```bash
aws ec2 describe-subnets \
  --filters "Name=vpc-id,Values=vpc-06570640e1cf7523a" \
  --query 'Subnets[*].[SubnetId,AvailabilityZone,CidrBlock,Tags[?Key==`Name`].Value|[0]]' \
  --output table
```

Get just the subnet IDs:

```bash
aws ec2 describe-subnets \
  --filters "Name=vpc-id,Values=vpc-06570640e1cf7523a" \
  --query 'Subnets[*].SubnetId' \
  --output text
```

### Method 2: AWS Console

1. Go to **VPC Dashboard** → **Subnets**
2. Filter by your VPC ID: `vpc-06570640e1cf7523a`
3. Copy the Subnet IDs from the list

## Validation Process

The playbook performs the following validations:

1. **Subnet Existence Check**
   - Verifies each subnet ID exists in AWS
   - Uses AWS CLI to query subnet information

2. **VPC Association Check**
   - Confirms each subnet belongs to the specified VPC
   - Fails if any subnet is in a different VPC

3. **Error Handling**
   - Clear error messages if validation fails
   - Indicates which subnet failed and why

## Example Output

### With Subnet-Based Discovery

When subnets are provided, you'll see the discovery process:

```
TASK [Discover route tables from subnets]
ok: [localhost] => (item=subnet-0123456789abcdef0)
ok: [localhost] => (item=subnet-fedcba9876543210)

TASK [Display discovered route tables from subnets]
ok: [localhost] => {
    "msg": [
        "Discovered 2 route table(s) from subnets:",
        ["rtb-02618f7cf5ce1c3a8", "rtb-0e4c50359ab3dd35a"]
    ]
}

TASK [MongoDB Atlas Route Table Configuration]
ok: [localhost] => {
    "msg": [
        "==========================================",
        "MongoDB Atlas Route Table Configuration",
        "==========================================",
        "Atlas Project ID ............ 68ffa9d908ff531136cef231",
        "Provider Name ............... AWS",
        "Atlas Region (API format) ... US_EAST_1",
        "AWS Region (CLI format) ..... us-east-1",
        "VPC ID ...................... vpc-06570640e1cf7523a",
        "Subnet IDs (provided) ....... 2 subnets",
        "Route Tables (manual) ....... 0 tables",
        "Route Tables (discovered) ... 2 tables",
        "Route Tables (total) ........ 2 tables",
        "=========================================="
    ]
}
```

And in the final summary:

```
TASK [Route table configuration completed successfully]
ok: [localhost] => {
    "msg": [
        "==========================================",
        "MongoDB Atlas Route Tables Configured!",
        "==========================================",
        "Atlas CIDR Block ............ 10.8.0.0/18",
        "VPC Peering Connection ...... pcx-0123456789abcdef0",
        "Routes Added ................ 2 route tables",
        "Subnets Validated ........... 2 subnets",
        "AWS Region .................. US_EAST_1",
        "Provider Name ............... AWS",
        "=========================================="
    ]
}
```

## Troubleshooting

### Error: Subnet not found

```
FAILED! => {"msg": "Subnet subnet-xxx does not exist"}
```

**Solution:** Verify the subnet ID is correct and exists in your AWS account.

### Error: Subnet not in VPC

```
FAILED! => {"msg": "Subnet subnet-xxx is not in VPC vpc-06570640e1cf7523a"}
```

**Solution:** Ensure the subnet belongs to the VPC you specified in `atlas_vpc_id`.

### Error: AWS CLI not configured

```
FAILED! => {"msg": "AWS credentials are not configured"}
```

**Solution:** Configure AWS CLI credentials:
```bash
aws configure
```

Or set environment variables:
```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

## Notes

- Subnet validation is **optional** - the playbook works without this parameter
- Subnets must exist in the same VPC as specified in `atlas_vpc_id`
- The playbook validates subnets but does not modify them
- Subnet IDs are used for validation purposes to ensure proper network configuration

## Related Parameters

- `atlas_vpc_id` - The VPC where subnets must exist
- `atlas_aws_route_table_ids` - Route tables that may be associated with these subnets
- `atlas_aws_region` - AWS region where subnets are located