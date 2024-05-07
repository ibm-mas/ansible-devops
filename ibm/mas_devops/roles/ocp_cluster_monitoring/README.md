ocp_cluster_monitoring
===============================================================================
Configures the OpenShift Container Platform Cluster Monitoring enabling two settings:

- [OpenShift user defined project monitoring](https://access.redhat.com/documentation/en-us/openshift_container_platform/4.12/html/monitoring/enabling-monitoring-for-user-defined-projects) is enabled (`openshift-monitoring` namespace)
- [OpenShift monitoring stack](https://access.redhat.com/documentation/en-us/openshift_container_platform/4.12/html/monitoring/index) is configured to use persistent storage (`openshift-monitoring` namespace)


Role Variables
-------------------------------------------------------------------------------
### cluster_monitoring_action
Inform the role whether to perform an `install` or an `uninstall` of the cluster monitoring stack.

- Optional
- Environment Variable: `CLUSTER_MONITORING_ACTION`
- Default: `install`

### prometheus_retention_period
Adjust the retention period for Prometheus metrics, only used when both `prometheus_storage_class` and `prometheus_alertmgr_storage_class` are set.

- Optional
- Environment Variable: `PROMETHEUS_RETENTION_PERIOD`
- Default Value: `15d`

### prometheus_storage_class
Declare the storage class for Prometheus' metrics data persistent volume.

- **Required** if one of the known supported storage classes is not installed in the cluster.
- Environment Variable: `PROMETHEUS_STORAGE_CLASS`
- Default Value: `ibmc-file-gold-gid`, `ocs-storagecluster-cephfs`, `azurefiles-premium` (if available)

### prometheus_storage_size
Adjust the size of the volume used to store metrics, only used when both `prometheus_storage_class` and `prometheus_alertmgr_storage_class` are set.

- Optional
- Environment Variable: `PROMETHEUS_STORAGE_SIZE`
- Default Value: `20Gi`

### prometheus_alertmgr_storage_class
Declare the storage class for AlertManager's persistent volume.

- **Required** if one of the known supported storage classes is not installed in the cluster.
- Environment Variable: `PROMETHEUS_ALERTMGR_STORAGE_CLASS`
- Default Value: `ibmc-file-gold-gid`, `ocs-storagecluster-cephfs`, `azurefiles-premium` (if available)

### prometheus_alertmgr_storage_size
Adjust the size of the volume used by AlertManager, only used when both `prometheus_storage_class` and `prometheus_alertmgr_storage_class` are set.

- Optional
- Environment Variable: `PROMETHEUS_ALERTMGR_STORAGE_SIZE`
- Default Value: `20Gi`

### prometheus_userworkload_retention_period
Adjust the retention period for User Workload Prometheus metrics, this parameter applies only to the User Workload Prometheus instance.

- Optional
- Environment Variable: `PROMETHEUS_USERWORKLOAD_RETENTION_PERIOD`
- Default Value: `15d`

### prometheus_userworkload_storage_class
Declare the storage class for User Workload Prometheus' metrics data persistent volume.

- Optional
- Environment Variable: `PROMETHEUS_USERWORKLOAD_STORAGE_CLASS`
- Default Value: `PROMETHEUS_STORAGE_CLASS`

### prometheus_userworkload_storage_size
Adjust the size of the volume used to store User Workload metrics.

- Optional
- Environment Variable: `PROMETHEUS_USERWORKLOAD_STORAGE_SIZE`
- Default Value: `20Gi`


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
