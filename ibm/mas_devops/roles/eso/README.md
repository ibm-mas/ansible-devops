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

| Variable | Required | Default |
|----------|----------|---------|
| [`eso_action`](#eso_action) | No | `install` |
| [`eso_namespace`](#eso_namespace) | No | `external-secrets-system` |
| [`eso_release_name`](#eso_release_name) | No | `external-secrets` |
| [`eso_repo_url`](#eso_repo_url) | No | `https://charts.external-secrets.io` |
| [`eso_chart_version`](#eso_chart_version) | No | Latest |
| [`eso_values`](#eso_values) | No | `{}` |
| [`eso_cleanup_crds`](#eso_cleanup_crds) | No | `false` |
| [`eso_cleanup_namespace`](#eso_cleanup_namespace) | No | `false` |
| [`eso_provider`](#eso_provider) | No | `ibm` |
| [`eso_store_name`](#eso_store_name) | No | `ibm-secrets-manager` |
| [`ibm_sm_instance_url`](#ibm_sm_instance_url) | Conditional | None |
| [`ibm_sm_api_key`](#ibm_sm_api_key) | Conditional | Falls back to `IBMCLOUD_APIKEY` |
| [`ibm_sm_store_namespace`](#ibm_sm_store_namespace) | Conditional | None |

The IBM Secrets Manager variables are only required for the secret store actions: `ibm_sm_instance_url` and `ibm_sm_api_key` when creating a ClusterSecretStore or SecretStore, and `ibm_sm_store_namespace` when creating or deleting a namespace-scoped SecretStore.

### Operator Installation

#### eso_action

Action to perform — one of `install`, `uninstall`, `create-clustersecretstore`, `delete-clustersecretstore`, `create-secretstore`, or `delete-secretstore`.

- **Optional**
- Environment Variable: `ESO_ACTION`
- Default: `install`

Installation is idempotent and can be run multiple times safely; uninstallation behavior depends on the cleanup flags. The `create-*`/`delete-*` actions manage IBM Secrets Manager stores and require the IBM Secrets Manager configuration variables. A ClusterSecretStore is cluster-wide and can be used by ExternalSecrets in any namespace, whereas a SecretStore is namespace-scoped and can only be used by ExternalSecrets in the same namespace.

#### eso_namespace

Namespace for the External Secrets Operator installation — any valid Kubernetes namespace name (lowercase alphanumeric with hyphens).

- **Optional**
- Environment Variable: `ESO_NAMESPACE`
- Default: `external-secrets-system`

All operator resources (deployments, services, webhooks) are created in this namespace, which is created if it doesn't exist. The default follows the operator's standard convention — override only for specific namespace requirements or multiple operator instances. CRDs are cluster-scoped regardless of namespace.

#### eso_release_name

Helm release name for the External Secrets Operator — a valid Helm release name (alphanumeric with hyphens), unique within the namespace.

- **Optional**
- Environment Variable: `ESO_RELEASE_NAME`
- Default: `external-secrets`

Used for Helm operations (install, upgrade, uninstall) and appears in `helm list` and other Helm commands; use the default unless deploying multiple instances or following specific naming conventions.

#### eso_repo_url

Helm repository URL for External Secrets charts — any valid HTTPS URL to a Helm repository.

- **Optional**
- Environment Variable: `ESO_REPO_URL`
- Default: `https://charts.external-secrets.io`

The default points to the official External Secrets Helm repository; override for private mirrors, custom repositories, or air-gapped/restricted environments.

#### eso_chart_version

Specific version of the External Secrets Helm chart to install — a valid semantic version (e.g., `0.9.11`, `0.10.0`).

- **Optional**
- Environment Variable: `ESO_CHART_VERSION`
- Default: `""` (latest version)

Leave empty to install the latest available version (suitable for development/testing); pin a specific version for production deployments, version upgrades, or rollbacks. Check the [releases](https://github.com/external-secrets/external-secrets/releases) page for available versions — pinning versions is recommended in production.

#### eso_values

Custom Helm values to override the default chart configuration — a dictionary of valid Helm chart values.

- **Optional**
- Environment Variable: None (must be set in playbook)
- Default: `{}` (empty dictionary)

Use to override resource limits and requests, replica counts for high availability, security contexts, provider-specific configurations, and feature flags. Values are merged with the defaults in `templates/values.yml.j2`, overriding any conflicts — see [Helm chart values](https://github.com/external-secrets/external-secrets/tree/main/deploy/charts/external-secrets) for available options and the [Example Playbooks](#example-playbooks) below for usage.

### Uninstallation Cleanup

#### eso_cleanup_crds

Flag to control CRD deletion during uninstallation — `true` or `false`.

- **Optional**
- Environment Variable: `ESO_CLEANUP_CRDS`
- Default: `false`

With `false` (recommended unless performing complete removal), CRDs and custom resources remain after uninstall; with `true`, all CRDs and custom resources are deleted. CRDs are cluster-scoped and affect all namespaces.

!!! warning
    Setting this to `true` deletes **all** ExternalSecret and SecretStore resources in the cluster.

#### eso_cleanup_namespace

Flag to control namespace deletion during uninstallation — `true` or `false`.

- **Optional**
- Environment Variable: `ESO_CLEANUP_NAMESPACE`
- Default: `false`

With `false` (recommended unless performing complete removal), the namespace remains after uninstall; with `true`, the namespace is deleted, including any remaining resources. Namespace deletion will fail if resources still exist in it.

### Secret Store Management

#### eso_provider

Provider type for secret store creation — currently only `ibm` (IBM Secrets Manager) is supported.

- **Optional**
- Environment Variable: `ESO_PROVIDER`
- Default: `ibm`

Only used when `eso_action` is one of the secret store actions (not `install`/`uninstall`); it determines which provider-specific tasks are executed. Future versions may support additional providers (AWS, Azure, GCP, HashiCorp Vault, etc.).

#### eso_store_name

Name for the SecretStore or ClusterSecretStore resource — a valid Kubernetes resource name (lowercase alphanumeric with hyphens).

- **Optional**
- Environment Variable: `ESO_STORE_NAME`
- Default: `ibm-secrets-manager`

Only used with the secret store actions; the name must be unique within the cluster for a ClusterSecretStore (cluster-scoped) and is referenced by ExternalSecret resources. The associated credentials secret is named `{eso_store_name}-apikey`. Override the default if you need multiple store instances or have specific naming requirements.

#### ibm_sm_instance_url

IBM Secrets Manager instance URL — a valid HTTPS URL (e.g., `https://my-instance.secrets-manager.cloud.ibm.com`).

- **Required** when using the `create-clustersecretstore` or `create-secretstore` actions
- Environment Variable: `IBM_SM_INSTANCE_URL`
- Default: None

Determines which IBM Secrets Manager instance the External Secrets Operator will connect to; the instance must be accessible from your Kubernetes cluster.

#### ibm_sm_api_key

IBM Cloud API key for authenticating with IBM Secrets Manager — a valid key with IAM permissions to access the Secrets Manager instance.

- **Required** when using the `create-clustersecretstore` or `create-secretstore` actions
- Environment Variable: `IBM_SM_API_KEY` or `IBMCLOUD_APIKEY`
- Default: Falls back to `IBMCLOUD_APIKEY` if `IBM_SM_API_KEY` is not set

Used to authenticate the External Secrets Operator with IBM Secrets Manager; the API key is stored as a Kubernetes secret (named `{eso_store_name}-apikey`) in the operator namespace. The `IBMCLOUD_APIKEY` fallback follows the collection pattern for convenience.

#### ibm_sm_store_namespace

Namespace for the IBM Secrets Manager SecretStore (namespace-scoped) — any valid Kubernetes namespace name (lowercase alphanumeric with hyphens).

- **Required** when using the `create-secretstore` or `delete-secretstore` actions
- Environment Variable: `IBM_SM_STORE_NAMESPACE`
- Default: None

Determines which namespace the SecretStore and its credentials secret will be created in; the namespace is created if it doesn't exist during `create-secretstore`. A SecretStore can only be used by ExternalSecrets in the same namespace — for cluster-wide access, use `create-clustersecretstore` instead (which does not require this variable).

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
```

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

### ExternalSecret: Arbitrary Secret (IBM Secrets Manager)

Arbitrary secrets contain a single text value stored in the `payload` field.

```yaml
apiVersion: external-secrets.io/v1
kind: ExternalSecret
metadata:
  name: example-arbitrary-secret
  namespace: default
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: ibm-secrets-manager
    kind: ClusterSecretStore  # Use 'SecretStore' for namespace-specific store
  target:
    name: my-arbitrary-secret
    creationPolicy: Owner
  data:
    - secretKey: API_KEY  # Key name in the Kubernetes Secret
      remoteRef:
        # Use the secret ID (recommended) or secret name
        key: YOUR-SECRET-ID-OR-NAME
```

### ExternalSecret: Key-Value Secret (individual keys)

Key-value secrets contain multiple key-value pairs. Prefix the secret ID with `kv/` and use `property` to select individual keys.

```yaml
apiVersion: external-secrets.io/v1
kind: ExternalSecret
metadata:
  name: example-kv-secret
  namespace: default
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: ibm-secrets-manager
    kind: ClusterSecretStore  # Use 'SecretStore' for namespace-specific store
  target:
    name: my-kv-secret
    creationPolicy: Owner
  data:
    - secretKey: USERNAME
      remoteRef:
        key: "kv/YOUR-SECRET-ID"
        property: "username"
    - secretKey: PASSWORD
      remoteRef:
        key: "kv/YOUR-SECRET-ID"
        property: "password"
```

### ExternalSecret: Key-Value Secret (fetch all keys at once)

Use `dataFrom.extract` to pull every key from a key-value secret in one operation.

```yaml
apiVersion: external-secrets.io/v1
kind: ExternalSecret
metadata:
  name: example-kv-all-keys
  namespace: default
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: ibm-secrets-manager
    kind: ClusterSecretStore
  target:
    name: my-kv-secret-all
    creationPolicy: Owner
  dataFrom:
    - extract:
        key: "kv/YOUR-SECRET-ID"
```

> **Notes:**
> - Always prefix key-value secret IDs with `kv/` (e.g. `"kv/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"`)
> - Secret IDs (UUIDs) are more reliable than secret names
> - Use `data` + `property` to fetch specific keys; use `dataFrom.extract` to fetch all keys at once

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
