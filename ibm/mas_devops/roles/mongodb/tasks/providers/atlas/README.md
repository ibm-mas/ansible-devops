# MongoDB Atlas Provider Tasks

This directory contains Ansible tasks for managing MongoDB Atlas clusters.

## Available Actions

### 1. Provision (`provision.yml`)
Creates a new MongoDB Atlas cluster with database users and network configuration.

**Usage:**
```yaml
mongodb_provider: atlas
mongodb_action: provision
```

**Key Features:**
- Creates Atlas cluster
- Configures database users
- Sets up IP access list (whitelist)
- Supports AWS Secrets Manager for credentials
- Waits for cluster to be ready

**Documentation:** See [mongodb_atlas_provision_example.yml](../../../../playbooks/mongodb_atlas_provision_example.yml)

---

### 2. Install (`install.yml`)
Connects to an existing Atlas cluster and configures MAS integration.

**Usage:**
```yaml
mongodb_provider: atlas
mongodb_action: install
```

**Key Features:**
- Retrieves cluster connection strings
- Downloads CA certificates
- Generates MAS MongoCfg configuration
- Supports private endpoints

**Documentation:** See [mongodb-atlas-install.yml](../../../../playbooks/mongodb-atlas-install.yml)

---

### 3. Uninstall (`uninstall.yml`)
Deletes MongoDB Atlas cluster and optionally removes database users and IP access list entries.

**Usage:**
```yaml
mongodb_provider: atlas
mongodb_action: uninstall
```

**Key Features:**
- Checks cluster existence before deletion
- Deletes database user (optional)
- Removes IP access list entries (optional)
- Waits for deletion to complete
- Graceful handling of already-deleted resources

**Documentation:** 
- [Uninstall Guide](../../../../../docs/mongodb-atlas-uninstall-guide.md)
- [Example Playbook](../../../../playbooks/mongodb_atlas_uninstall_example.yml)

**Configuration Options:**
```yaml
# Required
atlas_project_id: "your-project-id"
atlas_cluster_name: "your-cluster-name"

# Optional
atlas_db_username: "user-to-delete"              # Leave empty to skip user deletion
atlas_delete_ip_access_list: false               # Set true to remove IP entries
atlas_ip_access_list: ["10.0.0.0/8"]            # IPs to remove (if enabled)
atlas_delete_wait_timeout: 1800                  # Max wait time in seconds
```

---

## Authentication

All actions support two authentication methods:

### Option 1: AWS Secrets Manager (Recommended)
```yaml
atlas_aws_secret_name: "mongodb-atlas-api-credentials"
atlas_aws_secret_region: "us-east-1"
```

Secret format:
```json
{
  "public_key": "your-public-key",
  "private_key": "your-private-key"
}
```

### Option 2: Direct Credentials
```yaml
atlas_public_key: "{{ lookup('env', 'ATLAS_PUBLIC_KEY') }}"
atlas_private_key: "{{ lookup('env', 'ATLAS_PRIVATE_KEY') }}"
```

---

## Common Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `atlas_project_id` | Atlas project ID | Yes | - |
| `atlas_cluster_name` | Cluster name | Yes | - |
| `atlas_public_key` | API public key | Yes* | - |
| `atlas_private_key` | API private key | Yes* | - |
| `atlas_aws_secret_name` | AWS secret name | Yes* | - |
| `atlas_aws_secret_region` | AWS region | No | `us-east-1` |

*Either direct credentials OR AWS Secrets Manager must be provided

---

## API Access Requirements

⚠️ **Important:** Your IP address must be on the Atlas API Access List

**Setup:**
1. Log into [MongoDB Atlas](https://cloud.mongodb.com)
2. Go to **Organization Settings** → **Access Manager** → **API Keys**
3. Edit your API key
4. Add your IP to the **API Access List**

**Common Error:**
```
Status code was 403 and not [200, 404]: HTTP Error 403: Forbidden
"errorCode": "IP_ADDRESS_NOT_ON_ACCESS_LIST"
```

---

## Quick Start Examples

### Provision a Cluster
```bash
ansible-playbook ibm/mas_devops/playbooks/mongodb_atlas_provision_example.yml
```

### Uninstall a Cluster
```bash
ansible-playbook ibm/mas_devops/playbooks/mongodb_atlas_uninstall_example.yml
```

### Install MAS Integration
```bash
ansible-playbook ibm/mas_devops/playbooks/mongodb-atlas-install.yml
```

---

## Troubleshooting

### 403 Forbidden Error
- **Cause:** IP not on API Access List
- **Solution:** Add your IP in Atlas Organization Settings → API Keys

### 404 Not Found (during uninstall)
- **Cause:** Cluster already deleted
- **Solution:** This is expected; playbook will complete successfully

### Timeout Errors
- **Cause:** Operation taking longer than expected
- **Solution:** Increase timeout values or check Atlas console

---

## Related Documentation

- [MongoDB Atlas Uninstall Guide](../../../../../docs/mongodb-atlas-uninstall-guide.md)
- [AWS Secrets Manager Setup](../../../../../docs/mongodb-atlas-aws-secrets-setup.md)
- [MongoDB Atlas API Docs](https://www.mongodb.com/docs/atlas/api/)

---

**Made with Bob** - MongoDB Atlas Provider Tasks