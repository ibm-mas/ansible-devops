suite_uninstall
===============================================================================
This role removes Maximo Application Suite Core Platform.  Note that it does not remove any data from MongoDb, and does not remove any applications from the MAS install, generally it should be used after `suite_app_uninstall` to remove all installed Maximo Applicaton Suite applications.

Role Variables
-------------------------------------------------------------------------------

### mas_instance_id
Defines the MAS instance to be removed from the cluster

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

### mas_wipe_mongo_data
Defines whether Mongo databases should be deleted along with MAS uninstall

- **Optional**
- Environment Variable: `MAS_WIPE_MONGO_DATA`
- Default: False


Example Playbook
-------------------------------------------------------------------------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: "inst1"

  roles:
    - ibm.mas_devops.suite_uninstall
```


License
-------------------------------------------------------------------------------

EPL-2.0
