# OCP Playbooks

## Provision
Refer to the [ocp_provision](../roles/ocp_provision.md) role documentation for more information.

```bash
export CLUSTER_NAME=masinst1
export OCP_VERSION="4.8_openshift"
export CLUSTER_TYPE=roks

export IBMCLOUD_APIKEY=xxx

ansible-playbook ibm.mas_devops.ocp_provision
```

```bash
export CLUSTER_NAME=masinst1
export OCP_VERSION=4.6.16
export CLUSTER_TYPE=quickburn

export FYRE_USERNAME=xxx
export FYRE_APIKEY=xxx
export FYRE_PRODUCT_ID=xxx

ansible-playbook ibm.mas_devops.ocp_provision
```


## Deprovision
Refer to the [ocp_deprovision](../roles/ocp_deprovision.md) role documentation for more information.

```bash
export CLUSTER_NAME=masinst1
export CLUSTER_TYPE=roks

export IBMCLOUD_APIKEY=xxx

ansible-playbook ibm.mas_devops.ocp_deprovision
```

```bash
export CLUSTER_NAME=masinst1
export CLUSTER_TYPE=quickburn
export FYRE_USERNAME=xxx
export FYRE_APIKEY=xxx

ansible-playbook ibm.mas_devops.ocp_deprovision
```


## Configure
Refer to the [ocp_setup_mas_deps](../roles/ocp_setup_mas_deps.md) role documentation for more information.

```bash
ansible-playbook ibm.mas_devops.ocp_configure
```


## Verify
Refer to the [ocp_verify](../roles/ocp_verify.md) role documentation for more information.


```bash
ansible-playbook ibm.mas_devops.ocp_verify
```
