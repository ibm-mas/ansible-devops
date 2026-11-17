# gencfg_jdbc

Generate JDBC configuration files for connecting Maximo Application Suite to external databases. This role creates JdbcCfg custom resources that can be applied to MAS instances to configure database connectivity for various applications including Manage, Health, Predict, and others.

The role supports multiple database types (Db2, Oracle, SQL Server) with both secure and insecure connection options, and can generate configurations scoped at system, workspace, application, or workspace-application levels.


## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`db_instance_id`](#db_instance_id) | No | `dbinst` |
| [`db_username`](#db_username) | Yes | None |
| [`jdbc_instance_password`](#jdbc_instance_password) | Yes | None |
| [`jdbc_url`](#jdbc_url) | Yes | None |
| [`ssl_enabled`](#ssl_enabled) | Yes | None |
| [`db_pem_file`](#db_pem_file) | Conditional | None |
| [`mas_config_scope`](#mas_config_scope) | Yes | None |
| [`mas_instance_id`](#mas_instance_id) | Yes | None |
| [`mas_workspace_id`](#mas_workspace_id) | Conditional | None |
| [`mas_application_id`](#mas_application_id) | Conditional | None |
| [`mas_config_dir`](#mas_config_dir) | Yes | None |
| [`custom_labels`](#custom_labels) | No | None |

`db_pem_file` is required when `ssl_enabled` is `true`; `mas_workspace_id` is required when `mas_config_scope` is `ws` or `wsapp`, and `mas_application_id` when the scope is `app` or `wsapp`.

### Database Connection

#### db_instance_id

Database instance identifier used in the generated configuration — an alphanumeric string, typically lowercase with no spaces (for example `maxdb01`, `manage-prod`, or `oracle-dev`).

- **Optional**
- Environment Variable: `DB_INSTANCE_ID`
- Default: `dbinst`

This ID is used to reference the database connection in application configurations and must be unique within the scope of the MAS instance; the default `dbinst` is suitable for simple single-database deployments, but use descriptive names in multi-database environments to avoid confusion.

#### db_username

Database username that MAS applications will use to connect to the database; the user must have the privileges the target application needs — for Manage, full access to the MAXIMO schema.

- **Required**
- Environment Variable: `MAS_JDBC_USER`
- Default: None

Insufficient permissions will cause application failures. For Oracle, the schema prefix may need to be included in some configurations, and the user should have appropriate connection limits configured in the database.

#### jdbc_instance_password

Password for the database user account specified in `db_username`.

- **Required**
- Environment Variable: `MAS_JDBC_PASSWORD`
- Default: None

The password is stored as a Kubernetes secret in the MAS namespace. Ensure the password doesn't contain characters that require URL encoding if it is embedded in connection strings.

#### jdbc_url

Complete JDBC connection string including host, port, database name, and connection parameters, formatted for the target database type — for example `jdbc:db2://dbserver.example.com:50000/maxdb` for IBM Db2 (insecure), `jdbc:db2://dbserver.example.com:50000/maxdb:sslConnection=true;` for Db2 (secure), or `jdbc:oracle:thin:@dbserver.example.com:1521:maximo` for Oracle.

- **Required**
- Environment Variable: `MAS_JDBC_URL`
- Default: None

SQL Server URLs take the form `jdbc:sqlserver://;serverName=dbserver.example.com;portNumber=1433;databaseName=maxdb;integratedSecurity=false;sendStringParametersAsUnicode=false;selectMethod=cursor;encrypt=false;trustServerCertificate=false;` — use `encrypt=true;trustServerCertificate=true;` for secure connections. Port numbers and database names must match your actual database, some databases require specific JDBC driver parameters for optimal performance, and the SSL/TLS settings must match `ssl_enabled` and the database server configuration. Always test the JDBC URL with a database client before using it in MAS.

#### ssl_enabled

Whether SSL/TLS encryption is enabled for the database connection — `true` (encryption enabled) or `false` (insecure connection).

- **Required**
- Environment Variable: `SSL_ENABLED`
- Default: None

Explicitly declares the SSL/TLS status for applications that cannot determine this from the JDBC URL alone; a mismatch with the SSL settings in `jdbc_url` will cause connection failures in some MAS applications. Always use `true` for production environments, and provide `db_pem_file` when it is set.

#### db_pem_file

Local file path to the database SSL/TLS certificate in PEM format — for example `/tmp/db-ca.pem` or `./certs/database-cert.pem`.

- **Optional**, required when `ssl_enabled` is `true`
- Environment Variable: `MAS_JDBC_CERT_LOCAL_FILE`
- Default: None

The certificate is embedded in the generated JdbcCfg resource; without the correct certificate, SSL connections will fail with certificate validation errors. The file must be accessible from the Ansible controller and be PEM format (Base64-encoded with BEGIN/END markers). For self-signed certificates this should be the CA certificate, and for commercial certificates you may need to include the full certificate chain.

### MAS Configuration

#### mas_config_scope

Configuration scope level at which the generated JDBC configuration will be available within MAS — `system` (all workspaces and applications), `ws` (a specific workspace), `app` (a specific application across all workspaces), or `wsapp` (a specific application in a specific workspace).

- **Required**
- Environment Variable: `MAS_CONFIG_SCOPE`
- Default: None

Use `system` for shared databases used by multiple applications, and `wsapp` for dedicated databases per workspace-application combination. The scope cannot be changed after creation; changing it requires recreating the configuration.

#### mas_instance_id

MAS instance identifier that the configuration is being generated for — typically 3-12 lowercase alphanumeric characters, case-sensitive, matching the instance ID used during MAS installation.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

The generated configuration is namespace-scoped to `mas-<instance_id>-core`; an incorrect instance ID will cause the configuration to be created in the wrong namespace.

#### mas_workspace_id

MAS workspace identifier for workspace-scoped configurations — for example `masdev`, `prod`, or `test`.

- **Required** if `mas_config_scope` is `ws` or `wsapp`
- Environment Variable: `MAS_WORKSPACE_ID`
- Default: None

The JDBC configuration will only be available to the specified workspace; the workspace must exist before applying the configuration. Use workspace-scoped configs for tenant isolation in multi-tenant deployments.

#### mas_application_id

MAS application identifier for application-scoped configurations — valid values are `manage`, `health`, `predict`, `monitor`, `assist`, `visualinspection`, `iot`, `optimizer`, and `safety`.

- **Required** if `mas_config_scope` is `app` or `wsapp`
- Environment Variable: `MAS_APP_ID`
- Default: None

The JDBC configuration will only be available to the specified application; the application must be installed before applying the configuration. Most commonly used with `manage` for Manage-specific databases.

#### mas_config_dir

Local directory path where the generated JdbcCfg YAML file will be saved — the directory is created if it doesn't exist.

- **Required**
- Environment Variable: `MAS_CONFIG_DIR`
- Default: None

The generated file is named `jdbccfg-<db_instance_id>.yml` and can be applied using `kubectl apply` or the [suite_config](suite_config.md) role; keep generated files for documentation and disaster recovery purposes.

### Resource Labels

#### custom_labels

Custom Kubernetes labels to apply to the generated JdbcCfg resource, as comma-separated key=value pairs — for example `env=prod,team=platform,cost-center=12345`.

- **Optional**
- Environment Variable: `CUSTOM_LABELS`
- Default: None

Labels are useful for environment identification, cost tracking, GitOps workflows, and selection with label selectors in automation scripts; they must follow Kubernetes naming conventions.


## Example Playbook

```yaml

- hosts: localhost
  any_errors_fatal: true
  roles:
    - ibm.mas_devops.gencfg_jdbc
```

## License
EPL-2.0
