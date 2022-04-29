suite_upgrade_check
=============

This role just validates if a given MAS 8.6.x instance is ready to be upgraded to MAS 8.7.x version in an OpenShift Cluster.
This checks for readiness for MAS Core and all the existing application version deployed. 
In order to be able to upgrade to MAS 8.7 version, your MAS instance will need to have latest MAS 8.6 correspondent patches for MAS Core and applications.
For more information, please refer to [Upgrading Maximo Application Suite](https://www.ibm.com/docs/en/mas87/8.7.0?topic=upgrading) documentation.

Role Variables
--------------

- `mas_instance_id` Defines the instance id that is used in the existing MAS installation, will be used to lookup the existing MAS subscription.

Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  roles:
    - ibm.mas_devops.suite_upgrade_check
```
