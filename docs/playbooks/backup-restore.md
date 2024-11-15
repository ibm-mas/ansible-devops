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


Creation of both **full** and **incremental** backups are supported.  The backup and restore Ansible roles can also be used individually, allowing you to build your own customized backup and restore playbook covering exactly what you need. For example, you can only [backup/restore Manage attachments](../roles/suite_app_backup_restore.md).

For more information about backup and restore for Maximo Application Suite, please refer to [Backing up and restoring Maximo Application Suite](https://www.ibm.com/docs/en/mas-cd/continuous-delivery?topic=administering-backing-up-restoring-maximo-application-suite) in the product documentation.


Configuration - Storage
-------------------------------------------------------------------------------
You can save the backup files to a folder on your local file system by setting the following environment variables:

| Envrionment variable                 | Required (Default Value)   | Description |
| ------------------------------------ | -------------------------- | ----------- |
| MASBR_STORAGE_LOCAL_FOLDER           | **Yes**                    | The local path to save the backup files |
| MASBR_LOCAL_TEMP_FOLDER              | No (`/tmp/masbr`)          | Local folder for saving the temporary backup/restore data, the data in this folder will be deleted after the backup/restore job completed. |


Configuration - Backup
-------------------------------------------------------------------------------

| Envrionment variable                 | Required (Default Value) | Description |
| ------------------------------------ | ------------------------ | ----------- |
| MASBR_ACTION                         | **Yes**                  | Whether to run the playbook to perform a `backup` or a `restore` |
| MASBR_BACKUP_TYPE                    | No (`full`)              | Set `full` or `incr` to indicate the playbook to create a **full** backup or **incremental** backup. |
| MASBR_BACKUP_FROM_VERSION            | No                       | Set the full backup version to use in the incremental backup, this will be in the format of a `YYYMMDDHHMMSS` timestamp (e.g. `20240621021316`). |

The playbooks are switched to backup mode by setting `MASBR_ACTION` to `backup`.

### Full Backups
If you set environment variable `MASBR_BACKUP_TYPE=full` or do not specify a value for this variable, the playbook will take a full backup.

### Incremental Backups
You can set environment variable `MASBR_BACKUP_TYPE=incr` to indicate the playbook to take an incremental backup.

!!! important
    Only supports creating incremental backup for MonogDB, Db2 and persistent volume data. The playbook will always create a full backup for other type of data regardless of whether this variable be set to `incr`.

The environment variable `MASBR_BACKUP_FROM_VERSION` is only valid if `MASBR_BACKUP_TYPE=incr`. It indicates which backup version that the incremental backup to based on. If you do not set a value for this variable, the playbook will try to find the latest Completed Full backup from the specified storage location, and then take an incremental backup based on it.

!!! important
    The backup files you specified by `MASBR_BACKUP_FROM_VERSION` must be a Full backup. And the component name and data types in the specified Full backup file must be same as the current incremental backup job.


Configuration - Restore
-------------------------------------------------------------------------------

| Envrionment variable                 | Required (Default Value) | Description |
| ------------------------------------ | ------------------------ | ----------- |
| MASBR_ACTION                         | **Yes**                  | Whether to run the playbook to perform a `backup` or a `restore` |
| MASBR_RESTORE_FROM_VERSION           | **Yes**                  | Set the backup version to use in the restore, this will be in the format of a `YYYMMDDHHMMSS` timestamp (e.g. `20240621021316`) |

The playbooks are switched to restore mode by setting `MASBR_ACTION` to `restore`. You **must** specify the `MASBR_RESTORE_FROM_VERSION` environment variable to indicate which version of the backup files to use.

In the case of restoring from an incremental backup, the corresponding full backup will be restored first before continuing to restore the incremental backup.


Backup/Restore for MongoDB
-------------------------------------------------------------------------------
This playbook `ibm.mas_devops.br_mongodb` will invoke the role [mongodb](../roles/mongodb.md) to backup/restore the MongoDB databases.

This playbook supports backing up and restoring databases for an in-cluster MongoDB CE instance. If you are using other MongoDB venders, such as IBM Cloud Databases for MongoDB, Amazon DocumentDB or MongoDB Altas Database, please refer to the corresponding vender's documentation for more information about their provided backup/restore service.

### Environment Variables
- `MONGODB_NAMESPACE`: By default the backup and restore processes will use a namespace of `mongoce`, if you have customized the install of MongoDb CE you must set this environment variable to the appropriate namespace you wish to backup from/restore to.
- `MAS_INSTANCE_ID`: **Required**. This playbook supports backup/restore MongoDB databases that belong to a specific MAS instance, call the playbook multiple times with different values for `MAS_INSTANCE_ID` if you wish to back up multiple MAS instances that use the same MongoDB CE instance.
- `MAS_APP_ID`: **Optional**. By default, this playbook will backup all databases belonging to the specified MAS instance. You can backup the databases only belong to a specific MAS application by setting this environment variable to a supported MAS application id `core`, `manage`, `iot`, `monitor`, `health`, `optimizer` or `visualinspection`.

### Examples
```bash
# Full backup all MongoDB data for the dev1 instance
export MASBR_ACTION=backup
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MAS_INSTANCE_ID=dev
ansible-playbook ibm.mas_devops.br_mongodb

# Incremental backup all MongoDB data for the dev1 instance
export MASBR_ACTION=backup
export MASBR_BACKUP_TYPE=incr
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MAS_INSTANCE_ID=dev
ansible-playbook ibm.mas_devops.br_mongodb

# Restore all MongoDB data for the dev1 instance
export MASBR_ACTION=restore
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MASBR_RESTORE_FROM_VERSION=20240630132439
export MAS_INSTANCE_ID=dev
ansible-playbook ibm.mas_devops.br_mongodb

# Backup just the IoT MongoDB data for the dev2 instance
export MASBR_ACTION=backup
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
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export DB2_INSTANCE_NAME=db2w-shared
ansible-playbook ibm.mas_devops.br_db2

# Incremental backup for the db2w-shared Db2 instance
export MASBR_ACTION=backup
export MASBR_BACKUP_TYPE=incr
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export DB2_INSTANCE_NAME=db2w-shared
ansible-playbook ibm.mas_devops.br_db2

# Restore for the db2w-shared Db2 instance
export MASBR_ACTION=restore
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
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MAS_INSTANCE_ID=dev
ansible-playbook ibm.mas_devops.br_core

# Incremental backup all core data for the dev1 instance
export MASBR_ACTION=backup
export MASBR_BACKUP_TYPE=incr
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MAS_INSTANCE_ID=dev
ansible-playbook ibm.mas_devops.br_core

# Restore all core data for the dev1 instance
export MASBR_ACTION=restore
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MASBR_RESTORE_FROM_VERSION=20240630132439
export MAS_INSTANCE_ID=dev
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
- `DB2_INSTANCE_NAME` **Required**. This playbook will backup the the Db2 instance used by Manage, you need to set the correct Db2 instance name for this environment variable.

### Examples

```bash
# Full backup all manage data for the dev1 instance and ws1 workspace
export MASBR_ACTION=backup
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MAS_INSTANCE_ID=dev
export MAS_WORKSPACE_ID=ws1
export DB2_INSTANCE_NAME=mas-dev1-ws1-manage
ansible-playbook ibm.mas_devops.br_manage

# Incremental backup all manage data for the dev1 instance and ws1 workspace
export MASBR_ACTION=backup
export MASBR_BACKUP_TYPE=incr
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MAS_INSTANCE_ID=dev
export MAS_WORKSPACE_ID=ws1
export DB2_INSTANCE_NAME=mas-dev1-ws1-manage
ansible-playbook ibm.mas_devops.br_manage

# Restore all manage data for the dev1 instance and ws1 workspace
export MASBR_ACTION=restore
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MASBR_RESTORE_FROM_VERSION=20240630132439
export MAS_INSTANCE_ID=dev
export MAS_WORKSPACE_ID=ws1
export DB2_INSTANCE_NAME=mas-dev1-ws1-manage
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
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MAS_INSTANCE_ID=dev
export MAS_WORKSPACE_ID=ws1
export DB2_INSTANCE_NAME=db2w-shared
ansible-playbook ibm.mas_devops.br_iot

# Incremental backup all iot data for the dev1 instance
export MASBR_ACTION=backup
export MASBR_BACKUP_TYPE=incr
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MAS_INSTANCE_ID=dev
export MAS_WORKSPACE_ID=ws1
export DB2_INSTANCE_NAME=db2w-shared
ansible-playbook ibm.mas_devops.br_iot

# Restore all iot data for the dev1 instance
export MASBR_ACTION=restore
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MASBR_RESTORE_FROM_VERSION=20240630132439
export MAS_INSTANCE_ID=dev
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
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MAS_INSTANCE_ID=dev
export MAS_WORKSPACE_ID=ws1
export DB2_INSTANCE_NAME=db2w-shared
ansible-playbook ibm.mas_devops.br_monitor

# Incremental backup all monitor data for the dev1 instance
export MASBR_ACTION=backup
export MASBR_BACKUP_TYPE=incr
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MAS_INSTANCE_ID=dev
export MAS_WORKSPACE_ID=ws1
export DB2_INSTANCE_NAME=db2w-shared
ansible-playbook ibm.mas_devops.br_monitor

# Restore all monitor data for the dev1 instance
export MASBR_ACTION=restore
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MASBR_RESTORE_FROM_VERSION=20240630132439
export MAS_INSTANCE_ID=dev
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
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MAS_INSTANCE_ID=dev
export MAS_WORKSPACE_ID=ws1
export DB2_INSTANCE_NAME=mas-dev1-ws1-manage
ansible-playbook ibm.mas_devops.br_health

# Incremental backup all health data for the dev1 instance and ws1 workspace
export MASBR_ACTION=backup
export MASBR_BACKUP_TYPE=incr
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MAS_INSTANCE_ID=dev
export MAS_WORKSPACE_ID=ws1
export DB2_INSTANCE_NAME=mas-dev1-ws1-manage
ansible-playbook ibm.mas_devops.br_health

# Restore all health data for the dev1 instance and ws1 workspace
export MASBR_ACTION=restore
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MASBR_RESTORE_FROM_VERSION=20240630132439
export MAS_INSTANCE_ID=dev
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
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MAS_INSTANCE_ID=dev
export MAS_WORKSPACE_ID=ws1
export DB2_INSTANCE_NAME=mas-dev1-ws1-manage
ansible-playbook ibm.mas_devops.br_optimizer

# Incremental backup all optimizer data for the dev1 instance and ws1 workspace
export MASBR_ACTION=backup
export MASBR_BACKUP_TYPE=incr
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MAS_INSTANCE_ID=dev
export MAS_WORKSPACE_ID=ws1
export DB2_INSTANCE_NAME=mas-dev1-ws1-manage
ansible-playbook ibm.mas_devops.br_optimizer

# Restore all optimizer data for the dev1 instance and ws1 workspace
export MASBR_ACTION=restore
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MASBR_RESTORE_FROM_VERSION=20240630132439
export MAS_INSTANCE_ID=dev
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
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MAS_INSTANCE_ID=dev
export MAS_WORKSPACE_ID=ws1
ansible-playbook ibm.mas_devops.br_visualinspection

# Incremental backup all visual inspection data for the dev1 instance and ws1 workspace
export MASBR_ACTION=backup
export MASBR_BACKUP_TYPE=incr
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MAS_INSTANCE_ID=dev
export MAS_WORKSPACE_ID=ws1
ansible-playbook ibm.mas_devops.br_visualinspection

# Restore all visual inspection data for the dev1 instance and ws1 workspace
export MASBR_ACTION=restore
export MASBR_STORAGE_LOCAL_FOLDER=/tmp/backup
export MASBR_RESTORE_FROM_VERSION=20240630132439
export MAS_INSTANCE_ID=dev
export MAS_WORKSPACE_ID=ws1
ansible-playbook ibm.mas_devops.br_visualinspection
```


Reference
-------------------------------------------------------------------------------
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
