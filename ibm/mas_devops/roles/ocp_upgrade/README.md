ocp_upgrade
=============

This role supports the upgrade of the Openshift Cluster version for master and worker nodes in IBM Cloud provider.

Role Variables
--------------

### cluster_type
Required.  Specify the cluster type, only IBM Cloud Openshift Clusters are supported by this role at the moment. If you provide a different cluster type than `roks`, this role will fail.

- Environment Variable: `CLUSTER_TYPE`
- Default Value: None

### cluster_name
Required.  Specify the name of the cluster to be upgraded.

- Environment Variable: `CLUSTER_NAME`
- Default Value: None

### ocp_version_upgrade
Required.  Specify the target version of the Openshift to be upgraded.

- Environment Variable: `OCP_VERSION_UPGRADE`
- Default Value: None

Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    cluster_name: my-ocp-cluster
    cluster_type: roks
    ocp_version_upgrade: 4.10_openshift
  roles:
    - ibm.mas_devops.ocp_upgrade
```

License
-------

EPL-2.0
