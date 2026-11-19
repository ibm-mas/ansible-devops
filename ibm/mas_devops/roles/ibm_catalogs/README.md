# ibm_catalogs

This role installs the **IBM Maximo Operator Catalog**, which is a curated Operator Catalog derived from the **IBM Operator Catalog**, with all content certified compatible with IBM Maximo Application Suite.

Additionally, for IBM employees only, the pre-release development operator catalog can be installed; this is achieved by setting both the `artifactory_username` and `artifactory_token` variables.

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`ibm_catalogs_action`](#ibm_catalogs_action) | No | `install` |
| [`mas_catalog_version`](#mas_catalog_version) | No | `@@MAS_LATEST_CATALOG@@` |
| [`artifactory_username`](#artifactory_username) | No | None |
| [`artifactory_token`](#artifactory_token) | No | None |
| [`mas_backup_dir`](#mas_backup_dir) | Conditional | None |
| [`ibm_catalogs_backup_version`](#ibm_catalogs_backup_version) | Conditional | Auto-generated |

`mas_backup_dir` is required when `ibm_catalogs_action` is `backup` or `restore`, and `ibm_catalogs_backup_version` is required when the action is `restore`.

### Catalog Installation

#### ibm_catalogs_action

Action to perform on the IBM Operator Catalog — valid values are `install` (default), `backup`, `restore`, `uninstall`, or `none` (skip the role entirely).

- **Optional**
- Environment Variable: `IBM_CATALOGS_ACTION`
- Default: `install`

The `backup` and `restore` actions are described in detail in the [Backup and Restore Operations](#backup-and-restore-operations) section.

#### mas_catalog_version

Version of the IBM Maximo Operator Catalog to install — a valid catalog version string, for example `v8-240625-amd64` or `v9-250115-amd64`.

- **Optional**
- Environment Variable: `MAS_CATALOG_VERSION`
- Default: `@@MAS_LATEST_CATALOG@@` (latest stable version)

Determines which operator versions are available for installation; the catalog version must be compatible with your target MAS version, otherwise MAS installation or upgrades may fail. Leave as default to install the latest stable catalog version (recommended), or pin to a specific version for reproducible deployments — the default value is automatically updated to the latest stable catalog version with each release.

### Development Variables

#### artifactory_username

Artifactory username for accessing pre-release development catalogs (IBM employees only).

- **Optional**
- Environment Variable: `ARTIFACTORY_USERNAME`
- Default: None

Provides authentication to IBM Artifactory for installing development catalog sources containing pre-release MAS operators, enabling testing of upcoming MAS versions before general availability. Must be set together with [`artifactory_token`](#artifactory_token); without both credentials, only production catalogs are available.

!!! warning
    IBM employees only — for pre-release testing only. Never use development catalogs in production. Keep credentials secure and do not commit them to source control.

#### artifactory_token

Artifactory API token for accessing pre-release development catalogs (IBM employees only).

- **Optional**
- Environment Variable: `ARTIFACTORY_TOKEN`
- Default: None

Provides API token authentication to IBM Artifactory for installing development catalog sources containing pre-release MAS operators. Must be set together with [`artifactory_username`](#artifactory_username); without both credentials, only production catalogs are available. Generate tokens from IBM Artifactory.

!!! warning
    IBM employees only — for pre-release testing only. Never use development catalogs in production. Keep this token secure and do not commit it to source control.

### Backup and Restore Variables

#### mas_backup_dir

Directory path where IBM Operator Catalog backup files will be stored — any valid local filesystem path, for example `/backup/mas` or `/home/user/catalog-backups`.

- **Required** when `ibm_catalogs_action` is `backup` or `restore`
- Environment Variable: `MAS_BACKUP_DIR`
- Default: None

Specifies the local filesystem directory where backup archives are created (for backup) or read from (for restore). All backup files and metadata are stored in a timestamped directory structure under this path: `{mas_backup_dir}/backup-{version}-catalog/`. Use a persistent location with sufficient storage space, and back it up to external storage for disaster recovery.

#### ibm_catalogs_backup_version

Version identifier for the backup, used to create unique backup directories — any string suitable for directory names (alphanumeric, hyphens, underscores).

- **Optional** for backup (auto-generated if not provided)
- **Required** for restore
- Environment Variable: `IBM_CATALOGS_BACKUP_VERSION`
- Default: Auto-generated timestamp in format `YYYYMMDD-HHMMSS` (e.g., `20260122-131500`)

For backup, leaving this unset auto-generates a timestamp-based version and creates the directory `{mas_backup_dir}/backup-{version}-catalog/`; for restore, you must specify the exact version identifier of the backup to restore, which is looked up in `{mas_backup_dir}/backup-{version}-catalog/`. When restoring, list the contents of `mas_backup_dir` to see the available backups.

## Backup and Restore Operations

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

```text
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
