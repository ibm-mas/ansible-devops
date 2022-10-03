OCP Playbooks
===============================================================================

Provision
-------------------------------------------------------------------------------
Refer to the [ocp_provision](../roles/ocp_provision.md) role documentation for more information.

### Provision on AWS ROSA
This playbook uses your ROSA API Token to provision a brand new OCP cluster, provision an instance of EFS and set up the cluster with a ReadWriteMany storage class named `efs` utilizing that instance.

To obtain your API token login to the [OpenShift cluster manager](https://console.redhat.com/openshift/token/rosa/show#).

```bash
export AWS_ACCESS_KEY_ID=xxx
export AWS_SECRET_ACCESS_KEY=xxx
export ROSA_TOKEN=xxx

export CLUSTER_NAME=masonrosa
export OCP_VERSION=4.10
export ROSA_COMPUTE_NODES=5
export ROSA_CLUSTER_ADMIN_PASSWORD=xxx
ansible-playbook ibm.mas_devops.ocp_rosa_provision
```

### Provision on IBMCloud ROKS
This playbook uses your IBMCloud API key to provision a brand new OCP cluster.

The playbook supports installing an IBM entitlement key as a cluster-wide image pull secret and reboot all worker nodes, which is required for IBM Cloud Pak for Data v4; this can be enabled by setting `REBOOT_WORKER_NODES` to `true` and providing the entitlement key with `CPD_ENTITLEMENT_KEY`.

This also supports upgrading the storage volume used for the cluster's internal image registry from 100Gb to 400Gb, this must be enabled by setting `UPGRADE_IMAGE_REGISTRY_STORAGE` to `true`.  This option is stringly recommended if you intend to install the Watson services from Cloud Pak for Data as the default volume size is too small.

```bash
export CLUSTER_NAME=masinst1
export OCP_VERSION=4.8_openshift
export IBMCLOUD_APIKEY=xxx
export REBOOT_WORKER_NODES=true
export CPD_ENTITLEMENT_KEY=xxx
export UPGRADE_IMAGE_REGISTRY_STORAGE=true
ansible-playbook ibm.mas_devops.ocp_roks_provision
```

### Provision on IBM DevIT Fyre
This playbook will provision a QuickBurn OCP cluster in IBM DevIT Fyre service, QuickBurn clusters will be automatically deprovisioned after 36 hours and are only suitable for small scale deployments for local development and demostration systems.

```bash
export CLUSTER_NAME=masinst1
export OCP_VERSION=4.8
export FYRE_USERNAME=xxx
export FYRE_APIKEY=xxx
export FYRE_PRODUCT_ID=xxx

ansible-playbook ibm.mas_devops.ocp_fyre_provision
```


Deprovision
-------------------------------------------------------------------------------
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
