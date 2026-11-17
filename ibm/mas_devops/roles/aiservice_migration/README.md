# aiservice_migration

This role performs necessary migration tasks when AI Service is upgraded from one version to another. The role will detect whether or not a migration is required and perform the migration if necessary. If a migration has been performed, the fact `is_migration_needed` will be set to `true`. The table below shows which upgrade paths are currently included for migration.

| Installed Version | Target Version | Migration Steps |
|---|---|---|
| 9.1 | 9.2 | Remove the cluster-scoped tenant operator and install the namespace-scoped tenant operator in each tenant namespace. Move dependent resources. Clean-up. |

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`instance_id`](#instance_id) | Yes | None |
| [`catalog_channel`](#catalog_channel) | No | None |
| [`force_migration`](#force_migration) | No | `false` |

### Migration Target

#### instance_id

AI Service instance identifier to upgrade (typically lowercase alphanumeric; case-sensitive).

- **Required**
- Environment Variable: `AISERVICE_INSTANCE_ID`
- Default: None

Must match the instance ID from the AI Service installation; verify the instance exists before upgrading.

#### catalog_channel

The subscription channel from which components such as the AI Service tenant operator will be installed during the migration (e.g. `9.0.x`, `9.1.x`). This should match the channel used to install AI Service.

- **Optional**
- Environment Variable: `AISERVICE_CHANNEL`
- Default: None

If not provided, the role automatically selects the next appropriate version. The role validates that the target channel is a valid upgrade path from the current version.

#### force_migration

Skip any checks to determine if a migration is needed and perform the migration.

- **Optional**
- Environment Variable: `AISERVICE_FORCE_MIGRATION`
- Default: `false`

!!! warning
    Use this only when you are sure a migration is needed, for example to recover from an error during the migration process — forcing a migration that is not required may break your environment.

## Example Playbook

After installing the Ansible Collection you can include this role in your own custom playbooks.

```yaml
- hosts: localhost
  vars:
    instance_id: "{{ lookup('env', 'AISERVICE_INSTANCE_ID') }}"
    catalog_channel: 9.2.x
  roles:
    - ibm.mas_devops.aiservice_migration
```

## License

EPL-2.0
