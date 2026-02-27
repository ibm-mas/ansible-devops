# suite_upgrade

This role validates if a given MAS installation is ready for the core platform to be upgraded to a specific subscription channel, and (as long as dry run mode is not enabled) will execute the upgrade.

- It will validate that the current subscription channel is able to be upgraded to the target channel.
- It will validate that all installed applications have already been upgraded to versions compatible with the new version of the Core Platform.
- It will upgrade the MAS core platform to the desired channel (as long as dry run is not enabled).
- It will validate that the core platform has been successfully reconciled at the upgraded version.
- It will **not** validate that all core services successfully deploy after the reconcile (but we will be working on this limitation).

## Role Variables

### mas_instance_id
MAS instance identifier for core platform upgrade.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

**Purpose**: Identifies which MAS instance's core platform to upgrade. Used to locate and validate the MAS installation.

**When to use**:
- Always required for MAS core platform upgrades
- Must match the instance ID from MAS installation
- Used to validate upgrade readiness and application compatibility

**Valid values**: Lowercase alphanumeric string, 3-12 characters (e.g., `prod`, `dev`, `inst1`)

**Impact**: Determines which MAS instance will be upgraded. Incorrect instance ID will cause upgrade to fail.

**Related variables**:
- `mas_channel`: Target upgrade channel for this instance

**Note**: The role validates that all installed applications are compatible with the target MAS version before proceeding with the upgrade.

### mas_channel
Target subscription channel for MAS core platform upgrade.

- **Optional**
- Environment Variable: `MAS_CHANNEL`
- Default: Auto-selected based on current version

**Purpose**: Specifies the target subscription channel for MAS core platform upgrade. If not provided, the role automatically selects the next appropriate version.

**When to use**:
- Leave unset for automatic upgrade to next release
- Set explicitly when you need a specific target version
- Must be a valid upgrade path from current version

**Valid values**: Valid MAS subscription channel (e.g., `8.8.x`, `8.9.x`, `8.10.x`, `8.11.x`)

**Impact**: Determines the target version for MAS core platform upgrade. The role validates:
- Upgrade path compatibility (can upgrade from current to target)
- Application compatibility (all apps support target MAS version)
- If validation fails, no upgrade is performed

**Related variables**:
- `mas_instance_id`: Instance being upgraded
- `skip_compatibility_check`: Whether to skip validation (not recommended)

**Note**: When unset, the role automatically selects the next release. If already on the latest release, no action is taken. The role validates that all installed applications are compatible with the target MAS version before upgrading.

### mas_upgrade_dryrun
Dry-run mode for upgrade validation only.

- **Optional**
- Environment Variable: `MAS_UPGRADE_DRYRUN`
- Default: `false`

**Purpose**: Enables dry-run mode where the role performs all validation checks without making any changes to the MAS installation. Useful for testing upgrade paths.

**When to use**:
- Set to `true` to validate upgrade without executing it
- Use for testing and planning upgrade paths
- Recommended before production upgrades
- Leave as `false` (default) to perform actual upgrade

**Valid values**: `true`, `false`

**Impact**: 
- `true`: Performs validation only (upgrade path check, application compatibility check) without modifying the installation
- `false`: Performs validation and executes the upgrade if validation passes

**Related variables**:
- `skip_compatibility_check`: Controls whether compatibility validation is performed

**Note**: Dry-run mode is highly recommended before production upgrades to identify potential issues. All validation checks are performed, including application compatibility, but no changes are made to the subscription channel or MAS core platform.

### skip_compatibility_check
Skip compatibility validation before upgrade.

- **Optional**
- Environment Variable: `SKIP_COMPATIBILITY_CHECK`
- Default: `false`

**Purpose**: Controls whether compatibility validation is performed before MAS core platform upgrade. Validation checks if the target channel is compatible with current MAS version and all installed applications.

**When to use**:
- Leave as `false` (default) for safe upgrades with validation
- Set to `true` only in exceptional cases (not recommended)
- Use only when you have verified compatibility manually

**Valid values**: `true`, `false`

**Impact**: 
- `false` (default): Performs comprehensive compatibility validation before upgrade (recommended)
- `true`: Skips compatibility validation, allowing potentially incompatible upgrades

**Related variables**:
- `mas_upgrade_dryrun`: Controls whether upgrade is executed or only validated
- `mas_channel`: Target channel being validated

**Note**: **WARNING** - Skipping compatibility checks can lead to failed upgrades, application incompatibilities, or unstable installations. Only skip validation if you have manually verified that:
1. The upgrade path from current to target MAS version is supported
2. All installed applications are compatible with the target MAS version
The default validation protects against incompatible upgrades and application version mismatches.

## Example Playbook

### Automatic Target Selection
Running this playbook will upgrade MAS to the next release. If you run this playbook when you are already on the latest release then it will take no action.

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: instance1
    mas_upgrade_dryrun: False
  roles:
    - ibm.mas_devops.suite_upgrade
```

### Explicit Upgrade Target
Running this playbook will attempt to upgrade MAS to the specified release. If the specified release cannot be upgraded to from the installed version of MAS then no action will be taken.

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: instance1
    mas_channel: 8.8.x
    mas_upgrade_dryrun: False
  roles:
    - ibm.mas_devops.suite_upgrade
```

## License

EPL-2.0
