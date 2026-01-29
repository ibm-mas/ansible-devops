ocp_provision
===============================================================================
Provision OCP cluster on IBM Cloud ROKS, ROSA, or DevIT Fyre.

Fyre clusters will be automatically reconfigured to enable NFS storage.  By default this is made available via the `nfs-client` storage class and supports both `ReadWriteOnce` and `ReadWriteMany` access modes.  The `image-registry-storage` PVC used by the OpenShift image registry component will also be reconfigured to use this storage class.


Role Variables
-------------------------------------------------------------------------------
### cluster_type
Infrastructure provider type for cluster provisioning.

- **Required**
- Environment Variable: `CLUSTER_TYPE`
- Default: None

**Purpose**: Specifies which infrastructure provider to use for provisioning the OpenShift cluster. Determines provisioning method and required variables.

**When to use**:
- Always required for cluster provisioning
- Each type requires different provider-specific variables
- Determines available features (e.g., GPU support for ROKS)

**Valid values**: `fyre`, `roks`, `rosa`, `ipi`
- `fyre`: IBM DevIT Fyre clusters (internal development)
- `roks`: IBM Cloud Red Hat OpenShift Kubernetes Service
- `rosa`: AWS Red Hat OpenShift Service on AWS
- `ipi`: Installer-Provisioned Infrastructure (bare metal/on-premises)

**Impact**: Determines provisioning workflow and which provider-specific variables are required. Each type has different capabilities and configuration options.

**Related variables**:
- `cluster_name`: Name for the new cluster
- `ocp_version`: OpenShift version to install
- Provider-specific variables (ibmcloud_apikey, rosa_token, fyre_apikey, etc.)

**Note**: Fyre clusters automatically configure NFS storage. ROKS requires version format like `4.19_openshift`.

### cluster_name
Name for the new cluster.

- **Required**
- Environment Variable: `CLUSTER_NAME`
- Default: None

**Purpose**: Specifies the name for the OpenShift cluster to be provisioned. Used as the cluster identifier in the provider's system.

**When to use**:
- Always required for cluster provisioning
- Must be unique within the provider's account/region
- Used for cluster identification and resource naming

**Valid values**: String following provider naming conventions (typically lowercase alphanumeric with hyphens)

**Impact**: Determines the cluster name in the provider's system. Used for DNS, resource naming, and cluster identification.

**Related variables**:
- `cluster_type`: Provider where cluster will be created
- `ocp_version`: OpenShift version for the cluster

**Note**: Name must follow provider-specific naming rules. Some providers have length limits or character restrictions.

### ocp_version
OpenShift version to install.

- **Required**
- Environment Variable: `OCP_VERSION`
- Default: None

**Purpose**: Specifies which version of OpenShift Container Platform to install on the provisioned cluster.

**When to use**:
- Always required for cluster provisioning
- Use specific version for production (e.g., `4.19.14`)
- Use `default` for latest MAS-supported version
- Use `rotate` for testing (version changes by day of week)

**Valid values**: 
- Specific version: `4.19`, `4.19.14`
- Alias: `default` (newest MAS-supported version)
- Alias: `rotate` (predetermined version by day, for testing)
- **ROKS format**: Must append `_openshift` (e.g., `4.19_openshift`, `4.19.14_openshift`)

**Impact**: Determines OpenShift version installed. Version must be compatible with MAS and available from the provider.

**Related variables**:
- `cluster_type`: ROKS requires `_openshift` suffix

**Note**: **IMPORTANT** - For ROKS (`cluster_type=roks`), version MUST include `_openshift` suffix. The `default` alias selects the newest MAS-supported version. The `rotate` alias is for testing only.

### ocp_storage_provider
Storage provider configuration for Fyre clusters.

- **Optional**
- Environment Variable: `OCP_STORAGE_PROVIDER`
- Default: None

**Purpose**: Configures NFS storage for Fyre clusters, creating an nfs-client storage class and reconfiguring the image registry.

**When to use**:
- Set to `nfs` for Fyre clusters to enable NFS storage
- Only applies when `cluster_type=fyre`
- Leave unset for other cluster types (ROKS, ROSA, IPI)

**Valid values**: `nfs` (for Fyre clusters only)

**Impact**: 
- `nfs`: Creates nfs-client storage class connected to infrastructure node, reconfigures image registry PVC to use NFS
- Unset: No storage configuration changes

**Related variables**:
- `cluster_type`: Must be `fyre` for this to have effect

**Note**: Only functional for Fyre clusters. When enabled, the existing image registry PVC is deleted and recreated with NFS storage. NFS storage class supports both ReadWriteOnce (RWO) and ReadWriteMany (RWX) access modes.


Role Variables - GPU Node Support
-------------------------------------------------------------------------------
### ocp_provision_gpu
Enable GPU worker nodes during provisioning.

- **Optional**
- Environment Variable: `OCP_PROVISION_GPU`
- Default: `false`

**Purpose**: Controls whether GPU-enabled worker nodes are provisioned with the cluster. Required for GPU-intensive applications like MAS Visual Inspection (MVI).

**When to use**:
- Set to `true` for MAS Visual Inspection deployments
- Set to `true` for other GPU-intensive workloads
- Leave as `false` (default) for standard deployments
- Currently only supported for ROKS clusters

