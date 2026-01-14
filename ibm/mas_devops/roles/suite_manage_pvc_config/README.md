# suite_manage_pvc_config

This role extends support for configuring persistent volume claims for **Manage** application.

!!! note
    This role should be executed **after** Manage application is deployed and activated because it needs Manage up and running prior to configuring the additional persistent volume claims.

There are two options to setup new Manage PVCs:

- Exporting Manage PVCs variables
- Loading Manage PVCs variables from a file

## Role Variables

### mas_instance_id
MAS instance identifier for locating Manage resources.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

**Purpose**: Identifies which MAS instance contains the Manage application to configure. Used to locate the correct ManageWorkspace resource.

**When to use**:
- Always required when configuring Manage PVCs
- Must match the instance ID from MAS installation
- Used to construct resource names and locate Manage workspace

**Valid values**: Lowercase alphanumeric string, 3-12 characters (e.g., `prod`, `dev`, `inst1`)

**Impact**: Determines which MAS instance's Manage workspace will be configured with additional PVCs. Incorrect instance ID will cause configuration to fail.

**Related variables**:
- `mas_workspace_id`: Workspace within this instance
- `manage_workspace_cr_name`: Defaults to `{instance_id}-{workspace_id}`

**Note**: Manage application must already be deployed and activated in this instance before configuring PVCs.

### mas_workspace_id
Workspace identifier for locating Manage resources.

- **Required**
- Environment Variable: `MAS_WORKSPACE_ID`
- Default: None

**Purpose**: Identifies which workspace within the MAS instance contains the Manage application to configure. Used to locate the correct ManageWorkspace resource.

**When to use**:
- Always required when configuring Manage PVCs
- Must match the workspace ID from Manage installation
- Used to construct resource names and locate Manage workspace

**Valid values**: Lowercase alphanumeric string (e.g., `masdev`, `prod`, `test`)

**Impact**: Determines which Manage workspace will be configured with additional PVCs. Incorrect workspace ID will cause configuration to fail.

**Related variables**:
- `mas_instance_id`: Instance containing this workspace
- `manage_workspace_cr_name`: Defaults to `{instance_id}-{workspace_id}`

**Note**: Manage application must already be deployed and activated in this workspace before configuring PVCs.

### manage_workspace_cr_name
ManageWorkspace custom resource name to configure.

- **Optional**
- Environment Variable: `MANAGE_WORKSPACE_CR_NAME`
- Default: `{mas_instance_id}-{mas_workspace_id}`

**Purpose**: Specifies the exact name of the ManageWorkspace custom resource to modify with new PVC definitions.

**When to use**:
- Leave as default for standard deployments
- Set explicitly if ManageWorkspace CR has a custom name
- Useful when workspace CR name doesn't follow default pattern

**Valid values**: Valid Kubernetes resource name matching an existing ManageWorkspace CR

**Impact**: Determines which ManageWorkspace CR will be updated with PVC configuration. Incorrect name will cause configuration to fail.

**Related variables**:
- `mas_instance_id`: Used in default name
- `mas_workspace_id`: Used in default name

**Note**: The default value follows the standard naming pattern `{instance_id}-{workspace_id}`. Only override if your ManageWorkspace CR uses a different name.

### mas_app_settings_custom_persistent_volume_pvc_name
Name for the new Persistent Volume Claim.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_CUSTOM_PVC_NAME`
- Default: `{mas_instance_id}-{mas_workspace_id}-cust-files-pvc`

**Purpose**: Specifies the name of the PVC to create for additional Manage storage. This PVC will be mounted in Manage pods.

**When to use**:
- Use default for standard custom files storage
- Set custom name for specific storage purposes
- Must be unique within the namespace

**Valid values**: Valid Kubernetes PVC name (lowercase alphanumeric with hyphens)

**Impact**: Creates a PVC with this name that will be mounted in Manage pods at the specified mount path.

**Related variables**:
- `mas_app_settings_custom_persistent_volume_mount_path`: Where this PVC is mounted
- `mas_app_settings_custom_persistent_volume_pvc_size`: Size of this PVC
- `mas_app_settings_custom_persistent_volume_sc_name`: Storage class for this PVC

**Note**: The default name follows the pattern `{instance}-{workspace}-cust-files-pvc`. Choose descriptive names for multiple PVCs.

### mas_app_settings_custom_persistent_volume_pv_name
Name for the Persistent Volume (storage provider dependent).

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_CUSTOM_PV_NAME`
- Default: None (random name generated)

**Purpose**: Specifies the name of the underlying Persistent Volume. Some storage providers allow or require specific PV names.

**When to use**:
- Leave unset (recommended) for automatic random name generation
- Set only if your storage provider requires specific PV naming
- Verify your storage class supports custom PV names before setting

**Valid values**: Valid PV name if supported by storage provider, or leave unset

**Impact**: If set and storage provider doesn't support custom PV names, provisioning may fail. When unset, a random name is generated automatically.

**Related variables**:
- `mas_app_settings_custom_persistent_volume_sc_name`: Storage class that provisions this PV
- `mas_app_settings_custom_persistent_volume_pvc_name`: PVC that binds to this PV

**Note**: Most storage classes use dynamic provisioning with auto-generated PV names. Only set this if you have specific requirements or your storage provider requires it.

