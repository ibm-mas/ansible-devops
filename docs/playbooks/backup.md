Backing up MAS
===============================================================================

Overview
-------------------------------------------------------------------------------
MAS Devops Collection includes playbooks for backing up the following MAS components and their dependencies:

- [MongoDB](#backing-up-mongodb)
- [Db2](#backing-up-db2)
- [MAS Core](#backing-up-mas-core)
- [Manage](#backing-up-manage)
- [IoT](#backing-up-iot)
- [Monitor](#backing-up-monitor)
- [Optimizer](#backing-up-optimizer)
- [Visual Inspection](#backing-up-visual-inspection)

Before running the playbooks to back up different MAS components, you must set several environment variables to indicate the playbooks where to save the backup files. Please refer to [this doc](masbr-storage.md) to understand how to configure the storage system and related environment variables.

The playbooks support creating on-demand or scheduled backup jobs for taking full or incremental backups, please refer to [this doc](masbr-vars.md#backup) for more information about the backup related environment variables.


Backing up MongoDB
-------------------------------------------------------------------------------
This playbook `ibm.mas_devops.backup_mongodb` will invoke the role [mongodb](../roles/mongodb.md) to back up the MongoDB databases to the specified backup storage location.

Currently, this playbook only support backing up databases from MongoDB CE. If you are using other MongoDB venders, such as IBM Cloud Databases for MongoDB, Amazon DocumentDB or MongoDB Altas Database, please refer to the corresponding vender's documentation for more information about their provided backup/restore service.

Below environment variables are required for this playbook:

- `MAS_INSTANCE_ID`: This playbook only supports backing up MongoDB databases belong to a specific MAS instance at a time. If you have multiple MAS instances in the cluster to be backed up, you need to run this playbook multiple times with different value of this environment variable.

- `MAS_APP_ID`: By default, this playbook will backup all databases belong to the specified MAS instance. You can back up the databases only belong to a specific MAS application by setting this environment variable.

Please refer to the [example](#example) on how to use this playbook.


Backing up Db2
-------------------------------------------------------------------------------
This playbook `ibm.mas_devops.backup_db2` will invoke the role [db2](../roles/db2.md) to back up Db2 instance to the specified backup storage location.

Below environment variables are required for this playbook:

- `DB2_INSTANCE_NAME`: This playbook only supports backing up specific Db2 instance at a time. If you want to back up all Db2 instances in the Db2 cluster, you need to run this playbook multiple times with different value of this environment variable.

Please refer to the [example](#example) on how to use this playbook.


Backing up MAS Core
-------------------------------------------------------------------------------
This playbook `ibm.mas_devops.backup_core` will back up the following components that MAS Core depends on in order:

| Component | Role | Data included |
| --------- | ----- | ----- |
| mongodb | [mongodb](../roles/mongodb.md) | MongoDB databases used by MAS Core |
| core | [suite_backup_restore](../roles/suite_backup_restore.md) | MAS Core namespace resources |

!!! tip
    If you only want to back up a certain of above components, you should run a single role instead of using this playbook. Please refer to the corresponding role for details.

Below environment variables are required for this playbook:

- `MAS_INSTANCE_ID`: This playbook only supports backing up components belong to a specific MAS instance at a time. If you have multiple MAS instances in the cluster to be backed up, you need to run this playbook multiple times with different value of this environment variable.

Please refer to the [example](#example) on how to use this playbook.


Backing up Manage
-------------------------------------------------------------------------------
This playbook `ibm.mas_devops.backup_manage` will back up the following components that Manage depends on in order:

| Component | Role | Data included |
| --------- | ----- | ----- |
| mongodb | [mongodb](../roles/mongodb.md) | MongoDB databases used by MAS Core |
| db2 | [db2](../roles/db2.md) | Db2 instance used by Manage |
| core | [suite_backup_restore](../roles/suite_backup_restore.md) | MAS Core namespace resources |
| manage | [suite_app_backup_restore](../roles/suite_app_backup_restore.md) | - Manage namespace resources <br>- Persistent volume data, such as attachments |

!!! tip
    If you only want to back up a certain of above components, you should run a single role instead of using this playbook. Please refer to the corresponding role for details.

Below environment variables are required for this playbook:

- `MAS_INSTANCE_ID`: This playbook only supports backing up components belong to a specific MAS instance at a time. If you have multiple MAS instances in the cluster to be backed up, you need to run this playbook multiple times with different value of this environment variable.

- `MAS_WORKSPACE_ID`: This playbook only supports backing up components belong to a specific MAS workspace at a time. If you have multiple MAS workspaces in the cluster to be backed up, you need to run this playbook multiple times with different value of this environment variable.

- `DB2_INSTANCE_NAME`: This playbook will back up the the Db2 instance used by Manage, you need to set the correct Db2 instance name for this environment variable.

Please refer to the [example](#example) on how to use this playbook.


Backing up IoT
-------------------------------------------------------------------------------
This playbook `ibm.mas_devops.backup_iot` will back up the following components that IoT depends on in order:

| Component | Role | Data included |
| --------- | ----- | ----- |
| mongodb | [mongodb](../roles/mongodb.md) | MongoDB databases used by MAS Core and IoT |
| db2 | [db2](../roles/db2.md) | Db2 instance used by IoT |
| core | [suite_backup_restore](../roles/suite_backup_restore.md) | MAS Core namespace resources |
| iot | [suite_app_backup_restore](../roles/suite_app_backup_restore.md) | IoT namespace resources |

!!! tip
    If you only want to back up a certain of above components, you should run a single role instead of using this playbook. Please refer to the corresponding role for details.

Below environment variables are required for this playbook:

- `MAS_INSTANCE_ID`: This playbook only supports backing up components belong to a specific MAS instance at a time. If you have multiple MAS instances in the cluster to be backed up, you need to run this playbook multiple times with different value of this environment variable.

- `MAS_WORKSPACE_ID`: This playbook only supports backing up components belong to a specific MAS workspace at a time. If you have multiple MAS workspaces in the cluster to be backed up, you need to run this playbook multiple times with different value of this environment variable.

- `DB2_INSTANCE_NAME`: This playbook will back up the the Db2 instance used by IoT, you need to set the correct Db2 instance name for this environment variable.

Please refer to the [example](#example) on how to use this playbook.


Backing up Monitor
-------------------------------------------------------------------------------
This playbook `ibm.mas_devops.backup_monitor` will back up the following components that Monitor depends on in order:

| Component | Role | Data included |
| --------- | ----- | ----- |
| mongodb | [mongodb](../roles/mongodb.md) | MongoDB databases used by MAS Core, IoT and Monitor |
| db2 | [db2](../roles/db2.md) | Db2 instance used by IoT and Monitor |
| core | [suite_backup_restore](../roles/suite_backup_restore.md) | MAS Core namespace resources |
| iot | [suite_app_backup_restore](../roles/suite_app_backup_restore.md) | IoT namespace resources |
| monitor | [suite_app_backup_restore](../roles/suite_app_backup_restore.md) | Monitor namespace resources |

!!! tip
    If you only want to back up a certain of above components, you should run a single role instead of using this playbook. Please refer to the corresponding role for details.

Below environment variables are required for this playbook:

- `MAS_INSTANCE_ID`: This playbook only supports backing up components belong to a specific MAS instance at a time. If you have multiple MAS instances in the cluster to be backed up, you need to run this playbook multiple times with different value of this environment variable.

- `MAS_WORKSPACE_ID`: This playbook only supports backing up components belong to a specific MAS workspace at a time. If you have multiple MAS workspaces in the cluster to be backed up, you need to run this playbook multiple times with different value of this environment variable.

- `DB2_INSTANCE_NAME`: This playbook will back up the the Db2 instance used by IoT and Monitor, you need to set the correct Db2 instance name for this environment variable.

Please refer to the [example](#example) on how to use this playbook.


Backing up Optimizer
-------------------------------------------------------------------------------
This playbook `ibm.mas_devops.backup_optimizer` will back up the following components that Optimizer depends on in order:

| Component | Role | Data included |
| --------- | ----- | ----- |
| mongodb | [mongodb](../roles/mongodb.md) | MongoDB databases used by MAS Core and Optimizer |
| db2 | [db2](../roles/db2.md) | Db2 instance used by Manage |
| core | [suite_backup_restore](../roles/suite_backup_restore.md) | MAS Core namespace resources |
| manage | [suite_app_backup_restore](../roles/suite_app_backup_restore.md) | - Manage namespace resources <br>- Persistent volume data, such as attachments |
| optimizer | [suite_backup_restore](../roles/suite_backup_restore.md) | Optimizer namespace resources |

!!! tip
    If you only want to back up a certain of above components, you should run a single role instead of using this playbook. Please refer to the corresponding role for details.

Below environment variables are required for this playbook:

- `MAS_INSTANCE_ID`: This playbook only supports backing up components belong to a specific MAS instance at a time. If you have multiple MAS instances in the cluster to be backed up, you need to run this playbook multiple times with different value of this environment variable.

- `MAS_WORKSPACE_ID`: This playbook only supports backing up components belong to a specific MAS workspace at a time. If you have multiple MAS workspaces in the cluster to be backed up, you need to run this playbook multiple times with different value of this environment variable.

- `DB2_INSTANCE_NAME`: This playbook will back up the the Db2 instance used by Manage, you need to set the correct Db2 instance name for this environment variable.

Please refer to the [example](#example) on how to use this playbook.


Backing up Visual Inspection
-------------------------------------------------------------------------------
This playbook `ibm.mas_devops.backup_visualinspection` will back up the following components that Visual Inspection depends on in order:

| Component | Role | Data included |
| --------- | ----- | ----- |
| mongodb | [mongodb](../roles/mongodb.md) | MongoDB databases used by MAS Core and Visual Inspection |
| core | [suite_backup_restore](../roles/suite_backup_restore.md) | MAS Core namespace resources |
| visualinspection | [suite_app_backup_restore](../roles/suite_app_backup_restore.md) | - Visual Inspection namespace resources <br>- Persistent volume data, such as images and models |

!!! tip
    If you only want to back up a certain of above components, you should run a single role instead of using this playbook. Please refer to the corresponding role for details.

Below environment variables are required for this playbook:

- `MAS_INSTANCE_ID`: This playbook only supports backing up components belong to a specific MAS instance at a time. If you have multiple MAS instances in the cluster to be backed up, you need to run this playbook multiple times with different value of this environment variable.

- `MAS_WORKSPACE_ID`: This playbook only supports backing up components belong to a specific MAS workspace at a time. If you have multiple MAS workspaces in the cluster to be backed up, you need to run this playbook multiple times with different value of this environment variable.

Please refer to the [example](#example) on how to use this playbook.


Example
-------------------------------------------------------------------------------
!!! important
    Before you proceed with the following steps, please refer to [this doc](prepare-env.md) to prepare the testing environment.

All above playbooks support the [common environment variables](masbr-vars.md) to back up the MAS components in a similar way. In this example, we will use Manage to demonstrate how to:

- [Taking an on-demand full backup](#taking-a-full-backup)
- [Taking an on-demand incremental backup based on the latest full backup](#taking-an-incremental-backup)
- [Creating a scheduled backup job](#creating-a-scheduled-backup-job)

### Taking a full backup
Run below commands in the container to take a full backup:
```shell
$ export MAS_INSTANCE_ID=main
$ export MAS_WORKSPACE_ID=masdev
$ export DB2_INSTANCE_NAME=mas-main-masdev-manage

$ ansible-playbook ibm.mas_devops.backup_manage
```

The playbook will create a k8s Job in the OpenShift cluster to run the backup process, you can get the backup version and job link from the output:
```txt
TASK [Summary of backup job] ***************************************************************************************************************************************************************
ok: [localhost] =>
  msg:
  - Backup version ..................... 20240623062652
  - Backup from ........................ <none>
  - Job name ........................... backup-20240623062652-20240623062657
  - Job link ........................... https://console-openshift-console.apps.lubanbj5.cdl.ibm.com/k8s/ns/mas-main-manage/jobs/backup-20240623062652-20240623062657
```

Copy above job link and open it in the web browser to check the backup progress.

After the backup job is completed, you can login to the object storage web console to check the backed up files, or run below rclone commands in the container to have some checks:

- List the backup folders created by this backup job in the object storage:
```shell
$ export BACKUP_VERSION=20240623062652
$ rclone --config ${MASBR_STORAGE_CLOUD_RCLONE_FILE} lsd ${MASBR_STORAGE_CLOUD_RCLONE_NAME}:${MASBR_STORAGE_CLOUD_BUCKET}/backups | grep ${BACKUP_VERSION}
```

If the backup job is completed successfully, you will get the output similar to the following:
```text
           0 2000-01-01 00:00:00        -1 core-main-full-20240623062652-Completed
           0 2000-01-01 00:00:00        -1 db2-mas-main-masdev-manage-full-20240623062652-Completed
           0 2000-01-01 00:00:00        -1 manage-main-full-20240623062652-Completed
           0 2000-01-01 00:00:00        -1 mongodb-main-full-20240623062652-Completed
```

- Further check the files in a backup folder:
```shell
$ export FOLDER_NAME=db2-mas-main-masdev-manage-full-20240623062652-Completed
$ rclone --config ${MASBR_STORAGE_CLOUD_RCLONE_FILE} tree ${MASBR_STORAGE_CLOUD_RCLONE_NAME}:${MASBR_STORAGE_CLOUD_BUCKET}/backups/${FOLDER_NAME}
```

You will get the output similar to the following:
```text
/
├── backup.yml
├── database
│   └── db2-mas-main-masdev-manage-full-20240623062652.tar.gz
└── log
    ├── copy-20240623062652-20240623063515-db2-database-log.tar.gz
    ├── copy-20240623062652-20240623063820-db2-database-log.tar.gz
    ├── db2-backup-log.tar.gz
    └── db2-mas-main-masdev-manage-full-20240623062652-ansible-log.tar.gz

2 directories, 6 files
```

### Taking an incremental backup
!!! tip
    For more information about incremental backup, please refer to the doc for [MASBR_BACKUP_TYPE](vars.md#masbr_backup_type) and [MASBR_BACKUP_FROM_VERSION](vars.md#masbr_backup_from_version).

In the MAS CLI container, run below command to take an incremental backup based on the latest full backup:
```shell
$ export MASBR_BACKUP_TYPE=incr

$ export MAS_INSTANCE_ID=main
$ export MAS_WORKSPACE_ID=masdev
$ export DB2_INSTANCE_NAME=mas-main-masdev-manage

$ ansible-playbook ibm.mas_devops.backup_manage
```

The playbook will create a k8s Job in the OpenShift cluster, you can get the backup version and job link from the output:
```text
TASK [Summary of backup job] ***************************************************************************************************************************************************************
ok: [localhost] =>
  msg:
  - Backup version ..................... 20240623065309
  - Backup from ........................ manage-main-full-20240623062652
  - Job name ........................... backup-20240623065309-20240623065328
  - Job link ........................... https://console-openshift-console.apps.lubanbj5.cdl.ibm.com/k8s/ns/mas-main-manage/jobs/backup-20240623065309-20240623065328
```

The `Backup from` in the above outputs indicate which full backup this incremental backup is based on.

Copy above job link and open it in the web browser to check the backup progress. 

After the backup job is completed, you can login to the object storage web console to check the backed up files, or run below rclone commands in the container to have some checks:

- List the backup folders created by this backup job in the object storage:
```shell
$ export BACKUP_VERSION=20240623065309
$ rclone --config ${MASBR_STORAGE_CLOUD_RCLONE_FILE} lsd ${MASBR_STORAGE_CLOUD_RCLONE_NAME}:${MASBR_STORAGE_CLOUD_BUCKET}/backups | grep ${BACKUP_VERSION}
```

If the backup job is completed successfully, you will get the output similar to the following:
```
           0 2000-01-01 00:00:00        -1 core-main-incr-20240623065309-Completed
           0 2000-01-01 00:00:00        -1 db2-mas-main-masdev-manage-incr-20240623065309-Completed
           0 2000-01-01 00:00:00        -1 manage-main-incr-20240623065309-Completed
           0 2000-01-01 00:00:00        -1 mongodb-main-incr-20240623065309-Completed
```

- Further check the backup job details:
```shell
$ export FOLDER_NAME=db2-mas-main-masdev-manage-incr-20240623065309-Completed
$ rclone --config ${MASBR_STORAGE_CLOUD_RCLONE_FILE} cat ${MASBR_STORAGE_CLOUD_RCLONE_NAME}:${MASBR_STORAGE_CLOUD_BUCKET}/backups/${FOLDER_NAME}/backup.yml
```

You will get the output similar to the following:
```yaml
---
kind: Backup
name: "db2-mas-main-masdev-manage-incr-20240623065309"
version: "20240623065309"
type: "incr"
from: "db2-mas-main-masdev-manage-full-20240623062652"
source:
  domain: "lubanbj5.cdl.ibm.com"
  suite: ""
  instance: "main"
  workspace: "masdev"
component:
  name: "db2"
  instance: "mas-main-masdev-manage"
  namespace: "db2u"
data:
  - seq: "1"
    type: "database"
    phase: "Completed"
status:
  phase: "Completed"
  startTimestamp: "2024-06-23T06:56:21"
  completionTimestamp: "2024-06-23T07:01:46"
```

### Creating a scheduled backup job
!!! tip
    For more information about scheduled backup, please refer to the doc for [MASBR_BACKUP_SCHEDULE](vars.md#masbr_backup_schedule) and [MASBR_BACKUP_TIMEZONE](vars.md#masbr_backup_timezone).

In below example, we will create a scheduled backup job to run at 1:00 a.m. Monday through Friday:
```shell
$ export MASBR_BACKUP_SCHEDULE="0 1 * * 1-5"
$ export MASBR_BACKUP_TIMEZONE="Asia/Shanghai"

$ export MASBR_BACKUP_TYPE=incr

$ export MAS_INSTANCE_ID=main
$ export MAS_WORKSPACE_ID=masdev
$ export DB2_INSTANCE_NAME=mas-main-masdev-manage

$ ansible-playbook ibm.mas_devops.backup_manage
```

The playbook will create a k8s CronJob in the OpenShift cluster, you can get the backup version and job link from the output:
```text
TASK [Summary of backup job] ***************************************************************************************************************************************************************
ok: [localhost] =>
  msg:
  - Backup version ..................... 20240623071218
  - Backup from ........................ manage-main-full-20240623062652
  - Job name ........................... schedule-20240623071218-20240623071236
  - Job link ........................... https://console-openshift-console.apps.lubanbj5.cdl.ibm.com/k8s/ns/mas-main-manage/cronjobs/schedule-20240623071218-20240623071236
```

You can copy the above job link and open it in the web browser to check the CronJob running status.

If you want to change the schedule of this CronJob after it created, you can get necessary information from above output and run below command:
```shell
$ JOB_NAME=schedule-20240623071218-20240623071236
$ JOB_NAMESPACE=mas-main-manage
$ JOB_SCHEDULE="30 15 * * *"
$ oc patch CronJob ${JOB_NAME} -n ${JOB_NAMESPACE} -p "{\"spec\": {\"schedule\": \"${JOB_SCHEDULE}\"}}"
```

Reference 
-------------------------------------------------------------------------------

- [Backing up Maximo Application Suite](https://www.ibm.com/docs/en/mas-cd/continuous-delivery?topic=suite-backing-up-maximo-application)

