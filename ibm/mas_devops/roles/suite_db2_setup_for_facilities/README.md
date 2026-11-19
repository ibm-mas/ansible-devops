# suite_db2_setup_for_facilities

This role performs initial Db2 database setup required for Maximo Facilities (Real Estate and Facilities Management) application. It configures database parameters, creates tablespaces, and applies performance optimizations that the Facilities operator cannot yet handle automatically.

!!! note "Temporary Role"
    This role exists as a workaround until the Facilities operator can perform these setup tasks automatically. It handles Facilities-specific database requirements.

## What This Role Does

- Installs Db2 with required properties for Facilities
- Copies setup scripts into Db2 pod
- Executes database configuration changes inside container
- Creates and configures tablespaces for Facilities
- Applies enhanced Db2 performance parameters
- Optionally restarts Db2 instance to apply configuration

!!! warning "Downtime Risk"
    Setting `enforce_db2_config=true` will restart the Db2 instance, causing downtime. Schedule during maintenance windows or use with newly created instances.

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`db2_instance_name`](#db2_instance_name) | Yes | None |
| [`db2_namespace`](#db2_namespace) | No | `db2u` |
| [`db2_dbname`](#db2_dbname) | No | `BLUDB` |
| [`db2_schema`](#db2_schema) | No | `TRIDATA` |
| [`db2_username`](#db2_username) | No | `tridata` |
| [`db2_tablespace_data_size`](#db2_tablespace_data_size) | No | `5000 M` |
| [`db2_tablespace_index_size`](#db2_tablespace_index_size) | No | `5000 M` |
| [`db2_config_version`](#db2_config_version) | No | `1.0.0` |
| [`enforce_db2_config`](#enforce_db2_config) | No | `true` |
| [`db2_facilities_timezone`](#db2_facilities_timezone) | No | `UTC` |

### Db2 Connection

#### db2_instance_name

Db2 instance name for the Facilities setup — for example `db2w-facilities` or `db2u-db01`.

- **Required**
- Environment Variable: `DB2_INSTANCE_NAME`
- Default: None

Identifies the Db2 Warehouse instance that receives the Facilities-specific configuration and tablespace setup; the role uses it to locate the correct Db2 pod. To find the instance name, go to the Db2 namespace and look for pods with `label=engine`, then describe the pod and find the `app` label value.

#### db2_namespace

OpenShift namespace where the Db2 instance is deployed.

- **Optional**
- Environment Variable: `DB2_NAMESPACE`
- Default: `db2u`

Override if Db2 is deployed in a custom namespace; the default `db2u` is used by most Db2 Warehouse deployments.

#### db2_dbname

Database name within the Db2 instance where the Facilities setup is performed; the database must exist before running this role.

- **Optional**
- Environment Variable: `DB2_DBNAME`
- Default: `BLUDB`

`BLUDB` is the default database name for Facilities deployments.

#### db2_schema

Schema where the Facilities (TRIRIGA) tables and objects are created.

- **Optional**
- Environment Variable: `DB2_SCHEMA`
- Default: `TRIDATA`

`TRIDATA` is standard for Facilities/TRIRIGA deployments — this differs from Manage, which uses the `maximo` schema. Ensure this matches your Facilities database configuration.

#### db2_username

Username for connecting to the Db2 database during the Facilities setup script execution.

- **Optional**
- Environment Variable: `DB2_USERNAME`
- Default: `tridata`

The default `tridata` user is specific to Facilities/TRIRIGA; the user must have sufficient privileges to create tablespaces and modify the database configuration.

### Tablespace Sizing

#### db2_tablespace_data_size

Size of the data tablespace created for Facilities application data, in Db2 size format — for example `5000 M`, `10 G`, or `50 G`.

- **Optional**
- Environment Variable: `DB2_TABLESPACE_DATA_SIZE`
- Default: `5000 M`

Insufficient size will prevent data insertion. Requirements depend on the number of buildings and spaces, historical data retention, document attachments, and custom fields and extensions — start with 5GB and monitor usage; tablespaces can be expanded later if needed.

#### db2_tablespace_index_size

Size of the index tablespace created for Facilities database indexes, in Db2 size format — for example `5000 M`, `10 G`, or `20 G`.

- **Optional**
- Environment Variable: `DB2_TABLESPACE_INDEX_SIZE`
- Default: `5000 M`

A good rule of thumb is to allocate 20-30% of the data tablespace size for indexes; insufficient size will prevent index creation and impact performance. Monitor usage and adjust as needed.

### Db2 Configuration

#### db2_config_version

Version of the enhanced Db2 performance parameters to apply — `1.0.0` is the currently supported version.

- **Optional**
- Environment Variable: `DB2_CONFIG_VERSION`
- Default: `1.0.0`

The parameter set includes optimizations for Facilities' specific database access patterns; future versions may include additional optimizations.

#### enforce_db2_config

Whether the enhanced Db2 parameters are applied together with a database restart — `true` or `false`. The restart is required for the parameters to take effect.

- **Optional**
- Environment Variable: `ENFORCE_DB2_CONFIG`
- Default: `true`

!!! warning
    Setting this to `true` will restart the Db2 instance, causing downtime for all applications using the database. Schedule during maintenance windows and coordinate with stakeholders for production systems; for newly created instances it is safe as no applications are using the database yet. Setting it to `false` skips the enhanced parameter application, resulting in suboptimal performance.

#### db2_facilities_timezone

Timezone used by the Db2 server for timestamp operations and scheduling — for example `GMT`, `EST`, `PST`, `CET`, or `UTC`.

- **Optional**
- Environment Variable: `DB2_FACILITIES_TIMEZONE`
- Default: `UTC`

Use `UTC` for globally distributed systems, or the local timezone when all users are in the same timezone. Must match the MAS Facilities Server timezone.

## Example Playbook

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:

    # Configuration for the Db2 cluster
    db2_namespace: db2u
    db2_instance_name: db2u-db01
    db2_dbname: BLUDB

  roles:
    - ibm.mas_devops.suite_db2_setup_for_facilities
```


## License

EPL-2.0
