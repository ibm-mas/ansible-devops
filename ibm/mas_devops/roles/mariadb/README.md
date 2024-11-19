# Mariadb
=====

This role provides support to install and configure MariaDB 

* Install MariaDB

Role Variables
--------------

### mariadb_namespace
Action to be performed by minio role. Valid values are `string`.

* Environment Variable: `MARIADB_NAMESPACE`
* Default Value: `mariadb`

### mariadb_instance_name
Action to be performed by minio role. Valid values are `string`.

* Environment Variable: `MARIADB_INSTANCE_NAME`
* Default Value: `mariadb-instance`

### mariadb_user
Action to be performed by minio role. Valid values are `string`.

* Environment Variable: `MARIADB_USER`
* Default Value: `mariadb`

### mariadb_password
Action to be performed by minio role. Valid values are `string`.
  
* Environment Variable: `MARIADB_PASSWORD`
* Default Value: ``

### mariadb_database
Action to be performed by minio role. Valid values are `string`.
  
* Environment Variable: `MARIADB_DATABASE`
* Default Value: `kmpipeline`


Example Playbook
----------------

```yaml
---
- hosts: localhost
  any_errors_fatal: true
  roles:
    - ibm.mas_devops.mariadb
```

License
-------

EPL-2.0
