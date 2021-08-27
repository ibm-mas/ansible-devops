cp4d_install
============

This role installs [IBM Cloud Pak for Data](https://www.ibm.com/uk-en/products/cloud-pak-for-data) Operator in the target cluster.

Role Variables
--------------

- `cpd_registry_password` Holds the IBM Entitlement key
- `cpd_registry` cp.icr.io
- `cpd_registry_user` cp
- `cpd_meta_namespace` Namespace to be created and used for CP4D deployment


Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    cpd_registry: cp.icr.io
    cpd_registry_user: cp
    cpd_registry_password: "{{ lookup('env', 'CPD_ENTITLEMENT_KEY') }}"
    cpd_meta_namespace: cpd-meta-ops

    # CP4D service configuration
    cpd_storage_class: "{{ lookup('env', 'CPD_STORAGE_CLASS') }}"
    cpd_services:
      - lite
  roles:
    - ibm.mas_devops.cp4d_install
    - ibm.mas_devops.cp4d_install_services
```

License
-------

EPL-2.0
