# Mariadb
=====

This role provides support to install and configure MariaDB 

* Install MariaDB

Role Variables
--------------

### mas_instance_id
The instance ID of Maximo Application Suite.

* **Required**
* Environment Variable: `MAS_INSTANCE_ID`
* Default Value: ""

### mariadb_namespace
Define the namespace where mariadb will be installed.

* Optional
* Environment Variable: `MARIADB_NAMESPACE`
* Default Value: `mariadb`

### mariadb_instance_name
Define name of mariadb instance.

* Optional
* Environment Variable: `MARIADB_INSTANCE_NAME`
* Default Value: `mariadb-instance`

### mariadb_user
username for mariadb.

* Optional
* Environment Variable: `MARIADB_USER`
* Default Value: `mariadb`

### mariadb_password
password for mariadb user.

* **Required**
* Environment Variable: `MARIADB_PASSWORD`
* Default Value: ``

### mariadb_database
Define name of mariadb database.

* Optional  
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
