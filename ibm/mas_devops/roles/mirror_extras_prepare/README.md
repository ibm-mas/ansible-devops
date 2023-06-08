mirror_extras_prepare
===============================================================================
This role generates a mirror manifest file suitable for use with the `oc mirror` command (or the `ibm.mas_devops.mirror_images` role) for a specific set of extra images.

Available Extras
-------------------------------------------------------------------------------

| Extra        | Versions     | Description                                                                                    |
| ------------ | ------------ | ---------------------------------------------------------------------------------------------- |
| catalog      | N/A          | Special extra package for mirroring the IBM Maximo Operator Catalog                            |
| db2u         | 1.0.0, 1.0.1 | Extra container images missing from the ibm-db2operator CASE bundle                            |
| mongoce      | 4.2.6, 4.2.23, 4.4.21 | Package containing all images required to use MongoCE Operator in the disconnected environment |
| uds          | 1.0.0, 1.1.0. 1.2.0 | Extra container images missing from the ibm-uds CASE bundle                                    |
| wd           | 5.3.1        | Extra container images missing from the ibm-watson-discovery CASE bundle                       |


Role Variables
-------------------------------------------------------------------------------
### extras_name
The name of the extras package to prepare for mirroring.

- **Required**
- Environment Variable: `EXTRAS_NAME`
- Default: None

### extras_version
The version of the extras package to prepare for mirroring.

- **Required**
- Environment Variable: `EXTRAS_VERSION`
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


Example Playbook
-------------------------------------------------------------------------------

```yaml
- hosts: localhost
  vars:
    extras_name: mongoce
    extras_version: 4.2.6

    registry_public_host: myocp-5f1320191125833da1cac8216c06779e-0000.us-south.containers.appdomain.cloud
    registry_public_port: 32500

  roles:
    - ibm.mas_devops.mirror_extras_prepare
```


License
-------
EPL-2.0
