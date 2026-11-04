Backup MAS Core
===============================================================================

Overview
-------------------------------------------------------------------------------
This role supports backing up MAS Core namespace resources and supporting resources
in other namespaces; supports creating on-demand full backups.

!!! important

    Supported only for MAS 9.1.x.

    Backup can only be restored to an instance with the same MAS instance ID.


Role Variables
-------------------------------------------------------------------------------

### mas_instance_id
The instance ID of the Maximo Application Suite installation to backup.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### mas_backup_dir
The local directory path where backup files will be stored (for backup).

- **Required**
- Environment Variable: `MAS_BACKUP_DIR`
- Default: None
- Example: `/tmp/mas_backups`

### suite_backup_version
Set version to override the default `YYYYMMDD-HHMMSS` timestamp version used in the name of the backup file.

- **Optional**
- Default: `YYYYMMDD-HHMMSS` timestamp.
- Environment Variable: `SUITE_BACKUP_VERSION`

### include_sls
Controls whether to include the Suite SLS (Suite License Service) configuration in the backup archive.
If you plan to install a new SLS in any recovery action then you should set this to `false`.

- **Optional**
- Default: `true`
- Environment Variable: `INCLUDE_SLS`

### include_dro
Controls whether to include the Suite DRO configuration in the backup archive. 
If you plan to install a new DRO in any recovery action then you should set this to `false`.

- **Optional**
- Default: `true`
- Environment Variable: `INCLUDE_DRO`

### mas_workspace_id
The workspace ID of the Maximo Application Suite installation to include in strict named-only backup (for backing up Workspace and wsapp JdbcCfg CRs).

- **Optional**
- Default: None
- Environment Variable: `MAS_WORKSPACE_ID`

### strict_named_only
Enforce strict named-only backup mode (fails if any resource definition lacks an explicit name, preventing unnamed namespace-wide queries).
In strict mode `mas_workspace_id` is required, Secret auto-discovery is forced off, and the backup fails with a clear error if the installed `mas-devops` library does not support strict behavior (it never falls back to broad queries). Explicitly named CRDs (`suite_backup_crds`) and ConfigMaps are included.

- **Optional**
- Default: `false`
- Environment Variable: `STRICT_NAMED_ONLY`

### include_ca_keys
Opt-in for exporting CA key-pair Secrets (`tls.key`/`tls.crt`). Never exported by default. Setting this to `true` currently fails the role, because no backup-encryption mechanism has been approved to store CA private keys (MASCORE-20742).

- **Optional**
- Default: `false`
- Environment Variable: `INCLUDE_CA_KEYS`

### saas_envs_instance_dir / gitops_envs_instance_dir
Explicit environment-configuration folders copied into `<backup>/environment/` with owner-only permissions, plus an `ENVIRONMENT_SNAPSHOT.yaml` manifest. Leave `GITOPS_ENVS_INSTANCE_DIR` empty when no matching gitops-envs folder exists; the manifest records `no_matching_folder`.

- **Optional**
- Environment Variables: `SAAS_ENVS_INSTANCE_DIR`, `GITOPS_ENVS_INSTANCE_DIR`

### auto_discover_secrets
Controls whether secret references found in custom resource specs are automatically discovered and backed up.

- **Optional**
- Default: `true`
- Environment Variable: `AUTO_DISCOVER_SECRETS`


## Backup Operations
-------------------------------------------------------------------------------

This section provides comprehensive information about MAS Core backup operations.

### Overview

The MAS Core backup operation creates a comprehensive backup of your MAS Core installation, including all namespace resources and supporting resources in other namespaces. This backup can be restored using the [`suite_restore`](suite_restore.md) role.

**Important**: Backup can only be restored to an instance with the same MAS instance ID.

### What Gets Backed Up

The MAS Core backup operation captures all critical resources needed to restore a complete MAS Core instance:

**Core Namespace Resources (`mas-{instance-id}-core`):**
- **Projects/Namespaces**: The MAS Core namespace
- **Secrets**:
  - Superuser credentials (`{instance-id}-credentials-superuser`)
  - IBM entitlement key (`ibm-entitlement`)
  - Public certificates (`{instance-id}-cert-public`)
  - All auto-discovered secrets referenced by other resources
- **Operator Resources**:
  - Subscription (`ibm-mas`)
  - OperatorGroup
- **Certificate Manager Resources**:
  - Certificates (with label `mas.ibm.com/instanceId={instance-id}`)
