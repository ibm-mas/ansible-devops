ocp_roks_upgrade_registry_storage
=================================

This role will use IBMCloud APIs to upgrade the capacity of the volume backing the OCP cluster's image registry.  The volume will be increased from the default capacity of 100GB to 400GB.  This is needed if you intend to install all of the services available in CloudPak for Data because the 100GB volume is not large enough.


Role Variables
--------------
### ibmcloud_apikey
The APIKey to be used to modify the storage volume associated with the image registry.

- Environment Variable: `IBMCLOUD_APIKEY`
- Default Value: None


Example Playbook
----------------

```yaml
- hosts: localhost
  roles:
    - ibm.mas_devops.ocp_roks_tuning
```


License
-------

EPL-2.0
