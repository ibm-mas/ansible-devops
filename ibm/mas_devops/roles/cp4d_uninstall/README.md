# cp4d_uninstall

Uninstall IBM Cloud Pak for Data and all its services from an OpenShift cluster. This role provides a clean removal process for CP4D, removing all services, platform components, prerequisites, and optionally namespaces and persistent data.

The role supports uninstallation of all CP4D components including Watson Studio, Watson Machine Learning, Analytics Engine (Spark), and the CP4D platform itself.

!!! warning "Destructive Operation"
    This role performs destructive operations that cannot be undone. Always backup critical data before running this role. By default, PVCs are preserved, but this can be changed with the `cpd_uninstall_delete_pvcs` variable.

## Uninstall Process

The role follows a specific order to ensure clean uninstallation:

1. **Services** - Watson Studio, Watson Machine Learning, Spark, CCS, DataRefinery
2. **Platform** - ZenService and Ibmcpd custom resources
3. **Prerequisites** - CPFS, NamespaceScope, IBM Licensing
4. **ODLM Cleanup** - OperandRequest, OperandConfig, and OperandRegistry resources in both instance and operators namespaces
5. **Subscriptions** - All remaining operator subscriptions
6. **CSVs** - All ClusterServiceVersions
7. **Catalog Sources** - CP4D-specific catalog sources and ConfigMaps
8. **PVCs** - Persistent Volume Claims (optional, disabled by default)
9. **Namespaces** - All CP4D-related namespaces (optional, disabled by default)

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`cpd_operators_namespace`](#cpd_operators_namespace) | No | `ibm-cpd-operators` |
| [`cpd_instance_namespace`](#cpd_instance_namespace) | No | `ibm-cpd` |
| [`cpd_cs_control_namespace`](#cpd_cs_control_namespace) | No | `cs-control` |
| [`cpd_cpfs_namespace`](#cpd_cpfs_namespace) | No | `ibm-common-services` |
| [`cpd_ibm_licensing_namespace`](#cpd_ibm_licensing_namespace) | No | `ibm-licensing` |
| [`cpd_platform_cr_name`](#cpd_platform_cr_name) | No | `ibmcpd-cr` |
| [`zen_cr_name`](#zen_cr_name) | No | `lite-cr` |
| [`cpd_uninstall_delete_pvcs`](#cpd_uninstall_delete_pvcs) | No | `false` |
| [`cpd_uninstall_delete_namespaces`](#cpd_uninstall_delete_namespaces) | No | `false` |
| [`cpd_uninstall_delete_catalog_sources`](#cpd_uninstall_delete_catalog_sources) | No | `true` |
| [`cpd_uninstall_delete_helm_cluster_resources`](#cpd_uninstall_delete_helm_cluster_resources) | No | `true` |
| [`cpd_uninstall_wait_timeout`](#cpd_uninstall_wait_timeout) | No | `1200` |

### Namespaces

#### cpd_operators_namespace

Namespace where the CP4D operators are installed — a valid Kubernetes namespace name that must match the namespace used during CP4D installation.

- **Optional**
- Environment Variable: `CPD_OPERATORS_NAMESPACE`
- Default: `ibm-cpd-operators`

The role removes operator subscriptions and related resources from this namespace.

#### cpd_instance_namespace

Namespace where the CP4D instance workloads are deployed — a valid Kubernetes namespace name that must match the namespace used during CP4D installation.

- **Optional**
- Environment Variable: `CPD_INSTANCE_NAMESPACE`
- Default: `ibm-cpd`

The role removes all CP4D custom resources and workloads from this namespace.

#### cpd_cs_control_namespace

Namespace for the Common Services control plane — a valid Kubernetes namespace name that must match the namespace used during CP4D installation.

- **Optional**
- Environment Variable: `CPD_CS_CONTROL_NAMESPACE`
- Default: `cs-control`

The role removes Common Services CSVs and subscriptions from this namespace.

#### cpd_cpfs_namespace

Namespace for Cloud Pak Foundational Services — a valid Kubernetes namespace name that must match the namespace used during CP4D installation.

- **Optional**
- Environment Variable: `CPD_CPFS_NAMESPACE`
- Default: `ibm-common-services`

The role removes CPFS resources (and PVCs, when `cpd_uninstall_delete_pvcs` is enabled) from this namespace.

#### cpd_ibm_licensing_namespace

Namespace for IBM Licensing — a valid Kubernetes namespace name that must match the namespace used during CP4D installation.

- **Optional**
- Environment Variable: `CPD_IBM_LICENSING_NAMESPACE`
- Default: `ibm-licensing`

The role removes IBM Licensing resources from this namespace.

### Platform Custom Resources

#### cpd_platform_cr_name

Name of the Ibmcpd custom resource representing the CP4D platform installation — a valid Kubernetes resource name that must match the CR name used during installation.

- **Optional**
- Environment Variable: `CPD_PLATFORM_CR_NAME`
- Default: `ibmcpd-cr`

The role deletes the Ibmcpd custom resource with this name during platform uninstallation.

#### zen_cr_name

Name of the ZenService custom resource that manages the CP4D control plane — a valid Kubernetes resource name that must match the CR name used during installation.

- **Optional**
- Environment Variable: `ZEN_CR_NAME`
- Default: `lite-cr`

The role deletes the ZenService custom resource with this name during platform uninstallation.

### Uninstall Options

#### cpd_uninstall_delete_pvcs

Delete PersistentVolumeClaims during uninstall — `true` or `false`.

- **Optional**
- Environment Variable: `CPD_UNINSTALL_DELETE_PVCS`
- Default: `false`

When `false` (default), PVCs are preserved so data remains available for potential reinstallation.

!!! warning
    Setting this to `true` permanently deletes all CP4D data — PVCs in both `cpd_instance_namespace` and `cpd_cpfs_namespace` are removed and the data cannot be recovered. Always backup critical data before enabling this option.

#### cpd_uninstall_delete_namespaces

Delete the CP4D-related namespaces after all resources are uninstalled — `true` or `false`.

- **Optional**
- Environment Variable: `CPD_UNINSTALL_DELETE_NAMESPACES`
- Default: `false`

Set to `false` to preserve namespaces for troubleshooting or reinstallation (they may contain residual resources). Namespace deletion can take several minutes due to finalizers; the role includes appropriate wait conditions.

#### cpd_uninstall_delete_catalog_sources

Delete the CP4D-specific catalog sources (`cpd-platform`, `opencloud-operators`) — `true` or `false`.

- **Optional**
- Environment Variable: `CPD_UNINSTALL_DELETE_CATALOG_SOURCES`
- Default: `true`

Set to `false` if you plan to reinstall CP4D soon; catalog sources can be recreated during reinstallation if needed.

#### cpd_uninstall_delete_helm_cluster_resources

Delete the Helm cluster-scoped resources (CRDs, ClusterRole, ClusterRoleBinding) installed by the CPD 5.3.1 Helm cluster-scoped charts — `true` or `false`.

- **Optional**
- Environment Variable: `CPD_UNINSTALL_DELETE_HELM_CLUSTER_RESOURCES`
- Default: `true`

Safe to run on any CPD version — resources that do not exist are silently skipped. Set to `false` only if you want to preserve the CRDs for manual management.

#### cpd_uninstall_wait_timeout

Wait timeout for each resource deletion operation, in seconds — a positive integer.

- **Optional**
- Environment Variable: `CPD_UNINSTALL_WAIT_TIMEOUT`
- Default: `1200` (20 minutes)

Increase for large CP4D deployments or slow storage; longer timeouts allow more time for resource cleanup but increase total uninstall time. Individual retry loops may have different retry counts and delays beyond this timeout.

## Example Playbook

### Basic Uninstall (Preserve PVCs)

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    # Use default namespaces
    # PVCs will be preserved (default)
    # Namespaces will be preserved (default)
  roles:
    - ibm.mas_devops.cp4d_uninstall
```

### Complete Uninstall (Delete Everything)

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    cpd_uninstall_delete_pvcs: true  # WARNING: Deletes all data
    cpd_uninstall_delete_namespaces: true
    cpd_uninstall_delete_catalog_sources: true
  roles:
    - ibm.mas_devops.cp4d_uninstall
```

### Uninstall with Custom Namespaces

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    cpd_operators_namespace: my-cpd-operators
    cpd_instance_namespace: my-cpd
    cpd_uninstall_delete_namespaces: true
  roles:
    - ibm.mas_devops.cp4d_uninstall
```

### Uninstall but Preserve Namespaces

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    cpd_uninstall_delete_namespaces: false  # Keep namespaces
    cpd_uninstall_delete_pvcs: false        # Keep data
  roles:
    - ibm.mas_devops.cp4d_uninstall
```

## Run Role Playbook

```bash
# Basic uninstall (preserve PVCs and namespaces)
ansible-playbook ibm.mas_devops.run_role

# Complete uninstall (delete everything)
export CPD_UNINSTALL_DELETE_PVCS=true
export CPD_UNINSTALL_DELETE_NAMESPACES=true
export CPD_UNINSTALL_DELETE_CATALOG_SOURCES=true
ansible-playbook ibm.mas_devops.run_role

# Uninstall with custom namespaces
export CPD_OPERATORS_NAMESPACE=my-cpd-operators
export CPD_INSTANCE_NAMESPACE=my-cpd
ansible-playbook ibm.mas_devops.run_role
```

## Important Notes

### Data Preservation

- **By default, PVCs are NOT deleted** - Your data is preserved
- Set `cpd_uninstall_delete_pvcs: true` to permanently delete all data
- Always backup critical data before uninstalling

### Idempotency

- The role is idempotent and safe to run multiple times
- If CP4D is not installed, the role will exit gracefully
- Missing resources are handled without errors

### Uninstall Time

- Complete uninstall typically takes 20-40 minutes
- Namespace deletion can take additional time due to finalizers
- The role includes appropriate wait conditions and retries

### What Gets Removed

- All CP4D service custom resources (Watson Studio, WML, Spark)
- CP4D platform custom resources (ZenService, Ibmcpd)
- CPFS, NamespaceScope, and IBM Licensing
- All operator subscriptions and CSVs
- Custom catalog sources (if enabled)
- PVCs (if enabled)
- Namespaces (if enabled)

### What Does NOT Get Removed

- IBM Operator Catalog (shared resource)
- Certificate Manager (shared resource)
- External databases or storage
- Backup data stored outside the cluster

### Troubleshooting

If resources fail to delete due to finalizers:

1. Check for stuck pods: `oc get pods -A | grep -E 'cpd|zen|common-service'`
2. Check for stuck finalizers: `oc get <resource> -o yaml | grep finalizers`
3. Manually remove finalizers if needed (advanced users only)
4. Re-run the role - it's idempotent

## License

EPL-2.0
