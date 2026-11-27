# ibmcloud_resource_key

Create IBM Cloud resource keys (apikeys for specific services associated to the account)

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`service_instance`](#service_instance) | Yes | None |
| [`service_resource_key_name`](#service_resource_key_name) | No | `<service_instance>_resource-key` |
| [`delete_service_key`](#delete_service_key) | No | `False` |
| [`output_service_key_details_to_file`](#output_service_key_details_to_file) | No | `False` |
| [`output_dir`](#output_dir) | No | `.` |

### Service Instance and Key

#### service_instance

The name of the IBM Cloud service instance for which to create or manage resource keys — must match the exact, case-sensitive name of an existing instance in your account (e.g., `mas-db2-instance`, `mas-mongodb`, `mas-cos-bucket`, `cp4d-instance`).

- **Required**
- Environment Variable: `SERVICE_INSTANCE`
- Default: None

The service instance must already exist, and you must have appropriate IAM permissions to create resource keys for it. The generated credentials are scoped to this specific instance; different service types (Db2, COS, etc.) generate different credential formats, and each instance can have multiple resource keys for different purposes.

#### service_resource_key_name

The name to assign to the resource key (service credentials) — any string following IBM Cloud resource naming conventions (alphanumeric characters, hyphens, and underscores), unique within the service instance; recommended format `<purpose>-<service>-key` (e.g., `mas-db2-key`, `backup-cos-key`).

- **Optional**
- Environment Variable: `SERVICE_RESOURCE_KEY_NAME`
- Default: `<service_instance>_resource-key` (derived from `service_instance`)

Used to identify the resource key in the IBM Cloud console and CLI, and is required when deleting a specific key. Set a custom name when you need multiple keys for the same service instance or want to follow naming conventions; the name cannot be changed after creation (deletion and recreation required). Keep track of key names for future deletion or rotation.

### Key Lifecycle

#### delete_service_key

Controls whether to delete the specified resource key instead of creating it — `True` to permanently delete the resource key identified by `service_resource_key_name`, `False` to create a new key (default).

- **Optional**
- Environment Variable: `DELETE_SERVICE_KEY`
- Default: `False`

Useful for credential rotation, cleanup, or deprovisioning operations. The deletion does not affect the service instance itself, only the access credentials, and will fail if the key doesn't exist (this is not an error condition).

!!! warning
    Deletion is irreversible — credentials cannot be recovered, and applications using them will immediately lose access. Ensure no applications are using the credentials before deletion; consider creating a new key first for zero-downtime rotation, and always verify the key name to avoid removing the wrong credentials.

### Output

#### output_service_key_details_to_file

Controls whether to save the resource key credentials to a JSON file — `True` to export the complete resource key details and credentials to `service-key_<service_resource_key_name>.json`, `False` to create no output file (default).

- **Optional**
- Environment Variable: `OUTPUT_SERVICE_KEY_DETAILS_TO_FILE`
- Default: `False`

Useful for manual configuration, backup or documentation purposes, or integration with automation tools that consume JSON credentials. The JSON structure varies by service type (Db2, COS, MongoDB, etc.).

!!! warning
    The output file contains sensitive credentials including connection strings, passwords, and API keys — protect it appropriately, do not commit it to version control, and consider encrypting it or storing it in a secrets manager.

#### output_dir

The directory path where the resource key JSON file will be saved — any valid local filesystem path (relative or absolute, e.g., `~/credentials`, `/opt/mas/keys`, `./config`); the directory is created if it doesn't exist.

- **Optional**
- Environment Variable: `OUTPUT_DIR`
- Default: `.` (current directory, typically `ibm/mas_devops`)

Only used when `output_service_key_details_to_file` is `True`. The default `.` is relative to where Ansible is executed — for production use, specify an absolute path, ideally a dedicated credentials directory with restricted access.

## Example Playbook

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    ibmcloud_apikey: xxx
    service_instance: xxx
    service_resource_key_name: xxx
    output_service_key_details_to_file: True OR False
    delete_service_key: True OR False
  roles:
    - ibmcloud_resource_key
```

## License

EPL-2.0
