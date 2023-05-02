cis
===

This role provides support for Configuring IBM Cloud Internet Services.During CIS provisioning it performs four tasks during provisioning in given order:
```
1. Provision CIS Instance in customer account
2. Add customer domain to customer's CIS Instance
3. Configure Domain settings in customer CIS Instance
4. Add DNS Records of type `NS` for customer's Domain nameservers to Master CIS Account
```

During CIS Instance deprovisioing role will perform following tasks:
```
1. Delete DNS Record from Master Account
2. Delete Domain from Customer Account
3. Delete Customer CIS Instance
```

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
- Default Value: `{{mas_instance_id}}-cis`

### master_cis_base_domain
Required. Domain from Master CIS Instance
- Environment Variable: `MASTER_CIS_BASE_DOMAIN`

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
Create CIS Instance alongwith save Instance details in MAS_CONFIG_DIR path as ConfigMap

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    cis_action: provision
    mas_instance_id: masinst1
    mas_config_dir: ~/masconfig
    ibmcloud_apikey: "****"
    master_ibmcloud_api_key: "******"
    cluster_name: "test"
  roles:
    - ibm.mas_devops.cis
```