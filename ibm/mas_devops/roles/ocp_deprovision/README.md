# ocp_deprovision
Deprovision OCP cluster in Fyre, IBM Cloud, & ROSA.

!!! warning "Destructive Operation"
    Deprovisioning permanently deletes the cluster and all of its resources. This operation cannot be undone — always verify the cluster type and name, and back up any critical data, before running this role.

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`cluster_type`](#cluster_type) | Yes | None |
| [`cluster_name`](#cluster_name) | Yes | None |
| [`ibmcloud_apikey`](#ibmcloud_apikey) | Conditional | None |
| [`rosa_token`](#rosa_token) | Conditional | None |
| [`fyre_username`](#fyre_username) | Conditional | None |
| [`fyre_apikey`](#fyre_apikey) | Conditional | None |
| [`fyre_site`](#fyre_site) | No | `svl` |
| [`ipi_dir`](#ipi_dir) | No | `~/openshift-install` |
| [`ipi_platform`](#ipi_platform) | Conditional | None |
| [`aws_access_key_id`](#aws_access_key_id) | Conditional | None |
| [`aws_secret_access_key`](#aws_secret_access_key) | Conditional | None |
| [`aws_region`](#aws_region) | No | `eu-west-2` |
| [`gcp_service_account_file`](#gcp_service_account_file) | Conditional | None |

The provider-specific credentials are only required when `cluster_type` matches that provider (and, for the cloud credentials, when `ipi_platform` matches the platform).

### Cluster Identification

#### cluster_type

Infrastructure provider the cluster was provisioned with — one of `fyre` (IBM DevIT Fyre), `roks` (IBM Cloud Red Hat OpenShift Kubernetes Service), `roks-vpc` (ROKS on VPC infrastructure), `rosa` (Red Hat OpenShift Service on AWS), or `ipi` (Installer-Provisioned Infrastructure on AWS or GCP).

- **Required**
- Environment Variable: `CLUSTER_TYPE`
- Default: None

Determines the deprovisioning workflow and which provider-specific variables are required. `quickburn` is accepted as a backwards-compatible alias for `fyre`. The value must match the provider used to create the cluster, otherwise deprovisioning will fail.

#### cluster_name

Name of the cluster to deprovision — a string that must exactly match the cluster name in the provider's system.

- **Required**
- Environment Variable: `CLUSTER_NAME`
- Default: None

Identifies which cluster is located and deleted in the provider's system. Verify the name carefully before proceeding — an incorrect name may cause the wrong cluster to be deleted.

### ROKS

#### ibmcloud_apikey

IBM Cloud API key used to authenticate with IBM Cloud for ROKS cluster deletion — a key string (typically 40+ characters) whose IAM permissions allow cluster deletion in the resource group.

- **Required** when `cluster_type` is `roks` or `roks-vpc`
- Environment Variable: `IBMCLOUD_APIKEY`
- Default: None

The same API key used for cluster provisioning can be reused. Without a valid API key with delete permissions, cluster deprovisioning will fail.

### ROSA

#### rosa_token

ROSA API token used to authenticate with the ROSA service — obtained from [OpenShift Cluster Manager](https://console.redhat.com/openshift/token/rosa/show#); the token must be valid and not expired.

- **Required** when `cluster_type` is `rosa`
- Environment Variable: `ROSA_TOKEN`
- Default: None

Tokens expire periodically, so obtain a fresh token before deprovisioning. ROSA deprovisioning also uses `aws_access_key_id`, `aws_secret_access_key`, and `aws_region` to clean up the cluster's EFS file storage.

### Fyre

#### fyre_username

Fyre username for authenticating with the IBM DevIT Fyre API — a valid Fyre account username (IBM intranet ID).

- **Required** when `cluster_type` is `fyre`
- Environment Variable: `FYRE_USERNAME`
- Default: None

Fyre is an internal IBM development platform — access requires IBM credentials and appropriate permissions.

#### fyre_apikey

Fyre API key for authentication, paired with `fyre_username` — obtained from the Fyre portal; keys may expire and need renewal.

- **Required** when `cluster_type` is `fyre`
- Environment Variable: `FYRE_APIKEY`
- Default: None

Keep the API key secure and rotate it regularly.

#### fyre_site

Fyre datacenter site where the cluster was provisioned — a valid Fyre site code (e.g. `svl`, `rtp`, `raleigh`).

- **Optional**
- Environment Variable: `FYRE_SITE`
- Default: `svl`

`svl` (San Jose/Silicon Valley) is the default and most commonly used site. Must match the site used during provisioning — an incorrect site will cause deprovisioning to fail.

### IPI

The following variables are only used when `cluster_type = ipi`.

#### ipi_dir

Working directory for IPI deprovisioning, containing the `openshift-install` executable and the cluster metadata required for deprovisioning — an absolute filesystem path.

- **Optional**
- Environment Variable: `IPI_DIR`
- Default: `~/openshift-install`

Must match the directory used during cluster provisioning; the cluster metadata (under `config/{cluster_name}` in this directory) is required for proper cleanup of all resources. An incorrect path will cause deprovisioning to fail.

#### ipi_platform

Cloud platform the IPI cluster was deployed on — `aws` or `gcp`.

- **Required** when `cluster_type` is `ipi`
- Environment Variable: `IPI_PLATFORM`
- Default: None

Must match the platform used during cluster provisioning. Determines which cloud credentials are required: `aws_access_key_id` and `aws_secret_access_key` for `aws`, or `gcp_service_account_file` for `gcp`.

### AWS

The following variables are used when `cluster_type = ipi` and `ipi_platform = aws`; `aws_access_key_id`, `aws_secret_access_key`, and `aws_region` are also used by ROSA deprovisioning to clean up EFS file storage.

#### aws_access_key_id

AWS access key ID for authenticating with AWS — a key ID string (typically 20 characters, starting with `AKIA`).

- **Required** when deprovisioning an IPI cluster with `ipi_platform=aws`
- Environment Variable: `AWS_ACCESS_KEY_ID`
- Default: None

The associated IAM user or role must have permissions to delete all cluster resources (VPC, EC2, ELB, Route53, IAM, etc.) — incomplete permissions may leave orphaned resources. For AWS IPI deprovisioning the credentials must be provided as environment variables (the OpenShift installer reads them from the environment), not just as Ansible variables.

#### aws_secret_access_key

AWS secret access key for authentication, paired with `aws_access_key_id` — a key string (typically 40 characters).

- **Required** when deprovisioning an IPI cluster with `ipi_platform=aws`
- Environment Variable: `AWS_SECRET_ACCESS_KEY`
- Default: None

Keep the secret key secure and rotate it regularly. Like the access key ID, it must be provided as an environment variable for AWS IPI deprovisioning.

#### aws_region

AWS region used when cleaning up cluster resources with the AWS CLI — for example `eu-west-2`.

- **Optional**
- Environment Variable: `AWS_DEFAULT_REGION`
- Default: `eu-west-2`

Used by ROSA deprovisioning to locate and delete the cluster's EFS file storage.

### GCP

The following variables are only used when `cluster_type = ipi` and `ipi_platform = gcp`.

#### gcp_service_account_file

Path to the GCP service account credentials file — an absolute path to a valid service account JSON key file, whose service account has permissions to delete instances and networking resources.

- **Required** when `cluster_type` is `ipi` and `ipi_platform` is `gcp`
- Environment Variable: `GOOGLE_APPLICATION_CREDENTIALS`
- Default: None

The service account must have permissions to delete all cluster resources (Compute, Networking, IAM, etc.); the same service account used for provisioning can be reused. Incomplete permissions may leave orphaned resources.

## Example Playbook

```yaml
- hosts: localhost
  vars:
    cluster_name: mycluster
    cluster_type: roks

    ibmcloud_apikey: xxxxx
  roles:
    - ibm.mas_devops.ocp_deprovision
```

## License

EPL-2.0
