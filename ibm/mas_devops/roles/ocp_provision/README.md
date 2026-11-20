# ocp_provision
Provision OCP cluster on IBM Cloud ROKS, ROSA, or DevIT Fyre.

Fyre clusters will be automatically reconfigured to enable NFS storage.  By default this is made available via the `nfs-client` storage class and supports both `ReadWriteOnce` and `ReadWriteMany` access modes.  The `image-registry-storage` PVC used by the OpenShift image registry component will also be reconfigured to use this storage class.

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`cluster_type`](#cluster_type) | Yes | None |
| [`cluster_name`](#cluster_name) | Yes | None |
| [`ocp_version`](#ocp_version) | Yes | None |
| [`ocp_fips_enabled`](#ocp_fips_enabled) | No | `false` |
| [`ocp_storage_provider`](#ocp_storage_provider) | No | None |
| [`ocp_provision_gpu`](#ocp_provision_gpu) | No | `false` |
| [`gpu_workerpool_name`](#gpu_workerpool_name) | No | `gpu` |
| [`gpu_workers`](#gpu_workers) | No | `1` |
| [`gpu_flavor`](#gpu_flavor) | No | `gx2.8x64.v100` |
| [`ibmcloud_apikey`](#ibmcloud_apikey) | Conditional | None |
| [`ibmcloud_endpoint`](#ibmcloud_endpoint) | No | `https://cloud.ibm.com` |
| [`ibmcloud_resourcegroup`](#ibmcloud_resourcegroup) | No | `Default` |
| [`ibmcloud_region`](#ibmcloud_region) | Conditional | None |
| [`roks_zone`](#roks_zone) | No | `dal10` |
| [`roks_flavor`](#roks_flavor) | No | `b3c.16x64.300gb` |
| [`roks_workers`](#roks_workers) | No | `3` |
| [`roks_flags`](#roks_flags) | No | `''` |
| [`roks_vpc_name`](#roks_vpc_name) | No | `cluster_name` |
| [`roks_vpc_id`](#roks_vpc_id) | No | None |
| [`roks_subnet_id`](#roks_subnet_id) | No | None |
| [`roks_cos_instance_crn`](#roks_cos_instance_crn) | No | None |
| [`roks_secondary_storage`](#roks_secondary_storage) | No | `''` |
| [`rosa_token`](#rosa_token) | Conditional | None |
| [`rosa_cluster_admin_password`](#rosa_cluster_admin_password) | No | None (auto-generated) |
| [`rosa_compute_nodes`](#rosa_compute_nodes) | No | `3` |
| [`rosa_compute_machine_type`](#rosa_compute_machine_type) | No | `m5.4xlarge` |
| [`rosa_config_dir`](#rosa_config_dir) | No | `''` |
| [`fyre_username`](#fyre_username) | Conditional | None |
| [`fyre_password`](#fyre_password) | Conditional | None |
| [`fyre_quota_type`](#fyre_quota_type) | Conditional | `quick_burn` |
| [`fyre_product_id`](#fyre_product_id) | Conditional | None |
| [`fyre_site`](#fyre_site) | No | `svl` |
| [`cluster_platform`](#cluster_platform) | No | `x` |
| [`fyre_cluster_description`](#fyre_cluster_description) | No | `No description provided` |
| [`fyre_cluster_size`](#fyre_cluster_size) | Conditional | `medium` |
| [`fyre_worker_count`](#fyre_worker_count) | Conditional | `2` |
| [`fyre_worker_cpu`](#fyre_worker_cpu) | Conditional | `8` |
| [`fyre_worker_memory`](#fyre_worker_memory) | Conditional | `32` |
| [`fyre_worker_additional_disks`](#fyre_worker_additional_disks) | No | None |
| [`fyre_worker_base_disk`](#fyre_worker_base_disk) | No | None |
| [`fyre_master_base_disk`](#fyre_master_base_disk) | No | None |
| [`fyre_nfs_image_registry_size`](#fyre_nfs_image_registry_size) | No | `100Gi` |
| [`ocp_enable_ipv6`](#ocp_enable_ipv6) | No | `false` |
| [`ipi_platform`](#ipi_platform) | No | `aws` |
| [`ipi_region`](#ipi_region) | No | `us-east-1` |
| [`ipi_base_domain`](#ipi_base_domain) | Conditional | None |
| [`ipi_pull_secret_file`](#ipi_pull_secret_file) | Conditional | None |
| [`ipi_dir`](#ipi_dir) | No | `~/openshift-install` |
| [`sshKey`](#sshKey) | No | `''` |
| [`ipi_controlplane_type`](#ipi_controlplane_type) | No | `m5.4xlarge` |
| [`ipi_controlplane_replicas`](#ipi_controlplane_replicas) | No | `3` |
| [`ipi_compute_type`](#ipi_compute_type) | No | `m5.4xlarge` |
| [`ipi_compute_replicas`](#ipi_compute_replicas) | No | `3` |
| [`ipi_rootvolume_size`](#ipi_rootvolume_size) | No | Platform default (typically 120GB) |
| [`aws_access_key_id`](#aws_access_key_id) | Conditional | None |
| [`aws_secret_access_key`](#aws_secret_access_key) | Conditional | None |
| [`gcp_service_account_file`](#gcp_service_account_file) | Conditional | None |
| [`ipi_gcp_projectid`](#ipi_gcp_projectid) | Conditional | None |

Most variables are provider-specific: the `Conditional` entries are only required when provisioning the matching `cluster_type` (and, for the Fyre sizing variables, the matching `fyre_quota_type`) — each entry states its exact condition.

### Cluster Definition

#### cluster_type
Infrastructure provider type for cluster provisioning — one of `fyre` (IBM DevIT Fyre, internal development), `roks` (IBM Cloud ROKS classic infrastructure), `roks-vpc` (IBM Cloud ROKS on VPC infrastructure — modern, recommended; requires an existing VPC), `roks-vpc-setup` (creates a VPC, subnet, and public gateway — run this first, then use the output IDs with `roks-vpc`), `rosa` (Red Hat OpenShift Service on AWS), or `ipi` (Installer-Provisioned Infrastructure, bare metal/on-premises).

- **Required**
- Environment Variable: `CLUSTER_TYPE`
- Default: None

Determines the provisioning workflow and which provider-specific variables are required. Each type has different capabilities — for example GPU support is only available on `roks` and `roks-vpc`.

#### cluster_name
Name for the new cluster, used as the cluster identifier in the provider's system — must be unique within the provider's account/region and follow provider naming conventions (typically lowercase alphanumeric with hyphens; some providers impose length limits or character restrictions).

- **Required**
- Environment Variable: `CLUSTER_NAME`
- Default: None

Used for DNS, resource naming, and cluster identification.

#### ocp_version
OpenShift version to install — a specific version (e.g. `4.22`, `4.22.2`), the alias `default` (newest MAS-supported version), or the alias `rotate` (predetermined version by day of week, for testing only).

- **Required**
- Environment Variable: `OCP_VERSION`
- Default: None

The version must be compatible with MAS and available from the provider.

!!! warning
    For ROKS (`cluster_type=roks`), the version **must** append the `_openshift` suffix — for example `4.22_openshift` or `4.22.13_openshift`.

#### ocp_fips_enabled
Whether to provision the cluster with FIPS (Federal Information Processing Standards) 140-2 cryptographic mode enabled — set to `true` for government or regulated environments that require FIPS 140-2 compliance.

- **Optional**
- Environment Variable: `OCP_FIPS_ENABLED`
- Default: `false`

Applies to `fyre` and `ipi` cluster types. FIPS mode may impact performance and cannot be changed after cluster creation — only enable it if required for compliance.

#### ocp_storage_provider
Storage provider configuration for Fyre clusters — set to `nfs` to enable NFS storage; only applies when `cluster_type=fyre`, leave unset for other cluster types (ROKS, ROSA, IPI).

- **Optional**
- Environment Variable: `OCP_STORAGE_PROVIDER`
- Default: None

When set to `nfs`, an `nfs-client` storage class supporting both ReadWriteOnce (RWO) and ReadWriteMany (RWX) access modes is created connected to the Fyre infrastructure node, and the existing image registry PVC is deleted and recreated with NFS storage. See also [`fyre_nfs_image_registry_size`](#fyre_nfs_image_registry_size).

### GPU Node Support

GPU worker pools are supported on `roks` (classic) and `roks-vpc` (VPC) cluster types only.

#### ocp_provision_gpu
Whether to provision GPU-enabled worker nodes with the cluster — required for GPU-intensive workloads such as MAS Visual Inspection (MVI).

- **Optional**
- Environment Variable: `OCP_PROVISION_GPU`
- Default: `false`

When `true`, a GPU worker pool is provisioned with [`gpu_workers`](#gpu_workers) nodes. On classic ROKS (`roks`) the GPU flavor is hardcoded to `mg4c.32x384.2xp100`; on VPC ROKS (`roks-vpc`) set [`gpu_flavor`](#gpu_flavor) explicitly.

#### gpu_workerpool_name
Name for the GPU worker pool — use the default (`gpu`) for new GPU deployments, or set to an existing pool name to modify that pool rather than create a duplicate.

- **Optional**
- Environment Variable: `GPU_WORKERPOOL_NAME`
- Default: `gpu`

Only applies when [`ocp_provision_gpu`](#ocp_provision_gpu) is `true`. If a GPU worker pool already exists with this name, it will be modified rather than a second pool created.

#### gpu_workers
Number of GPU-enabled worker nodes to provision in the GPU worker pool — a positive integer (e.g. `1`, `2`, `3`).

- **Optional**
- Environment Variable: `GPU_WORKERS`
- Default: `1`

Use the default (1) for minimal GPU deployments or testing; increase for production MAS Visual Inspection deployments. GPU nodes use expensive hardware — only provision what you need.

#### gpu_flavor
GPU-enabled machine type for the GPU worker pool when using `cluster_type=roks-vpc` — for example `gx2.8x64.v100` (8 vCPU, 64 GB RAM, 1x V100 GPU, default) or `gx2.16x128.2v100` (16 vCPU, 128 GB RAM, 2x V100 GPUs).

- **Optional**
- Environment Variable: `GPU_FLAVOR`
- Default: `gx2.8x64.v100`

Only applies when [`ocp_provision_gpu`](#ocp_provision_gpu) is `true` and `cluster_type=roks-vpc`; on classic ROKS (`roks`) the GPU flavor is hardcoded to `mg4c.32x384.2xp100` and this variable is ignored.

!!! tip
    GPU flavor availability varies by zone — verify availability before deploying with `ibmcloud oc flavors --zone <zone> --provider vpc-gen2 | grep gpu`.

### ROKS
The following variables are only used when `cluster_type` is `roks`, `roks-vpc`, or `roks-vpc-setup` (unless noted otherwise).

#### ibmcloud_apikey
IBM Cloud API key for authentication, used by the ibmcloud CLI for all cluster operations — obtain it from IBM Cloud IAM (Identity and Access Management).

- **Required** (when `cluster_type` is `roks`, `roks-vpc`, or `roks-vpc-setup`)
- Environment Variable: `IBMCLOUD_APIKEY`
- Default: None

The key must have cluster creation permissions in the target resource group ([`ibmcloud_resourcegroup`](#ibmcloud_resourcegroup)). Keep API keys secure — use environment variables or secure vaults rather than hardcoding them in playbooks.

#### ibmcloud_endpoint
IBM Cloud API endpoint URL for authentication and cluster operations — override the default only for IBM Cloud dedicated or private environments, or for testing against staging environments.

- **Optional**
- Environment Variable: `IBMCLOUD_ENDPOINT`
- Default: `https://cloud.ibm.com`

Determines which IBM Cloud environment is targeted for cluster provisioning. Used together with [`ibmcloud_apikey`](#ibmcloud_apikey).

#### ibmcloud_resourcegroup
IBM Cloud resource group in which the ROKS cluster will be created — the group must exist before provisioning and [`ibmcloud_apikey`](#ibmcloud_apikey) must have permissions in it.

- **Optional**
- Environment Variable: `IBMCLOUD_RESOURCEGROUP`
- Default: `Default`

Use the default for simple deployments; specify a different existing resource group for organizational separation.

#### ibmcloud_region
IBM Cloud region targeted when running VPC Infrastructure Service (`ibmcloud is`) commands — a valid region identifier such as `us-south`, `eu-de`, `eu-gb`, `jp-tok`, or `au-syd`.

- **Required** (when `cluster_type=roks-vpc-setup`)
- **Optional** (when `cluster_type=roks-vpc` — auto-derived from the VPC CRN or from `roks_zone`)
- Environment Variable: `IBMCLOUD_REGION`
- Default: None

For `roks-vpc-setup` this must be provided explicitly, as it determines where all resources are created. For `roks-vpc` the region is resolved automatically in this order: `roks_zone` stripped of its zone suffix (e.g. `eu-gb-1` → `eu-gb`), then the VPC's CRN extracted during the VPC name lookup (which overrides the zone-derived value if different) — an explicitly set `ibmcloud_region` always wins.

#### roks_zone
IBM Cloud availability zone where the ROKS cluster will be provisioned — classic format for `roks` (`dal10`, `lon02`, `fra02`, `tok02`) or VPC format for `roks-vpc` (`us-south-1`, `eu-de-2`, `eu-gb-3`, `jp-tok-1` — always `<region>-<n>`).

- **Optional**
- Environment Variable: `ROKS_ZONE`
- Default: `dal10`

The zone determines cluster location, which affects latency, data residency, and available services. For `roks-vpc` the zone must be within [`ibmcloud_region`](#ibmcloud_region) (e.g. region `us-south` → zone `us-south-1`), and not all [`roks_flavor`](#roks_flavor) values are available in all zones — verify availability in your target zone.

#### roks_flavor
Worker node machine type (flavor) for the ROKS cluster — classic flavors for `roks` (e.g. `b3c.4x16`, `b3c.16x64.300gb`, `b3c.32x128`) or VPC flavors for `roks-vpc` (e.g. `bx2.4x16`, `bx2.16x64`, `bx2.48x192`).

- **Optional**
- Environment Variable: `ROKS_FLAVOR`
- Default: `b3c.16x64.300gb`

The default (16 vCPU, 64 GB RAM, 300 GB storage) suits standard MAS deployments on classic ROKS. Larger flavors cost more but provide more resources.

!!! warning
    The default is a **classic** flavor and will fail if used with `roks-vpc`. Always set an appropriate `bx2.*` VPC flavor when using `cluster_type=roks-vpc` — check availability with `ibmcloud oc flavors --zone <zone> --provider vpc-gen2`.

#### roks_workers
Number of worker nodes to provision in the ROKS cluster — a positive integer (minimum 1; 3 or more recommended for production high availability).

- **Optional**
- Environment Variable: `ROKS_WORKERS`
- Default: `3`

Total cluster capacity = worker count x [`roks_flavor`](#roks_flavor) resources. More workers provide more capacity and better high availability but increase costs; GPU workers can be added separately via [`ocp_provision_gpu`](#ocp_provision_gpu).

#### roks_flags
Additional command-line flags passed to the `ibmcloud ks cluster create` command — for example `--disable-public-service-endpoint`, `--pod-subnet`, or `--service-subnet`.

- **Optional**
- Environment Variable: `ROKS_FLAGS`
- Default: `''`

Use for advanced configurations not covered by the other ROKS variables; consult the IBM Cloud Kubernetes Service documentation for available flags.

!!! warning
    Use with caution — incorrect flags can cause provisioning failures.

### ROKS VPC Setup
The following variables are only used when `cluster_type = roks-vpc-setup`.
Run this provider first to create the VPC infrastructure, then pass the output IDs to `cluster_type=roks-vpc`.
Also uses `ibmcloud_apikey`, `ibmcloud_endpoint`, `ibmcloud_resourcegroup`, and `ibmcloud_region`.

**Note**: Does not require `ocp_version` or `roks_zone`. Subnets are always created in all three zones of `ibmcloud_region` (`<region>-1`, `<region>-2`, `<region>-3`), matching the default IBM Cloud UI layout.

**Resources created** (all idempotent — existing resources with the same name are reused):

- VPC: `<roks_vpc_name>`
- Public gateways: `<roks_vpc_name>-pgw-<region>-1/2/3`
- Subnets: `<roks_vpc_name>-subnet-<region>-1/2/3` (256 IPs each, gateway attached inline)
- COS instance: `<roks_vpc_name>-cos` (Standard plan, `premium-global-deployment`)

**Outputs** printed at completion for use with `cluster_type=roks-vpc`:

- `ROKS_VPC_ID`
- `ROKS_SUBNET_ID` (one per zone)
- `ROKS_COS_INSTANCE_CRN`

#### roks_vpc_name
Base name applied to the new VPC and all of its associated resources: VPC (`<name>`), subnets (`<name>-subnet-<region>-<n>`), public gateways (`<name>-pgw-<region>-<n>`), and COS instance (`<name>-cos`).

- **Optional**
- Environment Variable: `ROKS_VPC_NAME`
- Default: `cluster_name`

All resources are created idempotently — existing resources with the same name are reused. With `cluster_type=roks-vpc`, set this to the name used during `roks-vpc-setup` and the provider automatically resolves `roks_vpc_id`, `roks_subnet_id`, and `roks_cos_instance_crn` by name (see [ROKS VPC](#roks-vpc)); providing any of those directly overrides the lookup.

### ROKS VPC
The following variables are only used when `cluster_type = roks-vpc`.
Also uses `ibmcloud_apikey`, `ibmcloud_endpoint`, `ibmcloud_resourcegroup`, `ibmcloud_region`, `roks_zone`, `roks_flavor`, `roks_workers`, and `roks_flags`.

**Note**: `roks_zone` must use VPC zone format (e.g. `us-south-1`, `eu-de-2`). `roks_vpc_name` (see [ROKS VPC Setup](#roks-vpc-setup)) is used as the basis for the name-based lookups described below.

#### roks_vpc_id
IBM Cloud VPC ID — overrides the name-based lookup when provided, for example `r006-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`.

- **Optional** (if `roks_vpc_name` is provided)
- Environment Variable: `ROKS_VPC_ID`
- Default: None

Use when the VPC was not created by `roks-vpc-setup` or when the name-based lookup is not suitable; otherwise the VPC is looked up by [`roks_vpc_name`](#roks_vpc_name).

#### roks_subnet_id
ID of the VPC subnet to place worker nodes into — for example `0717-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`.

- **Optional** (resolved automatically from `roks_vpc_id` + `roks_zone` if not provided)
- Environment Variable: `ROKS_SUBNET_ID`
- Default: None

When not provided, the subnet is resolved automatically by finding the subnet in the VPC whose zone matches `roks_zone`. This works correctly when the VPC was created by `roks-vpc-setup`, which creates exactly one subnet per zone; provide directly to override.

#### roks_cos_instance_crn
CRN of the IBM Cloud Object Storage instance — for example `crn:v1:bluemix:public:cloud-object-storage:global:a/...::` — used because VPC-based ROKS clusters store the internal OpenShift image registry in COS.

- **Optional** (resolved automatically from `<roks_vpc_name>-cos` if not provided)
- Environment Variable: `ROKS_COS_INSTANCE_CRN`
- Default: None

When not provided, the CRN is looked up from the COS instance named `<roks_vpc_name>-cos` in the resource group; provide directly to override.

#### roks_secondary_storage
Optional secondary block storage for VPC worker nodes — for example `300gb.5iops-tier` — attached to each worker node at provision time, providing additional ephemeral storage capacity beyond the 100GB boot disk.

- **Optional**
- Environment Variable: `ROKS_SECONDARY_STORAGE`
- Default: `''`

Run `ibmcloud ks flavor get --provider vpc-gen2 --zone <zone> --flavor <flavor>` to list the available secondary storage configurations for your flavor.

### ROSA
The following variables are only used when `cluster_type = rosa`.

#### rosa_token
Red Hat OpenShift Service on AWS (ROSA) authentication token, obtained from [OpenShift Cluster Manager](https://console.redhat.com/openshift/token/rosa/show#) — required for all ROSA cluster operations.

- **Required** (when `cluster_type=rosa`)
- Environment Variable: `ROSA_TOKEN`
- Default: None

The token must be valid and have permissions to create clusters; without it ROSA cluster provisioning will fail. Tokens expire periodically — obtain a fresh token before provisioning and keep it secure.

#### rosa_cluster_admin_password
Password for the `cluster-admin` user account on the ROSA cluster — a string meeting OpenShift password requirements (typically 8+ characters).

- **Optional**
- Environment Variable: `ROSA_CLUSTER_ADMIN_PASSWORD`
- Default: None (auto-generated)

When unset, a secure password is auto-generated and saved to the rosa config file in [`rosa_config_dir`](#rosa_config_dir). Consider using auto-generation for better security.

#### rosa_compute_nodes
Number of compute (worker) nodes in the ROSA cluster — a positive integer (minimum 2; 3 or more recommended for production high availability).

- **Optional**
- Environment Variable: `ROSA_COMPUTE_NODES`
- Default: `3`

Total cluster capacity = node count x [`rosa_compute_machine_type`](#rosa_compute_machine_type) resources. More nodes provide more capacity and better high availability but increase AWS costs.

#### rosa_compute_machine_type
AWS EC2 instance type for ROSA worker nodes — for example `m5.2xlarge` (development/testing), `m5.4xlarge` (default, 16 vCPU / 64 GB RAM, suitable for most MAS deployments), `m5.8xlarge`, or `m5.12xlarge` (larger workloads).

- **Optional**
- Environment Variable: `ROSA_COMPUTE_MACHINE_TYPE`
- Default: `m5.4xlarge`

Verify instance type availability in your AWS region.

#### rosa_config_dir
Directory for storing ROSA cluster configuration files — an absolute filesystem path such as `/tmp/rosa-config` or `~/rosa-clusters`.

- **Optional**
- Environment Variable: `ROSA_CONFIG_DIR`
- Default: `''`

When set, cluster details (API endpoint, credentials) are saved to `rosa-{{cluster_name}}-details.yaml` in this directory, including the auto-generated [`rosa_cluster_admin_password`](#rosa_cluster_admin_password) if one was not specified; when unset, configuration files are not saved and details must be retrieved manually.

!!! warning
    The config file contains sensitive information (the cluster-admin password). Ensure the directory has appropriate permissions.

### Fyre
The following variables are only used when `cluster_type = fyre`. Fyre is an internal IBM development platform — access requires IBM credentials and appropriate permissions.

#### fyre_username
Fyre username for authentication with the IBM DevIT Fyre API — a valid Fyre username (IBM intranet ID).

- **Required** (when `cluster_type=fyre`)
- Environment Variable: `FYRE_USERNAME`
- Default: None

Paired with [`fyre_password`](#fyre_password); without valid credentials Fyre cluster provisioning will fail.

#### fyre_password
Fyre API key for authentication with the Fyre API, paired with [`fyre_username`](#fyre_username) — obtained from the Fyre portal.

- **Required** (when `cluster_type=fyre`)
- Environment Variable: `FYRE_APIKEY`
- Default: None

Without a valid API key Fyre cluster provisioning will fail. Keys may expire and need renewal — keep them secure and rotate regularly.

#### fyre_quota_type
Type of Fyre quota to use for cluster provisioning, which determines the billing method and required sizing variables — `quick_burn` (pre-defined cluster sizes, faster and simpler; requires [`fyre_cluster_size`](#fyre_cluster_size)) or `product_group` (custom sizing with more control; requires [`fyre_worker_count`](#fyre_worker_count), [`fyre_worker_cpu`](#fyre_worker_cpu), and [`fyre_worker_memory`](#fyre_worker_memory)).

- **Required** (when `cluster_type=fyre`)
- Environment Variable: `FYRE_QUOTA_TYPE`
- Default: `quick_burn`

#### fyre_product_id
Product ID for internal IBM accounting and cost tracking — cluster costs are charged to this product ID, so an incorrect ID may cause provisioning to fail or incorrect billing.

- **Required** (when `cluster_type=fyre`)
- Environment Variable: `FYRE_PRODUCT_ID`
- Default: None

Required for both quota types; obtain the correct ID for your project from your IBM product team or manager.

#### fyre_site
Fyre datacenter site to provision the cluster in — a valid Fyre site code such as `svl` (San Jose/Silicon Valley, default and most commonly used), `rtp`, or `raleigh`.

- **Optional**
- Environment Variable: `FYRE_SITE`
- Default: `svl`

The site determines cluster location, which affects network latency and available resources — not all sites support all features (see [`ocp_enable_ipv6`](#ocp_enable_ipv6)).

#### cluster_platform
Fyre platform type for the cluster, passed as the `platform` field in the Fyre API request.

- **Optional**
- Environment Variable: `CLUSTER_PLATFORM`
- Default: `x`

#### fyre_cluster_description
Human-readable description for the Fyre cluster, shown in the Fyre portal — any descriptive string (e.g. "MAS 9.0 testing", "Development cluster").

- **Optional**
- Environment Variable: `FYRE_CLUSTER_DESCRIPTION`
- Default: `No description provided`

No functional impact on the cluster; useful for tracking and managing multiple clusters (include purpose, owner, or project information).

#### fyre_cluster_size
Pre-defined Fyre cluster size to use when provisioning with quick_burn quota — for example `small` (minimal testing), `medium` (standard development/testing), or `large` (more intensive workloads).

- **Required** (when `cluster_type=fyre` and `fyre_quota_type=quick_burn`)
- Environment Variable: `FYRE_CLUSTER_SIZE`
- Default: `medium`

Quick burn sizes are pre-defined by Fyre and individual resources cannot be customized — for custom sizing use `fyre_quota_type=product_group` instead.

#### fyre_worker_count
Number of worker nodes to provision when using product_group quota with custom sizing — a positive integer (typically 2-10; use 2+ for development/testing and 3+ for high availability testing).

- **Required** (when `cluster_type=fyre` and `fyre_quota_type=product_group`)
- Environment Variable: `FYRE_WORKER_COUNT`
- Default: `2`

More workers provide more resources but consume more quota; total cluster capacity = worker count x per-worker resources.

#### fyre_worker_cpu
CPU cores to assign to each worker node when using product_group quota — a positive integer, maximum 16 (Fyre limit).

- **Required** (when `cluster_type=fyre` and `fyre_quota_type=product_group`)
- Environment Variable: `FYRE_WORKER_CPU`
- Default: `8`

Total cluster CPUs = [`fyre_worker_count`](#fyre_worker_count) x CPU per worker.

#### fyre_worker_memory
Memory in GB to assign to each worker node when using product_group quota — a positive integer, maximum 64 (Fyre limit).

- **Required** (when `cluster_type=fyre` and `fyre_quota_type=product_group`)
- Environment Variable: `FYRE_WORKER_MEMORY`
- Default: `32`

Total cluster memory = [`fyre_worker_count`](#fyre_worker_count) x memory per worker.

#### fyre_worker_additional_disks
Additional disks to attach to every worker node — a comma-separated list of disk sizes in GB (e.g. `400`, `400,400`, `200,300,400`).

- **Optional**
- Environment Variable: `FYRE_WORKER_ADDITIONAL_DISKS`
- Default: None

For example `400,400` adds two 400GB disks to each worker; total additional storage = disk sizes x [`fyre_worker_count`](#fyre_worker_count). Useful for testing storage configurations or providing extra capacity.

#### fyre_worker_base_disk
Base disk size in GB for each worker node when using product_group quota — an integer between 40 and 500 (Fyre API limits).

- **Optional**
- Environment Variable: `FYRE_WORKER_BASE_DISK`
- Default: None

When unset, the Fyre API default (250 GB per worker) applies. Reducing this can significantly save disk quota on development and test clusters — for example a 4-worker cluster defaults to at least 1000 GB of worker base disks.

#### fyre_master_base_disk
Base disk size in GB for each master node when using product_group quota — an integer between 40 and 500 (Fyre API limits).

- **Optional**
- Environment Variable: `FYRE_MASTER_BASE_DISK`
- Default: None

When unset, the Fyre API default (100 GB per master) applies. As with [`fyre_worker_base_disk`](#fyre_worker_base_disk), reducing this saves disk quota on development and test clusters.

#### fyre_nfs_image_registry_size
Size of NFS storage allocated for the OpenShift image registry when NFS storage is configured on Fyre clusters — a Kubernetes storage size such as `50Gi`, `100Gi`, or `200Gi`.

- **Optional**
- Environment Variable: `FYRE_NFS_IMAGE_REGISTRY_SIZE`
- Default: `100Gi`

Only applies when [`ocp_storage_provider`](#ocp_storage_provider) is `nfs`. The size is limited by available storage on the Fyre infrastructure node; the image registry stores all container images used in the cluster, so increase for clusters with many container images.

#### ocp_enable_ipv6
Whether to enable IPv6 networking for the Fyre cluster — set to `true` for IPv6 testing.

- **Optional**
- Environment Variable: `OCP_ENABLE_IPV6`
- Default: `false`

!!! warning
    IPv6 is only supported at the RTP (Raleigh) Fyre site ([`fyre_site`](#fyre_site) must be `rtp`) — it will fail at other sites.

### IPI
These variables are only used when `cluster_type = ipi`.

!!! note
    IPI stands for **Installer Provisioned Infrastructure**.  OpenShift offers two possible deployment methods: IPI and UPI (User Provisioned Infrastructure). The difference is the degree of automation and customization. IPI will not only deploy OpenShift but also all infrastructure components and configurations.

#### ipi_platform
Cloud platform for the IPI deployment — `aws` (default, tested and supported) or `gcp`; other platforms supported by openshift-install may work but are untested.

- **Optional**
- Environment Variable: `IPI_PLATFORM`
- Default: `aws`

Determines which cloud provider is used and which provider-specific variables are required: `aws` requires [`aws_access_key_id`](#aws_access_key_id) / [`aws_secret_access_key`](#aws_secret_access_key); `gcp` requires [`gcp_service_account_file`](#gcp_service_account_file) and [`ipi_gcp_projectid`](#ipi_gcp_projectid).

#### ipi_region
Cloud platform region where the IPI cluster will be deployed — a region valid for the selected platform, such as `us-east-1`, `us-west-2`, or `eu-west-1` for AWS.

- **Optional**
- Environment Variable: `IPI_REGION`
- Default: `us-east-1`

The region determines cluster location, which affects latency, data residency, and service availability — verify that your target region supports the required instance types.

#### ipi_base_domain
Base DNS domain for the OpenShift cluster — a domain you control, such as `example.com` or `ocp.mycompany.com`.

- **Required** (when `cluster_type=ipi`)
- Environment Variable: `IPI_BASE_DOMAIN`
- Default: None

Cluster URLs will be subdomains of this base domain (e.g. `api.clustername.example.com`). The openshift-install process creates DNS records in this domain, so you must have control over it and the ability to configure DNS.

#### ipi_pull_secret_file
Path to the file containing your Red Hat OpenShift pull secret (required to pull OpenShift container images during installation) — an absolute path to the pull secret JSON file, downloaded from the [Red Hat Hybrid Cloud Console](https://console.redhat.com/openshift/install/metal/user-provisioned).

- **Required** (when `cluster_type=ipi`)
- Environment Variable: `IPI_PULL_SECRET_FILE`
- Default: None

Must be a valid, non-expired pull secret; without one cluster installation fails when attempting to pull container images. Keep the file secure — it contains authentication credentials.

#### ipi_dir
Working directory for the IPI installation process — an absolute filesystem path containing the openshift-install executable, configuration files, and generated logs.

- **Optional**
- Environment Variable: `IPI_DIR`
- Default: `~/openshift-install`

`cluster_name` is used in the subdirectory structure beneath this directory. The directory contains sensitive information (kubeconfig, credentials) — ensure appropriate permissions and preserve it for cluster management and troubleshooting.

#### sshKey
Public SSH key to install on all cluster nodes, enabling SSH access via bastion host for troubleshooting — a valid SSH public key string such as `ssh-rsa AAAAB3...`.

- **Optional**
- Environment Variable: `SSH_PUB_KEY`
- Default: `''`

SSH access to nodes is typically not needed for normal operations of managed clusters; only set this if you need direct node access for debugging or advanced cluster management.

#### ipi_controlplane_type
Machine type for control plane (master) nodes — a machine type valid for the selected platform, such as `m5.2xlarge`, `m5.4xlarge` (default, 16 vCPU / 64 GB RAM), or `m5.8xlarge` for AWS.

- **Optional**
- Environment Variable: `IPI_CONTROLPLANE_TYPE`
- Default: `m5.4xlarge`

Control plane nodes run cluster management services — an undersized control plane can impact cluster stability, so do not undersize for production. See also [`ipi_controlplane_replicas`](#ipi_controlplane_replicas).

#### ipi_controlplane_replicas
Number of control plane (master) nodes to provision — an odd positive integer (1, 3, 5, 7) as required for etcd quorum; 3 is recommended for production.

- **Optional**
- Environment Variable: `IPI_CONTROLPLANE_REPLICAS`
- Default: `3`

!!! warning
    Must be an odd number for etcd quorum. Using 1 provides no high availability — use 3 for production.

#### ipi_compute_type
Machine type for compute (worker) nodes — a machine type valid for the selected platform, such as `m5.2xlarge` (development/testing), `m5.4xlarge` (default, 16 vCPU / 64 GB RAM, suitable for most MAS deployments), `m5.8xlarge`, or `m5.12xlarge` (larger workloads) for AWS.

- **Optional**
- Environment Variable: `IPI_COMPUTE_TYPE`
- Default: `m5.4xlarge`

Consider total cluster capacity (type x [`ipi_compute_replicas`](#ipi_compute_replicas)) when choosing.

#### ipi_compute_replicas
Number of compute (worker) nodes to provision — a positive integer (minimum 2; 3 or more recommended for production high availability).

- **Optional**
- Environment Variable: `IPI_COMPUTE_REPLICAS`
- Default: `3`

Total cluster capacity = worker count x [`ipi_compute_type`](#ipi_compute_type) resources.

#### ipi_rootvolume_size
Root volume size in GiB for cluster nodes — a positive integer such as `120`, `200`, or `500`, covering the OS, container images, and ephemeral storage.

- **Optional**
- Environment Variable: `IPI_ROOTVOLUME_SIZE`
- Default: Platform default (typically 120GB)

Platform defaults are typically sufficient — only increase for clusters with many container images or workloads with high ephemeral storage needs. Insufficient space can cause node issues.

### AWS
The following variables are only used when `cluster_type = ipi` and `ipi_platform = aws`.

#### aws_access_key_id
AWS access key ID for authentication — a string of typically 20 characters starting with `AKIA`, associated with an IAM user or role.

- **Required** (when `cluster_type=ipi` and `ipi_platform=aws`)
- Environment Variable: `AWS_ACCESS_KEY_ID`
- Default: None

The IAM user/role must have extensive permissions (VPC, EC2, ELB, Route53, IAM, etc.) to create the cluster infrastructure — consider using a dedicated IAM user for cluster provisioning.

#### aws_secret_access_key
AWS secret access key for authentication, paired with [`aws_access_key_id`](#aws_access_key_id) — a string of typically 40 characters.

- **Required** (when `cluster_type=ipi` and `ipi_platform=aws`)
- Environment Variable: `AWS_SECRET_ACCESS_KEY`
- Default: None

!!! warning
    Keep secret keys secure. Never commit them to version control — use environment variables or secure vaults, and rotate keys regularly.

### GCP
The following variables are only used when `cluster_type = ipi` and `ipi_platform = gcp`.

#### gcp_service_account_file
Path to the GCP service account credentials file — an absolute path to a service account JSON key file, downloaded from GCP IAM.

- **Required** (when `cluster_type=ipi` and `ipi_platform=gcp`)
- Environment Variable: `GOOGLE_APPLICATION_CREDENTIALS`
- Default: None

The service account must have extensive permissions (Compute, Networking, IAM, etc.) to create instances and networking resources; keep the file secure.

#### ipi_gcp_projectid
GCP project where the IPI cluster will be deployed — a valid, existing GCP project ID.

- **Required** (when `cluster_type=ipi` and `ipi_platform=gcp`)
- Environment Variable: `GOOGLE_PROJECTID`
- Default: None

All cluster resources are created in, and costs billed to, this project. The project must exist before provisioning and [`gcp_service_account_file`](#gcp_service_account_file) must have permissions in it.

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
