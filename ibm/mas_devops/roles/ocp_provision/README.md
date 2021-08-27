ocp_provision
=============

Provision OCP cluster on DevIT Fyre or IBM Cloud ROKS.


Role Variables
--------------

- `cluster_name` Gives a name for the provisioning cluster
- `cluster_type` quickburn | roks
- `ocp_version` Openshift version for the provisioning cluster

!!! warning
    Different providers expect OCP version strings is slightly different formats.  For example in Fyre you would use something like `4.6.16`, whereas in IBM Cloud it would be `4.6_openshift`


#### ROKS specific facts
- `ibmcloud_apikey` APIKey to be used by ibmcloud login comand
- `roks_zone` IBM Cloud zone where the cluster should be provisioned
- `roks_flavor` Worker node flavor
- `roks_workers` Number of worker nodes for the roks cluster
- `roks_flags` Can be used to specify additional parameters for the cluster creation

#### Fyre specific facts
- `username` Required when cluster type is quickburn
- `password` Required when cluster type is quickburn
- `fyre_product_id` Required when cluster_type is quickburn Product Group Id to use for cluster provisioning
- `fyre_cluster_size` Required when cluster_type is quickburn, currently supports `medium` or `large`


Example Playbook
----------------

```yaml
- hosts: localhost
  vars:
    cluster_name: "{{ lookup('env', 'CLUSTER_NAME')}}"
    cluster_type: roks
    ibmcloud_apikey: "{{ lookup('env', 'IBMCLOUD_APIKEY') }}"

    ocp_version: "{{ lookup('env', 'OCP_VERSION') }}"

    roks_zone: "{{ lookup('env', 'ROKS_ZONE') | default('lon02', true) }}"
    roks_flavor: "{{ lookup('env', 'ROKS_FLAVOR') | default('b3c.16x64', true) }}"
    roks_workers: "{{ lookup('env', 'ROKS_WORKERS') | default('3', true) }}"
    roks_flags: "{{ lookup('env', 'ROKS_FLAGS') | default('', true) }}"
    ibmcloud_resourcegroup: "{{ lookup('env', 'IBMCLOUD_RESOURCEGROUP') | default('Default', true) }}"

  roles:
    - ibm.mas_devops.ocp_provision
    - ibm.mas_devops.ocp_setup_mas_deps
```

License
-------

EPL-2.0
