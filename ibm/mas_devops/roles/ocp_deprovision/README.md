ocp_deprovision
===============================================================================
Deprovision OCP cluster in Fyre, IBM Cloud, & ROSA.

Role Variables
-------------------------------------------------------------------------------
### cluster_type
Infrastructure provider type for cluster deprovisioning.

- **Required**
- Environment Variable: `CLUSTER_TYPE`
- Default: None

**Purpose**: Specifies which infrastructure provider was used to provision the cluster. Determines the deprovisioning method and required credentials.

**When to use**:
- Always required for cluster deprovisioning
- Must match the provider used to create the cluster
- Each type requires different provider-specific variables

**Valid values**: `fyre`, `roks`, `rosa`, `ipi`
- `fyre`: IBM DevIT Fyre clusters (internal development)
- `roks`: IBM Cloud Red Hat OpenShift Kubernetes Service
- `rosa`: AWS Red Hat OpenShift Service on AWS
- `ipi`: Installer-Provisioned Infrastructure (AWS, GCP)

**Impact**: Determines deprovisioning workflow and which provider-specific variables are required. Using wrong type will cause deprovisioning to fail.

**Related variables**:
- `cluster_name`: Name of the cluster to deprovision
- Provider-specific credentials (ibmcloud_apikey, rosa_token, fyre_apikey, etc.)

**Note**: **IMPORTANT** - Must match the provider used to create the cluster. Verify cluster type before deprovisioning to avoid errors.

### cluster_name
Name of the cluster to deprovision.

- **Required**
- Environment Variable: `CLUSTER_NAME`
- Default: None

**Purpose**: Identifies which cluster to deprovision. Used to locate and delete the cluster in the provider's system.

**When to use**:
- Always required for cluster deprovisioning
- Must exactly match the cluster name in the provider
- Used to target the specific cluster for deletion

**Valid values**: String matching the cluster name in the provider's system

**Impact**: Determines which cluster is deleted. **CRITICAL** - Incorrect name may cause wrong cluster to be deleted or deprovisioning to fail.

**Related variables**:
- `cluster_type`: Provider where cluster exists

**Note**: **WARNING** - Deprovisioning permanently deletes the cluster and all its resources. Verify the cluster name carefully before proceeding. This operation cannot be undone.


Role Variables - ROKS
-------------------------------------------------------------------------------
### ibmcloud_apikey
IBM Cloud API key for authentication.

- **Required** (when `cluster_type=roks`)
- Environment Variable: `IBMCLOUD_APIKEY`
- Default: None

**Purpose**: Authenticates with IBM Cloud to deprovision ROKS clusters. Used by the ibmcloud CLI for cluster deletion operations.

**When to use**:
- Always required for ROKS cluster deprovisioning
- Must have permissions to delete clusters in the resource group
- Same API key used for cluster provisioning can be used

**Valid values**: IBM Cloud API key string (typically 40+ characters)

**Impact**: Without a valid API key with delete permissions, cluster deprovisioning will fail.

**Related variables**:
- `cluster_name`: ROKS cluster to deprovision

**Note**: The API key must have cluster deletion permissions in the resource group. Deprovisioning permanently deletes the cluster.


Role Variables - ROSA
-------------------------------------------------------------------------------
### rosa_token
Red Hat OpenShift Service on AWS (ROSA) authentication token.

- **Required** (when `cluster_type=rosa`)
- Environment Variable: `ROSA_TOKEN`
- Default: None

**Purpose**: Authenticates with the ROSA service to deprovision OpenShift clusters on AWS. Required for cluster deletion operations.

