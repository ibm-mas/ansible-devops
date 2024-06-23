Environment Variables for MAS Backup and Restore
===============================================================================

| Envrionment variable | Required | Default value | Description |
| --- | --- | --- | --- |
| MASBR_CONFIRM_CLUSTER | No | false | Whether to confirm the currently connected cluster before run tasks |
| [MASBR_CREATE_TASK_JOB](#masbr_create_task_job) | No | true | Whether to run backup/restore process in k8s Job |
| [MASBR_COPY_TIMEOUT_SEC](#masbr_copy_timeout_sec) | No | 3600 | Copying file timeout in seconds |
| [MASBR_STORAGE_TYPE](masbr-storage.md#saving-backup-files) | Yes | | Type of storage system for saving the backup files |
| [MASBR_STORAGE_LOCAL_FOLDER](masbr-storage.md#use-local-folder) | Yes only if `MASBR_STORAGE_TYPE=local` | | Local path for saving backup files |
| [MASBR_STORAGE_CLOUD_RCLONE_FILE](masbr-storage.md#use-cloud-object-storage) | Yes only if `MASBR_STORAGE_TYPE=cloud` | | The path of rclone.conf file |
| [MASBR_STORAGE_CLOUD_RCLONE_NAME](masbr-storage.md#use-cloud-object-storage) | Yes only if `MASBR_STORAGE_TYPE=cloud` | | The config name defined in rclone.conf file |
| [MASBR_STORAGE_CLOUD_BUCKET](masbr-storage.md#use-cloud-object-storage) | Yes only if `MASBR_STORAGE_TYPE=cloud` | | Object storage bucket for saving backup files |
| MASBR_LOCAL_TEMP_FOLDER | No | "/tmp/masbr" | Local temp folder for backup/restore |
| [MASBR_BACKUP_TYPE](#masbr_backup_type) | No | "full" | Take a full backup or incremental backup |
| [MASBR_BACKUP_DATA](#masbr_backup_data) | No | | Data types to be backed up |
| [MASBR_BACKUP_FROM_VERSION](#masbr_backup_from_version) | No | | The version of the backup to create incremental backup based on |
| [MASBR_BACKUP_SCHEDULE](#masbr_backup_schedule) | No | | Cron expression for running scheduled backup job |
| [MASBR_BACKUP_TIMEZONE](#masbr_backup_timezone) | No | | Time zone for scheduled backup |
| [MASBR_RESTORE_FROM_VERSION](#masbr_restore_from_version) | Yes only for restore job | | The version of the backup to be restored from |
| [MASBR_RESTORE_DATA](#masbr_restore_data) | No | | Data types to be restored |
| MASBR_MASCLI_IMAGE_TAG | No | "latest" | MAS CLI docker image tag |
| MASBR_MASCLI_IMAGE_PULL_POLICY | No | | MAS CLI docker [image pull policy](https://kubernetes.io/docs/concepts/containers/images/#imagepullpolicy-defaulting) |
| MASBR_RCLONE_IMAGE_TAG | No | "1.67.0" | Rclone docker image tag |
| MASBR_RCLONE_IMAGE_PULL_POLICY | No | | Rclone docker [image pull policy](https://kubernetes.io/docs/concepts/containers/images/#imagepullpolicy-defaulting) |
| MASBR_SLACK_ENABLED | No | false | Whether to send Slack notifications |
| [MASBR_SLACK_LEVEL](#masbr_slack_level) | No | "info" | Slack notification level |
| MASBR_SLACK_TOKEN | Yes only if `MASBR_SLACK_ENABLED=true` | | Slack integration token |
| MASBR_SLACK_CHANNEL | Yes only if `MASBR_SLACK_ENABLED=true` | | Channel to send the message to |
| MASBR_SLACK_USER | No | "MASBR" | Sender of the message. |


Job management
-------------------------------------------------------------------------------

###### MASBR_CREATE_TASK_JOB
When the playbook/role starts running in the terminal, it will first perform some checks, such as checking the required environment variables, get the soruce cluster information, etc. Then, depending on the value of environment variable `MASBR_CREATE_TASK_JOB` you specified, the remaining backup/restore process can be ran in different ways:

- `MASBR_CREATE_TASK_JOB=false`: continue to run bakcup/restore process in your current terminal, and you can view the terminal output to get the progress of the backup/restore. This is usually used for developing and debugging playbooks and roles on your local workstation.
- `MASBR_CREATE_TASK_JOB=true`: this is the default behavior, the playbook/role will create a new k8s Job to run the actual backup/restore process in the cluster and stop the current running process in the terminal, then you can check the log of the created k8s Job in the cluster to monitor the backup/restore progress.

###### MASBR_COPY_TIMEOUT_SEC
During the backup/restore process, the playbook/role will copy backup files between different data stores and specified backup storage systems. Set a suitable value for this environment variable to avoid the playbook/role entering a waiting state due to some errors, such as the specified storage system network speed is too slow or cannot be connected.

!!! warning
    Must set a suitable value based on the size of the backup/restore data and the network status, should to avoid the copying data process being interrupted due to this value be set too small.


Backup
-------------------------------------------------------------------------------

###### MASBR_BACKUP_TYPE
If you set environment variable `MASBR_BACKUP_TYPE=full` or do not specify a value for this variable, the playbook/role will take a full backup. You can set environment variable `MASBR_BACKUP_TYPE=incr` to indicate the playbook/role to take an incremental backup. 

Only below type of data support taking an incremental backup:

- `database`: MongoDB databases, Db2 instance
- `pv`: Persistent volume data

The playbook/role will always take a full backup for other type of data regardless of whether this variable is set to `incr`. 

###### MASBR_BACKUP_DATA
!!! important
    This environment variable is only valid for backing up a component by running a single role. Please do not set this variable when running a playbook to back up multiple components at once.

A backup role will perform the backup tasks for all types of data used by a component by default. For example, when we using `suite_app_backup_restore` to back up Manage, it will back up the following data in order:

- Manage namespace resources
- Persistent volume data used by Manage

If you only want to backup certain types of data, you can set this environment variable. The value of this environment variable is the data types separated by commas. For example, 

- `MASBR_BACKUP_DATA=namespace,pv`: this will indicate the role to backup `namespace` and `pv` data
- `MASBR_BACKUP_DATA=pv`: this will indicate the role to only backup `pv` data

The data types supported by each backup role are defined in the role document, please refer to corresponding role document for more details. 

###### MASBR_BACKUP_FROM_VERSION
This environment variable is only valid if `MASBR_BACKUP_TYPE=incr`, it indicate which backup version that the incremental backup to based on. 

!!! tip
    If you do not set a value for this variable, then the playbook/role will find and take an incremental backup based on the latest Completed Full backup from the specified storage location.

The backup files you specified by `MASBR_BACKUP_FROM_VERSION` should be a Full backup.

The component name and data types in the backup file which specified by `MASBR_BACKUP_FROM_VERSION` should be same as the ones in the current incremental backup job. 

###### MASBR_BACKUP_SCHEDULE
In addition to create an on-demand backup job, you can also set environment variable `MASBR_BACKUP_SCHEDULE` to indicate the playbook/role to create a k8s CronJob to run the backup process periodically.

The value of `MASBR_BACKUP_SCHEDULE` is a Cron expression:

```
 ┌───────────── minute (0–59)
 │ ┌───────────── hour (0–23)
 │ │ ┌───────────── day of the month (1–31)
 │ │ │ ┌───────────── month (1–12)
 │ │ │ │ ┌───────────── day of the week (0–6) (Sunday to Saturday;
 │ │ │ │ │                                   7 is also Sunday on some systems)
 │ │ │ │ │
 │ │ │ │ │
 * * * * *
```

For example, set below value to create a scheduled backup job that will run at 1:00 a.m. from Monday to Friday:  
`MASBR_BACKUP_SCHEDULE="0 1 * * 1-5"`

Please refer to [this doc](https://en.wikipedia.org/wiki/Cron) for more details about the Cron expression.

###### MASBR_BACKUP_TIMEZONE
By default, the k8s CronJob use UTC time zone, so maybe you want to set the Cron expression based on your local time zone. You can set the environment variable `MASBR_BACKUP_TIMEZONE` for this.

For a full list of available time zone, you can refer to [this doc](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).


Restore
-------------------------------------------------------------------------------

###### MASBR_RESTORE_FROM_VERSION
You must specify the environment variable `MASBR_RESTORE_FROM_VERSION` to indicate the playbook/role to restore from which version of the backup files. 

The playbook/role will first try to find all the backup folders which has the same backup version you specified by `MASBR_RESTORE_FROM_VERSION` on the specified backup storage location. For each found backup folder, the playbook/role will get the backup information from the backup folder and determine whether it is trying to restore from an incremental backup or not. If so, the playbook/role will retrieve and restore the corresponding full backup first and then continue to restore the incremental backup.

For example, we are going to restore MAS Core from an incremental backup with the version `20240622040201`. Because when you run playbook to back up MAS Core, it will back up the MongoDB and MAS Core namespace resources in order. So there should be two backup folders that have the same backup version `20240622040201` on the spedified backup storage:
```
           0 2000-01-01 00:00:00        -1 mongodb-main-incr-20240622040201-Completed
           0 2000-01-01 00:00:00        -1 core-main-incr-20240622040201-Completed
```

After we set `MASBR_RESTORE_FROM_VERSION=20240622040201` and run the playbook `ibm.mas_devops.restore_core` to restore MAS Core from this incremental backup version, the playbook will first find the backup folder `mongodb-main-incr-20240622040201-Completed`, and get the `backup.yml` file in it:
```
kind: Backup
name: "mongodb-main-incr-20240622040201"
version: "20240622040201"
type: "incr"
from: "mongodb-main-full-20240621122530"
source:
  domain: "lubanbj5.cdl.ibm.com"
  suite: ""
  instance: "main"
  workspace: ""
component:
  name: "mongodb"
  instance: "main"
  app: "core"
  namespace: "mongoce"
  provider: "community"
  version: "5.0.23"
data:
  - seq: "1"
    type: "database"
    phase: "Completed"
status:
  phase: "Completed"
  startTimestamp: "2024-06-22T04:03:30"
  completionTimestamp: "2024-06-22T04:04:48"
  sentNotifications:
    - type: "Slack"
      channel: "#ansible-slack-dev"
      timestamp: "2024-06-22T04:03:43"
      phase: "InProgress"
    - type: "Slack"
      channel: "#ansible-slack-dev"
      timestamp: "2024-06-22T04:04:50"
      phase: "Completed"
```

In the above `backup.yml` file, it has a field `from: "mongodb-main-full-20240621122530"` that indicate this incremental backup is based on the full backup `mongodb-main-full-20240621122530`. So the playbook will first try to find this full backup from the specified backup storage and restore it. After the playbook restored this full backup successfully, it will continue to restore the current incremental backup `mongodb-main-incr-20240622040201`.

Next, the playbook will perform similar steps as above to restore MAS Core namespace resources from the full backup folder `core-main-full-20240621122530-Completed` and the incremental backup folder `core-main-incr-20240622040201-Completed`


###### MASBR_RESTORE_DATA
!!! important
    This environment variable is only valid for restoring a component by running a single role. Please do not set this variable when running a playbook to restore multiple components at once.

A restore role will perform the restore tasks for all types of data used by a component by default. For example, when we using `suite_app_backup_restore` to restore Manage, it will restore the following data in order:

- Manage namespace resources
- Persistent volume data used by Manage

If you only want to restore certain types of data, you can set this environment variable. The value of this environment variable is the data types separated by commas. For example, 

- `MASBR_RESTORE_DATA=namespace,pv`: this will indicate the role to restore `namespace` and `pv` data
- `MASBR_RESTORE_DATA=pv`: this will indicate the role to only restore `pv` data

The data types supported by each restore role are defined in the role document, please refer to corresponding role document for more details. 


Slack notification
-------------------------------------------------------------------------------

###### MASBR_SLACK_LEVEL
Supported notification levels:

- `info`: send notifications when job in the phase `InProgress`, `Completed`, `Failed`, `PartiallyFailed`
- `failure`: sent notifications only when job in the phase `Failed`, `PartiallyFailed`
