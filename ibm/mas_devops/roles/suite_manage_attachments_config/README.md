suite_manage_attachments_config
===

This role extends support for Configuring IBM Cloud Object Storage or PVC File Storages for **Manage** application attachments.

The default for Manage attachments configuration is to use your cluster's default file storage system as persistent storage.

Although, you can optionally define IBM Cloud Object Storage.
You can run `cos` role to provision an IBM Cloud Object Storage or you can provide existing IBM Cloud Object Storage information to use it as storage for Manage application attachments

Role Variables
--------------
### mas_manage_attachments_provider
Required. Defines the storage provider type to be used to store Manage application's attachments.

- Environment Variable: `MAS_MANAGE_ATTACHMENTS_PROVIDER`
- Default Value: `filestorage`. Optionally set this variable to `cos` if you're planning to use IBM Cloud Object Storage instead of File Storage persistent volumes.

### cos_instance_name
Required. Only used if storage provider is `cos`.
IBM Cloud Object Storage instance name to be used to store Manage application attachments

- Environment Variable: `COS_INSTANCE_NAME`
- Default Value: None. If you do not have an existing IBM Cloud Object Storage instance, you can use `cos` role to provision one.

### ibmcloud_resourcegroup
Optional. Only used if storage provider is `cos`.
Provide the name of the resource group that hosts your IBM Cloud Object Storage instance. If you do not provide it, the role will try to find the IBM Cloud Object Storage instance in `Default` resource group.

- Environment Variable: `IBMCLOUD_RESOURCEGROUP`
- Default Value: `Default`

### ibmcloud_apikey
Required. Only used if storage provider is `cos`.
Provide your IBM Cloud API Key.

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
    db2_instance_name: db2w-manage
    cos_instance_name: cos-masinst1
    ibmcloud_apikey: xxxx
    mas_manage_attachments_provider: cos
  roles:
    - ibm.mas_devops.suite_manage_attachments_config
```

The following sample playbook can be used to provision COS in IBM Cloud and configure COS for an existing Manage application instance.

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_workspace_id: masdev
    db2_instance_name: db2w-manage
    cos_type: ibm
    cos_instance_name: cos-masinst1
    ibmcloud_apikey: xxxx
    mas_manage_attachments_provider: cos
  roles:
    - ibm.mas_devops.cos
    - ibm.mas_devops.suite_manage_attachments_config
```

The following sample playbook can be used to deploy Manage with default persistent storage for Manage attachments (PVC mount path `/DOCLINKS`), and configure Manage system properties with the corresponding attachments settings.

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_app_id: manage
    mas_app_channel: 8.4.x
    mas_instance_id: masinst1
    mas_workspace_id: masdev
    db2_instance_name: db2w-manage
    mas_app_settings_persistent_volumes_flag: true
    mas_app_settings_attachments_mount_path: /DOCLINKS
    mas_manage_attachments_provider: filestorage
  roles:
    - ibm.mas_devops.db2
    - ibm.mas_devops.suite_db2_setup_for_manage
    - ibm.mas_devops.suite_config
    - ibm.mas_devops.suite_app_install
    - ibm.mas_devops.suite_app_config
    - ibm.mas_devops.suite_manage_attachments_config
```

License
-------

EPL-2.0
