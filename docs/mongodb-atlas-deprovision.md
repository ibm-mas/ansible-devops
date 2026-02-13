# MongoDB Atlas Deprovision Guide

This guide explains how to decommission a MongoDB Atlas cluster and clean up all associated resources using the `ibm.mas_devops` collection.

## Overview

The deprovision process will:
1. Delete all database users
2. Delete the MongoDB Atlas cluster
3. Clean up MAS configuration files (if applicable)
4. Wait for deletion to complete (optional)

## Prerequisites

- Ansible 2.9 or later
- `ibm.mas_devops` collection installed
- MongoDB Atlas API credentials (public and private key)
- AWS CLI configured (if using AWS Secrets Manager for credentials)
- Appropriate permissions in MongoDB Atlas (Project Owner or Organization Owner role)

## Quick Start

### Basic Deprovision

```bash
export ATLAS_PROJECT_ID="your-project-id"
export ATLAS_CLUSTER_NAME="mas-mongodb-cluster"
export ATLAS_PUBLIC_KEY="your-public-key"
export ATLAS_PRIVATE_KEY="your-private-key"

ansible-playbook ibm.mas_devops.mongodb_atlas_deprovision_example
```

### Using AWS Secrets Manager

```bash
export ATLAS_PROJECT_ID="your-project-id"
export ATLAS_CLUSTER_NAME="mas-mongodb-cluster"
export ATLAS_AWS_SECRET_NAME="atlas-api-credentials"
export ATLAS_AWS_SECRET_REGION="us-east-1"

ansible-playbook ibm.mas_devops.mongodb_atlas_deprovision_example
```

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `ATLAS_PROJECT_ID` | MongoDB Atlas project ID | `507f1f77bcf86cd799439011` |
| `ATLAS_CLUSTER_NAME` | Name of the cluster to deprovision | `mas-mongodb-cluster` |

### Authentication Variables (choose one method)

**Method 1: Direct Credentials**
| Variable | Description |
|----------|-------------|
| `ATLAS_PUBLIC_KEY` | Atlas API public key |
| `ATLAS_PRIVATE_KEY` | Atlas API private key |

**Method 2: AWS Secrets Manager**
| Variable | Description | Default |
|----------|-------------|---------|
| `ATLAS_AWS_SECRET_NAME` | Name of AWS secret containing credentials | - |
| `ATLAS_AWS_SECRET_REGION` | AWS region where secret is stored | `us-east-1` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ATLAS_REMOVE_DB_USERS` | Remove all database users | `true` |
| `ATLAS_WAIT_FOR_DELETION` | Wait for cluster deletion to complete | `true` |
| `ATLAS_DB_USERNAME` | Specific user to remove (removes all if not set) | - |
| `MAS_INSTANCE_ID` | MAS instance ID for config cleanup | - |
| `MAS_CONFIG_DIR` | Directory containing MAS configs | - |

## Usage Examples

### Example 1: Complete Deprovision with Confirmation

```bash
#!/bin/bash

# Set required variables
export ATLAS_PROJECT_ID="507f1f77bcf86cd799439011"
export ATLAS_CLUSTER_NAME="mas-prod-mongodb"
export ATLAS_PUBLIC_KEY="abcdefgh"
export ATLAS_PRIVATE_KEY="12345678-1234-1234-1234-123456789abc"

# Run deprovision playbook (will prompt for confirmation)
ansible-playbook ibm.mas_devops.mongodb_atlas_deprovision_example
```

### Example 2: Deprovision Without Waiting

If you want to initiate deletion but not wait for it to complete:

```bash
export ATLAS_PROJECT_ID="507f1f77bcf86cd799439011"
export ATLAS_CLUSTER_NAME="mas-dev-mongodb"
export ATLAS_PUBLIC_KEY="abcdefgh"
export ATLAS_PRIVATE_KEY="12345678-1234-1234-1234-123456789abc"
export ATLAS_WAIT_FOR_DELETION="false"

ansible-playbook ibm.mas_devops.mongodb_atlas_deprovision_example
```

### Example 3: Deprovision with MAS Config Cleanup

```bash
export ATLAS_PROJECT_ID="507f1f77bcf86cd799439011"
export ATLAS_CLUSTER_NAME="mas-mongodb-cluster"
export ATLAS_PUBLIC_KEY="abcdefgh"
export ATLAS_PRIVATE_KEY="12345678-1234-1234-1234-123456789abc"
export MAS_INSTANCE_ID="inst1"
export MAS_CONFIG_DIR="/tmp/mas-config"

