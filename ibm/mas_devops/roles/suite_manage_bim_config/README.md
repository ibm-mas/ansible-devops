suite_manage_bim_config
===

This role extends support for configuring existing PVC mounted path for BIM (Building Information Models) in **Manage** application.

In order for this task to run successfully your Manage application must have been configured with a proper persistent volume and mounted path.

You can run `suite_app_config` with `mas_app_settings_persistent_volumes_flag: true` while installing `mas_app_id: manage` to have a default persistent storage configured as part of Manage deployment that can be used in this role to setup BIM.

For more details on how to configure persistent storage for Manage refer to [Configuring persistent volume claims](https://www.ibm.com/docs/en/maximo-manage/continuous-delivery?topic=storage-configuring-persistent-volume-claims).

Role Variables
--------------
### mas_app_settings_bim_mount_path
Required. Defines the persistent volume mount path to be used while configuring Manage BIM folders. If you used `suite_app_config` role to configure the persistent volumes while deploying Manage application, the default BIM persistent volume mount path will be the same.

- Environment Variable: `MAS_APP_SETTINGS_BIM_MOUNT_PATH`
- Default Value: `/bim`.

### mas_instance_id
Required. The instance ID of Maximo Application Suite. This will be used to lookup for Manage application resources.

- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### db2_instance_name
Required. The DB2 Warehouse instance name that stores your Manage application tables and data. This will be used to lookup for Manage application database and update it with the BIM system properties.

- Environment Variable: `DB2_INSTANCE_NAME` # e.g. db2u-manage
- Default Value: None

### db2_namespace
Optional. The namespace in your cluster that hosts the DB2 Warehouse instance name. This will be used to lookup for Manage application database and update it with the with the BIM system properties. If you do not provide it, the role will try to find the Db2 Warehouse in `db2u` namespace.

- Environment Variable: `DB2_NAMESPACE` # e.g. db2u
- Default Value: `db2u` 

### db2_dbname
Name of the database within the instance.

- Optional
- Environment Variable: `DB2_DBNAME`
- Default: `BLUDB`

Example Playbook
----------------
The following sample can be used to configure BIM for an existing Manage application instance.

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    db2_instance_name: db2w-manage
    mas_app_settings_bim_mount_path: /bim
  roles:
    - ibm.mas_devops.suite_manage_bim_config
```

The following sample playbook can be used to deploy Manage with default persistent storage for BIM (PVC mount path `/bim`), and configure Manage system properties with the corresponding BIM settings. 

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
    mas_app_settings_bim_mount_path: /bim
  roles:
    - ibm.mas_devops.db2
    - ibm.mas_devops.suite_db2_setup_for_manage
    - ibm.mas_devops.suite_config
    - ibm.mas_devops.suite_app_install
    - ibm.mas_devops.suite_app_config
    - ibm.mas_devops.suite_manage_bim_config
```
