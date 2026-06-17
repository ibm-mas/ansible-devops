# cp4d_uninstall

Uninstall IBM Cloud Pak for Data and all its services from an OpenShift cluster. This role provides a clean removal process for CP4D, removing all services, platform components, prerequisites, and optionally namespaces and persistent data.

The role supports uninstallation of all CP4D components including Watson Studio, Watson Machine Learning, Analytics Engine (Spark), Cognos Analytics, and the CP4D platform itself.

!!! warning "Destructive Operation"
    This role performs destructive operations that cannot be undone. Always backup critical data before running this role. By default, PVCs are preserved, but this can be changed with the `cpd_uninstall_delete_pvcs` variable.

## Uninstall Process

The role follows a specific order to ensure clean uninstallation:

1. **Services** - Watson Studio, Watson Machine Learning, Spark, Cognos Analytics, CCS, DataRefinery
2. **Platform** - ZenService and Ibmcpd custom resources
3. **Prerequisites** - CPFS, NamespaceScope, IBM Licensing
4. **ODLM Cleanup** - OperandRequest, OperandConfig, and OperandRegistry resources in both instance and operators namespaces
5. **Subscriptions** - All remaining operator subscriptions
6. **CSVs** - All ClusterServiceVersions
7. **Catalog Sources** - CP4D-specific catalog sources and ConfigMaps
8. **PVCs** - Persistent Volume Claims (optional, disabled by default)
9. **Namespaces** - All CP4D-related namespaces (optional, enabled by default)

## Role Variables

### cpd_operators_namespace
Namespace where CP4D operators are installed.

- **Optional**
- Environment Variable: `CPD_OPERATORS_NAMESPACE`
- Default: `ibm-cpd-operators`

**Purpose**: Specifies the namespace containing CP4D operator subscriptions and deployments.

**When to use**: Use default unless you customized the operators namespace during CP4D installation.

**Valid values**: Valid Kubernetes namespace name

**Impact**: The role will remove operator subscriptions and related resources from this namespace.

**Related variables**: `cpd_instance_namespace`

**Note**: Must match the namespace used during CP4D installation.

### cpd_instance_namespace
Namespace where CP4D instance workloads are deployed.

- **Optional**
- Environment Variable: `CPD_INSTANCE_NAMESPACE`
- Default: `ibm-cpd`

**Purpose**: Specifies the namespace containing CP4D instance custom resources and workloads.

**When to use**: Use default unless you customized the instance namespace during CP4D installation.

**Valid values**: Valid Kubernetes namespace name

**Impact**: The role will remove all CP4D custom resources and workloads from this namespace.

**Related variables**: `cpd_operators_namespace`

**Note**: Must match the namespace used during CP4D installation.

### cpd_cs_control_namespace
Namespace for Common Services control plane.

- **Optional**
- Environment Variable: `CPD_CS_CONTROL_NAMESPACE`
- Default: `cs-control`

**Purpose**: Specifies the namespace for IBM Licensing operator.

**When to use**: Use default unless you customized this namespace during CP4D installation.

**Valid values**: Valid Kubernetes namespace name

**Impact**: The role will remove IBM Licensing resources from this namespace.

### cpd_cpfs_namespace
Namespace for Cloud Pak Foundational Services.

- **Optional**
- Environment Variable: `CPD_CPFS_NAMESPACE`
- Default: `ibm-common-services`

**Purpose**: Specifies the namespace for CPFS resources.

**When to use**: Use default unless you customized this namespace during CP4D installation.

**Valid values**: Valid Kubernetes namespace name

**Impact**: The role will remove CPFS resources from this namespace.

### cpd_ibm_licensing_namespace
Namespace for IBM Licensing.

- **Optional**
- Environment Variable: `CPD_IBM_LICENSING_NAMESPACE`
- Default: `ibm-licensing`

**Purpose**: Specifies the namespace for IBM Licensing resources.

**When to use**: Use default unless you customized this namespace during CP4D installation.

**Valid values**: Valid Kubernetes namespace name

**Impact**: The role will remove IBM Licensing resources from this namespace.

### cpd_platform_cr_name
Name of the CP4D platform custom resource.

- **Optional**
- Environment Variable: `CPD_PLATFORM_CR_NAME`
- Default: `ibmcpd-cr`

**Purpose**: Specifies the name of the Ibmcpd custom resource that represents the CP4D platform installation.

