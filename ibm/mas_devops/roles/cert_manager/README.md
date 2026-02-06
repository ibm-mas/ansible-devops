# cert_manager
This role deploys the Red Hat Certificate Manager Operator into the target OpenShift cluster. The operator will be installed into the `cert-manager-operator` namespace, and the operand will be created in the `cert-manager` namespace.

Certificate Manager provides certificate management capabilities for Kubernetes and OpenShift clusters, enabling automated certificate provisioning and renewal.

## Prerequisites
- Red Hat Operators CatalogSource must be installed in the cluster
- Cluster administrator access

## Role Variables

### General Variables

#### cert_manager_action
Specifies which operation to perform on the Certificate Manager operator.

- **Optional**
- Environment Variable: `CERT_MANAGER_ACTION`
- Default Value: `install`

**Purpose**: Controls what action the role executes against the Certificate Manager operator. This allows the same role to handle installation, removal, or no action on the cert-manager deployment.

**When to use**:
- Use `install` (default) for initial deployment or to ensure cert-manager is present
- Use `uninstall` to remove cert-manager (use with extreme caution)
- Use `backup` to backup the cert-manager installation resources to an archive
- Use `restore` to restore the cert-manager installation resources from an archive created from the `backup` action
- Use `none` to skip cert-manager operations while running broader playbooks

**Valid values**: `install`, `uninstall`, `backup`, `restore`, `none`

**Impact**: 
- `install`: Deploys Red Hat Certificate Manager Operator to `cert-manager-operator` namespace and creates operand in `cert-manager` namespace
- `uninstall`: Removes cert-manager operator and operand (destructive operation)
- `backup`: Stores the resources used for the installation (not certificate or secrets) in an archive location
- `restore`: Restores the resources used for the installation (not certificate or secrets) from an archive location
- `none`: Role takes no action

**Related variables**: None

**Note**: **WARNING** - Certificate Manager is a cluster-wide dependency used by MAS, SLS, and other components. Uninstalling it will break certificate management for all dependent applications. Only use `uninstall` if you are certain no applications depend on it.

### Backup and Restore Variables

#### mas_backup_dir
Directory path where Certificate Manager backup files will be stored.

- **Required** for backup and restore operations
- Environment Variable: `MAS_BACKUP_DIR`
- Default: None

**Purpose**: Specifies the local filesystem directory where backup archives will be created (for backup) or read from (for restore). This directory serves as the central location for all Certificate Manager backup data.

**When to use**:
- Required when `cert_manager_action` is set to `backup` or `restore`
- Should be a persistent location with sufficient storage space
- Ensure the directory is accessible and has appropriate permissions

**Valid values**: Any valid local filesystem path (e.g., `/backup/mas`, `/home/user/certmanager-backups`)

**Impact**: All backup files and metadata will be stored in subdirectories under this path. The backup creates a timestamped directory structure: `{mas_backup_dir}/backup-{version}-certmanager/`

**Related variables**: Works with `certmanager_backup_version` to create unique backup directories.

**Note**: Ensure this directory has sufficient space for backup data and is regularly backed up to external storage for disaster recovery.

#### certmanager_backup_version
Version identifier for the backup, used to create unique backup directories.

- **Optional** for backup (auto-generated if not provided)
- **Required** for restore
- Environment Variable: `CERTMANAGER_BACKUP_VERSION`
- Default: Auto-generated timestamp in format `YYMMDD-HHMMSS`

**Purpose**: Provides a unique identifier for each backup, allowing multiple backups to coexist and enabling point-in-time restore operations.

**When to use**:
- For backup: Leave unset to auto-generate a timestamp-based version, or provide a custom identifier
- For restore: Must specify the exact version identifier of the backup to restore

**Valid values**: Any string suitable for directory names (alphanumeric, hyphens, underscores). Auto-generated format: `YYYYMMDD-HHMMSS` (e.g., `20260122-131500`)

**Impact**:
- For backup: Creates directory `{mas_backup_dir}/backup-{version}-certmanager/`
- For restore: Looks for backup in `{mas_backup_dir}/backup-{version}-certmanager/`

