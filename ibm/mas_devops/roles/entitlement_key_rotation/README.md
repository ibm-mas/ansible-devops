entitlement_key_rotation
===============================================================================

This role creates/updates the entitlement username and password that are stored in the secrets used to pull images throughout all MAS related namespaces for one or multiple clusters.

The main secret that is updated by this role is the `ibm-entitlement` which holds the credentials needed to pull the MAS images used by MAS Core or the MAS applications.

By default, this role will search for all MAS related namespaces that might contain the secret that holds the entitlement key to be updated. 

The list of namespaces to be updated with new username/password credentials are:

- All namespaces starting with `mas-`, which means by default it will update the `ibm-entitlement` secret with the new username/password credentials for all MAS namespaces/instances in the cluster.
- SLS namespace - holds `ibm-entitlement` which pulls Suite License Services related images.
- `openshift-marketplace` - holds `wiot-docker-local` which pulls the pre-release/development catalog source image for `ibm-operator-catalog`. Requires the `artifactory_username` and `artifactory_token` to be set.

**Note**
This role uses [`ocp_login`](../roles/ocp_login.md) to login into the target clusters, therefore make sure you export the corresponding environment variables accordingly to the cluster type you want to target.

Role Variables
-------------------------------------------------------------------------------
### artifactory_username 

- Required to rotate the `ibm-entitlement` and `wiotp-docker-local` secret credentials which is used to pull images across MAS namespaces for development installs and pre-release catalog sources.
- Environment Variable: `ARTIFACTORY_USERNAME`
- Default Value: None

### artifactory_token

- Required to rotate the `ibm-entitlement` and `wiotp-docker-local` secret credentials which is used to pull images across MAS namespaces for development installs and pre-release catalog sources.
- Environment Variable: `ARTIFACTORY_TOKEN`
- Default Value: None

### mas_entitlement_username

- Required to rotate the `ibm-entitlement` secret credentials only, which is used to pull images across MAS namespaces for MAS installs using release catalog sources.
- Environment Variable: `MAS_ENTITLEMENT_USERNAME`
- Default Value: None


### mas_entitlement_key
- Required to rotate the `ibm-entitlement` secret credentials only, which is used to pull images across MAS namespaces for MAS installs using release catalog sources.
- Environment Variable: `MAS_ENTITLEMENT_KEY`
- Default Value: None

### cluster_name
- Required. The target cluster to rotate the credentials/entitlement key secrets.
- Environment Variable: `CLUSTER_NAME`
- Default Value: None

### sls_namespace
- Optional. Defines the SLS namespace that holds `ibm-entitlement` secret which pulls Suite License Services related images.
- Environment Variable: `SLS_NAMESPACE`
- Default Value: `ibm-sls`

Role Variables - Advanced mode
-------------------------------------------------------------------------------

Use the following variables to change the default behavior of this role to only rotate the entitlement key for specific clusters or namespaces, instead of running it for all MAS related namespaces.

### mas_clusters_entitlement_key_rotation_list
- Optionally define a list of clusters to loop through the entitlement key rotation.
- Environment Variable: `MAS_CLUSTERS_ENTITLEMENT_KEY_ROTATION_LIST`
- Default Value: If not set, the `cluster_name` property will be used to target the cluster while executing this role.
- Example:
`export MAS_CLUSTERS_ENTITLEMENT_KEY_ROTATION_LIST='cluster1,cluster2'`

### mas_namespaces_entitlement_key_rotation_list
- Optionally define a specific list of namespaces to loop through the entitlement key rotation.
- Environment Variable: `MAS_NAMESPACES_ENTITLEMENT_KEY_ROTATION_LIST`
- Default Value: If not set, all MAS related namespaces for all MAS instances will be target for entitlement key rotation.
- Example:
`export MAS_NAMESPACES_ENTITLEMENT_KEY_ROTATION_LIST='ibm-sls,openshift-marketplace'`

Example Playbook
-------------------------------------------------------------------------------

Rotate entitlement credentials across all MAS instances for a given target cluster:

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    cluster_name: "{{ lookup('env', 'CLUSTER_NAME') }}"
    cluster_type: "{{ lookup('env', 'CLUSTER_TYPE') }}"
    ibmcloud_apikey: "{{ lookup('env', 'IBMCLOUD_APIKEY') }}"
    artifactory_username: "{{ lookup('env', 'ARTIFACTORY_USERNAME') }}"
    artifactory_token: "{{ lookup('env', 'ARTIFACTORY_TOKEN') }}"
    mas_entitlement_username: "{{ lookup('env', 'MAS_ENTITLEMENT_USERNAME') }}"
    mas_entitlement_key: "{{ lookup('env', 'MAS_ENTITLEMENT_KEY') }}"
  roles:
    - ibm.mas_devops.entitlement_key_rotation
```

Rotate entitlement credentials across a specific list of namespaces, targeting multiple clusters:

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    cluster_name: "{{ lookup('env', 'CLUSTER_NAME') }}" # this is the original cluster that will keep the login session context at the end of the rotation loop.
    cluster_type: "{{ lookup('env', 'CLUSTER_TYPE') }}"
    ibmcloud_apikey: "{{ lookup('env', 'IBMCLOUD_APIKEY') }}"
    artifactory_username: "{{ lookup('env', 'ARTIFACTORY_USERNAME') }}"
    artifactory_token: "{{ lookup('env', 'ARTIFACTORY_TOKEN') }}"
    mas_entitlement_username: "{{ lookup('env', 'MAS_ENTITLEMENT_USERNAME') }}"
    mas_entitlement_key: "{{ lookup('env', 'MAS_ENTITLEMENT_KEY') }}"
    mas_clusters_entitlement_key_rotation_list: "{{ lookup('env', 'MAS_CLUSTERS_ENTITLEMENT_KEY_ROTATION_LIST') }}"
    mas_namespaces_entitlement_key_rotation_list: "{{ lookup('env', 'MAS_NAMESPACES_ENTITLEMENT_KEY_ROTATION_LIST') }}"

  roles:
    - ibm.mas_devops.entitlement_key_rotation
```

License
-------

EPL-2.0
