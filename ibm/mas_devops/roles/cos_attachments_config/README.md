cos
===

This role extends support for Configuring IBM Cloud Object Storage for **Manage** application attachments.

You can run `cos` role to provision an IBM Cloud Object Storage or you can provide existing IBM Cloud Object Storage information to use it as storage for Manage application attachments

Role Variables
--------------

### cos_instance_name
Required. IBM Cloud Object Storage instance name to be used to store Manage application attachments

- Environment Variable: `COS_INSTANCE_NAME`
- Default Value: None. If you do not have an existing IBM Cloud Object Storage instance, you can use `cos` role to provision one.

### ibmcloud_resourcegroup
Optional. Provide the name of the resource group that hosts your IBM Cloud Object Storage instance. If you do not provide it, the role will try to find the IBM Cloud Object Storage instance in `Default` resource group.

- Environment Variable: `IBMCLOUD_RESOURCEGROUP`
- Default Value: `Default`
### ibmcloud_apikey
Required. Provide your IBM Cloud API Key.

- Environment Variable: `IBMCLOUD_APIKEY`
- Default Value: None

### mas_instance_id
Required. The instance ID of Maximo Application Suite. This will be used to lookup for Manage application resources.

- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### mas_workspace_id
Required. The workspace ID of Maximo Application Suite. This will be used to lookup for Manage application resources.

- Environment Variable: `MAS_WORKSPACE_ID`
- Default Value: None

### db2_instance_name
Required. The DB2 Warehouse instance name that stores your Manage application tables and data. This will be used to lookup for Manage application database and update it with the IBM Object Storage configuration.

- Environment Variable: `DB2_INSTANCE_NAME` # e.g. db2u-iot or db2wh-1658148844550964
- Default Value: None

### db2_namespace
Optional. The namespace in your cluster that hosts the DB2 Warehouse instance name. This will be used to lookup for Manage application database and update it with the IBM Object Storage configuration. If you do not provide it, the role will try to find the Db2 Warehouse in `db2u` namespace.

- Environment Variable: `DB2_NAMESPACE` # e.g. db2u
- Default Value: `db2u` 

Example Playbook
----------------
The following sample can be used to configure COS for an existing Manage application instance.

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_workspace_id: masdev
    db2_instance_name: db2u-manage
    cos_instance_name: cos-masinst1
    ibmcloud_apikey: xxxx
  roles:
    - ibm.mas_devops.cos_attachments_config
```

The following sample playbook can be used to provision COS in IBM Cloud and configure COS for an existing Manage application instance.

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_workspace_id: masdev
    db2_instance_name: db2u-manage
    cos_type: ibm
    cos_instance_name: cos-masinst1
    ibmcloud_apikey: xxxx
  roles:
    - ibm.mas_devops.cos
    - ibm.mas_devops.cos_attachments_config
```

License
-------

EPL-2.0
