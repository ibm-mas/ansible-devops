# AI Broker
=====

This role provides support to install and configure AI Broker:

* Install AI Broker api application
* Create, delete AI Broker tenant
* Create, delete AI Broker API Key
* Create, delete AWS S3 API Key
* Create, delete WatsonX AI API Key

Role Variables
--------------

### tenant_action

Action to be performed by AI Broker role. Valid values are `install` or `remove` .

* Environment Variable: `TENANT_ACTION`
* Default Value: `install`

### tenantName

The tenant name for AI Broker role.

* Environment Variable: `AISERVICE_TENANT_NAME`
* Default Value: `user`

### app_domain

The application domain for AI Broker role. Valid values is domain string `apps.domain`

* Environment Variable: `APP_DOMAIN`
* Default Value: ``

### aiservice_storage_host

The storge host for AI Broker role.

* Environment Variable: `AISERVICE_STORAGE_HOST`
* Default Value: ``

### aiservice_storage_accesskey

The storage accesskey for AI Broker role.

* Environment Variable: `AISERVICE_STORAGE_ACCESSKEY`
* Default Value: ``

### aiservice_storage_secretkey

The storage secretkey for AI Broker role.

* Environment Variable: `AISERVICE_STORAGE_SECRETKEY`
* Default Value: ``

### aiservice_storage_region

The storage region for AI Broker role.

* Environment Variable: `AISERVICE_STORAGE_REGION`
* Default Value: ``

### aiservice_watsonx_action

Action to be performed by AI Broker role. Valid values are `install` or `remove`

* Environment Variable: `AISERVICE_WATSONX_ACTION`
* Default Value: `install`

### aiservice_watsonxai_apikey

The watsonxai apikey for AI Broker role.

* Environment Variable: `AISERVICE_WATSONXAI_APIKEY`
* Default Value: ``

### aiservice_watsonxai_url

The watsonxai url for AI Broker role.

* Environment Variable: `AISERVICE_WATSONXAI_URL`
* Default Value: ``

### aiservice_watsonxai_project_id

The watsonxai project id for AI Broker role.

* Environment Variable: `AISERVICE_WATSONXAI_PROJECT_ID`
* Default Value: ``

## Entitlement
Configure the tenant's entitlement to the AI Service.

### tenant_entitlement_type

Set the tenant's entitlement type.

* Environment Variable: `AISERVICE_TENANT_ENTITLEMENT_TYPE`

### tenant_entitlement_start_date

Set the tenant's entitlement start date in format `YYYY-MM-DD`.

* Environment Variable: `AISERVICE_TENANT_ENTITLEMENT_START_DATE`

### tenant_entitlement_end_date

Set the tenant's entitlement end date in format `YYYY-MM-DD`.

* Environment Variable: `AISERVICE_TENANT_ENTITLEMENT_END_DATE`


License
-------

EPL-2.0