- **MAS Addon Resources** (addons.mas.ibm.com):
  - MVIEdge
  - ReplicaDB
  - GenericAddon
- **MAS Core Resources** (core.mas.ibm.com):
  - Suite CR
  - Workspace CRs
- **MAS Internal Resources** (internal.mas.ibm.com):
  - CoreIDP
- **MAS Configuration Resources** (config.mas.ibm.com):
  - AppCfg, IDPCfg, JdbcCfg, KafkaCfg, McpiCfg, MongoCfg
  - ObjectStorageCfg, PushNotificationCfg, ScimCfg
  - SmtpCfg, WatsonStudioCfg
  - BasCfg (if `include_dro` is true)
  - SlsCfg (if `include_sls` is true)

**Certificate Manager Resources:**
- **ClusterIssuers**:
  - Public cluster issuer (detected automatically)
  - `mas-{instance-id}-core-internal-issuer`
  - `mas-{instance-id}-ca`
- **Issuers** (in cert-manager namespace):
  - `mas-{instance-id}-core-internal-ca-issuer`
  - `mas-{instance-id}-core-public-ca-issuer`
- **Certificates** (in cert-manager namespace):
  - `{instance-id}-cert-internal-ca`
  - `{instance-id}-cert-public-ca`

### Backup Process

The MAS Core backup operation performs the following steps:

1. **Validation**: Verifies required variables (`mas_instance_id`, `mas_backup_dir`)
2. **Version Generation**: Creates or uses provided backup version identifier
3. **Certificate Manager Detection**: Detects the Certificate Manager installation and namespace
4. **Cluster Issuer Detection**: Identifies the public cluster issuer in use
5. **Resource Discovery**: Identifies all MAS Core resources and auto-discovers referenced secrets
6. **Backup Execution**: Exports all resources to YAML files in the backup directory
7. **Verification**: Reports backup statistics and any failures

**Backup Directory Structure:**
```
{mas_backup_dir}/
└── backup-{version}-suite/
    └── resources/
        ├── projects/
        ├── secrets/
        ├── configmaps/
        ├── subscriptions/
        ├── operatorgroups/
        ├── clusterissuers/
        ├── issuers/
        ├── certificates/
        ├── mviedges/
        ├── replicadbs/
        ├── genericaddons/
        ├── suites/
        ├── workspaces/
        ├── coreidps/
        ├── appcfgs/
        ├── idpcfgs/
        ├── jdbccfgs/
        ├── kafkacfgs/
        ├── mcpicfgs/
        ├── mongocfgs/
        ├── objectstoragecfgs/
        ├── pushnotificationcfgs/
        ├── scimcfgs/
        ├── smtpcfgs/
        ├── watsonstudiocfgs/
        ├── bascfgs/ (if include_dro is true)
        └── slscfgs/ (if include_sls is true)
```

### Important Considerations

**Instance ID Requirement:**
- Backup can only be restored to an instance with the same MAS instance ID
- The instance ID is embedded in resource names and cannot be changed during restore

**Storage Requirements:**
- Ensure sufficient storage in the backup directory
- Backup directory structure: `{mas_backup_dir}/backup-{version}-suite/`
- Monitor disk space during backup operations

**Security:**
- Backup files contain sensitive data including credentials and certificates
- Secure backup directory with appropriate permissions (chmod 700 recommended)
- Consider encrypting backups for long-term storage
- Restrict access to backup files to authorized personnel only

**SLS and DRO Configuration:**
- Use `include_sls=false` if you plan to install a new SLS during recovery
- Use `include_dro=false` if you plan to install a new DRO during recovery
- Default is `true` for both, which includes the configuration in the backup

### Backup Best Practices

1. **Regular Backups**: Schedule automated backups at regular intervals, especially before:
   - MAS upgrades
   - Configuration changes
   - Application installations
   - Cluster maintenance
2. **Test Restores**: Periodically test restore procedures in non-production environments
3. **Monitor Operations**: Implement monitoring and alerting for backup failures
4. **Backup Validation**: Verify backup integrity after completion
5. **Retention Policy**: Implement and document backup retention policies
6. **Disaster Recovery**: Include MAS Core backup/restore in your DR plan
7. **Coordinate Backups**: Coordinate MAS Core backups with:
   - Database backups (MongoDB, Db2)
   - SLS backups (if using separate SLS)
   - DRO backups (if using separate DRO)
   - Application-specific backups

