ocp_login
=========

This role provides support to login to a cluster using the `oc cli`. If you set `ocp_server` and `ocp_token` then a non cluster type specific login is attempted rather than using the cluster_type specific facts (apikey or username/password).


Role Variables
--------------

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
    - ibm.mas_devops.ocp_login
```

License
-------

EPL-2.0
