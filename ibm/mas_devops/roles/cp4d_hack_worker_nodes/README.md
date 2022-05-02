cp4d_hack_worker_nodes
======================

This should be executed as part of cluster prepararion if you want to use CP4D v4.  It will reboot all worker nodes, causing disruption to the entire cluster and everything running on it we do not include this as part of the normal flow because, well it shouldn't be necessary to reboot worker nodes to install containerized software.  Hopefully this is just an example of poor documentation and there's a simple alternative that we can implement to remove this role.

For more information, refer to https://cloud.ibm.com/docs/openshift?topic=openshift-registry#cluster_global_pull_secret


Role Variables
--------------

### cluster_type
Required.  Note that only supported value at present is `roks`.

- Environment Variable: `CLUSTER_TYPE`
- Default Value: None

### cluster_name
Required.  The name of the ROKS cluster that we are going to apply the CP4D hack to.

- Environment Variable: `CLUSTER_NAME`
- Default Value: None

### ibmcloud_apikey
Required.  Provide your IBM Cloud API Key, this will be used to query the status of the cluster and issue the node restart commands.

- Environment Variable: `IBMCLOUD_APIKEY`
- Default Value: None

### cpd_entitlement_key
Required.  Provide your IBM Entitlement Key.

- Environment Variable: `CPD_ENTITLEMENT_KEY`
- Default Value: None


Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    cluster_name: mycluster
    cluster_type: roks
    ibmcloud_apikey: "{{ lookup('env', 'IBMCLOUD_APIKEY') }}"

    cpd_entitlement_key: "{{ lookup('env', 'CPD_ENTITLEMENT_KEY') }}"

  roles:
    - ibm.mas_devops.cp4d_hack_worker_nodes
```

License
-------

EPL-2.0
