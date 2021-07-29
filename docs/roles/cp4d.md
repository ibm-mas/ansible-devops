# CP4D Roles

## cp4d_db2wh

!!! important "TODO"
    Document this

----

## cp4d_db2wh_manage_hack

!!! important "TODO"
    Document this

----

## cp4d_db2wh_restore
Currently not supported. This role will perform database restore on the db2wh instance created by this ansible collection.

!!! important "TODO"
    Implement & document this, or we delete it from master

----

## cp4d_install
This role installs the [Cloud Pak for Data](https://www.ibm.com/uk-en/products/cloud-pak-for-data) Operator in the target cluster.

### Role facts

- `cpd_registry_password` Holds the IBM Entitlement key
- `cpd_registry` cp.icr.io
- `cpd_registry_user` cp
- `cpd_meta_namespace` Namespace to be created and used for CP4D deployment

----

## cp4d_install_services

!!! important "TODO"
    Document this
