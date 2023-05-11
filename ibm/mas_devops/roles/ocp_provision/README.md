ocp_provision
===============================================================================

Provision OCP cluster on DevIT Fyre or IBM Cloud ROKS.

Role Variables
-------------------------------------------------------------------------------
### cluster_type
Required.  Specify the cluster type, supported values are `fyre`, `roks`, `rosa`, and `ipi`.

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
-------------------------------------------------------------------------------
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

### compute_node_count
The number of compute nodes (i.e. worker nodes) allocate to the OCP cluster.

- Environment Variable: `COMPUTE_NODE_COUNT`
- Default Value: `3`

### controlplane_node_count
The number of control plane nodes (i.e. master nodes) allocate to the OCP cluster.

- Environment Variable: `CONTROLPLANE_NODE_COUNT`
- Default Value: `3`

### gpu_workerpool_name
The name of the gpu worker pool to added to or modify in the cluster. If already existing, use the existing name to avoid recreating another gpu worker pool unless that is the goal.

- Environment Variable: `GPU_WORKERPOOL_NAME`
- Default Value: `gpu`


Role Variables - ROKS
-------------------------------------------------------------------------------
The following variables are only used when `cluster_type = roks`.

### ibmcloud_apikey
Required if `cluster_type = roks`.  The APIKey to be used by ibmcloud login comand.

- Environment Variable: `IBMCLOUD_APIKEY`
- Default Value: None

### ibmcloud_endpoint
Override the default IBMCloud API endpoint.

- Optional
- Environment Variable: `IBMCLOUD_ENDPOINT`
- Default Value: `https://cloud.ibm.com`

### ibmcloud_resourcegroup
The resource group to create the cluster inside.

- Optional
- Environment Variable: `IBMCLOUD_RESOURCEGROUP`
- Default Value: `Default`

### roks_zone
IBM Cloud zone where the cluster should be provisioned.

- Optional
- Environment Variable: `ROKS_ZONE`
- Default Value: `dal10`

### roks_flavor
Worker node flavor

- Optional
- Environment Variable: `ROKS_FLAVOR`
- Default Value: `b3c.16x64.300gb`

### roks_workers
Number of worker nodes for the roks cluster

- Optional
- Environment Variable: `ROKS_WORKERS`
- Default Value: `3`

### roks_flags
Can be used to specify additional parameters for the cluster creation

- Optional
- Environment Variable: `ROKS_FLAGS`
- Default Value: None


Role Variables - ROSA
-------------------------------------------------------------------------------
The following variables are only used when `cluster_type = rosa`.

