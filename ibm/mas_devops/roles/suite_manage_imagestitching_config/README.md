# suite_manage_imagestitching_config

This role configures image stitching functionality in Maximo Manage for the Civil Infrastructure component. Image stitching enables combining multiple images into panoramic views for infrastructure inspection and analysis. The role creates persistent storage, updates the ManageWorkspace CR, and sets required system properties.

!!! important "Prerequisites"
    - Manage application must be deployed and activated
    - Civil Infrastructure component must be installed
    - Storage class must support ReadWriteMany (RWX) access mode

## What This Role Does

- Creates PVC for image stitching data storage
- Patches ManageWorkspace CR with PVC configuration
- Configures persistent volume specifications
- Sets system properties:
  - `mci.imagestitching.apiurl`: API endpoint for image stitching service
  - `imagestitching.dataInputPath`: Data input path for image processing

## Role Variables

### mas_instance_id
MAS instance identifier.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

**Purpose**: Identifies which MAS instance contains the Manage application to configure for image stitching.

**When to use**:
- Always required for image stitching configuration
- Must match the instance ID from MAS installation
- Used in PVC name construction

**Valid values**: Lowercase alphanumeric string, 3-12 characters (e.g., `civil`, `prod`, `masinst1`)

**Impact**: Used to construct PVC name (`{instance}-{workspace}-{pvcname}`) and locate Manage resources.

**Related variables**:
- `mas_workspace_id`: Workspace within this instance
- `stitching_pvcname`: Combined to create full PVC name

**Note**: This must match the instance ID used during Manage installation with Civil component.

### mas_workspace_id
Workspace identifier for Manage application.

- **Required**
- Environment Variable: `MAS_WORKSPACE_ID`
- Default: None

**Purpose**: Identifies which workspace within the MAS instance contains the Manage application with Civil component.

**When to use**:
- Always required for image stitching configuration
- Must match the workspace ID where Manage is deployed
- Used in PVC name construction

**Valid values**: Lowercase alphanumeric string, typically 3-12 characters (e.g., `prod`, `dev`, `masdev`)

**Impact**: Used to construct PVC name (`{instance}-{workspace}-{pvcname}`) and locate Manage resources.

**Related variables**:
- `mas_instance_id`: Parent instance
- `stitching_pvcname`: Combined to create full PVC name

**Note**: This must match the workspace ID used during Manage installation.

### mas_domain
MAS cluster domain name.

- **Optional**
- Environment Variable: `MAS_DOMAIN`
- Default: Discovered from Suite CR

**Purpose**: Specifies the domain name for the Manage cluster, used to construct the image stitching API URL.

**When to use**:
- Use default (auto-discovery) for standard deployments
- Override if auto-discovery fails or for custom domains
- Required for constructing service endpoints

**Valid values**: Valid DNS domain name (e.g., `civil.ibmmasdev.com`, `apps.cluster.example.com`)

**Impact**: Used to construct the `mci.imagestitching.apiurl` system property for the image stitching service endpoint.

**Related variables**:
- `mas_instance_id`: Instance in this domain
- `mas_workspace_id`: Workspace in this domain

**Note**: The role attempts to discover the domain from the Suite CR. Only override if auto-discovery doesn't work for your environment.

### stitching_pvcname
PVC name postfix for image stitching storage.

- **Optional**
- Environment Variable: `IMAGESTITCHING_PVCNAME`
- Default: `manage-imagestitching`

**Purpose**: Defines the postfix for the PVC name. The full PVC name is constructed as `{mas_instance_id}-{mas_workspace_id}-{stitching_pvcname}`.

**When to use**:
- Use default for standard deployments
- Override for custom naming conventions
- Must be unique within the namespace

**Valid values**: Valid Kubernetes resource name (lowercase alphanumeric and hyphens)

**Impact**: Determines the PVC name used for image stitching data storage. The ManageWorkspace CR is updated with this PVC reference.

**Related variables**:
- `mas_instance_id`: Prepended to create full PVC name
- `mas_workspace_id`: Prepended to create full PVC name
- `stitching_storage_class`: Storage class for this PVC
- `stitching_storage_size`: Size of this PVC

**Note**: The default `manage-imagestitching` clearly identifies the PVC purpose. Full PVC name example: `civil-masdev-manage-imagestitching`.

### stitching_storage_class
Storage class for image stitching PVC.

- **Optional**
- Environment Variable: `IMAGESTITCHING_STORAGE_CLASS`
- Default: Auto-discovered

