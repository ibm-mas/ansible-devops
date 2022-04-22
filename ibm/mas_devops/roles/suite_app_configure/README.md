suite_app_configure
===================

This role is used to configure specific components of the application workspace after the application has been installed in the Maximo Application Suite.

Role Variables
--------------

### mas_instance_id
Defines the instance id that was used for the MAS installation

### mas_app_id
Defines the kind of application that is intended for installation such as `assist`, `health`, `iot`, `manage`, `monitor`, `mso`, `predict`, or `safety`

### mas_workspace_id
MAS application workspace to use to configure app components

### mas_appws_components
Defines the app components and versions to configure in the application workspace. Takes the form of key=value pairs seperated by a comma i.e. To install health within Manage set `base=latest,health=latest`

- Environment Variable: `MAS_APPWS_COMPONENTS`
- Default:
  For Manage the default is:
    `base=latest`

  For Health (standalone) the default is:
    `health=latest`

### mas_app_ws_spec
Optional.  The application workspace deployment spec used to configure various aspects of the application workspace configuration. Note that use of this will override anything set in `mas_appws_components`

- Environment Variable: None
- Default: defaults are specified in `vars/defaultspecs/{{mas_app_id}}.yml`


Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    # MAS configuration
    mas_instance_id: "{{ lookup('env', 'MAS_INSTANCE_ID') }}"

    # MAS workspace configuration
    mas_workspace_id: "{{ lookup('env', 'MAS_WORKSPACE_ID') }}"

    # MAS application configuration
    mas_app_id: "{{ lookup('env', 'MAS_APP_ID') }}"
    
    mas_app_ws_spec:
      bindings:
        jdbc: "{{ mas_appws_jdbc_binding | default( 'system' , true) }}"

  roles:
    - ibm.mas_devops.suite_app_config
```

License
-------

EPL-2.0
