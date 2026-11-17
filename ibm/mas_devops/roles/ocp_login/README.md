# ocp_login

This role provides support to login to a cluster using the `oc` CLI by looking up cluster information from the infrastructure provider's APIs, it also supports setting `ocp_server` and `ocp_token` directly to support login to any Kubernetes cluster.

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`cluster_name`](#cluster_name) | Conditional | None |
| [`cluster_type`](#cluster_type) | Conditional | None |
| [`ocp_server`](#ocp_server) | Conditional | None |
| [`ocp_token`](#ocp_token) | Conditional | None |
| [`ocp_skip_tls_verify`](#ocp_skip_tls_verify) | No | `true` |
| [`ibmcloud_apikey`](#ibmcloud_apikey) | Conditional | None |
| [`ibmcloud_endpoint`](#ibmcloud_endpoint) | No | `https://cloud.ibm.com` |
| [`fyre_username`](#fyre_username) | Conditional | None |
| [`fyre_apikey`](#fyre_apikey) | Conditional | None |
| [`fyre_site`](#fyre_site) | No | `svl` |
| [`rosa_token`](#rosa_token) | Conditional | None |
| [`rosa_cluster_admin_password`](#rosa_cluster_admin_password) | Conditional | None |

There are two login methods: either provide `cluster_name` and `cluster_type` for automatic credential lookup from the infrastructure provider's API (which also requires that provider's credentials), or provide `ocp_server` and `ocp_token` together for direct login to any Kubernetes cluster.

### Cluster Identification

#### cluster_name

Cluster name for credential lookup — a string matching your cluster name in the provider's system.

- **Required** (unless `ocp_server` and `ocp_token` are set)
- Environment Variable: `CLUSTER_NAME`
- Default: None

Combined with `cluster_type`, automatically retrieves the cluster server URL and login token from the provider API. This is the recommended approach for managed clusters (ROKS, ROSA, Fyre) and requires provider-specific credentials (e.g., `ibmcloud_apikey` for ROKS, `rosa_token` for ROSA, `fyre_username`/`fyre_apikey` for Fyre).

#### cluster_type

Infrastructure provider type for cluster, which determines which API is used for credential lookup — `roks` (IBM Cloud Red Hat OpenShift Kubernetes Service), `fyre` (IBM DevIT Fyre clusters), or `rosa` (Red Hat OpenShift Service on AWS).

- **Required** (unless `ocp_server` and `ocp_token` are set)
- Environment Variable: `CLUSTER_TYPE`
- Default: None

Each type requires different authentication variables: `ibmcloud_apikey` for `roks`, `fyre_username`/`fyre_apikey` for `fyre`, and `rosa_token` for `rosa`. The aliases `roks-vpc` (treated as `roks`) and `quickburn` (treated as `fyre`) are also accepted, and `in-cluster` skips the login entirely.

### Direct Login

#### ocp_server

OpenShift server URL for direct login — the full API server URL, for example `https://api.cluster.example.com:6443`.

- **Required** (unless `cluster_name` and `cluster_type` are set)
- Environment Variable: `OCP_SERVER`
- Default: None

Used directly for the `oc login` command, bypassing provider API credential lookup. Both `ocp_server` and `ocp_token` must be provided together; this method works with any Kubernetes cluster, including custom or on-premises clusters.

#### ocp_token

Authentication token for direct login — a valid OpenShift authentication token string, such as a service account token or a manually obtained token.

- **Required** (unless `cluster_name` and `cluster_type` are set)
- Environment Variable: `OCP_TOKEN`
- Default: None

Used directly for the `oc login --token` command, bypassing provider API credential lookup. Both `ocp_server` and `ocp_token` must be provided together.

#### ocp_skip_tls_verify

Disable the certificate check when logging in using the `ocp_server` and `ocp_token` properties.

- **Optional** — only applies to direct login with `ocp_server` and `ocp_token`
- Environment Variable: `OCP_SKIP_TLS_VERIFY`
- Default: `true`

### IBM Cloud ROKS

#### ibmcloud_apikey

IBM Cloud API key for ROKS authentication, obtained from IBM Cloud IAM.

- **Required** (when `cluster_type=roks`)
- Environment Variable: `IBMCLOUD_APIKEY`
- Default: None

Used to authenticate with the IBM Cloud API and retrieve the cluster server URL and login token for ROKS clusters. Keep the API key secure and do not commit it to version control.

#### ibmcloud_endpoint

IBM Cloud API endpoint URL used for authentication and cluster lookup.

- **Optional** — only applies when `cluster_type=roks`
- Environment Variable: `IBMCLOUD_ENDPOINT`
- Default: `https://cloud.ibm.com`

The default public endpoint works for most deployments; override it only for specific regional or private cloud requirements.

### IBM DevIT Fyre

#### fyre_username

IBM DevIT Fyre username.

- **Required** (when `cluster_type=fyre`)
- Environment Variable: `FYRE_USERNAME`
- Default: None

Used with `fyre_apikey` to authenticate with the Fyre API and retrieve the cluster server URL and login token. Fyre is IBM's internal development and test infrastructure and requires IBM internal credentials.

#### fyre_apikey

IBM DevIT Fyre API key.

- **Required** (when `cluster_type=fyre`)
- Environment Variable: `FYRE_APIKEY`
- Default: None

Used with `fyre_username` to authenticate with the Fyre API and retrieve the cluster server URL and login token. Keep the API key secure; Fyre is IBM's internal development and test infrastructure.

#### fyre_site

Fyre site location for the cluster — a Fyre site code such as `svl` or `rtp`.

- **Optional** — only applies when `cluster_type=fyre`
- Environment Variable: `FYRE_SITE`
- Default: `svl`

Determines which Fyre site API endpoint is used for cluster lookup; use the default (`svl`) for most Fyre clusters and override for clusters provisioned at other sites.

### AWS ROSA

#### rosa_token

AWS ROSA authentication token, obtained from the Red Hat Hybrid Cloud Console.

- **Required** (when `cluster_type=rosa`)
- Environment Variable: `ROSA_TOKEN`
- Default: None

Used to authenticate with the ROSA API and retrieve the cluster server URL and login credentials. Keep the token secure and do not commit it to version control.

#### rosa_cluster_admin_password

ROSA cluster-admin account password, created during cluster provisioning.

- **Required** (when `cluster_type=rosa`)
- Environment Variable: `ROSA_CLUSTER_ADMIN_PASSWORD`
- Default: None

Used to authenticate as the cluster-admin user on ROSA clusters. Keep the password secure and do not commit it to version control.

## Example Playbook

### Direct Login

```yaml
- hosts: localhost
  vars:
    ocp_server: xxxxx
    ocp_token: xxxxx
  roles:
    - ibm.mas_devops.ocp_login
```

### IBM Cloud ROKS

```yaml
- hosts: localhost
  vars:
    cluster_name: mycluster
    cluster_type: roks
    ibmcloud_apikey: xxxxx
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
    fyre_apikey: xxxxx
  roles:
    - ibm.mas_devops.ocp_login
```

## License

EPL-2.0
