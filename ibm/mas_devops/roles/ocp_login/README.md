# ocp_login

This role provides support to login to a cluster using the `oc` CLI by looking up cluster information from the infrastructure provider's APIs, it also supports setting `ocp_server` and `ocp_token` directly to support login to any Kubernetes cluster.


## Role Variables

### cluster_name
Cluster name for credential lookup.

- **Required** (unless `ocp_server` and `ocp_token` are set)
- Environment Variable: `CLUSTER_NAME`
- Default: None

**Purpose**: Identifies the cluster to login to by name. Used to automatically lookup login credentials from the infrastructure provider's API.

**When to use**:
- Use with `cluster_type` for automatic credential lookup
- Alternative to manually providing `ocp_server` and `ocp_token`
- Recommended for managed clusters (ROKS, ROSA, Fyre)

**Valid values**: String matching your cluster name in the provider's system

**Impact**: Combined with `cluster_type`, automatically retrieves cluster server URL and login token from provider API.

**Related variables**:
- `cluster_type`: Required with this variable (roks, fyre, rosa)
- `ocp_server`/`ocp_token`: Alternative manual login method

**Note**: Requires provider-specific credentials (e.g., `ibmcloud_apikey` for ROKS, `rosa_token` for ROSA, `fyre_apikey` for Fyre).

### cluster_type
Infrastructure provider type for cluster.

- **Required** (unless `ocp_server` and `ocp_token` are set)
- Environment Variable: `CLUSTER_TYPE`
- Default: None

**Purpose**: Specifies the infrastructure provider type to determine which API to use for credential lookup.

**When to use**:
- Use with `cluster_name` for automatic credential lookup
- Required for managed cluster login
- Each type requires specific provider credentials

**Valid values**: `roks`, `fyre`, `rosa`
- `roks`: IBM Cloud Red Hat OpenShift Kubernetes Service
- `fyre`: IBM DevIT Fyre clusters
- `rosa`: AWS Red Hat OpenShift Service on AWS

**Impact**: Determines which provider API is called to retrieve cluster credentials. Each type requires different authentication variables.

**Related variables**:
- `cluster_name`: Cluster to lookup
- `ibmcloud_apikey`: Required for `roks`
- `fyre_username`/`fyre_apikey`: Required for `fyre`
- `rosa_token`: Required for `rosa`

**Note**: Alternative to using `ocp_server` and `ocp_token` for direct login.

### ocp_server
OpenShift server URL for direct login.

- **Required** (unless `cluster_name` and `cluster_type` are set)
- Environment Variable: `OCP_SERVER`
- Default: None

**Purpose**: Specifies the OpenShift API server URL for direct cluster login without provider API lookup.

**When to use**:
- Use with `ocp_token` for direct login
- When cluster is not managed by supported providers
- For custom or on-premises clusters
- Alternative to `cluster_name`/`cluster_type` approach

**Valid values**: Full OpenShift API server URL (e.g., `https://api.cluster.example.com:6443`)

**Impact**: Used directly for `oc login` command. Bypasses provider API credential lookup.

**Related variables**:
- `ocp_token`: Required with this variable
- `cluster_name`/`cluster_type`: Alternative automatic lookup method

**Note**: Both `ocp_server` and `ocp_token` must be provided together for direct login. This method works with any Kubernetes cluster.

### ocp_token
Authentication token for direct login.

- **Required** (unless `cluster_name` and `cluster_type` are set)
- Environment Variable: `OCP_TOKEN`
- Default: None

**Purpose**: Provides the authentication token for direct cluster login without provider API lookup.

**When to use**:
- Use with `ocp_server` for direct login
- When cluster is not managed by supported providers
- For service account tokens or manually obtained tokens
- Alternative to `cluster_name`/`cluster_type` approach

**Valid values**: Valid OpenShift authentication token string

**Impact**: Used directly for `oc login --token` command. Bypasses provider API credential lookup.

**Related variables**:
- `ocp_server`: Required with this variable
- `cluster_name`/`cluster_type`: Alternative automatic lookup method

