gencfg_jdbc
============

Generate JDBC configuration files for connecting Maximo Application Suite to external databases. This role creates JdbcCfg custom resources that can be applied to MAS instances to configure database connectivity for various applications including Manage, Health, Predict, and others.

The role supports multiple database types (Db2, Oracle, SQL Server) with both secure and insecure connection options, and can generate configurations scoped at system, workspace, application, or workspace-application levels.


Role Variables - Data Source
-------------------------------------------------------------------------------

### db_instance_id
Database instance identifier used in the generated configuration.

- Optional
- Environment Variable: `DB_INSTANCE_ID`
- Default: `dbinst`

**Purpose**: Provides a unique identifier for the database instance within MAS configuration. This ID is used to reference the database connection in application configurations.

**When to use**: Always set this to a meaningful name that identifies the database instance, especially when managing multiple database connections.

**Valid values**: Alphanumeric string, typically lowercase with no spaces (e.g., `maxdb01`, `manage-prod`, `oracle-dev`).

**Impact**: This identifier appears in MAS configuration resources and must be unique within the scope of the MAS instance.

**Related variables**: `mas_config_scope`, `mas_instance_id`

**Notes**:
- Default value `dbinst` is suitable for simple single-database deployments
- Use descriptive names in multi-database environments to avoid confusion

### db_username
Database username for authentication.

- **Required**
- Environment Variable: `MAS_JDBC_USER`
- Default: None

**Purpose**: Specifies the database user account that MAS applications will use to connect to the database.

**When to use**: Always required. Must be a valid database user with appropriate permissions for the target MAS application.

**Valid values**: Valid database username according to the database system's naming rules.

**Impact**: This user must have the necessary privileges to access and modify the application schema. Insufficient permissions will cause application failures.

**Related variables**: `jdbc_instance_password`, `jdbc_url`

**Notes**:
- For Manage: User needs full access to the MAXIMO schema
- For Oracle: May need to include schema prefix in some configurations
- Ensure the user has appropriate connection limits configured in the database

### jdbc_instance_password
Database password for authentication.

- **Required**
- Environment Variable: `MAS_JDBC_PASSWORD`
- Default: None

**Purpose**: Provides the password for the database user account specified in `db_username`.

**When to use**: Always required for database authentication.

**Valid values**: Valid password string. Should meet your organization's password complexity requirements.

**Impact**: Stored as a Kubernetes secret in the MAS namespace. Incorrect password will prevent database connectivity.

**Related variables**: `db_username`, `jdbc_url`

**Notes**:
- Password is stored securely in Kubernetes secrets
- Consider using strong passwords and regular rotation policies
- Ensure password doesn't contain characters that require URL encoding if embedded in connection strings

### jdbc_url
JDBC connection URL for the database.

- **Required**
- Environment Variable: `MAS_JDBC_URL`
- Default: None

**Purpose**: Defines the complete JDBC connection string including host, port, database name, and connection parameters.

**When to use**: Always required. Must be formatted correctly for the specific database type.

**Valid values**: Valid JDBC URL string for the target database type. Examples:

- **IBM Db2 (insecure)**: `jdbc:db2://dbserver.example.com:50000/maxdb`
- **IBM Db2 (secure)**: `jdbc:db2://dbserver.example.com:50000/maxdb:sslConnection=true;`
- **Oracle Database**: `jdbc:oracle:thin:@dbserver.example.com:1521:maximo`
- **SQL Server (insecure)**: `jdbc:sqlserver://;serverName=dbserver.example.com;portNumber=1433;databaseName=maxdb;integratedSecurity=false;sendStringParametersAsUnicode=false;selectMethod=cursor;encrypt=false;trustServerCertificate=false;`
- **SQL Server (secure)**: `jdbc:sqlserver://;serverName=dbserver.example.com;portNumber=1433;databaseName=maxdb;integratedSecurity=false;sendStringParametersAsUnicode=false;selectMethod=cursor;encrypt=true;trustServerCertificate=true;`

