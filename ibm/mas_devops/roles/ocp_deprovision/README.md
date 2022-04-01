ocp_deprovision
===============

Deprovision OCP cluster in Fyre and IBM Cloud

Role Variables
--------------

### cluster_type
Required.  Specify the cluster type, supported values are `roks` and `quickburn`.

- Environment Variable: `CLUSTER_TYPE`
- Default Value: None

### cluster_name
Required.  Specify the name of the cluster

- Environment Variable: `CLUSTER_NAME`
- Default Value: None


Role Variables - ROKS
---------------------
The following variables are only used when `cluster_type = roks`.

### ibmcloud_apikey
Required if `cluster_type = roks`.  The APIKey to be used by ibmcloud login comand.

- Environment Variable: `IBMCLOUD_APIKEY`
- Default Value: None


Role Variables - Quickburn
--------------------------
The following variables are only used when `cluster_type = quickburn`.

### username
Required if `cluster_type = quickburn`.  IBM Cloud zone where the cluster should be provisioned.

- Environment Variable: `FYRE_USERNAME`
- Default Value: None

### password
Required if `cluster_type = quickburn`.  IBM Cloud zone where the cluster should be provisioned.

- Environment Variable: `FYRE_APIKEY`
- Default Value: None


Example Playbook
----------------

```yaml
- hosts: localhost
  roles:
    - ibm.mas_devops.ocp_deprovision
```

License
-------

EPL-2.0