### rosa_token
Token to authenticate to the ROSA service.  To obtain your API token login to the [OpenShift cluster manager](https://console.redhat.com/openshift/token/rosa/show#).

- **Required** if `cluster_type = rosa`.
- Environment Variable: `ROSA_TOKEN`
- Default Value: None

### rosa_cluster_admin_password
Password to set up for the `cluster-admin` user account on the OCP instance.  You will need this to log onto the cluster after it is provisioned.

- **Required** if `cluster_type = rosa`.
- Environment Variable: `ROSA_CLUSTER_ADMIN_PASSWORD`
- Default Value: None

### rosa_compute_nodes
Number of compute nodes to deploy in the cluster.

- Optional
- Environment Variable: `ROSA_COMPUTE_NODES`
- Default Value: `3`


Role Variables - FYRE
-------------------------------------------------------------------------------
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

### ocp_fips_enabled
Set to true to provision a FIPS enabled cluster.

- Optional
- Environment Variable: `OCP_FIPS_ENABLED`
- Default Value: `false`

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


Role Variables - IPI
-------------------------------------------------------------------------------
These variables are only used when `cluster_type = ipi`.

!!! note
    IPI stands for **Installer Provisioned Infrastructure**.  OpenShift offers two possible deployment methods: IPI and UPI (User Provisioned Infrastructure). The difference is the degree of automation and customization. IPI will not only deploy OpenShift but also all infrastructure components and configurations.

### ipi_platform
Platform to create the cluster on.  Technically, any platform supported by `openshift-install` should work here, but currently we have only specifically tested on `aws` and `gcp` , where `aws` is the default value.

- Optional when `cluster_type = ipi`
- Environment Variable: `IPI_PLATFORM`
- Default Value: `aws`


### ipi_region
Platform region where OCP cluster will be created.

- Optional when `cluster_type = ipi`
- Environment Variable: `IPI_REGION`
- Default Value: `us-east-1`

### ipi_base_domain
Specify the base domain of the cluster that will be provisioned.

- **Required** when `cluster_type = aipi`
- Environment Variable: `IPI_BASE_DOMAIN`
- Default Value: None

### ipi_pull_secret_file
Location of the file containing your Redhat OpenShift pull secret.  This file can be obtained from the [Red Hat Hybrid Cloud Console](https://console.redhat.com/openshift/install/metal/user-provisioned)

- **Required** when `cluster_type = ipi`
- Environment Variable: `IPI_PULL_SECRET_FILE`
- Default Value: None

### ipi_dir
The working directory that is used to perform the installation, it will contain the `openshift-install` executable, its configuration files, & any generated logs.

- Optional when `cluster_type = ipi`
- Environment Variable: `IPI_DIR`
- Default Value: `~/openshift-install`

### sshKey
Public SSH key value. It will be set in the OCP cluster nodes.
Can be used to SSH into the OCP cluster nodes using a bastion.

- Optional when `cluster_type = ipi`
- Environment Variable: `SSH_PUB_KEY`


### ipi_controlplane_type
Control plane node type.

- Optional when `cluster_type = ipi`
- Environment Variable: `IPI_CONTROLPLANE_TYPE`
- Default Value: `m5.4xlarge`

### ipi_controlplane_replicas
The number of master nodes to provision to form the control plane of your cluster.

- Optional when `cluster_type = ipi`
- Environment Variable: `IPI_CONTROLPLANE_REPLICAS`
- Default Value: `3`

### ipi_compute_type
Compute node type.

- Optional when `cluster_type = ipi`
- Environment Variable: `IPI_COMPUTE_TYPE`
- Default Value: `m5.4xlarge`

### ipi_compute_replicas
The number of worker nodes to provsision in the cluster, providing your compute resource.

- Optional when `cluster_type = ipi`
- Environment Variable: `IPI_COMPUTE_REPLICAS`
- Default Value: `3`


Role Variables - AWS
-------------------------------------------------------------------------------
The following variables are only used when `cluster_type = ipi` and `ipi_platform = aws`.

### aws_access_key_id
AWS access key associated with an IAM user or role. Make sure the access key has permissions to create instances.

- **Required** when `cluster_type = ipi` and `ipi_platform = aws`
- Environment Variable: `AWS_ACCESS_KEY_ID`
- Default Value: None

### aws_secret_access_key
AWS secret access key associated with an IAM user or role.

- **Required** when `cluster_type = aws-ipi` and `ipi_platform = aws`
- Environment Variable: `AWS_SECRET_ACCESS_KEY`
- Default Value: None

Role Variables - GCP
-------------------------------------------------------------------------------
The following variables are only used when `cluster_type = ipi` and `ipi_platform = gcp`.

### gcp_service_account_file
GCP service account file path. Make sure the service account has permissions to create instances.

- **Required** when `cluster_type = ipi` and `ipi_platform = gcp`
- Environment Variable: `GOOGLE_APPLICATION_CREDENTIALS`
- Default Value: None

### ipi_gcp_projectid
GCP project id in which the cluster will be deployed.

- **Required** when `cluster_type = ipi` and `ipi_platform = gcp`
- Environment Variable: `GOOGLE_PROJECTID`
- Default Value: None

Example Playbook
-------------------------------------------------------------------------------

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
-------------------------------------------------------------------------------

EPL-2.0
