configure_manage_cfg
===

This role configures manage to use IBM Cloud Eventstreams

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

- Optional
- Environment Variable: `IBMCLOUD_RESOURCEGROUP`
- Default Value: `Default`

### eventstreams_name

- Required
- Environment Variable: `EVENTSTREAMS_NAME`
- Default Value: None

### eventstreams_location

- Optional
- Environment Variable: `EVENTSTREAMS_LOCATION`
- Default Value: `us-east`

### db2wh_dbname

- Optional
- Environment Variable: `DB2WH_DBNAME`
- Default Value: `BLUDB`

### cpd_meta_namespace

- Required
- Environment Variable: `CPD_NAMESPACE`
- Default Value: None

### db2_instance_name

- Required
- Environment Variable: `DB2_INSTANCE_NAME`
- Default Value: None

### mas_app_id

- Optional
- Environment Variable: `MAS_APP_ID`
- Default Value: `manage`

### mas_app_ws_fqn

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