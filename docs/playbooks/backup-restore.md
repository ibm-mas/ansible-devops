Backup and Restore
===============================================================================

Overview
-------------------------------------------------------------------------------
MAS Devops Collection includes playbooks for backing up and restoring of the following MAS components and their dependencies:

- [MongoDB](#backuprestore-for-mongodb)
- [Db2](#backuprestore-for-db2)
- [MAS Core](#backuprestore-for-mas-core)
- [Manage](#backuprestore-for-manage)
- [IoT](#backuprestore-for-iot)
- [Monitor](#backuprestore-for-monitor)
- [Health](#backuprestore-for-health)
- [Optimizer](#backuprestore-for-optimizer)
- [Visual Inspection](#backuprestore-for-visual-inspection)


Creation of both **full** and **incremental** backups are supported. Backup and restore actions can be executed locally, or by generating **on-demand** or **scheduled** jobs that will allow the work to be performed on your OpenShift cluster using the [MAS CLI container image](https://github.ibm.com/ibm-mas/cli).

!!! tip
    The backup and restore Ansible roles can also be used individually, allowing you to build your own customized backup and restore playbook covering exactly what you need. For example, you can only [backup/restore Manage attachments](../roles/suite_app_backup_restore.md).


For more information about backup and restore for Maximo Application Suite, please refer to [Backing up and restoring Maximo Application Suite](https://www.ibm.com/docs/en/mas-cd/continuous-delivery?topic=administering-backing-up-restoring-maximo-application-suite) in the product documentation.


Configuration
-------------------------------------------------------------------------------

### Storage

| Envrionment variable                 | Required (Default Value)               | Description |
| ------------------------------------ | -------------------------------------- | ----------- |
| MASBR_STORAGE_TYPE                   | **Yes**                                | Type of storage system for saving the backup files |
| MASBR_STORAGE_LOCAL_FOLDER           | **Yes**, if `MASBR_STORAGE_TYPE=local` | The local path to save the backup files |
| MASBR_STORAGE_CLOUD_RCLONE_FILE      | **Yes**, if `MASBR_STORAGE_TYPE=cloud` | The path of `rclone.conf` file |
| MASBR_STORAGE_CLOUD_RCLONE_NAME      | **Yes** if `MASBR_STORAGE_TYPE=cloud`  | The configuration name defined in `rclone.conf` file |
| MASBR_STORAGE_CLOUD_BUCKET           | **Yes**, if `MASBR_STORAGE_TYPE=cloud` | Object storage bucket for saving backup files |
| MASBR_LOCAL_TEMP_FOLDER              | No (`/tmp/masbr`)                      | Local folder for saving the temporary backup/restore data, the data in this folder will be deleted after the backup/restore job completed. |

You need to set the environment variable `MASBR_STORAGE_TYPE` before you perform a backup or restore job. This variable indicates what type of storage systems that you are using for saving the backup files. Currently, it supports below types:

- `local`: use the local file system, e.g. a folder on your laptop or workstation.
- `cloud`: use the cloud object storage, such as IBM Cloud Object Storage, AWS S3, etc.

###### Use Local Folder

You can save the backup files to a folder on your local file system by setting the following environment variables: 
```
MASBR_STORAGE_TYPE=local
MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
```
- `MASBR_STORAGE_LOCAL_FOLDER`: the path for saving the backup files

######  Use Cloud Object Storage

The backup playbooks use [Rclone](https://rclone.org/) to copy backup files from data stores to cloud object storage. It requires a Rclone configuration file which you can either create it manually, or you can install the Rclone tool and create the configuration file by running the `rclone config` command. For more information about the rclone config command and configuration file format, please refer to the [Rclone documentation](https://rclone.org/s3/#configuration). 

Below is a sample Rclone configuration file that using MinIO object storage:
```
[masbr]
type = s3
provider = Minio
endpoint = http://minio-api.apps.mydomain.com
access_key_id = Qfx9YGnykJapxL7pzUyA
secret_access_key = qKRGSnxsJ7z6pIA74sVxJ6fkEh4Fq5m4fo0inDuJ
region = minio
```

Set the following environment variables to indicate the playbooks to use cloud object storage for saving backup files:
```
MASBR_STORAGE_TYPE=cloud
MASBR_STORAGE_CLOUD_RCLONE_FILE=/mnt/configmap/rclone.conf
MASBR_STORAGE_CLOUD_RCLONE_NAME=masbr
MASBR_STORAGE_CLOUD_BUCKET=mas-backup
```

- `MASBR_STORAGE_CLOUD_RCLONE_FILE`: the path where your rclone.conf file is located
- `MASBR_STORAGE_CLOUD_RCLONE_NAME`: the Rclone configuration name (`[masbr]` from above sample) defined in the rclone.conf file
- `MASBR_STORAGE_CLOUD_BUCKET`: the bucket name you created on the object storage for saving the backup files


### Kubernetes Jobs
| Envrionment variable                 | Required (Default Value) | Description |
| ------------------------------------ | ------------------------ | ----------- |
| MASBR_CONFIRM_CLUSTER                | No (`false`)             | Set `true` or `false` to indicate the playbook whether to confirm the currently connected cluster before running the backup or restore job |
| MASBR_CREATE_TASK_JOB                | No (`true`)              | Whether to run backup/restore process in kubernetes Job |
| MASBR_COPY_TIMEOUT_SEC               | No (`43200`)             | The transfer files timeout in seconds, default timeout value is 12 hours. |
| MASBR_JOB_TIMEZONE                   | No                       | The [time zone](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) for creating scheduled job. If not set a value for this variable, this role will use UTC time zone when creating a CronJob for running scheduled job. |
| MASBR_CLEANUP_SCHEDULE               | No (`0 1 * * *`)         | Cron expression of cleanup Job (default to run at 1:00 every day) |
| MASBR_CLEANUP_TTL_SEC                | No (`604800`)            | All completed jobs that exceed this TTL(time-to-live) in seconds will be deleted (default TTL is 1 week: 3600 * 24 * 7) |
| MASBR_MASCLI_IMAGE_TAG               | No (`latest`)            | MAS CLI docker image tag |
| MASBR_MASCLI_IMAGE_PULL_POLICY       | No                       | MAS CLI docker [image pull policy](https://kubernetes.io/docs/concepts/containers/images/#imagepullpolicy-defaulting) |

When the playbook starts running, it will first perform some checks, such as checking the required environment variables, get the source or target cluster information, etc. Then, depending on the value of `MASBR_CREATE_TASK_JOB`, the remaining backup/restore process can be ran in different ways:

- `MASBR_CREATE_TASK_JOB=false`, run backup/restore process in your current terminal, and you can view the terminal output to get the progress of the backup/restore.
- `MASBR_CREATE_TASK_JOB=true`, a new kubernetes Job will be created to run the backup/restore process in the cluster, then you can check the log of the created kubernetes Job in the cluster to monitor the backup/restore progress. 

The environment variable `MASBR_CREATE_TASK_JOB` is only valid when using cloud object storage (`MASBR_STORAGE_TYPE=cloud`). The playbooks will always run backup/restore process in your local terminal when using local storage system (`MASBR_STORAGE_TYPE=local`).

During the backup/restore process, the playbook will copy backup files between different data stores and specified backup storage systems. Set a suitable value for the environment variable `MASBR_COPY_TIMEOUT_SEC` to avoid the playbook entering a waiting state due to some errors, such as the specified storage system network speed is too slow or cannot be connected.

!!! warning
    Set a suitable value for `MASBR_COPY_TIMEOUT_SEC` based on the estimated size of the backup/restore data and the network conditions, setting it too low can result in the data copying process being interrupted.

The playbook will create an additional CronJob `masbr-cleanup` for each namespace that has backup/restore jobs created. This cleanup CronJob will periodically delete the completed jobs that exceed a certain priod of time which specified by `MASBR_CLEANUP_TTL_SEC`. You can also specify when to run the cleanup CronJob by setting Cron expression for `MASBR_CLEANUP_SCHEDULE`. 


### Backups
| Envrionment variable                 | Required (Default Value) | Description |
| ------------------------------------ | ------------------------ | ----------- |
| MASBR_ACTION                         | **Yes**                  | Whether to run the playbook to perform a `backup` or a `restore` |
| MASBR_BACKUP_TYPE                    | No (`full`)              | Set `full` or `incr` to indicate the playbook to create a **full** backup or **incremental** backup. |
| MASBR_BACKUP_FROM_VERSION            | No                       | Set the full backup version to use in the incremental backup, this will be in the format of a `YYYMMDDHHMMSS` timestamp (e.g. `20240621021316`). |
| MASBR_BACKUP_SCHEDULE                | No                       | Set [Cron expression](ttps://en.wikipedia.org/wiki/Cron) to create a scheduled backup. If not set a value for this varialbe, the playbook will create an on-demand backup. |

The playbooks are switched to backup mode by setting `MASBR_ACTION` to `backup`.

###### Full Backups
If you set environment variable `MASBR_BACKUP_TYPE=full` or do not specify a value for this variable, the playbook will take a full backup. 

###### Incremental Backups
You can set environment variable `MASBR_BACKUP_TYPE=incr` to indicate the playbook to take an incremental backup. 

!!! important
    Only supports creating incremental backup for MonogDB, Db2 and persistent volume data. The playbook will always create a full backup for other type of data regardless of whether this variable be set to `incr`.

The environment variable `MASBR_BACKUP_FROM_VERSION` is only valid if `MASBR_BACKUP_TYPE=incr`. It indicates which backup version that the incremental backup to based on. If you do not set a value for this variable, the playbook will try to find the latest Completed Full backup from the specified storage location, and then take an incremental backup based on it.

!!! important
    The backup files you specified by `MASBR_BACKUP_FROM_VERSION` must be a Full backup. And the component name and data types in the specified Full backup file must be same as the current incremental backup job.

###### Scheduled Backups
In addition to create an on-demand backup job, you can also set environment variable `MASBR_BACKUP_SCHEDULE` to indicate the playbook to create a kubernetes CronJob to run the backup process periodically.

The value of `MASBR_BACKUP_SCHEDULE` is a [Cron expression](https://en.wikipedia.org/wiki/Cron):

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

By default, the kubernetes CronJob use UTC time zone, so maybe you want to set environment variable `MASBR_JOB_TIMEZONE` with the Cron expression based on your local [time zone](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)


### Restore
| Envrionment variable                 | Required (Default Value) | Description |
| ------------------------------------ | ------------------------ | ----------- |
| MASBR_ACTION                         | **Yes**                  | Whether to run the playbook to perform a `backup` or a `restore` |
| MASBR_RESTORE_FROM_VERSION           | **Yes**                  | Set the backup version to use in the restore, this will be in the format of a `YYYMMDDHHMMSS` timestamp (e.g. `20240621021316`) |

The playbooks are switched to restore mode by setting `MASBR_ACTION` to `restore`. You **must** specify the `MASBR_RESTORE_FROM_VERSION` environment variable to indicate which version of the backup files to use.

In the case of restoring from an incremental backup, the corresponding full backup will be restored first before continuing to restore the incremental backup.


### Slack Notifications
| Envrionment variable                 | Required (Default Value)           | Description |
| ------------------------------------ | ---------------------------------- | ----------- |
| MASBR_SLACK_ENABLED                  | No (`false`)                       | Set `true` or `false` to indicate whether the playbook will send Slack notification messages of the backup and restore progress |
| MASBR_SLACK_LEVEL                    | No (`info`)                        | Set `failure`, `info` or `verbose` to indicate the playbook to send Slack notification messages in which backup and resore phases            |
| MASBR_SLACK_TOKEN                    | Yes, if `MASBR_SLACK_ENABLED=true` | Slack integration token             |
| MASBR_SLACK_CHANNEL                  | Yes, if `MASBR_SLACK_ENABLED=true` | Channel to send the message to      |
| MASBR_SLACK_USER                     | No (`MASBR`)                       | Sender of the message               |

Integration with Slack is supported with below notification levels:

- `verbose`: send notifications when job in the phase `InProgress`, `Completed`, `Failed` or `PartiallyFailed`.
- `info`: send notifications when job in the phase `Completed`, `Failed` or `PartiallyFailed`.
- `failure`: send notifications only when job in the phase `Failed` or `PartiallyFailed`


Backup/Restore for MongoDB
-------------------------------------------------------------------------------
This playbook `ibm.mas_devops.br_mongodb` will invoke the role [mongodb](../roles/mongodb.md) to backup/restore the MongoDB databases.

This playbook supports backing up and restoring databases for an in-cluster MongoDB CE instance. If you are using other MongoDB venders, such as IBM Cloud Databases for MongoDB, Amazon DocumentDB or MongoDB Altas Database, please refer to the corresponding vender's documentation for more information about their provided backup/restore service.

### Environment Variables

- `MAS_INSTANCE_ID`: **Required**. This playbook supports backup/restore MongoDB databases that belong to a specific MAS instance, call the playbook multiple times with different values for `MAS_INSTANCE_ID` if you wish to back up multiple MAS instances that use the same MongoDB CE instance.
- `MAS_APP_ID`: **Optional**. By default, this playbook will backup all databases belonging to the specified MAS instance. You can backup the databases only belong to a specific MAS application by setting this environment variable to a supported MAS application id `core`, `manage`, `iot`, `monitor`, `health`, `optimizer` or `visualinspection`.

### Examples
```bash
# Full backup all MongoDB data for the dev1 instance
export MASBR_ACTION=backup
export MASBR_STORAGE_TYPE=local
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MAS_INSTANCE_ID=dev1
ansible-playbook ibm.mas_devops.br_mongodb

# Incremental backup all MongoDB data for the dev1 instance
export MASBR_ACTION=backup
export MASBR_BACKUP_TYPE=incr
export MASBR_STORAGE_TYPE=local
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MAS_INSTANCE_ID=dev1
ansible-playbook ibm.mas_devops.br_mongodb

# Create a scheduled backup Job for the dev1 instance
export MASBR_ACTION=backup
export MASBR_BACKUP_SCHEDULE="50 0 * * *"
export MASBR_JOB_TIMEZONE="Asia/Shanghai"
export MASBR_STORAGE_TYPE=local
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MAS_INSTANCE_ID=dev1
ansible-playbook ibm.mas_devops.br_mongodb

# Restore all MongoDB data for the dev1 instance
export MASBR_ACTION=restore
export MASBR_STORAGE_TYPE=local
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MASBR_RESTORE_FROM_VERSION=20240630132439
export MAS_INSTANCE_ID=dev1
ansible-playbook ibm.mas_devops.br_mongodb

# Backup just the IoT MongoDB data for the dev2 instance
export MASBR_ACTION=backup
export MASBR_STORAGE_TYPE=local
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MAS_INSTANCE_ID=dev2
export MAS_APP_ID=iot
ansible-playbook ibm.mas_devops.br_mongodb
```


Backup/Restore for Db2
-------------------------------------------------------------------------------
This playbook `ibm.mas_devops.br_db2` will invoke the role [db2](../roles/db2.md) to backup/restore Db2 instance.

### Environment Variables

- `DB2_INSTANCE_NAME`: **Required**. This playbook only supports backing up specific Db2 instance at a time. If you want to backup all Db2 instances in the Db2 cluster, you need to run this playbook multiple times with different value of this environment variable.

### Examples
```bash
# Full backup for the db2w-shared Db2 instance
export MASBR_ACTION=backup
export MASBR_STORAGE_TYPE=local
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export DB2_INSTANCE_NAME=db2w-shared
ansible-playbook ibm.mas_devops.br_db2

# Incremental backup for the db2w-shared Db2 instance
export MASBR_ACTION=backup
export MASBR_BACKUP_TYPE=incr
export MASBR_STORAGE_TYPE=local
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export DB2_INSTANCE_NAME=db2w-shared
ansible-playbook ibm.mas_devops.br_db2

# Create a scheduled backup Job for the db2w-shared Db2 instance
export MASBR_ACTION=backup
export MASBR_BACKUP_SCHEDULE="50 0 * * *"
export MASBR_JOB_TIMEZONE="Asia/Shanghai"
export MASBR_STORAGE_TYPE=local
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export DB2_INSTANCE_NAME=db2w-shared
ansible-playbook ibm.mas_devops.br_db2

# Restore for the db2w-shared Db2 instance
export MASBR_ACTION=restore
export MASBR_STORAGE_TYPE=local
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MASBR_RESTORE_FROM_VERSION=20240630132439
export DB2_INSTANCE_NAME=db2w-shared
ansible-playbook ibm.mas_devops.br_db2
```

Backup/Restore for MAS Core
-------------------------------------------------------------------------------
This playbook `ibm.mas_devops.br_core` will backup the following components that MAS Core depends on in order:

| Component | Ansible Role                                             | Data included                      |
| --------- | -------------------------------------------------------- | ---------------------------------- |
| mongodb   | [mongodb](../roles/mongodb.md)                           | MongoDB databases used by MAS Core |
| core      | [suite_backup_restore](../roles/suite_backup_restore.md) | MAS Core namespace resources       |


### Environment Variables

- `MAS_INSTANCE_ID` **Required**. The MAS instance ID to perform a backup for.

### Examples
```bash
# Full backup all core data for the dev1 instance
export MASBR_ACTION=backup
export MASBR_STORAGE_TYPE=local
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MAS_INSTANCE_ID=dev1
ansible-playbook ibm.mas_devops.br_core

# Incremental backup all core data for the dev1 instance
export MASBR_ACTION=backup
export MASBR_BACKUP_TYPE=incr
export MASBR_STORAGE_TYPE=local
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MAS_INSTANCE_ID=dev1
ansible-playbook ibm.mas_devops.br_core

# Create a scheduled backup Job for the dev1 instance
export MASBR_ACTION=backup
export MASBR_BACKUP_SCHEDULE="50 0 * * *"
export MASBR_JOB_TIMEZONE="Asia/Shanghai"
export MASBR_STORAGE_TYPE=local
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MAS_INSTANCE_ID=dev1
ansible-playbook ibm.mas_devops.br_core

# Restore all core data for the dev1 instance
export MASBR_ACTION=restore
export MASBR_STORAGE_TYPE=local
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MASBR_RESTORE_FROM_VERSION=20240630132439
export MAS_INSTANCE_ID=dev1
ansible-playbook ibm.mas_devops.br_core
```


Backup/Restore for Manage
-------------------------------------------------------------------------------
This playbook `ibm.mas_devops.br_manage` will backup the following components that Manage depends on in order:

| Component | Role                                                             | Data included                                                                  |
| --------- | ---------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| mongodb   | [mongodb](../roles/mongodb.md)                                   | MongoDB databases used by MAS Core                                             |
| db2       | [db2](../roles/db2.md)                                           | Db2 instance used by Manage                                                    |
| core      | [suite_backup_restore](../roles/suite_backup_restore.md)         | MAS Core namespace resources                                                   |
| manage    | [suite_app_backup_restore](../roles/suite_app_backup_restore.md) | Manage namespace resources <br>Persistent volume data, such as attachments     |


### Environment Variables

- `MAS_INSTANCE_ID` **Required**. This playbook only supports backing up components belong to a specific MAS instance at a time. If you have multiple MAS instances in the cluster to be backed up, you need to run this playbook multiple times with different value of this environment variable.
- `MAS_WORKSPACE_ID` **Required**. This playbook only supports backing up components belong to a specific MAS workspace at a time. If you have multiple MAS workspaces in the cluster to be backed up, you need to run this playbook multiple times with different value of this environment variable.
- `DB2_INSTANCE_NAME` **Optional**. When defined, this playbook will backup the Db2 instance used by Manage. DB2 role is skipped when environment variable is not defined..

### Examples

```bash
# Full backup all manage data for the dev1 instance and ws1 workspace
export MASBR_ACTION=backup
export MASBR_STORAGE_TYPE=local
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MAS_INSTANCE_ID=dev1
export MAS_WORKSPACE_ID=ws1
export DB2_INSTANCE_NAME=mas-dev1-ws1-manage # set this to execute db2 backup role
ansible-playbook ibm.mas_devops.br_manage

# Incremental backup all manage data for the dev1 instance and ws1 workspace
export MASBR_ACTION=backup
export MASBR_BACKUP_TYPE=incr
export MASBR_STORAGE_TYPE=local
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MAS_INSTANCE_ID=dev1
export MAS_WORKSPACE_ID=ws1
export DB2_INSTANCE_NAME=mas-dev1-ws1-manage # set this to execute db2 backup role
ansible-playbook ibm.mas_devops.br_manage

# Restore all manage data for the dev1 instance and ws1 workspace
export MASBR_ACTION=restore
export MASBR_STORAGE_TYPE=local
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MASBR_RESTORE_FROM_VERSION=20240630132439
export MAS_INSTANCE_ID=dev1
export MAS_WORKSPACE_ID=ws1
export DB2_INSTANCE_NAME=mas-dev1-ws1-manage # set this to execute db2 restore role
ansible-playbook ibm.mas_devops.br_manage

# Create a scheduled backup of all manage data for the dev1 instance and ws1 workspace
# This will run at 01:00, Monday through Friday
export MASBR_ACTION=backup
export MASBR_BACKUP_TYPE=incr
export MASBR_BACKUP_SCHEDULE="0 1 * * 1-5"
export MASBR_JOB_TIMEZONE="Asia/Shanghai"
export MASBR_STORAGE_TYPE=local
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MAS_INSTANCE_ID=dev1
export MAS_WORKSPACE_ID=ws1
export DB2_INSTANCE_NAME=mas-dev1-ws1-manage # set this to execute db2 backup role
ansible-playbook ibm.mas_devops.br_manage
```


Backup/Restore for IoT
-------------------------------------------------------------------------------
This playbook `ibm.mas_devops.br_iot` will backup the following components that IoT depends on in order:

| Component | Ansible Role                                                     | Data included                              |
| --------- | ---------------------------------------------------------------- | ------------------------------------------ |
| mongodb   | [mongodb](../roles/mongodb.md)                                   | MongoDB databases used by MAS Core and IoT |
| db2       | [db2](../roles/db2.md)                                           | Db2 instance used by IoT                   |
| core      | [suite_backup_restore](../roles/suite_backup_restore.md)         | MAS Core namespace resources               |
| iot       | [suite_app_backup_restore](../roles/suite_app_backup_restore.md) | IoT namespace resources                    |

### Environment Variables

- `MAS_INSTANCE_ID` **Required**. This playbook only supports backing up components belong to a specific MAS instance at a time. If you have multiple MAS instances in the cluster to be backed up, you need to run this playbook multiple times with different value of this environment variable.
- `MAS_WORKSPACE_ID` **Required**. This playbook only supports backing up components belong to a specific MAS workspace at a time. If you have multiple MAS workspaces in the cluster to be backed up, you need to run this playbook multiple times with different value of this environment variable.
- `DB2_INSTANCE_NAME` **Required**. This playbook will backup the the Db2 instance used by IoT, you need to set the correct Db2 instance name for this environment variable.

### Examples

```bash
# Full backup all iot data for the dev1 instance
export MASBR_ACTION=backup
export MASBR_STORAGE_TYPE=local
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MAS_INSTANCE_ID=dev1
export MAS_WORKSPACE_ID=ws1
export DB2_INSTANCE_NAME=db2w-shared
ansible-playbook ibm.mas_devops.br_iot

# Incremental backup all iot data for the dev1 instance
export MASBR_ACTION=backup
export MASBR_BACKUP_TYPE=incr
export MASBR_STORAGE_TYPE=local
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MAS_INSTANCE_ID=dev1
export MAS_WORKSPACE_ID=ws1
export DB2_INSTANCE_NAME=db2w-shared
ansible-playbook ibm.mas_devops.br_iot

# Restore all iot data for the dev1 instance
export MASBR_ACTION=restore
export MASBR_STORAGE_TYPE=local
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MASBR_RESTORE_FROM_VERSION=20240630132439
export MAS_INSTANCE_ID=dev1
export MAS_WORKSPACE_ID=ws1
export DB2_INSTANCE_NAME=db2w-shared
ansible-playbook ibm.mas_devops.br_iot

# Create a scheduled backup of all iot data for the dev1 instance
# This will run at 01:00, Monday through Friday
export MASBR_ACTION=backup
export MASBR_BACKUP_TYPE=incr
export MASBR_BACKUP_SCHEDULE="0 1 * * 1-5"
export MASBR_JOB_TIMEZONE="Asia/Shanghai"
export MASBR_STORAGE_TYPE=local
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MAS_INSTANCE_ID=dev1
export MAS_WORKSPACE_ID=ws1
export DB2_INSTANCE_NAME=db2w-shared
ansible-playbook ibm.mas_devops.br_iot
```


Backup/Restore for Monitor
-------------------------------------------------------------------------------
This playbook `ibm.mas_devops.br_monitor` will backup the following components that Monitor depends on in order:

| Component | Ansible Role                                                     | Data included                                       |
| --------- | ---------------------------------------------------------------- | --------------------------------------------------- |
| mongodb   | [mongodb](../roles/mongodb.md)                                   | MongoDB databases used by MAS Core, IoT and Monitor |
| db2       | [db2](../roles/db2.md)                                           | Db2 instance used by IoT and Monitor                |
| core      | [suite_backup_restore](../roles/suite_backup_restore.md)         | MAS Core namespace resources                        |
| iot       | [suite_app_backup_restore](../roles/suite_app_backup_restore.md) | IoT namespace resources                             |
| monitor   | [suite_app_backup_restore](../roles/suite_app_backup_restore.md) | Monitor namespace resources                         |


### Environment Variables

- `MAS_INSTANCE_ID` **Required**. This playbook only supports backing up components belong to a specific MAS instance at a time. If you have multiple MAS instances in the cluster to be backed up, you need to run this playbook multiple times with different value of this environment variable.
- `MAS_WORKSPACE_ID` **Required**. This playbook only supports backing up components belong to a specific MAS workspace at a time. If you have multiple MAS workspaces in the cluster to be backed up, you need to run this playbook multiple times with different value of this environment variable.
- `DB2_INSTANCE_NAME` **Required**. This playbook will backup the the Db2 instance used by IoT and Monitor, you need to set the correct Db2 instance name for this environment variable.

### Examples

```bash
# Full backup all monitor data for the dev1 instance
export MASBR_ACTION=backup
export MASBR_STORAGE_TYPE=local
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MAS_INSTANCE_ID=dev1
export MAS_WORKSPACE_ID=ws1
export DB2_INSTANCE_NAME=db2w-shared
ansible-playbook ibm.mas_devops.br_monitor

# Incremental backup all monitor data for the dev1 instance
export MASBR_ACTION=backup
export MASBR_BACKUP_TYPE=incr
export MASBR_STORAGE_TYPE=local
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MAS_INSTANCE_ID=dev1
export MAS_WORKSPACE_ID=ws1
export DB2_INSTANCE_NAME=db2w-shared
ansible-playbook ibm.mas_devops.br_monitor

# Restore all monitor data for the dev1 instance
export MASBR_ACTION=restore
export MASBR_STORAGE_TYPE=local
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MASBR_RESTORE_FROM_VERSION=20240630132439
export MAS_INSTANCE_ID=dev1
export MAS_WORKSPACE_ID=ws1
export DB2_INSTANCE_NAME=db2w-shared
ansible-playbook ibm.mas_devops.br_monitor

# Create a scheduled backup of all monitor data for the dev1 instance
# This will run at 01:00, Monday through Friday
export MASBR_ACTION=backup
export MASBR_BACKUP_TYPE=incr
export MASBR_BACKUP_SCHEDULE="0 1 * * 1-5"
export MASBR_JOB_TIMEZONE="Asia/Shanghai"
export MASBR_STORAGE_TYPE=local
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MAS_INSTANCE_ID=dev1
export MAS_WORKSPACE_ID=ws1
export DB2_INSTANCE_NAME=db2w-shared
ansible-playbook ibm.mas_devops.br_monitor
```


Backup/Restore for Health
-------------------------------------------------------------------------------
This playbook `ibm.mas_devops.br_health` will backup the following components that Health depends on in order:

| Component | Ansible Role                                                     | Data included                                                                  |
| --------- | ---------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| mongodb   | [mongodb](../roles/mongodb.md)                                   | MongoDB databases used by MAS Core                                             |
| db2       | [db2](../roles/db2.md)                                           | Db2 instance used by Manage and Health                                         |
| core      | [suite_backup_restore](../roles/suite_backup_restore.md)         | MAS Core namespace resources                                                   |
| manage    | [suite_app_backup_restore](../roles/suite_app_backup_restore.md) | Manage namespace resources <br>Persistent volume data, such as attachments     |
| health    | [suite_backup_restore](../roles/suite_backup_restore.md)         | Health namespace resources <br>Watson Studio project assets                    |

### Environment Variables

- `MAS_INSTANCE_ID` **Required**. This playbook only supports backing up components belong to a specific MAS instance at a time. If you have multiple MAS instances in the cluster to be backed up, you need to run this playbook multiple times with different value of this environment variable.
- `MAS_WORKSPACE_ID` **Required**. This playbook only supports backing up components belong to a specific MAS workspace at a time. If you have multiple MAS workspaces in the cluster to be backed up, you need to run this playbook multiple times with different value of this environment variable.
- `DB2_INSTANCE_NAME` **Required**. This playbook will backup the the Db2 instance used by Manage and Health, you need to set the correct Db2 instance name for this environment variable.

### Examples

```bash
# Full backup all health data for the dev1 instance and ws1 workspace
export MASBR_ACTION=backup
export MASBR_STORAGE_TYPE=local
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MAS_INSTANCE_ID=dev1
export MAS_WORKSPACE_ID=ws1
export DB2_INSTANCE_NAME=mas-dev1-ws1-manage
ansible-playbook ibm.mas_devops.br_health

# Incremental backup all health data for the dev1 instance and ws1 workspace
export MASBR_ACTION=backup
export MASBR_BACKUP_TYPE=incr
export MASBR_STORAGE_TYPE=local
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MAS_INSTANCE_ID=dev1
export MAS_WORKSPACE_ID=ws1
export DB2_INSTANCE_NAME=mas-dev1-ws1-manage
ansible-playbook ibm.mas_devops.br_health

# Restore all health data for the dev1 instance and ws1 workspace
export MASBR_ACTION=restore
export MASBR_STORAGE_TYPE=local
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MASBR_RESTORE_FROM_VERSION=20240630132439
export MAS_INSTANCE_ID=dev1
export MAS_WORKSPACE_ID=ws1
export DB2_INSTANCE_NAME=mas-dev1-ws1-manage
ansible-playbook ibm.mas_devops.br_health

# Create a scheduled backup of all health data for the dev1 instance and ws1 workspace
# This will run at 01:00, Monday through Friday
export MASBR_ACTION=backup
export MASBR_BACKUP_TYPE=incr
export MASBR_BACKUP_SCHEDULE="0 1 * * 1-5"
export MASBR_JOB_TIMEZONE="Asia/Shanghai"
export MASBR_STORAGE_TYPE=local
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MAS_INSTANCE_ID=dev1
export MAS_WORKSPACE_ID=ws1
export DB2_INSTANCE_NAME=mas-dev1-ws1-manage
ansible-playbook ibm.mas_devops.br_health
```


Backup/Restore for Optimizer
-------------------------------------------------------------------------------
This playbook `ibm.mas_devops.br_optimizer` will backup the following components that Optimizer depends on in order:

| Component | Ansible Role                                                     | Data included                                                                  |
| --------- | ---------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| mongodb   | [mongodb](../roles/mongodb.md)                                   | MongoDB databases used by MAS Core and Optimizer                               |
| db2       | [db2](../roles/db2.md)                                           | Db2 instance used by Manage                                                    |
| core      | [suite_backup_restore](../roles/suite_backup_restore.md)         | MAS Core namespace resources                                                   |
| manage    | [suite_app_backup_restore](../roles/suite_app_backup_restore.md) | Manage namespace resources <br>Persistent volume data, such as attachments     |
| optimizer | [suite_backup_restore](../roles/suite_backup_restore.md)         | Optimizer namespace resources                                                  |

### Environment Variables

- `MAS_INSTANCE_ID` **Required**. This playbook only supports backing up components belong to a specific MAS instance at a time. If you have multiple MAS instances in the cluster to be backed up, you need to run this playbook multiple times with different value of this environment variable.
- `MAS_WORKSPACE_ID` **Required**. This playbook only supports backing up components belong to a specific MAS workspace at a time. If you have multiple MAS workspaces in the cluster to be backed up, you need to run this playbook multiple times with different value of this environment variable.
- `DB2_INSTANCE_NAME` **Required**. This playbook will backup the the Db2 instance used by Manage, you need to set the correct Db2 instance name for this environment variable.

### Examples

```bash
# Full backup all optimizer data for the dev1 instance and ws1 workspace
export MASBR_ACTION=backup
export MASBR_STORAGE_TYPE=local
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MAS_INSTANCE_ID=dev1
export MAS_WORKSPACE_ID=ws1
export DB2_INSTANCE_NAME=mas-dev1-ws1-manage
ansible-playbook ibm.mas_devops.br_optimizer

# Incremental backup all optimizer data for the dev1 instance and ws1 workspace
export MASBR_ACTION=backup
export MASBR_BACKUP_TYPE=incr
export MASBR_STORAGE_TYPE=local
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MAS_INSTANCE_ID=dev1
export MAS_WORKSPACE_ID=ws1
export DB2_INSTANCE_NAME=mas-dev1-ws1-manage
ansible-playbook ibm.mas_devops.br_optimizer

# Restore all optimizer data for the dev1 instance and ws1 workspace
export MASBR_ACTION=restore
export MASBR_STORAGE_TYPE=local
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MASBR_RESTORE_FROM_VERSION=20240630132439
export MAS_INSTANCE_ID=dev1
export MAS_WORKSPACE_ID=ws1
export DB2_INSTANCE_NAME=mas-dev1-ws1-manage
ansible-playbook ibm.mas_devops.br_optimizer

# Create a scheduled backup of all optimizer data for the dev1 instance and ws1 workspace
# This will run at 01:00, Monday through Friday
export MASBR_ACTION=backup
export MASBR_BACKUP_TYPE=incr
export MASBR_BACKUP_SCHEDULE="0 1 * * 1-5"
export MASBR_JOB_TIMEZONE="Asia/Shanghai"
export MASBR_STORAGE_TYPE=local
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MAS_INSTANCE_ID=dev1
export MAS_WORKSPACE_ID=ws1
export DB2_INSTANCE_NAME=mas-dev1-ws1-manage
ansible-playbook ibm.mas_devops.br_optimizer
```


Backup/Restore for Visual Inspection
-------------------------------------------------------------------------------
This playbook `ibm.mas_devops.br_visualinspection` will backup the following components that Visual Inspection depends on in order:

| Component        | Ansible Role                                                     | Data included                                                                               |
| ---------------- | ---------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| mongodb          | [mongodb](../roles/mongodb.md)                                   | MongoDB databases used by MAS Core and Visual Inspection                                    |
| core             | [suite_backup_restore](../roles/suite_backup_restore.md)         | MAS Core namespace resources                                                                |
| visualinspection | [suite_app_backup_restore](../roles/suite_app_backup_restore.md) | Visual Inspection namespace resources <br>Persistent volume data, such as images and models |

### Environment Variables

- `MAS_INSTANCE_ID` **Required**. This playbook only supports backing up components belong to a specific MAS instance at a time. If you have multiple MAS instances in the cluster to be backed up, you need to run this playbook multiple times with different value of this environment variable.
- `MAS_WORKSPACE_ID` **Required**. This playbook only supports backing up components belong to a specific MAS workspace at a time. If you have multiple MAS workspaces in the cluster to be backed up, you need to run this playbook multiple times with different value of this environment variable.

### Examples

```bash
# Full backup all visual inspection data for the dev1 instance and ws1 workspace
export MASBR_ACTION=backup
export MASBR_STORAGE_TYPE=local
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MAS_INSTANCE_ID=dev1
export MAS_WORKSPACE_ID=ws1
ansible-playbook ibm.mas_devops.br_visualinspection

# Incremental backup all visual inspection data for the dev1 instance and ws1 workspace
export MASBR_ACTION=backup
export MASBR_BACKUP_TYPE=incr
export MASBR_STORAGE_TYPE=local
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MAS_INSTANCE_ID=dev1
export MAS_WORKSPACE_ID=ws1
ansible-playbook ibm.mas_devops.br_visualinspection

# Restore all visual inspection data for the dev1 instance and ws1 workspace
export MASBR_ACTION=restore
export MASBR_STORAGE_TYPE=local
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MASBR_RESTORE_FROM_VERSION=20240630132439
export MAS_INSTANCE_ID=dev1
export MAS_WORKSPACE_ID=ws1
ansible-playbook ibm.mas_devops.br_visualinspection

# Create a scheduled backup of all visual inspection data for the dev1 instance and ws1 workspace
# This will run at 01:00, Monday through Friday
export MASBR_ACTION=backup
export MASBR_BACKUP_TYPE=incr
export MASBR_BACKUP_SCHEDULE="0 1 * * 1-5"
export MASBR_JOB_TIMEZONE="Asia/Shanghai"
export MASBR_STORAGE_TYPE=local
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MAS_INSTANCE_ID=dev1
export MAS_WORKSPACE_ID=ws1
ansible-playbook ibm.mas_devops.br_visualinspection
```


## Reference
### Directory Structure
No matter what kind of storage systems you choose, the folder structure created in the storage system is same.

Below is the sample folder structure for saving backup jobs:

```
<root_folder>/backups/mongodb-main-full-20240621122530
├── backup.yml
├── database
│   ├── mongodb-main-full-20240621122530.tar.gz
│   └── query.json
└── log
    ├── mongodb-main-full-20240621122530-backup-log.tar.gz
    └── mongodb-main-full-20240621122530-ansible-log.tar.gz

<root_folder>/backups/core-main-full-20240621122530
├── backup.yml
├── log
│   ├── core-main-full-20240621122530-ansible-log.tar.gz
│   └── core-main-full-20240621122530-namespace-log.tar.gz
└── namespace
    └── core-main-full-20240621122530-namespace.tar.gz
```

- `<root_folder>`: the root folder is specified by `MASBR_STORAGE_LOCAL_FOLDER` or `MASBR_STORAGE_CLOUD_BUCKET`
- The backup playbooks will create a seperated backup job folder under the `backups` folder for each component. The backup job folder is named by following this format: `{BACKUP COMPONENT}-{INSTANCE ID}-{BACKUP TYPE}-{BACKUP VERSION}`.
- When using playbook to backup multiple components at once, all backup job folders will be assigned to the same backup version. In above example, the same backup version `20240621122530` for backing up `mongodb` and `core` components.
- `backup.yml`: keep the backup job information
- `database`: data type for database. This folder save the backup files of MongoDB database, Db2 database.
- `namespace`: data type for namespace resources. This folder save the exported namespace resources.
- `pv`: data type for persistent volume. This folder save the persistent volume data, e.g. the Manage attachments, VI images and models.
- `log`: this folder save all job running log files

In addition to the backup jobs, we also save restore jobs in the specified storage location. For example:

```
<root_folder>/restores/mongodb-main-incr-20240622040201-20240622075501
├── log
│   ├── mongodb-main-incr-20240622040201-20240622075501-ansible-log.tar.gz
│   └── mongodb-main-incr-20240622040201-20240622075501-restore-log.tar.gz
└── restore.yml

<root_folder>/restores/core-main-incr-20240622040201-20240622075501
├── log
│   ├── core-main-incr-20240622040201-20240622075501-ansible-log.tar.gz
│   └── core-main-incr-20240622040201-20240622075501-namespace-log.tar.gz
└── restore.yml
```

The restore playbooks will create a seperated restore job folder under the `restores` folder for each component. The restore job folder is named by following this format: `{BACKUP JOB NAME}-{RESTORE VERSION}`.

- `restore.yml`: keep the restore job information
- `log`: this folder save all job running log files

### Data Model
#### backup.yml
```yaml
kind: Backup
name: "core-main-incr-20240622040201"
version: "20240622040201"
type: "incr"
from: "core-main-full-20240621122530"
source:
  domain: "source-cluster.mydomain.com"
  suite: "8.11.11"
  instance: "main"
  workspace: ""
component:
  name: "core"
  instance: "main"
  namespace: "mas-main-core"
data:
  - seq: "1"
    type: "namespace"
    phase: "Completed"
status:
  phase: "Completed"
  startTimestamp: "2024-06-22T04:05:22"
  completionTimestamp: "2024-06-22T04:06:04"
  sentNotifications:
    - type: "Slack"
      channel: "#ansible-slack-dev"
      timestamp: "2024-06-22T04:05:34"
      phase: "InProgress"
    - type: "Slack"
      channel: "#ansible-slack-dev"
      timestamp: "2024-06-22T04:06:10"
      phase: "Completed"
```

#### restore.yml
```yaml
kind: Restore
name: "core-main-incr-20240622040201-20240622075501"
version: "20240622075501"
from: "core-main-incr-20240622040201"
target:
  domain: "target-cluster.mydomain.com"
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
