# suite_manage_load_dbc_scripts

This role loads and executes ad-hoc DBC (Database Configuration) script files into Maximo Manage or Health server. DBC scripts are used to customize Manage/Health database configurations, add custom fields, modify system properties, or perform database maintenance tasks.

!!! important "Script Requirements"
    - Only `.dbc` format files are accepted
    - Scripts must be valid Maximo DBC syntax
    - Role validates successful execution and fails on errors

## What This Role Does

- Locates DBC script files from specified local directory
- Copies scripts to Manage/Health server pods
- Executes scripts using Maximo's DBC processor
- Validates each script execution for errors
- Fails if any script encounters errors

## Role Variables

### mas_instance_id
MAS instance identifier.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

**Purpose**: Identifies which MAS instance contains the Manage or Health application where DBC scripts will be executed.

**When to use**:
- Always required for DBC script execution
- Must match the instance ID from MAS installation
- Used to construct namespace for script execution

**Valid values**: Lowercase alphanumeric string, 3-12 characters (e.g., `prod`, `dev`, `masinst1`)

**Impact**: Determines which MAS instance's Manage/Health application receives the DBC scripts. Namespace format: `mas-{instance_id}-{app_id}`.

**Related variables**:
- `mas_app_id`: Application within this instance (manage or health)
- `dbc_script_path_local`: Location of scripts to execute

**Note**: This must match the instance ID used during Manage/Health installation.

### mas_app_id
MAS application identifier.

- **Required**
- Environment Variable: `MAS_APP_ID`
- Default: None

**Purpose**: Specifies which MAS application (Manage or Health) will execute the DBC scripts.

**When to use**:
- Always required for DBC script execution
- Must match the deployed application
- Determines target namespace and server

**Valid values**: `manage`, `health`

**Impact**: Determines which application server executes the DBC scripts. Different applications have different database schemas and configurations.

**Related variables**:
- `mas_instance_id`: Instance containing this application
- `dbc_script_path_local`: Scripts to execute on this application

**Note**: DBC scripts are application-specific. Scripts written for Manage may not work in Health and vice versa. Ensure scripts are compatible with the target application.

### dbc_script_path_local
Local directory path for DBC script files.

- **Optional**
- Environment Variable: `DBC_SCRIPT_PATH_LOCAL`
- Default: `suite_manage_load_dbc_scripts/files`

**Purpose**: Specifies the local filesystem directory containing DBC script files to be loaded and executed on the Manage/Health server.

**When to use**:
- Use default for scripts in role's files directory
- Override to specify custom script location
- Directory must contain `.dbc` files

**Valid values**: Valid local filesystem path (e.g., `/path/to/dbc/scripts`, `~/manage-scripts`)

**Impact**: The role scans this directory for `.dbc` files, copies them to the server, and executes them in alphabetical order.

**Related variables**:
- `mas_instance_id`: Instance where scripts execute
- `mas_app_id`: Application executing the scripts

**Note**:
- All `.dbc` files in the directory will be executed
- Scripts execute in alphabetical order by filename
- Use filename prefixes (e.g., `01-`, `02-`) to control execution order
- Ensure scripts are idempotent if role may be run multiple times
- Test scripts in non-production environment first

## Example Playbook

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: "{{ lookup('env', 'MAS_INSTANCE_ID') }}"
    mas_app_id: manage
    dbc_script_path_local: "{{ lookup('env', 'DBC_SCRIPT_PATH_LOCAL') }}"
  roles:
    - ibm.mas_devops.suite_manage_load_dbc_scripts
```

## License
EPL-2.0
