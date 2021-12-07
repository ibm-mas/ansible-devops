cp4d_install
============

This role installs [IBM Cloud Pak for Data](https://www.ibm.com/uk-en/products/cloud-pak-for-data) Operator in the target cluster.

Role Variables
--------------

- `cpd_version` CP4D version to be installed. Supported versions are `cpd35` (for CP4D 3.5) and `cpd40` (for CP4D 4.0)
- `cpd_registry_password` Holds the IBM Entitlement key
- `cpd_registry` cp.icr.io
- `cpd_registry_user` cp
- `cpd_meta_namespace` Namespace to be created and used for CP4D deployment. For CP4D 4.0 version, namespace will always be 'ibm-common-services' 
- `mas_channel` - Optionally, you can specify this property in case you want to install a CP4D version that is compatible with an specific MAS channel.

Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    cpd_version: "{{ lookup('env', 'CPD_VERSION') }}"
    cpd_registry: cp.icr.io
    cpd_registry_user: cp
    cpd_registry_password: "{{ lookup('env', 'CPD_ENTITLEMENT_KEY') }}"
    cpd_meta_namespace: cpd-meta-ops

    # CP4D service configuration
    cpd_storage_class: "{{ lookup('env', 'CPD_STORAGE_CLASS') }}"
    cpd_services:
      - db2wh
  roles:
    - ibm.mas_devops.cp4d_install
    - ibm.mas_devops.cp4d_install_services
```

License
-------

EPL-2.0