**Note**: **SECURITY** - Both `ocp_server` and `ocp_token` must be provided together. Token should be kept secure and not committed to version control. This method works with any Kubernetes cluster.


Role Variables - IBMCloud ROKS
### ibmcloud_apikey
IBM Cloud API key for ROKS authentication.

- **Required** (when `cluster_type=roks`)
- Environment Variable: `IBMCLOUD_APIKEY`
- Default: None

**Purpose**: Provides IBM Cloud API key for authenticating with IBM Cloud to retrieve ROKS cluster credentials.

**When to use**:
- Required when `cluster_type=roks`
- Used to authenticate with IBM Cloud API
- Enables automatic cluster credential lookup

**Valid values**: Valid IBM Cloud API key string

**Impact**: Used to authenticate with IBM Cloud and retrieve cluster server URL and login token for ROKS clusters.

**Related variables**:
- `cluster_type`: Must be `roks`
- `cluster_name`: ROKS cluster name to lookup
- `ibmcloud_endpoint`: Optional API endpoint override

**Note**: **SECURITY** - API key should be kept secure and not committed to version control. Obtain from IBM Cloud IAM.

### ibmcloud_endpoint
IBM Cloud API endpoint URL.

- **Optional**
- Environment Variable: `IBMCLOUD_ENDPOINT`
- Default: `https://cloud.ibm.com`

**Purpose**: Overrides the default IBM Cloud API endpoint for ROKS cluster credential lookup.

**When to use**:
- Use default for public IBM Cloud
- Override for private or regional endpoints
- Only applies when `cluster_type=roks`

**Valid values**: Valid IBM Cloud API endpoint URL

**Impact**: Determines which IBM Cloud API endpoint is used for authentication and cluster lookup.

**Related variables**:
- `cluster_type`: Must be `roks`
- `ibmcloud_apikey`: Required for authentication

**Note**: The default public endpoint works for most deployments. Override only for specific regional or private cloud requirements.


Role Variables - IBM DevIT Fyre
### fyre_username
IBM DevIT Fyre username.

- **Required** (when `cluster_type=fyre`)
- Environment Variable: `FYRE_USERNAME`
- Default: None

**Purpose**: Provides Fyre username for authenticating with IBM DevIT Fyre to retrieve cluster credentials.

**When to use**:
- Required when `cluster_type=fyre`
- Used with `fyre_apikey` for Fyre authentication
- Enables automatic cluster credential lookup

**Valid values**: Valid Fyre username string

**Impact**: Used to authenticate with Fyre API and retrieve cluster server URL and login token.

**Related variables**:
- `cluster_type`: Must be `fyre`
- `fyre_apikey`: Required for authentication
- `cluster_name`: Fyre cluster name to lookup
- `fyre_site`: Fyre site location

**Note**: Fyre is IBM's internal development and test infrastructure. Requires IBM internal credentials.

### fyre_apikey
IBM DevIT Fyre API key.

- **Required** (when `cluster_type=fyre`)
- Environment Variable: `FYRE_APIKEY`
- Default: None

**Purpose**: Provides Fyre API key for authenticating with IBM DevIT Fyre to retrieve cluster credentials.

**When to use**:
- Required when `cluster_type=fyre`
- Used with `fyre_username` for Fyre authentication
- Enables automatic cluster credential lookup

**Valid values**: Valid Fyre API key string

**Impact**: Used to authenticate with Fyre API and retrieve cluster server URL and login token.

**Related variables**:
- `cluster_type`: Must be `fyre`
- `fyre_username`: Required for authentication
- `cluster_name`: Fyre cluster name to lookup
- `fyre_site`: Fyre site location

**Note**: **SECURITY** - API key should be kept secure. Fyre is IBM's internal development and test infrastructure.

### fyre_site
Fyre site location for cluster.

- **Optional**
- Environment Variable: `FYRE_SITE`
- Default: `svl`

**Purpose**: Specifies which Fyre site the cluster was provisioned in for proper API routing.

**When to use**:
- Use default (`svl`) for most Fyre clusters
- Override for clusters in other sites (e.g., `rtp`)
- Only applies when `cluster_type=fyre`

**Valid values**: Fyre site codes (e.g., `svl`, `rtp`)

