ocp_login
=========

This role provides support to login to a cluster using the `oc` CLI by looking up cluster information from the infrastructure provider's APIs, it also supports setting `ocp_server` and `ocp_token` directly to support login to any Kubernetes cluster.


Role Variables
--------------

### cluster_name
The name of the cluster to login to.  This will be used to lookup the actual login credentials of the system.

- **Required** unless `ocp_server` and `ocp_token` are set
- Environment Variable: `CLUSTER_NAME`
- Default: None

### cluster_type
The type of cluster to login to (`roks`, `fyre`, or `rosa`)

- **Required** unless `ocp_server` and `ocp_token` are set
- Environment Variable: `CLUSTER_TYPE`
- Default: None

### ocp_server
The OCP server address to perform oc login against

- **Required** unless `cluster_name` and `cluster_type` are set
- Environment Variable: `OCP_SERVER`
- Default: None

### ocp_token
The login token to use for oc login

- **Required** unless `cluster_name` and `cluster_type` are set
- Environment Variable: `OCP_TOKEN`
- Default: None


Role Variables - IBMCloud ROKS
------------------------------
### ibmcloud_apikey
APIKey to be used by ibmcloud login comand

- **Required** when `cluster_type` is `roks`
- Environment Variable: `IBMCLOUD_APIKEY`
- Default: None

### ibmcloud_endpoint
Override the default IBMCloud API endpoint.

- Optional
- Environment Variable: `IBMCLOUD_ENDPOINT`
- Default Value: `https://cloud.ibm.com`


Role Variables - IBM DevIT Fyre
------------------------------
### fyre_username
Your FYRE username

- **Required** when `cluster_type` is `fyre`
- Environment Variable: `FYRE_APIKEY`
- Default: None

### fyre_apikey
Your FYRE API Key
- **Required** when `cluster_type` is `fyre`
- Environment Variable: `FYRE_APIKEY`
- Default: None

### fyre_site
Site where cluster had been provisioned in Fyre

- Optional
- Environment Variable: `FYRE_SITE`
- Default Value: `svl`

### enable_ipv6
Enable IPv6.  This is for Fyre at RTP site only
- Environment Variable: `ENABLE_IPV6`
- Default: False

Role Variables - AWS ROSA
-------------------------
### rosa_token
Your ROSA secure token.

- **Required** when `cluster_type` is `rosa`
- Environment Variable: `ROSA_TOKEN`
- Default: None

### rosa_cluster_admin_password
The password for the `cluster-admin` account (created when the cluster was provisioned).

- **Required** when `cluster_type` is `rosa`
- Environment Variable: `ROSA_CLUSTER_ADMIN_PASSWORD`
- Default: None

Example Playbooks
----------------

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

License
-------

EPL-2.0
