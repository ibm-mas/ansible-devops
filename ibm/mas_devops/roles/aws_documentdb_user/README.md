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
Required. AWS DocumentDB Instance Host Address

- Environment Variable: `DOCDB_HOST`

### docdb_port
Required. AWS DocumentDB Port Address

- Environment Variable: `DOCDB_PORT`

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