install_digest_cm
===============================================================================

This role installs the additional ConfigMaps that enable disconnected install support in early Maximo Application Suite operators.  It is being phased-out in favour of built-in disconnect install support from MAS 8.8 onwards.

!!! note
    This is an internal role, you should not need to explicitly call this yourself.  It will automatically be invoked at the appropriate time when using roles in ibm.mas_devops if it detects the environment is running in disconnected mode.


Role Variables
-------------------------------------------------------------------------------

### case_name
The name of the IBM CASE bundle that contains the digest ConfigMap.

- **Required**
- Environment Variable: None
- Default: None

### case_version
Version of the IBM CASE bundle from which the digest ConfigMap should be taken.

- **Required**
- Environment Variable: None
- Default: None

### digest_image_map_namespace
The namespace where the ConfigMap will be created.

- **Required**
- Environment Variable: None
- Default: None


License
-------------------------------------------------------------------------------
EPL-2.0