# ocp_upgrade

This role supports the upgrade of the Openshift Cluster version for master and worker nodes in IBM Cloud provider.

## Role Variables

### cluster_type
Cluster type for upgrade operation.

- **Required**
- Environment Variable: `CLUSTER_TYPE`
- Default: None

**Purpose**: Specifies the type of OpenShift cluster to upgrade. Currently only IBM Cloud ROKS clusters are supported by this role.

**When to use**:
- Always required for cluster upgrade operations
- Must be set to `roks` (only supported type)
- Role will fail if any other cluster type is specified

**Valid values**: `roks` (IBM Cloud Red Hat OpenShift Kubernetes Service)

**Impact**: Determines the upgrade method and CLI commands used. Only ROKS clusters can be upgraded with this role.

**Related variables**:
- `cluster_name`: Name of the ROKS cluster to upgrade
- `ocp_version_upgrade`: Target version for the upgrade

**Note**: **IMPORTANT** - Only IBM Cloud ROKS clusters are supported. The role will fail if `cluster_type` is not `roks`. For other cluster types, use provider-specific upgrade procedures.

### cluster_name
Name of the cluster to upgrade.

- **Required**
- Environment Variable: `CLUSTER_NAME`
- Default: None

**Purpose**: Identifies which IBM Cloud ROKS cluster to upgrade. Used to target the specific cluster for the upgrade operation.

**When to use**:
- Always required for cluster upgrade operations
- Must match the exact cluster name in IBM Cloud
- Used by IBM Cloud CLI to locate the cluster

**Valid values**: String matching an existing ROKS cluster name in your IBM Cloud account

**Impact**: Determines which cluster is upgraded. Incorrect name will cause the upgrade to fail.

**Related variables**:
- `cluster_type`: Must be `roks` for this role
- `ocp_version_upgrade`: Target version for this cluster

**Note**: The cluster name must exactly match the name in IBM Cloud. Verify the cluster name before running the upgrade to avoid targeting the wrong cluster.

### ocp_version_upgrade
Target OpenShift version for upgrade.

- **Required**
- Environment Variable: `OCP_VERSION_UPGRADE`
- Default: None

**Purpose**: Specifies the target OpenShift Container Platform version to upgrade the cluster to. Determines which version will be installed.

**When to use**:
- Always required for cluster upgrade operations
- Must be a valid version available for ROKS clusters
- Should be a supported upgrade path from current version

**Valid values**: ROKS version format with `_openshift` suffix (e.g., `4.10_openshift`, `4.11_openshift`, `4.12_openshift`)

**Impact**: Cluster is upgraded to this version. Upgrade may take significant time and cause temporary service disruption. Version must be a valid upgrade path from current version.

**Related variables**:
- `cluster_name`: Cluster to upgrade to this version
- `cluster_type`: Must be `roks`

**Note**: **IMPORTANT** - Version must include `_openshift` suffix for ROKS clusters (e.g., `4.10_openshift`). Verify the version is a supported upgrade path from your current version. Upgrades cannot be rolled back. Plan for maintenance window as upgrade causes temporary disruption. Check IBM Cloud documentation for available versions and supported upgrade paths.

## Example Playbook

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    cluster_name: my-ocp-cluster
    cluster_type: roks
    ocp_version_upgrade: 4.10_openshift
  roles:
    - ibm.mas_devops.ocp_upgrade
```

## License

EPL-2.0
