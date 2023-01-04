suite_manage_pvc_config
===
This role extends support for configuring persistent volume claims for **Manage** application.

!!! note
    This role should be executed **after** Manage application is deployed and activated because it needs Manage up and running prior to configuring the additional persistent volume claims.

The are two options to setup new Manage PVCS:

- Exporting Manage PVCs variables
- Loading Manage PVCs variables from a file

Role Variables
--------------

### mas_instance_id
Required. The instance ID of Maximo Application Suite. This will be used to lookup for Manage application resources.

- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### mas_workspace_id
Required. The workspace ID of Maximo Application Suite. This will be used to lookup for Manage application resources.

- Environment Variable: `MAS_WORKSPACE_ID`
- Default Value: None

### manage_workspace_cr_name
Optional. Name of the `ManageWorkspace` Custom Resource that will be targeted to configure the new PVC definitions.

- Environment Variable: `MANAGE_WORKSPACE_CR_NAME`
- Default Value: `$MAS_INSTANCE_ID-$MAS_WORKSPACE_ID`

### mas_app_settings_custom_persistent_volume_pvc_name
Optional. Name of the Persistent Volume Claim to be configured.

- Environment Variable: `MAS_APP_SETTINGS_CUSTOM_PVC_NAME`
- Default Value: `$MAS_INSTANCE_ID-$MAS_WORKSPACE_ID-cust-files-pvc`

### mas_app_settings_custom_persistent_volume_pv_name
Optional. Name of the volume that will be created to store data from the PVC.
Make sure your storage class provider supports the name you define.
If not sure about what to set, you can leave it unset then a random name will the defined.

- Environment Variable: `MAS_APP_SETTINGS_CUSTOM_PV_NAME`
- Default Value: None.

### mas_app_settings_custom_persistent_volume_pvc_size
Optional. Size of the Persistent Volume Claim.

- Environment Variable: `MAS_APP_SETTINGS_CUSTOM_PVC_SIZE`
- Default Value: `100Gi`

### mas_app_settings_custom_persistent_volume_mount_path
Optional. Mouth path of the Persistent Volume in the Manage server container.

- Environment Variable: `MAS_APP_SETTINGS_CUSTOM_MOUNT_PATH`
- Default Value: `/MeaGlobalDirs`

### mas_app_settings_custom_persistent_volume_sc_name
Optional. Persistent Volume Claim Storage Class. If not set, it will be automatically defined accordingly to your cluster's available storage classes.

- Environment Variable: `MAS_APP_SETTINGS_CUSTOM_PV_STORAGE_CLASS`
- Default Value: None.

### mas_app_settings_custom_persistent_volume_file_path
Optional. Alternatively, this defines a local path pointing the persistent volume definition from a custom file. Sample file definition can be found in `files/manage-persistent-volumes-sample.yml`.

- Environment Variable: `MAS_APP_SETTINGS_CUSTOM_PV_FILE_PATH`
- Default Value: None.


Example Playbook
----------------
The following sample can be used to configure new PVCs for an existing Manage application instance.

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_workspace_id: masdev
    mas_app_settings_custom_persistent_volume_sc_name: "ibmc-file-gold-gid"
    mas_app_settings_custom_persistent_volume_pvc_name: "my-manage-pvc"
    mas_app_settings_custom_persistent_volume_pvc_size: "20Gi"
    mas_app_settings_custom_persistent_volume_mount_path: "/MyOwnFolder"
  roles:
    - ibm.mas_devops.suite_manage_pvc_config
```

The following sample can be used to configure new PVCs for an existing Manage application instance from a custom file definition.

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_workspace_id: masdev
    mas_app_settings_custom_persistent_volume_file_path: "/my-path/manage-pv.yml"
  roles:
    - ibm.mas_devops.suite_manage_pvc_config
```

Run Role Playbook
----------------
After installing the Ansible Collection you can easily run the role standalone using the `run_role` playbook provided.

```bash
export MAS_APP_SETTINGS_CUSTOM_PV_STORAGE_CLASS=ibmc-file-silver-gid
export MAS_APP_SETTINGS_CUSTOM_PVC_NAME=my-manage-pvc
export MAS_APP_SETTINGS_CUSTOM_PVC_SIZE=20Gi
export MAS_APP_SETTINGS_CUSTOM_MOUNT_PATH=/MyOwnDir
export MAS_APP_SETTINGS_CUSTOM_PV_FILE_PATH=/my-path/manage-pv.yml

ROLE_NAME='suite_manage_pvc_config' ansible-playbook playbooks/run_role.yml


License
-------

EPL-2.0
