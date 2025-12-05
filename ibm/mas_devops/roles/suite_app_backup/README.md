Backup and Restore MAS Applications
===============================================================================

Overview
-------------------------------------------------------------------------------
This role supports backing up the data for below MAS applications:

- `manage`: Manage namespace resources, persistent volume data (e.g. attachments)
<!-- - `iot`: IoT namespace resources
- `monitor`: Monitor namespace resources
- `health`: Health namespace resources, Watson Studio project asset
- `optimizer`: Optimizer namespace resources
- `visualinspection`: Visual Inspection namespace resources, persistent volume data (e.g. image datasets, models) -->


Supports creating on-demand full backups.

!!! important
    An application backup can only be restored to an instance with the same MAS instance ID.


Role Variables - General
-------------------------------------------------------------------------------
### mas_app_id
Defines the MAS application ID (`manage`, `iot`, `monitor`, `health`, `optimizer`, or `visualinspection`) for the backup or restore action.

- **Required**
- Environment Variable: `MAS_APP_ID`
- Default: None

### mas_instance_id
Defines the MAS instance ID for the backup or restore action.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

### mas_workspace_id
Defines the MAS workspace ID for the backup or restore action.

- **Required**
- Environment Variable: `MAS_WORKSPACE_ID`
- Default: None


Role Variables - Manage
-------------------------------------------------------------------------------
### masbr_manage_pvc_paths
Set the Manage PVC paths to use in backup and restore. The PVC path is in the format of `<pvcName>:<mountPath>/<subPath>`. Multiple PVC paths are separated by commas (e.g. `manage-doclinks1-pvc:/mnt/doclinks1/attachments,manage-doclinks2-pvc:/mnt/doclinks2`).

The `<pvcName>` and `<mountPath>` are defined in the `ManageWorkspace` CRD instance `spec.settings.deployment.persistentVolumes`:
```
persistentVolumes:
  - accessModes:
      - ReadWriteMany
    mountPath: /mnt/doclinks1
    pvcName: manage-doclinks1-pvc
    size: '20'
    storageClassName: ocs-storagecluster-cephfs
    volumeName: ''
  - accessModes:
      - ReadWriteMany
    mountPath: /mnt/doclinks2
    pvcName: manage-doclinks2-pvc
    size: '20'
    storageClassName: ocs-storagecluster-cephfs
    volumeName: ''
```

If not set a value for this variable, this role will not backup and restore persistent valumne data for Manage.


- Optional
- Environment Variable: `MASBR_MANAGE_PVC_PATHS`
- Default: None


Example Playbook
-------------------------------------------------------------------------------

### Backup
Backup Manage attachments, note that this does not include backup of any data in Db2, see the `backup` action in the [db2](db2.md) role.

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    masbr_action: backup
    mas_instance_id: main
    mas_workspace_id: ws1
    mas_app_id: manage
    masbr_backup_data: pv
    masbr_manage_pvc_paths: "manage-doclinks1-pvc:/mnt/doclinks1"
    masbr_storage_local_folder: /tmp/masbr
  roles:
    - ibm.mas_devops.suite_app_backup_restore
```

