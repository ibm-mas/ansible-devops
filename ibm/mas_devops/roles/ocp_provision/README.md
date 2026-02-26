# ocp_provision
Provision OCP cluster on IBM Cloud ROKS, ROSA, or DevIT Fyre.

Fyre clusters will be automatically reconfigured to enable NFS storage.  By default this is made available via the `nfs-client` storage class and supports both `ReadWriteOnce` and `ReadWriteMany` access modes.  The `image-registry-storage` PVC used by the OpenShift image registry component will also be reconfigured to use this storage class.


## Role Variables - General
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

**Note**: Fyre clusters automatically configure NFS storage. ROKS requires version format like `4.20_openshift`.

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
- Use specific version for production (e.g., `4.20.8`)
- Use `default` for latest MAS-supported version
- Use `rotate` for testing (version changes by day of week)

**Valid values**: 
- Specific version: `4.20`, `4.20.8`
- Alias: `default` (newest MAS-supported version)
- Alias: `rotate` (predetermined version by day, for testing)
- **ROKS format**: Must append `_openshift` (e.g., `4.20_openshift`, `4.20.8_openshift`)

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


## Role Variables - GPU Node Support
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
Number of GPU worker nodes to provision in the cluster.

- **Optional**
- Environment Variable: `GPU_WORKERS`
- Default: `1`

**Purpose**: Specifies how many GPU-enabled worker nodes to provision in the GPU worker pool. Each node uses mg4c.32x384.2xp100-GPU flavor with P100 GPUs.

**When to use**:
- Use default (1) for minimal GPU deployments or testing
- Increase for production MAS Visual Inspection deployments
- Scale based on GPU workload requirements
- Only applies when `ocp_provision_gpu=true`

**Valid values**: Positive integer (e.g., `1`, `2`, `3`)

**Impact**: Determines the number of GPU nodes provisioned. More nodes provide more GPU capacity but increase costs.

**Related variables**:
- `ocp_provision_gpu`: Must be `true` for this to apply
- `gpu_workerpool_name`: Name of the pool containing these nodes
- `cluster_type`: Must be `roks` for GPU support

**Note**: GPU nodes use expensive hardware (P100 GPUs). Only provision what you need. Currently only supported on ROKS clusters.


## Role Variables - ROKS
The following variables are only used when `cluster_type = roks`.

### ibmcloud_apikey
IBM Cloud API key for authentication.

- **Required** (when `cluster_type=roks`)
- Environment Variable: `IBMCLOUD_APIKEY`
- Default: None

**Purpose**: Authenticates with IBM Cloud to provision and manage ROKS clusters. Used by the ibmcloud CLI for all cluster operations.

**When to use**:
- Always required for ROKS cluster provisioning
- Must have permissions to create clusters in the target resource group
- Obtain from IBM Cloud IAM (Identity and Access Management)

**Valid values**: IBM Cloud API key string (typically 40+ characters)

**Impact**: Without a valid API key, cluster provisioning will fail. The key must have appropriate IAM permissions for cluster creation.

**Related variables**:
- `ibmcloud_resourcegroup`: Resource group where cluster will be created
- `ibmcloud_endpoint`: IBM Cloud API endpoint to authenticate against

**Note**: Keep API keys secure. Use environment variables or secure vaults rather than hardcoding in playbooks. The key needs cluster creation permissions in the specified resource group.

### ibmcloud_endpoint
IBM Cloud API endpoint URL.

- **Optional**
- Environment Variable: `IBMCLOUD_ENDPOINT`
- Default: `https://cloud.ibm.com`

**Purpose**: Specifies the IBM Cloud API endpoint for authentication and cluster operations. Allows targeting different IBM Cloud environments.

**When to use**:
- Use default for standard IBM Cloud (public cloud)
- Override for IBM Cloud dedicated or private environments
- Change for testing against staging environments

**Valid values**: Valid IBM Cloud API endpoint URL

**Impact**: Determines which IBM Cloud environment is targeted for cluster provisioning.

**Related variables**:
- `ibmcloud_apikey`: API key used with this endpoint

**Note**: The default endpoint works for standard IBM Cloud deployments. Only change if you're using a dedicated or private IBM Cloud environment.

### ibmcloud_resourcegroup
IBM Cloud resource group for the cluster.

- **Optional**
- Environment Variable: `IBMCLOUD_RESOURCEGROUP`
- Default: `Default`

**Purpose**: Specifies which IBM Cloud resource group the ROKS cluster will be created in. Resource groups organize and manage access to IBM Cloud resources.

**When to use**:
- Use default (`Default`) for simple deployments
- Specify a different resource group for organizational separation
- Ensure the API key has access to the specified resource group

**Valid values**: Name of an existing IBM Cloud resource group

**Impact**: Cluster is created in the specified resource group. The API key must have permissions in this resource group.

**Related variables**:
- `ibmcloud_apikey`: Must have permissions in this resource group

**Note**: The resource group must exist before provisioning. The API key must have appropriate IAM permissions in the target resource group.