**Related variables**: Works with `mas_backup_dir` to determine backup location.

**Note**: When restoring, you must know the exact backup version identifier. List the contents of `mas_backup_dir` to see available backups.

## Backup and Restore Operations
-------------------------------------------------------------------------------

This section provides comprehensive information about Certificate Manager backup and restore operations.

### Action Comparison

| Action | Purpose | Instance Resources | Prerequisites | Use Case |
|--------|---------|-------------------|---------------|----------|
| `backup` | Create backup | Yes (operator and operand resources) | Running Certificate Manager instance | Regular backups, disaster recovery preparation |
| `restore` | Full restore | Yes (recreates operator and operand) | Backup archive | Disaster recovery, cluster migration, complete restoration |

### Backup Process

The Certificate Manager backup operation creates a backup of your Certificate Manager installation resources:

1. **Operator Resources**: Backs up Kubernetes resources including:
   - Projects/Namespaces (`cert-manager-operator` and `cert-manager`)
   - Subscription (`openshift-cert-manager-operator`)
   - OperatorGroup
2. **Auto-discovered Secrets**: Any secrets referenced by the backed-up resources are automatically discovered and included

**Note**: The backup does NOT include individual certificates or secrets created by Certificate Manager for applications. Those are backed up as part of the specific service (e.g., MongoDB, SLS) that uses them.

**Backup Directory Structure:**
```
{mas_backup_dir}/
└── backup-{version}-certmanager/
    └── resources/
        ├── projects/
        ├── subscriptions/
        ├── operatorgroups/
        └── secrets/
```

### Restore Process

The Certificate Manager restore operation performs a complete restoration of the Certificate Manager operator and operand:

**Steps:**
1. Validates backup files and required variables
2. Restores Projects/Namespaces
3. Restores OperatorGroups
4. Restores Subscriptions (triggers operator installation)
5. Waits for cert-manager-operator-controller-manager deployment to be ready (up to 30 minutes)
6. Waits for CertManager cluster Custom Resource to be created (up to 5 minutes)
7. Waits for cert-manager-webhook deployment to be ready (up to 30 minutes)

**When to use:**
- Disaster recovery scenarios
- Migrating Certificate Manager to a new cluster
- Recreating a deleted Certificate Manager instance
- Setting up a new environment from backup

### Important Considerations

**Version Compatibility:**
- Target Certificate Manager version should match the backup version
- Version upgrades should be performed separately, not during restore
- The restore process validates version compatibility before proceeding

**Storage Requirements:**
- Ensure sufficient storage in the backup directory
- Backup directory structure: `{mas_backup_dir}/backup-{version}-certmanager/`
- Monitor disk space during backup operations

**Security:**
- Backup files contain operator configuration and auto-discovered secrets
- Secure backup directory with appropriate permissions (chmod 700 recommended)
- Consider encrypting backups for long-term storage
- Restrict access to backup files to authorized personnel only

### Backup and Restore Best Practices

1. **Regular Backups**: Schedule automated backups at regular intervals, especially before upgrades
2. **Test Restores**: Periodically test restore procedures in non-production environments
3. **Monitor Operations**: Implement monitoring and alerting for backup failures
4. **Backup Validation**: Verify backup integrity after completion
5. **Retention Policy**: Implement and document backup retention policies
6. **Disaster Recovery**: Include Certificate Manager backup/restore in your DR plan
7. **Coordinate with Services**: Coordinate Certificate Manager backups with dependent service backups


## Example Playbook
After installing the Ansible Collection you can include this role in your own custom playbooks.

```yaml
- hosts: localhost
  vars:
    cert_manager_action: install
  roles:
    - ibm.mas_devops.cert_manager
```

## Run Role Playbook
After installing the Ansible Collection you can easily run the role standalone using the `run_role` playbook provided.

```bash
export CERT_MANAGER_ACTION=install
ROLE_NAME=cert_manager ansible-playbook ibm.mas_devops.run_role
```

## License
EPL-2.0
