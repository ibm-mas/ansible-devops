suite_app_uninstall
===============================================================================

This role is used to uninstall a specified application in Maximo Application Suite.


Role Variables - General
-------------------------------------------------------------------------------
### mas_instance_id
Defines the MAS instance id from which an appplication will be uninstalled

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

### mas_app_id
Defines the kind of application that will be uninstalled such as `assist`, `health`, `hputilities`, `iot`, `manage`, `monitor`, `mso`, `optimizer`, `predict`, `safety` or `visualinspection`

- **Required**
- Environment Variable: `MAS_APP_ID`
- Default: None


Example Playbook
-------------------------------------------------------------------------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    # MAS configuration
    mas_instance_id: "{{ lookup('env', 'MAS_INSTANCE_ID') }}"

    # MAS application configuration
    mas_app_id: "{{ lookup('env', 'MAS_APP_ID') }}"

  roles:
    - ibm.mas_devops.suite_app_uninstall
```

License
-------------------------------------------------------------------------------

EPL-2.0
