aiservice_upgrade
===============================================================================
This role validates if a given AI SERVICE installation is ready to be upgraded to a specific subscription channel, and (as long as dry run mode is not enabled) will execute the upgrade.

- It will validate that the current subscription channel is able to be upgraded to the target channel.
- It will upgrade the AI SERVICE to the desired channel (as long as dry run is not enabled).
- It will validate that the AI Service has been successfully reconciled at the upgraded version.
- It will **not** validate that all AI Service services successfully deploy after the reconcile (but we will be working on this limitation).


Role Variables
-------------------------------------------------------------------------------

### aiservice_instance_id
AI Service instance identifier to upgrade.

- **Required**
- Environment Variable: `AISERVICE_INSTANCE_ID`
- Default: None

**Purpose**: Identifies the target AI Service instance for upgrade operations.

**When to use**: Always required. Must match an existing AI Service instance ID.

**Valid values**: Valid AI Service instance ID (typically lowercase alphanumeric)

**Impact**: Determines which AI Service instance will be upgraded. Incorrect instance ID will cause the upgrade to fail.

**Related variables**: [`aiservice_channel`](#aiservice_channel)

**Notes**:
- Must match the instance ID from AI Service installation
- Verify instance exists before upgrading
- Case-sensitive value

### aiservice_channel
Target subscription channel for AI Service upgrade.

- Optional
- Environment Variable: `AISERVICE_CHANNEL`
- Default: None (auto-selected)

**Purpose**: Specifies the target subscription channel to upgrade AI Service to. If not provided, the role automatically selects the next appropriate version.

**When to use**:
- Leave unset for automatic upgrade to next release
- Set explicitly when you need a specific target version
- Must be a valid upgrade path from current version

**Valid values**: Valid AI Service subscription channel (e.g., `9.0.x`, `9.1.x`)

**Impact**: Determines the target version for AI Service upgrade. The role validates:
- Upgrade path compatibility (can upgrade from current to target)
- If validation fails, no upgrade is performed

**Related variables**: [`aiservice_instance_id`](#aiservice_instance_id), [`aiservice_upgrade_dryrun`](#aiservice_upgrade_dryrun)

**Notes**:
- When unset, the role automatically selects the next release
- If already on the latest release, no action is taken
- Review release notes before changing channels
- Channel changes may trigger operator restarts

### aiservice_upgrade_dryrun
Enable dry run mode for upgrade validation only.

- Optional
- Environment Variable: `AISERVICE_UPGRADE_DRYRUN`
- Default: `false`

**Purpose**: When enabled, performs all validation checks for upgrade compatibility without making any actual changes to the AI Service installation.

**When to use**:
- Set to `true` to validate upgrade without executing it
- Use for testing and planning upgrade paths
- Recommended before production upgrades
- Leave as `false` (default) to perform actual upgrade

**Valid values**: `true`, `false`

**Impact**:
- `true`: Validates upgrade compatibility but makes no changes (safe)
- `false`: Performs validation and executes the upgrade if validation passes (default)

**Related variables**: [`aiservice_channel`](#aiservice_channel)

**Notes**:
- Dry-run mode is highly recommended before production upgrades to identify potential issues
- All validation checks are performed, but no changes are made to the subscription channel or AI Service
- Helps ensure upgrade feasibility before committing to the operation

Example Playbook
-------------------------------------------------------------------------------
### Automatic Target Selection
Running this playbook will upgrade AI Service to the next release.  If you run this playbook when you are already on the latest release then it will take no action.

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    aiservice_instance_id: instance1
    aiservice_upgrade_dryrun: False
  roles:
    - ibm.mas_devops.aiservice_upgrade
```

### Explicit Upgrade Target
Running this playbook will attempt to upgrade AI Service to the specified release.  If the specified release cannot be upgraded to from the installed version of AI Service then no action will be taken.
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    aiservice_instance_id: instance1
    aiservice_channel: 9.1.x
    aiservice_upgrade_dryrun: False
  roles:
    - ibm.mas_devops.aiservice_upgrade
```
