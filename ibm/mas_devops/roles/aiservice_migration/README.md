# aiservice_migration
This role performs necessary migration tasks when AI Service is upgraded from one version to another. The role will detect whether or not a migration is required and perform the migration if necessary. If a migration has been performed, the fact `is_migration_needed` will be set to `true`. The table below shows
which upgrade paths are currently included for migration.


| Installed Version | Target Version | Migration Steps |
|---|---|---|
| 9.1 | 9.2 | Remove the cluster-scoped tenant operator and install the namespace-scoped tenant operator in each tenant namespace. Move dependent resources. Clean-up. |



## Role Variables

### instance_id
AI Service instance identifier to upgrade.

- **Required**
- Environment Variable: `AISERVICE_INSTANCE_ID`
- Default: None

**Purpose**: Identifies the target AI Service instance for upgrade operations.

**When to use**: Always required. Must match an existing AI Service instance ID.

**Valid values**: Valid AI Service instance ID (typically lowercase alphanumeric)

**Impact**: Determines which AI Service instance will be migrated. Incorrect instance ID will cause the upgrade to fail.

**Notes**:
- Must match the instance ID from AI Service installation
- Verify instance exists before upgrading
- Case-sensitive value

### catalog_channel
The subscription channel from which components such as the AI Service tenant operator will be installed during the migration. This should match the channel used to install AI Service.

- Environment Variable: `AISERVICE_CHANNEL`
- Default: None

**Purpose**: Specifies the target subscription channel to install AI Service components during the migration. If not provided, the role automatically selects the next appropriate version.

**When to use**:
- Must be set explicitly.
- Must be a valid upgrade path from current version

**Valid values**: Valid AI Service subscription channel (e.g., `9.0.x`, `9.1.x`)

**Impact**: Determines the target version for AI Service migration. The role validates:
- Upgrade path compatibility (can upgrade from current to target)

### force_migration
Skip any checks to determine if a migration is needed and perform the migration

- Environment Variable: `AISERVICE_FORCE_MIGRATION`
- Default: false

**Purpose**: If set to true, the migration will be performed regardless of whether a migration is needed.

**When to use**:
- When you want to force a migration due to an error occurring during the migration process

**Valid values**: True or false

**Impact**: Forces a migration to happen. Use this option only when you are sure that a migration is needed. This may break your environment if used incorrectly.

## License

EPL-2.0
