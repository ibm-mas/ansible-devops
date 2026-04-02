Backup and Restore
===============================================================================

!!! important
    These playbooks are samples to demonstrate how to use the roles in this collection.

    They are **not intended for production use** as-is, they are a starting point for power users to aid in the development of their own Ansible playbooks using the roles in this collection.

    The recommended way to perform backup and restore operations for MAS is to use the [MAS CLI](https://ibm-mas.github.io/cli/), which uses this Ansible Collection to deliver a complete managed lifecycle for your MAS instance.

Overview
-------------------------------------------------------------------------------
MAS Devops Collection includes playbooks/guidance for backing up and restoring MAS components and their dependencies. The backup and restore operations are designed to protect your MAS installation and enable disaster recovery, cluster migration, and testing scenarios.

**Supported Components:**
- [MongoDB Community](#mongodb-community-backup-and-restore)
- [MAS Core](#mas-core-backup-and-restore)
- [Db2 Backup and Restore](#db2-backup-and-restore)
- [Manage Application](#manage-application-backup-and-restore)

**Roles Supporting Backup/Restore:**
- [`ibm.mas_devops.cert_manager`](../roles/cert_manager.md)
- [`ibm.mas_devops.db2`](../roles/db2.md)
- [`ibm.mas_devops.ibm_catalogs`](../roles/ibm_catalogs.md)
- [`ibm.mas_devops.mongodb`](../roles/mongodb.md)
- [`ibm.mas_devops.sls`](../roles/sls.md)
- [`ibm.mas_devops.suite_backup`](../roles/suite_backup.md)
- [`ibm.mas_devops.suite_restore`](../roles/suite_restore.md)
- [`ibm.mas_devops.suite_app_backup`](../roles/suite_app_backup.md)
- [`ibm.mas_devops.suite_app_restore`](../roles/suite_app_restore.md)

MongoDB Community Backup and Restore
===============================================================================

## Overview
This playbook performs backup and restore operations for MongoDB Community Edition instances. It supports backing up both the MongoDB instance configuration and database data.

**Important**: 
- Supports MongoDB Community Edition only
- Can backup/restore entire instance or individual databases
- Backup includes both Kubernetes resources and database data

## Playbook Content

The playbook executes the following operations:

### Backup Operation
1. [Backup MongoDB Instance Resources](../roles/mongodb.md) - Kubernetes resources (Deployment, Custom resources, ConfigMaps, Secrets)
2. [Backup MongoDB Database Data](../roles/mongodb.md) - Database data using mongodump

### Restore Operation
1. [Restore MongoDB Instance Resources](../roles/mongodb.md) - Recreate Kubernetes resources
2. [Restore MongoDB Database Data](../roles/mongodb.md) - Restore database data using mongorestore

## Required Environment Variables

### Common Variables (Backup and Restore)
- `MAS_INSTANCE_ID` - The instance ID of the MAS installation
- `MAS_BACKUP_DIR` - Directory where backup files will be stored/retrieved (e.g., `/tmp/mas_backups`)
- `MONGODB_ACTION` - Set to `backup`, `backup-database`, `restore`, or `restore-database`
- `MONGODB_INSTANCE_NAME` - MongoDB instance name (default: `mas-mongo-ce`)
- `MONGODB_NAMESPACE` - Namespace where MongoDB is installed (default: `mongoce`)

### Backup-Specific Variables
- `MONGODB_BACKUP_VERSION` - (Optional) Custom version identifier for the backup. If not provided, defaults to timestamp format `YYYYMMDD-HHMMSS`

### Restore-Specific Variables
- `MONGODB_BACKUP_VERSION` - (Required) The backup version identifier to restore

## Optional Environment Variables

### Storage Class Override (Restore)
- `OVERRIDE_STORAGECLASS` - Set to `true` to override storage class names from backup (default: `false`)
- `MONGODB_STORAGECLASS_NAME_RWO` - Custom RWO storage class for MongoDB

### Application-Specific
- `MAS_APP_ID` - (Optional) MAS application ID if backing up application-specific database

## Usage Examples

### Backup MongoDB Instance
Create a complete backup of MongoDB instance and all databases:

```bash
export MAS_INSTANCE_ID=inst1
export MAS_BACKUP_DIR=/backup/mas
export MONGODB_ACTION=backup
export MONGODB_INSTANCE_NAME=mas-mongo-ce
export MONGODB_NAMESPACE=mongoce

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.br_mongodb
```

### Backup with Custom Version
Create a backup with a custom version identifier:

```bash
export MAS_INSTANCE_ID=inst1
export MAS_BACKUP_DIR=/backup/mas
export MONGODB_ACTION=backup
export MONGODB_BACKUP_VERSION=pre-upgrade-mongo
export MONGODB_INSTANCE_NAME=mas-mongo-ce

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.br_mongodb
```

### Backup Individual Database
Create a backup of a specific database only:

```bash
export MAS_INSTANCE_ID=inst1
export MAS_BACKUP_DIR=/backup/mas
export MONGODB_ACTION=backup-database
export MONGODB_INSTANCE_NAME=mas-mongo-ce
export MAS_APP_ID=manage

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.br_mongodb
```

### Restore MongoDB Instance
Restore MongoDB instance from a backup:

```bash
export MAS_INSTANCE_ID=inst1
export MAS_BACKUP_DIR=/backup/mas
export MONGODB_ACTION=restore
export MONGODB_BACKUP_VERSION=20260122-131500
export MONGODB_INSTANCE_NAME=mas-mongo-ce
export MONGODB_NAMESPACE=mongoce

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.br_mongodb
```

### Restore with Storage Class Override
Restore MongoDB to a different cluster with different storage class:

```bash
export MAS_INSTANCE_ID=inst1
export MAS_BACKUP_DIR=/backup/mas
export MONGODB_ACTION=restore
export MONGODB_BACKUP_VERSION=20260122-131500
export MONGODB_INSTANCE_NAME=mas-mongo-ce
export MONGODB_NAMESPACE=mongoce

# Override storage class
export OVERRIDE_STORAGECLASS=true
export MONGODB_STORAGECLASS_NAME_RWO=ocs-storagecluster-ceph-rbd

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.br_mongodb
```

### Restore Individual Database
Restore a specific database only:

```bash
export MAS_INSTANCE_ID=inst1
export MAS_BACKUP_DIR=/backup/mas
export MONGODB_ACTION=restore-database
export MONGODB_BACKUP_VERSION=20260122-131500
export MONGODB_INSTANCE_NAME=mas-mongo-ce
export MAS_APP_ID=manage

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.br_mongodb
```

## Important Considerations

### Backup Actions
- **backup**: Full backup of MongoDB instance (Kubernetes resources + all database data)
- **backup-database**: Backup specific database data only (requires `MAS_APP_ID`)

### Restore Actions
- **restore**: Full restore of MongoDB instance (Kubernetes resources + all database data)
- **restore-database**: Restore specific database data only (requires `MAS_APP_ID`)

### Prerequisites for Restore
- Target cluster must have MongoDB Community Operator installed
- Sufficient storage capacity for database restoration
- Same or compatible MongoDB version as the backup
- Target cluster must use the same MAS instance ID as the backup

### Backup Best Practices
1. **Regular Schedule**: Perform backups regularly, especially before:
   - MongoDB upgrades
   - MAS upgrades
   - Configuration changes
2. **Full vs Database Backups**: 
   - Use full backups for complete disaster recovery
   - Use database backups for application-specific data protection
3. **Test Restores**: Periodically test restore procedures in non-production environments
4. **Secure Storage**: Store backups in a secure location separate from the cluster

### Restore Best Practices
1. **Pre-Restore Validation**:
   - Verify backup archive exists and is complete
   - Confirm target cluster has sufficient resources
   - Verify MongoDB instance name matches the backup
2. **Post-Restore Verification**:
   - Verify MongoDB pods are running
   - Test database connectivity
   - Verify data integrity
   - Check application connectivity to MongoDB

### Storage Requirements
- Plan for sufficient storage for MongoDB backups
- Database backups can be large depending on data size
- Backup directory structure: `{mas_backup_dir}/backup-{version}-mongoce/`

### Security Considerations
- Backup files contain sensitive data including database contents and credentials
- Secure backup directory with appropriate permissions (chmod 700 recommended)
- Consider encrypting backups for long-term storage
- Restrict access to backup files to authorized personnel only

!!! tip
    If you do not want to set up all the dependencies on your local system, you can run the playbook inside our docker image: `docker run -ti --pull always quay.io/ibmmas/cli`

## Additional Resources

For detailed information about MongoDB backup and restore operations, refer to the role documentation:
- [MongoDB Backup/Restore](../roles/mongodb.md)

Db2 Backup and Restore
===============================================================================

## Overview
This playbook performs backup and restore operations for IBM Db2 Universal Operator instances. It supports both online and offline backups, and can store backups either on disk or in S3-compatible object storage(database backups only).

**Important**: The playbook supports multiple backup actions:
- `backup` - Full Db2 instance backup
- `backup-database` - Individual database backup
- `restore` - Full Db2 instance restore
- `restore-database` - Individual database restore

## Required Environment Variables

### Common Variables (Backup and Restore)
- `MAS_INSTANCE_ID` - The instance ID of the MAS installation
- `MAS_BACKUP_DIR` - Directory where backup files will be stored/retrieved (e.g., `/tmp/mas_backups`)
- `DB2_INSTANCE_NAME` - Name of the Db2 instance
- `DB2_ACTION` - Set to `backup`, `backup-database`, `restore`, or `restore-database`

### Backup-Specific Variables
- `DB2_BACKUP_TYPE` - Set to `online` or `offline` (default: `online`)
- `BACKUP_VENDOR` - Set to `disk` or `s3` (default: `disk`)

### Restore-Specific Variables
- `DB2_BACKUP_VERSION` - (Required) The backup version identifier to restore

### S3 Storage Variables (when BACKUP_VENDOR=s3)
- `BACKUP_S3_ALIAS` - S3 alias name (default: `S3DB2COS`)
- `BACKUP_S3_ENDPOINT` - S3 endpoint URL
- `BACKUP_S3_BUCKET` - S3 bucket name
- `BACKUP_S3_ACCESS_KEY` - S3 access key
- `BACKUP_S3_SECRET_KEY` - S3 secret key

## Optional Environment Variables

### Db2 Configuration
- `DB2_NAMESPACE` - Namespace where Db2 is installed (default: `db2u`)

### Storage Class Override (Restore)
- `OVERRIDE_STORAGECLASS` - Set to `true` to override storage class names from backup (default: `false`)
- `CUSTOM_STORAGE_CLASS_RWO` - Storage class for Read-write-only
- `CUSTOM_STORAGE_CLASS_RWX` - Storage class for Read-write-many


## Usage Examples

### Backup Db2 to Disk (Online)
Create an online backup of Db2 instance to local disk:

```bash
export MAS_INSTANCE_ID=inst1
export MAS_BACKUP_DIR=/backup/mas
export DB2_INSTANCE_NAME=db2w-shared
export DB2_ACTION=backup
export DB2_BACKUP_TYPE=online
export BACKUP_VENDOR=disk

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.br_db2
```

### Backup Db2 to S3
Create a backup of Db2 instance to S3 storage:

```bash
export MAS_INSTANCE_ID=inst1
export MAS_BACKUP_DIR=/backup/mas
export DB2_INSTANCE_NAME=db2w-shared
export DB2_ACTION=backup
export DB2_BACKUP_TYPE=online
export BACKUP_VENDOR=s3
export BACKUP_S3_ENDPOINT=https://s3.us-east.cloud-object-storage.appdomain.cloud
export BACKUP_S3_BUCKET=mas-db2-backups
export BACKUP_S3_ACCESS_KEY=your-access-key
export BACKUP_S3_SECRET_KEY=your-secret-key

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.br_db2
```

### Restore Db2 from Backup
Restore Db2 instance from a previous backup:

```bash
export MAS_INSTANCE_ID=inst1
export MAS_BACKUP_DIR=/backup/mas
export DB2_INSTANCE_NAME=db2w-shared
export DB2_ACTION=restore
export DB2_BACKUP_VERSION=20260122-131500
export BACKUP_VENDOR=disk

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.br_db2
```

### Restore with Storage Class Override
Restore Db2 to a different cluster with different storage classes:

```bash
export MAS_INSTANCE_ID=inst1
export MAS_BACKUP_DIR=/backup/mas
export DB2_INSTANCE_NAME=db2w-shared
export DB2_ACTION=restore
export DB2_BACKUP_VERSION=20260122-131500
export BACKUP_VENDOR=disk

# Override storage classes
export OVERRIDE_STORAGECLASS=true
export DB2_META_STORAGE_CLASS=ocs-storagecluster-ceph-rbd
export DB2_DATA_STORAGE_CLASS=ocs-storagecluster-ceph-rbd
export DB2_BACKUP_STORAGE_CLASS=ocs-storagecluster-ceph-rbd
export DB2_LOGS_STORAGE_CLASS=ocs-storagecluster-ceph-rbd
export DB2_TEMP_STORAGE_CLASS=ocs-storagecluster-ceph-rbd

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.br_db2
```

## Important Considerations

### Backup Types
- **Online Backup**: Database remains available during backup (recommended for production)
- **Offline Backup**: Database is taken offline during backup (faster but causes downtime)

### Storage Vendor Options
- **Disk**: Stores backups on local filesystem or mounted storage
- **S3**: Stores backups in S3-compatible object storage (recommended for production)

### Prerequisites for Restore
- Target cluster must have Db2 Universal Operator installed
- Sufficient storage capacity for database restoration
- Same or compatible Db2 version as the backup


MAS Core Backup and Restore
===============================================================================

## Overview
This guide shows backup and restore operations for IBM Maximo Application Suite Core and its dependencies. This guidance can be used to build your own playbooks to run against any OCP cluster regardless of its type; whether it's running in IBM Cloud, Azure, AWS, or your local datacenter.

**Important**: Backup can only be restored to an instance with the same MAS instance ID.

## Guidance Content

Sequence of roles:

### Backup Operation
1. [Backup IBM Operator Catalogs](../roles/ibm_catalogs.md) (~1 minute)
2. [Backup Certificate Manager](../roles/cert_manager.md) (~1 minute)
3. [Backup MongoDB Community Edition](../roles/mongodb.md) (~5-30 minutes depending on database size)
4. [Backup Suite License Service](../roles/sls.md) (~2 minutes, optional)
5. [Backup MAS Core](../roles/suite_backup.md) (~5 minutes)

### Restore Operation
1. [Restore IBM Operator Catalogs](../roles/ibm_catalogs.md) (~2 minutes)
2. [Restore Certificate Manager](../roles/cert_manager.md) (~5 minutes)
3. [Install Grafana](../roles/grafana.md) (~10 minutes, optional)
4. [Restore MongoDB Community Edition](../roles/mongodb.md) (~10-60 minutes depending on database size)
5. [Restore Suite License Service](../roles/sls.md) (~10 minutes, optional)
6. [Install Data Reporter Operator](../roles/dro.md) (~10 minutes, optional)
7. [Restore MAS Core](../roles/suite_restore.md) (~30 minutes)

All timings are estimates. See the individual role documentation for more information and full details of all configuration options.

## Important Considerations

### Prerequisites for Restore
- Target cluster must have sufficient resources (CPU, memory, storage)
- Certificate Manager must be installed (handled by playbook)
- Target cluster must use the same MAS instance ID as the backup
- Backup files must be accessible from the restore environment

### Backup Best Practices
1. **Regular Schedule**: Perform backups regularly, especially before:
   - MAS upgrades
   - Configuration changes
   - Application installations
   - Cluster maintenance
2. **Test Restores**: Periodically test restore procedures in non-production environments
3. **Secure Storage**: Store backups in a secure location separate from the cluster
4. **Retention Policy**: Implement and document backup retention policies
5. **Verify Integrity**: Verify backup integrity after completion

### Restore Best Practices
1. **Pre-Restore Validation**:
   - Verify backup archive exists and is complete
   - Confirm target cluster has sufficient resources
   - Verify MAS instance ID matches the backup
2. **Dependency Coordination**:
   - Ensure all external services (SLS, DRO, databases) are accessible
   - Verify network connectivity to external services
3. **Post-Restore Verification**:
   - Verify Suite status is Ready
   - Verify all Workspaces are Ready
   - Test application connectivity
   - Test user authentication

### Storage Requirements
- Ensure sufficient storage in the backup directory
- Plan for at least 2x the database size for MongoDB backups
- Monitor disk space during backup operations
- Backup directory structure: `{mas_backup_dir}/backup-{version}-{component}/`

### Security Considerations
- Backup files contain sensitive data including credentials and certificates
- Secure backup directory with appropriate permissions (chmod 700 recommended)
- Consider encrypting backups for long-term storage
- Restrict access to backup files to authorized personnel only
- Ensure secure transfer of backup files to restore environment

!!! tip
    If you do not want to set up all the dependencies on your local system, you can run the playbook inside our docker image: `docker run -ti --pull always quay.io/ibmmas/cli`

## Additional Resources

For detailed information about individual backup and restore operations, refer to the role documentation:
- [IBM Operator Catalogs Backup/Restore](../roles/ibm_catalogs.md)
- [Certificate Manager Backup/Restore](../roles/cert_manager.md)
- [MongoDB Backup/Restore](../roles/mongodb.md)
- [SLS Backup/Restore](../roles/sls.md)
- [MAS Core Backup](../roles/suite_backup.md)
- [MAS Core Restore](../roles/suite_restore.md)
- [Db2 Backup/Restore](../roles/db2.md)

Manage Application Backup and Restore
===============================================================================

## Overview
This guide shows backup and restore operations for IBM Maximo Manage application.

**Important**:
- Backup can only be restored to an instance with the same MAS instance ID
- You **MUST** run the [DB2 backup and restore playbook](#db2-backup-and-restore) as a prerequisite step before running Manage backup or restore operations

## Content

Executes the following operations:

### Backup Operation
1. **[Backup Db2 Database](../roles/db2.md) - PREREQUISITE STEP** (run `br_db2.yml` playbook separately first)
2. [Backup Manage Application](../roles/suite_app_backup.md)

### Restore Operation
1. **[Restore Db2 Database](../roles/db2.md) - PREREQUISITE STEP** (run `br_db2.yml` playbook separately first)
2. [Restore Manage Application](../roles/suite_app_restore.md)

## Important Considerations

### Prerequisites for Restore
- Target cluster must have MAS Core installed and configured
- Target cluster must have Db2 Universal Operator installed
- Workspace must exist with the same workspace ID
- Sufficient resources (CPU, memory, storage) for both Db2 and Manage
- Target cluster must use the same MAS instance ID as the backup

### Backup Best Practices
1. **Two-Step Process**: Always backup DB2 first, then Manage application
   - Run `br_db2.yml` playbook before running Manage application backup
   - DB2 backup is NOT automatically included in Manage backup
2. **Version Alignment**: Use consistent version identifiers for both DB2 and Manage backups for easier tracking
3. **Regular Schedule**: Perform backups regularly, especially before:
   - Manage upgrades or updates
   - Configuration changes
   - Data migrations
4. **Test Restores**: Periodically test restore procedures in non-production environments
5. **Secure Storage**: Store backups in a secure location, preferably using S3 storage

### Restore Best Practices
1. **Pre-Restore Validation**:
   - Verify both DB2 and Manage backup archives exist
   - Confirm target cluster has sufficient resources
   - Verify MAS instance ID and workspace ID match the backup
2. **Restore Order**: **CRITICAL** - Always restore DB2 first, then Manage application
   - Run `br_db2.yml` playbook before running Manage application restore
   - DB2 restore is NOT automatically included in Manage restore
3. **Post-Restore Verification**:
   - Verify DB2 instance is running and accessible
   - Verify Manage workspace status is Ready
   - Test Manage application functionality
   - Verify data integrity

### Storage Requirements
- Plan for sufficient storage for both Db2 and Manage backups
- Db2 backups can be large depending on database size
- Manage application configuration is relatively small
- Consider using S3 storage for production backups

### Security Considerations
- Backup files contain sensitive data including database contents and credentials
- Secure backup directory with appropriate permissions
- Consider encrypting backups for long-term storage
- Restrict access to backup files to authorized personnel only
- Ensure secure transfer of backup files to restore environment

!!! tip
    If you do not want to set up all the dependencies on your local system, you can run the playbook inside our docker image: `docker run -ti --pull always quay.io/ibmmas/cli`

## Additional Resources

For detailed information about individual backup and restore operations, refer to the role documentation:
- [Db2 Backup/Restore](../roles/db2.md)
- [Manage Application Backup](../roles/suite_app_backup.md)
- [Manage Application Restore](../roles/suite_app_restore.md)

