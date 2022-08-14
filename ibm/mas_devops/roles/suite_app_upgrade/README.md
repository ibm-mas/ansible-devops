suite_app_upgrade
===============================================================================
This role will upgrade the subscription channel for an an installed MAS application after validating:

- That the application is installed and in a healthy state
- That the new version of the application can be upgraded to from the existing version
- That the new version of the application is compatible with the running MAS core platform


Role Variables
-------------------------------------------------------------------------------
### mas_instance_id
Set the instance ID for the MAS installation where you wish to upgrade the application.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### mas_app_channel
Select the subscription channel you wish to upgrade to.  Built-in validation will ensure that the upgrade will only proceed if a supportable upgrade path is chosen.

- **Required**
- Environment Variable: `MAS_APP_CHANNEL`
- Default Value: None

### mas_upgrade_dryrun
When set to `true` will ensure that the role only preforms upgrade validation checks and does not make any changes to the target installation.

- Optional
- Environment Variable: `MAS_UPGRADE_DRYRUN`
- Default: `False`


Example Playbook
-------------------------------------------------------------------------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: instance1
    mas_app_id: iot
    mas_app_channel: 8.5.x
  roles:
    - ibm.mas_devops.suite_app_upgrade
```
