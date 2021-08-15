# MAS Roles
The following set of roles does provide support to install Maximo Application Suite and Manage application using their operator resources.


## dns_setup
This role will manage MAS and DNS provider integration.  IBM Cloud Internet Services is the only supported DNS provider currently.


### Cloud Internet Services (CIS)
This role will create DNS entries automatically in the CIS service instance.  Two different modes are available:

#### Top Level DNS entries
This mode will create the entries directly using your DNS zone value. It is usually recommended when you have 1x1 relationship between MAS Instance -> CIS service. e.g: mas.whirlpool.com, where the domain matches exactly the CIS zone name.

#### Subdomain DNS entries
This mode will create entries using a subdomain. It allows you to have multiple MAS instances using same CIS service. e.g: dev.mas.whirlpool.com, where 'dev' is the subdomain.

#### Webhook
The Webhook Task will deploy a cert-manager webhook for CIS integration.  The webhook is responsible for managent the certificate challenge requests from letsencrypt and CIS.  This task will also create two ClusterIssuers by default, pointing to Staging & Production LetsEncrypt servers.

!!! warning
    We need to support a seperate `cis_apikey` property, because the API key provided will be stored in a secret in the cluster used by the webhook to create challenge request files in your DNS. We should support the ability to set the API key used here seperate from the main IBMCloud API key used elsewhere so that it can be restricted to only the permissions required by CIS.

----

## suite_app_configure

!!! important "TODO"
    Document this

----

## suite_app_install

!!! important "TODO"
    Document this

----

## suite_cleanup
This role provides support to Uninstall Maximo Application Suite and wipe data of the configured MongoDb instace associated to the Maximo Application Suite instance.

### Role facts
- `mas_instance_id` Defines the instance id to be used for MAS installation to be cleaned up

----

## suite_config

!!! important "TODO"
    Document this

----

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

----

## suite_verify
This role will verify a Maximo Application Suite installation and provides the admin dashboard URL and Superuser credentials.

### Role facts

- `mas_instance_id` Defines the instance id to be used for MAS installation to be cleanedup