**When to use**: Use default unless you customized the platform CR name during CP4D installation.

**Valid values**: Valid Kubernetes resource name

**Impact**: The role will delete the Ibmcpd custom resource with this name during platform uninstallation.

**Related variables**: `zen_cr_name`, `cpd_instance_namespace`

**Note**: Must match the CR name used during CP4D installation.

### zen_cr_name
Name of the ZenService custom resource.

- **Optional**
- Environment Variable: `ZEN_CR_NAME`
- Default: `lite-cr`

**Purpose**: Specifies the name of the ZenService custom resource that manages the CP4D control plane.

**When to use**: Use default unless you customized the Zen CR name during CP4D installation.

**Valid values**: Valid Kubernetes resource name

**Impact**: The role will delete the ZenService custom resource with this name during platform uninstallation.

**Related variables**: `cpd_platform_cr_name`, `cpd_instance_namespace`

**Note**: Must match the CR name used during CP4D installation.

### cpd_uninstall_delete_pvcs
Delete PersistentVolumeClaims (WARNING: Permanently deletes all data).

- **Optional**
- Environment Variable: `CPD_UNINSTALL_DELETE_PVCS`
- Default: `false`

**Purpose**: Controls whether PVCs are deleted during uninstall. When enabled, all CP4D data is permanently deleted.

**When to use**:
- Set to `false` (default) to preserve data for potential reinstallation
- Set to `true` only when you want to completely remove all CP4D data

**Valid values**: `true`, `false`

**Impact**: 
- `false`: PVCs are preserved, data remains available for potential reinstallation
- `true`: All PVCs are permanently deleted, data cannot be recovered

**Related variables**: None

**Note**: 
- **WARNING**: Setting this to `true` will permanently delete all CP4D data
- Always backup critical data before enabling this option
- This operation cannot be undone
- PVCs in both `cpd_instance_namespace` and `cpd_cpfs_namespace` will be deleted

### cpd_uninstall_delete_namespaces
Delete CP4D namespaces after uninstall.

- **Optional**
- Environment Variable: `CPD_UNINSTALL_DELETE_NAMESPACES`
- Default: `true`

**Purpose**: Controls whether CP4D namespaces are deleted after uninstalling all resources.

**When to use**:
- Use default (`true`) for complete cleanup
- Set to `false` if you want to preserve namespaces for troubleshooting or reinstallation

**Valid values**: `true`, `false`

**Impact**: 
- `true`: All CP4D namespaces are deleted after resource cleanup
- `false`: Namespaces are preserved (may contain residual resources)

**Related variables**: `cpd_uninstall_delete_pvcs`

**Note**: Namespace deletion can take several minutes due to finalizers. The role includes appropriate wait conditions.

### cpd_uninstall_delete_catalog_sources
Delete CP4D-specific catalog sources.

- **Optional**
- Environment Variable: `CPD_UNINSTALL_DELETE_CATALOG_SOURCES`
- Default: `true`

**Purpose**: Controls whether CP4D-specific catalog sources are removed.

**When to use**:
- Use default (`true`) for complete cleanup
- Set to `false` if you plan to reinstall CP4D soon

**Valid values**: `true`, `false`

**Impact**: 
- `true`: CP4D catalog sources (`cpd-platform`, `opencloud-operators`) are deleted
- `false`: Catalog sources are preserved

**Related variables**: None

**Note**: Catalog sources can be recreated during reinstallation if needed.

### cpd_uninstall_wait_timeout
Wait timeout for resource deletion operations (seconds).

- **Optional**
- Environment Variable: `CPD_UNINSTALL_WAIT_TIMEOUT`
- Default: `600` (10 minutes)

**Purpose**: Specifies how long to wait for each resource deletion operation to complete.

**When to use**:
- Use default for most scenarios
- Increase if you have large CP4D deployments or slow storage

**Valid values**: Positive integer (seconds)

**Impact**: Longer timeouts allow more time for resource cleanup but increase total uninstall time.

**Related variables**: None

**Note**: Individual retry loops may have different retry counts and delays beyond this timeout.

## Example Playbook

### Basic Uninstall (Preserve PVCs)
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    # Use default namespaces
    # PVCs will be preserved (default)
    # Namespaces will be deleted (default)
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
# Basic uninstall (preserve PVCs, delete namespaces)
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
- All CP4D service custom resources (Watson Studio, WML, Spark, Cognos)
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