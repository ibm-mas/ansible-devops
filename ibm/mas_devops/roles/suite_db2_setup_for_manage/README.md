# suite_db2_setup_for_manage

This role performs initial Db2 database setup required for Maximo Manage application. It configures database parameters, creates tablespaces, and applies performance optimizations that the Manage operator cannot yet handle automatically.

!!! note "Temporary Role"
    This role exists as a workaround until the Manage operator can perform these setup tasks automatically. It supports both CP4D version 3.5 and 4.0.

## What This Role Does

- Copies setup script (`setupdb.sh`) into Db2 pod
- Executes database configuration changes inside container
- Creates and configures tablespaces for Manage
- Applies enhanced Db2 performance parameters
- Optionally restarts Db2 instance to apply configuration

!!! warning "Downtime Risk"
    Setting `enforce_db2_config=true` will restart the Db2 instance, causing downtime. Schedule during maintenance windows or use with newly created instances.

## Role Variables

### db2_instance_name
Db2 instance name for Manage setup.

- **Required**
- Environment Variable: `DB2_INSTANCE_NAME`
- Default: None

**Purpose**: Identifies the Db2 Warehouse instance where Manage database setup will be performed.

**When to use**:
- Always required for Manage database setup
- Must match the Db2 instance name for Manage
- Used to locate the correct Db2 pod

**Valid values**: Valid Db2 instance name (e.g., `db2w-manage`, `db2u-manage`)

**Impact**: Determines which Db2 instance receives the Manage-specific configuration and tablespace setup.

**Related variables**:
- `db2_namespace`: Namespace containing this instance
- `db2_dbname`: Database within this instance

**Note**: To find the instance name, go to the Db2 namespace and look for pods with `label=engine`. Describe the pod and find the `app` label value.

### db2_namespace
Db2 instance namespace.

- **Optional**
- Environment Variable: `DB2_NAMESPACE`
- Default: `db2u`

**Purpose**: Specifies the OpenShift namespace where the Db2 instance is deployed.

**When to use**:
- Use default (`db2u`) for standard Db2 deployments
- Override if Db2 is deployed in a custom namespace
- Required to locate the Db2 pod

**Valid values**: Valid Kubernetes namespace name

**Impact**: Determines where to find the Db2 instance for setup script execution.

**Related variables**:
- `db2_instance_name`: Instance to find in this namespace

**Note**: The default `db2u` namespace is used by most Db2 Warehouse deployments.

### db2_username
Database connection username.

- **Optional**
- Environment Variable: None
- Default: `db2inst1`

**Purpose**: Specifies the username for connecting to the Db2 database during setup script execution.

**When to use**:
- Use default (`db2inst1`) for standard Db2 deployments
- Override if using custom database user
- Must have appropriate database privileges

**Valid values**: Valid Db2 username with admin privileges

**Impact**: Determines which user account executes the setup script and database configuration changes.

**Related variables**:
- `db2_dbname`: Database to connect to
- `db2_schema`: Schema to configure

**Note**: The user must have sufficient privileges to create tablespaces and modify database configuration.

### db2_dbname
Database name within Db2 instance.

- **Optional**
- Environment Variable: None
- Default: `BLUDB`

**Purpose**: Specifies the database name within the Db2 instance where Manage setup will be performed.

**When to use**:
- Use default (`BLUDB`) for standard Manage deployments
- Override if using custom database name
- Must exist before running this role

**Valid values**: Valid Db2 database name

**Impact**: Determines which database receives the Manage tablespace and configuration setup.

**Related variables**:
- `db2_instance_name`: Instance containing this database
- `db2_schema`: Schema within this database

**Note**: `BLUDB` is the default database name for Manage deployments.

### db2_schema
Manage database schema name.

- **Optional**
- Environment Variable: None
- Default: `maximo`

**Purpose**: Specifies the schema name where Manage tables and objects will be created.

**When to use**:
- Use default (`maximo`) for standard Manage deployments
- Override if using custom schema name
- Must match Manage configuration

**Valid values**: Valid Db2 schema name