### roks_zone
IBM Cloud availability zone for cluster deployment.

- **Optional**
- Environment Variable: `ROKS_ZONE`
- Default: `dal10`

**Purpose**: Specifies the IBM Cloud availability zone where the ROKS cluster will be provisioned. Determines the physical location of cluster resources.

**When to use**:
- Use default (`dal10`) for Dallas datacenter
- Change based on geographic requirements or latency needs
- Consider data residency and compliance requirements

**Valid values**: Valid IBM Cloud zone identifier (e.g., `dal10`, `lon02`, `fra02`, `tok02`)

**Impact**: Determines cluster location, which affects latency, data residency, and available services.

**Related variables**:
- `roks_flavor`: Worker node flavors available vary by zone

**Note**: Not all zones support all worker node flavors. Verify flavor availability in your target zone. Zone selection affects network latency to your users and services.

### roks_flavor
Worker node machine type for ROKS cluster.

- **Optional**
- Environment Variable: `ROKS_FLAVOR`
- Default: `b3c.16x64.300gb`

**Purpose**: Specifies the machine type (flavor) for worker nodes in the ROKS cluster. Determines CPU, memory, and local storage for each worker node.

**When to use**:
- Use default (`b3c.16x64.300gb`) for standard MAS deployments (16 vCPU, 64GB RAM, 300GB storage)
- Increase for larger workloads or more applications
- Decrease for development/testing environments

**Valid values**: Valid IBM Cloud worker node flavor (e.g., `b3c.4x16`, `b3c.16x64.300gb`, `b3c.32x128`)

**Impact**: Determines worker node capacity. Affects cluster performance and cost. Larger flavors cost more but provide more resources.

**Related variables**:
- `roks_workers`: Number of nodes with this flavor
- `roks_zone`: Not all flavors available in all zones

**Note**: The default flavor (16 vCPU, 64GB RAM) is suitable for most MAS deployments. Verify flavor availability in your target zone. Consider total cluster capacity (flavor × worker count).

### roks_workers
Number of worker nodes in the ROKS cluster.

- **Optional**
- Environment Variable: `ROKS_WORKERS`
- Default: `3`

**Purpose**: Specifies how many worker nodes to provision in the ROKS cluster. Determines cluster capacity and high availability.

**When to use**:
- Use default (3) for standard high-availability deployments
- Increase for larger workloads or more applications
- Minimum 3 recommended for production (high availability)

**Valid values**: Positive integer, minimum 1 (3+ recommended for production)

**Impact**: Determines total cluster capacity (workers × flavor resources). More workers provide more capacity and better high availability but increase costs.

**Related variables**:
- `roks_flavor`: Machine type for each worker
- `ocp_provision_gpu`: Additional GPU workers can be added separately

**Note**: For production, use at least 3 workers for high availability. Total cluster capacity = worker count × flavor resources. Consider workload requirements when sizing.

### roks_flags
Additional flags for ROKS cluster creation.

- **Optional**
- Environment Variable: `ROKS_FLAGS`
- Default: None

**Purpose**: Allows passing additional command-line flags to the `ibmcloud ks cluster create` command for advanced cluster configuration.

**When to use**:
- Leave unset for standard deployments
- Use for advanced configurations not covered by other variables
- Consult IBM Cloud documentation for available flags

**Valid values**: Valid ibmcloud CLI flags (e.g., `--disable-public-service-endpoint`, `--pod-subnet`, `--service-subnet`)

**Impact**: Passes additional configuration options to cluster creation. Incorrect flags may cause provisioning to fail.

**Related variables**:
- All other ROKS variables: Flags supplement standard configuration

**Note**: Use with caution. Incorrect flags can cause provisioning failures. Consult IBM Cloud Kubernetes Service documentation for available options.


## Role Variables - ROSA
The following variables are only used when `cluster_type = rosa`.

### rosa_token
Red Hat OpenShift Service on AWS (ROSA) authentication token.

- **Required** (when `cluster_type=rosa`)
- Environment Variable: `ROSA_TOKEN`
- Default: None

**Purpose**: Authenticates with the ROSA service to provision and manage OpenShift clusters on AWS. Required for all ROSA cluster operations.

