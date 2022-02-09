suite_app_install
=================

TODO: Summarize role

Role Variables
--------------
### mas_app_spec
Optional.  The application deployment spec used to configure various aspects of the application deployment configuration. 

- Environment Variable: None
- Default: defaults are specified in vars/defaultspecs/{{mas_app_id}}.yml

Example,
```
- hosts: localhost
  any_errors_fatal: true
    roles:
    # Install IoT App
    - role: ibm.mas_devops.suite_app_install
        vars:
          mas_app_catalog_source: ibm-mas-iot-operators
          mas_app_channel: 8.x
          mas_app_id: iot
          mas_app_spec:
            bindings:
              jdbc: system
              mongo: system
              kafka: system
            components: {}
            settings:
              messagesight:
                storage:
                  class: block1000p
                  size: 100Gi
              deployment:
                size: medium
```

Example Playbook
----------------

```yaml
TODO: Add example
```

License
-------

EPL-2.0
