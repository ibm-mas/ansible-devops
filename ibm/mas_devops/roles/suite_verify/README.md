# suite_verify

Verify a MAS installation is ready to use. This role will also print out the Admin Dashboard URL and the username and password of the superuser. If you want to disable these credentials being written to the output set the `mas_hide_superuser_credentials` to `True`.

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`mas_instance_id`](#mas_instance_id) | Yes | None |
| [`mas_hide_superuser_credentials`](#mas_hide_superuser_credentials) | No | `true` |

### Verification

#### mas_instance_id

MAS instance identifier to verify (lowercase alphanumeric, 3-12 characters, e.g. `prod`, `dev`, `masinst1`).

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

Must match the instance ID from the MAS installation. The role checks that the instance is ready to use and retrieves the Admin Dashboard URL and superuser credentials.

#### mas_hide_superuser_credentials

Hide superuser credentials in the verification output.

- **Optional**
- Environment Variable: `MAS_HIDE_SUPERUSER_CREDENTIALS`
- Default: `true`

When `true` (the default) only the name of the secret containing the credentials is shown; when `false` the actual username and password are written to the output.

!!! tip
    Keep this set to `true` in CI/CD pipelines and shared environments. The credentials can always be retrieved directly from the Kubernetes secret, so there is rarely a need to display them.

## Example Playbook

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_hide_superuser_credentials: True
  roles:
    - ibm.mas_devops.suite_verify
```

## License

EPL-2.0
