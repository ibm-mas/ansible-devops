# external_secrets

Install **External Secrets Operator (ESO)** and configure it to connect to **IBM Secrets Manager** instances for cluster-wide secret synchronization.

External Secrets Operator synchronizes secrets from external secret management systems (like IBM Secrets Manager, AWS Secrets Manager, HashiCorp Vault, etc.) into Kubernetes secrets. This role focuses on IBM Secrets Manager integration.

## Prerequisites

- OpenShift Container Platform cluster with cluster-admin access
- IBM Secrets Manager instance
- IAM API key with appropriate permissions to access IBM Secrets Manager
- External Secrets Operator available in the `community-operators` catalog

## Role Variables

### General Variables

#### eso_action
Specifies which operation to perform on External Secrets Operator.

- **Optional**
- Environment Variable: `ESO_ACTION`
- Default: `install`

**Purpose**: Controls what action the role executes. This allows the same role to handle installation, configuration, and removal of ESO and its stores.

**When to use**:
- Use `install` for initial ESO operator deployment
- Use `create-clustersecretstore` to create a cluster-wide store for IBM Secrets Manager
- Use `create-secretstore` to create a namespace-scoped store
- Use `delete-clustersecretstore` to remove a cluster-wide store
- Use `delete-secretstore` to remove a namespace-scoped store
- Use `uninstall` to remove ESO operator (use with caution)
- Use `none` to skip all actions

**Valid values**: `install`, `uninstall`, `create-clustersecretstore`, `create-secretstore`, `delete-clustersecretstore`, `delete-secretstore`, `none`

**Impact**:
- `install`: Deploys ESO operator to the cluster
- `uninstall`: Removes ESO operator (does not remove stores or secrets)
- `create-clustersecretstore`: Creates a ClusterSecretStore accessible from any namespace
- `create-secretstore`: Creates a SecretStore in a specific namespace
- `delete-clustersecretstore`: Removes ClusterSecretStore and its authentication secret
- `delete-secretstore`: Removes SecretStore and its authentication secret from target namespace
- `none`: Role takes no action

**Related variables**: Different actions require different variables (see action-specific sections below)

#### eso_namespace
OpenShift namespace where the ESO operator will be deployed.

- **Optional**
- Environment Variable: `ESO_NAMESPACE`
- Default: `external-secrets-system`

**Purpose**: Defines the Kubernetes namespace for ESO operator resources.

**When to use**: Use the default unless you have specific namespace requirements.

**Valid values**: Any valid Kubernetes namespace name

**Impact**: All ESO operator resources will be created in this namespace. For ClusterSecretStore, authentication secrets are also stored here.

#### eso_operator_name
Name of the ESO operator subscription.

- **Optional**
- Environment Variable: `ESO_OPERATOR_NAME`
- Default: `external-secrets-operator`

**Purpose**: Specifies the name for the operator subscription and related resources.

**When to use**: Use the default unless you need a custom name for organizational purposes.

**Valid values**: Any valid Kubernetes resource name

**Impact**: Used to name the Subscription and OperatorGroup resources.

### Installation Variables

#### eso_catalog_source
Specifies the OpenShift operator catalog source containing the ESO operator.

- **Optional**
- Environment Variable: `ESO_CATALOG_SOURCE`
- Default: `community-operators`

**Purpose**: Controls which operator catalog is used to locate and install the ESO operator.

**When to use**: Use default for standard installations. Change only if using a custom catalog or mirror registry.

**Valid values**: Any valid CatalogSource name in the `openshift-marketplace` namespace

**Impact**: Determines where OpenShift looks for the ESO operator images and metadata.

#### eso_channel
Specifies the ESO operator subscription channel.

- **Optional**
- Environment Variable: `ESO_CHANNEL`
- Default: `stable`

**Purpose**: Controls which version stream of ESO will be installed and receive updates.

**When to use**: Use default `stable` for production. Other channels may be available for testing.

**Valid values**: Check the operator catalog for available channels (typically `stable`)

**Impact**: Determines which ESO version is installed and which automatic updates are applied.

#### eso_install_plan_approval
Controls whether operator updates require manual approval.

- **Optional**
- Environment Variable: `ESO_INSTALL_PLAN_APPROVAL`
- Default: `Automatic`

**Purpose**: Determines if operator updates are applied automatically or require manual approval.

**When to use**: Use `Automatic` for development/test. Use `Manual` for production to control update timing.

