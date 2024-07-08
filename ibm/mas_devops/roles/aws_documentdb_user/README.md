aws_documentdb_user
-----------------------
This role creates a docdb user for MAS instance and saves username and password as k8 Secret in specified config directory

## Prerequisites
To run this role with providers you must have already installed the [Mongo Shell](https://www.mongodb.com/docs/mongodb-shell/install/).

Role variables
=================

### mas_instance_id
Required.The instance ID of Maximo Application Suite required for creating docdb user credentials secret

- Environment Variable: `MAS_INSTANCE_ID`

### docdb_host
AWS DocumentDB Instance Host Address, Required if docdb_hosts is not set

- Environment Variable: `DOCDB_HOST`

### docdb_port
AWS DocumentDB Port Address, Required if docdb_hosts is not set

- Environment Variable: `DOCDB_PORT`

### docdb_hosts
AWS DocumentDB Instance Host Address & Port Address, Required if both docdb_host & docdb_port are not set

- Environment Variable: `DOCDB_HOSTS`

### docdb_master_username
Required. AWS DocumentDB Master Username

- Environment Variable: `DOCDB_MASTER_USERNAME`

### docdb_master_password
Required. AWS DocumentDB Master Password

- Environment Variable: `DOCDB_MASTER_PASSWORD`

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    docdb_master_username: test-user
    docdb_master_password: test-pass-***
    docdb_host: test1.aws-01....
    docdb_port: 27017

  roles:
    - ibm.mas_devops.aws_documentdb_user
```

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    docdb_master_username: test-user
    docdb_master_password: test-pass-***
    docdb_hosts: test1.aws-01:27017,test1.aws-02:27017,test1.aws-03:27017

  roles:
    - ibm.mas_devops.aws_documentdb_user
```