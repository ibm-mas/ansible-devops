# ibm_catalogs
This role installs the **IBM Maximo Operator Catalog**, which is a curated Operator Catalog derived from the **IBM Operator Catalog**, with all content certified compatible with IBM Maximo Application Suite:

Additional, for IBM employees only, the pre-release development operator catalog can be installed, this is achieved by setting both the `artifactory_username` and `artifactory_token` variables.


## Role Variables

### General Variables

#### mas_catalog_version
Version of the IBM Maximo Operator Catalog to install.

- **Optional**
- Environment Variable: `MAS_CATALOG_VERSION`
- Default Value: `@@MAS_LATEST_CATALOG@@` (latest stable version)

**Purpose**: Specifies which version of the IBM Maximo Operator Catalog to install. The catalog provides certified operators compatible with MAS, including MAS Core, applications, and dependencies.

**When to use**:
- Leave as default to install the latest stable catalog version (recommended)
- Set explicitly when you need a specific catalog version
- Set to match your MAS version requirements
- Use specific version for reproducible deployments

**Valid values**: Valid catalog version string (e.g., `v8-240625-amd64`, `v9-250115-amd64`)

**Impact**: Determines which operator versions are available for installation. The catalog version must be compatible with your target MAS version. Using an incompatible catalog version may prevent MAS installation or upgrades.

**Related variables**: The catalog version affects which MAS and application versions can be installed.

**Note**: The default value is automatically updated to the latest stable catalog version. For production deployments, consider pinning to a specific version for consistency and reproducibility.

### Development Variables

#### artifactory_username
Artifactory username for accessing pre-release development catalogs (IBM employees only).

- **Optional**
- Environment Variable: `ARTIFACTORY_USERNAME`
- Default Value: None

**Purpose**: Provides authentication to IBM Artifactory for installing development catalog sources containing pre-release MAS operators. This enables testing of upcoming MAS versions before general availability.

**When to use**:
- Only for IBM employees with Artifactory access
- Only for development/testing of pre-release MAS versions
- Must be set together with `artifactory_token`
- Never use in production environments

**Valid values**: Valid IBM Artifactory username

**Impact**: When set with `artifactory_token`, enables installation of development catalog sources. Without both credentials, only production catalogs are available.

**Related variables**:
- `artifactory_token`: Required together with this username
- Both must be set to enable development catalog access

**Note**: **IBM EMPLOYEES ONLY** - This is for pre-release testing only. Never use development catalogs in production. Keep credentials secure and do not commit to source control.

#### artifactory_token
Artifactory API token for accessing pre-release development catalogs (IBM employees only).

- **Optional**
- Environment Variable: `ARTIFACTORY_TOKEN`
- Default Value: None

**Purpose**: Provides API token authentication to IBM Artifactory for installing development catalog sources containing pre-release MAS operators. This enables testing of upcoming MAS versions before general availability.

**When to use**:
- Only for IBM employees with Artifactory access
- Only for development/testing of pre-release MAS versions
- Must be set together with `artifactory_username`
- Never use in production environments

**Valid values**: Valid IBM Artifactory API token string

**Impact**: When set with `artifactory_username`, enables installation of development catalog sources. Without both credentials, only production catalogs are available.

**Related variables**:
- `artifactory_username`: Required together with this token
- Both must be set to enable development catalog access

**Note**: **IBM EMPLOYEES ONLY** - This is for pre-release testing only. Never use development catalogs in production. Keep this token secure and do not commit to source control. Generate tokens from IBM Artifactory.

### Backup and Restore Variables

#### mas_backup_dir
Directory path where IBM Operator Catalog backup files will be stored.

- **Required** for backup and restore operations
- Environment Variable: `MAS_BACKUP_DIR`
- Default: None

**Purpose**: Specifies the local filesystem directory where backup archives will be created (for backup) or read from (for restore). This directory serves as the central location for all IBM Operator Catalog backup data.

**When to use**:
- Required when `ibm_catalogs_action` is set to `backup` or `restore`
- Should be a persistent location with sufficient storage space
- Ensure the directory is accessible and has appropriate permissions

**Valid values**: Any valid local filesystem path (e.g., `/backup/mas`, `/home/user/catalog-backups`)

**Impact**: All backup files and metadata will be stored in subdirectories under this path. The backup creates a timestamped directory structure: `{mas_backup_dir}/backup-{version}-catalog/`

**Related variables**: Works with `ibm_catalogs_backup_version` to create unique backup directories.

**Note**: Ensure this directory has sufficient space for backup data and is regularly backed up to external storage for disaster recovery.

#### ibm_catalogs_backup_version
Version identifier for the backup, used to create unique backup directories.

