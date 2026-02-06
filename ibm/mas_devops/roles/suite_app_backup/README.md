Backup MAS Applications
===============================================================================

Overview
-------------------------------------------------------------------------------
This role supports backing up MAS application resources and data. Currently supported applications:

- **`manage`**: Backs up Manage namespace resources (CRs, secrets, subscriptions) and persistent volume data

Future support planned for: `iot`, `monitor`, `health`, `optimizer`, `visualinspection`

The backup process creates a timestamped backup directory containing:
1. **Namespace Resources**: Kubernetes resources including ManageApp, ManageWorkspace, secrets, and subscriptions
2. **Persistent Volume Data**: Application data stored in PVCs (automatically detected from ManageWorkspace CR)

!!! important
    - An application backup can only be restored to an instance with the same MAS instance ID
    - This role backs up application resources and PV data only. Database backups must be performed separately using the appropriate database backup role
    - For Manage, see the [db2](db2.md) role for database backup


Role Variables - General
-------------------------------------------------------------------------------
### mas_app_id
Defines the MAS application ID for the backup action.

- **Required**
- Environment Variable: `MAS_APP_ID`
- Default: None
- Valid Values: `manage` (currently supported)

### mas_instance_id
Defines the MAS instance ID for the backup action.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

### mas_workspace_id
Defines the MAS workspace ID for the backup action.

- **Required**
- Environment Variable: `MAS_WORKSPACE_ID`
- Default: None

### mas_backup_dir
Defines the directory where backups will be stored. The role will create a timestamped subdirectory within this location.

- **Required**
- Environment Variable: `MAS_BACKUP_DIR`
- Default: None
- Example: `/backup/mas`

### mas_app_backup_version
Optional custom version identifier for the backup. If not specified, defaults to timestamp format `YYMMDD-HHMMSS`.

- Optional
- Environment Variable: `MAS_APP_BACKUP_VERSION`
- Default: Auto-generated timestamp
- Example: `240315-143022` or `v1.0-prod`


What Gets Backed Up
-------------------------------------------------------------------------------
### Manage Application
When backing up the Manage application, the following resources are included:

**Namespace Resources** (automatically backed up):
- `ManageApp` CR
- `ManageWorkspace` CR
- Encryption secrets (dynamically determined from ManageWorkspace CR)
- Certificates with `mas.ibm.com/instanceId` label
- Subscription and OperatorGroup
- IBM entitlement secret
- All referenced secrets (auto-discovered)

**Persistent Volume Data** (automatically backed up if configured in ManageWorkspace CR):
- All persistent volumes defined in `spec.settings.deployment.persistentVolumes`
- Data is backed up as compressed tar.gz archives
- Each PVC's mount path is archived separately
- Archives are stored in the `data` subdirectory

**NOT Included** (must be backed up separately):
- Manage database (Db2) - use the [db2](db2.md) role
- Suite-level resources - use the [suite_backup](suite_backup.md) role


How Persistent Volume Backup Works
-------------------------------------------------------------------------------
The role automatically detects and backs up persistent volumes configured in the ManageWorkspace CR:

1. **Detection**: Reads `spec.settings.deployment.persistentVolumes` from ManageWorkspace CR
2. **Pod Selection**: Finds the UI or ALL server bundle pod for the workspace
3. **Archive Creation**: Creates tar.gz archives of each mount path inside the pod
4. **Transfer**: Copies archives from pod to local backup directory
5. **Cleanup**: Removes temporary archives from the pod

Example ManageWorkspace CR configuration:
```yaml
spec:
  settings:
    deployment:
      persistentVolumes:
        - accessModes:
            - ReadWriteMany
          mountPath: /jmsstore
          pvcName: mas-inst1-ws1-jmsserver-pvc
          size: 25Gi
          storageClassName: efs-csi
        - accessModes:
            - ReadWriteMany
          mountPath: /usr/share/fonts/truetype/Free3of9Extended
          pvcName: masms-inst1-ws1-fonts-pvc
          size: 8Gi
          storageClassName: efs-csi
```

This configuration will result in two tar.gz archives:
- `mas-inst1-ws1-jmsserver-pvc.tar.gz`
- `masms-inst1-ws1-fonts-pvc.tar.gz`


Backup Directory Structure
-------------------------------------------------------------------------------
The role creates a backup directory with the following structure:

```
<mas_backup_dir>/
└── backup-<version>-manage-<workspace_id>/
    ├── namespace/
    │   ├── ManageApp-<instance_id>.yaml
    │   ├── ManageWorkspace-<instance_id>-<workspace_id>.yaml
    │   ├── Secret-<workspace_id>-manage-encryptionsecret.yaml
    │   ├── Secret-<workspace_id>-manage-encryptionsecret-operator.yaml
    │   ├── Subscription-ibm-mas-manage.yaml
    │   └── ... (other resources)
    └── data/
        ├── <pvc-name-1>.tar.gz
        ├── <pvc-name-2>.tar.gz
        └── ... (one archive per PVC)
```


Example Playbooks
-------------------------------------------------------------------------------

### Basic Backup
Backup Manage namespace resources and any configured persistent volumes:

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: inst1
    mas_workspace_id: ws1
    mas_app_id: manage
    mas_backup_dir: /backup/mas
  roles:
    - ibm.mas_devops.suite_app_backup
```

### Backup with Custom Version
Backup with a custom version identifier:

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: inst1
    mas_workspace_id: ws1
    mas_app_id: manage
    mas_backup_dir: /backup/mas
    mas_app_backup_version: "prod-backup-20240315"
  roles:
    - ibm.mas_devops.suite_app_backup
```


Notes
-------------------------------------------------------------------------------
- **Database Backup**: This role does NOT backup the Manage database. Use the [db2](db2.md) role to backup Db2 databases separately
- **Suite Resources**: This role backs up application-specific resources only. For suite-level resources (Suite CR, workspace CRs, etc.), use the [suite_backup](suite_backup.md) role
- **Storage Requirements**: Ensure sufficient storage space in `mas_backup_dir` for both namespace resources and PV data
- **Pod Access**: The role uses the UI or ALL server bundle pod to access PVC data. Ensure at least one of these pods is running and healthy
- **Backup Time**: PV backup duration depends on the amount of data in the persistent volumes
- **Automatic Detection**: Persistent volumes are automatically detected from the ManageWorkspace CR - no manual configuration needed
- **Compression**: All PV data is compressed using gzip to minimize storage requirements