**Valid values**: `Automatic`, `Manual`

**Impact**:
- `Automatic`: Operator updates are applied automatically when available
- `Manual`: Operator updates require manual approval via InstallPlan

#### eso_store_name
Name of the SecretStore or ClusterSecretStore resource.

- **Optional**
- Environment Variable: `ESO_STORE_NAME`
- Default: `ibm-secrets-manager`

**Purpose**: Specifies the name for the SecretStore or ClusterSecretStore resource that will be created.

**When to use**: Use the default for standard deployments. Customize if you need multiple stores or have naming conventions.

**Valid values**: Any valid Kubernetes resource name

**Impact**: This name is used when creating SecretStore/ClusterSecretStore resources and must be referenced in ExternalSecret resources.

**Related variables**: Used by `create-secretstore`, `create-clustersecretstore`, `delete-secretstore`, and `delete-clustersecretstore` actions.

### IBM Secrets Manager Configuration Variables

These variables are used when `eso_action` is `create-secretstore` or `create-clustersecretstore`.

#### ibm_sm_instance_url
IBM Secrets Manager instance URL.

- **Required** for `create-secretstore` and `create-clustersecretstore` actions
- Environment Variable: `IBM_SM_INSTANCE_URL`
- Default: None

**Purpose**: Specifies the endpoint URL for your IBM Secrets Manager instance.

**When to use**: Required when creating any SecretStore or ClusterSecretStore for IBM Secrets Manager.

**Valid values**: Full HTTPS URL to your IBM Secrets Manager instance (e.g., `https://{instance-id}.{region}.secrets-manager.appdomain.cloud`)

**Impact**: This URL is used by ESO to connect to IBM Secrets Manager and retrieve secrets.

**How to find**: In IBM Cloud console, navigate to your Secrets Manager instance and copy the endpoint URL.

#### ibm_sm_api_key
IAM API key for authenticating to IBM Secrets Manager.

- **Required** for `create-secretstore` and `create-clustersecretstore` actions
- Environment Variable: `IBM_SM_API_KEY`
- Default: Falls back to `IBMCLOUD_APIKEY` if not set

**Purpose**: Provides the IAM API key credential for authenticating with IBM Secrets Manager.

**When to use**:
- Set `IBM_SM_API_KEY` for a dedicated Secrets Manager API key
- Leave unset to use `IBMCLOUD_APIKEY` (convenient when using same credentials)

**Valid values**: Valid IBM Cloud IAM API key with permissions to access the Secrets Manager instance

**Impact**: This API key is stored in a Kubernetes secret and used by ESO to authenticate to IBM Secrets Manager.

**Security**: This is a sensitive credential. The role uses `no_log: true` to prevent logging. The API key is stored in a Kubernetes secret with appropriate RBAC.

**How to create**: In IBM Cloud console, go to Manage > Access (IAM) > API keys, and create a new API key with appropriate permissions.

#### ibm_sm_store_namespace
Target namespace for SecretStore creation.

- **Required** for `create-secretstore` and `delete-secretstore` actions only
- Environment Variable: `IBM_SM_STORE_NAMESPACE`
- Default: None

**Purpose**: Specifies which namespace to create or delete the SecretStore in.

**When to use**: Only needed for namespace-scoped SecretStore operations. Not used for ClusterSecretStore.

**Valid values**: Any existing Kubernetes namespace name

**Impact**: The SecretStore and its authentication secret will be created in this namespace.

## Internal Implementation Details

The following values are hardcoded internally and are not user-configurable. This simplifies usage and ensures consistency:

- **SecretStore/ClusterSecretStore name**: Always `ibm-secrets-manager`
- **Authentication secret name**: Always `ibm-sm-credentials`
- **Authentication secret namespace**:
  - For ClusterSecretStore: Always in ESO operator namespace (`external-secrets-system`)
  - For SecretStore: Always in the same namespace as the SecretStore

## Usage Examples

### Example 1: Install ESO Operator

```yaml
---
- hosts: localhost
  any_errors_fatal: true
  vars:
    eso_action: install
  roles:
    - ibm.mas_devops.external_secrets
```

### Example 2: Create ClusterSecretStore for IBM Secrets Manager

```yaml
---
- hosts: localhost
  any_errors_fatal: true
  vars:
    eso_action: create-clustersecretstore
    ibm_sm_instance_url: "https://my-instance.us-south.secrets-manager.appdomain.cloud"
    # ibm_sm_api_key will fall back to IBMCLOUD_APIKEY if not set
  roles:
    - ibm.mas_devops.external_secrets
```

