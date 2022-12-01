cis
===

This role provides support for Configuring IBM Cloud Internet Services.

Role Variables
--------------

### cis_action
Required. Action to be performed by CIS role. Valid values are `provision` or `deprovision`

- Environment Variable: `CIS_ACTION`
- Default Value: `provision`

### cis_plan
Required. The plan type of the service

- Environment Variable: `CIS_PLAN`
- Default Value: `standard`

### ibmcloud_apikey
Required.  Provide your IBM Cloud API Key.

- Environment Variable: `IBMCLOUD_APIKEY`
- Default Value: None

### ibmcloud_resourcegroup
Provide the name of the resource group which will own the CIS instance.

- Environment Variable: `IBMCLOUD_RESOURCEGROUP`
- Default Value: `Default`

### master_ibmcloud_api_key
Required. Provide IBM Cloud API Key for Account where Master CIS Instance is running.

- Environment Variable: `MASTER_IBMCLOUD_APIKEY`
- Default Value: None

### master_cis_resource_group
Required. Provide the name of the resource group which owns the Master CIS instance.

- Environment Variable: `MASTER_CIS_RESOURCE_GROUP`
- Default Value: `manager`

### master_cis_resource_name
Required. Master CIS Instance name

- Environment Variable: `MASTER_CIS_RESOURCE_NAME`
- Default Value: `masms-cis`

### masms_base_domain

- Environment Variable: `MASMS_BASE_DOMAIN`
- Default Value: `suite.maximo.com`

### mas_instance_id
Used as suffix string to define CIS Service name.

- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None
### cluster_name
Used as prefix string to define CIS Service name.

- Environment Variable: `CLUSTER_NAME`
- Default Value: None
### mas_config_dir
Local directory to save the generated CIS Instance details as ConfigMap.

- Environment Variable: `MAS_CONFIG_DIR`
- Default Value: None

Example Playbook
----------------