**Impact**: Determines which schema receives the tablespace configuration and Manage-specific setup.

**Related variables**:
- `db2_dbname`: Database containing this schema
- `db2_username`: User accessing this schema

**Note**: The default `maximo` schema is standard for Manage deployments. Ensure this matches your Manage database configuration.

### db2_tablespace_data_size
Data tablespace size.

- **Optional**
- Environment Variable: `DB2_TABLESPACE_DATA_SIZE`
- Default: `5000 M`

**Purpose**: Specifies the size of the data tablespace created for Manage application data.

**When to use**:
- Use default (`5000 M`) for small to medium deployments
- Increase for large Manage deployments with extensive data
- Consider data growth over time

**Valid values**: Db2 size format (e.g., `5000 M`, `10 G`, `50 G`)

**Impact**: Determines how much data can be stored in Manage tables. Insufficient size will prevent data insertion.

**Related variables**:
- `db2_tablespace_index_size`: Related index tablespace size

**Note**: Size requirements depend on:
- Number of assets and work orders
- Historical data retention
- Attachment storage (if using database)
- Custom fields and extensions
Start with 5GB and monitor usage. Tablespaces can be expanded later if needed.

### db2_tablespace_index_size
Index tablespace size.

- **Optional**
- Environment Variable: `DB2_TABLESPACE_INDEX_SIZE`
- Default: `5000 M`

**Purpose**: Specifies the size of the index tablespace created for Manage database indexes.

**When to use**:
- Use default (`5000 M`) for small to medium deployments
- Increase for large Manage deployments with many indexes
- Typically 20-30% of data tablespace size

**Valid values**: Db2 size format (e.g., `5000 M`, `10 G`, `20 G`)

**Impact**: Determines how many indexes can be created. Insufficient size will prevent index creation and impact performance.

**Related variables**:
- `db2_tablespace_data_size`: Related data tablespace size

**Note**: Indexes improve query performance but consume space. A good rule of thumb is to allocate 20-30% of the data tablespace size for indexes. Monitor usage and adjust as needed.

### db2_config_version
Db2 configuration parameter version.

- **Optional**
- Environment Variable: `DB2_CONFIG_VERSION`
- Default: `1.0.0`

**Purpose**: Specifies the version of enhanced Db2 performance parameters to apply during setup.

**When to use**:
- Use default (`1.0.0`) for current parameter set
- Override only if specific version required
- Different versions may have different parameter sets

**Valid values**: `1.0.0` (currently supported version)

**Impact**: Determines which set of Db2 performance parameters are applied to optimize for Manage workloads.

**Related variables**:
- `enforce_db2_config`: Controls whether parameters are applied with restart

**Note**: The parameter set includes optimizations for Manage's specific database access patterns. Future versions may include additional optimizations.

### enforce_db2_config
Force Db2 configuration with restart.

- **Optional**
- Environment Variable: `ENFORCE_DB2_CONFIG`
- Default: `true`

**Purpose**: Controls whether enhanced Db2 parameters are applied with a database restart. Restart is required for parameters to take effect but causes downtime.

**When to use**:
- Set to `true` (default) for new Db2 instances
- Set to `true` during scheduled maintenance windows
- Set to `false` to skip parameter application (not recommended)

**Valid values**: `true`, `false`

**Impact**:
- `true`: Applies enhanced parameters and restarts Db2 instance (causes downtime)
- `false`: Skips enhanced parameter application (suboptimal performance)

**Related variables**:
- `db2_config_version`: Version of parameters to apply

**Note**: **CRITICAL** - Setting to `true` will restart the Db2 instance, causing downtime for all applications using the database. Schedule during maintenance windows. For production systems, coordinate with stakeholders. For new instances, this is safe as no applications are using the database yet.

## Example Playbook

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    db2_instancename: mydb2

    db2_namespace: db2u
    db2_config_version: "1.0.0"

    # It will cause downtime if set to true, please be careful.
    enforce_db2_config: true
  roles:
    - ibm.mas_devops.suite_db2_setup_for_manage
```


## License

EPL-2.0