**Valid values**: `true`, `false`

**Impact**: 
- `true`: Provisions GPU worker pool with specified number of GPU nodes
- `false`: No GPU nodes provisioned (standard cluster)

**Related variables**:
- `gpu_workerpool_name`: Name of GPU worker pool
- `gpu_workers`: Number of GPU nodes to provision
- `cluster_type`: Must be `roks` for GPU support

**Note**: GPU support is currently only available for ROKS clusters. GPU nodes use mg4c.32x384.2xp100-GPU flavor with P100 GPUs.

### gpu_workerpool_name
Name for GPU worker pool.

- **Optional**
- Environment Variable: `GPU_WORKERPOOL_NAME`
- Default: `gpu`

**Purpose**: Specifies the name for the GPU worker pool to be created or modified in the cluster.

**When to use**:
- Use default (`gpu`) for new GPU deployments
- Set to existing pool name to modify rather than create new
- Only applies when `ocp_provision_gpu=true`

**Valid values**: String following worker pool naming conventions

**Impact**: Determines GPU worker pool name. Using an existing name modifies that pool; using a new name creates a new pool.

**Related variables**:
- `ocp_provision_gpu`: Must be `true` for this to apply
- `gpu_workers`: Number of nodes in this pool
- `cluster_type`: Must be `roks`

**Note**: If a GPU worker pool already exists with this name, it will be modified rather than creating a duplicate. Use the existing name to avoid multiple GPU pools.

### gpu_workers
The number of GPU worker nodes that will be deploy in the cluster. The node created will have mg4c.32x384.2xp100-GPU flavor. This variable depends on `ocp_provision_gpu` and is currently supported on ROKS clusters only.

- Optional
- Environment Variable: `GPU_WORKERS`
- Default Value: `1`

### compute_node_count
The number of compute nodes (i.e. worker nodes) allocate to the OCP cluster.

- Optional
- Environment Variable: `COMPUTE_NODE_COUNT`
- Default Value: `3`

### controlplane_node_count
The number of control plane nodes (i.e. master nodes) allocate to the OCP cluster.

- Optional
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
The APIKey to be used by ibmcloud login comand.

- **Required** if `cluster_type = roks`
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
Password to set up for the `cluster-admin` user account on the OCP instance.  You will need this to log onto the cluster after it is provisioned. If this is not set then a password is auto-generated.

- **Optional** if `cluster_type = rosa`.
- Environment Variable: `ROSA_CLUSTER_ADMIN_PASSWORD`
- Default Value: None

### rosa_compute_nodes
Number of compute nodes to deploy in the cluster.

- Optional
- Environment Variable: `ROSA_COMPUTE_NODES`
- Default Value: `3`

### rosa_compute_machine_type
Worker nodes machine

- Optional
- Environment Variable: `ROSA_COMPUTE_MACHINE_TYPE`
- Default Value: `m5.4xlarge`

### rosa_config_dir
Config directory to hold the rosa-{{cluster_name}}-details.yaml file that contains the api endpoint and cluster-admin details

- Optional
- Environment Variable: `ROSA_CONFIG_DIR`
- Default Value: None


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

### fyre_site
Provide a site in Fyre where cluster will be provisioned

- Optional
- Environment Variable: `FYRE_SITE`
- Default Value: `svl`

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
- Default Value: `medium`

### fyre_worker_count
The number of worker nodes to provision in the cluster.

- **Required** when `cluster_type = fyre` and `fyre_quota_type = product_group`.
- Environment Variable: `FYRE_WORKER_COUNT`
- Default Value: `2`

### fyre_worker_cpu
The amount of CPU to assign to each worker node (maximum value supported by FYRE 16).

- **Required** when `cluster_type = fyre` and `fyre_quota_type = product_group`.
- Environment Variable: `FYRE_WORKER_CPU`
- Default Value: `8`

### fyre_worker_memory
The amount of memory to assign to each worker node (maximum value supported by FYRE 64).

- **Required** when `cluster_type = fyre` and `fyre_quota_type = product_group`.
- Environment Variable: `FYRE_WORKER_MEMORY`
- Default Value: `32`

### fyre_worker_additional_disks
The size of additional disks in Gb added to each worker node, defined in a comma-seperated list, e.g. `400,400` will add two 400gb disks to each worker node. By default no additional disks will be attached.

- Optional
- Environment Variable: `FYRE_WORKER_ADDITIONAL_DISKS`
- Default Value: `None`

### fyre_nfs_image_registry_size
Defines the image registry storage size when configured to use NFS. The size allocated cannot be superior of storage available in the Fyre Infrastructure node.

- Optional
- Environment Variable: `FYRE_NFS_IMAGE_REGISTRY_SIZE`
- Default: `100Gi`

### enable_ipv6
Enable IPv6. This is for Fyre at RTP site only.

- Environment Variable: `ENABLE_IPV6`
- Default: False

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

- **Required** when `cluster_type = ipi`
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

### ipi_rootvolume_size
The size of root volume in GiB.

- Optional when `cluster_type = ipi`
- Environment variable: `IPI_ROOTVOLUME_SIZE`

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
