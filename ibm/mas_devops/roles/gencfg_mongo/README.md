gencfg_mongo
============

This role is used to generate mongo configuration in Maximo Application Suite for the below providers:
  - Mongo
  - AWS Documentdb

This generated mongo configuration can be used as an input to the [suite_config](suite_config.md) role, to configure a MAS instance to connect with an existing Mongo cluster

Role Variables
--------------

### db_provider
Required.  Defines the provider that is used for the Mongo configure in MAS installation. If DB provider is Mongo, set DB_PROVIDER as mongo. If DB provider is AWS Documentdb, set DB_PROVIDER as documentdb

- Environment Variable: `DB_PROVIDER`
- Default: None

### mongo_namespace
The generated Mongo Config file name will be suffixed with this namespace value eg, mongo-<<mongo_namespace>>.yml

- Environment Variable: `MONGODB_NAMESPACE`
- Default: mongoce

### mongo_admin_username
Required. MongoDB admin username

- Environment Variable: `MONGO_ADMIN_USERNAME`
- Default: None

### mongo_admin_password
Required. MongoDB admin password

- Environment Variable: `MONGO_ADMIN_PASSWORD`
- Default: None

### mongo_hosts
Required. In case if there are multiple instances, the host address should be seperated by a ,. Example: docdb-1.abc.ca-central-1.docdb.amazonaws.com:27017,docdb-2.def.ca-central-1.docdb.amazonaws.com:27017

- Environment Variable: `MONGO_HOSTS`
- Default: None

### mongo_ca_pem_local_file
Required. defines the CA pem file's local file path

- Environment Variable: `MONGO_CA_PEM_LOCAL_FILE`
- Default: None

### mas_instance_id
Required. The instance ID of Maximo Application Suite for which the MongoCfg configuration will generate 

- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

### mas_config_dir
Required. Local directory to save the generated MongoCfg resource definition. This can be used as an input to the [suite_config](suite_config.md) role, to configure a MAS instance to connect with an existing Mongo cluster

- Environment Variable: `MAS_CONFIG_DIR`
- Default: None

Example Playbook
----------------

```yaml
---

- hosts: localhost
  any_errors_fatal: true 
  vars:
    db_provider: mongo
    mongo_namespace: mongoce
    mongo_admin_username: mongoadmin
    mongo_admin_password: mongo-strong-password
    mongo_hosts: docdb-1.abc.ca-central-1.docdb.amazonaws.com:27017,docdb-2.def.ca-central-1.docdb.amazonaws.com:27017
    mongo_ca_pem_local_file: /tmp/mongo-ca.pem
    mas_instance_id: masinst1
    mas_config_dir: ~/masconfig  
  roles:
    - ibm.mas_devops.gencfg_mongo
```

License
-------

EPL-2.0