### Example 3: Create Namespace-Scoped SecretStore

```yaml
---
- hosts: localhost
  any_errors_fatal: true
  vars:
    eso_action: create-secretstore
    ibm_sm_instance_url: "https://my-instance.us-south.secrets-manager.appdomain.cloud"
    ibm_sm_store_namespace: my-app-namespace
  roles:
    - ibm.mas_devops.external_secrets
```

### Example 4: Complete Setup (Install + Configure)

```yaml
---
- hosts: localhost
  any_errors_fatal: true
  tasks:
    # Step 1: Install ESO operator
    - name: Install External Secrets Operator
      include_role:
        name: ibm.mas_devops.external_secrets
      vars:
        eso_action: install

    # Step 2: Create ClusterSecretStore
    - name: Create ClusterSecretStore for IBM Secrets Manager
      include_role:
        name: ibm.mas_devops.external_secrets
      vars:
        eso_action: create-clustersecretstore
        ibm_sm_instance_url: "{{ lookup('env', 'IBM_SM_INSTANCE_URL') }}"
```

### Example 5: Delete ClusterSecretStore

```yaml
---
- hosts: localhost
  any_errors_fatal: true
  vars:
    eso_action: delete-clustersecretstore
  roles:
    - ibm.mas_devops.external_secrets
```

### Example 6: Delete SecretStore

```yaml
---
- hosts: localhost
  any_errors_fatal: true
  vars:
    eso_action: delete-secretstore
    ibm_sm_store_namespace: my-app-namespace
  roles:
    - ibm.mas_devops.external_secrets
```

### Example 7: Uninstall ESO Operator

```yaml
---
- hosts: localhost
  any_errors_fatal: true
  vars:
    eso_action: uninstall
  roles:
    - ibm.mas_devops.external_secrets
```

## Creating ExternalSecrets

After creating a SecretStore or ClusterSecretStore, you can create ExternalSecret resources to sync secrets from IBM Secrets Manager into Kubernetes secrets.

### ExternalSecret Creation Policies

The `creationPolicy` field controls how ESO manages the target Kubernetes secret:

- **`Owner`** (recommended, default): ESO creates and owns the secret. If the ExternalSecret is deleted, the secret is also deleted.
- **`Orphan`**: ESO creates the secret but doesn't set an owner reference. If the ExternalSecret is deleted, the secret remains.
- **`Merge`**: ESO merges data into an existing secret without overwriting other keys. Creates the secret if it doesn't exist.
- **`None`**: ESO updates an existing secret but will NOT create it if it doesn't exist. Fails if secret is missing.

### Example: Arbitrary Secret (Key-Value Pairs)

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: my-app-secret
  namespace: my-namespace
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: ibm-secrets-manager
    kind: ClusterSecretStore
  target:
    name: my-kubernetes-secret
    creationPolicy: Owner
  data:
    - secretKey: username
      remoteRef:
        key: my-secret-id  # IBM Secrets Manager secret ID
        property: username
    - secretKey: password
      remoteRef:
        key: my-secret-id
        property: password
```

### Example: Username/Password Credentials

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: database-credentials
  namespace: my-namespace
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: ibm-secrets-manager
    kind: ClusterSecretStore
  target:
    name: db-credentials
    creationPolicy: Owner
  dataFrom:
    - extract:
        key: my-credentials-secret-id  # IBM Secrets Manager secret ID
```

### Example: TLS Certificate

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: tls-certificate
  namespace: my-namespace
spec:
  refreshInterval: 24h
  secretStoreRef:
    name: ibm-secrets-manager
    kind: ClusterSecretStore
  target:
    name: my-tls-cert
    creationPolicy: Owner
    template:
      type: kubernetes.io/tls
  data:
    - secretKey: tls.crt
      remoteRef:
        key: my-certificate-secret-id
        property: certificate
    - secretKey: tls.key
      remoteRef:
        key: my-certificate-secret-id
        property: private_key
