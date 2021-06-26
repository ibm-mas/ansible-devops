# MAS Roles
The following set of roles does provide support to install Maximo Application Suite and Manage application using their operator resources.


## suite_appinstall_manage
This role does provide the capability of installing Manage in the target cluster. Before you use this role make sure you have installed MAS and have a valid JdbcCfg and it points to a database that is pré configured for Manage.

!!! warning "Warning"
    This role does install Manage using it's OLM resources, it's not recommended to use it with MAS versions bellow 8.5, since you won't have the ability to manage your application from MAS UI but from Openshift Console.

### Role facts
- mas_instance_id: Defines the instance id of Maximo Application Suite where Manage must be installed.


## suite_cleanup
This role provides support to Uninstall Maximo Application Suite and wipe data of the configured MongoDb instace associated to the Maximo Application Suite instance.

### Role facts
- mas_instance_id: Defines the instance id to be used for MAS installation to be cleaned up


## suite_install
This role provides support to Install Maximo Application Suite

### Role facts

- `mas_catalog_source` Defines the catalog to be used to install MAS. You can set it to      ibm-operator-catalog for release install or ibm-mas-operators for development
- `artifactory_username` Required when using this role for development versions of MAS
- `artifactory_apikey` Required when using this role for development versions of MAS
- `mas_channel` Defines which channel of MAS to subscribe to
- `mas_domain` Opitional fact, if not provided the role will use the default cluster subdomain
- `mas_instance_id` Defines the instance id to be used for MAS installation
- `mas_icr_cp` Defines the entitled registry from the images should be pulled from. Set this to `cp.icr.io/cp` when installing release version of MAS or `wiotp-docker-local.artifactory.swg-devops.com` for dev
- `mas_icr_cpopen` Defines the registry for non entitled images, such as operators. Set this to `icr.io/cpopen` when installing release version of MAS or `wiotp-docker-local.artifactory.swg-devops.com` for dev
- `mas_entitlement_username` Username for entitled registry. This username will be used to create the image pull secret. Set to `cp` when installing release or use your `w3Id` for dev.
- `mas_entitlement_key` API Key for entitled registry. This password will be used to create the image pull secret. Set to with IBM entitlement key when installing release or use your artifactory `apikey` for dev.
- `mas_config` List of configuration files to be applied to configure the MAS installation


## suite_verify
This role will verify a Maximo Application Suite installation and provides the admin dashboard URL and Superuser credentials.

### Role facts

- `mas_instance_id` Defines the instance id to be used for MAS installation to be cleanedup