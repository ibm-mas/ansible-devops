# CP4D Roles
!!! note "Note"
    The following roles does not support development versions of CP4D

## cp4d
!!! warning "Make Sure"
    Always use `cp` as username since this role install CP4D released image versions

This role install Cloud Pak for Data Operator in the target cluster. 

### Role facts
List of role facts defined by a playbook and required by this role.

- cpd_registry_password: Holds the IBM Entitlement key 
- cpd_registry: cp.icr.io
- cpd_registry_user: cp 
- cpd_meta_namespace: Namespace to be created and used for CP4D deployment

## cp4d_db2wh
This role deploys a CPDService with serviceName of db2wh on the target cluster. This role also generated a JdbcCfg file that can be used by MAS.

### Role facts
List of role facts defined by a playbook and required by this role.

- cpd_meta_namespace: Namespace to be created and used for CP4D deployment, should be the same as the CP4D namespace
- cpd_storage_class: Storage Class to be used withing the DB2Wh Persistent Volumes
- db2wh_version: Db2u version to be used within the Db2wh CPDService
- db2wh_dbname: Used to set DB name in the Db2wh service instance

#### Create the MAS JdbcCfg & Secret resource definitions

- mas_instance_id: MAS Instance Name where the JdbcCfg is going to be used
- db2wh_cfg_file: Path for the generated JdbcCfg file i.e `/tmp/jdbccfg-cp4ddb2wh-system.yaml`


## cp4d_db2wh_restore
Current not supported. This role will performe database restore on db2wh instance created by this ansible collection.

## cp4d_spark
Enables Spark assembly on the CP4D instance deployed by this collection.
