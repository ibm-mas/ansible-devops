# MongoDB Atlas Uninstall Guide

This guide explains how to uninstall (delete) MongoDB Atlas clusters using the Ansible automation.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration Options](#configuration-options)
- [Usage Examples](#usage-examples)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)

## Overview

The MongoDB Atlas uninstall functionality provides automated deletion of:

- **Atlas Clusters** - The MongoDB cluster itself
- **Database Users** - Optionally delete the database user created during provisioning
- **IP Access List** - Optionally remove IP whitelist entries

### What Gets Deleted

| Resource | Default Behavior | Configurable |
|----------|-----------------|--------------|
| Atlas Cluster | Always deleted | No |
| Database User | Deleted if `atlas_db_username` is provided | Yes |
| IP Access List | Not deleted | Yes (via `atlas_delete_ip_access_list`) |

### Important Warnings

⚠️ **CLUSTER DELETION IS PERMANENT**
- All data in the cluster will be lost
- Deletion cannot be undone
- Ensure you have backups before proceeding

⚠️ **BILLING IMPLICATIONS**
- Billing stops once cluster is deleted
- Prorated charges apply for partial month usage
- Deletion may take 5-30 minutes depending on cluster size

## Prerequisites

### 1. Atlas API Credentials

You need Atlas API credentials with the following permissions:
- **Project Owner** or **Organization Owner** role
- API key must have access to the project

### 2. IP Access List for API

Your IP address must be on the **Atlas API Access List**:

1. Log into [MongoDB Atlas](https://cloud.mongodb.com)
2. Go to **Organization Settings** → **Access Manager** → **API Keys**
3. Find your API key and click **Edit**
4. Add your IP address to the **API Access List**

**Common Error:**
```
Status code was 403 and not [200, 404]: HTTP Error 403: Forbidden
"errorCode": "IP_ADDRESS_NOT_ON_ACCESS_LIST"
```

**Solution:** Add your current IP to the API Access List (see above)

### 3. Required Tools

- Ansible 2.9+
- AWS CLI (if using AWS Secrets Manager)
- Python 3.6+

## Quick Start

### Step 1: Set Up Credentials

**Option A: Using AWS Secrets Manager (Recommended)**

```bash
# Ensure AWS CLI is configured
aws configure

# Verify secret exists
aws secretsmanager get-secret-value \
  --secret-id mongodb-atlas-api-credentials \
  --region us-east-1
```

**Option B: Using Environment Variables**

```bash
export ATLAS_PUBLIC_KEY="your-public-key"
export ATLAS_PRIVATE_KEY="your-private-key"
```

### Step 2: Create Uninstall Playbook

Create `uninstall-atlas.yml`:

```yaml
---
- name: "Uninstall MongoDB Atlas cluster"
  hosts: localhost
  connection: local
  vars:
    mongodb_provider: atlas
    mongodb_action: uninstall
    
    # AWS Secrets Manager (or use direct credentials)
    atlas_aws_secret_name: "mongodb-atlas-api-credentials"
    atlas_aws_secret_region: "us-east-1"
    
    # Cluster to delete
    atlas_project_id: "YOUR_PROJECT_ID"
    atlas_cluster_name: "mas-test-cluster"
    
    # Optional: Delete database user
    atlas_db_username: "mas-admin"
    
    # Optional: Delete IP access list entries
    atlas_delete_ip_access_list: false
    
  roles:
    - ibm.mas_devops.mongodb
```

### Step 3: Run Uninstall

```bash
ansible-playbook uninstall-atlas.yml
```

### Step 4: Monitor Progress

The playbook will:
1. ✅ Check if cluster exists
2. ✅ Delete database user (if specified)
3. ✅ Delete IP access list entries (if enabled)
4. ✅ Initiate cluster deletion
5. ✅ Wait for deletion to complete (up to 30 minutes)

## Configuration Options

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `mongodb_provider` | Must be set to `atlas` | `atlas` |
| `mongodb_action` | Must be set to `uninstall` | `uninstall` |
| `atlas_project_id` | Atlas project ID | `68ffa9d908ff531136cef231` |
| `atlas_cluster_name` | Name of cluster to delete | `mas-test-cluster` |

### Authentication Variables

**Option 1: AWS Secrets Manager**

| Variable | Description | Default |
|----------|-------------|---------|
| `atlas_aws_secret_name` | AWS secret name | - |
| `atlas_aws_secret_region` | AWS region | `us-east-1` |

**Option 2: Direct Credentials**

| Variable | Description | Default |
|----------|-------------|---------|
| `atlas_public_key` | Atlas API public key | - |
| `atlas_private_key` | Atlas API private key | - |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `atlas_db_username` | Database user to delete | - (skip deletion) |
| `atlas_delete_ip_access_list` | Delete IP access list entries | `false` |
| `atlas_ip_access_list` | List of IPs to remove | `[]` |
| `atlas_delete_wait_timeout` | Max wait time (seconds) | `1800` (30 min) |

## Usage Examples

### Example 1: Basic Uninstall (Cluster Only)

```yaml
---
- name: "Delete cluster only"
  hosts: localhost
  connection: local
  vars:
    mongodb_provider: atlas
    mongodb_action: uninstall
    atlas_aws_secret_name: "mongodb-atlas-api-credentials"
    atlas_aws_secret_region: "us-east-1"
    atlas_project_id: "68ffa9d908ff531136cef231"
    atlas_cluster_name: "mas-test-cluster"
  roles:
    - ibm.mas_devops.mongodb
```

### Example 2: Complete Cleanup

```yaml
---
- name: "Delete cluster, user, and IP access list"
  hosts: localhost
  connection: local
  vars:
    mongodb_provider: atlas
    mongodb_action: uninstall
    atlas_aws_secret_name: "mongodb-atlas-api-credentials"
    atlas_aws_secret_region: "us-east-1"
    atlas_project_id: "68ffa9d908ff531136cef231"
    atlas_cluster_name: "mas-test-cluster"
    atlas_db_username: "mas-admin"
    atlas_delete_ip_access_list: true
    atlas_ip_access_list:
      - "172.16.0.0/12"
      - "152.59.32.98/32"
  roles:
    - ibm.mas_devops.mongodb
```

### Example 3: Using Direct Credentials

```yaml
---
- name: "Uninstall with direct credentials"
  hosts: localhost
  connection: local
  vars:
    mongodb_provider: atlas
    mongodb_action: uninstall
    atlas_public_key: "{{ lookup('env', 'ATLAS_PUBLIC_KEY') }}"
    atlas_private_key: "{{ lookup('env', 'ATLAS_PRIVATE_KEY') }}"
    atlas_project_id: "68ffa9d908ff531136cef231"
    atlas_cluster_name: "mas-test-cluster"
    atlas_db_username: "mas-admin"
  roles:
    - ibm.mas_devops.mongodb
```

### Example 4: Multiple Clusters

```yaml
---
- name: "Uninstall multiple clusters"
  hosts: localhost
  connection: local
  vars:
    mongodb_provider: atlas
    mongodb_action: uninstall
    atlas_aws_secret_name: "mongodb-atlas-api-credentials"
    atlas_aws_secret_region: "us-east-1"
    atlas_project_id: "68ffa9d908ff531136cef231"
  tasks:
    - name: "Delete dev cluster"
      include_role:
        name: ibm.mas_devops.mongodb
      vars:
        atlas_cluster_name: "mas-dev-cluster"
        atlas_db_username: "mas-dev-admin"
    
    - name: "Delete staging cluster"
      include_role:
        name: ibm.mas_devops.mongodb
      vars:
        atlas_cluster_name: "mas-staging-cluster"
        atlas_db_username: "mas-staging-admin"
```

### Example 5: Custom Timeout for Large Clusters

```yaml
---
- name: "Uninstall large cluster with extended timeout"
  hosts: localhost
  connection: local
  vars:
    mongodb_provider: atlas
    mongodb_action: uninstall
    atlas_aws_secret_name: "mongodb-atlas-api-credentials"
    atlas_aws_secret_region: "us-east-1"
    atlas_project_id: "68ffa9d908ff531136cef231"
    atlas_cluster_name: "mas-large-cluster"
    atlas_db_username: "mas-admin"
    atlas_delete_wait_timeout: 3600  # 60 minutes
  roles:
    - ibm.mas_devops.mongodb
```

## Troubleshooting

### Error: 403 Forbidden - IP_ADDRESS_NOT_ON_ACCESS_LIST

**Problem:** Your IP is not on the Atlas API Access List

**Solution:**
1. Log into MongoDB Atlas
2. Go to **Organization Settings** → **Access Manager** → **API Keys**
3. Edit your API key
4. Add your current IP to the **API Access List**
5. Get your current IP: `curl https://api.ipify.org`

### Error: 404 Not Found - Cluster doesn't exist

**Problem:** Cluster has already been deleted

**Solution:** This is expected behavior. The playbook will skip deletion and complete successfully.

### Error: Timeout waiting for deletion

**Problem:** Cluster deletion is taking longer than expected

**Solution:**
1. Check Atlas console to verify deletion is in progress
2. Increase `atlas_delete_wait_timeout` (default: 1800 seconds)
3. Large clusters can take 30+ minutes to delete

### Error: Invalid credentials

**Problem:** Atlas API credentials are incorrect or expired

**Solution:**
1. Verify credentials in AWS Secrets Manager or environment variables
2. Test credentials manually:
   ```bash
   curl --user "${ATLAS_PUBLIC_KEY}:${ATLAS_PRIVATE_KEY}" \
     --digest \
     "https://cloud.mongodb.com/api/atlas/v1.0/groups/${PROJECT_ID}/clusters"
   ```

### Cluster still shows in Atlas after deletion

**Problem:** Atlas UI may cache cluster status

**Solution:**
1. Wait 5-10 minutes and refresh the page
2. Check the cluster list API directly
3. Verify deletion completed in playbook output

## FAQ

### Q: Can I recover a deleted cluster?

**A:** No. Cluster deletion is permanent and cannot be undone. Always ensure you have backups before deleting.

### Q: Will I be charged after deletion?

**A:** Billing stops once the cluster is deleted. You'll be charged for the prorated usage up to the deletion time.

### Q: How long does deletion take?

**A:** 
- Small clusters (M10-M20): 5-10 minutes
- Medium clusters (M30-M50): 10-20 minutes
- Large clusters (M60+): 20-30 minutes

### Q: What happens to my data?

**A:** All data is permanently deleted. There is no recovery option unless you have backups.

### Q: Can I delete just the database user?

**A:** Yes, set `atlas_db_username` but don't run the uninstall action. Instead, use the Atlas UI or API directly to delete the user.

### Q: Will this delete all users in my project?

**A:** No. Only the user specified in `atlas_db_username` is deleted. Other users are not affected.

### Q: Can I delete multiple clusters at once?

**A:** Yes, use the multiple clusters example (Example 4) or run the playbook multiple times with different cluster names.

### Q: What if my IP address changes during deletion?

**A:** The deletion will continue in the background. You can check status in the Atlas console.

### Q: Is there a dry-run mode?

**A:** Yes, use `--check` flag:
```bash
ansible-playbook uninstall-atlas.yml --check
```

### Q: Can I cancel a deletion in progress?

**A:** No. Once deletion is initiated, it cannot be cancelled.

## Best Practices

1. **Always backup data** before deleting clusters
2. **Verify cluster name** to avoid deleting the wrong cluster
3. **Use AWS Secrets Manager** for credential management
4. **Test in development** before running in production
5. **Document deletions** for audit purposes
6. **Check dependencies** - ensure no applications are using the cluster
7. **Review billing** after deletion to confirm charges stopped

## Related Documentation

- [MongoDB Atlas Provisioning Guide](mongodb-atlas-provision-guide.md)
- [AWS Secrets Manager Setup](mongodb-atlas-aws-secrets-setup.md)
- [MongoDB Atlas API Documentation](https://www.mongodb.com/docs/atlas/api/)

## Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review the [FAQ](#faq)
3. Check MongoDB Atlas documentation
4. Contact your MongoDB support team

---

**Made with Bob** - MongoDB Atlas Uninstall Automation