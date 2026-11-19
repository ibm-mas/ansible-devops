# suite_upgrade

This role validates if a given MAS installation is ready for the core platform to be upgraded to a specific subscription channel, and (as long as dry run mode is not enabled) will execute the upgrade.

- It will validate that the current subscription channel is able to be upgraded to the target channel.
- It will validate that all installed applications have already been upgraded to versions compatible with the new version of the Core Platform.
- It will upgrade the MAS core platform to the desired channel (as long as dry run is not enabled).
- It will validate that the core platform has been successfully reconciled at the upgraded version.
- It will **not** validate that all core services successfully deploy after the reconcile (but we will be working on this limitation).

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`mas_instance_id`](#mas_instance_id) | Yes | None |
| [`mas_channel`](#mas_channel) | No | Auto-selected |
| [`mas_upgrade_dryrun`](#mas_upgrade_dryrun) | No | `false` |
| [`skip_compatibility_check`](#skip_compatibility_check) | No | `false` |

### Upgrade Target

#### mas_instance_id
MAS instance identifier whose core platform will be upgraded — a lowercase alphanumeric string, 3-12 characters (e.g. `prod`, `dev`, `inst1`), matching the instance ID from the MAS installation.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

The role uses this to locate the installation and validate upgrade readiness and application compatibility; an incorrect instance ID will cause the upgrade to fail.

#### mas_channel
Target subscription channel for the MAS core platform upgrade — a valid MAS subscription channel such as `8.8.x`, `8.9.x`, `8.10.x`, or `8.11.x`.

- **Optional**
- Environment Variable: `MAS_CHANNEL`
- Default: Auto-selected based on current version (the next appropriate release)

When unset, the role automatically selects the next release; if already on the latest release, no action is taken. Set it explicitly when you need a specific target version — the role validates that a supported upgrade path exists from the current version and that all installed applications are compatible with the target MAS version, and no upgrade is performed if validation fails.

### Upgrade Validation

#### mas_upgrade_dryrun
Dry-run mode, which performs all validation checks (upgrade path check, application compatibility check) without making any changes to the MAS installation — `true` or `false`.

- **Optional**
- Environment Variable: `MAS_UPGRADE_DRYRUN`
- Default: `false`

When `false`, validation runs and the upgrade is executed if validation passes. Dry-run mode is highly recommended before production upgrades to identify potential issues while testing and planning upgrade paths.

#### skip_compatibility_check
Whether to skip the compatibility validation that checks the target channel against the current MAS version and all installed applications — `true` or `false`.

- **Optional**
- Environment Variable: `SKIP_COMPATIBILITY_CHECK`
- Default: `false`

!!! warning
    Skipping compatibility checks can lead to failed upgrades, application incompatibilities, or unstable installations. Only set this to `true` in exceptional cases where you have manually verified that the upgrade path from the current to the target MAS version is supported **and** that all installed applications are compatible with the target MAS version — the default validation protects against incompatible upgrades and application version mismatches.

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
