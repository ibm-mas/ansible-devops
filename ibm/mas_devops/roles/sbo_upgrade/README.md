sbo_upgrade
=============
This role will upgrade Service Binding Operator version 0.8v (preview channel) to 1.0.x (stable channel), which is the supported SBO version for MAS 8.7+

For more information, please refer to [Upgrading Maximo Application Suite](https://www.ibm.com/docs/en/mas87/8.7.0?topic=upgrading) documentation.

Role Variables
--------------
### mas_instance_id
Required - Defines the instance id that is used in the existing MAS installation, will be used to lookup the existing Service Binding resources associated to your MAS instance, to ensure it is ready to support SBO version 1.0.x.

- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  roles:
    - ibm.mas_devops.sbo_upgrade
```
