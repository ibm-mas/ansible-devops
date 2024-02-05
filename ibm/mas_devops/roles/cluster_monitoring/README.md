cluster_monitoring
===============================================================================
Configures an in-cluster monitoring stack for IBM Maximo Application Suite:

- [OpenShift user defined project monitoring](https://access.redhat.com/documentation/en-us/openshift_container_platform/4.12/html/monitoring/enabling-monitoring-for-user-defined-projects) is enabled (`openshift-monitoring` namespace)
- [OpenShift monitoring stack](https://access.redhat.com/documentation/en-us/openshift_container_platform/4.12/html/monitoring/index) is configured to use persistent storage (`openshift-monitoring` namespace)
- [OpenTelemetry operator](https://github.com/open-telemetry/opentelemetry-operator) is installed (optional, `openshift-operators` namespace)
- [Grafana](https://grafana.com/) installed using the [community grafana operator](https://github.com/grafana-operator/grafana-operator) (`grafana` or `grafana5` namespace)

The credentials for the grafana admin user are stored in `grafana-admin-credentials` secret in the grafana namespace. A route  is created in the grafana namespace to allow access to the grafana UI.


Role Variables
-------------------------------------------------------------------------------
### cluster_monitoring_action
Inform the role whether to perform an `install` or an `uninstall` of the cluster monitoring stack. Can also be set to `update_grafana` to update the Grafana Operator from V4 to V5.

!!! note
    When using this role to upgrade from Grafana 4 to 5, the Grafana 5 instance will have a new URL and will not inherit the user database from the old v4 installation, the admin password will be new, and user accounts set up in the v4 instance will need to be recreated in the v5 instance.

- Optional
- Environment Variable: `CLUSTER_MONITORING_ACTION`
- Default: `install`

### cluster_monitoring_include_prometheus
By default this role will reconfigure Prometheus to enable persistent storage and user workload monitoring, this can be disabled by setting this variable to `False`.

- Optional
- Environment Variable: `CLUSTER_MONITORING_INCLUDE_PROMETHEUS`
- Default: `True`

### cluster_monitoring_include_grafana
By default Grafana is included in the monitoring stack, this can be disabled by setting this variable to `False`.

- Optional
- Environment Variable: `CLUSTER_MONITORING_INCLUDE_GRAFANA`
- Default: `True`

### cluster_monitoring_include_opentelemetry
By default OpenTelemtry is **not** included in the monitoring stack, this can be enabled by setting this variable to `True`.

- Optional
- Environment Variable: `CLUSTER_MONITORING_INCLUDE_OPENTELEMETRY`
- Default: `False`


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


Role Variables - Grafana
-------------------------------------------------------------------------------
### grafana_major_version
Sets the major version of the grafana operator to install. `4` or `5`

- Optional
- Environment Variable: `GRAFANA_MAJOR_VERSION`
- Default Value: `4`

### grafana_namespace
Sets the namespace to install the grafana operator V4 and grafana instance

- Optional
- Environment Variable: `GRAFANA_V4_NAMESPACE`
- Default Value: `grafana`

### grafana_v5_namespace
Sets the namespace to install the grafana operator V5 and grafana instance

- Optional
- Environment Variable: `GRAFANA_V5_NAMESPACE`
- Default Value: `grafana5`

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

To Upgrade from Grafana Operator from V4 to V5

```yaml
- hosts: localhost
  vars:
    cluster_monitoring_action: "update-grafana"
  roles:
    - ibm.mas_devops.cluster_monitoring
```

License
-------------------------------------------------------------------------------

EPL-2.0
