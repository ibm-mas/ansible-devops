suite_app_monitoring
===============================================================================

This role is used to install or uninstall OpenTelemetry Operator.


Role Variables - General
-------------------------------------------------------------------------------
### mas_app_monitoring_action
Defines the instance id that was used for the MAS installation

- Optional
- Environment Variable: `MAS_APP_MONITORING_ACTION`
- Default: `install`


Example Playbook
-------------------------------------------------------------------------------

- Install OpenTelemetry Operator

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_app_monitoring_action: "install"
  roles:
    - ibm.mas_devops.suite_app_monitoring
```

- Uninstall OpenTelemetry Operator

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_app_monitoring_action: "uninstall"
  roles:
    - ibm.mas_devops.suite_app_monitoring
```

License
-------------------------------------------------------------------------------

EPL-2.0