**Impact**: Incorrect URL format will prevent database connectivity. SSL/TLS settings in the URL must match the `ssl_enabled` variable and database server configuration.

**Related variables**: `ssl_enabled`, `db_pem_file`, `db_username`

**Notes**:
- Always test the JDBC URL with a database client before using in MAS
- For SSL connections, ensure the URL includes appropriate SSL parameters
- Some databases require specific JDBC driver parameters for optimal performance
- Port numbers and database names must match your actual database configuration

### db_pem_file
Local file path to the database SSL/TLS certificate in PEM format.

- Optional
- Environment Variable: `MAS_JDBC_CERT_LOCAL_FILE`
- Default: None

**Purpose**: Provides the SSL/TLS certificate for secure database connections. The certificate is embedded in the generated JdbcCfg resource.

**When to use**: Required when `ssl_enabled` is `true` and the database uses SSL/TLS encryption. Not needed for insecure connections.

**Valid values**: Absolute or relative file path to a valid PEM-encoded certificate file (e.g., `/tmp/db-ca.pem`, `./certs/database-cert.pem`).

**Impact**: Without the correct certificate, SSL connections will fail with certificate validation errors.

**Related variables**: `ssl_enabled`, `jdbc_url`

**Notes**:
- The file must be accessible from the Ansible controller
- For self-signed certificates, this should be the CA certificate
- For commercial certificates, may need to include the full certificate chain
- Certificate must be in PEM format (Base64-encoded with BEGIN/END markers)


Role Variables - MAS Configuration
-------------------------------------------------------------------------------

### mas_config_scope
Configuration scope level for the generated JDBC configuration.

- **Required**
- Environment Variable: `MAS_CONFIG_SCOPE`
- Default: None

**Purpose**: Determines at what level the JDBC configuration will be available within MAS - system-wide, workspace-specific, application-specific, or workspace-application combination.

**When to use**: Always required. Choose based on how the database will be shared across MAS components.

**Valid values**:
- `system` - Available to all workspaces and applications
- `ws` - Available only to a specific workspace
- `app` - Available only to a specific application across all workspaces
- `wsapp` - Available only to a specific application in a specific workspace

**Impact**: Determines which MAS components can access this database configuration. Incorrect scope may prevent applications from finding the database configuration.

**Related variables**: `mas_workspace_id` (required for `ws` and `wsapp`), `mas_application_id` (required for `app` and `wsapp`)

**Notes**:
- Use `system` scope for shared databases used by multiple applications
- Use `wsapp` scope for dedicated databases per workspace-application combination
- Scope cannot be changed after creation; requires recreation of the configuration

### mas_config_dir
Local directory path where the generated YAML configuration file will be saved.

- **Required**
- Environment Variable: `MAS_CONFIG_DIR`
- Default: None

**Purpose**: Specifies the output directory for the generated JdbcCfg YAML file that can be applied to the MAS instance.

**When to use**: Always required. Directory must exist or be creatable by the Ansible user.

**Valid values**: Valid directory path (absolute or relative) where the Ansible controller has write permissions.

**Impact**: The generated YAML file will be created in this directory and can be applied using `kubectl apply` or the `suite_config` role.

**Related variables**: `mas_instance_id`, `db_instance_id`

**Notes**:
- Directory will be created if it doesn't exist
- Generated filename format: `jdbccfg-<db_instance_id>.yml`
- Keep generated files for documentation and disaster recovery purposes

### mas_instance_id
MAS instance identifier for which the configuration is being generated.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

**Purpose**: Identifies the target MAS instance where this JDBC configuration will be applied.

**When to use**: Always required. Must match an existing MAS instance ID.

**Valid values**: Valid MAS instance ID (typically 3-12 lowercase alphanumeric characters).

**Impact**: The generated configuration will be namespace-scoped to `mas-<instance-id>-core`. Incorrect instance ID will cause the configuration to be created in the wrong namespace.

