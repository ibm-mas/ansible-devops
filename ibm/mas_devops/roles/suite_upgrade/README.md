suite_upgrade
===============================================================================
This role validates if a given MAS installation is ready for the core platform to be upgraded to a specific subscription channel, and (as long as dry run mode is not enabled) will execute the upgrade.

- It will validate that the current subscription channel is able to be upgraded to the target channel.
- It will validate that all installed applications have already been upgraded to versions compatible with the new version of the Core Platform.
- It will upgrade the MAS core platform to the desired channel (as long as dry run is not enabled).
- It will validate that the core platform has been successfully reconciled at the upgraded version.
- It will **not** validate that all core services successfully deploy after the reconcile, but we will be working on this limitation.


Role Variables
-------------------------------------------------------------------------------
### mas_instance_id
The ID of the MAS instance to upgrade.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

### mas_channel
The name of the MAS subscription channel that you want to upgrade to.

- **Required**
- Environment Variable: `MAS_CHANNEL`
- Default: None

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
    mas_channel: 8.8.x
    mas_upgrade_dryrun: False
  roles:
    - ibm.mas_devops.suite_upgrade_check
```
