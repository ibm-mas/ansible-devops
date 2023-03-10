mirror_case_prepare
===============================================================================
This role generates a mirror manifest file suitable for use with the `oc mirror` command (or the `ibm.mas_devops.mirror_images` role) from an IBM CASE bundle.

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


Role Variables - IBM Pak
-------------------------------------------------------------------------------
### ibmpak_skip_verify
Skip the certification verification when downloading CASE bundles with `oc ibm-pak get`.

- Optional
- Environment Variable: `IBMPAK_SKIP_VERIFY`
- Default: `False`

### ibmpak_skip_dependencies
Skip downloading CASE bundle dependencies with `oc ibm-pak get`.

- Optional
- Environment Variable: `IBMPAK_SKIP_DEPENDENCIES`
- Default: `False`

### ibmpak_insecure
Skip TLS/SSL verification when downloading CASE bundles with `oc ibm-pak get`.

- Optional
- Environment Variable: `IBMPAK_INSECURE`
- Default: `False`


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
    - ibm.mas_devops.mirror_case_prepare
```


License
-------

EPL-2.0
