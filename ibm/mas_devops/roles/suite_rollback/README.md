suite_rollback
===============================================================================
This role is to roll back Maximo Application Suite to an earlier version. Rollback is possible only in 8.11 and later. From 8.11 onwards, every version comes with a set of supported versions to which Suite can be rolled back. For example, you can roll back Maximo Application Suite from 8.11.x to 8.11.0. This role validates given MAS installation is ready for the core platform to be rolled back to a specific MAS core version, and (as long as dry run mode is not enabled) will execute the rollback.

- It will validate that the specified version is compatible to rollback from the current version.
- It will validate that the core is already running at the targetted version.
- It will rollback the MAS core platform to the desired version (as long as dry run is not enabled).
- It will validate that the core platform has been successfully reconciled at the rolled back version.
- It will **not** validate that all core services successfully deploy after the reconcile (but we will be working on this limitation).


Role Variables
-------------------------------------------------------------------------------
### mas_instance_id
The ID of the MAS instance to rollback.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

### rollback_mas_core
When set to `true` will ensure that the role performs rollback operation.

- optional
- Environment Variable: `ROLLBACK_MAS_CORE`
- Default: True

### verify_core_version
When set to `true` will ensure that the role checks the current MAS core version matches with specified version. 

- optional
- Environment Variable: `VERIFY_CORE_VERSION`
- Default: False

### mas_core_version
The version of the MAS core that you want to rollback to or to validate current version. It is required when any of the ROLLBACK_MAS_CORE and VERIFY_CORE_VERSION variables is set to `true`.

- **Required**
- Environment Variable: `MAS_CORE_VERSION`
- Default: None

### mas_rollback_dryrun
When set to `true` will ensure that the role only preforms rollback validation checks and does not make any changes to the target installation.

- Optional
- Environment Variable: `MAS_ROLLBACK_DRYRUN`
- Default: `False`

Example Playbook
-------------------------------------------------------------------------------
### Automatic Target Selection
Running this playbook will rollback MAS core to the specified version.  If you run this playbook when you are already on the same version it will take no action.

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: instance1
    mas_core_version: 8.11.0
    mas_rollback_dryrun: False
  roles:
    - ibm.mas_devops.suite_rollback
```

### Verify MAS core version
Running this playbook will attempt to verify the current version of MAS core matches with the specified version. 
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: instance1
    mas_core_version: 8.11.0
    mas_upgrade_dryrun: False
    rollback_mas_core: False
    verify_core_version: True
  roles:
    - ibm.mas_devops.suite_rollback
```
