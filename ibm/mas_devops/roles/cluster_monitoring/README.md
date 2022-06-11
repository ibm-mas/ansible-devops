cluster_monitoring
==================

Configure both prometheus cluster monitoring and prometheus user workload cluster monitoring with persistant storage. Also configures 
the [community grafana operator](https://github.com/grafana-operator/grafana-operator) v4 and deploys a grafana instance along with 
a datasource to prometheus. The grafana operator will scan for dashboards across the whole cluster so that it can import any dashbaords
from Maximo Application Suite. The namespace grafana is installed to defaults to `grafana` but can be changed using the role variables
below. The credentials for the grafana admin user are stored in `grafana-admin-credentials` secret in the grafana namespace. A route
is created in the grafana namespace to allow access to the grafana UI.

Role Variables
--------------
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

### grafana_namespace
Sets the namespace to install the grafana operator and grafana instance

- Optional
- Environment Variable: `GRAFANA_NAMESPACE`
- Default Value: `grafana`

Example Playbook
----------------

```yaml
- hosts: localhost
  vars:
    prometheus_storage_class: "ibmc-block-gold"
    prometheus_alertmgr_storage_class: "ibmc-file-gold-gid"
  roles:
    - ibm.mas_devops.cluster_monitoring
```


Tekton Task
-----------
Start a run of the **mas-devops-cluster-monitoring** Task as below, you must have already prepared the namespace:

```
cat <<EOF | oc create -f -
apiVersion: tekton.dev/v1beta1
kind: TaskRun
metadata:
  generateName: mas-devops-cluster-monitoring-
spec:
  taskRef:
    kind: Task
    name: mas-devops-cluster-monitoring
  params:
  - name: prometheus_storage_class
    value: "ibmc-block-gold"
  - name: prometheus_alertmgr_storage_class
    value: "ibmc-file-gold-gid"
  - name: prometheus_userworkload_storage_class
    value: "ibmc-block-gold"
  resources: {}
  serviceAccountName: pipeline
  timeout: 24h0m0s
EOF
```


License
-------

EPL-2.0
