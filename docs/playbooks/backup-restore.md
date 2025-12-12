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


Backup/Restore for MongoDB
-------------------------------------------------------------------------------
This playbook `ibm.mas_devops.br_mongodb` will invoke the role [mongodb](../roles/mongodb.md) to backup/restore the MongoDB cluster instance and databases.

This playbook supports backing up and restoring cluster instance & databases for an in-cluster MongoDB Community Edition instance. If you are using other MongoDB venders, such as IBM Cloud Databases for MongoDB, Amazon DocumentDB or MongoDB Altas Database, please refer to the corresponding vender's documentation for more information about their provided backup/restore service.

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

