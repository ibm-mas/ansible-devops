cluster_monitoring
===============================================================================
Configures an in-cluster monitoring stack for IBM Maximo Application Suite:

- [OpenShift user defined project monitoring](https://access.redhat.com/documentation/en-us/openshift_container_platform/4.12/html/monitoring/enabling-monitoring-for-user-defined-projects) is enabled (`openshift-monitoring` namespace)
- [OpenShift monitoring stack](https://access.redhat.com/documentation/en-us/openshift_container_platform/4.12/html/monitoring/index) is configured to use persistent storage (`openshift-monitoring` namespace)
- [OpenTelemetry operator](https://github.com/open-telemetry/opentelemetry-operator) is installed (`openshift-operators` namespace)
- [Grafana](https://grafana.com/) installed using the [community grafana operator](https://github.com/grafana-operator/grafana-operator) (`grafana` namespace)

The credentials for the grafana admin user are stored in `grafana-admin-credentials` secret in the grafana namespace. A route  is created in the grafana namespace to allow access to the grafana UI.


Role Variables
-------------------------------------------------------------------------------
### cluster_monitoring_action
Inform the role whether to perform an install or an uninstall of cluster monitoring.

- Optional
- Environment Variable: `CLUSTER_MONITORING_ACTION`
- Default: `install`


Role Variables - Prometheus
-------------------------------------------------------------------------------
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
- Default Value: `300Gi`

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
- Default Value: `300Gi`


Role Variables - Grafana
-------------------------------------------------------------------------------
### grafana_namespace
Sets the namespace to install the grafana operator and grafana instance

- Optional
- Environment Variable: `GRAFANA_NAMESPACE`
- Default Value: `grafana`

### grafana_instance_storage_class
Declare the storage class for Grafana Instance user data persistent volume.

- **Required** if one of the known supported storage classes is not installed in the cluster.
- Environment Variable: `GRAFANA_INSTANCE_STORAGE_CLASS`
- Default Value: `ibmc-file-gold-gid`, `ocs-storagecluster-cephfs`, `azurefiles-premium` (if available)

### grafana_instance_storage_size
Adjust the size of the volume used to store Grafana user data.

- Optional
- Environment Variable: `GRAFANA_INSTANCE_STORAGE_SIZE`
- Default Value: `10Gi`


Example Playbook
-------------------------------------------------------------------------------

```yaml
- hosts: localhost
  vars:
    prometheus_storage_class: "ibmc-block-gold"
    prometheus_alertmgr_storage_class: "ibmc-file-gold-gid"
    grafana_instance_storage_class: "ibmc-file-gold-gid"
  roles:
    - ibm.mas_devops.cluster_monitoring
```


License
-------------------------------------------------------------------------------

EPL-2.0
