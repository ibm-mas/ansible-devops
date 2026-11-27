# suite_app_restore

Restore MAS Applications

!!! important
    Supported only for MAS 9.1.x.

    Restore can only be made to an instance with the same MAS instance ID as the backup.

## Overview

This role supports restoring MAS application resources and data from backups created by the `suite_app_backup` role. Currently supported applications:

- **`manage`**: Restores Manage namespace resources (CRs, secrets, subscriptions) and persistent volume data
- **`facilities`**: Restores Facilities namespace resources (CRs, secrets, subscriptions) and persistent volume data

Future support planned for: `iot`, `monitor`, `health`, `optimizer`, `visualinspection`

The restore process follows these phases:

1. **Phase 1**: Restore Kubernetes resources like Project, Secrets, Configmaps, Subscription, Certificates and ManageApp CR (not ManageWorkspace CR)
2. **Phase 2**: Check if ManageWorkspace CR is already available
3. **Phase 3**: Restore persistent volume data
   - If ManageWorkspace exists: Scale it down, restore data, then continue
   - If ManageWorkspace doesn't exist: Create PVCs, create dummy pod, restore data, delete dummy pod
4. **Phase 4**: Restore ManageWorkspace CR
5. **Phase 5**: Wait for Manage deployment to be activated

!!! important
    - An application backup can only be restored to an instance with the same MAS instance ID
    - This role restores application resources and PV data only. Database restores must be performed separately using the appropriate database restore role
    - For Manage, see the [db2](db2.md) role for database restore
    - The restore process is designed to be idempotent and can handle both fresh installations and existing deployments

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`mas_app_id`](#mas_app_id) | Yes | None |
| [`mas_instance_id`](#mas_instance_id) | Yes | None |
| [`mas_backup_dir`](#mas_backup_dir) | Yes | None |
| [`mas_app_backup_version`](#mas_app_backup_version) | Yes | None |
| [`mas_workspace_id`](#mas_workspace_id) | No | Auto-discovered |
| [`mas_app_restore_include_pvc`](#mas_app_restore_include_pvc) | No | `true` |
| [`mas_app_restore_wait_retries`](#mas_app_restore_wait_retries) | No | `180` |
| [`mas_app_restore_wait_delay`](#mas_app_restore_wait_delay) | No | `360` |
| [`override_storageclass`](#override_storageclass) | No | `false` |
| [`mas_app_custom_storage_class_rwx`](#mas_app_custom_storage_class_rwx) | No | None |
| [`mas_app_custom_storage_class_rwo`](#mas_app_custom_storage_class_rwo) | No | None |
| [`helper_pod_image`](#helper_pod_image) | No | `registry.redhat.io/ubi9/ubi:latest` |

The two custom storage class variables only take effect when `override_storageclass` is enabled.

### Restore Target

#### mas_app_id

MAS application to restore — `manage` or `facilities` are the currently supported applications.

- **Required**
- Environment Variable: `MAS_APP_ID`
- Default: None

Future support is planned for `iot`, `monitor`, `health`, `optimizer`, and `visualinspection`.

#### mas_instance_id

MAS instance ID of the restore target — must match the instance ID used when the backup was created.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

An application backup can only be restored to an instance with the same MAS instance ID as the backup.

#### mas_backup_dir

Directory where backups are stored — for example `/backup/mas`. The role looks for the backup version subdirectory within this location.

- **Required**
- Environment Variable: `MAS_BACKUP_DIR`
- Default: None

#### mas_app_backup_version

Backup version to restore, matching the version identifier used during backup — for example `20240315-143022` or `v1.0-prod`.

- **Required**
- Environment Variable: `MAS_APP_BACKUP_VERSION`
- Default: None

#### mas_workspace_id

MAS workspace ID for the restore action.

- **Optional**
- Environment Variable: `MAS_WORKSPACE_ID`
- Default: Auto-discovered from the `mas.ibm.com/workspaceId` label on the workspace backup CR

Only set it explicitly if you want to override the value discovered from the backup.

### Restore Behavior

#### mas_app_restore_include_pvc

Controls whether persistent volume data is restored — `true` or `false`.

- **Optional**
- Environment Variable: `MAS_APP_RESTORE_INCLUDE_PVC`
- Default: `true`

When `false`, only namespace resources (CRs, secrets, subscriptions) are restored and the PVC data restore is skipped.

#### mas_app_restore_wait_retries

Number of retries when waiting for the workspace to become ready after the restore.

- **Optional**
- Environment Variable: `MAS_APP_RESTORE_WAIT_RETRIES`
- Default: `180`

Together with `mas_app_restore_wait_delay` this defines the total wait time — increase both for large or slow deployments.

#### mas_app_restore_wait_delay

Delay in seconds between status checks when waiting for the workspace to become ready.

- **Optional**
- Environment Variable: `MAS_APP_RESTORE_WAIT_DELAY`
- Default: `360` for Manage, `180` for Facilities

The default differs by application: with the default retries (180), Manage waits up to 18 hours (180 × 360 seconds) and Facilities up to 9 hours (180 × 180 seconds).

### Storage Class Override

#### override_storageclass

Enables storage class override during restore — `true` or `false`. When enabled, the restore process uses custom storage classes instead of the storage classes from the backup.

- **Optional**
- Environment Variable: `OVERRIDE_STORAGECLASS`
- Default: `false`

Useful when restoring to a different cluster with different storage classes. PVCs are mapped to storage classes based on their access mode: ReadWriteMany (RWX) uses `mas_app_custom_storage_class_rwx` and ReadWriteOnce (RWO) uses `mas_app_custom_storage_class_rwo`; if a custom class is not specified, the cluster's default storage class is used automatically.

#### mas_app_custom_storage_class_rwx

Custom storage class for PVCs with ReadWriteMany (RWX) access mode when `override_storageclass` is enabled — for example `ocs-storagecluster-cephfs`.

- **Optional**
- Environment Variable: `MAS_APP_CUSTOM_STORAGE_CLASS_RWX`
- Default: None (uses the cluster's default storage class)

#### mas_app_custom_storage_class_rwo

Custom storage class for PVCs with ReadWriteOnce (RWO) access mode when `override_storageclass` is enabled — for example `ocs-storagecluster-ceph-rbd`.

- **Optional**
- Environment Variable: `MAS_APP_CUSTOM_STORAGE_CLASS_RWO`
- Default: None (uses the cluster's default storage class)

### Helper Pod

#### helper_pod_image

Image used by the PVC-restore helper pod, which is deployed in the application's namespace to mount PVC volumes and extract the PVC backup to the mounted path.

- **Optional**
- Environment Variable: `HELPER_POD_IMAGE`
- Default: `registry.redhat.io/ubi9/ubi:latest`

The image must have `tar` installed for `oc cp` to work.

## What Gets Restored

### Manage Application

When restoring the Manage application, the following resources are restored:

**Namespace Resources** (Phase 1 & 4):

- `Project` (namespace)
- Encryption secrets
- Certificates with `mas.ibm.com/instanceId` label
- IBM entitlement secret
- All referenced secrets
- Subscription and OperatorGroup
- `ManageApp` CR (Phase 1)
- `ManageWorkspace` CR (Phase 4)

**Persistent Volume Data** (Phase 3):

- All persistent volumes defined in `spec.settings.deployment.persistentVolumes`
- Data is restored from compressed tar.gz archives
- Each PVC's mount path is restored separately
- Archives are read from the `data` subdirectory

**NOT Restored** (must be restored separately):

- Manage database (Db2) - use the [db2](db2.md) role
- Suite-level resources - use the [suite_restore](suite_restore.md) role

### Facilities Application

When restoring the Facilities application, the following resources are restored:

**Namespace Resources** (Phase 1 & 4):

- `Project` (namespace)
- Encryption secrets
- Certificates with `mas.ibm.com/instanceId` label
- IBM entitlement secret
- All referenced secrets
- Subscription and OperatorGroup
- `FacilitiesApp` CR (Phase 1)
- `FacilitiesWorkspace` CR (Phase 4)

**Persistent Volume Data** (Phase 3):

- All persistent volumes defined in `spec.settings.deployment.persistentVolumes`
- Data is restored from compressed tar.gz archives
- Each PVC is restored with special handling for extracted data:
  - Extracts tar.gz to temporary location
  - Moves config files to appropriate config directory
  - Moves userfiles to userfiles directory
  - Preserves original file ownership
- Archives are read from the `data` subdirectory

**NOT Restored** (must be restored separately):

- Facilities database (Db2) - use the [db2](db2.md) role
- Suite-level resources - use the [suite_restore](suite_restore.md) role

## How Persistent Volume Restore Works

The role intelligently handles PV restoration based on whether ManageWorkspace CR is already deployed:

### Scenario 1: ManageWorkspace CR Does Not Exist (Fresh Restore)

1. **Read Configuration**: Extracts PVC configuration from ManageWorkspace CR backup
2. **Create PVCs**: Creates all PVCs defined in the backup
3. **Create Dummy Pod**: Creates a temporary pod that mounts all PVCs
4. **Restore Data**: Copies tar.gz archives to the pod and extracts them to mount paths
5. **Cleanup**: Deletes the dummy pod
6. **Deploy CR**: Restores the ManageWorkspace CR
7. **Wait**: Waits for Manage deployment to be activated

### Scenario 2: ManageWorkspace CR Already Exists (Re-restore/Update)

1. **Scale Down**: Sets ManageWorkspace `spec.settings.deployment.mode` to `down`
2. **Wait**: Waits for workspace to scale down
3. **Find Pod**: Locates UI, ALL, or maxinst pod for data access
4. **Restore Data**: Copies tar.gz archives to the pod and extracts them to mount paths
5. **Update CR**: Restores the ManageWorkspace CR (which will scale back up)
6. **Wait**: Waits for Manage deployment to be activated

### Dummy Pod Specification

When a dummy pod is created for restoration, it uses:

- **Image**: `helper_pod_image` (default `registry.redhat.io/ubi9/ubi:latest`)
- **Command**: `sleep infinity` (keeps pod running)
- **Volumes**: All PVCs from ManageWorkspace CR configuration
- **Labels**: Tagged with instance ID and workspace ID for easy identification

## Manage Restore Process Phases

### Phase 1: Restore Resources Until ManageApp CR

- Restores all namespace resources except ManageWorkspace CR
- Includes: ManageApp, secrets, certificates, subscriptions, operator groups
- Waits for ManageApp CR to become ready
- Auto-discovers and restores referenced secrets

### Phase 2: Check ManageWorkspace Status

- Checks if ManageWorkspace CR already exists
- If exists: Sets `spec.settings.deployment.mode` to `down` and waits for scale down
- If not exists: Proceeds to create PVCs and dummy pod

### Phase 3: Restore Persistent Volume Data

- Reads PVC configuration from ManageWorkspace CR backup
- Creates PVCs if needed (when ManageWorkspace doesn't exist)
- Creates dummy pod or uses existing server bundle pod
- Restores data from tar.gz archives to each PVC
- Cleans up dummy pod if created

### Phase 4: Restore ManageWorkspace CR

- Restores the ManageWorkspace CR
- This triggers the Manage deployment to start/restart

### Phase 5: Wait for Deployment Activation

- Monitors ManageWorkspace CR status
- Waits for Ready condition to be True
- Configurable timeout and delay between checks

## Facilities Restore Process Phases

### Phase 1: Restore Resources Until FacilitiesApp CR

- Restores all namespace resources except FacilitiesWorkspace CR
- Includes: FacilitiesApp, secrets, certificates, subscriptions, operator groups
- Waits for FacilitiesApp CR to become ready
- Auto-discovers and restores referenced secrets

### Phase 2: Check FacilitiesWorkspace Status

- Checks if FacilitiesWorkspace CR already exists
- If exists: Proceeds to scale down deployments and statefulsets using pod templates
- If not exists: Deploys FacilitiesWorkspace CR and waits for CR to be ready and proceeds to scale down deployments and statefulsets replicas using pod templates

### Phase 3: Restore Persistent Volume Data

- PVC backup tar.gz are named after the pvc names
- PVCs are created by the workspace operator when CR was deployed
- Create dummy pods to mount to each of the PVCs
- Restore data from tar.gz archives to each PVC
- Clean up dummy pods

### Phase 4: Restore FacilitiesWorkspace CR

- Revert the podtemplates changes done in phase 2
- Wait for deployments and statefulsets to be ready

## Expected Backup Directory Structure

The role expects the backup directory to have the following structure:

```text
<mas_backup_dir>/
├── backup-<version>-app-manage/
│   ├── resources/
│   │   ├── projects
│   │   │   └── mas-<instance_id>-manage.yaml
│   |   ├── secrets
│   │   │   └── <secret1_name>.yaml
│   │   │   └── <secret2_name>.yaml
│   |   ├── configmaps
│   │   │   └── <configmap1_name>.yaml
│   │   │   └── <configmap2_name>.yaml
│   ├── subscriptions
│   │   │   └── <subscription_name>.yaml
│   │   └── ... (other resources)
│   └── data/
│       ├── <pvc-name-1>.tar.gz
│       └── <pvc-name-2>.tar.gz
└── backup-<version>-app-facilities/
    ├── resources/
    │   ├── projects
    │   │   └── mas-<instance_id>-facilities.yaml
    │   ├── secrets
    │   │   └── <secret1_name>.yaml
    │   │   └── <secret2_name>.yaml
    │   ├── configmaps
    │   │   └── <configmap1_name>.yaml
    │   │   └── <configmap2_name>.yaml
    │   ├── subscriptions
    │   │   └── <subscription_name>.yaml
    │   └── ... (other resources)
    └── data/
        ├── <pvc-name-1>.tar.gz
        └── <pvc-name-2>.tar.gz
```

## Example Playbooks

### Basic Restore

Restore Manage namespace resources and persistent volumes from a backup. The workspace ID is automatically derived from the backup CR:

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: inst1
    mas_app_id: manage
    mas_backup_dir: /backup/mas
    mas_app_backup_version: "20240315-143022"
  roles:
    - ibm.mas_devops.suite_app_restore
```

### Restore with Custom Timeout

Restore with a custom wait timeout for large deployments:

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: inst1
    mas_app_id: manage
    mas_backup_dir: /backup/mas
    mas_app_backup_version: "prod-backup-20240315"
    mas_app_restore_wait_retries: 180
    mas_app_restore_wait_delay: 360      # Check 6 minutes
  roles:
    - ibm.mas_devops.suite_app_restore
```

### Restore Facilities Application

Restore Facilities namespace resources and persistent volumes from a backup:

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: inst1
    mas_app_id: facilities
    mas_backup_dir: /backup/mas
    mas_app_backup_version: "20240315-143022"
  roles:
    - ibm.mas_devops.suite_app_restore
```

### Complete Restore Workflow - Manage

Complete workflow including database restore:

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: inst1
    mas_backup_dir: /backup/mas
    backup_version: "20240315-143022"

  tasks:
    # 1. Restore Db2 database first
    - name: "Restore Manage database"
      include_role:
        name: ibm.mas_devops.db2
      vars:
        db2_action: restore
        db2_backup_version: "{{ backup_version }}"

    # 2. Restore Manage application
    - name: "Restore Manage application"
      include_role:
        name: ibm.mas_devops.suite_app_restore
      vars:
        mas_app_id: manage
        mas_app_backup_version: "{{ backup_version }}"
```

### Complete Restore Workflow - Facilities

Complete workflow including database restore:

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: inst1
    mas_backup_dir: /backup/mas
    backup_version: "20240315-143022"

  tasks:
    # 1. Restore Db2 database first
    - name: "Restore Facilities database"
      include_role:
        name: ibm.mas_devops.db2
      vars:
        db2_action: restore
        db2_backup_version: "{{ backup_version }}"

    # 2. Restore Facilities application
    - name: "Restore Facilities application"
      include_role:
        name: ibm.mas_devops.suite_app_restore
      vars:
        mas_app_id: facilities
        mas_app_backup_version: "{{ backup_version }}"
```

### Restore with Storage Class Override

Restore to a different cluster with different storage classes:

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: inst1
    mas_app_id: manage
    mas_backup_dir: /backup/mas
    mas_app_backup_version: "20240315-143022"
    # Enable storage class override
    override_storageclass: true
    # Specify custom storage classes
    mas_app_custom_storage_class_rwo: "ocs-storagecluster-cephfs"
    mas_app_custom_storage_class_rwx: "ocs-storagecluster-ceph-rbd"
  roles:
    - ibm.mas_devops.suite_app_restore
```

### Restore with Storage Class Override Using Default Classes

Restore with override enabled but using cluster's default storage classes:

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: inst1
    mas_app_id: manage
    mas_backup_dir: /backup/mas
    mas_app_backup_version: "20240315-143022"
    # Enable storage class override without specifying custom classes
    # Will automatically use the cluster's default storage class
    override_storageclass: true
  roles:
    - ibm.mas_devops.suite_app_restore
```

### Restore Without PVC Data

Restore only namespace resources without restoring persistent volume data:

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: inst1
    mas_app_id: manage
    mas_backup_dir: /backup/mas
    mas_app_backup_version: "20240315-143022"
    # Skip PVC restore
    mas_app_restore_include_pvc: false
  roles:
    - ibm.mas_devops.suite_app_restore
```

### Restore Facilities Without PVC Data

Restore Facilities namespace resources without restoring persistent volume data:

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: inst1
    mas_app_id: facilities
    mas_backup_dir: /backup/mas
    mas_app_backup_version: "20240315-143022"
    # Skip PVC restore
    mas_app_restore_include_pvc: false
  roles:
    - ibm.mas_devops.suite_app_restore
```

## Troubleshooting

### Restore Fails at Phase 1

**Issue**: Resources fail to restore in Phase 1

**Solution**:

- Check that the backup directory exists and contains the expected files
- Verify namespace exists: `oc get namespace mas-<instance_id>-manage`
- Check for conflicting resources: `oc get manageapp,subscription -n mas-<instance_id>-manage`

### Dummy Pod Fails to Start

**Issue**: Dummy pod remains in Pending state

**Solution**:

- Check PVC status: `oc get pvc -n mas-<instance_id>-manage`
- Verify storage class exists and can provision volumes
- Check pod events: `oc describe pod <pod-name> -n mas-<instance_id>-manage`

### PV Data Restore Fails

**Issue**: Data extraction fails in the pod

**Solution**:

- Verify tar.gz archives are not corrupted
- Check pod has sufficient disk space
- Verify mount paths are accessible in the pod

### ManageWorkspace Never Becomes Ready

**Issue**: Phase 5 times out waiting for ManageWorkspace

**Solution**:

- Check ManageWorkspace status: `oc describe manageworkspace -n mas-<instance_id>-manage`
- Verify database is accessible and restored
- Check pod logs: `oc logs -l mas.ibm.com/appType=serverBundle -n mas-<instance_id>-manage`
- Increase `mas_app_restore_wait_retries` and `mas_app_restore_wait_delay` values if deployment is slow

## Notes

- **Workspace ID Auto-Discovery**: `mas_workspace_id` is automatically derived from the `mas.ibm.com/workspaceId` label on the workspace backup CR. You only need to set `MAS_WORKSPACE_ID` explicitly if you want to override the value from the backup
- **Database Restore**: This role does NOT restore application databases. Use the [db2](db2.md) role to restore Db2 databases separately, and do this BEFORE running the application restore
- **Suite Resources**: This role restores application-specific resources only. For suite-level resources (Suite CR, workspace CRs, etc.), use the [suite_restore](suite_restore.md) role
- **Instance ID Match**: The restore must be performed on a cluster with the same MAS instance ID as the backup
- **Idempotent**: The restore process is idempotent and can be run multiple times
- **Dummy Pod**: When workspace CR doesn't exist, a temporary pod is created for data restoration and automatically cleaned up
- **Scale Down**: When workspace CR exists, it's automatically scaled down before data restoration
- **Automatic Detection**: Persistent volumes are automatically detected from the workspace CR backup
- **Compression**: All PV data is stored as compressed tar.gz archives
- **Wait Time**: Default wait timeout varies by application (Manage: 18 hours, Facilities: 9 hours), but can be adjusted based on deployment size
- **Prerequisites**: Ensure the MAS operator and application operator are installed before running restore
- **Storage Class Override**: When restoring to a different cluster with different storage classes, enable `override_storageclass` to automatically map PVCs to appropriate storage classes based on access modes (RWX/RWO)
- **Default Storage Classes**: If `override_storageclass` is enabled but custom storage classes are not specified, the cluster's default storage class will be used automatically
- **Access Mode Mapping**: The role intelligently assigns storage classes based on PVC access modes - RWX (ReadWriteMany) uses `mas_app_custom_storage_class_rwx` and RWO (ReadWriteOnce) uses `mas_app_custom_storage_class_rwo`

## License

EPL-2.0
