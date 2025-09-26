aiservice_upgrade
===============================================================================
This role validates if a given AI SERVICE installation is ready to be upgraded to a specific subscription channel, and (as long as dry run mode is not enabled) will execute the upgrade.

- It will validate that the current subscription channel is able to be upgraded to the target channel.
- It will upgrade the AI SERVICE to the desired channel (as long as dry run is not enabled).
- It will validate that the AI Service has been successfully reconciled at the upgraded version.
- It will **not** validate that all AI Service services successfully deploy after the reconcile (but we will be working on this limitation).


Role Variables
-------------------------------------------------------------------------------
### aiservice_instance_id
The ID of the AI SERVICE instance to upgrade.

- **Required**
- Environment Variable: `AISERVICE_INSTANCE_ID`
- Default: None

### aiservice_channel
The name of the AISERVICE subscription channel that you want to upgrade to, if not provided the correct version to upgrade to will be automatically selected based on the current version of AISERVICE installed.

- Optional
- Environment Variable: `AISERVICE_CHANNEL`
- Default: None

### aiservice_upgrade_dryrun
When set to `true` will ensure that the role only preforms upgrade validation checks and does not make any changes to the target installation.

- Optional
- Environment Variable: `AISERVICE_UPGRADE_DRYRUN`
- Default: `False`

Example Playbook
-------------------------------------------------------------------------------
### Automatic Target Selection
Running this playbook will upgrade AI Service to the next release.  If you run this playbook when you are already on the latest release then it will take no action.

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    aiservice_instance_id: instance1
    aiservice_upgrade_dryrun: False
  roles:
    - ibm.mas_devops.aiservice_upgrade
```

### Explicit Upgrade Target
Running this playbook will attempt to upgrade AI Service to the specified release.  If the specified release cannot be upgraded to from the installed version of AI Service then no action will be taken.
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    aiservice_instance_id: instance1
    aiservice_channel: 9.1.x
    aiservice_upgrade_dryrun: False
  roles:
    - ibm.mas_devops.aiservice_upgrade
```
