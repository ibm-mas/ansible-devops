# OCP Roles
The following roles does provide support to provision, deprovision and configure OCP cluster for MAS. Currently the collection provides support for 3 types of clusters.

!!! note "Note"
    For Fyre based cluster make sure you have a valid fyre user id, apikey and the user is also part of a Product Group.

- Quickburn: Short term cluster on Fyre platform, this type of cluster does not requires user quota but will only exist for maximum of 36 hours.
- Product Group: Long term cluster on Fyre platform, requires user individual quota to provision this type of cluster
- Roks: IBM Cloud hosted cluster

## ocp_provision
Provision OCP cluster on Fyre and IBM Cloud.

!!! warning "Warning"
    Different providers expect OCP version strings is slightly different formats.  For example in Fyre you would use something like `4.6.16`, whereas in IBM Cloud it would be `4.6_openshift`

### Role Facts
List of role facts defined by a playbook and required by this role.

- `cluster_name` Gives a name for the provisioning cluster
- `cluster_type` quickburn | product_group | roks
- `ocp_version` Openshift version for the provisioning cluster

#### ROKS specific facts
- `ibmcloud_apikey` APIKey to be used by ibmcloud login comand
- `roks_zone` IBM Cloud zone where the cluster should be provisioned
- `roks_flavor` Worker node flavor
- `roks_workers` Number of worker nodes for the roks cluster
- `roks_flags` Can be used to specify additional parameters for the cluster creation

#### Fyre specific facts
- `username` Required when cluster type is quickburn or product_group
- `password` Required when cluster type is quickburn or product_group
- `fyre_product_id` Required when cluster_type is quickburn or product_group Product Group Id to use for cluster provisioning

#### Quick Burn specific facts
- `fyre_cluster_size` Required when cluster_type is quickburn, currently supports `medium` or `large`

#### Product group specific facts
- `workers_count` Number of workers to be provisioned for the product group cluster


## ocp_deprovision
Deprovision OCP cluster in Fyre and IBM Cloud

### Role Facts
List of role facts defined by a playbook and required by this role.

- `cluster_name` Gives a name for the provisioning cluster
- `cluster_type` quickburn | product_group | roks

#### ROKS specific facts
- `ibmcloud_apikey` APIKey to be used by ibmcloud login comand

#### Fyre specific facts
- `username` Required when cluster type is quickburn or product_group
- `password` Required when cluster type is quickburn or product_group


## ocp_login
This role provides support to login to a cluster using the `oc cli`

### Role Facts
List of role facts defined by a playbook and required by this role.

- `cluster_name` Gives a name for the provisioning cluster
- `cluster_type` quickburn | product_group | roks

#### ROKS specific facts
- `ibmcloud_apikey` APIKey to be used by ibmcloud login comand

#### Fyre specific facts
- `username` Required when cluster type is quickburn or product_group
- `password` Required when cluster type is quickburn or product_group


## ocp_setup_github_oauth
This role provides to support to configure cluster oauth using GitHub.

!!! warning "Warning"
    Make sure you have configured the oauth app in GitHub organization before use this role. When configuring make sure to use `ibmgithub` as the oauth id. Requires organization admin permission to perform this action.

### Role facts
List of role facts defined by a playbook and required by this role.

- `oauth.github_client_secret_value` Secret value provided by the GitHub oauth app configuration.
- `ouath.github_client_id_value` Client ID value provided by the GitHub oauth app configuration.
- `oauth.github_hostname` can be used to target public GitHub or an enterprise account (e.g. github.ibm.com)
- `oauth.groups` List of groups to be created and its cluster role bindings
- `oauth.groups.name` Defines the name of the group
- `oauth.groups.users` List of users to be added to the group
- `oauth.groups.groups_cluster_rolebindings` List of cluster role bindings to be created for the group
- `oauth.organizations` List of GitHub organizations where the authentication will be performed


## ocp_setup_mas_deps
This role provides support to install operators that are required by MAS to work. The role will deploy Service Binding Operator in all namespaces and Cert Manager in the cert-manager namespace.

!!! note
    There are no facts included in this role, make sure to use this role in conjuction with [ocp_provivion](#ocp_provision) and [ocp_login](#ocp_login) to fulfill the requirements


## ocp_setup_ocs
This role provides support to install Openshift Container Storage. This role is not used by defualt when setting up IBM Cloud OpenShift clusters because they are automatically provisioned with their own storage plugin already.

!!! note
    There are no facts included in this role, make sure to use this role in conjuction with [ocp_provivion](#ocp_provision) and [ocp_login](#ocp_login) to fulfill the requirements
