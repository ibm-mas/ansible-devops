# OCP Playbooks


## Provision
Refer to the [ocp_provision](../roles/ocp_provision.md) role documentation for more information.

### Provision on IBMCloud ROKS
```bash
export CLUSTER_NAME=masinst1
export OCP_VERSION="4.8_openshift"
export IBMCLOUD_APIKEY=xxx

ansible-playbook ibm.mas_devops.ocp_roks_provision
```

### Provision on IBM DevIT Fyre
```bash
export CLUSTER_NAME=masinst1
export OCP_VERSION=4.8
export FYRE_USERNAME=xxx
export FYRE_APIKEY=xxx
export FYRE_PRODUCT_ID=xxx

ansible-playbook ibm.mas_devops.ocp_fyre_provision
```


## Deprovision
Refer to the [ocp_deprovision](../roles/ocp_deprovision.md) role documentation for more information.

### Deprovision on IBMCloud ROKS
```bash
export CLUSTER_NAME=masinst1
export IBMCLOUD_APIKEY=xxx

ansible-playbook ibm.mas_devops.ocp_roks_deprovision
```

### Deprovision on IBM DevIT Fyre
```bash
export CLUSTER_NAME=masinst1
export FYRE_USERNAME=xxx
export FYRE_APIKEY=xxx

ansible-playbook ibm.mas_devops.ocp_fyre_deprovision
```
