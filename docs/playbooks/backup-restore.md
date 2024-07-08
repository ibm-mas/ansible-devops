Backup and Restore
===============================================================================

Overview
-------------------------------------------------------------------------------
MAS Devops Collection includes playbooks for backup and restore of the following MAS components and their dependencies:

- [MongoDB](#backuprestore-for-mongodb)
- [Db2](#backuprestore-for-db2)
- [MAS Core](#backuprestore-for-mas-core)
- [Manage](#backuprestore-for-manage)
- [IoT](#backuprestore-for-iot)
- [Monitor](#backuprestore-for-monitor)
- [Optimizer](#backuprestore-for-optimizer)
- [Visual Inspection](#backuprestore-for-visual-inspection)

Creation of both full and incremental backups are supported.  Backup and restore actions can be executed locally, or by generating on-demand or scheduled jobs that will allow the work to be performed on your OpenShift cluster using the [MAS CLI container image](https://github.ibm.com/ibm-mas/cli).

!!! tip
    The backup and restore Ansible roles can also be used individually, allowing you to build your own customized backup and restore playbook covering exactly what you need.


For more information about backup and restore for Maximo Application Suite refer to [Restoring and validating Maximo Application Suite](https://www.ibm.com/docs/en/mas-cd/continuous-delivery?topic=suite-restoring-validating-maximo-application) in the product documentation.


Configuration
-------------------------------------------------------------------------------
Before running the playbooks to backup different MAS components, you must set several environment variables to indicate the playbooks where to save the backup files

| Envrionment variable                 | Required (Default Value) | Description |
| ------------------------------------ | ------------------------ | ----------- |
| MASBR_ACTION                         | Yes                      | Whether to run the playbook to perform a `backup` or a `restore` |
| MASBR_CONFIRM_CLUSTER                | No (`false`)             | Whether to confirm the currently connected cluster before run tasks |
| MASBR_CREATE_TASK_JOB                | No (`false`)             | Whether to run backup/restore process in k8s Job |
| MASBR_COPY_TIMEOUT_SEC               | No (`3600`)              | Copying file timeout in seconds |
| MASBR_BACKUP_TYPE                    | No (`full`)              | Take a full backup or incremental backup |
| MASBR_BACKUP_FROM_VERSION            | No                       | The version of the backup to create incremental backup based on |
| MASBR_BACKUP_SCHEDULE                | No                       | Cron expression for running scheduled backup job |
| MASBR_BACKUP_TIMEZONE                | No                       | Time zone for scheduled backup |
| MASBR_RESTORE_FROM_VERSION           | Yes, if `MASBR_ACTION=restore` | The version of the backup to be restored from |
| MASBR_MASCLI_IMAGE_TAG               | No (`latest`)            | MAS CLI docker image tag |
| MASBR_MASCLI_IMAGE_PULL_POLICY       | No                       | MAS CLI docker [image pull policy](https://kubernetes.io/docs/concepts/containers/images/#imagepullpolicy-defaulting) |
| MASBR_RCLONE_IMAGE_TAG               | No (`1.67.0`)            | Rclone docker image tag |
| MASBR_RCLONE_IMAGE_PULL_POLICY       | No                       | Rclone docker [image pull policy](https://kubernetes.io/docs/concepts/containers/images/#imagepullpolicy-defaulting) |
| MASBR_STORAGE_TYPE                   | Yes                                    | Type of storage system for saving the backup files |
| MASBR_STORAGE_LOCAL_FOLDER           | Yes, if `MASBR_STORAGE_TYPE=local` | Local path for saving backup files |
| MASBR_STORAGE_CLOUD_RCLONE_FILE      | Yes, if `MASBR_STORAGE_TYPE=cloud` | The path of rclone.conf file |
| MASBR_STORAGE_CLOUD_RCLONE_NAME      | Yes if `MASBR_STORAGE_TYPE=cloud` | The config name defined in rclone.conf file |
| MASBR_STORAGE_CLOUD_BUCKET           | Yes, if `MASBR_STORAGE_TYPE=cloud` | Object storage bucket for saving backup files |
| MASBR_LOCAL_TEMP_FOLDER              | No (`/tmp/masbr`)                      | Local temp folder for backup/restore |
| MASBR_SLACK_ENABLED                  | No (false)                             | Whether to send Slack notifications |
| MASBR_SLACK_LEVEL                    | No (info)                              | Slack notification level            |
| MASBR_SLACK_TOKEN                    | Yes, if `MASBR_SLACK_ENABLED=true` | Slack integration token             |
| MASBR_SLACK_CHANNEL                  | Yes, if `MASBR_SLACK_ENABLED=true` | Channel to send the message to      |
| MASBR_SLACK_USER                     | No (MASBR)                             | Sender of the message               |

### Kubernetes Jobs
When the playbook/role starts running, it will first perform some checks, such as checking the required environment variables, get the soruce cluster information, etc. Then, depending on the value of `MASBR_CREATE_TASK_JOB`, the remaining backup/restore process can be ran in different ways:

- `MASBR_CREATE_TASK_JOB=false` Run backup/restore process in your current terminal, and you can view the terminal output to get the progress of the backup/restore
- `MASBR_CREATE_TASK_JOB=true` A new k8s Job will be created to run the backup/restore process in the cluster, then you can check the log of the created k8s Job in the cluster to monitor the backup/restore progress

### File Transfer Timeout
During the backup/restore process, the playbook/role will copy backup files between different data stores and specified backup storage systems. Set a suitable value for this environment variable to avoid the playbook/role entering a waiting state due to some errors, such as the specified storage system network speed is too slow or cannot be connected.

!!! important
    Set a suitable value based on the expected size of the backup/restore data and the network conditions, setting this too low can result in the data copying process being interrupted

### Incremental Backups
If you set environment variable `MASBR_BACKUP_TYPE=full` or do not specify a value for this variable, the playbook/role will take a full backup. You can set environment variable `MASBR_BACKUP_TYPE=incr` to indicate the playbook/role to take an incremental backup.

Only the below types of data support incremental backups:

- `database`: MongoDB databases, Db2 instance
- `pv`: Persistent volume data

The playbook/role will always take a full backup for other type of data regardless of whether this variable is set to `incr`.

To perform an incremental backup `MASBR_BACKUP_FROM_VERSION` can be used to indicate which backup version that the incremental backup to based on.  If you do not set a value, then the playbook/role will take an incremental backup based on the latest completed full backup from the specified storage location.

!!! important
    The component name and data types in the backup file which specified by `MASBR_BACKUP_FROM_VERSION` should be same as the ones in the current incremental backup job.

### Scheduled Backups
In addition to create an on-demand backup job, you can also set environment variable `MASBR_BACKUP_SCHEDULE` to indicate the playbook/role to create a k8s CronJob to run the backup process periodically.

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

By default, the k8s CronJob use UTC time zone, so maybe you want to set the Cron expression based on your local [time zone](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones). You can set the environment variable `MASBR_BACKUP_TIMEZONE` for this.


### Restore
The playbooks are switched to restore mode by setting `MASBR_ACTION` to `restore`.  You **must** specify the `MASBR_RESTORE_FROM_VERSION` environment variable to indicate which version of the backup files to use.

In the case of restoring from an incremental backup, the corresponding full backup will be restored first before continuing to restore the incremental backup.


### Storage
You need to set the environment variable `MASBR_STORAGE_TYPE` before you perform a backup or restore job. This variable indicates what type of storage systems that you are using for saving the backup files. Currently, it supports below types:

- When `MASBR_STORAGE_TYPE` is set to `local` the backup roles will use the local file system, e.g. a folder on your laptop or workstation.
- When `MASBR_STORAGE_TYPE` is set to `cloud` the backup roles use [rclone](https://rclone.org/) to copy backup files from data stores to cloud object storage. It requires an [rclone configuration file](https://rclone.org/s3/#configuration) which you can either create manually, or use `rclone config` to generate.


### Slack Notifications
Integration with Slack is support through the following environment variables, with two supported notification levels:

- `info` Send notifications when job in the phase `InProgress`, `Completed`, `Failed`, `PartiallyFailed`
- `failure` Send notifications only when job in the phase `Failed`, `PartiallyFailed`


Backup/Restore for MongoDB
-------------------------------------------------------------------------------
This playbook `ibm.mas_devops.backup_mongodb` will invoke the role [mongodb](../roles/mongodb.md) to backup the MongoDB databases to the specified backup storage location.

This playbook supports backing up databases from an in-cluster MongoDB CE instance. If you are using other MongoDB venders, such as IBM Cloud Databases for MongoDB, Amazon DocumentDB or MongoDB Altas Database, please refer to the corresponding vender's documentation for more information about their provided backup/restore service.

### Environment Variables

- `MAS_INSTANCE_ID`: **Required** This playbook supports backing up MongoDB databases that belong to a specific MAS instance, call the playbook multiple times with different values for `MAS_INSTANCE_ID` if you wish to backup multiple MAS instances that use the same MongoDb CE instance.
- `MAS_APP_ID`: **Optional** By default, this playbook will backup all databases belonging to the specified MAS instance. You can backup the databases only belong to a specific MAS application by setting this environment variable to either `core` or `iot`.

### Examples
```bash
# Full backup all MongoDb data for the dev1 instance
export MASBR_ACTION=backup
export MASBR_STORAGE_TYPE=local
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MAS_INSTANCE_ID=dev1
ansible-playbook ibm.mas_devops.br_mongodb

# Incremental backup all MongoDb data for the dev1 instance
export MASBR_ACTION=backup
export MASBR_BACKUP_TYPE=incr
export MASBR_STORAGE_TYPE=local
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MAS_INSTANCE_ID=dev1
ansible-playbook ibm.mas_devops.br_mongodb

# Restore all MongoDb data for the dev1 instance
export MASBR_ACTION=restore
export MASBR_STORAGE_TYPE=local
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MASBR_RESTORE_FROM_VERSION=20240630132439
export MAS_INSTANCE_ID=dev1
ansible-playbook ibm.mas_devops.br_mongodb

# Backup just the IoT MongoDb data for the dev2 instance
export MASBR_STORAGE_TYPE=local
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MAS_INSTANCE_ID=dev2
export MAS_APP_ID=iot
ansible-playbook ibm.mas_devops.br_mongodb
```


Backup/Restore for Db2
-------------------------------------------------------------------------------
This playbook `ibm.mas_devops.backup_db2` will invoke the role [db2](../roles/db2.md) to backup Db2 instance to the specified backup storage location.

### Environment Variables

- `DB2_INSTANCE_NAME`: **Required** This playbook only supports backing up specific Db2 instance at a time. If you want to backup all Db2 instances in the Db2 cluster, you need to run this playbook multiple times with different value of this environment variable.


Backup/Restore for MAS Core
-------------------------------------------------------------------------------
This playbook `ibm.mas_devops.backup_core` will backup the following components that MAS Core depends on in order:

| Component | Ansible Role                                             | Data included                      |
| --------- | -------------------------------------------------------- | ---------------------------------- |
| mongodb   | [mongodb](../roles/mongodb.md)                           | MongoDB databases used by MAS Core |
| core      | [suite_backup_restore](../roles/suite_backup_restore.md) | MAS Core namespace resources       |


### Environment Variables

- `MAS_INSTANCE_ID` **Required** The MAS instance ID to perform a backup for.

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
This playbook `ibm.mas_devops.backup_manage` will backup the following components that Manage depends on in order:

| Component | Role                                                             | Data included                                                                  |
| --------- | ---------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| mongodb   | [mongodb](../roles/mongodb.md)                                   | MongoDB databases used by MAS Core                                             |
| db2       | [db2](../roles/db2.md)                                           | Db2 instance used by Manage                                                    |
| core      | [suite_backup_restore](../roles/suite_backup_restore.md)         | MAS Core namespace resources                                                   |
| manage    | [suite_app_backup_restore](../roles/suite_app_backup_restore.md) | Manage namespace resources <br>Persistent volume data, such as attachments     |


### Environment Variables

- `MAS_INSTANCE_ID` **Required** This playbook only supports backing up components belong to a specific MAS instance at a time. If you have multiple MAS instances in the cluster to be backed up, you need to run this playbook multiple times with different value of this environment variable.
- `MAS_WORKSPACE_ID` **Required** This playbook only supports backing up components belong to a specific MAS workspace at a time. If you have multiple MAS workspaces in the cluster to be backed up, you need to run this playbook multiple times with different value of this environment variable.
- `DB2_INSTANCE_NAME` **Required** This playbook will backup the the Db2 instance used by Manage, you need to set the correct Db2 instance name for this environment variable.

### Examples

```bash
# Full backup all manage data for the dev1 instance
export MASBR_ACTION=backup
export MASBR_STORAGE_TYPE=local
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MAS_INSTANCE_ID=dev1
export MAS_WORKSPACE_ID=ws1
export DB2_INSTANCE_NAME=mas-main-masdev-manage
ansible-playbook ibm.mas_devops.br_manage

# Incremental backup all manage data for the dev1 instance
export MASBR_ACTION=backup
export MASBR_BACKUP_TYPE=incr
export MASBR_STORAGE_TYPE=local
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MAS_INSTANCE_ID=dev1
export MAS_WORKSPACE_ID=ws1
export DB2_INSTANCE_NAME=mas-dev1-ws1-manage
ansible-playbook ibm.mas_devops.br_manage

# Restore all manage data for the dev1 instance
export MASBR_ACTION=restore
export MASBR_STORAGE_TYPE=local
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MASBR_RESTORE_FROM_VERSION=20240630132439
export MAS_INSTANCE_ID=dev1
export MAS_WORKSPACE_ID=ws1
export DB2_INSTANCE_NAME=mas-dev1-ws1-manage
ansible-playbook ibm.mas_devops.br_manage

# Create a scheduled backup of all manage data for the dev1 instance
# This will run at 01:00, Monday through Friday
export MASBR_BACKUP_SCHEDULE="0 1 * * 1-5"
export MASBR_BACKUP_TYPE=incr
export MAS_INSTANCE_ID=dev1
export MAS_WORKSPACE_ID=ws1
export DB2_INSTANCE_NAME=mas-dev1-ws1-manage
ansible-playbook ibm.mas_devops.backup_manage
```


Backup/Restore for IoT
-------------------------------------------------------------------------------
This playbook `ibm.mas_devops.backup_iot` will backup the following components that IoT depends on in order:

| Component | Ansible Role                                                     | Data included                              |
| --------- | ---------------------------------------------------------------- | ------------------------------------------ |
| mongodb   | [mongodb](../roles/mongodb.md)                                   | MongoDB databases used by MAS Core and IoT |
| db2       | [db2](../roles/db2.md)                                           | Db2 instance used by IoT                   |
| core      | [suite_backup_restore](../roles/suite_backup_restore.md)         | MAS Core namespace resources               |
| iot       | [suite_app_backup_restore](../roles/suite_app_backup_restore.md) | IoT namespace resources                    |

### Environment Variables

- `MAS_INSTANCE_ID` **Required** This playbook only supports backing up components belong to a specific MAS instance at a time. If you have multiple MAS instances in the cluster to be backed up, you need to run this playbook multiple times with different value of this environment variable.
- `MAS_WORKSPACE_ID` **Required** This playbook only supports backing up components belong to a specific MAS workspace at a time. If you have multiple MAS workspaces in the cluster to be backed up, you need to run this playbook multiple times with different value of this environment variable.
- `DB2_INSTANCE_NAME` **Required** This playbook will backup the the Db2 instance used by IoT, you need to set the correct Db2 instance name for this environment variable.


Backup/Restore for Monitor
-------------------------------------------------------------------------------
This playbook `ibm.mas_devops.backup_monitor` will backup the following components that Monitor depends on in order:

| Component | Ansible Role                                                     | Data included                                       |
| --------- | ---------------------------------------------------------------- | --------------------------------------------------- |
| mongodb   | [mongodb](../roles/mongodb.md)                                   | MongoDB databases used by MAS Core, IoT and Monitor |
| db2       | [db2](../roles/db2.md)                                           | Db2 instance used by IoT and Monitor                |
| core      | [suite_backup_restore](../roles/suite_backup_restore.md)         | MAS Core namespace resources                        |
| iot       | [suite_app_backup_restore](../roles/suite_app_backup_restore.md) | IoT namespace resources                             |
| monitor   | [suite_app_backup_restore](../roles/suite_app_backup_restore.md) | Monitor namespace resources                         |


### Environment Variables

- `MAS_INSTANCE_ID` **Required** TThis playbook only supports backing up components belong to a specific MAS instance at a time. If you have multiple MAS instances in the cluster to be backed up, you need to run this playbook multiple times with different value of this environment variable.
- `MAS_WORKSPACE_ID` **Required** TThis playbook only supports backing up components belong to a specific MAS workspace at a time. If you have multiple MAS workspaces in the cluster to be backed up, you need to run this playbook multiple times with different value of this environment variable.
- `DB2_INSTANCE_NAME` **Required** TThis playbook will backup the the Db2 instance used by IoT and Monitor, you need to set the correct Db2 instance name for this environment variable.


Backup/Restore for Optimizer
-------------------------------------------------------------------------------
This playbook `ibm.mas_devops.backup_optimizer` will backup the following components that Optimizer depends on in order:

| Component | Ansible Role                                                     | Data included                                                                  |
| --------- | ---------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| mongodb   | [mongodb](../roles/mongodb.md)                                   | MongoDB databases used by MAS Core and Optimizer                               |
| db2       | [db2](../roles/db2.md)                                           | Db2 instance used by Manage                                                    |
| core      | [suite_backup_restore](../roles/suite_backup_restore.md)         | MAS Core namespace resources                                                   |
| manage    | [suite_app_backup_restore](../roles/suite_app_backup_restore.md) | Manage namespace resources <br>Persistent volume data, such as attachments     |
| optimizer | [suite_backup_restore](../roles/suite_backup_restore.md)         | Optimizer namespace resources                                                  |

### Environment Variables

- `MAS_INSTANCE_ID` **Required** TThis playbook only supports backing up components belong to a specific MAS instance at a time. If you have multiple MAS instances in the cluster to be backed up, you need to run this playbook multiple times with different value of this environment variable.
- `MAS_WORKSPACE_ID` **Required** TThis playbook only supports backing up components belong to a specific MAS workspace at a time. If you have multiple MAS workspaces in the cluster to be backed up, you need to run this playbook multiple times with different value of this environment variable.
- `DB2_INSTANCE_NAME` **Required** TThis playbook will backup the the Db2 instance used by Manage, you need to set the correct Db2 instance name for this environment variable.


Backup/Restore for Visual Inspection
-------------------------------------------------------------------------------
This playbook `ibm.mas_devops.backup_visualinspection` will backup the following components that Visual Inspection depends on in order:

| Component        | Ansible Role                                                     | Data included                                                                               |
| ---------------- | ---------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| mongodb          | [mongodb](../roles/mongodb.md)                                   | MongoDB databases used by MAS Core and Visual Inspection                                    |
| core             | [suite_backup_restore](../roles/suite_backup_restore.md)         | MAS Core namespace resources                                                                |
| visualinspection | [suite_app_backup_restore](../roles/suite_app_backup_restore.md) | Visual Inspection namespace resources <br>Persistent volume data, such as images and models |

### Environment Variables

- `MAS_INSTANCE_ID` **Required** TThis playbook only supports backing up components belong to a specific MAS instance at a time. If you have multiple MAS instances in the cluster to be backed up, you need to run this playbook multiple times with different value of this environment variable.
- `MAS_WORKSPACE_ID` **Required** TThis playbook only supports backing up components belong to a specific MAS workspace at a time. If you have multiple MAS workspaces in the cluster to be backed up, you need to run this playbook multiple times with different value of this environment variable.


## Reference
### Directory Structure
No matter what kind of above storage systems you choose, the folder structure created in the storage system is same.

Below is the sample folder structure for saving backup jobs:

```
<root_folder>/backups/mongodb-main-full-20240621122530-Completed
├── backup.yml
├── database
│   ├── mongodb-main-full-20240621122530.tar.gz
│   └── query.json
└── log
    ├── mongodb-backup-log.tar.gz
    └── mongodb-main-full-20240621122530-ansible-log.tar.gz

<root_folder>/backups/core-main-full-20240621122530-Completed
├── backup.yml
├── log
│   ├── core-main-full-20240621122530-ansible-log.tar.gz
│   └── core-main-full-20240621122530-namespace-log.tar.gz
└── namespace
    └── core-main-full-20240621122530-namespace.tar.gz
```

- `<root_folder>`: the root folder is specified by `MASBR_STORAGE_LOCAL_FOLDER` or `MASBR_STORAGE_CLOUD_BUCKET`
- The backup roles will create a seperated backup job folder under the `backups` folder for each component. The backup job folder is named by following this format: `{BACKUP COMPONENT}-{INSTANCE ID}-{BACKUP TYPE}-{BACKUP VERSION}-{BACKUP RESULT}`.
- If you are using playbook to backup multiple components at once, all backup job folder will be assigned to the same backup version. In above example, the same backup version `20240621122530` for backing up `mongodb` and `core` components.
- `backup.yml`: keep the backup job information
- `database`: this folder save the backup files of MongoDB database, Db2 database
- `namespace`: this folder save the exported namespace resources
- `pv`: this folder save the persistent volume data
- `log`: this folder save all job running log files

In addition to the backup jobs, we also save restore jobs in the specified storage location. For example:

```
<root_folder>/restores/mongodb-main-incr-20240622040201-20240622075501-Completed
├── log
│   ├── mongodb-main-incr-20240622040201-20240622075501-ansible-log.tar.gz
│   └── mongodb-restore-log.tar.gz
└── restore.yml

<root_folder>/restores/core-main-incr-20240622040201-20240622075501-Completed
├── log
│   ├── core-main-incr-20240622040201-20240622075501-ansible-log.tar.gz
│   └── core-main-incr-20240622040201-20240622075501-namespace-log.tar.gz
└── restore.yml
```

The restore roles will create a seperated restore job folder under the `restores` folder for each component. The restore job folder is named by following this format: `{BACKUP JOB NAME}-{RESTORE VERSION}-{RESTORE RESULT}`.
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
  domain: "lubanbj5.cdl.ibm.com"
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
