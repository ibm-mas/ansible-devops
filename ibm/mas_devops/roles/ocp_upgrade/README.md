ocp_upgrade
=============

This role supports the upgrade of the Openshift Cluster version in IBM Cloud provider, from version 4.6 to 4.7 then 4.8 (latest patch) which is the supported version of Openshift to run MAS in 8.7 release.

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
