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
    Fyre and Roks does have different versions for the same Openshift version. i.e OCP 4.6 in Fyre is 4.6.16 on roks is 4.6_openshift

### Role Facts
List of role facts defined by a playbook and required by this role.

- cluster_name: Gives a name for the provisioning cluster
- cluster_type: quickburn | product_group | roks
- ocp_version: Openshift version for the provisioning cluster


#### ROKS specific facts
- ibmcloud_apikey: APIKey to be used by ibmcloud login comand
- roks_zone: IBM Cloud zone where the cluster should be provisioned
- roks_flavor: Worker node flavor
- roks_workers: Number of worker nodes for the roks cluster
- roks_flags: Can be used to specify --public-endpoint

#### Fyre specific facts
- username: Required when cluster type is quickburn or product_group
- password: Required when cluster type is quickburn or product_group
- fyre_product_id: Required when cluster_type is quickburn or product_group Product Group Id to use for cluster provisioning

#### Quick Burn specific facts
- fyre_cluster_size: Required when cluster_type is quickburn, currently supports `medium` or `large`

#### Product group specific facts
- workers_count: Number of workers to be provisioned for the product group cluster


## ocp_deprovision
Deprovision OCP cluster in Fyre and IBM Cloud

### Role Facts
List of role facts defined by a playbook and required by this role.

- cluster_name: Gives a name for the provisioning cluster
- cluster_type: quickburn | product_group | roks


#### ROKS specific facts
- ibmcloud_apikey: APIKey to be used by ibmcloud login comand

#### Fyre specific facts
- username: Required when cluster type is quickburn or product_group
- password: Required when cluster type is quickburn or product_group


## ocp_login
This role provides support to login to a cluster using the `oc cli` 

### Role Facts
List of role facts defined by a playbook and required by this role.

- cluster_name: Gives a name for the provisioning cluster
- cluster_type: quickburn | product_group | roks


#### ROKS specific facts
- ibmcloud_apikey: APIKey to be used by ibmcloud login comand

#### Fyre specific facts
- username: Required when cluster type is quickburn or product_group
- password: Required when cluster type is quickburn or product_group

## ocp_setup_github_oauth
This role provides to suppor to configure cluster oauth using ibm github.
!!! warning "Warning"
    Make sure you have configured the oauth app in github organization before use this role. When configuring make sure to use `ibmgithub` as the oauth id. Requires organization admin permission to perform this action.

### Role facts
List of role facts defined by a playbook and required by this role.

 - oauth.github_client_secret_value: Secret value provided by the oauth app configuration done in github enterprise.
- ouath.github_client_id_value: Client Id value provided by the oauth app configuration done in github enterprise.
- oauth.github_hostname: github.ibm.com
- oauth. groups: List of groups to be created and its cluster role bindings
- oauth.groups.name: Defines the name of the group
- oauth.groups.users: List of user to be added to the group
- oauth.groups.groups_cluster_rolebindings: List of cluster role bindings to be created for the group
- oauth.organizations: List of github organizations where the authentication will be performed
    
## ocp_setup_mas_deps
This role provides support to install operators that are required by MAS to work. The role will deploy Service Binding Operator in all namespaces and Cert Manager in the cert-manager namespace. 

!!! note "Note"
    There is no fact for this role, make sure you do use this role in conjuction with ocp_provivion and ocp_login to fulfill the requirements


## ocp_setup_ocs
This role provides support to install Openshift Container Storage. Currently it is only required on Fyre based cluster since IBM Cloud ( ROKS ), is provisioned with its own storage plugin.

!!! note "Note"
    There is no fact for this role, make sure you do use this role in conjuction with ocp_provivion and ocp_login to fulfill the requirements