**When to use**:
- Always required for ROSA cluster deprovisioning
- Obtain from [OpenShift Cluster Manager](https://console.redhat.com/openshift/token/rosa/show#)
- Token must be valid and not expired

**Valid values**: ROSA API token string from Red Hat OpenShift Cluster Manager

**Impact**: Without a valid token, ROSA cluster deprovisioning will fail.

**Related variables**:
- `cluster_name`: ROSA cluster to deprovision

**Note**: Tokens expire periodically. Obtain a fresh token before deprovisioning. Deprovisioning permanently deletes the cluster and all AWS resources.


Role Variables - FYRE
-------------------------------------------------------------------------------
### fyre_username
Fyre username for authentication.

- **Required** (when `cluster_type=fyre`)
- Environment Variable: `FYRE_USERNAME`
- Default: None

**Purpose**: Authenticates with the IBM DevIT Fyre API to deprovision OpenShift clusters on Fyre infrastructure.

**When to use**:
- Always required for Fyre cluster deprovisioning
- Must be a valid Fyre account username
- Used for internal IBM development and testing

**Valid values**: Valid Fyre username (IBM intranet ID)

**Impact**: Without valid credentials, Fyre cluster deprovisioning will fail.

**Related variables**:
- `fyre_apikey`: API key paired with this username
- `cluster_name`: Fyre cluster to deprovision

**Note**: Fyre is an internal IBM development platform. Access requires IBM credentials and appropriate permissions.

### fyre_apikey
Fyre API key for authentication.

- **Required** (when `cluster_type=fyre`)
- Environment Variable: `FYRE_APIKEY`
- Default: None

**Purpose**: Authenticates with the Fyre API for cluster deprovisioning operations. Paired with Fyre username for authentication.

**When to use**:
- Always required for Fyre cluster deprovisioning
- Obtain from Fyre portal
- Keep secure and rotate regularly

**Valid values**: Valid Fyre API key string

**Impact**: Without a valid API key, Fyre cluster deprovisioning will fail.

**Related variables**:
- `fyre_username`: Username paired with this API key
- `cluster_name`: Fyre cluster to deprovision

**Note**: Keep API keys secure. Obtain from the Fyre portal. Keys may expire and need renewal.

### fyre_site
Fyre datacenter site location.

- **Optional**
- Environment Variable: `FYRE_SITE`
- Default: `svl`

**Purpose**: Specifies which Fyre datacenter site the cluster was provisioned in. Used to locate the cluster for deprovisioning.

**When to use**:
- Use default (`svl` - San Jose/Silicon Valley) if cluster was provisioned there
- Set to the site where cluster was originally provisioned
- Must match the site used during provisioning

**Valid values**: Valid Fyre site code (e.g., `svl`, `rtp`, `raleigh`)

**Impact**: Determines where to look for the cluster. Incorrect site will cause deprovisioning to fail.

**Related variables**:
- `cluster_name`: Cluster to deprovision at this site

**Note**: Must match the site where the cluster was originally provisioned. SVL is the default and most commonly used site.


Role Variables - IPI
-------------------------------------------------------------------------------
The following variables are only used when `cluster_type = ipi`.

### ipi_dir
Working directory for IPI deprovisioning.

- **Optional**
- Environment Variable: `IPI_DIR`
- Default: `~/openshift-install`

**Purpose**: Specifies the directory containing the openshift-install executable and cluster metadata required for deprovisioning.

**When to use**:
- Use default if cluster was provisioned with default directory
- Set to match the directory used during cluster provisioning
- Directory must contain cluster metadata for deprovisioning

**Valid values**: Absolute filesystem path

**Impact**: Deprovisioning requires cluster metadata from this directory. Incorrect path will cause deprovisioning to fail.

**Related variables**:
- `cluster_name`: Cluster metadata stored in subdirectory

**Note**: Must be the same directory used during cluster provisioning. The directory contains cluster metadata required for proper cleanup of all resources.

### ipi_platform
Cloud platform for IPI cluster deprovisioning.

- **Required** (when `cluster_type=ipi`)
- Environment Variable: `IPI_PLATFORM`
- Default: None

**Purpose**: Specifies which cloud platform the IPI cluster was deployed on. Determines which provider-specific credentials are required for deprovisioning.

**When to use**:
- Always required for IPI cluster deprovisioning
- Must match the platform used during provisioning
- Each platform requires different credentials

**Valid values**: `aws`, `gcp`

**Impact**: Determines which cloud provider is used for deprovisioning and which credentials are required.

**Related variables**:
- `aws_access_key_id`, `aws_secret_access_key`: Required when `aws`
- `gcp_service_account_file`: Required when `gcp`

**Note**: Must match the platform used during cluster provisioning. AWS and GCP are supported.

Role Variables - AWS
-------------------------------------------------------------------------------
The following variables are only used when `cluster_type = ipi` and `ipi_platform = aws`.

### aws_access_key_id
AWS access key ID for authentication.

- **Required** (when `cluster_type=ipi` and `ipi_platform=aws`)
- Environment Variable: `AWS_ACCESS_KEY_ID`
- Default: None

**Purpose**: Authenticates with AWS to deprovision IPI cluster infrastructure. Must have permissions to delete VPCs, instances, load balancers, and other AWS resources.

**When to use**:
- Always required for AWS IPI cluster deprovisioning
- Must be associated with IAM user or role with deletion permissions
- Can be same credentials used for provisioning

**Valid values**: AWS access key ID string (typically 20 characters, starts with `AKIA`)

**Impact**: Without valid credentials with appropriate permissions, cluster deprovisioning will fail or be incomplete.

**Related variables**:
- `aws_secret_access_key`: Secret key paired with this access key ID

**Note**: The IAM user/role must have permissions to delete all cluster resources (VPC, EC2, ELB, Route53, IAM, etc.). Incomplete permissions may leave orphaned resources.

### aws_secret_access_key
AWS secret access key for authentication.

- **Required** (when `cluster_type=ipi` and `ipi_platform=aws`)
- Environment Variable: `AWS_SECRET_ACCESS_KEY`
- Default: None

**Purpose**: Authenticates with AWS to deprovision IPI cluster infrastructure. Paired with AWS access key ID for authentication.

**When to use**:
- Always required for AWS IPI cluster deprovisioning
- Must correspond to the provided access key ID
- Keep secure and rotate regularly

**Valid values**: AWS secret access key string (typically 40 characters)

**Impact**: Without valid credentials, cluster deprovisioning will fail.

**Related variables**:
- `aws_access_key_id`: Access key ID paired with this secret key

**Note**: Keep secret keys secure. Ensure credentials have permissions to delete all cluster resources to avoid orphaned resources.

Role Variables - GCP
-------------------------------------------------------------------------------
The following variables are only used when `cluster_type = ipi` and `ipi_platform = gcp`.

### gcp_service_account_file
Path to GCP service account credentials file.

- **Required** (when `cluster_type=ipi` and `ipi_platform=gcp`)
- Environment Variable: `GOOGLE_APPLICATION_CREDENTIALS`
- Default: None

**Purpose**: Authenticates with Google Cloud Platform to deprovision IPI cluster infrastructure. Service account must have permissions to delete instances and networking resources.

**When to use**:
- Always required for GCP IPI cluster deprovisioning
- Must be a valid service account JSON key file
- Service account must have cluster deletion permissions

**Valid values**: Absolute path to GCP service account JSON key file

**Impact**: Without valid credentials with appropriate permissions, cluster deprovisioning will fail or be incomplete.

**Related variables**:
- `cluster_name`: Cluster to deprovision

**Note**: The service account must have permissions to delete all cluster resources (Compute, Networking, IAM, etc.). Can be same service account used for provisioning. Incomplete permissions may leave orphaned resources.


Example Playbook
-------------------------------------------------------------------------------

```yaml
- hosts: localhost
  vars:
    cluster_name: mycluster
    cluster_type: roks

    ibmcloud_apikey: xxxxx
  roles:
    - ibm.mas_devops.ocp_deprovision
```

License
-------------------------------------------------------------------------------

EPL-2.0
