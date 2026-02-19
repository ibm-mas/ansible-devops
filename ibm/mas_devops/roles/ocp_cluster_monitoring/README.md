ocp_cluster_monitoring
===============================================================================

Configure OpenShift Container Platform cluster monitoring with persistent storage and user-defined project monitoring. This role enables comprehensive monitoring capabilities essential for MAS deployments, including metrics collection, alerting, and user workload monitoring.

Key capabilities:
- **User-defined project monitoring**: Enable monitoring for user applications and MAS workloads
- **Persistent storage**: Configure durable storage for Prometheus metrics and AlertManager data
- **Version-aware configuration**: Automatically applies appropriate templates for OpenShift 4.18+ or earlier versions

The role configures both the platform monitoring stack (for OpenShift infrastructure) and user workload monitoring (for MAS applications) in the `openshift-monitoring` namespace.


Role Variables
-------------------------------------------------------------------------------

### cluster_monitoring_action
Action to perform on the cluster monitoring stack.

- Optional
- Environment Variable: `CLUSTER_MONITORING_ACTION`
- Default: `install`

**Purpose**: Controls whether to install/configure or uninstall the cluster monitoring stack configuration.

**When to use**: Set to `install` for normal operations. Use `uninstall` to remove persistent storage configuration and revert to default ephemeral storage.

**Valid values**:
- `install` - Configure monitoring with persistent storage (default)
- `uninstall` - Remove persistent storage configuration

**Impact**:
- `install`: Applies monitoring configuration with persistent storage
- `uninstall`: Removes custom configuration, monitoring reverts to defaults with ephemeral storage (metrics will be lost on pod restart)

**Related variables**: All other variables only apply when action is `install`

**Notes**:
- Uninstall does not remove the monitoring stack itself, only the persistent storage configuration
- Metrics data will be lost when reverting to ephemeral storage
- Backup important metrics before uninstalling

### prometheus_retention_period
Retention period for platform Prometheus metrics.

- Optional
- Environment Variable: `PROMETHEUS_RETENTION_PERIOD`
- Default: `15d`

**Purpose**: Defines how long Prometheus retains metrics data before deletion. Longer retention enables historical analysis but requires more storage.

**When to use**: Adjust based on compliance requirements, troubleshooting needs, and storage capacity.

**Valid values**: Duration string with unit suffix (e.g., `7d`, `15d`, `30d`, `90d`). Common values:
- `7d` - Minimal retention for basic troubleshooting
- `15d` - Default, suitable for most deployments
- `30d` - Extended retention for detailed analysis
- `90d` - Long-term retention for compliance

**Impact**: Directly affects storage consumption. Longer retention requires proportionally more storage space.

**Related variables**: `prometheus_storage_size` (must be sized appropriately for retention period)

**Notes**:
- Only applies when both `prometheus_storage_class` and `prometheus_alertmgr_storage_class` are set
- Calculate storage needs: ~1-2GB per day for typical MAS deployment
- Consider backup strategy for long-term metric retention

### prometheus_storage_class
Storage class for platform Prometheus metrics persistent volume.

- **Required** if known storage classes are not available
- Environment Variable: `PROMETHEUS_STORAGE_CLASS`
- Default: Auto-detected (`ibmc-block-gold`, `ocs-storagecluster-ceph-rbd`, or `managed-premium`)

**Purpose**: Specifies the storage class for Prometheus metrics data. Must support ReadWriteOnce (RWO) access mode.

**When to use**: Required if the cluster doesn't have one of the auto-detected storage classes. Always specify explicitly for production deployments.

**Valid values**: Valid storage class name that supports RWO access mode. Common values by platform:
- **IBM Cloud**: `ibmc-block-gold`, `ibmc-block-silver`
- **OpenShift Container Storage**: `ocs-storagecluster-ceph-rbd`
- **Azure**: `managed-premium`, `managed-standard`
- **AWS**: `gp3`, `gp2`

**Impact**: Determines performance and availability characteristics of metrics storage. Block storage is recommended for performance.

**Related variables**: `prometheus_storage_size`, `prometheus_retention_period`

**Notes**:
- **Critical**: Must support RWO access mode
- Block storage preferred over file storage for performance
- Verify storage class exists: `oc get storageclass`
- Role auto-detects common storage classes if not specified

### prometheus_storage_size
Size of the persistent volume for platform Prometheus metrics.

- Optional
- Environment Variable: `PROMETHEUS_STORAGE_SIZE`
- Default: `20Gi`

**Purpose**: Defines the capacity of the persistent volume for storing Prometheus metrics data.

**When to use**: Adjust based on retention period, cluster size, and number of monitored workloads.

**Valid values**: Kubernetes resource quantity (e.g., `20Gi`, `50Gi`, `100Gi`, `200Gi`). Sizing guidelines:
- `20Gi` - Default, suitable for small clusters (< 50 nodes)
- `50Gi` - Medium clusters (50-100 nodes) or extended retention
- `100Gi` - Large clusters (100-200 nodes)
- `200Gi+` - Very large clusters or long retention periods

**Impact**: Insufficient storage will cause metrics collection to fail. Over-provisioning wastes resources and costs.

**Related variables**: `prometheus_retention_period`, `prometheus_storage_class`

**Notes**:
- Only applies when both `prometheus_storage_class` and `prometheus_alertmgr_storage_class` are set
- Calculate: ~1-2GB per day × retention days × number of nodes / 50
- Monitor usage: `oc get pvc -n openshift-monitoring`
- Can be expanded later if needed (depending on storage class)

### prometheus_alertmgr_storage_class
Storage class for AlertManager persistent volume.