```

## IBM Secrets Manager Setup

### Quick Start: Recommended Setup for Production

For production deployments, follow these steps to create a Service ID with minimal permissions:

1. **Create IBM Secrets Manager instance** (if you don't have one)
2. **Create a Service ID** with a descriptive name like `external-secrets-operator-<cluster-name>`
3. **Create an API key** for the Service ID
4. **Assign SecretsReader role** to the Service ID for your Secrets Manager instance
5. **Use the Service ID's API key** with this role (set `IBM_SM_API_KEY` environment variable)

This approach follows the principle of least privilege and provides better security than using personal API keys.

### Creating an IBM Secrets Manager Instance

1. Log in to IBM Cloud console
2. Navigate to Catalog > Security > Secrets Manager
3. Create a new instance in your desired region
4. Note the instance endpoint URL (needed for `ibm_sm_instance_url`)

### Creating a Service ID with Limited Permissions (Recommended)

For production deployments, it's recommended to create a dedicated Service ID with minimal permissions rather than using a personal API key. This follows the principle of least privilege.

#### Step 1: Create a Service ID

**Using IBM Cloud Console:**

1. In IBM Cloud console, go to **Manage > Access (IAM) > Service IDs**
2. Click **Create**
3. Provide a name: `external-secrets-operator-<cluster-name>`
   - Example: `external-secrets-operator-prod-us-south`
4. Provide a description: `Service ID for External Secrets Operator to read secrets from IBM Secrets Manager in <cluster-name> cluster`
5. Click **Create**

**Using IBM Cloud CLI:**

```bash
# Login to IBM Cloud
ibmcloud login

# Create Service ID
# Syntax: ibmcloud iam service-id-create <SERVICE_ID_NAME>
ibmcloud iam service-id-create external-secrets-operator-prod \
  --description "Service ID for External Secrets Operator to read secrets from IBM Secrets Manager"

# Note the Service ID from the output (e.g., ServiceId-12345678-1234-1234-1234-123456789abc)
# You'll use the SERVICE_ID_NAME (external-secrets-operator-prod) in subsequent commands
```

#### Step 2: Create an API Key for the Service ID

**Using IBM Cloud Console:**

1. In the Service ID details page, go to the **API keys** tab
2. Click **Create**
3. Provide a name: `eso-api-key`
4. Provide a description: `API key for ESO to authenticate to IBM Secrets Manager`
5. Click **Create**
6. **Important**: Copy and securely store the API key immediately (you won't be able to see it again)
7. This API key will be used for `ibm_sm_api_key` or `IBM_SM_API_KEY`

**Using IBM Cloud CLI:**

```bash
# Create API key for the Service ID
# Syntax: ibmcloud iam service-api-key-create <API_KEY_NAME> <SERVICE_ID_NAME>
ibmcloud iam service-api-key-create eso-api-key external-secrets-operator-prod \
  --description "API key for ESO to authenticate to IBM Secrets Manager"

# Where:
#   eso-api-key = Name of the API key being created
#   external-secrets-operator-prod = Name of the Service ID (created in Step 1)

# The API key will be displayed once - save it immediately!
# Example output:
# API Key eso-api-key was created
# API Key: abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGH
```

#### Step 3: Assign Access Policy to Service ID

**Using IBM Cloud Console:**

1. In the Service ID details page, go to the **Access** tab
2. Click **Assign access**
3. Select **IAM services**
4. For **Service**, select **Secrets Manager**
5. For **Resources**, select:
   - **Specific resources** > **Service instance** > Select your Secrets Manager instance
6. For **Service access**, select:
   - **SecretsReader** role (minimum - for read-only access)
   - Or **Manager** role (if ESO needs to create/update secrets)
7. Click **Add** then **Assign**

**Using IBM Cloud CLI:**

```bash
# Get your Secrets Manager instance GUID
ibmcloud resource service-instance <your-secrets-manager-name> --output json | grep guid

# Assign SecretsReader role to the Service ID
# Syntax: ibmcloud iam service-policy-create <SERVICE_ID_NAME> --roles <ROLE> --service-name <SERVICE> --service-instance <GUID>
ibmcloud iam service-policy-create external-secrets-operator-prod \
  --roles SecretsReader \
  --service-name secrets-manager \
  --service-instance <secrets-manager-instance-guid>

# Where:
#   external-secrets-operator-prod = Name of the Service ID (from Step 1)
#   SecretsReader = IAM role (read-only access)
#   <secrets-manager-instance-guid> = GUID from the previous command

# Verify the policy was created
ibmcloud iam service-policies external-secrets-operator-prod
```

#### Step 4: Use the API Key with External Secrets Operator

Now you can use the Service ID's API key with the External Secrets Operator role:

```bash
# Set the API key as an environment variable
export IBM_SM_API_KEY="<api-key-from-step-2>"

