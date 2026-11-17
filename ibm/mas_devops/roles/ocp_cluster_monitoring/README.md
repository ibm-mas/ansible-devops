# ocp_cluster_monitoring

Configure OpenShift Container Platform cluster monitoring with persistent storage and user-defined project monitoring. This role enables comprehensive monitoring capabilities essential for MAS deployments, including metrics collection, alerting, and user workload monitoring.

Key capabilities:

- **User-defined project monitoring**: Enable monitoring for user applications and MAS workloads
- **Persistent storage**: Configure durable storage for Prometheus metrics and AlertManager data
- **Version-aware configuration**: Automatically applies appropriate templates for OpenShift 4.18+ or earlier versions

The role configures both the platform monitoring stack (for OpenShift infrastructure) and user workload monitoring (for MAS applications) in the `openshift-monitoring` namespace.

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`cluster_monitoring_action`](#cluster_monitoring_action) | No | `install` |
| [`prometheus_retention_period`](#prometheus_retention_period) | No | `15d` |
| [`prometheus_storage_class`](#prometheus_storage_class) | Conditional | Auto-detected |
| [`prometheus_storage_size`](#prometheus_storage_size) | No | `20Gi` |
| [`prometheus_alertmgr_storage_class`](#prometheus_alertmgr_storage_class) | Conditional | Auto-detected |
| [`prometheus_alertmgr_storage_size`](#prometheus_alertmgr_storage_size) | No | `20Gi` |
| [`prometheus_userworkload_retention_period`](#prometheus_userworkload_retention_period) | No | `15d` |
| [`prometheus_userworkload_storage_class`](#prometheus_userworkload_storage_class) | No | `prometheus_storage_class` |
| [`prometheus_userworkload_storage_size`](#prometheus_userworkload_storage_size) | No | `20Gi` |

The storage class variables are only required when auto-detection does not find a known storage class; for production deployments we recommend always setting them explicitly.

### Actions

#### cluster_monitoring_action

Action to perform on the cluster monitoring stack.

- **Optional**
- Environment Variable: `CLUSTER_MONITORING_ACTION`
- Default: `install`

Valid values are `install` (configure monitoring with persistent storage) and `uninstall` (remove the persistent storage configuration). All other variables only apply when the action is `install`.

!!! warning
    Uninstalling does not remove the monitoring stack itself, only the persistent storage configuration. Monitoring reverts to ephemeral storage and **all metrics data will be lost** when pods restart — back up any important metrics before uninstalling.

### Platform Monitoring

#### prometheus_retention_period

Retention period for platform Prometheus metrics, as a duration string with unit suffix — for example `7d` (minimal troubleshooting), `15d` (most deployments), `30d` (extended analysis), or `90d` (compliance).

- **Optional**
- Environment Variable: `PROMETHEUS_RETENTION_PERIOD`
- Default: `15d`

Only applies when both `prometheus_storage_class` and `prometheus_alertmgr_storage_class` are set. As a rule of thumb, a typical MAS deployment generates ~1-2GB of metrics per day — size `prometheus_storage_size` accordingly for your retention period.

#### prometheus_storage_class

Storage class for the platform Prometheus metrics persistent volume. Must support ReadWriteOnce (RWO) access mode; block storage is recommended for performance.

- **Required** when auto-detection does not find a known storage class
- Environment Variable: `PROMETHEUS_STORAGE_CLASS`
- Default: Auto-detected (`ibmc-block-gold`, `ocs-storagecluster-ceph-rbd`, or `managed-premium`)

Common values by platform: **IBM Cloud** `ibmc-block-gold` / `ibmc-block-silver`, **OpenShift Container Storage** `ocs-storagecluster-ceph-rbd`, **Azure** `managed-premium` / `managed-standard`, **AWS** `gp3` / `gp2`.

!!! tip
    Verify available storage classes with `oc get storageclass`. When this variable is not set, the role auto-detects the common storage classes listed above.

#### prometheus_storage_size

Size of the persistent volume for platform Prometheus metrics — for example `20Gi` (default, clusters with fewer than 50 nodes), `50Gi` (50-100 nodes), `100Gi` (100-200 nodes), or `200Gi` and above (very large clusters or long retention periods).

- **Optional**
- Environment Variable: `PROMETHEUS_STORAGE_SIZE`
- Default: `20Gi`

Only applies when both storage classes are set. Storage can be estimated as ~1-2GB per day × retention days × number of nodes / 50. Usage can be monitored with `oc get pvc -n openshift-monitoring`, and volumes can typically be expanded later (depending on the storage class).

### AlertManager

#### prometheus_alertmgr_storage_class

Storage class for the AlertManager persistent volume. Must support ReadWriteMany (RWX) access mode for the multi-replica AlertManager deployment — file storage is required, because block storage does not support RWX.

- **Required** when auto-detection does not find a known storage class
- Environment Variable: `PROMETHEUS_ALERTMGR_STORAGE_CLASS`
- Default: Auto-detected (`ibmc-file-gold-gid`, `ocs-storagecluster-cephfs`, or `azurefiles-premium`)

Common values by platform: **IBM Cloud** `ibmc-file-gold-gid` / `ibmc-file-silver-gid`, **OpenShift Container Storage** `ocs-storagecluster-cephfs`, **Azure** `azurefiles-premium` / `azurefiles-standard`, **AWS** `efs-sc` (requires the EFS CSI driver).

#### prometheus_alertmgr_storage_size

Size of the persistent volume for AlertManager. AlertManager uses far less storage than Prometheus: `20Gi` is sufficient for most deployments, `50Gi` for a large number of alert rules or notification channels.

- **Optional**
- Environment Variable: `PROMETHEUS_ALERTMGR_STORAGE_SIZE`
- Default: `20Gi`

Only applies when both storage classes are set.

### User Workload Monitoring

#### prometheus_userworkload_retention_period

Retention period for the user workload Prometheus instance, covering metrics from user applications and MAS workloads (not platform metrics) — for example `7d`, `15d` (default), or `30d` for extended application analysis.

- **Optional**
- Environment Variable: `PROMETHEUS_USERWORKLOAD_RETENTION_PERIOD`
- Default: `15d`

MAS applications (especially Manage) generate substantial metrics data — take this into account when setting retention and `prometheus_userworkload_storage_size`.

#### prometheus_userworkload_storage_class

Storage class for the user workload Prometheus metrics persistent volume. Must support ReadWriteOnce (RWO) access mode.

- **Optional**
- Environment Variable: `PROMETHEUS_USERWORKLOAD_STORAGE_CLASS`
- Default: Value of `prometheus_storage_class`

Typically inherits from `prometheus_storage_class`; set explicitly only if user workload metrics require different storage characteristics.

#### prometheus_userworkload_storage_size

Size of the persistent volume for user workload metrics — for example `20Gi` (default, 1-2 MAS applications), `50Gi` (3-5 applications), or `100Gi` (full MAS suite with extended retention).

- **Optional**
- Environment Variable: `PROMETHEUS_USERWORKLOAD_STORAGE_SIZE`
- Default: `20Gi`

Size based on the number of MAS applications × retention period × expected metrics volume. Usage can be monitored with `oc get pvc -n openshift-user-workload-monitoring`, and volumes can typically be expanded later.

## Example Playbook

```yaml
- hosts: localhost
  vars:
    prometheus_storage_class: "ibmc-block-gold"
    prometheus_alertmgr_storage_class: "ibmc-file-gold-gid"
  roles:
    - ibm.mas_devops.ocp_cluster_monitoring
```

## License

EPL-2.0
