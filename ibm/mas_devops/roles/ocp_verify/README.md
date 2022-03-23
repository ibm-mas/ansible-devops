ocp_verify
==========

This role will verify that a provisioned OCP cluster is ready to be setup for MAS.

In IBMCloud ROKS we have seen delays of over an hour before the Red Hat Operator catalog is ready to use.  This will cause attempts to install anything from that CatalogSource to fail as the timeouts built into those roles are designed to catch problems with an install, rather than a half-provisioned cluster that is not properly ready to use.


Role Variables
--------------
The role requires no variables itself, but depends on the `ibm.mas_devops.ocp_login` role, and as such inherits it's requirements. If you set `ocp_server` and `ocp_token` then a non cluster type specific login is attempted rather than using the cluster_type specific facts (apikey or username/password).

- `cluster_name` Gives a name for the provisioning cluster
- `cluster_type` quickburn | roks

#### ROKS specific facts
- `ibmcloud_apikey` APIKey to be used by ibmcloud login comand

#### Fyre specific facts
- `username` Required when cluster type is quickburn
- `password` Required when cluster type is quickburn

#### Non cluster_type specific facts
- `ocp_server` The OCP server address to perform oc login against
- `ocp_token` The login token to use for oc login


Example Playbook
----------------

```yaml
- hosts: localhost
  vars:
    cluster_name: "{{ lookup('env', 'CLUSTER_NAME')}}"
    cluster_type: roks
    ibmcloud_apikey: "{{ lookup('env', 'IBMCLOUD_APIKEY') }}"
    ibmcloud_resourcegroup: "{{ lookup('env', 'IBMCLOUD_RESOURCEGROUP') | default('Default', true) }}"
  roles:
    - ibm.mas_devops.ocp_verify
```


License
-------

EPL-2.0
