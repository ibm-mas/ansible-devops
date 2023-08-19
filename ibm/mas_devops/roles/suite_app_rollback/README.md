suite_app_rollback
===============================================================================
This role is to roll back Maximo Application Suite Applications to an earlier version. Currently, this is designed for Manage Application only. Rollback is possible only in 8.7 and later. From 8.7 onwards, every version comes with a set of supported versions to which the Application can be rolled back. For example, you can roll back Manage Application from 8.7.x to 8.7.0. 
This role will rollback the version for an an installed MAS application after validating:
- That the specificied version of application is compatible to rollback from the current version. 
- That the specificied version of application is compatible with the running MAS core platform.

It will rollback the Manage Application to the desired version.
It will validate that the Manage Application has been successfully reconciled at the rolled back version.

Role Variables
-------------------------------------------------------------------------------
### mas_instance_id
Set the instance ID for the MAS installation where you wish to rollback the application.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### rollback_mas_app
When set to `true` will ensure that the role performs rollback operation.

- optional
- Environment Variable: `ROLLBACK_MAS_APP`
- Default: True

### verify_app_version
When set to `true` will ensure that the role checks the current Manage Appliation version matches with specified version. 

- optional
- Environment Variable: `VERIFY_APP_VERSION`
- Default: False

### mas_app_version
The version you wish to rollback to.  Built-in validation will ensure that the rollback will only proceed if a supportable rollback path is chosen. It is required when any of the ROLLBACK_MAS_APP and VERIFY_APP_VERSION variables is set to `true`.

- **Required**
- Environment Variable: `MAS_APP_VERSION`
- Default Value: None

### mas_app_id
The name of the Maximo Application Suite Application. This will be used to lookup for application namespace and resources. Please be aware that at present, 'manage' is the only supported value for this variable.

- **Required**
- Environment Variable: `MAS_APP_ID`
- Default Value: None 


Example Playbook
-------------------------------------------------------------------------------
### Automatic Target Selection
Running this playbook will rollback Manage Application to the 8.7.1 version. If you run this playbook when you are already on the same version it will take no action.

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: instance1
    mas_app_id: manage
    mas_app_version: 8.7.1
  roles:
    - ibm.mas_devops.suite_app_rollback
```

### Verify Manage App version
Running this playbook will attempt to verify the current version of Manage Application matches with the specified version. 
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: instance1
    mas_app_id: manage
    mas_app_version: 8.7.1
    rollback_mas_app: False
    verify_app_version: True
  roles:
    - ibm.mas_devops.suite_app_rollback
```
