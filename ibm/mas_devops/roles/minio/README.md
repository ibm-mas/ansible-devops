# Minio
=====

This role provides support to install and configure Minio Storage

* Install Minio storage

Role Variables
--------------

### minio_namespace
Define namespace where minio will be installed.

* Optional
* Environment Variable: `MINIO_NAMESPACE`
* Default Value: `minio`

### minio_instance_name
instance name for minio.

* Optional
* Environment Variable: `MINIO_INSTANCE_NAME`
* Default Value: `minio`

### minio_root_user
root username for minio

* Optional
* Environment Variable: `MINIO_ROOT_USER`
* Default Value: `minio`

### minio_root_password
password for minio root user.

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
