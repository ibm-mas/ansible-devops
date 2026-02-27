# ibmcloud_resource_key

Create IBM Cloud resource keys (apikeys for specific services associated to the account)


## Role Variables

### service_instance
The name of the IBM Cloud service instance for which to create or manage resource keys.

- **Required**
- Environment Variable: `SERVICE_INSTANCE`
- Default Value: None

**Purpose**: Identifies the IBM Cloud service instance (such as Db2, MongoDB, Cloud Object Storage, or Cloud Pak for Data) for which a resource key (service credentials) will be created or deleted.

**When to use**: Always required when creating or deleting service keys. The service instance must already exist in your IBM Cloud account.

**Valid values**:
- Any valid IBM Cloud service instance name in your account
- Common examples: `mas-db2-instance`, `mas-mongodb`, `mas-cos-bucket`, `cp4d-instance`
- Must match the exact name of an existing service instance
- Case-sensitive

**Impact**:
- Determines which service instance the resource key will provide access to
- The generated credentials will be scoped to this specific service instance
- Different service types (Db2, COS, etc.) will generate different credential formats
- Used to derive the default resource key name if not explicitly specified

**Related variables**:
- [`service_resource_key_name`](#service_resource_key_name) - Name of the key to create (defaults to `<service_instance>_resource-key`)
- [`output_service_key_details_to_file`](#output_service_key_details_to_file) - Whether to save credentials to file

**Notes**:
- Ensure the service instance exists before running this role
- You must have appropriate IAM permissions to create resource keys for the service
- Resource keys provide full access to the service instance - protect them carefully
- Each service instance can have multiple resource keys for different purposes

### service_resource_key_name
The name to assign to the resource key (service credentials).

- **Optional**
- Environment Variable: `SERVICE_RESOURCE_KEY_NAME`
- Default Value: `<service_instance>_resource-key` (derived from service_instance)

**Purpose**: Specifies a custom name for the resource key. If not provided, the role automatically generates a name by appending `_resource-key` to the service instance name.

**When to use**:
- When you need multiple resource keys for the same service instance
- When you want a more descriptive name than the default
- When following specific naming conventions in your organization

**Valid values**:
- Any string that follows IBM Cloud resource naming conventions
- Alphanumeric characters, hyphens, and underscores
- Should be unique within the service instance
- Recommended format: `<purpose>-<service>-key` (e.g., `mas-db2-key`, `backup-cos-key`)

**Impact**:
- Used to identify the resource key in IBM Cloud console and CLI
- Required when deleting a specific resource key
- Appears in the output filename if `output_service_key_details_to_file` is enabled
- Cannot be changed after creation (requires deletion and recreation)

**Related variables**:
- [`service_instance`](#service_instance) - The service for which this key is created
- [`delete_service_key`](#delete_service_key) - Uses this name to identify which key to delete
- [`output_service_key_details_to_file`](#output_service_key_details_to_file) - Uses this name in the output filename

**Notes**:
- If not specified, defaults to `<service_instance>_resource-key`
- Use descriptive names to identify the purpose of each key
- Keep track of key names for future deletion or rotation
- Multiple keys can exist for the same service instance with different names

### delete_service_key
Controls whether to delete the specified resource key instead of creating it.

- **Optional**
- Environment Variable: `DELETE_SERVICE_KEY`
- Default Value: `False`

**Purpose**: When set to `True`, the role will delete the specified resource key instead of creating a new one. This is used for credential rotation or cleanup operations.

**When to use**:
- When rotating service credentials and removing old keys
- During cleanup or deprovisioning operations
- When a resource key is no longer needed
- Before recreating a key with the same name

**Valid values**:
- `True` - Delete the resource key specified by `service_resource_key_name`
- `False` - Create a new resource key (default behavior)

**Impact**:
- When `True`: Permanently deletes the specified resource key and its credentials
- Applications using the deleted credentials will immediately lose access
- Deletion is irreversible - credentials cannot be recovered
- Does not affect the service instance itself, only the access credentials

**Related variables**:
- [`service_resource_key_name`](#service_resource_key_name) - Identifies which key to delete
- [`service_instance`](#service_instance) - The service instance containing the key

**Notes**:
- Ensure no applications are using the credentials before deletion
- Consider creating a new key before deleting the old one for zero-downtime rotation
- Deletion will fail if the key doesn't exist (this is not an error condition)
- Always verify the key name before deletion to avoid removing the wrong credentials

### output_service_key_details_to_file
Controls whether to save the resource key credentials to a JSON file.

- **Optional**
- Environment Variable: `OUTPUT_SERVICE_KEY_DETAILS_TO_FILE`
- Default Value: `False`

**Purpose**: When set to `True`, the role will export the complete resource key details and credentials to a JSON file for later use or reference.

**When to use**:
- When you need to store credentials for manual configuration
- For backup or documentation purposes
- When integrating with other automation tools that consume JSON credentials
- During initial setup to review credential structure

**Valid values**:
- `True` - Export credentials to JSON file
- `False` - Do not create output file (default)

**Impact**:
- When `True`: Creates a JSON file named `service-key_<service_resource_key_name>.json`
- File contains complete credential details including connection strings, passwords, and API keys
- File is created in the directory specified by `output_dir`
- Credentials in the file are sensitive and should be protected

**Related variables**:
- [`output_dir`](#output_dir) - Directory where the JSON file will be created
- [`service_resource_key_name`](#service_resource_key_name) - Used in the output filename

**Notes**:
- The output file contains sensitive credentials - protect it appropriately
- Do not commit credential files to version control
- Consider encrypting the output file or storing it in a secrets manager
- The JSON structure varies by service type (Db2, COS, MongoDB, etc.)
- Useful for troubleshooting connection issues or manual configuration

### output_dir
The directory path where the resource key JSON file will be saved.

- **Optional**
- Environment Variable: `OUTPUT_DIR`
- Default Value: `.` (current directory, typically `ibm/mas_devops`)

**Purpose**: Specifies the local filesystem directory where the resource key credentials JSON file will be written when `output_service_key_details_to_file` is enabled.

**When to use**: Set this when you want to save credentials to a specific location other than the current directory, such as a secure credentials directory or a mounted volume.

**Valid values**:
- Any valid local filesystem path (e.g., `~/credentials`, `/opt/mas/keys`, `./config`)
- Can be relative or absolute path
- Directory will be created if it doesn't exist
- Must have write permissions

**Impact**:
- Determines where the `service-key_<service_resource_key_name>.json` file is created
- Only used when `output_service_key_details_to_file` is `True`
- Default of `.` places the file in the Ansible collection directory

**Related variables**:
- [`output_service_key_details_to_file`](#output_service_key_details_to_file) - Must be `True` for this to take effect
- [`service_resource_key_name`](#service_resource_key_name) - Used in the output filename

**Notes**:
- Ensure the directory has appropriate permissions for writing
- Consider using a dedicated credentials directory with restricted access
- The default `.` location is relative to where Ansible is executed
- For production use, specify an absolute path to avoid confusion
- Back up this directory if it contains important credentials


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
