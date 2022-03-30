ocp_provision
=============

Provision OCP cluster on DevIT Fyre or IBM Cloud ROKS.


Role Variables
--------------

### cluster_type
Required.  Specify the cluster type, supported values are `roks` and `quickburn`.

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

### ocp_provision_gpu
Flag that determines if GPU worker nodes should be added during cluster creation (eg. needed for MVI application). This is currently only set up for ROKS clusters.

- Environment Variable: `OCP_PROVISION_GPU`
- Default Value: `false`

### gpu_workers
The number of GPU worker nodes to deploy in the cluster. Depends on `ocp_provision_gpu` and is currently only set up for ROKS clusters.

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
- Default Value: `b3c.8x32`

### roks_workers
Number of worker nodes for the roks cluster

- Environment Variable: `ROKS_WORKERS`
- Default Value: `6`

### roks_flags
Can be used to specify additional parameters for the cluster creation

- Environment Variable: `ROKS_FLAGS`
- Default Value: None


Role Variables - Quickburn
--------------------------
The following variables are only used when `cluster_type = quickburn`.

### fyre_username
Required if `cluster_type = quickburn`.  IBM Cloud zone where the cluster should be provisioned.

- Environment Variable: `FYRE_USERNAME`
- Default Value: None

### fyre_password
Required if `cluster_type = quickburn`.  IBM Cloud zone where the cluster should be provisioned.

- Environment Variable: `FYRE_PASSWORD`
- Default Value: None

### fyre_product_id
Required if `cluster_type = quickburn`.  The Product ID that the cluster will be associated with for accounting purposes.

- Environment Variable: `FYRE_PRODUCT_ID`
- Default Value: None

### fyre_cluster_size
The name of one of Fyre's pre-defined cluster sizes to use for the new cluster.

- Environment Variable: `FYRE_CLUSTER_SIZE`
- Default Value: `large`



Example Playbook - ROKS
-----------------------

```yaml
- hosts: localhost
  vars:
    cluster_name: masinst1
    cluster_type: roks
    ocp_version: "4.8_openshift"
    ibmcloud_apikey: "{{ lookup('env', 'IBMCLOUD_APIKEY') }}"
  roles:
    - ibm.mas_devops.ocp_provision
```

Example Playbook - Quickburn
----------------------------

```yaml
- hosts: localhost
  vars:
    cluster_name: masinst1
    cluster_type: quickburn
    ocp_version: "4.6.16"
    fyre_username: "{{ lookup('env', 'FYRE_USERNAME') }}"
    fyre_password: "{{ lookup('env', 'FYRE_PASSWORD') }}"
    fyre_product_id: "{{ lookup('env', 'FYRE_PRODUCT_ID') }}"
  roles:
    - ibm.mas_devops.ocp_provision
```

License
-------

EPL-2.0
