Role Name
=========

This role install Maximo Appplication Suite Dependency stack

Requirements
------------

Openshift Cluster 4.X

Role Variables
--------------

- cpd_registry: cp.icr.io
- cpd_registry_user: cp
- cpd_registry_password: IBM Entitlement key
- cpd_meta_namespace: Namespace where CPD is supposed to be installed
- cpd_storage_class: Storage class to be used by cpd
- cpd_assemblies: List of assembly to be installed

Dependencies
------------

- community.kubernentes

Example Playbook
----------------
```
---
- hosts: localhost
  vars:
    cpd_registry: cp.icr.io
    cpd_registry_user: cp
    cpd_registry_password: XXX
    cpd_meta_namespace: cpd-meta-ops
    cpd_storage_class: ibmc-file-gold-gid
    cpd_assemblies:
      - db2wh
  roles:
    - mas.devops.dependencies
```
License
-------

Internal Use only

