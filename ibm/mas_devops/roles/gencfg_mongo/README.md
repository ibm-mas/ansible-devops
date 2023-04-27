gencfg_mongo
============

This role is used to generate mongo configuration in Maximo Application Suite
This generated mongo configuration can be used as an input to the [suite_config](suite_config.md) role, to configure a MAS instance to connect with an existing Mongo cluster

Role Variables
--------------

### mongodb_namespace
The generated Mongo Config file name will be suffixed with this namespace value eg, mongo-<<mongodb_namespace>>.yml

- Environment Variable: `MONGODB_NAMESPACE`
- Default: mongoce

### mongodb_admin_username
Required. MongoDB admin username

- Environment Variable: `MONGODB_ADMIN_USERNAME`
- Default: None

### mongodb_admin_password
Required. MongoDB admin password

- Environment Variable: `MONGODB_ADMIN_PASSWORD`
- Default: None

### mongodb_hosts
Required. In case if there are multiple instances, the host address should be seperated by a ,. Example: docdb-1.abc.ca-central-1.docdb.amazonaws.com:27017,docdb-2.def.ca-central-1.docdb.amazonaws.com:27017

- Environment Variable: `MONGODB_HOSTS`
- Default: None

### mongodb_retry_writes
Set to true if MongoDB support retryable writes. In case if retryable writes is not supported (like in case of Amazon DocumentDB), set to false

- Optional
- Environment Variable: `MONGODB_RETRY_WRITES`
- Default: `true`

### mongodb_ca_pem_local_file
Required. defines the CA pem file's local file path

- Environment Variable: `MONGODB_CA_PEM_LOCAL_FILE`
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
    mongodb_namespace: mongoce
    mongodb_admin_username: mongoadmin
    mongodb_admin_password: mongo-strong-password
    mongodb_hosts: docdb-1.abc.ca-central-1.docdb.amazonaws.com:27017,docdb-2.def.ca-central-1.docdb.amazonaws.com:27017
    mongodb_retry_writes: false
    mongodb_ca_pem_local_file: /tmp/mongo-ca.pem
    mas_instance_id: masinst1
    mas_config_dir: ~/masconfig  
  roles:
    - ibm.mas_devops.gencfg_mongo
```

License
-------

EPL-2.0
