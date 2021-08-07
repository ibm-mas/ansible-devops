# CP4D Roles

## cp4d_install
This role installs the [Cloud Pak for Data](https://www.ibm.com/uk-en/products/cloud-pak-for-data) Operator in the target cluster.

### Role facts

- `cpd_registry_password` Holds the IBM Entitlement key
- `cpd_registry` cp.icr.io
- `cpd_registry_user` cp
- `cpd_meta_namespace` Namespace to be created and used for CP4D deployment