# Or if you prefer to use IBMCLOUD_APIKEY (the role will use it as fallback)
export IBMCLOUD_APIKEY="<api-key-from-step-2>"

# Set your Secrets Manager instance URL
export IBM_SM_INSTANCE_URL="https://<instance-id>.<region>.secrets-manager.appdomain.cloud"

# Run the playbook to create ClusterSecretStore
ansible-playbook ibm.mas_devops.external_secrets -e eso_action=create-clustersecretstore
```

#### Step 5: (Optional) Restrict to Specific Secret Groups

For even tighter security, you can restrict the Service ID to only access specific secret groups:

**Using IBM Cloud Console:**

1. When assigning access in Step 3, under **Resources**, select:
   - **Specific resources** > **Service instance** > Select your Secrets Manager instance
   - **Resource type** > **secret-group**
   - **Resource ID** > Enter the secret group ID
2. This limits the Service ID to only secrets in that group

### Alternative: Using a Personal API Key (Not Recommended for Production)

If you need to use a personal API key (e.g., for development/testing):

1. In IBM Cloud console, go to **Manage > Access (IAM) > API keys**
2. Click **Create an IBM Cloud API key**
3. Give it a descriptive name (e.g., "external-secrets-operator-dev")
4. Copy and securely store the API key (needed for `ibm_sm_api_key`)

**Note**: Personal API keys inherit all your permissions, which violates the principle of least privilege. Use Service IDs for production.

### Required IAM Permissions Summary

The Service ID or API key needs one of the following roles on the Secrets Manager instance:

- **SecretsReader** role (minimum, recommended) - Read-only access to secrets
- **Manager** role - Full access including create/update/delete (only if needed)

**Best Practice**: Use **SecretsReader** role unless you specifically need ESO to create or modify secrets.

### Creating Secrets in IBM Secrets Manager

1. Navigate to your Secrets Manager instance in IBM Cloud
2. Click "Add" to create a new secret
3. Choose secret type:
   - **Arbitrary** - for key-value pairs
   - **Username/Password** - for credentials
   - **Certificate** - for TLS certificates
   - **IAM credentials** - for service IDs
4. Note the secret ID (needed in ExternalSecret `remoteRef.key`)

## Architecture

### ClusterSecretStore vs SecretStore

- **ClusterSecretStore**: Cluster-scoped resource that can be referenced by ExternalSecrets in any namespace. Recommended for shared secret backends.
- **SecretStore**: Namespace-scoped resource that can only be referenced by ExternalSecrets in the same namespace. Use for namespace-specific backends or credentials.

### Best Practices

1. **Use ClusterSecretStore for shared backends**: When multiple namespaces need access to the same IBM Secrets Manager instance, use ClusterSecretStore to avoid duplicating credentials.

2. **Use SecretStore for sensitive environments**: When you need strict namespace isolation or different credentials per namespace, use SecretStore.

3. **Organize secrets in IBM Secrets Manager**: Use consistent naming conventions and secret groups to organize secrets logically.

4. **Set appropriate refresh intervals**: Balance between secret freshness and API call frequency. Use longer intervals (e.g., 24h) for rarely-changing secrets like certificates.

5. **Monitor ExternalSecret sync status**: Check the status of ExternalSecret resources to ensure secrets are syncing correctly.

6. **Rotate API keys regularly**: Implement a process to rotate the IBM Cloud API key used by ESO.

## Troubleshooting

### ClusterSecretStore/SecretStore Not Ready

Check the status of the store:

```bash
oc get clustersecretstore ibm-secrets-manager -o yaml
# or
oc get secretstore ibm-secrets-manager -n <namespace> -o yaml
```

Common issues:
- Invalid IBM Secrets Manager URL
- Invalid or expired API key
- Network connectivity issues
- Insufficient IAM permissions

### ExternalSecret Not Syncing

Check the ExternalSecret status:

```bash
oc get externalsecret <name> -n <namespace> -o yaml
```

Common issues:
- Invalid secret ID in `remoteRef.key`
- Secret doesn't exist in IBM Secrets Manager
- Incorrect property name in `remoteRef.property`
- SecretStore/ClusterSecretStore not ready

### Viewing ESO Operator Logs

```bash
oc logs -n external-secrets-system deployment/external-secrets
```

## License

EPL-2.0