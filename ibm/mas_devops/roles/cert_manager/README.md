# cert_manager
This role deploys the Red Hat Certificate Manager Operator into the target OpenShift cluster. The operator will be installed into the `cert-manager-operator` namespace, and the operand will be created in the `cert-manager` namespace.

Certificate Manager provides certificate management capabilities for Kubernetes and OpenShift clusters, enabling automated certificate provisioning and renewal.

## Prerequisites

- Red Hat Operators CatalogSource must be installed in the cluster
- Cluster administrator access

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`cert_manager_action`](#cert_manager_action) | No | `install` |
| [`cert_manager_channel`](#cert_manager_channel) | No | `stable-v1` |
| [`cert_manager_operator_namespace`](#cert_manager_operator_namespace) | No | `cert-manager-operator` |
| [`cert_manager_namespace`](#cert_manager_namespace) | No | `cert-manager` |
| [`mas_backup_dir`](#mas_backup_dir) | Conditional | None |
| [`certmanager_backup_version`](#certmanager_backup_version) | Conditional | Auto-generated |

`mas_backup_dir` and `certmanager_backup_version` only apply when `cert_manager_action` is `backup` or `restore`. `certmanager_backup_version` is auto-generated for backup operations but must be provided explicitly for restore.

### Installation

#### cert_manager_action
Action to perform on the Certificate Manager operator — one of `install` (deploy the operator and operand), `uninstall` (remove them), `backup` (save the installation resources to an archive), `restore` (recreate the installation from an archive created by the `backup` action), or `none` (skip Certificate Manager operations while running broader playbooks).

- **Optional**
- Environment Variable: `CERT_MANAGER_ACTION`
- Default: `install`

`install` deploys the Red Hat Certificate Manager Operator to the `cert-manager-operator` namespace and creates the operand in the `cert-manager` namespace. `backup` and `restore` cover only the resources used for the installation — not certificates or secrets created by Certificate Manager for applications, which are backed up as part of the specific service (e.g. MongoDB, SLS) that uses them.

!!! warning
    Certificate Manager is a cluster-wide dependency used by MAS, SLS, and other components. Uninstalling it will break certificate management for all dependent applications. Only use `uninstall` if you are certain no applications depend on it.

#### cert_manager_channel
Update channel for the Red Hat Certificate Manager operator subscription, for example `stable-v1`.

- **Optional**
- Environment Variable: `REDHAT_CERT_MANAGER_CHANNEL`
- Default: `stable-v1`

#### cert_manager_operator_namespace
Namespace into which the Red Hat Certificate Manager Operator is installed.

- **Optional**
- Environment Variable: None (hardcoded in defaults)
- Default: `cert-manager-operator`

#### cert_manager_namespace
Namespace in which the Certificate Manager operand is created.

- **Optional**
- Environment Variable: None (hardcoded in defaults)
- Default: `cert-manager`

### Backup and Restore

#### mas_backup_dir
Local filesystem directory where backup archives are created (for `backup`) or read from (for `restore`) — any valid local filesystem path, for example `/backup/mas` or `/home/user/certmanager-backups`.

- **Required** when `cert_manager_action` is `backup` or `restore`
- Environment Variable: `MAS_BACKUP_DIR`
- Default: None

All backup files and metadata are stored under `{mas_backup_dir}/backup-{version}-certmanager/`. Use a persistent, accessible location with sufficient storage space, secure it with appropriate permissions (chmod 700 recommended), and back it up to external storage for disaster recovery.

#### certmanager_backup_version
Version identifier for the backup, allowing multiple backups to coexist and enabling point-in-time restores — any string suitable for directory names (alphanumeric, hyphens, underscores), auto-generated as a `YYYYMMDD-HHMMSS` timestamp (e.g. `20260122-131500`) when not provided.

- **Optional** for backup (auto-generated if not provided); **Required** for restore
- Environment Variable: `CERTMANAGER_BACKUP_VERSION`
- Default: Auto-generated timestamp in `YYYYMMDD-HHMMSS` format

The backup is created in (for `backup`) or looked up in (for `restore`) `{mas_backup_dir}/backup-{version}-certmanager/`. When restoring, you must know the exact backup version identifier — list the contents of `mas_backup_dir` to see available backups.

## Backup and Restore Operations

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

The backup does **not** include individual certificates or secrets created by Certificate Manager for applications — those are backed up as part of the specific service (e.g. MongoDB, SLS) that uses them.

Backup directory structure:

```text
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

1. Validates backup files and required variables
2. Restores Projects/Namespaces
3. Restores OperatorGroups
4. Restores Subscriptions (triggers operator installation)
5. Waits for cert-manager-operator-controller-manager deployment to be ready (up to 30 minutes)
6. Waits for CertManager cluster Custom Resource to be created (up to 5 minutes)
7. Waits for cert-manager-webhook deployment to be ready (up to 30 minutes)

Use restore for disaster recovery scenarios, migrating Certificate Manager to a new cluster, recreating a deleted Certificate Manager instance, or setting up a new environment from backup.

### Important Considerations

- **Version compatibility**: The target Certificate Manager version should match the backup version; version upgrades should be performed separately, not during restore. The restore process validates version compatibility before proceeding.
- **Storage**: Ensure sufficient storage in the backup directory and monitor disk space during backup operations.
- **Security**: Backup files contain operator configuration and auto-discovered secrets. Secure the backup directory with appropriate permissions (chmod 700 recommended), consider encrypting backups for long-term storage, and restrict access to backup files to authorized personnel only.

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
