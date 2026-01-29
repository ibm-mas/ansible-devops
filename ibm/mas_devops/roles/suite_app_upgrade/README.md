# suite_app_upgrade

This role will upgrade the subscription channel for an installed MAS application after validating:

- That the application is installed and in a healthy state
- That the new version of the application can be upgraded to from the existing version
- That the new version of the application is compatible with the running MAS core platform

## Role Variables

### mas_instance_id
MAS instance identifier for application upgrade.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

**Purpose**: Identifies which MAS instance contains the application to upgrade. Used to locate and validate the application installation.

**When to use**:
- Always required for application upgrades
- Must match the instance ID from MAS installation
- Used to validate application health before upgrade

**Valid values**: Lowercase alphanumeric string, 3-12 characters (e.g., `prod`, `dev`, `inst1`)

**Impact**: Determines which MAS instance's application will be upgraded. Incorrect instance ID will cause upgrade to fail.

**Related variables**:
- `mas_app_id`: Application to upgrade in this instance
- `mas_app_channel`: Target upgrade channel

**Note**: The role validates that the application is installed and healthy in this instance before proceeding with the upgrade.

### mas_app_id
MAS application identifier to upgrade.

- **Required**
- Environment Variable: `MAS_APP_ID`
- Default: None

**Purpose**: Specifies which MAS application to upgrade. The role validates the application is installed and healthy before upgrading.

**When to use**:
- Always required for application upgrades
- Must match an installed application in the instance
- Application must be in healthy state for upgrade

**Valid values**: Valid MAS application ID (e.g., `iot`, `manage`, `monitor`, `predict`, `health`, `assist`, `visualinspection`, `optimizer`)

**Impact**: Determines which application's subscription channel will be upgraded. The role validates compatibility and upgrade path before proceeding.

**Related variables**:
- `mas_instance_id`: Instance containing this application
- `mas_app_channel`: Target upgrade channel for this application

**Note**: The role performs comprehensive validation including application health, upgrade path compatibility, and MAS core platform compatibility before upgrading.

### mas_app_channel
Target subscription channel for application upgrade.

- **Required**
- Environment Variable: `MAS_APP_CHANNEL`
- Default: None

**Purpose**: Specifies the target subscription channel to upgrade the application to. The role validates that a supported upgrade path exists from the current version.

**When to use**:
- Always required for application upgrades
- Must be a valid channel for the application
- Should represent a newer version than currently installed

**Valid values**: Valid subscription channel for the application (e.g., `8.5.x`, `8.6.x`, `8.7.x` for IoT; `8.4.x`, `8.5.x`, `8.6.x` for Manage)

**Impact**: Determines the target version for the application upgrade. The role validates:
- Upgrade path compatibility (can upgrade from current to target)
- MAS core platform compatibility (target version works with current MAS)
- Application health before proceeding

**Related variables**:
- `mas_app_id`: Application being upgraded
- `skip_compatibility_check`: Whether to skip validation (not recommended)

**Note**: Built-in validation ensures safe upgrades. The role will fail if the upgrade path is not supported or if the target version is incompatible with the current MAS core platform.

### mas_upgrade_dryrun
Dry-run mode for upgrade validation only.

- **Optional**
- Environment Variable: `MAS_UPGRADE_DRYRUN`
- Default: `false`

**Purpose**: Enables dry-run mode where the role performs all validation checks without making any changes to the installation. Useful for testing upgrade paths.

**When to use**:
- Set to `true` to validate upgrade without executing it
- Use for testing and planning upgrade paths
- Recommended before production upgrades
- Leave as `false` (default) to perform actual upgrade

**Valid values**: `true`, `false`

**Impact**: 
- `true`: Performs validation only (health check, compatibility check, upgrade path validation) without modifying the installation
- `false`: Performs validation and executes the upgrade if validation passes

**Related variables**:
- `skip_compatibility_check`: Controls whether compatibility validation is performed

**Note**: Dry-run mode is highly recommended before production upgrades to identify potential issues. All validation checks are performed, but no changes are made to the subscription channel or application.

### skip_compatibility_check
Skip compatibility validation before upgrade.

- **Optional**
- Environment Variable: `SKIP_COMPATIBILITY_CHECK`
- Default: `false`

**Purpose**: Controls whether compatibility validation is performed before upgrade. Validation checks if the target channel is compatible with current MAS and application versions.

**When to use**:
- Leave as `false` (default) for safe upgrades with validation
- Set to `true` only in exceptional cases (not recommended)
- Use only when you have verified compatibility manually

**Valid values**: `true`, `false`

**Impact**: 
- `false` (default): Performs compatibility validation before upgrade (recommended)
- `true`: Skips compatibility validation, allowing potentially incompatible upgrades

**Related variables**:
- `mas_upgrade_dryrun`: Controls whether upgrade is executed or only validated
- `mas_app_channel`: Target channel being validated

**Note**: **WARNING** - Skipping compatibility checks can lead to failed upgrades or unstable installations. Only skip validation if you have manually verified the upgrade path is supported. The default validation protects against incompatible upgrades.

## Example Playbook

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: instance1
    mas_app_id: iot
    mas_app_channel: 8.5.x
  roles:
    - ibm.mas_devops.suite_app_upgrade
```

## License

EPL-2.0
