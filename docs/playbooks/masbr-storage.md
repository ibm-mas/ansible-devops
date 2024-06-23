# Saving Backup Files

You need to set the environment variable `MASBR_STORAGE_TYPE` before you perform a backup or restore job. This variable indicates what type of storage systems that you are using for saving the backup files. Currently, it supports below types:

- `local`: use the local file system, e.g. a folder on your laptop or workstation.
- `cloud`: use the cloud object storage, such as IBM Cloud Object Storage, AWS S3, etc.

## Use local folder

You can save the backup files to a folder on your local file system by setting the following environment variables: 
```
MASBR_STORAGE_TYPE=local
MASBR_STORAGE_LOCAL_FOLDER=~/masbr/lubanbj5
```
- `MASBR_STORAGE_LOCAL_FOLDER`: the path for saving the backup files

## Use cloud object storage

The backup roles use [Rclone](https://rclone.org/) to copy backup files from data stores to cloud object storage. It requires a Rclone configuration file which you can either create it manually, or you can install the Rclone tool and create the configuration file by running the `rclone config` command. For more information about the rclone config command and configuration file format, please refer to the [Rclone documentation](https://rclone.org/s3/#configuration). 

Below is a sample Rclone configuration file that using MinIO object storage:
```
[masbr]
type = s3
provider = Minio
endpoint = http://minio-api.apps.lubanbj5.cdl.ibm.com
access_key_id = Qfx9YGnykJapxL7pzUyA
secret_access_key = qKRGSnxsJ7z6pIA74sVxJ6fkEh4Fq5m4fo0inDuJ
region = minio
```

Set the following environment variables to indicate the roles to use cloud object storage for saving backup files:
```
MASBR_STORAGE_TYPE=cloud
MASBR_STORAGE_CLOUD_RCLONE_FILE=/mnt/configmap/rclone.conf
MASBR_STORAGE_CLOUD_RCLONE_NAME=masbr
MASBR_STORAGE_CLOUD_BUCKET=mas-backup
```

- `MASBR_STORAGE_CLOUD_RCLONE_FILE`: the path where your rclone.conf file is located
- `MASBR_STORAGE_CLOUD_RCLONE_NAME`: the Rclone configuration name (`[masbr]` from above sample) defined in the rclone.conf file
- `MASBR_STORAGE_CLOUD_BUCKET`: the bucket name you created on the object storage for saving the backup files

## Folder structure

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
- The backup roles will create a seperated backup job folder under the `backups` folder for each component. The backup job folder is named by following this format: `{{ BACKUP COMPONENT }}-{{ INSTANCE ID }}-{{ BACKUP TYPE }}-{{ BACKUP VERSION }}-{{ BACKUP RESULT }}`. 
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

- The restore roles will create a seperated restore job folder under the `restores` folder for each component. The restore job folder is named by following this format: `{{ BACKUP JOB NAME }}-{{ RESTORE VERSION }}-{{ RESTORE RESULT }}`. 
- `restore.yml`: keep the restore job information
- `log`: this folder save all job running log files


## backup.yml

```
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

## restore.yml

```
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
