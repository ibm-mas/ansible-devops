# suite_verify

Verify a MAS installation is ready to use. This role will also print out the Admin Dashboard URL and the username and password of the superuser. If you want to disable these credentials being written to the output set the `mas_hide_superuser_credentials` to `True`.

## Role Variables

### mas_instance_id
MAS instance identifier to verify.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

**Purpose**: Identifies which MAS instance to verify. The role checks that the instance is ready to use and retrieves access credentials.

**When to use**:
- Always required for verification operations
- Must match the instance ID from MAS installation
- Used after installation to confirm readiness

**Valid values**: Lowercase alphanumeric string, 3-12 characters (e.g., `prod`, `dev`, `masinst1`)

**Impact**: Determines which MAS instance is verified. The role checks instance status and retrieves the Admin Dashboard URL and superuser credentials.

**Related variables**:
- `mas_hide_superuser_credentials`: Controls credential display in output

**Note**: This role verifies that the MAS instance is ready to use and provides access information. Run after installation or upgrade to confirm successful deployment.

### mas_hide_superuser_credentials
Hide superuser credentials in output.

- **Optional**
- Environment Variable: `MAS_HIDE_SUPERUSER_CREDENTIALS`
- Default: `true`

**Purpose**: Controls whether superuser credentials are displayed in the verification output. When enabled, only the secret name is shown instead of actual credentials.

**When to use**:
- Leave as `true` (default) for security (recommended)
- Set to `false` only when you need to see credentials in output
- Use `true` in CI/CD pipelines and shared environments

**Valid values**: `true`, `false`

**Impact**: 
- `true`: Displays only the secret name containing credentials (secure)
- `false`: Displays actual username and password in output (insecure)

**Related variables**:
- `mas_instance_id`: Instance whose credentials are being verified

**Note**: **SECURITY** - The default `true` is recommended for security. Only set to `false` in secure, private environments where you need immediate access to credentials. Credentials can always be retrieved from the Kubernetes secret.

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
