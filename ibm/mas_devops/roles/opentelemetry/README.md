opentelemetry
===============================================================================
Install and configure [OpenTelemetry operator](https://github.com/open-telemetry/opentelemetry-operator) for IBM Maximo Application Suite (in `openshift-operators` namespace).

Role Variables
-------------------------------------------------------------------------------
### opentelemetry_action
Inform the role whether to perform an `install` or an `uninstall` of Open Telemetry.

- Optional
- Environment Variable: `OPENTELEMETRY_ACTION`
- Default: `install`


Example Playbook
-------------------------------------------------------------------------------

```yaml
- hosts: localhost
  vars:
    opentelemetry_action: "install"
  roles:
    - ibm.mas_devops.opentelemetry
```


License
-------------------------------------------------------------------------------

EPL-2.0
