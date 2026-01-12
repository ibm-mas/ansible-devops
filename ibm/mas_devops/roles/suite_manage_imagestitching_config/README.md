# suite_manage_imagestitching_config

This role configures the manage workspace to autodeploy the image stitching application. The role will only make changes if the Civil component has been installed. It will configure a PVC, patch the ManageWorkspace CR with the name of the PVC and also patch PV specifications based on the PVC. It also sets two key system properties required by the image stitching application: 'mci.imagestitching.apiurl' and 'imagestitching.dataInputPath'.

**Note:** This role should be executed **after** Manage application is deployed and activated as it needs Manage up and running in order to set system properties.

## Role Variables

### mas_instance_id
The instance ID of Maximo Application Suite. This will be used to lookup for Manage application resources.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

### mas_workspace_id
The workspace ID of Maximo Application Suite. This will be used to lookup for Manage application resources.

- **Required**
- Environment Variable: `MAS_WORKSPACE_ID`
- Default: None

### mas_domain
The domain name for the Manage cluster.

- **Required**
- Environment Variable: `MAS_DOMAIN`
- Default: Discovered from Suite CR

### stitching_pvcname
The postfix for the PVC created for image stitching. The ManageWorkspace CR will prepend 'mas_instance_id-mas_workspace_id-' to generate the actual name of the PVC.

- **Required**
- Environment Variable: `IMAGESTITCHING_PVCNAME`
- Default: `manage-imagestitching`

### stitching_storage_class
The storage class used for the PVC. If not specified the default value will be found by discovery. The storage class must support ReadWriteMany(RWX) access mode.

- **Optional**
- Environment Variable: `IMAGESTITCHING_STORAGE_CLASS`
- Default: None

### stitching_storage_size
The size of the persistent volume claim.

- **Required**
- Environment Variable: `IMAGESTITCHING_STORAGE_SIZE`
- Default: `20Gi`

### stitching_storage_mode
The access mode for the PVC.

- **Required**
- Environment Variable: `IMAGESTITCHING_STORAGE_MODE`
- Default: `ReadWriteMany`

### stitching_storage_mountpath
The mount path of the Persistent Volume.

- **Required**
- Environment Variable: `IMAGESTITCHING_STORAGE_MOUNTPATH`
- Default: `imagestitching`

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