**When to use**:
- Always required for ROSA cluster provisioning
- Obtain from [OpenShift Cluster Manager](https://console.redhat.com/openshift/token/rosa/show#)
- Token must be valid and not expired

**Valid values**: ROSA API token string from Red Hat OpenShift Cluster Manager

**Impact**: Without a valid token, ROSA cluster provisioning will fail. Token must have permissions to create clusters.

**Related variables**:
- `cluster_name`: Name for the ROSA cluster
- `rosa_compute_nodes`: Number of worker nodes to provision

**Note**: Tokens expire periodically. Obtain a fresh token from the OpenShift Cluster Manager before provisioning. Keep tokens secure.

### rosa_cluster_admin_password
Password for the cluster-admin user account.

- **Optional**
- Environment Variable: `ROSA_CLUSTER_ADMIN_PASSWORD`
- Default: None (auto-generated)

**Purpose**: Sets the password for the `cluster-admin` user account on the ROSA cluster. Used to log into the cluster after provisioning.

**When to use**:
- Set to specify a known password for cluster access
- Leave unset to auto-generate a secure password
- Auto-generated password is saved to config directory

**Valid values**: String meeting OpenShift password requirements (typically 8+ characters)

**Impact**:
- When set: Uses specified password for cluster-admin account
- When unset: Auto-generates a secure password and saves it to config

**Related variables**:
- `rosa_config_dir`: Location where auto-generated password is saved

**Note**: If not set, the auto-generated password is saved in the rosa config file. Keep passwords secure. Consider using auto-generation for better security.

### rosa_compute_nodes
Number of compute (worker) nodes in the ROSA cluster.

- **Optional**
- Environment Variable: `ROSA_COMPUTE_NODES`
- Default: `3`

**Purpose**: Specifies how many worker nodes to provision in the ROSA cluster. Determines cluster capacity and high availability.

**When to use**:
- Use default (3) for standard high-availability deployments
- Increase for larger workloads or more applications
- Minimum 2 required, 3+ recommended for production

**Valid values**: Positive integer, minimum 2 (3+ recommended for production)

**Impact**: Determines total cluster capacity. More nodes provide more capacity and better high availability but increase AWS costs.

**Related variables**:
- `rosa_compute_machine_type`: Machine type for each worker node

**Note**: For production, use at least 3 workers for high availability. Total cluster capacity = worker count × machine type resources. ROSA clusters run on AWS infrastructure.

### rosa_compute_machine_type
AWS machine type for ROSA worker nodes.

- **Optional**
- Environment Variable: `ROSA_COMPUTE_MACHINE_TYPE`
- Default: `m5.4xlarge`

**Purpose**: Specifies the AWS EC2 instance type for worker nodes in the ROSA cluster. Determines CPU, memory, and network capacity for each worker.

**When to use**:
- Use default (`m5.4xlarge`: 16 vCPU, 64GB RAM) for standard MAS deployments
- Increase for larger workloads (e.g., `m5.8xlarge`, `m5.12xlarge`)
- Decrease for development/testing (e.g., `m5.2xlarge`)

**Valid values**: Valid AWS EC2 instance type (e.g., `m5.2xlarge`, `m5.4xlarge`, `m5.8xlarge`, `m5.12xlarge`)

**Impact**: Determines worker node capacity. Affects cluster performance and AWS costs. Larger instance types cost more but provide more resources.

**Related variables**:
- `rosa_compute_nodes`: Number of nodes with this instance type

**Note**: The default m5.4xlarge (16 vCPU, 64GB RAM) is suitable for most MAS deployments. Consider total cluster capacity (instance type × node count). Verify instance type availability in your AWS region.

### rosa_config_dir
Directory for storing ROSA cluster configuration files.

- **Optional**
- Environment Variable: `ROSA_CONFIG_DIR`
- Default: None

**Purpose**: Specifies the directory where ROSA cluster configuration files are saved, including the `rosa-{{cluster_name}}-details.yaml` file containing API endpoint and cluster-admin credentials.

**When to use**:
- Set to save cluster details to a specific location
- Leave unset to skip saving configuration files
- Useful for automation and cluster access management

**Valid values**: Absolute filesystem path (e.g., `/tmp/rosa-config`, `~/rosa-clusters`)

**Impact**:
- When set: Cluster details (API endpoint, credentials) are saved to this directory
- When unset: Configuration files are not saved (must retrieve details manually)

**Related variables**:
- `rosa_cluster_admin_password`: Auto-generated password saved here if not specified
- `cluster_name`: Used in config filename

**Note**: The config file contains sensitive information (cluster-admin password). Ensure the directory has appropriate permissions. File format: `rosa-{{cluster_name}}-details.yaml`.


## Role Variables - FYRE
The following variables are only used when `cluster_type = fyre`.

### fyre_username
Fyre username for authentication.

- **Required** (when `cluster_type=fyre`)
- Environment Variable: `FYRE_USERNAME`
- Default: None

**Purpose**: Authenticates with the IBM DevIT Fyre API to provision and manage OpenShift clusters on Fyre infrastructure.

**When to use**:
- Always required for Fyre cluster provisioning
- Must be a valid Fyre account username
- Used for internal IBM development and testing

**Valid values**: Valid Fyre username (IBM intranet ID)

**Impact**: Without valid credentials, Fyre cluster provisioning will fail.

**Related variables**:
- `fyre_apikey`: API key paired with this username

**Note**: Fyre is an internal IBM development platform. Access requires IBM credentials and appropriate permissions.

### fyre_apikey
Fyre API key for authentication.

- **Required** (when `cluster_type=fyre`)
- Environment Variable: `FYRE_APIKEY`
- Default: None

**Purpose**: Authenticates with the Fyre API for cluster provisioning operations. Paired with Fyre username for authentication.

**When to use**:
- Always required for Fyre cluster provisioning
- Obtain from Fyre portal
- Keep secure and rotate regularly

**Valid values**: Valid Fyre API key string

**Impact**: Without a valid API key, Fyre cluster provisioning will fail.

**Related variables**:
- `fyre_username`: Username paired with this API key

**Note**: Keep API keys secure. Obtain from the Fyre portal. Keys may expire and need renewal.

### fyre_quota_type
Fyre quota type for cluster provisioning.

- **Required** (when `cluster_type=fyre`)
- Environment Variable: `FYRE_QUOTA_TYPE`
- Default: `quick_burn`

**Purpose**: Specifies which type of Fyre quota to use for cluster provisioning. Determines billing method and available configuration options.

**When to use**:
- Use `quick_burn` (default) for pre-defined cluster sizes (faster, simpler)
- Use `product_group` for custom cluster configurations (more control)
- Choice affects which other variables are required

**Valid values**: `quick_burn`, `product_group`

**Impact**:
- `quick_burn`: Uses pre-defined cluster sizes, requires `fyre_cluster_size`
- `product_group`: Allows custom sizing, requires `fyre_worker_count`, `fyre_worker_cpu`, `fyre_worker_memory`

**Related variables**:
- `fyre_cluster_size`: Required when `quick_burn`
- `fyre_worker_count`, `fyre_worker_cpu`, `fyre_worker_memory`: Required when `product_group`
- `fyre_product_id`: Required for both types

**Note**: Quick burn is simpler but less flexible. Product group allows custom sizing but requires more configuration.

### fyre_product_id
Product ID for Fyre accounting.

- **Required** (when `cluster_type=fyre`)
- Environment Variable: `FYRE_PRODUCT_ID`
- Default: None

**Purpose**: Associates the Fyre cluster with a product ID for internal IBM accounting and cost tracking purposes.

**When to use**:
- Always required for Fyre cluster provisioning
- Obtain from your IBM product team or manager
- Used for internal cost allocation

**Valid values**: Valid IBM product ID

**Impact**: Cluster costs are charged to this product ID. Incorrect ID may cause provisioning to fail or incorrect billing.

**Related variables**:
- `fyre_quota_type`: Product ID required for both quota types

**Note**: Contact your IBM product team or manager to obtain the correct product ID for your project.

### fyre_site
Fyre datacenter site location.

- **Optional**
- Environment Variable: `FYRE_SITE`
- Default: `svl`

**Purpose**: Specifies which Fyre datacenter site to provision the cluster in. Determines physical location and network connectivity.

**When to use**:
- Use default (`svl` - San Jose/Silicon Valley) for most cases
- Change based on geographic requirements or network proximity
- Consider latency to your development location

**Valid values**: Valid Fyre site code (e.g., `svl`, `rtp`, `raleigh`)

**Impact**: Determines cluster location, which affects network latency and available resources.

**Related variables**:
- `enable_ipv6`: IPv6 only available at RTP site

**Note**: Not all sites support all features. SVL is the default and most commonly used site.

### fyre_cluster_description
Description for the Fyre cluster.

- **Optional**
- Environment Variable: `FYRE_CLUSTER_DESCRIPTION`
- Default: None

**Purpose**: Provides a human-readable description for the Fyre cluster. Helps identify cluster purpose in Fyre portal.

**When to use**:
- Set to document cluster purpose (e.g., "MAS 9.0 testing", "Development cluster")
- Leave unset for unnamed clusters
- Useful for tracking and managing multiple clusters

**Valid values**: Any descriptive string

**Impact**: Description appears in Fyre portal. No functional impact on cluster.

**Related variables**:
- `cluster_name`: Cluster identifier

**Note**: Good descriptions help manage multiple clusters. Include purpose, owner, or project information.

### ocp_fips_enabled
Enable FIPS mode for the cluster.

- **Optional**
- Environment Variable: `OCP_FIPS_ENABLED`
- Default: `false`

**Purpose**: Controls whether the OpenShift cluster is provisioned with FIPS (Federal Information Processing Standards) 140-2 cryptographic mode enabled.

**When to use**:
- Set to `true` for compliance with FIPS 140-2 requirements
- Set to `true` for government or regulated environments
- Leave as `false` (default) for standard deployments

**Valid values**: `true`, `false`

**Impact**:
- `true`: Cluster uses FIPS-validated cryptographic modules (required for some compliance)
- `false`: Standard cryptography (better performance)

**Related variables**:
- `cluster_type`: FIPS support varies by cluster type

**Note**: FIPS mode may impact performance. Only enable if required for compliance. Cannot be changed after cluster creation.

### fyre_cluster_size
Pre-defined Fyre cluster size.

- **Required** (when `cluster_type=fyre` and `fyre_quota_type=quick_burn`)
- Environment Variable: `FYRE_CLUSTER_SIZE`
- Default: `medium`

**Purpose**: Specifies which pre-defined cluster size to use when provisioning with quick_burn quota. Determines worker node count and resources.

**When to use**:
- Only applies when `fyre_quota_type=quick_burn`
- Use `medium` (default) for standard development/testing
- Use `small` for minimal testing
- Use `large` for more intensive workloads

**Valid values**: Fyre pre-defined sizes (e.g., `small`, `medium`, `large`)

**Impact**: Determines cluster capacity based on Fyre's pre-defined configurations. Cannot customize individual resources.

**Related variables**:
- `fyre_quota_type`: Must be `quick_burn` for this to apply

**Note**: Quick burn sizes are pre-defined by Fyre. For custom sizing, use `fyre_quota_type=product_group` instead.

### fyre_worker_count
Number of worker nodes for custom Fyre clusters.

- **Required** (when `cluster_type=fyre` and `fyre_quota_type=product_group`)
- Environment Variable: `FYRE_WORKER_COUNT`
- Default: `2`

**Purpose**: Specifies the number of worker nodes to provision when using product_group quota with custom sizing.

**When to use**:
- Only applies when `fyre_quota_type=product_group`
- Use 2+ for development/testing
- Use 3+ for high availability testing

**Valid values**: Positive integer (typically 2-10)

**Impact**: Determines cluster capacity. More workers provide more resources but consume more quota.

**Related variables**:
- `fyre_quota_type`: Must be `product_group` for this to apply
- `fyre_worker_cpu`, `fyre_worker_memory`: Resources per worker

**Note**: Total cluster capacity = worker count × (CPU + memory per worker). Consider quota limits.

### fyre_worker_cpu
CPU cores per worker node for custom Fyre clusters.

- **Required** (when `cluster_type=fyre` and `fyre_quota_type=product_group`)
- Environment Variable: `FYRE_WORKER_CPU`
- Default: `8`

**Purpose**: Specifies the number of CPU cores to assign to each worker node when using product_group quota.

**When to use**:
- Only applies when `fyre_quota_type=product_group`
- Use default (8) for standard workloads
- Increase for CPU-intensive testing

**Valid values**: Positive integer, maximum 16 (Fyre limit)

**Impact**: Determines CPU capacity per worker. More CPUs provide better performance but consume more quota.

**Related variables**:
- `fyre_quota_type`: Must be `product_group` for this to apply
- `fyre_worker_count`: Number of workers with this CPU allocation
- `fyre_worker_memory`: Memory paired with CPU

**Note**: Maximum 16 CPUs per worker (Fyre limitation). Total cluster CPUs = worker count × CPU per worker.

### fyre_worker_memory
Memory (GB) per worker node for custom Fyre clusters.

- **Required** (when `cluster_type=fyre` and `fyre_quota_type=product_group`)
- Environment Variable: `FYRE_WORKER_MEMORY`
- Default: `32`

**Purpose**: Specifies the amount of memory (in GB) to assign to each worker node when using product_group quota.

**When to use**:
- Only applies when `fyre_quota_type=product_group`
- Use default (32GB) for standard workloads
- Increase for memory-intensive testing

**Valid values**: Positive integer, maximum 64 (Fyre limit)

**Impact**: Determines memory capacity per worker. More memory supports larger workloads but consumes more quota.

**Related variables**:
- `fyre_quota_type`: Must be `product_group` for this to apply
- `fyre_worker_count`: Number of workers with this memory allocation
- `fyre_worker_cpu`: CPU paired with memory

**Note**: Maximum 64GB per worker (Fyre limitation). Total cluster memory = worker count × memory per worker.

### fyre_worker_additional_disks
Additional disk sizes for Fyre worker nodes.

- **Optional**
- Environment Variable: `FYRE_WORKER_ADDITIONAL_DISKS`
- Default: None

**Purpose**: Specifies additional disks to attach to each worker node. Useful for testing storage configurations or providing extra capacity.

**When to use**:
- Leave unset for standard deployments (no additional disks)
- Set to add extra storage for testing or specific workloads
- Use comma-separated list for multiple disks

**Valid values**: Comma-separated list of disk sizes in GB (e.g., `400`, `400,400`, `200,300,400`)

**Impact**: Each specified disk is attached to every worker node. Increases storage capacity but consumes more quota.

**Related variables**:
- `fyre_worker_count`: Additional disks added to each worker

**Note**: Example: `400,400` adds two 400GB disks to each worker. Total additional storage = disk sizes × worker count.

### fyre_nfs_image_registry_size
NFS storage size for OpenShift image registry.

- **Optional**
- Environment Variable: `FYRE_NFS_IMAGE_REGISTRY_SIZE`
- Default: `100Gi`

**Purpose**: Specifies the size of NFS storage allocated for the OpenShift image registry when NFS storage is configured on Fyre clusters.

**When to use**:
- Use default (100Gi) for most deployments
- Increase for clusters with many container images
- Only applies when `ocp_storage_provider=nfs`

**Valid values**: Kubernetes storage size (e.g., `50Gi`, `100Gi`, `200Gi`)

**Impact**: Determines image registry storage capacity. Size cannot exceed available storage on Fyre infrastructure node.

**Related variables**:
- `ocp_storage_provider`: Must be `nfs` for this to apply

**Note**: Size is limited by available storage on the Fyre infrastructure node. Image registry stores all container images used in the cluster.

### enable_ipv6
Enable IPv6 networking for Fyre cluster.

- **Optional**
- Environment Variable: `ENABLE_IPV6`
- Default: `false`

**Purpose**: Enables IPv6 networking for the Fyre cluster. Only supported at the RTP (Raleigh) Fyre site.

**When to use**:
- Set to `true` for IPv6 testing
- Only works at RTP site
- Leave as `false` (default) for standard IPv4 networking

**Valid values**: `true`, `false`

**Impact**:
- `true`: Cluster uses IPv6 networking (RTP site only)
- `false`: Standard IPv4 networking

**Related variables**:
- `fyre_site`: Must be `rtp` for IPv6 support

**Note**: **IMPORTANT** - IPv6 is only supported at the RTP (Raleigh) Fyre site. Will fail at other sites.

## Role Variables - IPI
These variables are only used when `cluster_type = ipi`.

!!! note
    IPI stands for **Installer Provisioned Infrastructure**.  OpenShift offers two possible deployment methods: IPI and UPI (User Provisioned Infrastructure). The difference is the degree of automation and customization. IPI will not only deploy OpenShift but also all infrastructure components and configurations.

### ipi_platform
Cloud platform for IPI cluster deployment.

- **Optional**
- Environment Variable: `IPI_PLATFORM`
- Default: `aws`

**Purpose**: Specifies which cloud platform to use for Installer-Provisioned Infrastructure (IPI) deployment. Determines infrastructure provider and configuration requirements.

**When to use**:
- Use default (`aws`) for AWS deployments
- Set to `gcp` for Google Cloud Platform deployments
- Other platforms supported by openshift-install may work but are untested

**Valid values**: `aws`, `gcp` (other openshift-install platforms may work)

**Impact**: Determines which cloud provider is used and which provider-specific variables are required.

**Related variables**:
- `aws_access_key_id`, `aws_secret_access_key`: Required when `aws`
- `gcp_service_account_file`, `ipi_gcp_projectid`: Required when `gcp`

**Note**: AWS and GCP are tested and supported. Other platforms supported by openshift-install may work but have not been specifically tested.

### ipi_region
Cloud platform region for cluster deployment.

- **Optional**
- Environment Variable: `IPI_REGION`
- Default: `us-east-1`

**Purpose**: Specifies the cloud platform region where the IPI cluster will be deployed. Determines physical location and available services.

**When to use**:
- Use default (`us-east-1`) for AWS US East region
- Change based on geographic requirements or latency needs
- Ensure region supports required instance types

**Valid values**: Valid region for the selected platform (e.g., `us-east-1`, `us-west-2`, `eu-west-1` for AWS)

**Impact**: Determines cluster location, which affects latency, data residency, and service availability.

**Related variables**:
- `ipi_platform`: Region must be valid for this platform

**Note**: Not all regions support all instance types. Verify instance type availability in your target region.

### ipi_base_domain
Base DNS domain for the cluster.

- **Required** (when `cluster_type=ipi`)
- Environment Variable: `IPI_BASE_DOMAIN`
- Default: None

**Purpose**: Specifies the base DNS domain for the OpenShift cluster. Used to construct cluster URLs and DNS records.

**When to use**:
- Always required for IPI cluster provisioning
- Must be a domain you control
- DNS must be properly configured for the domain

**Valid values**: Valid DNS domain name (e.g., `example.com`, `ocp.mycompany.com`)

**Impact**: Cluster URLs will be subdomains of this base domain (e.g., `api.clustername.example.com`). DNS must be configured to route to the cluster.

**Related variables**:
- `cluster_name`: Combined with base domain for cluster URLs

**Note**: You must have control over this domain and ability to configure DNS records. The openshift-install process will create DNS records in this domain.

### ipi_pull_secret_file
Path to Red Hat OpenShift pull secret file.

- **Required** (when `cluster_type=ipi`)
- Environment Variable: `IPI_PULL_SECRET_FILE`
- Default: None

**Purpose**: Specifies the location of the file containing your Red Hat OpenShift pull secret. Required to pull OpenShift container images during installation.

**When to use**:
- Always required for IPI cluster provisioning
- Obtain from [Red Hat Hybrid Cloud Console](https://console.redhat.com/openshift/install/metal/user-provisioned)
- Must be a valid, non-expired pull secret

**Valid values**: Absolute path to pull secret JSON file

**Impact**: Without a valid pull secret, cluster installation will fail when attempting to pull container images.

**Related variables**:
- None

**Note**: Download your pull secret from the Red Hat Hybrid Cloud Console. Keep the file secure as it contains authentication credentials.

### ipi_dir
Working directory for IPI installation.

- **Optional**
- Environment Variable: `IPI_DIR`
- Default: `~/openshift-install`

**Purpose**: Specifies the working directory for the IPI installation process. Contains the openshift-install executable, configuration files, and generated logs.

**When to use**:
- Use default for standard installations
- Change to specify a different working location
- Useful for organizing multiple cluster installations

**Valid values**: Absolute filesystem path

**Impact**: All installation files, configs, and logs are stored in this directory. Directory must be writable.

**Related variables**:
- `cluster_name`: Used in subdirectory structure

**Note**: The directory will contain sensitive information (kubeconfig, credentials). Ensure appropriate permissions. Preserve this directory for cluster management and troubleshooting.

### sshKey
Public SSH key for cluster node access.

- **Optional**
- Environment Variable: `SSH_PUB_KEY`
- Default: None

**Purpose**: Specifies the public SSH key to be installed on OpenShift cluster nodes. Enables SSH access to nodes via bastion host.

**When to use**:
- Set to enable SSH access to cluster nodes for troubleshooting
- Leave unset if SSH access is not needed
- Useful for debugging and advanced cluster management

**Valid values**: Valid SSH public key string (e.g., `ssh-rsa AAAAB3...`)

**Impact**:
- When set: SSH key is installed on all cluster nodes
- When unset: No SSH access to nodes (standard for managed clusters)

**Related variables**:
- None

**Note**: SSH access to nodes is typically not needed for normal operations. Only set if you need direct node access for troubleshooting.

### ipi_controlplane_type
Machine type for control plane nodes.

- **Optional**
- Environment Variable: `IPI_CONTROLPLANE_TYPE`
- Default: `m5.4xlarge`

**Purpose**: Specifies the machine type for control plane (master) nodes in the IPI cluster. Determines CPU, memory, and network capacity for control plane.

**When to use**:
- Use default (`m5.4xlarge`: 16 vCPU, 64GB RAM) for standard deployments
- Increase for very large clusters (many nodes or workloads)
- Decrease for small test clusters (not recommended for production)

**Valid values**: Valid machine type for the selected platform (e.g., `m5.2xlarge`, `m5.4xlarge`, `m5.8xlarge` for AWS)

**Impact**: Determines control plane capacity. Affects cluster management performance and costs. Undersized control plane can impact cluster stability.

**Related variables**:
- `ipi_controlplane_replicas`: Number of nodes with this type
- `ipi_platform`: Machine type must be valid for this platform

**Note**: Control plane nodes run cluster management services. Don't undersize for production. The default m5.4xlarge is suitable for most deployments.

### ipi_controlplane_replicas
Number of control plane (master) nodes.

- **Optional**
- Environment Variable: `IPI_CONTROLPLANE_REPLICAS`
- Default: `3`

**Purpose**: Specifies the number of control plane (master) nodes to provision. Determines cluster management high availability.

**When to use**:
- Use default (3) for production (high availability)
- Must be odd number (1, 3, 5) for etcd quorum
- Never use 1 for production (no high availability)

**Valid values**: Odd positive integer (1, 3, 5, 7), 3 recommended for production

**Impact**: Determines control plane high availability. 3 nodes provide HA with one node failure tolerance.

**Related variables**:
- `ipi_controlplane_type`: Machine type for each control plane node

**Note**: **IMPORTANT** - Must be an odd number for etcd quorum. Use 3 for production (HA). Using 1 provides no high availability.

### ipi_compute_type
Machine type for compute (worker) nodes.

- **Optional**
- Environment Variable: `IPI_COMPUTE_TYPE`
- Default: `m5.4xlarge`

**Purpose**: Specifies the machine type for compute (worker) nodes in the IPI cluster. Determines CPU, memory, and network capacity for workloads.

**When to use**:
- Use default (`m5.4xlarge`: 16 vCPU, 64GB RAM) for standard MAS deployments
- Increase for larger workloads (e.g., `m5.8xlarge`, `m5.12xlarge`)
- Decrease for development/testing (e.g., `m5.2xlarge`)

**Valid values**: Valid machine type for the selected platform (e.g., `m5.2xlarge`, `m5.4xlarge`, `m5.8xlarge` for AWS)

**Impact**: Determines worker node capacity. Affects workload performance and costs. Larger types cost more but provide more resources.

**Related variables**:
- `ipi_compute_replicas`: Number of nodes with this type
- `ipi_platform`: Machine type must be valid for this platform

**Note**: The default m5.4xlarge (16 vCPU, 64GB RAM) is suitable for most MAS deployments. Consider total cluster capacity (type × replicas).

### ipi_compute_replicas
Number of compute (worker) nodes.

- **Optional**
- Environment Variable: `IPI_COMPUTE_REPLICAS`
- Default: `3`

**Purpose**: Specifies the number of compute (worker) nodes to provision. Determines cluster workload capacity and high availability.

**When to use**:
- Use default (3) for standard high-availability deployments
- Increase for larger workloads or more applications
- Minimum 2 required, 3+ recommended for production

**Valid values**: Positive integer, minimum 2 (3+ recommended for production)

**Impact**: Determines total cluster capacity. More nodes provide more capacity and better high availability but increase costs.

**Related variables**:
- `ipi_compute_type`: Machine type for each worker node

**Note**: For production, use at least 3 workers for high availability. Total cluster capacity = worker count × machine type resources.

### ipi_rootvolume_size
Root volume size for cluster nodes.

- **Optional**
- Environment Variable: `IPI_ROOTVOLUME_SIZE`
- Default: Platform default (typically 120GB)

**Purpose**: Specifies the size of the root volume (in GiB) for cluster nodes. Determines available disk space for OS, container images, and ephemeral storage.

**When to use**:
- Leave unset to use platform default (typically sufficient)
- Increase for clusters with many container images
- Increase for workloads with high ephemeral storage needs

**Valid values**: Positive integer (GiB), e.g., `120`, `200`, `500`

**Impact**: Larger volumes provide more disk space but increase costs. Insufficient space can cause node issues.

**Related variables**:
- None

**Note**: Platform defaults are typically sufficient. Only increase if you have specific requirements for more disk space.

## Role Variables - AWS
The following variables are only used when `cluster_type = ipi` and `ipi_platform = aws`.

### aws_access_key_id
AWS access key ID for authentication.

- **Required** (when `cluster_type=ipi` and `ipi_platform=aws`)
- Environment Variable: `AWS_ACCESS_KEY_ID`
- Default: None

**Purpose**: Authenticates with AWS to provision IPI cluster infrastructure. Must have permissions to create VPCs, instances, load balancers, and other AWS resources.

**When to use**:
- Always required for AWS IPI cluster provisioning
- Must be associated with IAM user or role with cluster creation permissions
- Obtain from AWS IAM

**Valid values**: AWS access key ID string (typically 20 characters, starts with `AKIA`)

**Impact**: Without valid credentials with appropriate permissions, cluster provisioning will fail.

**Related variables**:
- `aws_secret_access_key`: Secret key paired with this access key ID

**Note**: The IAM user/role must have extensive permissions (VPC, EC2, ELB, Route53, IAM, etc.). Consider using a dedicated IAM user for cluster provisioning.

### aws_secret_access_key
AWS secret access key for authentication.

- **Required** (when `cluster_type=ipi` and `ipi_platform=aws`)
- Environment Variable: `AWS_SECRET_ACCESS_KEY`
- Default: None

**Purpose**: Authenticates with AWS to provision IPI cluster infrastructure. Paired with AWS access key ID for authentication.

**When to use**:
- Always required for AWS IPI cluster provisioning
- Must correspond to the provided access key ID
- Keep secure and rotate regularly

**Valid values**: AWS secret access key string (typically 40 characters)

**Impact**: Without valid credentials, cluster provisioning will fail.

**Related variables**:
- `aws_access_key_id`: Access key ID paired with this secret key

**Note**: Keep secret keys secure. Never commit to version control. Use environment variables or secure vaults. Rotate keys regularly.

## Role Variables - GCP
The following variables are only used when `cluster_type = ipi` and `ipi_platform = gcp`.

### gcp_service_account_file
Path to GCP service account credentials file.

- **Required** (when `cluster_type=ipi` and `ipi_platform=gcp`)
- Environment Variable: `GOOGLE_APPLICATION_CREDENTIALS`
- Default: None

**Purpose**: Authenticates with Google Cloud Platform to provision IPI cluster infrastructure. Service account must have permissions to create instances and networking resources.

**When to use**:
- Always required for GCP IPI cluster provisioning
- Must be a valid service account JSON key file
- Service account must have cluster creation permissions

**Valid values**: Absolute path to GCP service account JSON key file

**Impact**: Without valid credentials with appropriate permissions, cluster provisioning will fail.

**Related variables**:
- `ipi_gcp_projectid`: GCP project where cluster will be created

**Note**: The service account must have extensive permissions (Compute, Networking, IAM, etc.). Download the JSON key file from GCP IAM. Keep the file secure.

### ipi_gcp_projectid
GCP project ID for cluster deployment.

- **Required** (when `cluster_type=ipi` and `ipi_platform=gcp`)
- Environment Variable: `GOOGLE_PROJECTID`
- Default: None

**Purpose**: Specifies the GCP project where the IPI cluster will be deployed. All cluster resources are created in this project.

**When to use**:
- Always required for GCP IPI cluster provisioning
- Must be a valid, existing GCP project
- Service account must have permissions in this project

**Valid values**: Valid GCP project ID string

**Impact**: Cluster resources are created in this project. Costs are billed to this project.

**Related variables**:
- `gcp_service_account_file`: Service account must have permissions in this project

**Note**: The project must exist before provisioning. Ensure the service account has appropriate permissions in the project. All cluster costs are billed to this project.


## Example Playbook

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

## License

EPL-2.0
