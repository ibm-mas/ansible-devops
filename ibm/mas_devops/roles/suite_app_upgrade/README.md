# suite_app_upgrade

This role will upgrade the subscription channel for an installed MAS application after validating:

- That the application is installed and in a healthy state
- That the new version of the application can be upgraded to from the existing version
- That the new version of the application is compatible with the running MAS core platform

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`mas_instance_id`](#mas_instance_id) | Yes | None |
| [`mas_app_id`](#mas_app_id) | Yes | None |
| [`mas_app_channel`](#mas_app_channel) | Yes | None |
| [`mas_upgrade_dryrun`](#mas_upgrade_dryrun) | No | `false` |
| [`skip_compatibility_check`](#skip_compatibility_check) | No | `false` |

### Upgrade Target

#### mas_instance_id
MAS instance identifier containing the application to upgrade — a lowercase alphanumeric string, 3-12 characters (e.g. `prod`, `dev`, `inst1`), matching the instance ID from the MAS installation.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

The role uses this to locate the application installation and validate that the application is installed and healthy in the instance before proceeding with the upgrade; an incorrect instance ID will cause the upgrade to fail.

#### mas_app_id
MAS application identifier to upgrade — a valid MAS application ID such as `iot`, `manage`, `monitor`, `predict`, `health`, `assist`, `visualinspection`, or `optimizer`.

- **Required**
- Environment Variable: `MAS_APP_ID`
- Default: None

Must match an installed application in the instance, in a healthy state. The role performs comprehensive validation — application health, upgrade path compatibility, and MAS core platform compatibility — before upgrading the application's subscription channel.

#### mas_app_channel
Target subscription channel for the application upgrade — a valid channel for the application representing a newer version than currently installed (e.g. `8.5.x`, `8.6.x`, `8.7.x` for IoT; `8.4.x`, `8.5.x`, `8.6.x` for Manage).

- **Required**
- Environment Variable: `MAS_APP_CHANNEL`
- Default: None

Before upgrading, the role validates that a supported upgrade path exists from the current version and that the target version is compatible with the running MAS core platform. The role will fail if the upgrade path is not supported or the target version is incompatible.

### Upgrade Validation

#### mas_upgrade_dryrun
Dry-run mode, which performs all validation checks (health check, compatibility check, upgrade path validation) without making any changes to the installation — `true` or `false`.

- **Optional**
- Environment Variable: `MAS_UPGRADE_DRYRUN`
- Default: `false`

When `false`, validation runs and the upgrade is executed if validation passes. Dry-run mode is highly recommended before production upgrades to identify potential issues while testing and planning upgrade paths.

#### skip_compatibility_check
Whether to skip the compatibility validation that checks the target channel against the current MAS and application versions — `true` or `false`.

- **Optional**
- Environment Variable: `SKIP_COMPATIBILITY_CHECK`
- Default: `false`

!!! warning
    Skipping compatibility checks can lead to failed upgrades or unstable installations. Only set this to `true` in exceptional cases where you have manually verified that the upgrade path is supported — the default validation protects against incompatible upgrades.

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
