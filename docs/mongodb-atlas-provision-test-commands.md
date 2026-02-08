# Check MongoCfg status
oc describe mongocfg mongocfg-atlas-system -n mas-prod-core
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. AWS Secrets Manager Access Denied

**Error:**
```
An error occurred (AccessDeniedException) when calling the GetSecretValue operation
```

**Solution:**
```bash
# Verify AWS credentials
aws sts get-caller-identity

# Check IAM permissions
aws iam get-user-policy --user-name YOUR_USER --policy-name SecretsManagerAccess

# Grant required permissions
aws iam put-user-policy \
  --user-name YOUR_USER \
  --policy-name SecretsManagerAccess \
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
```

#### 2. Atlas API Authentication Failed

**Error:**
```
401 Unauthorized - Invalid API credentials
```

**Solution:**
```bash
# Verify credentials in AWS Secrets Manager
aws secretsmanager get-secret-value \
  --secret-id mongodb-atlas-api-credentials \
  --region us-east-1 \
  --query SecretString \
  --output text | jq '.'

# Test Atlas API directly
curl -u "PUBLIC_KEY:PRIVATE_KEY" \
  "https://cloud.mongodb.com/api/atlas/v1.0/groups/YOUR_PROJECT_ID" \
  | jq '.'

# Regenerate Atlas API keys if needed (via Atlas UI)
```

#### 3. Cluster Already Exists

**Error:**
```
Cluster with name 'mas-cluster' already exists
```

**Solution:**
```bash
# Option 1: Use different cluster name
ansible-playbook ... -e atlas_cluster_name="mas-cluster-v2"

# Option 2: Delete existing cluster (CAUTION: Data loss!)
curl -X DELETE -u "PUBLIC_KEY:PRIVATE_KEY" \
  "https://cloud.mongodb.com/api/atlas/v1.0/groups/YOUR_PROJECT_ID/clusters/mas-cluster"

# Option 3: Use install action instead of provision
ansible-playbook ... -e mongodb_action=install
```

#### 4. Cluster Provisioning Timeout

**Error:**
```
Cluster state is CREATING after 30 minutes
```

**Solution:**
```bash
# Increase timeout
ansible-playbook ... -e atlas_api_timeout=120

# Check cluster status manually
curl -u "PUBLIC_KEY:PRIVATE_KEY" \
  "https://cloud.mongodb.com/api/atlas/v1.0/groups/YOUR_PROJECT_ID/clusters/mas-cluster" \
  | jq '.stateName'

# Wait and retry
sleep 300
ansible-playbook ... -e mongodb_action=install
```

#### 5. IP Access List Configuration Failed

**Error:**
```
Failed to add IP address to access list
```

**Solution:**
```bash
# Verify IP format (CIDR notation required)
# Correct: 0.0.0.0/0, 10.0.0.0/8
# Incorrect: 0.0.0.0, 10.0.0.*

# Add IPs manually via Atlas UI or API
curl -X POST -u "PUBLIC_KEY:PRIVATE_KEY" \
  -H "Content-Type: application/json" \
  "https://cloud.mongodb.com/api/atlas/v1.0/groups/YOUR_PROJECT_ID/accessList" \
  -d '[{"ipAddress": "0.0.0.0/0", "comment": "Allow all"}]'
```

#### 6. Database User Creation Failed

**Error:**
```
User 'mas-admin' already exists
```

**Solution:**
```bash
# This is usually not an error - user exists and will be reused
# To update password:
curl -X PATCH -u "PUBLIC_KEY:PRIVATE_KEY" \
  -H "Content-Type: application/json" \
  "https://cloud.mongodb.com/api/atlas/v1.0/groups/YOUR_PROJECT_ID/databaseUsers/admin/mas-admin" \
  -d '{"password": "NewPassword123!"}'
```

#### 7. Connection Test Failed

**Error:**
```
ServerSelectionTimeoutError: No servers found
```

**Solution:**
```bash
# 1. Verify cluster is IDLE
curl -u "PUBLIC_KEY:PRIVATE_KEY" \
  "https://cloud.mongodb.com/api/atlas/v1.0/groups/YOUR_PROJECT_ID/clusters/mas-cluster" \
  | jq '.stateName'

# 2. Check IP whitelist
curl -u "PUBLIC_KEY:PRIVATE_KEY" \
  "https://cloud.mongodb.com/api/atlas/v1.0/groups/YOUR_PROJECT_ID/accessList" \
  | jq '.results'

# 3. Verify connection string
curl -u "PUBLIC_KEY:PRIVATE_KEY" \
  "https://cloud.mongodb.com/api/atlas/v1.0/groups/YOUR_PROJECT_ID/clusters/mas-cluster/connectStrings" \
  | jq '.standardSrv'

# 4. Test with correct credentials
mongosh "mongodb+srv://mas-admin:CORRECT_PASSWORD@cluster.mongodb.net/admin"
```

---

## Performance Benchmarks

### Typical Provisioning Times

| Cluster Size | Provisioning Time | Cost (Approx) |
|--------------|-------------------|---------------|
| M10          | 7-10 minutes      | $0.08/hour    |
| M20          | 8-12 minutes      | $0.20/hour    |
| M30          | 10-15 minutes     | $0.54/hour    |
| M40          | 12-18 minutes     | $1.04/hour    |

### Playbook Execution Times

| Action    | With AWS Secrets | Without Secrets | Notes |
|-----------|------------------|-----------------|-------|
| Provision | 10-15 min        | 10-15 min       | Most time is cluster creation |
| Install   | 30-45 sec        | 25-35 sec       | +5-10 sec for secret retrieval |

---

## Best Practices

### 1. Security

```bash
# Use AWS Secrets Manager for credentials
atlas_aws_secret_name="mongodb-atlas-api-credentials"

# Restrict IP access
atlas_ip_access_list="10.0.0.0/8,172.16.0.0/12"

# Enable backup for production
atlas_backup_enabled=true

# Use strong passwords
export ATLAS_DB_PASSWORD=$(openssl rand -base64 32)
```

### 2. Cost Optimization

```bash
# Use appropriate cluster size
# Dev: M10, Staging: M20, Prod: M30+

# Enable auto-scaling
# (Configured in cluster settings)

# Use shared clusters for dev/test
atlas_cluster_size="M2"  # Shared tier
```

### 3. High Availability

```bash
# Use multi-region clusters for production
atlas_cluster_provider="AWS"
atlas_cluster_region="US_EAST_1"

# Enable backup
atlas_backup_enabled=true

# Use private endpoints
atlas_private_endpoint_enabled=true
```

### 4. Monitoring

```bash
# Enable Atlas monitoring
# Check cluster metrics via Atlas UI or API

# Monitor provisioning progress
watch -n 30 'curl -s -u "PUBLIC_KEY:PRIVATE_KEY" \
  "https://cloud.mongodb.com/api/atlas/v1.0/groups/PROJECT_ID/clusters/CLUSTER_NAME" \
  | jq ".stateName"'
```

---

## Additional Resources

- [MongoDB Atlas API Documentation](https://docs.atlas.mongodb.com/api/)
- [AWS Secrets Manager Documentation](https://docs.aws.amazon.com/secretsmanager/)
- [MAS DevOps Collection](https://github.com/ibm-mas/ansible-devops)
- [MongoDB Atlas Best Practices](https://docs.atlas.mongodb.com/best-practices/)

---

**Created by Bob** - MongoDB Atlas Provisioning Test Guide