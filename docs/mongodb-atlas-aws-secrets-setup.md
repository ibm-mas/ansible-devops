# MongoDB Atlas with AWS Secrets Manager - Setup Guide

## Overview

This guide explains how to securely store and retrieve MongoDB Atlas API credentials using AWS Secrets Manager for use with the MAS DevOps Ansible collection.

## Table of Contents

1. [Why Use AWS Secrets Manager?](#why-use-aws-secrets-manager)
2. [Prerequisites](#prerequisites)
3. [Setup Steps](#setup-steps)
4. [Usage Examples](#usage-examples)
5. [Security Best Practices](#security-best-practices)
6. [Troubleshooting](#troubleshooting)

---

## Why Use AWS Secrets Manager?

### Benefits

✅ **Security**: Credentials are encrypted at rest and in transit  
✅ **Centralized Management**: Single source of truth for credentials  
✅ **Audit Trail**: Track who accessed credentials and when  
✅ **Rotation**: Automatic credential rotation support  
✅ **Access Control**: Fine-grained IAM permissions  
✅ **No Hardcoding**: Credentials never stored in code or playbooks  

### Cost

- **Storage**: $0.40 per secret per month
- **API Calls**: $0.05 per 10,000 API calls
- **Typical Cost**: ~$0.50/month for Atlas credentials

---

## Prerequisites

### Required Tools

```bash
# AWS CLI
aws --version  # Should be 2.x or higher

# jq (for JSON parsing)
jq --version

# Ansible
ansible --version  # Should be 2.9 or higher
```

### Required Permissions

Your AWS IAM user/role needs these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:CreateSecret",
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret",
        "secretsmanager:PutSecretValue",
        "secretsmanager:UpdateSecret",
        "secretsmanager:TagResource"
      ],
      "Resource": "arn:aws:secretsmanager:*:*:secret:mongodb-atlas-*"
    }
  ]
}
```

### MongoDB Atlas Requirements

- Atlas account with Organization or Project Owner role
- API keys generated (see [Generating Atlas API Keys](#generating-atlas-api-keys))

---

## Setup Steps

### Step 1: Generate MongoDB Atlas API Keys

1. **Login to MongoDB Atlas**
   - Go to https://cloud.mongodb.com
   - Navigate to your organization

2. **Create API Key**
   - Click "Access Manager" → "Organization Access" → "API Keys"
   - Click "Create API Key"
   - Name: `mas-devops-automation`
   - Permissions: `Organization Project Creator` or `Project Owner`

3. **Save Credentials**
   ```bash
   # Save these securely - you'll only see the private key once!
   PUBLIC_KEY="abcd1234"
   PRIVATE_KEY="12345678-1234-1234-1234-123456789abc"
   ```

4. **Configure IP Access List**
   - Add your IP address or `0.0.0.0/0` (for testing only)
   - For production, use specific IP ranges

### Step 2: Configure AWS CLI

```bash
# Configure AWS credentials
aws configure

# Verify configuration
aws sts get-caller-identity

# Expected output:
# {
#     "UserId": "AIDAXXXXXXXXXXXXXXXXX",
#     "Account": "123456789012",
#     "Arn": "arn:aws:iam::123456789012:user/your-user"
# }
```

### Step 3: Create Secret in AWS Secrets Manager

#### Option A: Using AWS CLI (Recommended)

```bash
# Create secret with Atlas API credentials
aws secretsmanager create-secret \
  --name mongodb-atlas-api-credentials \
  --description "MongoDB Atlas API credentials for MAS DevOps automation" \
  --secret-string '{
    "public_key": "YOUR_ATLAS_PUBLIC_KEY",
    "private_key": "YOUR_ATLAS_PRIVATE_KEY"
  }' \
  --tags Key=Environment,Value=Production Key=Application,Value=MAS \
  --region us-east-1

# Expected output:
# {
#     "ARN": "arn:aws:secretsmanager:us-east-1:123456789012:secret:mongodb-atlas-api-credentials-AbCdEf",
#     "Name": "mongodb-atlas-api-credentials",
#     "VersionId": "12345678-1234-1234-1234-123456789abc"
# }
```

#### Option B: Using AWS Console

1. Go to AWS Secrets Manager console
2. Click "Store a new secret"
3. Select "Other type of secret"
4. Add key-value pairs:
   - Key: `public_key`, Value: `YOUR_ATLAS_PUBLIC_KEY`
   - Key: `private_key`, Value: `YOUR_ATLAS_PRIVATE_KEY`
5. Name: `mongodb-atlas-api-credentials`
6. Add tags (optional)
7. Review and store

#### Option C: Using Terraform

```hcl
resource "aws_secretsmanager_secret" "atlas_credentials" {
  name        = "mongodb-atlas-api-credentials"
  description = "MongoDB Atlas API credentials for MAS DevOps"

  tags = {
    Environment = "Production"
    Application = "MAS"
  }
}

resource "aws_secretsmanager_secret_version" "atlas_credentials" {
  secret_id = aws_secretsmanager_secret.atlas_credentials.id
  secret_string = jsonencode({
    public_key  = var.atlas_public_key
    private_key = var.atlas_private_key
  })
}
```

### Step 4: Verify Secret Creation

```bash
# List secrets
aws secretsmanager list-secrets \
  --region us-east-1 \
  --filters Key=name,Values=mongodb-atlas

# Get secret metadata (no credentials shown)
aws secretsmanager describe-secret \
  --secret-id mongodb-atlas-api-credentials \
  --region us-east-1

# Retrieve secret value (CAREFUL - shows credentials!)
aws secretsmanager get-secret-value \
  --secret-id mongodb-atlas-api-credentials \
  --region us-east-1 \
  --query SecretString \
  --output text | jq '.'
```

### Step 5: Grant Access to IAM Users/Roles

```bash
# Create IAM policy
aws iam create-policy \
  --policy-name MongoDBAtlasSecretsAccess \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret"
      ],
      "Resource": "arn:aws:secretsmanager:*:*:secret:mongodb-atlas-*"
    }]
  }'

