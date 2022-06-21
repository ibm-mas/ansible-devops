ocp_deprovision
===============
Deprovision OCP cluster in Fyre, IBM Cloud, & ROSA.

Role Variables
--------------
### cluster_type
Required.  Specify the cluster type, supported values are `roks` and `quickburn`.

- **Required**
- Environment Variable: `CLUSTER_TYPE`
- Default Value: None

### cluster_name
Required.  Specify the name of the cluster

- **Required**
- Environment Variable: `CLUSTER_NAME`
- Default Value: None


Role Variables - ROKS
---------------------
### ibmcloud_apikey
The APIKey to be used by ibmcloud login comand.

- **Required** if `cluster_type = roks`
- Environment Variable: `IBMCLOUD_APIKEY`
- Default Value: None


Role Variables - ROSA
---------------------
### rosa_token
The Token used to authenticate with the ROSA service.

- **Required** if `cluster_type = rosa`
- Environment Variable: `ROSA_TOKEN`
- Default Value: None


Role Variables - Quickburn
--------------------------
### fyre_username
Username to authenticate with the Fyre API.

- **Required** if `cluster_type = quickburn`.
- Environment Variable: `FYRE_USERNAME`
- Default Value: None

### fyre_apikey
API key to authenticate with the Fyre API.

- **Required** if `cluster_type = quickburn`.
- Environment Variable: `FYRE_APIKEY`
- Default Value: None


Example Playbook
----------------

```yaml
- hosts: localhost
  vars:
    cluster_name: mycluster
    cluster_type: roks

    ibmcloud_apikey: xxxxx
  roles:
    - ibm.mas_devops.ocp_deprovision
```

License
-------

EPL-2.0