**Impact**: Determines which Fyre site API endpoint is used for cluster lookup.

**Related variables**:
- `cluster_type`: Must be `fyre`
- `enable_ipv6`: Required for RTP site

**Note**: SVL (San Jose Valley) is the default site. RTP (Research Triangle Park) requires IPv6 enablement.

### enable_ipv6
Enable IPv6 for Fyre RTP site.

- **Optional**
- Environment Variable: `ENABLE_IPV6`
- Default: `false`

**Purpose**: Enables IPv6 networking for Fyre clusters at the RTP (Research Triangle Park) site.

**When to use**:
- Set to `true` only for Fyre RTP site clusters
- Leave as `false` for all other sites (including SVL)
- Only applies when `cluster_type=fyre`

**Valid values**: `true`, `false`

**Impact**: Configures network settings for IPv6 connectivity to RTP site clusters.

**Related variables**:
- `cluster_type`: Must be `fyre`
- `fyre_site`: Should be `rtp` when this is `true`

**Note**: Only required for Fyre RTP site. SVL and other sites use IPv4.

Role Variables - AWS ROSA
### rosa_token
AWS ROSA authentication token.

- **Required** (when `cluster_type=rosa`)
- Environment Variable: `ROSA_TOKEN`
- Default: None

**Purpose**: Provides ROSA (Red Hat OpenShift Service on AWS) authentication token for retrieving cluster credentials.

**When to use**:
- Required when `cluster_type=rosa`
- Used to authenticate with ROSA API
- Enables automatic cluster credential lookup

**Valid values**: Valid ROSA authentication token string

**Impact**: Used to authenticate with ROSA API and retrieve cluster server URL and login credentials.

**Related variables**:
- `cluster_type`: Must be `rosa`
- `cluster_name`: ROSA cluster name to lookup
- `rosa_cluster_admin_password`: Required for cluster-admin login

**Note**: **SECURITY** - Token should be kept secure and not committed to version control. Obtain from Red Hat Hybrid Cloud Console.

### rosa_cluster_admin_password
ROSA cluster-admin account password.

- **Required** (when `cluster_type=rosa`)
- Environment Variable: `ROSA_CLUSTER_ADMIN_PASSWORD`
- Default: None

**Purpose**: Provides the password for the cluster-admin account to login to ROSA clusters.

**When to use**:
- Required when `cluster_type=rosa`
- Password created during cluster provisioning
- Used for cluster-admin level access

**Valid values**: Valid cluster-admin password string

**Impact**: Used to authenticate as cluster-admin user on ROSA clusters.

**Related variables**:
- `cluster_type`: Must be `rosa`
- `rosa_token`: Required for ROSA API authentication
- `cluster_name`: ROSA cluster name to login to

**Note**: **SECURITY** - Password should be kept secure and not committed to version control. This is the cluster-admin account password set during ROSA cluster provisioning.

Example Playbooks

### Direct Login
```yaml
- hosts: localhost
  vars:
    ocp_server: xxxxx
    ocp_token: xxxxx
  roles:
    - ibm.mas_devops.ocp_login
```

### IBMCloud ROKS
```yaml
- hosts: localhost
  vars:
    cluster_name: mycluster
    cluster_type: roks
    ibmcloud_apikey: xxxxx
    ibmcloud_resourcegroup: mygroup
  roles:
    - ibm.mas_devops.ocp_login
```

### AWS ROSA
```yaml
- hosts: localhost
  vars:
    cluster_name: mycluster
    cluster_type: rosa
    rosa_token: xxxxx
    rosa_cluster_admin_password: xxxxx
  roles:
    - ibm.mas_devops.ocp_login
```

### IBM DevIT Fyre
```yaml
- hosts: localhost
  vars:
    cluster_name: mycluster
    cluster_type: fyre
    fyre_username: xxxxx
    fyre_password: xxxxx
  roles:
    - ibm.mas_devops.ocp_login
```


## Example Playbook

```yaml
- hosts: localhost
  vars:
    # Add required variables here
  roles:
    - ibm.mas_devops.ocp_login
```

## License

EPL-2.0
