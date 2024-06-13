
wipe_mongo
============

This role removes all databases associated with the specified MAS instance ID from the chosen MongoDB instance.

Role Variables
--------------

### instance_id
The specified MAS instance ID

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### mongo_username
Mongo Username

- Environment Variable: `MONGO_USERNAME`
- Default Value: None

### mongo_password
Mongo password

- Environment Variable: `MONGO_PASSWORD`
- Default Value: None

### mongo_uri
Mongo URI

- Environment Variable: `MONGO_URI`
- Default Value: None

### config
Path to the mas config directory. 

- **Required**
- Environment Variable: `CONFIG`
- Default Value: None

### certificates
Boolean flag to indicate whether to run role in gitops mode. True means that no openshift resources
are created on the cluster. 

- **Required**
- Environment Variable: `CERTIFICATES`
- Default Value: None


Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    instance_id: masinst1
    config: True
    certificates: /Users/johnbarnes/Document/masconfig
  roles:
    - ibm.mas_devops.suite_certs

```



License
-------

EPL-2.0
