suite_app_configure
===================

TODO: Summarize role

Role Variables
--------------
### mas_app_ws_spec
Optional.  The application workspace deployment spec used to configure various aspects of the application workspace configuration. 

- Environment Variable: None
- Default: defaults are specified in vars/defaultspecs/{{mas_app_id}}.yml

Example,
```
- hosts: localhost
  any_errors_fatal: true
    roles:
    # Cofigure Manage App
    - role: ibm.mas_devops.suite_app_configure
        vars:
          mas_app_id: manage
          mas_app_ws_spec:
            bindings:
              jdbc: "{{ mas_appws_jdbc_binding | default( 'system' , true) }}"
              components: "{{ mas_appws_components | default({'base': {'version': 'latest'}}, true) }}"
```

TODO: Finish documentation


Example Playbook
----------------

```yaml
TODO: Add example
```

License
-------

EPL-2.0