- **Optional** for backup (auto-generated if not provided)
- **Required** for restore
- Environment Variable: `IBM_CATALOGS_BACKUP_VERSION`
- Default: Auto-generated timestamp in format `YYYYMMDD-HHMMSS`

**Purpose**: Provides a unique identifier for each backup, allowing multiple backups to coexist and enabling point-in-time restore operations.

**When to use**:
- For backup: Leave unset to auto-generate a timestamp-based version, or provide a custom identifier
- For restore: Must specify the exact version identifier of the backup to restore

**Valid values**: Any string suitable for directory names (alphanumeric, hyphens, underscores). Auto-generated format: `YYYYMMDD-HHMMSS` (e.g., `20260122-131500`)

**Impact**:
- For backup: Creates directory `{mas_backup_dir}/backup-{version}-catalog/`
- For restore: Looks for backup in `{mas_backup_dir}/backup-{version}-catalog/`

**Related variables**: Works with `mas_backup_dir` to determine backup location.

**Note**: When restoring, you must know the exact backup version identifier. List the contents of `mas_backup_dir` to see available backups.

Backup and Restore Operations
-------------------------------------------------------------------------------

This section provides comprehensive information about IBM Operator Catalog backup and restore operations.

### Action Comparison

| Action | Purpose | Instance Resources | Prerequisites | Use Case |
|--------|---------|-------------------|---------------|----------|
| `backup` | Create backup | Yes (catalog and related resources) | Running IBM Operator Catalog | Regular backups, disaster recovery preparation |
| `restore` | Full restore | Yes (recreates catalog and related resources) | Backup archive | Disaster recovery, cluster migration, complete restoration |

### Backup Process

The IBM Operator Catalog backup operation creates a backup of your catalog installation resources:

1. **Catalog Resources**: Backs up Kubernetes resources including:
   - CatalogSource (`ibm-operator-catalog`)
   - Secrets (for development catalogs: `wiotp-docker-local`)
   - ServiceAccounts (`ibm-operator-catalog`, `default`)
2. **Auto-discovered Secrets**: Any secrets referenced by the backed-up resources are automatically discovered and included

**Note**: The backup includes development catalog credentials if they were configured during installation.

**Backup Directory Structure:**
```
{mas_backup_dir}/
└── backup-{version}-catalog/
    └── resources/
        ├── catalogsources/
        ├── secrets/
        └── serviceaccounts/
```

### Restore Process

The IBM Operator Catalog restore operation performs a complete restoration of the catalog:

**Steps:**
1. Validates backup files and required variables
2. Restores Secrets (or creates new `wiotp-docker-local` secret if `artifactory_username` and `artifactory_token` are provided)
3. Restores ServiceAccounts
4. Restores CatalogSource
5. Waits for CatalogSource to be ready (up to 30 minutes)

**When to use:**
- Disaster recovery scenarios
- Migrating IBM Operator Catalog to a new cluster
- Recreating a deleted catalog
- Setting up a new environment from backup

### Important Considerations

**Version Compatibility:**
- Target catalog version should match the backup version
- The restore process validates version compatibility before proceeding

**Storage Requirements:**
- Ensure sufficient storage in the backup directory
- Backup directory structure: `{mas_backup_dir}/backup-{version}-catalog/`
- Monitor disk space during backup operations

**Security:**
- Backup files contain catalog configuration and credentials (for development catalogs)
- Secure backup directory with appropriate permissions (chmod 700 recommended)
- Consider encrypting backups for long-term storage
- Restrict access to backup files to authorized personnel only

**Development Catalog Credentials:**
- If restoring with new `artifactory_username` and `artifactory_token`, the restore will create a new secret instead of using the backed-up one
- This allows updating credentials during restore if needed

### Backup and Restore Best Practices

1. **Regular Backups**: Schedule automated backups at regular intervals, especially before upgrades
2. **Test Restores**: Periodically test restore procedures in non-production environments
3. **Monitor Operations**: Implement monitoring and alerting for backup failures
4. **Backup Validation**: Verify backup integrity after completion
5. **Retention Policy**: Implement and document backup retention policies
6. **Disaster Recovery**: Include IBM Operator Catalog backup/restore in your DR plan
7. **Coordinate with Operators**: Coordinate catalog backups with operator backups that depend on it


## Example Playbook
After installing the Ansible Collection you can include this role in your own custom playbooks.

```yaml
- hosts: localhost
  roles:
    - ibm.mas_devops.ibm_catalogs
```


## Run Role Playbook
After installing the Ansible Collection you can easily run the role standalone using the `run_role` playbook provided.

```bash
ROLE_NAME=ibm_catalogs ansible-playbook ibm.mas_devops.run_role
```


## License
EPL-2.0
