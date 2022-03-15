cp4d_install
============

This role installs [IBM Cloud Pak for Data](https://www.ibm.com/uk-en/products/cloud-pak-for-data) Operator in the target cluster.  Support is available for both CP4D v3.5 (installed into the `cpd-meta-ops` namespace) and CP4D v4.0 (installed into the `ibm-common-services` namespace).

If you are installing CP4D v4 then the [cp4d_hack_worker_nodes](cp4d_hack_worker_nodes.md) role must have been executed during cluster set up to update the cluster's global image pull secret and reload all worker nodes.

The role assumes that you have already installed the IBM Operator Catalog in the target cluster.  This action is performed by the [ocp_setup_mas_deps](ocp_setup_mas_deps.md) role if you want to use this collection to install the CatalogSource.


Role Variables
--------------

### cpd_version
Required.  CP4D version to be installed. Supported versions are `cpd35` (for CP4D 3.5) and `cpd40` (for CP4D 4.0)

- Environment Variable: `CPD_VERSION`
- Default: None

### cpd_entitlement_key
Required only if `cpd_version = cpd35`, otherwise unused because in CP4D v4 we have to use the [cp4d_hack_worker_nodes](cp4d_hack_worker_nodes.md) role to prepare the cluster ahead of time by setting up a global image pull secret for CP4D.  Holds your IBM Entitlement key.

- Environment Variable: `CPD_ENTITLEMENT_KEY`
- Default: None

### cpd_storage_class
Required only if `cpd_version = cpd40`, otherwise unused. 

- Environment Variable: `CPD_STORAGE_CLASS`
- Default Value: None

Note: As per CloudPak For Data support team's recommendation, the value set for `cpd_storage_class` will also be used for file and metastore storages while installing CPD v4.0 Control Plane.
Source: https://www.ibm.com/docs/en/cloud-paks/cp-data/4.0?topic=requirements-storage

### mas_channel
You can specify this property as an alternative to `cpd_version` to allow the role to automatically select the appropriate version of CP4D based on the MAS Channel you are subscribing to.  If `cpd_version` is set, then this is ignored.

- Environment Variable: `MAS_CHANNEL`
- Default: None


Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    cpd_version: cpd40
    cpd_storage_class: ibmc-file-gold-gid
  roles:
    - ibm.mas_devops.cp4d_install
```

License
-------

EPL-2.0
