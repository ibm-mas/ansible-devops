gencfg_jdbc
============

This role is used to configure database in Maximo Application Suite. It will use the database SSL certificate if ssl_enabled flag is true. The`db_pem-file` defines the location of the pem file used for JDBC connection in MAS installation.

Role Variables - Data Source
-------------------------------------------------------------------------------
### db_instance_id
Defines the instance id that is used for the db configure in MAS installation

- **Required**
- Environment Variable: `DB_INSTANCE_ID`
- Default: `dbinst`

### db_username
Defines the username that is used for the db configure in MAS installation

- **Required**
- Environment Variable: `MAS_JDBC_USER`
- Default: None

### jdbc_instance_password
Defines the password that is used to connect to db in MAS installation

- **Required**
- Environment Variable: `MAS_JDBC_PASSWORD`
- Default: None

### jdbc_url
Defines the jdbc URL that is used to connect to db in MAS installation:

- **Required**
- Environment Variable: `MAS_JDBC_URL`
- Default: None

!!! tip
    Example URL strings:

    - IBM Db2 (insecure): `jdbc:db2://dbserverxx:50000/maxdbxx`
    - IBM Db2 (secure): `jdbc:db2://dbserverxx:50000/maxdbxx:sslConnection=true`
    - Oracle Database: `jdbc:oracle:thin:@dbserverxx:1521:maximo`
    - Microsoft SQL Server (insecure): `jdbc:sqlserver://;serverName=dbserverxx;portNumber=1433;databaseName=msdbxx;integratedSecurity=false;sendStringParametersAsUnicode=false;selectMethod=cursor;encrypt=false;trustServerCertificate=false;`
    - Microsoft SQL Server (secure): `jdbc:sqlserver://;serverName=dbserverxx;portNumber=1433;databaseName=msdbxx;integratedSecurity=false;sendStringParametersAsUnicode=false;selectMethod=cursor;encrypt=true;trustServerCertificate=true;`

### db_pem_file
Defines the location of the pem file used for JDBC connection in MAS installation

- Optional
- Environment Variable: `MAS_JDBC_CERT_LOCAL_FILE`
- Default: None


Role Variables - MAS Configuration
-------------------------------------------------------------------------------
### mas_config_scope
Configure whether to generate a binding suitable for System, Workspace, Application, or Workspace-Application use within MAS (`system`, `ws`, `app`, or `wsapp`).

- **Required**
- Environment Variable: `MAS_CONFIG_SCOPE`
- Default: None

### mas_config_dir
Configure the destination directory for the generated yaml file.

- **Required**
- Environment Variable: `MAS_CONFIG_DIR`
- Default: None

### mas_instance_id
MAS Instance ID we are generating a configuration for.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

### mas_workspace_id
Set the workspace ID when generating a configuration for workspace or workspace-application scope.

- **Required** if `mas_config_scope` is set to either `ws` or `wsapp`
- Environment Variable: `MAS_WORKSPACE_ID`
- Default: None

### mas_application_id
Set the application ID when generating a configuration for application or workspace-application scope.

- **Required** if `mas_config_scope` is set to either `app` or `wsapp`
- Environment Variable: `MAS_APP_ID`
- Default: None

### ssl_enabled
Some applications in MAS are unable to determine whether SSL is enabled or disable via the JDBC string, and require this additional setting.  Make sure to set this to match the setting in `jdbc_url`.

- **Required**
- Environment Variable: `SSL_ENABLED`
- Default: None

### custom_labels
List of comma separated key=value pairs for setting custom labels on instance specific resources.

- Optional
- Environment Variable: `CUSTOM_LABELS`
- Default: None


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
