# Quick Start - Test MongoDB Atlas Provisioning

## Step-by-Step Testing Guide

Follow these commands in order to test the MongoDB Atlas provisioning with AWS Secrets Manager.

---

## Prerequisites Check

```bash
# 1. Check Ansible is installed
ansible --version
# Expected: ansible 2.9 or higher

# 2. Check AWS CLI is installed and configured
aws --version
aws sts get-caller-identity
# Should show your AWS account details

# 3. Check you're in the correct directory
pwd
# Should be: /Users/prajapatiyogeshkumatr/DEVELOP-SAAS/ansible-devops
```

---

## Step 1: Setup AWS Secrets Manager (One-time setup)

```bash
# Replace YOUR_ATLAS_PUBLIC_KEY and YOUR_ATLAS_PRIVATE_KEY with your actual Atlas API keys
aws secretsmanager create-secret \
  --name mongodb-atlas-api-credentials \
  --description "MongoDB Atlas API credentials for MAS" \
  --secret-string '{
    "public_key": "YOUR_ATLAS_PUBLIC_KEY",
    "private_key": "YOUR_ATLAS_PRIVATE_KEY"
  }' \
  --region us-east-1

# Verify secret was created
aws secretsmanager describe-secret \
  --secret-id mongodb-atlas-api-credentials \
  --region us-east-1
```

---

## Step 2: Test Syntax (Dry Run)

```bash
# Check playbook syntax
ansible-playbook \
  ibm/mas_devops/playbooks/mongodb_atlas_provision_example.yml \
  --syntax-check

# Expected output: "playbook: ... Syntax OK"
```

---

## Step 3: Test Provision Action (Create Atlas Cluster)

### Option A: With AWS Secrets Manager (Recommended)

```bash
# Set your database password
export ATLAS_DB_PASSWORD="YourSecurePassword123!"

# Replace these values with your actual Atlas configuration:
# - YOUR_PROJECT_ID: Your Atlas project ID (found in Atlas UI)
# - mas-test-cluster: Name for your new cluster

ansible-playbook \
  --connection=local \
  ibm/mas_devops/playbooks/mongodb_atlas_provision_example.yml \
  -e mongodb_provider=atlas \
  -e mongodb_action=provision \
  -e atlas_aws_secret_name="mongodb-atlas-api-credentials" \
  -e atlas_aws_secret_region="us-east-1" \
  -e atlas_project_id="YOUR_PROJECT_ID" \
  -e atlas_cluster_name="mas-test-cluster" \
  -e atlas_cluster_provider="AWS" \
  -e atlas_cluster_region="US_EAST_1" \
  -e atlas_cluster_size="M10" \
  -e atlas_mongodb_version="6.0" \
  -e atlas_backup_enabled=true \
  -e atlas_db_username="mas-admin" \
  -e atlas_ip_access_list="0.0.0.0/0" \
  -v

# This will take 7-10 minutes to provision the cluster
# Watch for "Cluster is ready" message
```

### Option B: Without AWS Secrets Manager (Direct credentials)

```bash
# Set environment variables
export ATLAS_PUBLIC_KEY="your-atlas-public-key"
export ATLAS_PRIVATE_KEY="your-atlas-private-key"
export ATLAS_DB_PASSWORD="YourSecurePassword123!"

ansible-playbook \
  --connection=local \
  ibm/mas_devops/playbooks/mongodb_atlas_provision_example.yml \
  -e mongodb_provider=atlas \
  -e mongodb_action=provision \
  -e atlas_project_id="YOUR_PROJECT_ID" \
  -e atlas_cluster_name="mas-test-cluster" \
  -e atlas_cluster_provider="AWS" \
  -e atlas_cluster_region="US_EAST_1" \
  -e atlas_cluster_size="M10" \
  -e atlas_db_username="mas-admin" \
  -e atlas_ip_access_list="0.0.0.0/0" \
  -v
```

---

## Step 4: Verify Cluster Creation

```bash
# Using curl (replace PUBLIC_KEY:PRIVATE_KEY and PROJECT_ID)
curl -u "PUBLIC_KEY:PRIVATE_KEY" \
  "https://cloud.mongodb.com/api/atlas/v1.0/groups/YOUR_PROJECT_ID/clusters/mas-test-cluster" \
  | jq '.stateName'

# Expected output: "IDLE" (cluster is ready)
```

---

## Step 5: Test Install Action (Configure MAS Integration)

```bash
# This connects to the existing cluster and generates MAS configuration
export ATLAS_DB_PASSWORD="YourSecurePassword123!"

ansible-playbook \
  --connection=local \
  ibm/mas_devops/playbooks/mongodb_atlas_example.yml \
  -e mongodb_provider=atlas \
  -e mongodb_action=install \
  -e atlas_aws_secret_name="mongodb-atlas-api-credentials" \
  -e atlas_aws_secret_region="us-east-1" \
  -e atlas_project_id="YOUR_PROJECT_ID" \
  -e atlas_cluster_name="mas-test-cluster" \
  -e atlas_db_username="mas-admin" \
  -e mas_instance_id="test" \
  -e mas_config_dir="/tmp/masconfig" \
  -v

# This should complete in 30-45 seconds
```