# Attach policy to user
aws iam attach-user-policy \
  --user-name ansible-automation \
  --policy-arn arn:aws:iam::123456789012:policy/MongoDBAtlasSecretsAccess

# Or attach to role
aws iam attach-role-policy \
  --role-name ansible-automation-role \
  --policy-arn arn:aws:iam::123456789012:policy/MongoDBAtlasSecretsAccess
```

---

## Usage Examples

### Example 1: Provision Atlas Cluster

```bash
# Set database password (not stored in Secrets Manager)
export ATLAS_DB_PASSWORD="SecurePassword123!"

# Run provisioning with AWS Secrets Manager
ansible-playbook \
  --connection=local \
  ibm/mas_devops/playbooks/mongodb_atlas_provision_example.yml \
  -e mongodb_provider=atlas \
  -e mongodb_action=provision \
  -e atlas_aws_secret_name="mongodb-atlas-api-credentials" \
  -e atlas_aws_secret_region="us-east-1" \
  -e atlas_project_id="YOUR_PROJECT_ID" \
  -e atlas_cluster_name="mas-prod-cluster" \
  -e atlas_cluster_provider="AWS" \
  -e atlas_cluster_region="US_EAST_1" \
  -e atlas_cluster_size="M10" \
  -e atlas_db_username="mas-admin" \
  -e atlas_ip_access_list="0.0.0.0/0" \
  -v
```

### Example 2: Configure MAS Integration

```bash
export ATLAS_DB_PASSWORD="SecurePassword123!"

ansible-playbook \
  --connection=local \
  ibm/mas_devops/playbooks/mongodb_atlas_example.yml \
  -e mongodb_provider=atlas \
  -e mongodb_action=install \
  -e atlas_aws_secret_name="mongodb-atlas-api-credentials" \
  -e atlas_aws_secret_region="us-east-1" \
  -e atlas_project_id="YOUR_PROJECT_ID" \
  -e atlas_cluster_name="mas-prod-cluster" \
  -e atlas_db_username="mas-admin" \
  -e mas_instance_id="prod" \
  -e mas_config_dir="/tmp/masconfig" \
  -v
```

### Example 3: Using Environment Variables

```bash
# Set environment variables
export ATLAS_AWS_SECRET_NAME="mongodb-atlas-api-credentials"
export ATLAS_AWS_SECRET_REGION="us-east-1"
export ATLAS_PROJECT_ID="YOUR_PROJECT_ID"
export ATLAS_CLUSTER_NAME="mas-cluster"
export ATLAS_DB_USERNAME="mas-admin"
export ATLAS_DB_PASSWORD="SecurePassword123!"

# Run playbook (variables auto-loaded from environment)
ansible-playbook \
  --connection=local \
  ibm/mas_devops/playbooks/mongodb_atlas_provision_example.yml \
  -e mongodb_provider=atlas \
  -e mongodb_action=provision \
  -v
```

---

## Security Best Practices

### 1. Least Privilege Access

```bash
# Create separate secrets for different environments
aws secretsmanager create-secret \
  --name mongodb-atlas-dev-credentials \
  --secret-string '{"public_key":"DEV_KEY","private_key":"DEV_SECRET"}'

aws secretsmanager create-secret \
  --name mongodb-atlas-prod-credentials \
  --secret-string '{"public_key":"PROD_KEY","private_key":"PROD_SECRET"}'

# Grant environment-specific access
# Dev team: access to dev secrets only
# Ops team: access to all secrets
```

### 2. Enable Secret Rotation

```bash
# Enable automatic rotation (requires Lambda function)
aws secretsmanager rotate-secret \
  --secret-id mongodb-atlas-api-credentials \
  --rotation-lambda-arn arn:aws:lambda:us-east-1:123456789012:function:SecretsManagerRotation \
  --rotation-rules AutomaticallyAfterDays=90