**Purpose**: Specifies the Kubernetes storage class to use for the image stitching PVC. Must support ReadWriteMany (RWX) access mode.

**When to use**:
- Use default (auto-discovery) if cluster has suitable RWX storage class
- Override to specify a particular RWX-capable storage class
- Required when multiple RWX storage classes exist

**Valid values**: Valid Kubernetes storage class name that supports RWX (e.g., `nfs-client`, `ocs-storagecluster-cephfs`, `ibmc-file-gold`)

**Impact**: Determines the underlying storage technology for image stitching data. Must support ReadWriteMany for multiple pod access.

**Related variables**:
- `stitching_pvcname`: PVC using this storage class
- `stitching_storage_mode`: Must be `ReadWriteMany`
- `stitching_storage_size`: Size of storage to provision

**Note**: **CRITICAL** - The storage class MUST support ReadWriteMany (RWX) access mode as image stitching requires shared access from multiple pods. Common RWX storage classes include NFS, CephFS, and IBM Cloud File Storage.

### stitching_storage_size
PVC storage size for image stitching.

- **Optional**
- Environment Variable: `IMAGESTITCHING_STORAGE_SIZE`
- Default: `20Gi`

**Purpose**: Specifies the size of the persistent volume claim for storing image stitching data and processed images.

**When to use**:
- Use default (`20Gi`) for small to medium deployments
- Increase for large-scale infrastructure inspection projects
- Consider image resolution and retention requirements

**Valid values**: Kubernetes storage size format (e.g., `20Gi`, `50Gi`, `100Gi`, `1Ti`)

**Impact**: Determines how much image data can be stored. Insufficient storage will prevent new image processing.

**Related variables**:
- `stitching_pvcname`: PVC with this size
- `stitching_storage_class`: Storage class providing this capacity

**Note**: Size requirements depend on:
- Number of images processed
- Image resolution and format
- Retention period for processed images
- Number of concurrent stitching operations
Start with 20Gi and monitor usage to adjust as needed.

### stitching_storage_mode
PVC access mode for image stitching.

- **Optional**
- Environment Variable: `IMAGESTITCHING_STORAGE_MODE`
- Default: `ReadWriteMany`

**Purpose**: Specifies the Kubernetes access mode for the image stitching PVC. Must be ReadWriteMany to allow multiple pods to access the storage simultaneously.

**When to use**:
- Always use default `ReadWriteMany` for image stitching
- Do not change unless you understand the implications
- Required for multi-pod access to shared data

**Valid values**: `ReadWriteMany` (RWX) - other modes not supported

**Impact**: Enables multiple Manage pods to read and write image stitching data concurrently. Essential for distributed image processing.

**Related variables**:
- `stitching_storage_class`: Must support this access mode
- `stitching_pvcname`: PVC with this access mode

**Note**: **CRITICAL** - ReadWriteMany (RWX) is mandatory for image stitching functionality. Do not change this value. Ensure your storage class supports RWX access mode.

### stitching_storage_mountpath
Mount path for image stitching storage.

- **Optional**
- Environment Variable: `IMAGESTITCHING_STORAGE_MOUNTPATH`
- Default: `imagestitching`

**Purpose**: Specifies the mount path where the image stitching PVC is mounted in Manage pods.

**When to use**:
- Use default (`imagestitching`) for standard deployments
- Override only if you have specific path requirements
- Must not conflict with other mount paths

**Valid values**: Valid Linux filesystem path component (alphanumeric, no leading slash)

**Impact**: Determines where image stitching data is accessible within Manage pods. The `imagestitching.dataInputPath` system property is set to this path.

**Related variables**:
- `stitching_pvcname`: PVC mounted at this path

**Note**: The default `imagestitching` is relative to the Manage pod's base mount path. The full path is constructed by Manage. Do not include leading or trailing slashes.

## Example Playbook

The following sample will configure image stitching for an existing Manage application instance via ManageWorkspace CR update:

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: civil
    mas_workspace_id: masdev
    mas_domain: civil.ibmmasdev.com
    stitching_pvcname: manage-imagestitching
    stitching_storage_class: nfs-client
    stitching_storage_size: 20Gi
    stitching_storage_mode: ReadWriteMany
    stitching_storage_mountpath: imagestitching
  roles:
    - ibm.mas_devops.suite_manage_imagestitching_config
```

## License

EPL-2.0