- **Required** if known storage classes are not available
- Environment Variable: `PROMETHEUS_ALERTMGR_STORAGE_CLASS`
- Default: Auto-detected (`ibmc-file-gold-gid`, `ocs-storagecluster-cephfs`, `azurefiles-premium`)

**Purpose**: Specifies the storage class for AlertManager data. Must support ReadWriteMany (RWX) access mode for high availability.

**When to use**: Required if the cluster doesn't have one of the auto-detected storage classes. Always specify explicitly for production deployments.

**Valid values**: Valid storage class name that supports RWX access mode. Common values by platform:
- **IBM Cloud**: `ibmc-file-gold-gid`, `ibmc-file-silver-gid`
- **OpenShift Container Storage**: `ocs-storagecluster-cephfs`
- **Azure**: `azurefiles-premium`, `azurefiles-standard`
- **AWS**: `efs-sc` (requires EFS CSI driver)

**Impact**: Determines AlertManager high availability and performance. RWX is required for multi-replica AlertManager deployment.

**Related variables**: `prometheus_alertmgr_storage_size`

**Notes**:
- **Critical**: Must support RWX access mode for HA
- File storage required (block storage doesn't support RWX)
- Verify storage class exists and supports RWX: `oc get storageclass`
- Role auto-detects common storage classes if not specified

### prometheus_alertmgr_storage_size
Size of the persistent volume for AlertManager.

- Optional
- Environment Variable: `PROMETHEUS_ALERTMGR_STORAGE_SIZE`
- Default: `20Gi`

**Purpose**: Defines the capacity of the persistent volume for storing AlertManager configuration and notification state.

**When to use**: Default is usually sufficient. Increase if managing many alert rules or notification integrations.

**Valid values**: Kubernetes resource quantity (e.g., `20Gi`, `50Gi`). Sizing guidelines:
- `20Gi` - Default, sufficient for most deployments
- `50Gi` - Large number of alert rules or notification channels

**Impact**: AlertManager storage needs are typically minimal. Default size is adequate for most scenarios.

**Related variables**: `prometheus_alertmgr_storage_class`

**Notes**:
- Only applies when both `prometheus_storage_class` and `prometheus_alertmgr_storage_class` are set
- AlertManager uses much less storage than Prometheus
- Default 20Gi is generous for typical use cases

### prometheus_userworkload_retention_period
Retention period for user workload Prometheus metrics.

- Optional
- Environment Variable: `PROMETHEUS_USERWORKLOAD_RETENTION_PERIOD`
- Default: `15d`

**Purpose**: Defines how long the user workload Prometheus instance retains metrics from user applications and MAS workloads.

**When to use**: Adjust based on application monitoring requirements and storage capacity. May differ from platform metrics retention.

**Valid values**: Duration string with unit suffix (e.g., `7d`, `15d`, `30d`). Common values:
- `7d` - Minimal retention
- `15d` - Default, suitable for most MAS deployments
- `30d` - Extended retention for detailed application analysis

**Impact**: Affects storage consumption for user workload metrics. MAS applications generate significant metrics data.

**Related variables**: `prometheus_userworkload_storage_size`

**Notes**:
- Applies only to user workload monitoring, not platform monitoring
- MAS applications (especially Manage) generate substantial metrics
- Consider MAS-specific monitoring requirements when setting retention

### prometheus_userworkload_storage_class
Storage class for user workload Prometheus metrics persistent volume.

- Optional
- Environment Variable: `PROMETHEUS_USERWORKLOAD_STORAGE_CLASS`
- Default: Value of `prometheus_storage_class`

**Purpose**: Specifies the storage class for user workload Prometheus metrics. Must support ReadWriteOnce (RWO) access mode.

**When to use**: Typically inherits from `prometheus_storage_class`. Set explicitly if user workload metrics require different storage characteristics.

**Valid values**: Valid storage class name that supports RWO access mode. Usually same as `prometheus_storage_class`.

**Impact**: Determines performance and availability of user workload metrics storage.

**Related variables**: `prometheus_storage_class`, `prometheus_userworkload_storage_size`

**Notes**:
- Defaults to same storage class as platform Prometheus
- Must support RWO access mode
- Can use different storage class if user workloads have specific requirements

### prometheus_userworkload_storage_size
Size of the persistent volume for user workload Prometheus metrics.

- Optional
- Environment Variable: `PROMETHEUS_USERWORKLOAD_STORAGE_SIZE`
- Default: `20Gi`

**Purpose**: Defines the capacity of the persistent volume for storing user workload metrics from MAS applications.

**When to use**: Adjust based on number of MAS applications, retention period, and metrics volume.

**Valid values**: Kubernetes resource quantity (e.g., `20Gi`, `50Gi`, `100Gi`). Sizing guidelines:
- `20Gi` - Default, suitable for 1-2 MAS applications
- `50Gi` - Multiple MAS applications (3-5)
- `100Gi` - Full MAS suite with extended retention

**Impact**: MAS applications generate significant metrics. Insufficient storage will cause metrics collection failures.

**Related variables**: `prometheus_userworkload_retention_period`, `prometheus_userworkload_storage_class`

**Notes**:
- MAS Manage generates substantial metrics data
- Size based on: number of MAS apps × retention period × expected metrics volume
- Monitor usage: `oc get pvc -n openshift-user-workload-monitoring`
- Can be expanded later if needed


Example Playbook
-------------------------------------------------------------------------------

```yaml
- hosts: localhost
  vars:
    prometheus_storage_class: "ibmc-block-gold"
    prometheus_alertmgr_storage_class: "ibmc-file-gold-gid"
  roles:
    - ibm.mas_devops.ocp_cluster_monitoring
```


License
-------------------------------------------------------------------------------

EPL-2.0
