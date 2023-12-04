ocp_provision
===============================================================================

Provision OCP cluster on DevIT Fyre, IBM Cloud ROKS, ROSA or MCSP.

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


Role Variables - MCSP
-------------------------------------------------------------------------------
The following variables are only used when `cluster_type = mcsp`.
NOTE: This is only intended for internal use within IBM.

### mcsp_control_plane_api

OCP API URL of the Control Plane for the targeted MCSP environment. See https://pages.github.ibm.com/ibm-saas-platform/MultiCloud-SaaS-Framework/MCSP_Overview/mcsp_clusters/

- **Required** when `cluster_type = mcsp`
- Environment Variable: `MCSP_CONTROL_PLANE_API`
- Default Value: None

### mcsp_control_plane_token
Temporary; will be replaced with the credentials for a functional ID. See https://ibm-watson-iot.slack.com/archives/C04E0SN54KW/p1697543955467329. In the meantime, if you want to use this role, log in to the MCSP Control Plane OCP using your IBM ID and request a token via the "Copy Login Command" feature.

### mcsp_region
MCSP region within which to create the cluster. Supported values will vary depending on the MCSP environment that is being targeted. See https://pages.github.ibm.com/ibm-saas-platform/MultiCloud-SaaS-Framework/MCSP_Overview/mcsp_clusters/

- **Required** when `cluster_type = mcsp`
- Environment Variable: `MCSP_REGION`
- Default Value: None

### mcsp_platform

Hyperscaler platform to target. Currently supports `aws` only.

- **Required** when `cluster_type = mcsp`
- Environment Variable: `MCSP_PLATFORM`
- Default Value: `aws`

### mcsp_platform_account_secret_name

Name of the secret in the MCSP Control Plane OCP containing details necessary to authenticate with MAS's account in the targeted hyperscaler platform. This should already have been configured as part of the MAS onboarding process.

- **Required** when `cluster_type = mcsp`
- Environment Variable: `MCSP_PLATFORM_ACCOUNT_SECRET_NAME`
- Default Value: `aws-account`

### mcsp_control_plane_namespace
The namespace assigned to MAS in the MCSP Control Plane OCP.

- **Required** when `cluster_type = mcsp`
- Environment Variable: `MCSP_CONTROL_PLANE_NAMESPACE`
- Default Value: `mas`

### mcsp_worker_count

Number of worker nodes for the cluster

- **Required** when `cluster_type = mcsp`
- Environment Variable: `MCSP_WORKER_COUNT`
- Default Value: `3`

### mcsp_worker_flavor

The hardware to use for each worker. See https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-types.html

- **Required** when `cluster_type = mcsp`
- Environment Variable: `MCSP_WORKER_FLAVOR`
- Default Value: `r5a.xlarge`

### mcsp_argocd_api

API URL of the ArgoCD worker for the targeted MCSP environment/region. See https://pages.github.ibm.com/ibm-saas-platform/CICD-Playbook/continuous-delivery/Overview

- **Required** when `cluster_type = mcsp`
- Environment Variable: `MCSP_ARGOCD_API`
- Default Value: None

### mcsp_argocd_secret_name

Name of the secret in the MCSP Control Plane OCP containing details necessary to authenticate with the targeted ArgoCD worker. This should already have been configured as part of the MAS onboarding process.

- **Required** when `cluster_type = mcsp`
- Environment Variable: `MCSP_ARGOCD_SECRET_NAME`
- Default Value: `argo`

### mcsp_argocd_project_name

Name of the ArgoCD project which will contain the Applications that will be deployed to this cluster by ArgoCD.

- **Required** when `cluster_type = mcsp`
- Environment Variable: `MCSP_ARGOCD_PROJECT_NAME`
- Default Value: `mas`

### mcsp_idpverify_enabled

Whether or not to enable the MCSP idpverify addon for this cluster. See https://pages.github.ibm.com/ibm-saas-platform/CP-Playbook/Addons/Addon%20List/idpverify/

- **Required** when `cluster_type = mcsp`
- Environment Variable: `MCSP_IDPVERIFY_ENABLED`
- Default Value: true

### mcsp_idpverify_secret_verify_name

Name of the secret in the MCSP Control Plane OCP containing details used by the idpverify addon. This should already have been configured by the MCSP team as part of the MAS onboarding process.

- **Required** when `cluster_type = mcsp`
- Environment Variable: `MCSP_IDPVERIFY_SECRET_VERIFY_NAME`
- Default Value: `verify`

### mcsp_security_enabled

Whether or not to enable the MCSP security addon for this cluster. See https://pages.github.ibm.com/ibm-saas-platform/CP-Playbook/Addons/Addon%20List/security/

- **Required** when `cluster_type = mcsp`
- Environment Variable: ``MCSP_SECURITY_ENABLED``
- Default Value: true

### mcsp_logforwarder_enabled

Whether or not to enable the MCSP security addon for this cluster. See https://pages.github.ibm.com/ibm-saas-platform/CP-Playbook/Addons/Addon%20List/logforwarder/

- **Required** when `cluster_type = mcsp`
- Environment Variable: ``MCSP_LOGFORWARDER_ENABLED``
- Default Value: true


### mcsp_logforwarder_secret_dlc_name

Name of a secret in the MCSP Control Plane OCP containing details necessary used by the logforwarder addon. This should already have been configured by the MCSP team as part of the MAS onboarding process.

- **Required** when `cluster_type = mcsp`
- Environment Variable: `MCSP_LOGFORWARDER_SECRET_DLC_NAME`
- Default Value: `dlc-cert`

### mcsp_logforwarder_secret_sf_name

Name of a secret in the MCSP Control Plane OCP containing details necessary used by the logforwarder addon. This should already have been configured by the MCSP team as part of the MAS onboarding process.

- **Required** when `cluster_type = mcsp`
- Environment Variable: `MCSP_LOGFORWARDER_SECRET_SF_NAME`
- Default Value: `syslog-forwarder`

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