### mas_app_settings_custom_persistent_volume_pvc_size
Size of the Persistent Volume Claim.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_CUSTOM_PVC_SIZE`
- Default: `100Gi`

**Purpose**: Specifies the storage capacity for the PVC. This determines how much data can be stored in the mounted volume.

**When to use**:
- Use default (`100Gi`) for standard custom files storage
- Increase for larger storage requirements
- Consider your data volume and growth projections
- Ensure sufficient space for your use case

**Valid values**: Kubernetes storage size format (e.g., `50Gi`, `100Gi`, `500Gi`, `1Ti`)

**Impact**: Determines the storage capacity available to Manage. Insufficient size will cause storage full errors. Some storage classes may not support resizing after creation.

**Related variables**:
- `mas_app_settings_custom_persistent_volume_pvc_name`: PVC with this size
- `mas_app_settings_custom_persistent_volume_sc_name`: Storage class providing this capacity

**Note**: The default `100Gi` is suitable for moderate custom files storage. Plan capacity based on expected data volume. Check if your storage class supports volume expansion for future growth.

### mas_app_settings_custom_persistent_volume_mount_path
Mount path for the PVC in Manage containers.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_CUSTOM_MOUNT_PATH`
- Default: `/MeaGlobalDirs`

**Purpose**: Specifies where the PVC will be mounted inside Manage server containers. This is the directory path where the persistent storage will be accessible.

**When to use**:
- Use default (`/MeaGlobalDirs`) for standard Manage global directories
- Set custom path for specific storage purposes
- Ensure path doesn't conflict with existing Manage directories
- Path must be absolute (start with `/`)

**Valid values**: Absolute Linux filesystem path (e.g., `/MeaGlobalDirs`, `/MyCustomDir`, `/opt/data`)

**Impact**: Determines where Manage can access the persistent storage. Applications and configurations must reference this path to use the storage.

**Related variables**:
- `mas_app_settings_custom_persistent_volume_pvc_name`: PVC mounted at this path
- `mas_app_settings_custom_persistent_volume_pvc_size`: Size available at this path

**Note**: The default `/MeaGlobalDirs` is the standard location for Manage global directories. Ensure the path doesn't conflict with existing Manage directories or mount points.

### mas_app_settings_custom_persistent_volume_sc_name
Storage class for the PVC (supports RWX or RWO).

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_CUSTOM_PV_STORAGE_CLASS`
- Default: Auto-detected from available storage classes

**Purpose**: Specifies which storage class to use for provisioning the PVC. The storage class determines the underlying storage technology and performance characteristics.

**When to use**:
- Leave unset for automatic detection (recommended)
- Set explicitly when you need a specific storage class
- Both ReadWriteMany (RWX) and ReadWriteOnce (RWO) access modes are supported

**Valid values**: Any storage class name available in your cluster

**Impact**: Determines the storage technology, performance, and access mode for the PVC. Incorrect storage class will cause provisioning to fail.

**Related variables**:
- `mas_app_settings_custom_persistent_volume_pvc_size`: Size to provision from this storage class
- `mas_app_settings_custom_persistent_volume_pv_name`: PV name (if storage class supports it)

**Note**: Both RWX (ReadWriteMany) and RWO (ReadWriteOnce) storage classes are supported. RWX allows multiple pods to access the volume simultaneously, while RWO restricts to a single pod. Choose based on your access requirements.

### mas_app_settings_custom_persistent_volume_file_path
Path to custom PVC definition file (alternative to individual variables).

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_CUSTOM_PV_FILE_PATH`
- Default: None

**Purpose**: Provides an alternative method to configure PVCs using a complete YAML definition file instead of individual variables. Useful for complex or multiple PVC configurations.

**When to use**:
- Use when you have complex PVC requirements
- Use when configuring multiple PVCs at once
- Use when you need full control over PVC specification
- Alternative to setting individual PVC variables

**Valid values**: Absolute path to YAML file containing PVC definitions

**Impact**: When set, the role uses this file instead of individual PVC variables. The file must contain valid PVC definitions matching the expected format.

**Related variables**: Overrides all individual `mas_app_settings_custom_persistent_volume_*` variables when set

**Note**: See `files/manage-persistent-volumes-sample.yml` for file format example. This approach is more flexible but requires understanding of PVC YAML structure. For simple single-PVC scenarios, use individual variables instead.

## Example Playbook

### Using Variables
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

### Using File Definition
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

## Run Role Playbook
After installing the Ansible Collection you can easily run the role standalone using the `run_role` playbook provided.

```bash
export MAS_APP_SETTINGS_CUSTOM_PV_STORAGE_CLASS=ibmc-file-silver-gid
export MAS_APP_SETTINGS_CUSTOM_PVC_NAME=my-manage-pvc
export MAS_APP_SETTINGS_CUSTOM_PVC_SIZE=20Gi
export MAS_APP_SETTINGS_CUSTOM_MOUNT_PATH=/MyOwnDir
export MAS_APP_SETTINGS_CUSTOM_PV_FILE_PATH=/my-path/manage-pv.yml

ROLE_NAME='suite_manage_pvc_config' ansible-playbook playbooks/run_role.yml
```

## License

EPL-2.0
