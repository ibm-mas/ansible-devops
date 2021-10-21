# OCP Playbooks

## Provision

### ROKS
As part of provisioning on IBM Cloud:

- The **IBM operator catalog** will be installed
- MAS development catalogs will be installed if `W3_USERNAME` and `ARTIFACTORY_APIKEY` environment variables are **both** defined
- [Certificate manager](https://cert-manager.io) and [service binding](https://github.com/redhat-developer/service-binding-operator) operators will be installed at cluster scope
- [Monitoring for user-defined projects](https://docs.openshift.com/container-platform/4.6/monitoring/enabling-monitoring-for-user-defined-projects.html#enabling-monitoring-for-user-defined-projects_enabling-monitoring-for-user-defined-projects) will be enabled in the cluster

#### Required environment variables
- `IBMCLOUD_APIKEY` Short statement
- `CLUSTER_NAME` Short statement
- `OCP_VERSION` Short statement

#### Optional environment variables
- `ROKS_ZONE` Short statement
- `ROKS_FLAVOR` Short statement
- `ROKS_WORKERS` Short statement
- `ROKS_FLAGS` Short statement

#### Example
```bash
export VAR_NAME=xxx
export VAR_NAME=xxx

ansible-playbook playbooks/ocp/provision-roks.yml
```


### QuickBurn
As part of provisioning on QuickBurn:

#### Required environment variables
- `FYRE_USERNAME` Short statement
- `FYRE_APIKEY` Short statement
- `FYRE_PRODUCT_ID` Short statement
- `CLUSTER_NAME` Short statement
- `OCP_VERSION` Short statement

#### Optional environment variables
- `FYRE_CLUSTER_SIZE` Short statement

### Example
```bash
export FYRE_USERNAME=xxx
export FYRE_APIKEY=xxx
export FYRE_PRODUCT_ID=225
export CLUSTER_NAME=xxx
export OCP_VERSION=4.6.16

ansible-playbook playbooks/ocp/provision-quickburn.yml
```



## Configure
Running configuration will result in the following actions being taken:
- The **IBM operator catalog** and **IBM common services catalog** will be installed
- MAS development catalogs will be installed if `W3_USERNAME` and `ARTIFACTORY_APIKEY` environment variables are **both** defined
- [Certificate manager](https://cert-manager.io) and [service binding](https://github.com/redhat-developer/service-binding-operator) operators will be installed at cluster scope
- [Monitoring for user-defined projects](https://docs.openshift.com/container-platform/4.6/monitoring/enabling-monitoring-for-user-defined-projects.html#enabling-monitoring-for-user-defined-projects_enabling-monitoring-for-user-defined-projects) will be enabled in the cluster
- [OpenShift Container Storage](https://www.redhat.com/en/resources/quay-overview) will be configured in the cluster

### Required environment variables
- `GRAFANA_USER` user name to be registered for authentication in Grafana portal
- `GRAFANA_PASSWORD` user password to be registered for authentication in Grafana portal
- `GRAFANA_STORAGE_CLASS` storage class of GrafanaDataSource

### Optional environment variables
- `GRAFANA_STORAGE_SIZE` size of GrafanaDataSource, this will default to `10Gi`
- `GRAFANA_DATASOURCE_URL` url of grafana data source, this will default to Thanos Querier (Prometheus) internal service: `https://thanos-querier.openshift-monitoring.svc:9091`
- `W3_USERNAME` This is required if you want to install the pre-release MAS operator catalogs
- `ARTIFACTORY_APIKEY` This is required if you want to install the pre-release MAS operator catalogs

### Example

```bash
export GRAFANA_USER=admin
export GRAFANA_PASSWORD=password
export GRAFANA_STORAGE_CLASS=ibmc-file-gold-gid

ansible-playbook playbooks/ocp/configure-ocp.yml
```



## Deprovision

### ROKS
```bash
export VAR_NAME=xxx
export VAR_NAME=xxx

ansible-playbook playbooks/ocp/deprovision-roks.yml
```

### QuickBurn
```bash
export FYRE_USERNAME=xxx
export FYRE_APIKEY=xxx
export CLUSTER_NAME=xxx

ansible-playbook playbooks/ocp/deprovision-quickburn.yml
```
