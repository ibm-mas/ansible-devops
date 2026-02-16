Backup and Restore
===============================================================================

!!! important
    These playbooks are samples to demonstrate how to use the roles in this collection.

    They are **not intended for production use** as-is, they are a starting point for power users to aid in the development of their own Ansible playbooks using the roles in this collection.

    The recommended way to perform backup and restore operations for MAS is to use the [MAS CLI](https://ibm-mas.github.io/cli/), which uses this Ansible Collection to deliver a complete managed lifecycle for your MAS instance.

Overview
-------------------------------------------------------------------------------
MAS Devops Collection includes playbooks for backing up and restoring MAS components and their dependencies. The backup and restore operations are designed to protect your MAS installation and enable disaster recovery, cluster migration, and testing scenarios.

**Supported Components:**
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

MAS Core Backup and Restore
===============================================================================

## Overview
This playbook performs comprehensive backup and restore operations for IBM Maximo Application Suite Core and its dependencies. The playbook can be run against any OCP cluster regardless of its type; whether it's running in IBM Cloud, Azure, AWS, or your local datacenter.

**Important**: Backup can only be restored to an instance with the same MAS instance ID.

## Playbook Content

The playbook executes the following roles in sequence:

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

## Required Environment Variables

### Common Variables (Backup and Restore)
- `MAS_INSTANCE_ID` - The instance ID of the MAS installation
- `MAS_BACKUP_DIR` - Directory where backup files will be stored/retrieved (e.g., `/tmp/mas_backups`)
- `BR_ACTION` - Set to `backup` or `restore`

### Backup-Specific Variables
- `BACKUP_VERSION` - (Optional) Custom version identifier for the backup. If not provided, defaults to timestamp format `YYYYMMDD-HHMMSS`

### Restore-Specific Variables
- `BACKUP_VERSION_TO_RESTORE` - (Required) The backup version identifier to restore
- `IBM_ENTITLEMENT_KEY` - Your IBM Entitlement key (required if `INCLUDE_DRO=true`)
- `DRO_CONTACT_EMAIL` - Primary contact email (required if `INCLUDE_DRO=true`)
- `DRO_CONTACT_FIRSTNAME` - Primary contact first name (required if `INCLUDE_DRO=true`)
- `DRO_CONTACT_LASTNAME` - Primary contact last name (required if `INCLUDE_DRO=true`)

## Optional Environment Variables

### SLS and DRO Configuration
- `INCLUDE_SLS` - Set to `false` to skip SLS backup/restore (default: `true`)
  - Use `false` if SLS is configured externally to the cluster
- `INCLUDE_DRO` - Set to `false` to skip DRO installation on restore (default: `true`)
  - Use `false` if DRO is configured externally to the cluster

### GRAFANA Configuration
- `INCLUDE_GRAFANA` - Set to ``false`` to skip Grafana install (default: `true`)

### Restore to Different Cluster
When restoring to a different cluster with a different domain:
- `MAS_DOMAIN_ON_RESTORE` - Override the MAS domain for the restored instance
- `SLS_URL_ON_RESTORE` - Override the SLS URL in the SLS Config (when `INCLUDE_SLS=false`)
- `DRO_URL_ON_RESTORE` - Override the DRO URL in the DRO Config (when `INCLUDE_DRO=false`)

### MongoDB Configuration
- `MONGODB_INSTANCE_NAME` - MongoDB instance name (default: `mas-mongo-ce`)

### Configuration Directory
- `MAS_CONFIG_DIR` - Directory for SLS/DRO configuration files (required when `INCLUDE_SLS=true` or `INCLUDE_DRO=true` on restore)

## Usage Examples

### Backup MAS Core
Create a complete backup of MAS Core and all dependencies:

```bash
export MAS_INSTANCE_ID=inst1
export MAS_BACKUP_DIR=/backup/mas
export BR_ACTION=backup

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.br_core
```

### Backup with Custom Version
Create a backup with a custom version identifier:

```bash
export MAS_INSTANCE_ID=inst1
export MAS_BACKUP_DIR=/backup/mas
export BR_ACTION=backup
export BACKUP_VERSION=pre-upgrade-backup

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.br_core
```

### Backup Without SLS
Create a backup excluding SLS (when using external SLS):

```bash
export MAS_INSTANCE_ID=inst1
export MAS_BACKUP_DIR=/backup/mas
export BR_ACTION=backup
export INCLUDE_SLS=false

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.br_core
```

### Restore MAS Core
Restore MAS Core from a backup to the same cluster:

```bash
export MAS_INSTANCE_ID=inst1
export MAS_BACKUP_DIR=/backup/mas
export BR_ACTION=restore
export BACKUP_VERSION_TO_RESTORE=20260122-131500

export IBM_ENTITLEMENT_KEY=xxx
export DRO_CONTACT_EMAIL=user@example.com
export DRO_CONTACT_FIRSTNAME=John
export DRO_CONTACT_LASTNAME=Doe
export MAS_CONFIG_DIR=~/masconfig

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.br_core
```

### Restore MAS Core without Grafana
Restore MAS Core from a backup without grafana:

```bash
export MAS_INSTANCE_ID=inst1
export MAS_BACKUP_DIR=/backup/mas
export BR_ACTION=restore
export BACKUP_VERSION_TO_RESTORE=20260122-131500

export INCLUDE_GRAFANA=false

export IBM_ENTITLEMENT_KEY=xxx
export DRO_CONTACT_EMAIL=user@example.com
export DRO_CONTACT_FIRSTNAME=John
export DRO_CONTACT_LASTNAME=Doe
export MAS_CONFIG_DIR=~/masconfig

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.br_core
```


### Restore to Different Cluster
Restore MAS Core to a different cluster with a different domain:

```bash
export MAS_INSTANCE_ID=inst1
export MAS_BACKUP_DIR=/backup/mas
export BR_ACTION=restore
export BACKUP_VERSION_TO_RESTORE=20260122-131500

export IBM_ENTITLEMENT_KEY=xxx
export DRO_CONTACT_EMAIL=user@example.com
export DRO_CONTACT_FIRSTNAME=John
export DRO_CONTACT_LASTNAME=Doe
export MAS_CONFIG_DIR=~/masconfig

# Override domain for new cluster
export MAS_DOMAIN_ON_RESTORE=mas.newcluster.example.com

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.br_core
```

### Restore with External SLS and DRO
Restore MAS Core using external SLS and DRO services:

```bash
export MAS_INSTANCE_ID=inst1
export MAS_BACKUP_DIR=/backup/mas
export BR_ACTION=restore
export BACKUP_VERSION_TO_RESTORE=20260122-131500

# Skip SLS and DRO installation
export INCLUDE_SLS=false
export INCLUDE_DRO=false

# Provide external service URLs
export SLS_URL_ON_RESTORE=https://sls.external.example.com
export DRO_URL_ON_RESTORE=https://dro.external.example.com

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.br_core
```

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

Db2 Backup and Restore
===============================================================================

## Overview
This playbook performs backup and restore operations for IBM Db2 Universal Operator instances. It supports both online and offline backups, and can store backups either on disk or in S3-compatible object storage(database backups only).

**Important**: The playbook supports multiple backup actions:
- `backup` - Full Db2 instance backup
- `backup_database` - Individual database backup
- `restore` - Full Db2 instance restore
- `restore_database` - Individual database restore

## Required Environment Variables

### Common Variables (Backup and Restore)
- `MAS_INSTANCE_ID` - The instance ID of the MAS installation
- `MAS_BACKUP_DIR` - Directory where backup files will be stored/retrieved (e.g., `/tmp/mas_backups`)
- `DB2_INSTANCE_NAME` - Name of the Db2 instance
- `DB2_ACTION` - Set to `backup`, `backup_database`, `restore`, or `restore_database`

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
- `DB2_META_STORAGE_CLASS` - Storage class for metadata
- `DB2_DATA_STORAGE_CLASS` - Storage class for data
- `DB2_BACKUP_STORAGE_CLASS` - Storage class for backups
- `DB2_LOGS_STORAGE_CLASS` - Storage class for logs
- `DB2_TEMP_STORAGE_CLASS` - Storage class for temporary files

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

Manage Application Backup and Restore
===============================================================================

## Overview
This playbook performs backup and restore operations for IBM Maximo Manage application.

**Important**:
- Backup can only be restored to an instance with the same MAS instance ID
- **DB2 backup and restore is NOT automatically included** in the Manage backup/restore playbook
- You **MUST** run the [DB2 backup and restore playbook](#db2-backup-and-restore) as a prerequisite step before running Manage backup or restore operations

## Playbook Content

The playbook executes the following operations:

### Backup Operation
1. **[Backup Db2 Database](../roles/db2.md) - PREREQUISITE STEP** (run `br_db2.yml` playbook separately first)
2. [Backup Manage Application](../roles/suite_app_backup.md)

### Restore Operation
1. **[Restore Db2 Database](../roles/db2.md) - PREREQUISITE STEP** (run `br_db2.yml` playbook separately first)
2. [Restore Manage Application](../roles/suite_app_restore.md)

## Required Environment Variables

### Common Variables (Backup and Restore)
- `MAS_INSTANCE_ID` - The instance ID of the MAS installation
- `MAS_WORKSPACE_ID` - The workspace ID for Manage
- `MAS_BACKUP_DIR` - Directory where backup files will be stored/retrieved (e.g., `/tmp/mas_backups`)
- `MAS_APP_ACTION` - Set to `backup` or `restore` (default: `backup`)

### Backup-Specific Variables
- `MAS_APP_BACKUP_VERSION` - (Optional) Custom version identifier for the backup. If not provided, defaults to timestamp format `YYYYMMDD-HHMMSS`

### Restore-Specific Variables
- `MAS_APP_BACKUP_VERSION_TO_RESTORE` - (Required) The backup version identifier to restore

!!! warning "DB2 Backup/Restore Prerequisites"
    Before running Manage backup or restore, you **MUST** first run the DB2 backup or restore playbook separately. See the [DB2 Backup and Restore](#db2-backup-and-restore) section for all required DB2 environment variables including:
    
    - `DB2_INSTANCE_NAME`
    - `DB2_ACTION` (set to `backup` or `restore`)
    - `DB2_BACKUP_TYPE`
    - `BACKUP_VENDOR`
    - `DB2_BACKUP_VERSION` (for restore operations)
    - S3 variables (if using S3 storage)

## Optional Environment Variables

### Storage Class Override (Restore)
- `OVERRIDE_STORAGECLASS` - Set to `true` to override storage class names from backup (default: `false`)
- `MAS_APP_CUSTOM_STORAGE_CLASS_RWO` - Custom RWO storage class for Manage
- `MAS_APP_CUSTOM_STORAGE_CLASS_RWX` - Custom RWX storage class for Manage

### Db2 Configuration
- `DB2_NAMESPACE` - Namespace where Db2 is installed (default: `db2u`)

## Usage Examples

### Backup Manage Application
Create a complete backup of Manage application. **Note:** You must backup DB2 first as a separate step.

```bash
# STEP 1: Backup DB2 database (PREREQUISITE)
export MAS_INSTANCE_ID=inst1
export MAS_BACKUP_DIR=/backup/mas
export DB2_INSTANCE_NAME=db2w-shared
export DB2_ACTION=backup
export DB2_BACKUP_TYPE=online
export BACKUP_VENDOR=disk

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.br_db2

# STEP 2: Backup Manage application
export MAS_INSTANCE_ID=inst1
export MAS_WORKSPACE_ID=masdev
export MAS_BACKUP_DIR=/backup/mas
export MAS_APP_ACTION=backup

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.br_manage
```

### Backup with Custom Version
Create a backup with a custom version identifier:

```bash
# STEP 1: Backup DB2 database (PREREQUISITE)
export MAS_INSTANCE_ID=inst1
export MAS_BACKUP_DIR=/backup/mas
export DB2_INSTANCE_NAME=db2w-shared
export DB2_ACTION=backup
export DB2_BACKUP_TYPE=online
export BACKUP_VENDOR=disk

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.br_db2

# STEP 2: Backup Manage application with custom version
export MAS_INSTANCE_ID=inst1
export MAS_WORKSPACE_ID=masdev
export MAS_BACKUP_DIR=/backup/mas
export MAS_APP_ACTION=backup
export MAS_APP_BACKUP_VERSION=pre-upgrade-manage

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.br_manage
```

### Backup to S3 Storage
Create a backup storing DB2 and Manage data to S3:

```bash
# STEP 1: Backup DB2 database to S3 (PREREQUISITE)
export MAS_INSTANCE_ID=inst1
export MAS_BACKUP_DIR=/backup/mas
export DB2_INSTANCE_NAME=db2w-shared
export DB2_ACTION=backup
export DB2_BACKUP_TYPE=online
export BACKUP_VENDOR=s3
export BACKUP_S3_ENDPOINT=https://s3.us-east.cloud-object-storage.appdomain.cloud
export BACKUP_S3_BUCKET=mas-manage-backups
export BACKUP_S3_ACCESS_KEY=your-access-key
export BACKUP_S3_SECRET_KEY=your-secret-key

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.br_db2

# STEP 2: Backup Manage application
export MAS_INSTANCE_ID=inst1
export MAS_WORKSPACE_ID=masdev
export MAS_BACKUP_DIR=/backup/mas
export MAS_APP_ACTION=backup

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.br_manage
```

### Restore Manage Application
Restore Manage application. **Note:** You must restore DB2 first as a separate step.

```bash
# STEP 1: Restore DB2 database (PREREQUISITE)
export MAS_INSTANCE_ID=inst1
export MAS_BACKUP_DIR=/backup/mas
export DB2_INSTANCE_NAME=db2w-shared
export DB2_ACTION=restore
export DB2_BACKUP_VERSION=20260122-131500
export BACKUP_VENDOR=disk

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.br_db2

# STEP 2: Restore Manage application
export MAS_INSTANCE_ID=inst1
export MAS_WORKSPACE_ID=masdev
export MAS_BACKUP_DIR=/backup/mas
export MAS_APP_ACTION=restore
export MAS_APP_BACKUP_VERSION_TO_RESTORE=20260122-131500

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.br_manage
```

### Restore with Storage Class Override
Restore Manage to a different cluster with different storage classes:

```bash
# STEP 1: Restore DB2 database with storage override (PREREQUISITE)
export MAS_INSTANCE_ID=inst1
export MAS_BACKUP_DIR=/backup/mas
export DB2_INSTANCE_NAME=db2w-shared
export DB2_ACTION=restore
export DB2_BACKUP_VERSION=20260122-131500
export BACKUP_VENDOR=disk
export OVERRIDE_STORAGECLASS=true
export DB2_META_STORAGE_CLASS=ocs-storagecluster-ceph-rbd
export DB2_DATA_STORAGE_CLASS=ocs-storagecluster-ceph-rbd
export DB2_BACKUP_STORAGE_CLASS=ocs-storagecluster-ceph-rbd
export DB2_LOGS_STORAGE_CLASS=ocs-storagecluster-ceph-rbd
export DB2_TEMP_STORAGE_CLASS=ocs-storagecluster-ceph-rbd

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.br_db2

# STEP 2: Restore Manage application with storage override
export MAS_INSTANCE_ID=inst1
export MAS_WORKSPACE_ID=masdev
export MAS_BACKUP_DIR=/backup/mas
export MAS_APP_ACTION=restore
export MAS_APP_BACKUP_VERSION_TO_RESTORE=20260122-131500
export OVERRIDE_STORAGECLASS=true
export MAS_APP_CUSTOM_STORAGE_CLASS_RWO=ocs-storagecluster-ceph-rbd
export MAS_APP_CUSTOM_STORAGE_CLASS_RWX=ocs-storagecluster-cephfs

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.br_manage
```

## Important Considerations

### Prerequisites for Restore
- Target cluster must have MAS Core installed and configured
- Target cluster must have Db2 Universal Operator installed
- Workspace must exist with the same workspace ID
- Sufficient resources (CPU, memory, storage) for both Db2 and Manage
- Target cluster must use the same MAS instance ID as the backup

### Backup Best Practices
1. **Two-Step Process**: Always backup DB2 first, then Manage application
   - Run `br_db2.yml` playbook before `br_manage.yml`
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
   - Run `br_db2.yml` playbook before `br_manage.yml`
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

