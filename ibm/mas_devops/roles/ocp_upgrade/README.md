ocp_upgrade
=============

This role supports the upgrade of the Openshift Cluster version in IBM Cloud provider.
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

### ocp_upgrade_version
Required.  Specify the target Openshift version to upgrade.

- Environment Variable: `OCP_UPGRADE_VERSION`
- Default Value: None

Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  roles:
    - ibm.mas_devops.ocp_upgrade
```

License
-------

EPL-2.0
