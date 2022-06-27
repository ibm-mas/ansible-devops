ocp_provision
=============

Provision OCP cluster on DevIT Fyre or IBM Cloud ROKS.


Role Variables
--------------

### cluster_type
Required.  Specify the cluster type, supported values are `fyre`, `roks` and `rosa`.

- Environment Variable: `CLUSTER_TYPE`
- Default Value: None

### cluster_name
Required.  Specify the name of the cluster

- Environment Variable: `CLUSTER_NAME`
- Default Value: None

### ocp_version
Required.  Specify the version of OCP to install.  The exact format of this will vary depending on `cluster_type`.  For ROKS clusters the format is `4.6_openshift`, `4.8_openshift`, for Fyre it is `4.6.16`.

- Environment Variable: `OCP_VERSION`
- Default Value: None


Role Variables - GPU Node Support
---------------------------------
### ocp_provision_gpu
Flag that determines if GPU worker nodes should be added during cluster creation (eg. needed for MVI application). This is currently only set up for ROKS clusters.

- Environment Variable: `OCP_PROVISION_GPU`
- Default Value: `false`

### gpu_workerpool_name
The name of the gpu worker pool to added to or modify in the cluster. If already existing, use the existing name to avoid recreating another gpu worker pool unless that is the goal.

- Environment Variable: `GPU_WORKERPOOL_NAME`
- Default Value: `gpu`

### gpu_workers
The number of GPU worker nodes that will be deploy in the cluster. The node created will have mg4c.32x384.2xp100-GPU flavor. This variable depends on `ocp_provision_gpu` and is currently supported on ROKS clusters only.

- Environment Variable: `GPU_WORKERS`
- Default Value: `1`


Role Variables - ROKS
---------------------
The following variables are only used when `cluster_type = roks`.

### ibmcloud_apikey
Required if `cluster_type = roks`.  The APIKey to be used by ibmcloud login comand.

- Environment Variable: `IBMCLOUD_APIKEY`
- Default Value: None

### ibmcloud_resourcegroup
The resource group to create the cluster inside.

- Environment Variable: `IBMCLOUD_RESOURCEGROUP`
- Default Value: `Default`

### roks_zone
IBM Cloud zone where the cluster should be provisioned.

- Environment Variable: `ROKS_ZONE`
- Default Value: `lon02`

### roks_flavor
Worker node flavor

- Environment Variable: `ROKS_FLAVOR`
- Default Value: `b3c.16x64.300gb`

### roks_workers
Number of worker nodes for the roks cluster

- Environment Variable: `ROKS_WORKERS`
- Default Value: `3`

### roks_flags
Can be used to specify additional parameters for the cluster creation

- Environment Variable: `ROKS_FLAGS`
- Default Value: None


Role Variables - ROSA
---------------------
The following variables are only used when `cluster_type = rosa`.

### roso_token
Token to authenticate to the ROSA service

- **Required** if `cluster_type = rosa`.
- Environment Variable: `ROSA_TOKEN`
- Default Value: None

### roso_cluster_admin_password
Password to set up for the `cluster-admin` user account on the OCP instance.  You will need this to log onto the cluster after it is provisioned.

- **Required** if `cluster_type = rosa`.
- Environment Variable: `ROSA_CLUSTER_ADMIN_PASSWORD`
- Default Value: None

### rosa_compute_nodes
Number of compute nodes to deploy in the cluster.

- Optional
- Environment Variable: `ROSA_COMPUTE_NODES`
- Default Value: `3`


Role Variables - Fyre
---------------------
The following variables are only used when `cluster_type = fyre`.

### fyre_username
Username to authenticate with Fyre API.

- **Required** if `cluster_type = fyre`.
- Environment Variable: `FYRE_USERNAME`
- Default Value: None

### fyre_apikey
API key to authenticate with Fyre API.

- **Required** if `cluster_type = fyre`.
- Environment Variable: `FYRE_APIKEY`
- Default Value: None

### fyre_quota_type
Type of quota to draw from when provisioning the cluster, valid options are `quick_burn` and `product_group`.

- **Required** if `cluster_type = fyre`.
- Environment Variable: `FYRE_QUOTA_TYPE`
- Default Value: `quick_burn`

### fyre_product_id
The Product ID that the cluster will be associated with for accounting purposes.

- **Required** if `cluster_type = fyre`.
- Environment Variable: `FYRE_PRODUCT_ID`
- Default Value: None

### fyre_cluster_description
Provide a description for the cluster.

- Optional
- Environment Variable: `FYRE_CLUSTER_DESCRIPTION`
- Default Value: None

### fyre_cluster_size
The name of one of Fyre's pre-defined cluster sizes to use for the new cluster.

- **Required** when `cluster_type = fyre` and `fyre_quota_type = quick_burn`.
- Environment Variable: `FYRE_CLUSTER_SIZE`
- Default Value: `large`

### fyre_worker_count
The number of worker nodes to provision in the cluster.

- **Required** when `cluster_type = fyre` and `fyre_quota_type = quick_burn`.
- Environment Variable: `FYRE_WORKER_COUNT`
- Default Value: `3`

### fyre_worker_cpu
The amount of CPU to assign to each worker node (maximum value supported by FYRE 16).

- **Required** when `cluster_type = fyre` and `fyre_quota_type = quick_burn`.
- Environment Variable: `FYRE_WORKER_CPU`
- Default Value: `16`

### fyre_worker_memory
The amount of memory to assign to each worker node (maximum value supported by FYRE 64).

- **Required** when `cluster_type = fyre` and `fyre_quota_type = quick_burn`.
- Environment Variable: `FYRE_WORKER_MEMORY`
- Default Value: `64`



Example Playbook
-----------------------

```yaml
- hosts: localhost
  vars:
    cluster_type: roks
    cluster_name: mycluster
    ocp_version: 4.10

    ibmcloud_apikey: xxxxx
  roles:
    - ibm.mas_devops.ocp_provision
```

License
-------

EPL-2.0
