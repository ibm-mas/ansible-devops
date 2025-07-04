# Minio
=====

This role provides support to install and configure Minio Storage

* Install Minio storage

Role Variables
--------------

### minio_namespace
Action to be performed by minio role. Valid values are `string`.

* Optional
* Environment Variable: `MINIO_NAMESPACE`
* Default Value: `minio`

### minio_instance_name
Action to be performed by minio role. Valid values are `string`.

* Optional
* Environment Variable: `MINIO_INSTANCE_NAME`
* Default Value: `minio`

### minio_root_user
Action to be performed by minio role. Valid values are `string`.

* Optional
* Environment Variable: `MINIO_ROOT_USER`
* Default Value: `minio`

### minio_root_password
Action to be performed by minio role. Valid values are `string`.

* **Required**
* Environment Variable: `MINIO_ROOT_PASSWORD`
* Default Value: ``

Example Playbook
----------------

```yaml
---
- hosts: localhost
  any_errors_fatal: true
  roles:
    - ibm.mas_devops.minio
```

License
-------

EPL-2.0
