# SLS Role
The following role provide support to install Suite License Service and generate configuration that can be directly applied to Maximo Application Suite to support full automation of the deployment and configuration of a complete MAS system including the license system.

### Role facts
- `mas_instance_id` The instance ID of Maximo Application Suite that the KafkaCfg configuration will target, there
- `sls_catalog_source` Defines the catalog to be used to install SLS. You can set it to      ibm-operator-catalog for release install or ibm-sls-operators for development
- `sls_channel`  Defines which channel of MAS to subscribe to
- `sls_namespace`  Defined the namespace where sls must be installed
- `sls_icr_cp` when installing release version of MAS or `wiotp-docker-local.artifactory.swg-devops.com` for dev
- `sls_icr_cpopen` when installing release version of MAS or `wiotp-docker-local.artifactory.swg-devops.com` for dev
- `sls_instance_name` Defines the instance id to be used for SLS installation
- `sls_entitlement_username` Username for entitled registry. This username will be used to create the image pull secret. Set to `cp` when installing release or use your `w3Id` for dev.
- `sls_entitlement_key`  API Key for entitled registry. This password will be used to create the image pull secret. Set to with IBM entitlement key when installing release or use your
- `artifactory_username`: Required when using this role for development versions of SLS
- `artifactory_apikey` Required when using this role for development versions of SLS
- `sls_storage_class` Defines the Storage Class that can be used by SLS to store data

!!! note
    Use the follwing when using with MAS
- `mas_config_dir` Defines the directory from where some configs can be pulled from including the entitlement file and mongo configuration
- `mas_instance_id` Used to generate a output slscfg file for MAS
- `sls_cfg_file` Defines the destination dir for the generated SLS configuration for MAS

!!! note
    Use the following to setup mongodb to be used with SLS
- `mongodb_cfg_file` Defines the path to the mongodb configuration used with MAS, when defined the SLS role will extract the configuration from there.

- `mongodb` Defines custom configuration for mongodb to be used with SLS, all the follwing facts are required when this fact is defined
- mongodb.hosts Defines list of host and port pair for MongoDb to be used with SLS

- `mongodb.username` Defines the MongoDB Username
- `mongodb.password` Defines the MongoDb Password

!!! note
    Bootstrap is used to initialize SLS, provide if you do have a lic file and licenseId you want to use
- `bootstrap` Parent fact that holds the boostrapped values
- `bootstrap.license_id` Defines the License Id to be used to bootstrap SLS
- `bootstrap.registration_key`  Defines the Registration Key to be used to bootstrap SLS
- `bootstrap.entitlement_file` Defines the License File to be used to bootstrap SLS