**Related variables**: `mas_config_scope`, `mas_workspace_id`

**Notes**:
- Must match the instance ID used during MAS installation
- Case-sensitive value
- Cannot be changed after MAS installation

### mas_workspace_id
MAS workspace identifier for workspace-scoped configurations.

- **Required** if `mas_config_scope` is `ws` or `wsapp`
- Environment Variable: `MAS_WORKSPACE_ID`
- Default: None

**Purpose**: Specifies the target workspace when generating workspace-scoped or workspace-application-scoped JDBC configurations.

**When to use**: Required when `mas_config_scope` is set to `ws` or `wsapp`. Not used for `system` or `app` scopes.

**Valid values**: Valid MAS workspace ID (typically lowercase alphanumeric, e.g., `masdev`, `prod`, `test`).

**Impact**: The JDBC configuration will only be available to the specified workspace. Applications in other workspaces cannot access this database configuration.

**Related variables**: `mas_config_scope`, `mas_application_id`

**Notes**:
- Workspace must exist before applying the configuration
- Use workspace-scoped configs for tenant isolation in multi-tenant deployments

### mas_application_id
MAS application identifier for application-scoped configurations.

- **Required** if `mas_config_scope` is `app` or `wsapp`
- Environment Variable: `MAS_APP_ID`
- Default: None

**Purpose**: Specifies the target application when generating application-scoped or workspace-application-scoped JDBC configurations.

**When to use**: Required when `mas_config_scope` is set to `app` or `wsapp`. Not used for `system` or `ws` scopes.

**Valid values**: Valid MAS application ID: `manage`, `health`, `predict`, `monitor`, `assist`, `visualinspection`, `iot`, `optimizer`, `safety`.

**Impact**: The JDBC configuration will only be available to the specified application. Other applications cannot access this database configuration.

**Related variables**: `mas_config_scope`, `mas_workspace_id`

**Notes**:
- Application must be installed before applying the configuration
- Most commonly used with `manage` for Manage-specific databases

### ssl_enabled
Indicates whether SSL/TLS encryption is enabled for the database connection.

- **Required**
- Environment Variable: `SSL_ENABLED`
- Default: None

**Purpose**: Explicitly declares SSL/TLS status for applications that cannot determine this from the JDBC URL alone. Must match the SSL configuration in `jdbc_url`.

**When to use**: Always required. Set to `true` for encrypted connections, `false` for unencrypted connections.

**Valid values**:
- `true` - SSL/TLS encryption is enabled
- `false` - No encryption (insecure connection)

**Impact**: Mismatch between this setting and the actual JDBC URL SSL parameters will cause connection failures in some MAS applications.

**Related variables**: `jdbc_url`, `db_pem_file`

**Notes**:
- Always use `true` for production environments
- When `true`, ensure `db_pem_file` is provided
- Must match the SSL settings in the `jdbc_url` parameter
- Some MAS applications rely on this flag rather than parsing the JDBC URL

### custom_labels
Custom Kubernetes labels to apply to the generated JdbcCfg resource.

- Optional
- Environment Variable: `CUSTOM_LABELS`
- Default: None

**Purpose**: Adds custom labels to the JdbcCfg resource for organization, filtering, or automation purposes.

**When to use**: Use when you need to tag configurations for specific purposes like environment identification, cost tracking, or automated management.

**Valid values**: Comma-separated key=value pairs (e.g., `env=prod,team=platform,cost-center=12345`).

**Impact**: Labels are applied to the Kubernetes resource and can be used for selection, filtering, and automation workflows.

**Related variables**: None

**Notes**:
- Labels must follow Kubernetes naming conventions
- Useful for GitOps workflows and resource management
- Can be used with label selectors in automation scripts


Example Playbook
-------------------------------------------------------------------------------

```yaml
---

- hosts: localhost
  any_errors_fatal: true
  roles:
    - ibm.mas_devops.gencfg_jdbc
```

License
-------------------------------------------------------------------------------
EPL-2.0