---

## Step 6: Verify MongoCfg Generation

```bash
# Check if MongoCfg file was created
ls -lh /tmp/masconfig/mongocfg-atlas-system.yaml

# View the generated configuration
cat /tmp/masconfig/mongocfg-atlas-system.yaml

# Validate YAML syntax
yamllint /tmp/masconfig/mongocfg-atlas-system.yaml
```

---

## Step 7: Test Connection (Optional)

```bash
# If you have mongosh installed
mongosh "mongodb+srv://mas-admin:YourSecurePassword123!@mas-test-cluster.xxxxx.mongodb.net/admin" \
  --eval "db.adminCommand('ping')"

# Expected output: { ok: 1 }
```

---

## Minimal Test Command (Fastest)

If you just want to test that everything works:

```bash
# 1. Setup (one-time)
export ATLAS_DB_PASSWORD="TestPassword123!"

# 2. Create secret (one-time)
aws secretsmanager create-secret \
  --name mongodb-atlas-api-credentials \
  --secret-string '{"public_key":"YOUR_KEY","private_key":"YOUR_SECRET"}' \
  --region us-east-1

# 3. Test provision (7-10 minutes)
ansible-playbook --connection=local \
  ibm/mas_devops/playbooks/mongodb_atlas_provision_example.yml \
  -e mongodb_provider=atlas \
  -e mongodb_action=provision \
  -e atlas_aws_secret_name="mongodb-atlas-api-credentials" \
  -e atlas_aws_secret_region="us-east-1" \
  -e atlas_project_id="YOUR_PROJECT_ID" \
  -e atlas_cluster_name="test-cluster" \
  -e atlas_cluster_provider="AWS" \
  -e atlas_cluster_region="US_EAST_1" \
  -e atlas_cluster_size="M10" \
  -e atlas_db_username="admin" \
  -e atlas_ip_access_list="0.0.0.0/0" \
  -v

# 4. Test install (30 seconds)
ansible-playbook --connection=local \
  ibm/mas_devops/playbooks/mongodb_atlas_example.yml \
  -e mongodb_provider=atlas \
  -e mongodb_action=install \
  -e atlas_aws_secret_name="mongodb-atlas-api-credentials" \
  -e atlas_aws_secret_region="us-east-1" \
  -e atlas_project_id="YOUR_PROJECT_ID" \
  -e atlas_cluster_name="test-cluster" \
  -e atlas_db_username="admin" \
  -e mas_instance_id="test" \
  -e mas_config_dir="/tmp/masconfig" \
  -v
```

---

## Troubleshooting

### Error: "Could not match supplied host pattern"

**Fix:** Add `--connection=local` to the ansible-playbook command

### Error: "AccessDeniedException" from AWS

**Fix:** Check AWS credentials:
```bash
aws sts get-caller-identity
aws secretsmanager describe-secret --secret-id mongodb-atlas-api-credentials --region us-east-1
```

### Error: "401 Unauthorized" from Atlas

**Fix:** Verify Atlas API keys in the secret:
```bash
aws secretsmanager get-secret-value \
  --secret-id mongodb-atlas-api-credentials \
  --region us-east-1 \
  --query SecretString \
  --output text | jq '.'
```

### Error: "Cluster already exists"

**Fix:** Either:
1. Use a different cluster name: `-e atlas_cluster_name="test-cluster-2"`
2. Or use `install` action instead of `provision`

---

## What You Need to Replace

Before running commands, replace these placeholders:

1. **YOUR_ATLAS_PUBLIC_KEY** - Get from Atlas UI → Organization → Access Manager → API Keys
2. **YOUR_ATLAS_PRIVATE_KEY** - Get from Atlas UI (shown only once when creating key)
3. **YOUR_PROJECT_ID** - Get from Atlas UI → Project Settings → Project ID
4. **YourSecurePassword123!** - Choose a strong password for the database user

---

## Expected Output

### Successful Provision:
```
TASK [MongoDB Atlas cluster provisioned successfully] ****
ok: [localhost] => {
    "msg": [
        "==========================================",
        "MongoDB Atlas Cluster Provisioned!",
        "==========================================",
        "Cluster Name ................ test-cluster",
        "Connection String (SRV) ..... mongodb+srv://test-cluster.xxxxx.mongodb.net",
        ...
    ]
}
```

### Successful Install:
```
TASK [MongoDB Atlas installation completed successfully] ****
ok: [localhost] => {
    "msg": [
        "==========================================",
        "MongoDB Atlas Configuration Complete!",
        "==========================================",
        "MongoCfg file created at:",
        "  /tmp/masconfig/mongocfg-atlas-system.yaml",
        ...
    ]
}
```

---

## Quick Reference

| Action | Time | What It Does |
|--------|------|--------------|
| `provision` | 7-10 min | Creates new Atlas cluster |
| `install` | 30-45 sec | Generates MAS configuration |
| `backup` | 1-2 min | Creates cluster snapshot |
| `restore` | 10-15 min | Restores from snapshot |
| `uninstall` | 10 sec | Removes MAS configuration |

---

**Ready to test!** Start with Step 1 and work your way through. 🚀