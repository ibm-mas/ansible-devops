# suite_restore

Restore MAS Core

## Overview

This role supports restoring the MAS Core namespace resources and supporting
resources in other namespace when provided the backup archive generated from
`suite_backup` role.

!!! important
    Supported only for MAS 9.1.x.

    Restore can only be made to an instance with the same MAS instance ID as the backup.

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`mas_instance_id`](#mas_instance_id) | Yes | None |
| [`mas_backup_dir`](#mas_backup_dir) | Yes | None |
| [`suite_backup_version`](#suite_backup_version) | Yes | None |
| [`mas_domain`](#mas_domain) | No | `NO_OVERRIDE` |
| [`include_sls_from_backup`](#include_sls_from_backup) | No | `true` |
| [`sls_url`](#sls_url) | No | `NO_OVERRIDE` |
| [`sls_cfg_file`](#sls_cfg_file) | Conditional | None |
| [`include_dro_from_backup`](#include_dro_from_backup) | No | `true` |
| [`bas_url`](#bas_url) | No | `NO_OVERRIDE` |
| [`dro_cfg_file`](#dro_cfg_file) | Conditional | None |

`sls_cfg_file` is required only when `include_sls_from_backup` is `false`, and `dro_cfg_file` only when `include_dro_from_backup` is `false`.

### Backup Source

#### mas_instance_id

The instance ID of the Maximo Application Suite installation to restore. This must match the instance ID of the backup.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

#### mas_backup_dir

The local directory path where backup files to restore are stored — for example `/tmp/mas_backups`.

- **Required**
- Environment Variable: `MAS_BACKUP_DIR`
- Default: None

#### suite_backup_version

The version of the backup file located in the `MAS_BACKUP_DIR` to be used in the restore — for example `20260116-130937`.

- **Required**
- Environment Variable: `SUITE_BACKUP_VERSION`
- Default: None

### Domain Override

#### mas_domain

The domain to use for the MAS Suite instance — for example `mydomain.example.com`.

- **Optional**
- Environment Variable: `MAS_DOMAIN`
- Default: `NO_OVERRIDE` (uses value from backup)

Use to change the domain when restoring to a different cluster; when not provided, the domain from the backup is used.

### SLS Configuration

#### include_sls_from_backup

Controls whether to restore the Suite SLS (Suite License Service) configuration from the backup archive.

- **Optional**
- Environment Variable: `INCLUDE_SLS_FROM_BACKUP`
- Default: `true`

Set to `true` when the registration key stays the same, either because the same SLS service is also being restored or because you are using a centralized SLS service that has not changed. If you plan to install and use a new SLS service, set this to `false` and use the `sls_cfg_file` variable to point to the new SLS configuration file.

#### sls_url

The URL for the Suite License Service (SLS) — for example `https://sls.example.com`. Only applies when `include_sls_from_backup` is `true`.

- **Optional**
- Environment Variable: `SLS_URL`
- Default: `NO_OVERRIDE` (uses value from backup)

Use when the domain has changed for SLS but SLS was restored from a backup, so the registration key is the same.

#### sls_cfg_file

Path to the file containing an external SLS configuration YAML file to apply — for example `/tmp/sls_config/sls.yml`. Only applies when `include_sls_from_backup` is `false`.

- **Required** when `include_sls_from_backup` is `false`
- Environment Variable: `SLS_CFG_FILE`
- Default: None

Use SLS configuration from outside the backup archive (e.g., from a separate SLS role execution).

### DRO (BAS) Configuration

#### include_dro_from_backup

Controls whether to restore the Suite DRO configuration from the backup archive.

- **Optional**
- Environment Variable: `INCLUDE_DRO_FROM_BACKUP`
- Default: `true`

Set to `true` when the DRO details stay the same and you are using a centralized DRO service that has not changed. If you plan to install and use a new DRO service, set this to `false` and use the `dro_cfg_file` variable to point to the new DRO configuration file.

#### bas_url

The URL for the Behavior Analytics Service (BAS) — for example `https://bas.example.com`. Only applies when `include_dro_from_backup` is `true`.

- **Optional**
- Environment Variable: `BAS_URL`
- Default: `NO_OVERRIDE` (uses value from backup)

Use when the domain has changed for DRO but DRO was restored from a backup, so the API key is the same.

#### dro_cfg_file

Path to the file containing an external DRO (BAS) configuration YAML file to apply — for example `/tmp/dro_config/dro.yml`. Only applies when `include_dro_from_backup` is `false`.

- **Required** when `include_dro_from_backup` is `false`
- Environment Variable: `DRO_CFG_FILE`
- Default: None

Use DRO configuration from outside the backup archive (e.g., from a separate DRO role execution).

## Restore Operations

This section provides comprehensive information about MAS Core restore operations.

### Overview

The MAS Core restore operation performs a complete restoration of a MAS Core installation from a backup created by the [`suite_backup`](suite_backup.md) role. The restore process recreates all namespace resources and supporting resources in the correct order.

**Important**: Restore can only be made to an instance with the same MAS instance ID as the backup.

### Restore Process

The MAS Core restore operation performs the following steps in sequence:

1. **Validation**: Verifies required variables and backup archive existence
2. **Certificate Manager Check**: Ensures cert-manager is installed in the cluster
3. **Projects Restoration**: Restores the MAS Core namespace
4. **Secrets and ConfigMaps**: Restores all secrets and configuration maps
5. **Operator Resources**: Restores OperatorGroups and Subscriptions
6. **Subscription Wait**: Waits for subscriptions to be ready (up to 30 minutes)
7. **Certificate Manager Resources**: Restores ClusterIssuers, Issuers, and Certificates
8. **MAS Addon Resources**: Restores MVIEdge, ReplicaDB, and GenericAddon resources
9. **MAS Configuration Resources**: Restores all config.mas.ibm.com resources with optional overrides:
   - BasCfg (if `include_dro_from_backup` is true, with optional `bas_url` override)
   - SlsCfg (if `include_sls_from_backup` is true, with optional `sls_url` override)
   - AppCfg, IDPCfg, JdbcCfg, KafkaCfg, MongoCfg, ObjectStorageCfg, etc.
10. **MAS Internal Resources**: Restores CoreIDP resources
11. **Suite Restoration**: Restores the Suite CR with optional `mas_domain` override
12. **Suite Wait**: Waits for Suite to be ready (up to 60 minutes)
13. **Workspace Restoration**: Restores all Workspace CRs
14. **Workspace Wait**: Waits for all Workspaces to be ready (up to 60 minutes)

### Configuration Override Options

The restore process supports several override options to adapt the backup to a new environment:

**Domain Override:**

- Use `mas_domain` to change the domain when restoring to a different cluster
- Default: Uses the domain from the backup

**SLS Configuration:**

- If `include_sls_from_backup=true`: Restores SlsCfg from backup
  - Use `sls_url` to override the SLS URL if the domain changed
- If `include_sls_from_backup=false`: Use `sls_cfg_file` to provide external SLS configuration

**DRO Configuration:**

- If `include_dro_from_backup=true`: Restores BasCfg from backup
  - Use `bas_url` to override the BAS URL if the domain changed
- If `include_dro_from_backup=false`: Use `dro_cfg_file` to provide external DRO configuration

### When to Use

**Full Restore Scenarios:**

- Disaster recovery after cluster failure
- Migrating MAS Core to a new cluster
- Recreating a deleted MAS Core instance
- Setting up a new environment from backup
- Testing backup integrity in non-production

**Partial Configuration Scenarios:**

- Restoring with new SLS service (set `include_sls_from_backup=false`)
- Restoring with new DRO service (set `include_dro_from_backup=false`)
- Restoring to cluster with different domain (use `mas_domain` override)

### Important Considerations

**Prerequisites:**

- Target cluster must have Certificate Manager installed
- Target cluster must have the same MAS instance ID as the backup
- **Required** dependencies (MongoDB, Db2, etc.) must be available and accessible
- Sufficient cluster resources (CPU, memory, storage) must be available

**Instance ID Requirement:**

- Restore can only be made to an instance with the same MAS instance ID
- The instance ID is embedded in resource names and cannot be changed

**Storage Requirements:**

- Ensure backup directory is accessible from the restore environment
- Verify backup archive integrity before starting restore

**Security:**

- Backup files contain sensitive data including credentials and certificates
- Ensure secure transfer of backup files to restore environment
- Verify backup file permissions and access controls

**Configuration Dependencies:**

- If using external SLS/DRO configuration files, ensure they are valid and accessible
- Coordinate with database restore operations to ensure data consistency
- Verify network connectivity to external services (SLS, DRO, databases)

### Restore Best Practices

1. **Pre-Restore Validation**:
   - Verify backup archive exists and is complete
   - Confirm Certificate Manager is installed
   - Ensure target cluster has sufficient resources
   - Verify MAS instance ID matches the backup

2. **Dependency Coordination**:
   - Restore databases (MongoDB, Db2) before MAS Core
   - Restore SLS before MAS Core if using separate SLS
   - Restore DRO before MAS Core if using separate DRO
   - Ensure all external services are accessible

3. **Configuration Planning**:
   - Determine if domain override is needed
   - Decide whether to use backup SLS/DRO or new services
   - Prepare external configuration files if needed
   - Document any configuration changes

4. **Post-Restore Verification**:
   - Verify Suite status is Ready
   - Verify all Workspaces are Ready
   - Test application connectivity
   - Verify database connections
   - Test user authentication

5. **Disaster Recovery**:
   - Test restore procedures regularly in non-production
   - Document restore procedures and configuration
   - Maintain backup version identifiers
   - Keep external configuration files secure and accessible

## Example Playbook

After installing the Ansible Collection you can include this role in your own custom playbooks.

```yaml
- hosts: localhost
  vars:
    mas_instance_id: "{{ lookup('env', 'MAS_INSTANCE_ID') }}"
    mas_backup_dir: /tmp/mas_backups
    suite_backup_version: 20260116-130937
  roles:
    - ibm.mas_devops.suite_restore
```

## License

EPL-2.0
