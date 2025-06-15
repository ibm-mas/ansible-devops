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

* Environment Variable: `MAS_AIBROKER_TENANT_NAME`
* Default Value: `user`

### app_domain

The application domain for AI Broker role. Valid values is domain string `apps.domain`

* Environment Variable: `APP_DOMAIN`
* Default Value: ``

### mas_aibroker_s3_action

Action to be performed by AI Broker role. Valid values are `install` or `remove`

* Environment Variable: `MAS_AIBROKER_S3_ACTION`
* Default Value: `install`

### mas_aibroker_storage_host

The storge host for AI Broker role.

* Environment Variable: `MAS_AIBROKER_STORAGE_HOST`
* Default Value: ``

### mas_aibroker_storage_accesskey

The storage accesskey for AI Broker role.

* Environment Variable: `MAS_AIBROKER_STORAGE_ACCESSKEY`
* Default Value: ``

### mas_aibroker_storage_secretkey

The storage secretkey for AI Broker role. 

* Environment Variable: `MAS_AIBROKER_STORAGE_SECRETKEY`
* Default Value: ``

### mas_aibroker_storage_region

The storage region for AI Broker role.

* Environment Variable: `MAS_AIBROKER_STORAGE_REGION`
* Default Value: ``

### mas_aibroker_watsonx_action

Action to be performed by AI Broker role. Valid values are `install` or `remove`

* Environment Variable: `MAS_AIBROKER_WATSONX_ACTION`
* Default Value: `install`

### mas_aibroker_watsonxai_apikey

The watsonxai apikey for AI Broker role.

* Environment Variable: `MAS_AIBROKER_WATSONXAI_APIKEY`
* Default Value: ``

### mas_aibroker_watsonxai_url

The watsonxai url for AI Broker role.

* Environment Variable: `MAS_AIBROKER_WATSONXAI_URL`
* Default Value: ``

### mas_aibroker_watsonxai_project_id

The watsonxai project id for AI Broker role.

* Environment Variable: `MAS_AIBROKER_WATSONXAI_PROJECT_ID`
* Default Value: ``

License
-------

EPL-2.0
