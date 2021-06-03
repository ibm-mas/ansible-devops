# OCP Playbooks

## ROKS
Provide intro ...

### Required environment variables
- `IBMCLOUD_APIKEY` Short statement
- `CLUSTER_NAME` Short statement
- `OCP_VERSION` Short statement

### Optional environment variables
- `ROKS_ZONE` Short statement
- `ROKS_FLAVOR` Short statement
- `ROKS_WORKERS` Short statement
- `ROKS_FLAGS` Short statement
- `W3_USERNAME` This is required if you want to install the pre-release MAS operator catalogs
- `ARTIFACTORY_APIKEY` This is required if you want to install the pre-release MAS operator catalogs


### Provision

As part of provisioning on ROKS:

- The **IBM operator catalog** and **IBM common services catalog** will be installed
- MAS development catalogs will be installed if `W3_USERNAME` and `ARTIFACTORY_APIKEY` environment variables are **both** defined
- [Certificate manager](https://cert-manager.io) and [service binding](https://github.com/redhat-developer/service-binding-operator) operators will be installed at cluster scope
- [Monitoring for user-defined projects](https://docs.openshift.com/container-platform/4.6/monitoring/enabling-monitoring-for-user-defined-projects.html#enabling-monitoring-for-user-defined-projects_enabling-monitoring-for-user-defined-projects) will be enabled in the cluster

```bash
export VAR_NAME=xxx
export VAR_NAME=xxx

ansible-playbook playbooks/ocp/provision-roks.yml
```

### Deprovision
```bash
export VAR_NAME=xxx
export VAR_NAME=xxx

ansible-playbook playbooks/ocp/deprovision-roks.yml
```

## QuickBurn
Provide intro ...

### Required environment variables
- `FYRE_USERNAME` Short statement
- `FYRE_APIKEY` Short statement
- `FYRE_PRODUCT_ID` Short statement
- `CLUSTER_NAME` Short statement
- `OCP_VERSION` Short statement

### Optional environment variables
- `FYRE_CLUSTER_SIZE` Short statement
- `W3_USERNAME` This is required if you want to install the pre-release MAS operator catalogs
- `ARTIFACTORY_APIKEY` This is required if you want to install the pre-release MAS operator catalogs

### Provision

As part of provisioning on QuickBurn:

- The **IBM operator catalog** and **IBM common services catalog** will be installed
- MAS development catalogs will be installed if `W3_USERNAME` and `ARTIFACTORY_APIKEY` environment variables are **both** defined
- [Certificate manager](https://cert-manager.io) and [service binding](https://github.com/redhat-developer/service-binding-operator) operators will be installed at cluster scope
- [Monitoring for user-defined projects](https://docs.openshift.com/container-platform/4.6/monitoring/enabling-monitoring-for-user-defined-projects.html#enabling-monitoring-for-user-defined-projects_enabling-monitoring-for-user-defined-projects) will be enabled in the cluster
- [OpenShift Container Storage](https://www.redhat.com/en/resources/quay-overview) will be configured in the cluster

```bash
export FYRE_USERNAME=xxx
export FYRE_APIKEY=xxx
export FYRE_PRODUCT_ID=225
export CLUSTER_NAME=xxx
export OCP_VERSION=4.6.16

ansible-playbook playbooks/ocp/provision-quickburn.yml
```

### Deprovision
```bash
export FYRE_USERNAME=xxx
export FYRE_APIKEY=xxx
export CLUSTER_NAME=xxx

ansible-playbook playbooks/ocp/deprovision-quickburn.yml
```

