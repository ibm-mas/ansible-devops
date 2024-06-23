Backup and Restore MAS Core
===============================================================================

Overview
-------------------------------------------------------------------------------
This role supports backing up and restoring MAS Core namespace resources.

Before running the role, you must set several environment variables to indicate this role where to save and retrieve the backup files. Please refer to [this doc](../playbooks/masbr-storage.md) to understand how to configure the storage system and related environment variables.

This role supports creating on-demand or scheduled backup jobs for taking full or incremental backups, please refer to [this doc](../playbooks/masbr-vars.md#backup) for more information about the backup related environment variables.

This role supports creating jobs for running the restore process, please refer to [this doc](../playbooks/masbr-vars.md#restore) for more information about the restore related environment variables.

!!! important
    Before you run this role, please make sure the MAS Core are installed and running properly on the target cluster.

!!! important
    The `MAS_INSTANCE_ID` in the target environment must be same as the values in the backup files which you taken from the source cluster.


Environment variables
-------------------------------------------------------------------------------
!!! tip
    You also need to set some other common environment variables for creating backup/restore jobs, please refer to [this doc](../playbooks/masbr-vars.md) for details.

Below environment variables are required for this role:

- `MASBR_ACTION`: Set `backup` or `restore` to indicate the role to create a backup or restore job.

- `MAS_INSTANCE_ID`: This role only supports backing up data belong to a specific MAS instance at a time. If you have multiple MAS instances in the cluster to be backed up, you need to run this role multiple times with different value of this environment variable.


Example
-------------------------------------------------------------------------------
!!! important
    Before you proceed with the following steps, please refer to [this doc](../playbooks/prepare-env.md) to prepare the testing environment.

This role back up and restore the supported MAS applications in a similar way. In this example, we will use Manage to demonstrate how to:

- Back up MAS Core namespace resources
- Restore MAS Core namespace resources

### Back up MAS Core namespace resources
Run below command in the container to take a backup of MAS Core namespace resources:

```shell
$ export MASBR_ACTION=backup
$ export MAS_INSTANCE_ID=main

$ ROLE_NAME=suite_backup_restore ansible-playbook ibm.mas_devops.run_role
```

### Restore MAS Core namespace resources
Run below command in the container to restore MAS Core namespace resources:

```shell
$ export MASBR_RESTORE_FROM_VERSION=20240621021316

$ export MASBR_ACTION=restore
$ export MAS_INSTANCE_ID=main

$ ROLE_NAME=suite_backup_restore ansible-playbook ibm.mas_devops.run_role
```

License
-------------------------------------------------------------------------------

EPL-2.0
