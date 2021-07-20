# CP4D Roles

## cp4d
This role installs the [Cloud Pak for Data](https://www.ibm.com/uk-en/products/cloud-pak-for-data) Operator in the target cluster.

### Role facts

- `cpd_registry_password` Holds the IBM Entitlement key
- `cpd_registry` cp.icr.io
- `cpd_registry_user` cp
- `cpd_meta_namespace` Namespace to be created and used for CP4D deployment


## cp4d_db2wh
This role deploys a CPDService with serviceName of db2wh on the target cluster and generates a JdbcCfg file that can be used by MAS.

### Role facts

- `cpd_meta_namespace` Namespace to be created and used for CP4D deployment, should be the same as the CP4D namespace
- `cpd_storage_class` Storage Class to be used withing the DB2Wh Persistent Volumes
- `db2wh_version` Db2u version to be used within the Db2wh CPDService
- `db2wh_dbname` Used to set DB name in the Db2wh service instance
- `mas_instance_id` MAS Instance Name where the JdbcCfg is going to be used
- `db2wh_cfg_file` Path for the generated JdbcCfg file i.e `/tmp/jdbccfg-cp4ddb2wh-system.yaml`


## cp4d_db2wh_restore
Currently not supported. This role will perform database restore on the db2wh instance created by this ansible collection.

!!! important "TODO"
    Implement & document this, or we delete it from master


## cp4d_spark
Enables Spark assembly on the CP4D instance deployed by this collection.

## cp4d_aiopenscale
Enables OpenScale assembly on the CP4D instance deployed by this collection.

## cp4d_wsl
Enables Watson Studio assembly on the CP4D instance deployed by this collection.

## cp4d_wml
Enables Watson Machine Learning assembly on the CP4D instance deployed by this collection.
