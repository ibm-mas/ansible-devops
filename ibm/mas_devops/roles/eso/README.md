# eso

Deploy External Secrets Operator for Kubernetes, enabling seamless integration with external secret management systems like AWS Secrets Manager, Azure Key Vault, Google Secret Manager, HashiCorp Vault, and many others.

External Secrets Operator is a Kubernetes operator that integrates external secret management systems. It reads information from external APIs and automatically injects the values into Kubernetes Secrets, keeping them synchronized with the external source.

## Features

- **Multi-Provider Support**: Integrates with 20+ secret management providers
- **Automatic Synchronization**: Keeps Kubernetes secrets in sync with external sources
- **Secure by Design**: Secrets are fetched at runtime, not stored in Git
- **Flexible Configuration**: Supports namespace-scoped and cluster-wide secret stores
- **Template Support**: Transform and combine secrets before injection
- **High Availability**: Configurable replica counts for production deployments

## Deployed Components

After installation, the following deployments will be available:

```bash
kubectl get deployments -n external-secrets-system
NAME                              READY   UP-TO-DATE   AVAILABLE   AGE
external-secrets                  1/1     1            1           5m
external-secrets-cert-controller  1/1     1            1           5m
external-secrets-webhook          1/1     1            1           5m
```

## Custom Resource Definitions

The operator creates the following CRDs:

```bash
kubectl get crd | grep external-secrets
clustersecretstores.external-secrets.io
externalsecrets.external-secrets.io
secretstores.external-secrets.io
clusterexternalsecrets.external-secrets.io
pushsecrets.external-secrets.io
```

## Additional Resources

