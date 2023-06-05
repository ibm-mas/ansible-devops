configure_manage_eventstreams
===

This role configures manage to use IBM Cloud Eventstreams.

**NOTE**
This role inserts dummy kafka password during configuration (not the actual one),so user has to follow below guide to configure kafka password manually via Manage Dashboard.

<img width="1479" alt="Screenshot 2023-02-23 at 7 21 27 PM" src="https://user-images.githubusercontent.com/100187956/220930223-bd3f2cab-3eb9-4ae4-86f9-e5f6480bc22d.png">



Role Variables
--------------

### mas_instance_id

- Required
- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### mas_workspace_id

- Required
- Environment Variable: `MAS_WORKSPACE_ID`
- Default Value: None

### ibmcloud_apikey

- Required
- Environment Variable: `IBMCLOUD_APIKEY`
- Default Value: None

### ibmcloud_region

- Optional
- Environment Variable: `IBMCLOUD_REGION`
- Default Value: `us-east`

### ibmcloud_resourcegroup
IBM Cloud Resource Group Name where the IBM Cloud Eventstreams is provisioned.
- Optional
- Environment Variable: `IBMCLOUD_RESOURCEGROUP`
- Default Value: `Default`

### eventstreams_name
IBM Cloud Eventstreams Service Name
- Required
- Environment Variable: `EVENTSTREAMS_NAME`
- Default Value: None

### eventstreams_location
IBM Cloud Eventstreams Service Location
- Optional
- Environment Variable: `EVENTSTREAMS_LOCATION`
- Default Value: `us-east`

### db2wh_dbname
DB2 Database name where configurations will be done for Manage to use IBM Cloud Eventstreams
- Optional
- Environment Variable: `DB2WH_DBNAME`
- Default Value: `BLUDB`

### cpd_meta_namespace

- Required
- Environment Variable: `CPD_NAMESPACE`
- Default Value: None

### db2_instance_name
Required to build up pod name running db2

- Required
- Environment Variable: `DB2_INSTANCE_NAME`
- Default Value: None

### mas_app_id

- Optional
- Environment Variable: `MAS_APP_ID`
- Default Value: `manage`

### mas_app_ws_fqn
Fully Qualified Name for MAS Application
- Optional
- Environment Variable: `MAS_APP_WS_FQN`
- Default Value: `manageworkspaces.apps.mas.ibm.com`

Example Playbook
----------------
Configures IBM Cloud Evenstreams service with Manage

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: 'test-instance'
    mas_workspace_id: 'main'
    ibmcloud_apikey: 'test-api-key'
    eventstreams_name: 'test-es'
    cpd_meta_namespace: 'db2u'
    db2_instance_name: 'test-db2'
  roles:
    - ibm.mas_devops.configure_manage_cfg
```