ansible-playbook ibm.mas_devops.mongodb_atlas_deprovision_example
```

### Example 4: Keep Database Users

If you want to delete only the cluster but keep database users:

```bash
export ATLAS_PROJECT_ID="507f1f77bcf86cd799439011"
export ATLAS_CLUSTER_NAME="mas-mongodb-cluster"
export ATLAS_PUBLIC_KEY="abcdefgh"
export ATLAS_PRIVATE_KEY="12345678-1234-1234-1234-123456789abc"
export ATLAS_REMOVE_DB_USERS="false"

ansible-playbook ibm.mas_devops.mongodb_atlas_deprovision_example
```

### Example 5: Using in Custom Playbook

```yaml
---
- hosts: localhost
  vars:
    mongodb_provider: atlas
    mongodb_action: deprovision
    atlas_project_id: "507f1f77bcf86cd799439011"
    atlas_cluster_name: "mas-mongodb-cluster"
    atlas_public_key: "{{ lookup('env', 'ATLAS_PUBLIC_KEY') }}"
    atlas_private_key: "{{ lookup('env', 'ATLAS_PRIVATE_KEY') }}"
    atlas_wait_for_deletion: true
    atlas_remove_db_users: true

  roles:
    - ibm.mas_devops.mongodb
```

## Deprovision Process Details

### Step 1: Credential Retrieval
- If using AWS Secrets Manager, retrieves Atlas API credentials
- Validates that credentials are available

### Step 2: Cluster Verification
- Checks if the cluster exists
- If cluster doesn't exist, skips deletion steps

### Step 3: Database User Cleanup
- Retrieves all database users in the project
- Deletes each user using Digest authentication
- Continues even if some deletions fail

### Step 4: Cluster Deletion
- Initiates cluster deletion via Atlas API
- Returns immediately (deletion happens in background)

### Step 5: Wait for Deletion (Optional)
- Polls Atlas API every 30 seconds
- Waits up to 20 minutes for deletion to complete
- Can be disabled with `ATLAS_WAIT_FOR_DELETION=false`

### Step 6: MAS Config Cleanup (Optional)
- Removes MAS MongoDB configuration file if it exists
- Only runs if `MAS_INSTANCE_ID` and `MAS_CONFIG_DIR` are set

## Timing Expectations

- **Database User Cleanup**: 1-2 minutes
- **Cluster Deletion Initiation**: 10-30 seconds
- **Cluster Deletion Completion**: 5-15 minutes (if waiting)

Total time: 6-17 minutes (depending on whether you wait for deletion)

## Safety Features

1. **Confirmation Prompt**: The example playbook prompts for confirmation before proceeding
2. **Idempotent**: Safe to run multiple times - skips if cluster doesn't exist
3. **Graceful Failures**: Continues even if some cleanup steps fail
4. **No Data Loss Risk**: Only deletes the specified cluster

## Troubleshooting

### Error: "401 Unauthorized"
- **Cause**: Invalid Atlas API credentials or insufficient permissions
- **Solution**: Verify your API key has "Project Owner" or "Organization Owner" role

### Error: "Cluster not found"
- **Cause**: Cluster has already been deleted or name is incorrect
- **Solution**: Verify cluster name and project ID are correct

### Error: "AWS CLI not found"
- **Cause**: AWS CLI not installed (when using Secrets Manager)
- **Solution**: Install AWS CLI or use direct credentials instead

### Cluster Deletion Takes Too Long
- **Cause**: Large clusters take longer to delete
- **Solution**: Set `ATLAS_WAIT_FOR_DELETION=false` to not wait, or increase timeout

### Some Resources Not Deleted
- **Cause**: Permissions issue or resources in use
- **Solution**: Check Atlas console and manually delete remaining resources

## Best Practices

1. **Always backup data** before deprovisioning
2. **Use confirmation prompts** in production environments
3. **Document cluster details** before deletion
4. **Verify deletion** in Atlas console after completion
5. **Use AWS Secrets Manager** for credential management in production
6. **Test in development** environment first

## Related Documentation

- [MongoDB Atlas Provision Guide](mongodb-atlas-provision-test-commands.md)
- [MongoDB Atlas API Documentation](https://www.mongodb.com/docs/atlas/api/)
- [MAS DevOps Collection README](../ibm/mas_devops/README.md)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review MongoDB Atlas API documentation
3. Open an issue in the repository
4. Contact IBM MAS support