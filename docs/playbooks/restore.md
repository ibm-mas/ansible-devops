Restoring MAS
===============================================================================

Overview
-------------------------------------------------------------------------------
MAS Devops Collection includes playbooks for restoring the following MAS components and their dependencies:

- [MongoDB](#restoring-mongodb)
- [Db2](#restoring-db2)
- [MAS Core](#restoring-mas-core)
- [Manage](#restoring-manage)
- [IoT](#restoring-iot)
- [Monitor](#restoring-monitor)
- [Optimizer](#restoring-optimizer)
- [Visual Inspection](#restoring-visual-inspection)

Before running the playbooks to restore different MAS components, you must set several environment variables to indicate the playbooks where to retrieve the backup files. Please refer to [this doc](masbr-storage.md) to understand how to configure the storage system and related environment variables.

The playbooks support creating jobs for running the restore process, please refer to [this doc](masbr-vars.md#restore) for more information about the restore related environment variables.

!!! important
    Before you run the playbooks, please make sure the MAS components are installed and running properly on the target cluster.

!!! important
    The `MAS_INSTANCE_ID` and `MAS_WORKSPACE_ID` in the target environment must be same as the values in the backup files which you taken from the source cluster.


Restoring MongoDB
-------------------------------------------------------------------------------
This playbook `ibm.mas_devops.restore_mongodb` will invoke the role [mongodb](../roles/mongodb.md) to restore MongoDB databases from the backup files located on the specified backup storage location.

Currently, this playbook only support restore databases for MongoDB CE. If you are using other MongoDB venders, such as IBM Cloud Databases for MongoDB, Amazon DocumentDB or MongoDB Altas Database, please refer to the corresponding vender's documentation for more information about their provided backup/restore service.

The playbook will restore all databases found in the specified MongoDB backup file, you cannot choose to restore only selected databases.

Below environment variables are required for this playbook:

- `MAS_INSTANCE_ID`: This playbook will restore the MongoDB databases belong to this MAS instance in the target cluster.

- `MAS_APP_ID`: By default, this playbook will restore all MongoDB databases belong to the specified MAS instance. You can restore the databases only belong to a specific MAS application by setting this environment variable.

Please refer to the [example](#example) on how to use this playbook.


Restoring Db2
-------------------------------------------------------------------------------
This playbook `ibm.mas_devops.restore_db2` will invoke the role [db2](../roles/db2.md) to restore Db2 instance from the backup files located on the specified backup storage location.

Below environment variables are required for this playbook:

- `DB2_INSTANCE_NAME`: This playbook will restore the data belong to this Db2 instance in the target cluster.

Please refer to the [example](#example) on how to use this playbook.


Restoring MAS Core
-------------------------------------------------------------------------------
This playbook `ibm.mas_devops.restore_core` will restore the following components that MAS Core depends on in order:

| Component | Role | Data included |
| --------- | ----- | ----- |
| mongodb | [mongodb](../roles/mongodb.md) | MongoDB databases used by MAS Core |
| core | [suite_backup_restore](../roles/suite_backup_restore.md) | MAS Core namespace resources |

!!! tip
    If you only want to restore a certain of above components, you should run a single role instead of using this playbook. Please refer to the corresponding role for details.

Below environment variables are required for this playbook:

- `MAS_INSTANCE_ID`: This playbook will restore the data belong to this MAS instance in the target cluster.

Please refer to the [example](#example) on how to use this playbook.


Restoring Manage
-------------------------------------------------------------------------------
This playbook `ibm.mas_devops.restore_manage` will restore the following components that Manage depends on in order:

| Component | Role | Data included |
| --------- | ----- | ----- |
| mongodb | [mongodb](../roles/mongodb.md) | MongoDB databases used by MAS Core |
| db2 | [db2](../roles/db2.md) | Db2 instance used by Manage |
| core | [suite_backup_restore](../roles/suite_backup_restore.md) | MAS Core namespace resources |
| manage | [suite_app_backup_restore](../roles/suite_app_backup_restore.md) | - Manage namespace resources <br>- Persistent volume data, such as attachments |

!!! tip
    If you only want to restore a certain of above components, you should run a single role instead of using this playbook. Please refer to the corresponding role for details.

Below environment variables are required for this playbook:

- `MAS_INSTANCE_ID`: This playbook will restore the data belong to this MAS instance in the target cluster.

- `MAS_WORKSPACE_ID`: This playbook will restore the data belong to this MAS workspace in the target cluster.

- `DB2_INSTANCE_NAME`: This playbook will restore the the Db2 instance used by Manage, you need to set the correct Db2 instance name for this environment variable.

Please refer to the [example](#example) on how to use this playbook.


Restoring IoT
-------------------------------------------------------------------------------
This playbook `ibm.mas_devops.restore_iot` will restore the following components that IoT depends on in order:

| Component | Role | Data included |
| --------- | ----- | ----- |
| mongodb | [mongodb](../roles/mongodb.md) | MongoDB databases used by MAS Core and IoT |
| db2 | [db2](../roles/db2.md) | Db2 instance used by IoT |
| core | [suite_backup_restore](../roles/suite_backup_restore.md) | MAS Core namespace resources |
| iot | [suite_app_backup_restore](../roles/suite_app_backup_restore.md) | IoT namespace resources |

!!! tip
    If you only want to restore a certain of above components, you should run a single role instead of using this playbook. Please refer to the corresponding role for details.

Below environment variables are required for this playbook:

- `MAS_INSTANCE_ID`: This playbook will restore the data belong to this MAS instance in the target cluster.

- `MAS_WORKSPACE_ID`: This playbook will restore the data belong to this MAS workspace in the target cluster.

- `DB2_INSTANCE_NAME`: This playbook will restore the the Db2 instance used by IoT, you need to set the correct Db2 instance name for this environment variable.

Please refer to the [example](#example) on how to use this playbook.


Restoring Monitor
-------------------------------------------------------------------------------
This playbook `ibm.mas_devops.restore_monitor` will restore the following components that Monitor depends on in order:

| Component | Role | Data included |
| --------- | ----- | ----- |
| mongodb | [mongodb](../roles/mongodb.md) | MongoDB databases used by MAS Core, IoT and Monitor |
| db2 | [db2](../roles/db2.md) | Db2 instance used by IoT and Monitor |
| core | [suite_backup_restore](../roles/suite_backup_restore.md) | MAS Core namespace resources |
| iot | [suite_app_backup_restore](../roles/suite_app_backup_restore.md) | IoT namespace resources |
| monitor | [suite_app_backup_restore](../roles/suite_app_backup_restore.md) | Monitor namespace resources |

!!! tip
    If you only want to restore a certain of above components, you should run a single role instead of using this playbook. Please refer to the corresponding role for details.

Below environment variables are required for this playbook:

- `MAS_INSTANCE_ID`: This playbook will restore the data belong to this MAS instance in the target cluster.

- `MAS_WORKSPACE_ID`: This playbook will restore the data belong to this MAS workspace in the target cluster.

- `DB2_INSTANCE_NAME`: This playbook will restore the the Db2 instance used by IoT and Monitor, you need to set the correct Db2 instance name for this environment variable.

Please refer to the [example](#example) on how to use this playbook.


Restoring Optimizer
-------------------------------------------------------------------------------
This playbook `ibm.mas_devops.restore_optimizer` will restore the following components that Optimizer depends on in order:

| Component | Role | Data included |
| --------- | ----- | ----- |
| mongodb | [mongodb](../roles/mongodb.md) | MongoDB databases used by MAS Core and Optimizer |
| db2 | [db2](../roles/db2.md) | Db2 instance used by Manage |
| core | [suite_backup_restore](../roles/suite_backup_restore.md) | MAS Core namespace resources |
| manage | [suite_app_backup_restore](../roles/suite_app_backup_restore.md) | - Manage namespace resources <br>- Persistent volume data, such as attachments |
| optimizer | [suite_backup_restore](../roles/suite_backup_restore.md) | Optimizer namespace resources |

!!! tip
    If you only want to restore a certain of above components, you should run a single role instead of using this playbook. Please refer to the corresponding role for details.

Below environment variables are required for this playbook:

- `MAS_INSTANCE_ID`: This playbook will restore the data belong to this MAS instance in the target cluster.

- `MAS_WORKSPACE_ID`: This playbook will restore the data belong to this MAS workspace in the target cluster.

- `DB2_INSTANCE_NAME`: This playbook will restore the the Db2 instance used by Manage, you need to set the correct Db2 instance name for this environment variable.

Please refer to the [example](#example) on how to use this playbook.


Restoring Visual Inspection
-------------------------------------------------------------------------------
This playbook `ibm.mas_devops.restore_visualinspection` will restore the following components that Visual Inspection depends on in order:

| Component | Role | Data included |
| --------- | ----- | ----- |
| mongodb | [mongodb](../roles/mongodb.md) | MongoDB databases used by MAS Core and Visual Inspection |
| core | [suite_backup_restore](../roles/suite_backup_restore.md) | MAS Core namespace resources |
| visualinspection | [suite_app_backup_restore](../roles/suite_app_backup_restore.md) | - Visual Inspection namespace resources <br>- Persistent volume data, such as images and models |

!!! tip
    If you only want to restore a certain of above components, you should run a single role instead of using this playbook. Please refer to the corresponding role for details.

Below environment variables are required for this playbook:

- `MAS_INSTANCE_ID`: This playbook will restore the data belong to this MAS instance in the target cluster.

- `MAS_WORKSPACE_ID`: This playbook will restore the data belong to this MAS workspace in the target cluster.

Please refer to the [example](#example) on how to use this playbook.


Example
-------------------------------------------------------------------------------
!!! important
    Before you proceed with the following steps, please refer to [this doc](prepare-env.md) to prepare the testing environment.

All above playbooks support the [common environment variables](masbr-vars.md) to restore the MAS components in a similar way. In this example, we will use Manage to demonstrate how to:

- Creating a Job to restore MAS Core from an incremental backup

### Resore from an incremental backup

First, run below command to get all MAS Core backup jobs from the object storage:
```shell
$ rclone --config ${MASBR_STORAGE_CLOUD_RCLONE_FILE} lsd ${MASBR_STORAGE_CLOUD_RCLONE_NAME}:${MASBR_STORAGE_CLOUD_BUCKET}/backups | grep core
```

You will get a list of backup job folders stored on the object storage, the output is similar to the following: 
```text
           0 2000-01-01 00:00:00        -1 core-main-full-20240621122530-Completed
           0 2000-01-01 00:00:00        -1 core-main-incr-20240622040201-Completed
```

Run below command to restore the data from the backup `core-main-incr-20240622040201-Completed`, the backup version is `20240622040201`:
```shell
$ export MASBR_RESTORE_FROM_VERSION=20240622040201
$ export MAS_INSTANCE_ID=main

$ ansible-playbook ibm.mas_devops.restore_core
```

The playbook will create a k8s Job in the OpenShift cluster to restore MongoDB databases and MAS Core namespace resources one by one, you can get the restore version and job link in the output:
```text
TASK [Summary of restore job] **************************************************************************************************************************************************************
ok: [localhost] =>
  msg:
  - Restore version .................... 20240622075501
  - Restore from ....................... core-main-incr-20240622040201
  - Job name ........................... restore-20240622075501-20240622075523
  - Job link ........................... https://console-openshift-console.apps.lubanbj5.cdl.ibm.com/k8s/ns/mas-main-core/jobs/restore-20240622075501-20240622075523
```

Copy above job link and open it in the web browser to check the restore progress.  

After the restore job is completed, you can login to the object storage web console to check the restore job information, or run below rclone commands in the container to have some checks:

- List the restore folders created by this restore job in the object storage:
```shell
$ export RESTORE_VERSION=20240622075501
$ rclone --config ${MASBR_STORAGE_CLOUD_RCLONE_FILE} lsd ${MASBR_STORAGE_CLOUD_RCLONE_NAME}:${MASBR_STORAGE_CLOUD_BUCKET}/restores | grep ${RESTORE_VERSION}
```

If the restore job is completed successfully, you will get the output similar to the following:
```text
           0 2000-01-01 00:00:00        -1 core-main-incr-20240622040201-20240622075501-Completed
           0 2000-01-01 00:00:00        -1 mongodb-main-incr-20240622040201-20240622075501-Completed
```

- Further check the files in a restore folder:
```shell
$ export FOLDER_NAME=core-main-incr-20240622040201-20240622075501-Completed
$ rclone --config ${MASBR_STORAGE_CLOUD_RCLONE_FILE} tree ${MASBR_STORAGE_CLOUD_RCLONE_NAME}:${MASBR_STORAGE_CLOUD_BUCKET}/restores/${FOLDER_NAME}
```

You will get the output similar to the following:
```text
/
├── log
│   ├── core-main-incr-20240622040201-20240622075501-ansible-log.tar.gz
│   └── core-main-incr-20240622040201-20240622075501-namespace-log.tar.gz
└── restore.yml

1 directories, 3 files
```

- View the detail information of this restore job:
```shell
$ rclone --config ${MASBR_STORAGE_CLOUD_RCLONE_FILE} cat ${MASBR_STORAGE_CLOUD_RCLONE_NAME}:${MASBR_STORAGE_CLOUD_BUCKET}/restores/${FOLDER_NAME}/restore.yml
```

You will get the output similar to the following:
```yaml
---
kind: Restore
name: "core-main-incr-20240622040201-20240622075501"
version: "20240622075501"
from: "core-main-incr-20240622040201"
target:
  domain: "lubanbj7.cdl.ibm.com"
component:
  name: "core"
  instance: "main"
  namespace: "mas-main-core"
data:
  - seq: 1
    type: "namespace"
    phase: "Completed"
status:
  phase: "Completed"
  startTimestamp: "2024-06-22T08:04:19"
  completionTimestamp: "2024-06-22T08:04:33"
```

Reference 
-------------------------------------------------------------------------------

- [Restoring and validating Maximo Application Suite](https://www.ibm.com/docs/en/mas-cd/continuous-delivery?topic=suite-restoring-validating-maximo-application)