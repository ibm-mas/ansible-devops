Backup and Restore MAS Applications
===============================================================================

Overview
-------------------------------------------------------------------------------
This role supports backing up and restoring the data for below MAS applications:

- `manage`: Manage namespace resources, persistent volume data
- `iot`: IoT namespace resources
- `monitor`: Monitor namespace resources
- `health`: Health namespace resources
- `optimizer`: Optimizer namespace resources
- `visualinspection`: Visual Inspection namespace resources, persistent volume data

Before running the role, you must set several environment variables to indicate this role where to save and retrieve the backup files. Please refer to [this doc](../playbooks/masbr-storage.md) to understand how to configure the storage system and related environment variables.

This role supports creating on-demand or scheduled backup jobs for taking full or incremental backups, please refer to [this doc](../playbooks/masbr-vars.md#backup) for more information about the backup related environment variables.

This role supports creating jobs for running the restore process, please refer to [this doc](../playbooks/masbr-vars.md#restore) for more information about the restore related environment variables.

!!! important
    Before you run this role, please make sure the MAS components are installed and running properly on the target cluster.

!!! important
    The `MAS_INSTANCE_ID` and `MAS_WORKSPACE_ID` in the target environment must be same as the values in the backup files which you taken from the source cluster.


Environment variables
-------------------------------------------------------------------------------
!!! tip
    You also need to set some other common environment variables for creating backup/restore jobs, please refer to [this doc](../playbooks/masbr-vars.md) for details.

Below environment variables are required for this role:

- `MASBR_ACTION`: Set `backup` or `restore` to indicate the role to create a backup or restore job.

- `MAS_APP_ID`: This role will backup or restore the data for the MAS application specified by this environment variable.

- `MAS_INSTANCE_ID`: This role only supports backing up components belong to a specific MAS instance at a time. If you have multiple MAS instances in the cluster to be backed up, you need to run this role multiple times with different value of this environment variable.

- `MAS_WORKSPACE_ID`: This role only supports backing up components belong to a specific MAS workspace at a time. If you have multiple MAS workspaces in the cluster to be backed up, you need to run this role multiple times with different value of this environment variable.


Example
-------------------------------------------------------------------------------
!!! important
    Before you proceed with the following steps, please refer to [this doc](../playbooks/masbr-prepare.md) to prepare the testing environment.

This role back up and restore the supported MAS applications in a similar way. In this example, we will use Manage to demonstrate how to:

- Back up PV data used by Manage
- Restore PV data for Manage

### Back up PV data used by Manage
Run below command in the container to take a full backup for PV data:

```shell
$ export MASBR_ACTION=backup
$ export MAS_APP_ID=manage
$ export MASBR_BACKUP_DATA=pv

$ export MAS_INSTANCE_ID=main
$ export MAS_WORKSPACE_ID=masdev

$ ROLE_NAME=suite_app_backup_restore ansible-playbook ibm.mas_devops.run_role
```

### Restore PV data for Manage
Run below command in the container to only restore the PV data from backup files:

```shell
$ export MASBR_RESTORE_FROM_VERSION=20240621021316

$ export MASBR_ACTION=restore
$ export MAS_APP_ID=manage
$ export MASBR_RESTORE_DATA=pv

$ export MAS_INSTANCE_ID=main
$ export MAS_WORKSPACE_ID=masdev

$ ROLE_NAME=suite_app_backup_restore ansible-playbook ibm.mas_devops.run_role
```

License
-------------------------------------------------------------------------------

EPL-2.0
