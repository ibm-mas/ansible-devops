mirror_case_prepare
===============================================================================
This role generates a mirror manifest file suitable for use with the `oc mirror` command (or the `ibm.mas_airgap.mirror_images` role) from an IBM CASE bundle.

Requirements
-------------------------------------------------------------------------------
The [ibm-pak plugin](https://github.com/IBM/ibm-pak-plugin) must be installed.


Role Variables
-------------------------------------------------------------------------------
### case_name
The name of the CASE bundle to prepare for mirroring.

- **Required**
- Environment Variable: `CASE_NAME`
- Default: None

### case_version
The version of the CASE bundle to prepare for mirroring.

- **Required**
- Environment Variable: `CASE_VERSION`
- Default: None

### registry_public_host
The public hostname for the target registry.  The images will not be mirrored to the registry at this time, but to prepare the manifest we need to know the target destination.

- **Required**
- Environment Variable: `REGISTRY_PUBLIC_HOST`
- Default: None

### registry_public_port
The public port for the target registry.  The images will not be mirrored to the registry at this time, but to prepare the manifest we need to know the target destination.

- **Required**
- Environment Variable: `REGISTRY_PUBLIC_PORT`
- Default: None

### exclude_images
A list of child CASE bundles to exclude from the mirroring process.

- Optional
- Environment Variable: None
- Default: None


Example Playbook
-------------------------------------------------------------------------------

```yaml
- hosts: localhost
  vars:
    case_name: ibm-mas
    case_version: 8.8.1

    exclude_images:
      - ibm-truststore-mgr
      - ibm-sls
      - ibm-mas-assist
      - ibm-mas-iot
      - ibm-mas-manage

    registry_public_host: myregistry.com
    registry_public_port: 32500

  roles:
    - ibm.mas_airgap.mirror_case_prepare
```


License
-------

EPL-2.0
