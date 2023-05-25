gencfg_jdbc
============

This role is used to configure database in Maximo Application Suite. It will use the database SSL certificate if ssl_enabled flag is true. The`db_pem-file` defines the location of the pem file used for JDBC connection in MAS installation.

Role Variables
--------------

### mas_instance_id
Providing this and `mas_config_dir` will instruct the role to generate a JdbcCfg template that can be used to configure MAS to connect to this database.

- Environment Variable: `MAS_INSTANCE_ID`
- Default: None
- 
### mas_workspace_id
This is only used when both `mas_config_dir` and `mas_instance_id` are set, and `mas_config_scope` is set to either `ws` or `wsapp`

- Environment Variable: `MAS_WORKSPACE_ID`
- Default: None

### db_instance_id
Defines the instance id that is used for the db configure in MAS installation

- Environment Variable: `DB_INSTANCE_ID`
- Default: `dbinst`

### db_username
Defines the username that is used for the db configure in MAS installation

- Environment Variable: `MAS_JDBC_USER`
- Default: None
- 
### jdbc_instance_password
Defines the password that is used to connect to db in MAS installation

- Environment Variable: `MAS_JDBC_PASSWORD`
- Default: None
- 
### jdbc_url
Defines the jdbc url  that is used to connect to db in MAS installation , Append ;sslConnection=true to the URL so that it has the form jdbc:db2://hostname:port/database_name:sslConnection=true .

- Environment Variable: `MAS_JDBC_URL`
- Default: None
- 
### db_pem_file
Defines the location of the pem file used for JDBC connection in MAS installation

- Environment Variable: `MAS_JDBC_CERT_LOCAL_FILE`
- Default: None

### custom_labels
List of comma separated key=value pairs for setting custom labels on instance specific resources.

- Optional
- Environment Variable: `CUSTOM_LABELS`
- Default: None


Example Playbook
----------------

```yaml
---

- hosts: localhost
  any_errors_fatal: true  
  roles:
    - ibm.mas_devops.gencfg_jdbc
```

License
-------

EPL-2.0
