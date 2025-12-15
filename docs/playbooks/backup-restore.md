Backup and Restore
===============================================================================

Overview
-------------------------------------------------------------------------------
MAS Devops Collection includes playbooks for backing up and restoring of the following MAS components and their dependencies:

- [MongoDB](#backuprestore-for-mongodb)
- [Db2](#backuprestore-for-db2)
- [MAS Core](#backuprestore-for-mas-core)
- [Manage](#backuprestore-for-manage)


Configuration - Backup
-------------------------------------------------------------------------------

| Envrionment variable                 | Required (Default Value) | Description |
| ------------------------------------ | ------------------------ | ----------- |
| MASBR_ACTION                         | **Yes**                  | Whether to run the playbook to perform a `backup` or a `restore` |
| MASBR_BACKUP_VERSION            | No                       | By default, this will be in the format of a `YYMMDD-HHMMSS` timestamp (e.g. `251212-021316`). |

The playbooks are switched to backup mode by setting `MASBR_ACTION` to `backup`.

Configuration - Restore
-------------------------------------------------------------------------------

| Envrionment variable                 | Required (Default Value) | Description |
| ------------------------------------ | ------------------------ | ----------- |
| MASBR_ACTION                         | **Yes**                  | Whether to run the playbook to perform a `backup` or a `restore` |
| MASBR_BACKUP_VERSION            | **Yes**                  | Set the backup version to use in the restore, this will be in the format of a `YYMMDD-HHMMSS` timestamp (e.g. `251212-021316`) |

The playbooks are switched to restore mode by setting `MASBR_ACTION` to `restore`. You **must** specify the `MASBR_BACKUP_VERSION` environment variable to indicate which version of the backup files to use.


# MongoDB Community Edition Backup and Restore Playbook
-------------------------------------------------------------------------------
This playbook `ibm.mas_devops.br_mongodb` will invoke the role [mongodb](../roles/mongodb.md) to backup/restore the MongoDB cluster instance and databases.

### Overview

This playbook supports backup and restore operations for a MongoDB Community Edition deployment used by a MAS instance.
If you are using other MongoDB venders, such as IBM Cloud Databases for MongoDB, Amazon DocumentDB or MongoDB Atlas Database, please refer to the corresponding vender's documentation for more information about their provided backup/restore service.

The process is split into instance-level and database-level operations to provide flexibility depending on the target environment and recovery scenario.

## Backup Workflow

The backup operation consists of **two independent phases**.

### 1. MongoDB Instance Backup (Optional)

This phase captures the **Kubernetes resources** required to recreate a MongoDB Community Edition cluster, including:

- MongoDBCommunity custom resource
- Configuration parameters
- User credentials and authentication settings
- TLS and secret references (if applicable)

This backup enables reinstallation of a MongoDB instance while **preserving configuration and users**.

#### Skipping Instance Backup

If instance-level backup is not required, it can be skipped by setting the following environment variable:

```bash
export BR_SKIP_INSTANCE=true
```

2. MongoDB Database Backup

This phase performs a backup of the MongoDB databases associated with the specified MAS instance ID.

- Only databases belonging to the MAS instance are included
- The backup is independent of the MongoDB installation method
- Can be used for restore into a new or existing MongoDB instance

### Restore Workflow

The restore operation also consists of two phases, with behavior determined by the state of the target environment.

### 1. MongoDB Instance Restore (Conditional)

- If no MongoDB instance is currently running in the target namespace:
    - The playbook restores the MongoDB Community Edition instance using the previously backed-up Kubernetes resources
    - Configuration, users, and credentials are recreated
    - Once the instance is ready, database restore begins
- If a MongoDB instance already exists:
    - Instance restore is skipped automatically
    - The playbook proceeds directly to database restore


### 2. MongoDB Database Restore

- Restores the MongoDB databases from the backup
- Databases are restored into the target MongoDB instance
- Supports restoring into:
    - A newly recreated MongoDB instance
    - An existing, running MongoDB instance


| Scenario                               | Instance Restore | Database Restore |
| -------------------------------------- | ---------------- | ---------------- |
| Backup with `BR_SKIP_INSTANCE=true`    | Skipped          | Executed         |
| Restore with no MongoDB instance       | Executed         | Executed         |
| Restore with existing MongoDB instance | Skipped          | Executed         |

### Notes for Operators
- Ensure the correct MAS instance ID is provided before running the playbook
- Verify namespace access and required permissions for Kubernetes resources and secrets
- Instance restore is idempotent and safely skipped when not applicable



### Environment Variables
- `MAS_INSTANCE_ID`: **Required**. This playbook supports backup/restore MongoDB databases that belong to a specific MAS instance, call the playbook multiple times with different values for `MAS_INSTANCE_ID` if you wish to back up multiple MAS instances that use the same MongoDB CE instance.
- `MONGODB_NAMESPACE`: By default the backup and restore processes will use a namespace of `mongoce`, if you have customized the install of MongoDb CE you must set this environment variable to the appropriate namespace you wish to backup from/restore to.
- `MONGODB_INSTANCE_NAME`: By default, the backup process will use `mas-mongo-ce`,  if you have customized the install of MongoDb CE you must set this environment variable to the appropriate namespace you wish to backup from. For restore, this will be picked from the backup data.
- `BR_SKIP_INSTANCE`: By default, this is set to `false`, This flag is used to skip the Mongo instance backup/restore. Set this flag to `true` if you wish to backup/restore only the databases.

### Examples
```bash
# Backup of MongoDB CE cluster instance and database for the dev1 instance
export MASBR_ACTION=backup
export MAS_BACKUP_DIR=/tmp/backup
export MAS_INSTANCE_ID=dev
ansible-playbook ibm.mas_devops.br_mongodb


# Backup of ONLY MongoDB database for the dev1 instance
export MASBR_ACTION=backup
export MAS_BACKUP_DIR=/tmp/backup
export MAS_INSTANCE_ID=dev
export BR_SKIP_INSTANCE=true 
ansible-playbook ibm.mas_devops.br_mongodb


# Restore MongoDB cluster instance and database
export MASBR_ACTION=restore
export MAS_BACKUP_DIR=/tmp/backup
export MASBR_BACKUP_VERSION=251212-101010
export MAS_INSTANCE_ID=dev
ansible-playbook ibm.mas_devops.br_mongodb

# Restore ONLY MongoDB database
export MASBR_ACTION=restore
export MAS_BACKUP_DIR=/tmp/backup
export MASBR_BACKUP_VERSION=251212-101010
export MAS_INSTANCE_ID=dev
export BR_SKIP_INSTANCE=true
ansible-playbook ibm.mas_devops.br_mongodb
```



Backup/Restore for Db2
-------------------------------------------------------------------------------

Coming soon...

Backup/Restore for MAS Core
-------------------------------------------------------------------------------
Coming soon...


Backup/Restore for Manage
-------------------------------------------------------------------------------
Coming soon...

