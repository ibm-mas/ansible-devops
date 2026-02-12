ocp_cluster_monitoring
===============================================================================
Configures the OpenShift Container Platform Cluster Monitoring enabling two settings:

- [OpenShift user defined project monitoring](https://docs.redhat.com/en/documentation/openshift_container_platform/4.20/html/monitoring/configuring-user-workload-monitoring#preparing-to-configure-the-monitoring-stack-uwm) is enabled (`openshift-monitoring` namespace)
- [OpenShift monitoring stack](https://docs.redhat.com/en/documentation/monitoring_stack_for_red_hat_openshift/4.20/html/release_notes_for_openshift_monitoring/monitoring-release-notes) is configured to use persistent storage (`openshift-monitoring` namespace)

This role is version-aware and will automatically apply the appropriate configuration template based on the detected OpenShift version:
- For OpenShift 4.18 and higher: Uses a simplified configuration template compatible with newer versions
- For OpenShift versions below 4.18: Uses the traditional configuration template


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
Declare the storage class for Prometheus' metrics data persistent volume. Storage class must support ReadWriteOnce(RWO) access mode.

- **Required** if one of the known supported storage classes is not installed in the cluster.
- Environment Variable: `PROMETHEUS_STORAGE_CLASS`
- Default Value: `ibmc-block-gold`, `ocs-storagecluster-ceph-rbd`, or `managed-premium` (if available)

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
- **Note**: Storage class must support ReadWriteMany(RWX) access mode.

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
Declare the storage class for User Workload Prometheus' metrics data persistent volume. Storage class must support ReadWriteOnce(RWO) access mode.

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