```

### 3. Enable CloudTrail Logging

```bash
# Create CloudTrail for audit logging
aws cloudtrail create-trail \
  --name secrets-manager-audit \
  --s3-bucket-name my-audit-logs-bucket

# Start logging
aws cloudtrail start-logging \
  --name secrets-manager-audit

# View who accessed secrets
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=ResourceName,AttributeValue=mongodb-atlas-api-credentials
```

### 4. Use Resource Policies

```bash
# Restrict secret access to specific IAM roles
aws secretsmanager put-resource-policy \
  --secret-id mongodb-atlas-api-credentials \
  --resource-policy '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::123456789012:role/ansible-automation-role"
      },
      "Action": "secretsmanager:GetSecretValue",
      "Resource": "*"
    }]
  }'
```

### 5. Enable Encryption with KMS

```bash
# Create KMS key
aws kms create-key \
  --description "MongoDB Atlas secrets encryption key"

# Use KMS key for secret encryption
aws secretsmanager create-secret \
  --name mongodb-atlas-api-credentials \
  --secret-string '{"public_key":"KEY","private_key":"SECRET"}' \
  --kms-key-id arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789abc
```

---

## Troubleshooting

### Issue 1: Access Denied

**Error:**
```
An error occurred (AccessDeniedException) when calling the GetSecretValue operation
```

**Solution:**
```bash
# Check IAM permissions
aws iam get-user-policy --user-name YOUR_USER --policy-name SecretsManagerAccess

# Verify secret exists
aws secretsmanager describe-secret --secret-id mongodb-atlas-api-credentials

# Test access
aws secretsmanager get-secret-value --secret-id mongodb-atlas-api-credentials --query SecretString
```

### Issue 2: Secret Not Found

**Error:**
```
ResourceNotFoundException: Secrets Manager can't find the specified secret
```

**Solution:**
```bash
# List all secrets
aws secretsmanager list-secrets

# Check region
aws secretsmanager list-secrets --region us-east-1

# Verify secret name (case-sensitive)
aws secretsmanager describe-secret --secret-id mongodb-atlas-api-credentials
```

### Issue 3: Invalid JSON Format

**Error:**
```
Invalid JSON in secret string
```

**Solution:**
```bash
# Validate JSON before creating secret
echo '{"public_key":"KEY","private_key":"SECRET"}' | jq '.'

# Update secret with valid JSON
aws secretsmanager update-secret \
  --secret-id mongodb-atlas-api-credentials \
  --secret-string '{"public_key":"VALID_KEY","private_key":"VALID_SECRET"}'
```

### Issue 4: Ansible Can't Parse Secret

**Error:**
```
Failed to parse secret value as JSON
```

**Solution:**
```bash
# Verify secret structure
aws secretsmanager get-secret-value \
  --secret-id mongodb-atlas-api-credentials \
  --query SecretString \
  --output text | jq '.'

# Ensure keys match expected names
# Required: "public_key" and "private_key"
```

---

## Maintenance

### Update Credentials

```bash
# Update secret value
aws secretsmanager update-secret \
  --secret-id mongodb-atlas-api-credentials \
  --secret-string '{
    "public_key": "NEW_PUBLIC_KEY",
    "private_key": "NEW_PRIVATE_KEY"
  }'

# Verify update
aws secretsmanager get-secret-value \
  --secret-id mongodb-atlas-api-credentials \
  --version-stage AWSCURRENT
```

### Delete Secret

```bash
# Schedule deletion (7-30 days recovery window)
aws secretsmanager delete-secret \
  --secret-id mongodb-atlas-api-credentials \
  --recovery-window-in-days 30

# Force immediate deletion (CAUTION: No recovery!)
aws secretsmanager delete-secret \
  --secret-id mongodb-atlas-api-credentials \
  --force-delete-without-recovery

# Restore deleted secret (within recovery window)
aws secretsmanager restore-secret \
  --secret-id mongodb-atlas-api-credentials
```

### Monitor Costs

```bash
# View Secrets Manager costs
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics UnblendedCost \
  --filter file://filter.json

# filter.json:
# {
#   "Dimensions": {
#     "Key": "SERVICE",
#     "Values": ["AWS Secrets Manager"]
#   }
# }
```

---

## Additional Resources

- [AWS Secrets Manager Documentation](https://docs.aws.amazon.com/secretsmanager/)
- [MongoDB Atlas API Keys](https://docs.atlas.mongodb.com/configure-api-access/)
- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [Ansible Vault Alternative](https://docs.ansible.com/ansible/latest/user_guide/vault.html)

---

**Created by Bob** - MongoDB Atlas AWS Secrets Manager Setup Guide