- [External Secrets Documentation](https://external-secrets.io/)
- [Getting Started Guide](https://external-secrets.io/latest/introduction/getting-started/)
- [Provider Documentation](https://external-secrets.io/latest/provider/aws-secrets-manager/)
- [Helm Chart Values](https://github.com/external-secrets/external-secrets/tree/main/deploy/charts/external-secrets)

## Role Variables

### eso_action
Action to perform: install, uninstall, or manage SecretStore/ClusterSecretStore resources.

- **Optional**
- Environment Variable: `ESO_ACTION`
- Default: `install`

**Purpose**: Determines the operation to perform with the External Secrets Operator.

**When to use**:
- Use `install` for deploying the operator
- Use `uninstall` for removing the operator
- Use `create-clustersecretstore` for creating an IBM Secrets Manager ClusterSecretStore (cluster-wide)
- Use `delete-clustersecretstore` for removing an IBM Secrets Manager ClusterSecretStore
- Use `create-secretstore` for creating an IBM Secrets Manager SecretStore (namespace-scoped)
- Use `delete-secretstore` for removing an IBM Secrets Manager SecretStore

**Valid values**: `install`, `uninstall`, `create-clustersecretstore`, `delete-clustersecretstore`, `create-secretstore`, `delete-secretstore`

**Impact**: Controls the primary operation of the role.

**Related variables**: `eso_cleanup_crds`, `eso_cleanup_namespace`, `eso_store_name`, `ibm_sm_instance_url`, `ibm_sm_api_key`, `ibm_sm_store_namespace`

**Notes**:
- Installation is idempotent - can be run multiple times safely
- Uninstallation behavior depends on cleanup flags
- The `create-clustersecretstore` and `create-secretstore` actions require IBM Secrets Manager configuration variables
- ClusterSecretStore is cluster-wide and can be used by ExternalSecrets in any namespace
- SecretStore is namespace-scoped and can only be used by ExternalSecrets in the same namespace

### eso_namespace
Namespace for External Secrets Operator installation.

- **Optional**
- Environment Variable: `ESO_NAMESPACE`
- Default: `external-secrets-system`

**Purpose**: Specifies the Kubernetes namespace where External Secrets Operator components will be deployed.

**When to use**: Use default unless you have specific namespace requirements or multiple operator instances.

**Valid values**: Valid Kubernetes namespace name (lowercase alphanumeric with hyphens)

**Impact**: All operator resources (deployments, services, webhooks) will be created in this namespace.

**Related variables**: `eso_cleanup_namespace`

**Notes**:
- Default `external-secrets-system` follows the operator's standard convention
- Namespace will be created if it doesn't exist
- CRDs are cluster-scoped regardless of namespace

### eso_release_name
Helm release name for the External Secrets Operator.

- **Optional**
- Environment Variable: `ESO_RELEASE_NAME`
- Default: `external-secrets`

**Purpose**: Identifies the Helm release for management operations.

**When to use**: Use default unless deploying multiple instances or following specific naming conventions.

**Valid values**: Valid Helm release name (alphanumeric with hyphens)

**Impact**: Used for Helm operations (install, upgrade, uninstall).

**Related variables**: None

**Notes**:
- Must be unique within the namespace
- Used in `helm list` and other Helm commands

### eso_repo_url
Helm repository URL for External Secrets charts.

- **Optional**
- Environment Variable: `ESO_REPO_URL`
- Default: `https://charts.external-secrets.io`

**Purpose**: Specifies the Helm repository containing External Secrets charts.

**When to use**: Use default for official releases. Override for private mirrors or custom repositories.

**Valid values**: Valid HTTPS URL to a Helm repository

**Impact**: Determines where Helm charts are downloaded from.

**Related variables**: `eso_chart_version`

**Notes**:
- Default points to official External Secrets Helm repository
- Can be overridden for air-gapped or restricted environments

### eso_chart_version
Specific version of the External Secrets Helm chart to install.

- **Optional**
- Environment Variable: `ESO_CHART_VERSION`
- Default: `""` (latest version)

**Purpose**: Pins the operator to a specific version for consistency and stability.

**When to use**:
- Leave empty for latest version (development/testing)
- Specify version for production deployments
- Use for version upgrades or rollbacks

**Valid values**: Valid semantic version (e.g., `0.9.11`, `0.10.0`)

**Impact**: Determines which operator version is deployed.

**Related variables**: `eso_repo_url`

**Notes**:
- Empty value installs latest available version
- Check [releases](https://github.com/external-secrets/external-secrets/releases) for available versions
- Recommended to pin versions in production

### eso_cleanup_crds
Flag to control CRD deletion during uninstallation.

- **Optional**
- Environment Variable: `ESO_CLEANUP_CRDS`
- Default: `false`

**Purpose**: Determines whether Custom Resource Definitions are removed during uninstallation.

**When to use**:
- Set to `false` (default) to preserve CRDs and custom resources
- Set to `true` for complete cleanup (removes all ExternalSecrets, SecretStores, etc.)

**Valid values**: `true`, `false`

**Impact**: 
- `false`: CRDs and custom resources remain after uninstall
- `true`: All CRDs and custom resources are deleted

**Related variables**: `eso_action`, `eso_cleanup_namespace`

**Notes**:
- **WARNING**: Setting to `true` will delete all ExternalSecret and SecretStore resources
- Recommended to keep `false` unless performing complete removal
- CRDs are cluster-scoped and affect all namespaces

### eso_cleanup_namespace
Flag to control namespace deletion during uninstallation.

- **Optional**
- Environment Variable: `ESO_CLEANUP_NAMESPACE`
- Default: `false`

**Purpose**: Determines whether the operator namespace is removed during uninstallation.

**When to use**:
- Set to `false` (default) to preserve namespace
- Set to `true` for complete cleanup

**Valid values**: `true`, `false`

**Impact**:
- `false`: Namespace remains after uninstall
- `true`: Namespace is deleted (including any remaining resources)

**Related variables**: `eso_action`, `eso_namespace`

**Notes**:
- Namespace deletion will fail if resources still exist
- Recommended to keep `false` unless performing complete removal

### eso_values
Custom Helm values to override default configuration.

- **Optional**
- Environment Variable: None (must be set in playbook)
- Default: `{}` (empty dictionary)

**Purpose**: Allows customization of External Secrets Operator Helm chart values.

**When to use**: Override default values for:
- Resource limits and requests
- Replica counts for high availability
- Security contexts
- Provider-specific configurations
- Feature flags

**Valid values**: Dictionary of valid Helm chart values

**Impact**: Merged with default values, overriding any conflicts.

**Related variables**: None

**Notes**:
- See [Helm chart values](https://github.com/external-secrets/external-secrets/tree/main/deploy/charts/external-secrets) for available options
- Values are merged with defaults in `templates/values.yml.j2`
- Use for advanced configurations not covered by other variables

**Example**:
```yaml
eso_values:
  replicaCount: 3
  resources:
    limits:
      cpu: 200m
      memory: 256Mi
```

### eso_provider
Provider type for secret store creation.

- **Optional**
- Environment Variable: `ESO_PROVIDER`
- Default: `ibm`

**Purpose**: Specifies which secret management provider to use when creating a ClusterSecretStore.

**When to use**: Set when using the `create-clustersecretstore` action to specify the provider type.

**Valid values**: `ibm` (currently only IBM Secrets Manager is supported)

**Impact**: Determines which provider-specific tasks are executed during ClusterSecretStore creation.

**Related variables**: `eso_action`, `eso_store_name`

**Notes**:
- Only used when `eso_action` is set to `create-clustersecretstore`
- Future versions may support additional providers (AWS, Azure, GCP, HashiCorp Vault, etc.)

### eso_store_name
Name for the ClusterSecretStore resource.

- **Optional**
- Environment Variable: `ESO_STORE_NAME`
- Default: `ibm-secrets-manager`

**Purpose**: Specifies the name of the ClusterSecretStore resource when using the `create-clustersecretstore` action.

**When to use**: Override the default name if you need multiple ClusterSecretStore instances or have specific naming requirements.

**Valid values**: Valid Kubernetes resource name (lowercase alphanumeric with hyphens)

**Impact**: Determines the name of the ClusterSecretStore that ExternalSecret resources will reference.

**Related variables**: `eso_action`, `eso_provider`, `ibm_sm_instance_url`, `ibm_sm_api_key`

**Notes**:
- Only used when `eso_action` is set to `create-clustersecretstore`
- The name must be unique within the cluster (ClusterSecretStore is cluster-scoped)

### ibm_sm_instance_url
IBM Secrets Manager instance URL.

- **Required** (when using `create-clustersecretstore` action)
- Environment Variable: `IBM_SM_INSTANCE_URL`
- Default: None

**Purpose**: Specifies the URL of your IBM Secrets Manager instance for the ClusterSecretStore configuration.

**When to use**: Required when creating a ClusterSecretStore for IBM Secrets Manager integration.

**Valid values**: Valid HTTPS URL to an IBM Secrets Manager instance (e.g., `https://my-instance.secrets-manager.cloud.ibm.com`)

**Impact**: Determines which IBM Secrets Manager instance the External Secrets Operator will connect to.

**Related variables**: `eso_action`, `eso_store_name`, `ibm_sm_api_key`

**Notes**:
- Only used when `eso_action` is set to `create-clustersecretstore`
- Must be a valid IBM Secrets Manager instance URL
- The instance must be accessible from your Kubernetes cluster

### ibm_sm_api_key
IBM Cloud API key for authenticating with IBM Secrets Manager.

- **Required** (when using `create-clustersecretstore` action)
- Environment Variable: `IBM_SM_API_KEY` or `IBMCLOUD_APIKEY`
- Default: Falls back to `IBMCLOUD_APIKEY` if `IBM_SM_API_KEY` is not set

**Purpose**: Provides authentication credentials for accessing IBM Secrets Manager.

**When to use**: Required when creating a ClusterSecretStore for IBM Secrets Manager integration.

**Valid values**: Valid IBM Cloud API key with permissions to access the Secrets Manager instance

**Impact**: Used to authenticate the External Secrets Operator with IBM Secrets Manager.

**Related variables**: `eso_action`, `eso_store_name`, `ibm_sm_instance_url`

**Notes**:
- Only used when `eso_action` is set to `create-clustersecretstore`
- The API key is stored as a Kubernetes secret in the operator namespace
- Follows the collection pattern by falling back to `IBMCLOUD_APIKEY` for convenience
- Ensure the API key has appropriate IAM permissions for the Secrets Manager instance

### ibm_sm_store_namespace
Namespace for the IBM Secrets Manager SecretStore (namespace-scoped).

- **Required** (when using `create-secretstore` or `delete-secretstore` actions)
- Environment Variable: `IBM_SM_STORE_NAMESPACE`
- Default: None

**Purpose**: Specifies the namespace where a namespace-scoped SecretStore will be created or deleted.

**When to use**: Required when creating or deleting a namespace-scoped SecretStore for IBM Secrets Manager integration.

**Valid values**: Valid Kubernetes namespace name (lowercase alphanumeric with hyphens)

**Impact**: Determines which namespace the SecretStore and its credentials secret will be created in.

**Related variables**: `eso_action`, `eso_store_name`, `ibm_sm_instance_url`, `ibm_sm_api_key`

**Notes**:
- Only used when `eso_action` is set to `create-secretstore` or `delete-secretstore`
- SecretStore is namespace-scoped and can only be used by ExternalSecrets in the same namespace
- The namespace will be created if it doesn't exist during `create-secretstore`
- For cluster-wide access, use `create-clustersecretstore` instead (does not require this variable)

## Example Playbooks

### Basic Installation

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    eso_namespace: external-secrets-system
  roles:
    - ibm.mas_devops.eso
```

### Installation with Specific Version

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    eso_namespace: external-secrets-system
    eso_chart_version: "0.9.11"
  roles:
    - ibm.mas_devops.eso
```

### Installation with Custom Values

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    eso_namespace: external-secrets-system
    eso_values:
      replicaCount: 3
      resources:
        requests:
          cpu: 50m
          memory: 128Mi
        limits:
          cpu: 200m
          memory: 256Mi
      webhook:
        replicaCount: 2
  roles:
    - ibm.mas_devops.eso
```

### Uninstallation (Preserve Resources)

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    eso_action: uninstall
    eso_namespace: external-secrets-system
  roles:
    - ibm.mas_devops.eso
```

### Complete Uninstallation (Remove Everything)

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    eso_action: uninstall
    eso_namespace: external-secrets-system
    eso_cleanup_crds: true
    eso_cleanup_namespace: true
  roles:
    - ibm.mas_devops.eso
```

### Create IBM Secrets Manager ClusterSecretStore

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    eso_action: create-clustersecretstore
    eso_namespace: external-secrets-system
    eso_store_name: ibm-secrets-manager
    ibm_sm_instance_url: "https://my-instance.secrets-manager.cloud.ibm.com"
    ibm_sm_api_key: "{{ lookup('env', 'IBMCLOUD_APIKEY') }}"
  roles:
    - ibm.mas_devops.eso

### Delete IBM Secrets Manager ClusterSecretStore

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    eso_action: delete-clustersecretstore
    eso_namespace: external-secrets-system
    eso_store_name: ibm-secrets-manager
  roles:
    - ibm.mas_devops.eso
```

### Create IBM Secrets Manager SecretStore (Namespace-Scoped)

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    eso_action: create-secretstore
    eso_store_name: ibm-secrets-manager
    ibm_sm_store_namespace: mas-core
    ibm_sm_instance_url: "https://my-instance.secrets-manager.cloud.ibm.com"
    ibm_sm_api_key: "{{ lookup('env', 'IBMCLOUD_APIKEY') }}"
  roles:
    - ibm.mas_devops.eso
```

### Delete IBM Secrets Manager SecretStore

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    eso_action: delete-secretstore
    eso_store_name: ibm-secrets-manager
    ibm_sm_store_namespace: mas-core
  roles:
    - ibm.mas_devops.eso
```
```

## Prerequisites

- Kubernetes cluster (1.19+) or OpenShift (4.8+)
- Helm 3.x installed and configured
- `kubernetes.core` Ansible collection installed
- Cluster admin permissions for CRD installation
- Network access to Helm repository

## Important Notes

### Handling Existing CRDs

If External Secrets CRDs already exist in your cluster from a previous installation (manual or non-Helm), the role will automatically:

1. Detect existing CRDs without Helm ownership metadata
2. Display a warning message
3. Delete the existing CRDs
4. Reinstall them with proper Helm ownership

This process is **safe** and will not affect existing ExternalSecret, SecretStore, or ClusterSecretStore resources. The CRDs are recreated with the same schema, allowing existing custom resources to continue functioning.

**Note**: If you have active ExternalSecret resources, they will briefly stop syncing during CRD recreation (typically 10-30 seconds) but will automatically resume once the new CRDs are in place.

## Post-Installation

After installation, you can create SecretStores and ExternalSecrets to start managing secrets:

```yaml
# Example: AWS Secrets Manager SecretStore
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: aws-secrets-manager
  namespace: default
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-east-1
      auth:
        secretRef:
          accessKeyIDSecretRef:
            name: aws-credentials
            key: access-key-id
          secretAccessKeySecretRef:
            name: aws-credentials
            key: secret-access-key
```

```yaml
# Example: ExternalSecret
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: my-secret
  namespace: default
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore
  target:
    name: my-k8s-secret
    creationPolicy: Owner
  data:
    - secretKey: password
      remoteRef:
        key: my-secret-name
        property: password
```

## License
EPL-2.0