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
- MongoDB Community Edition
- Db2w Universal Operator
- Manage

**Roles Supporting Backup/Restore:**
- [`ibm.mas_devops.cert_manager`](../roles/cert_manager.md)
- [`ibm.mas_devops.db2`](../roles/db2.md)
- [`ibm.mas_devops.ibm_catalogs`](../roles/ibm_catalogs.md)
- [`ibm.mas_devops.mongodb`](../roles/mongodb.md)
- [`ibm.mas_devops.sls`](../roles/sls.md)
- [`ibm.mas_devops.suite_backup`](../roles/suite_backup.md)
- [`ibm.mas_devops.suite_restore`](../roles/suite_restore.md)

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

