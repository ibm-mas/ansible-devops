# suite_manage_bim_config

This role configures Building Information Modeling (BIM) support in Maximo Manage application by setting up the persistent volume mount path and updating database system properties. BIM enables 3D visualization and management of building models within Manage.

!!! important "Prerequisites"
    - Manage application must be deployed with persistent volume storage configured
    - A PVC with appropriate mount path must exist before running this role
    - Use `suite_app_config` with `mas_app_settings_persistent_volumes_flag: true` to create default persistent storage

For detailed information on persistent storage configuration, see [Configuring persistent volume claims](https://www.ibm.com/docs/en/maximo-manage/continuous-delivery?topic=storage-configuring-persistent-volume-claims).

## What This Role Does

- Configures BIM folder paths in Manage system properties
- Updates Manage database with BIM mount path configuration
- Enables BIM functionality for 3D building model visualization
- Validates persistent volume mount path exists

## Role Variables

### mas_app_settings_bim_mount_path
Persistent volume mount path for BIM files.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_BIM_MOUNT_PATH`
- Default: `/bim`

**Purpose**: Specifies the container mount path where BIM files (3D models, drawings, documents) are stored in persistent storage.

**When to use**:
- Use default `/bim` when using `suite_app_config` with persistent volumes
- Override if you have a custom mount path configuration
- Must match the actual PVC mount path in Manage pods

**Valid values**: Valid Linux filesystem path (e.g., `/bim`, `/data/bim`, `/mnt/bim`)

**Impact**: Determines where Manage stores and retrieves BIM files. The path must exist as a mounted volume in Manage pods.

**Related variables**:
- `mas_instance_id`: Instance containing Manage
- `db2_instance_name`: Database to update with BIM configuration

**Note**: The mount path must correspond to an actual PVC mounted in the Manage deployment. If using `suite_app_config` with `mas_app_settings_persistent_volumes_flag: true`, the default `/bim` path is automatically configured.

### mas_instance_id
MAS instance identifier.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

**Purpose**: Identifies which MAS instance contains the Manage application to configure for BIM.

**When to use**:
- Always required for BIM configuration
- Must match the instance ID from MAS installation
- Used to locate Manage resources

**Valid values**: Lowercase alphanumeric string, 3-12 characters (e.g., `prod`, `dev`, `masinst1`)

**Impact**: Determines which MAS instance's Manage application is configured with BIM support.

**Related variables**:
- `mas_app_settings_bim_mount_path`: BIM storage path to configure
- `db2_instance_name`: Database instance for this Manage deployment

**Note**: This must match the instance ID used during Manage installation.

### db2_instance_name
Db2 Warehouse instance name.

- **Required**
- Environment Variable: `DB2_INSTANCE_NAME`
- Default: None

**Purpose**: Identifies the Db2 Warehouse instance that stores Manage application data, which will be updated with BIM system properties.

**When to use**:
- Always required for BIM configuration
- Must match the Db2 instance name used by Manage
- Used to connect to database for SQL updates

**Valid values**: Valid Db2 instance name (e.g., `db2w-manage`, `db2u-manage`)

**Impact**: Determines which Db2 instance is accessed to update BIM configuration system properties via SQL.

**Related variables**:
- `db2_namespace`: Namespace containing this instance
- `db2_dbname`: Database name within the instance
- `mas_instance_id`: MAS instance using this database

**Note**: To find the instance name, go to the Db2 namespace and look for pods with `label=engine`. Describe the pod and find the `app` label value - that's your instance name.

### db2_namespace
Db2 Warehouse namespace.

- **Optional**
- Environment Variable: `DB2_NAMESPACE`
- Default: `db2u`

**Purpose**: Specifies the OpenShift namespace where the Db2 Warehouse instance is deployed.

**When to use**:
- Use default (`db2u`) for standard Db2 deployments
- Override if Db2 is deployed in a custom namespace
- Required to locate the Db2 instance

**Valid values**: Valid Kubernetes namespace name

**Impact**: Determines where to look for the Db2 instance when connecting for BIM configuration updates.

**Related variables**:
- `db2_instance_name`: Instance to find in this namespace
- `db2_dbname`: Database within the instance

**Note**: The default `db2u` namespace is used by most Db2 Warehouse deployments. Only change if you have a custom deployment.

### db2_dbname
Database name within Db2 instance.

- **Optional**
- Environment Variable: `DB2_DBNAME`
- Default: `BLUDB`

**Purpose**: Specifies the database name within the Db2 instance where Manage tables and BIM configuration are stored.

**When to use**:
- Use default (`BLUDB`) for standard Manage deployments
- Override if Manage uses a custom database name
- Required for database connection

**Valid values**: Valid Db2 database name

**Impact**: Determines which database within the Db2 instance is updated with BIM system properties.

**Related variables**:
- `db2_instance_name`: Instance containing this database
- `db2_namespace`: Namespace of the instance

**Note**: `BLUDB` is the default database name for Manage deployments. Only change if you have a custom database configuration.

## Example Playbook

### Configure BIM for Existing Manage Instance
The following sample can be used to configure BIM for an existing Manage application instance:

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    db2_instance_name: db2w-manage
    mas_app_settings_bim_mount_path: /bim
  roles:
    - ibm.mas_devops.suite_manage_bim_config
```

### Deploy Manage with BIM Configuration
The following sample playbook can be used to deploy Manage with default persistent storage for BIM (PVC mount path `/bim`), and configure Manage system properties with the corresponding BIM settings:

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_app_id: manage
    mas_app_channel: 8.4.x
    mas_instance_id: masinst1
    mas_workspace_id: masdev
    db2_instance_name: db2w-manage
    mas_app_settings_persistent_volumes_flag: true
    mas_app_settings_bim_mount_path: /bim
  roles:
    - ibm.mas_devops.db2
    - ibm.mas_devops.suite_db2_setup_for_manage
    - ibm.mas_devops.suite_config
    - ibm.mas_devops.suite_app_install
    - ibm.mas_devops.suite_app_config
    - ibm.mas_devops.suite_manage_bim_config
```

## License
EPL-2.0
