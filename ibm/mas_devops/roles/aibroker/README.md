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

* Environment Variable: `TENANT_NAME`
* Default Value: `user`

### app_domain

The application domain for AI Broker role. Valid values is domain string `apps.domain`

* Environment Variable: `APP_DOMAIN`
* Default Value: ``

### s3_action

Action to be performed by AI Broker role. Valid values are `install` or `remove`

* Environment Variable: `S3_ACTION`
* Default Value: `install`

### storage_host

The storge host for AI Broker role.

* Environment Variable: `STORAGE_HOST`
* Default Value: ``

### storage_accesskey

The storage accesskey for AI Broker role.

* Environment Variable: `STORAGE_ACCESSKEY`
* Default Value: ``

### storage_secretkey

The storage secretkey for AI Broker role. 

* Environment Variable: `STORAGE_SECRETKEY`
* Default Value: ``

### storage_region

The storage region for AI Broker role.

* Environment Variable: `STORAGE_REGION`
* Default Value: ``

### watsonx_action

Action to be performed by AI Broker role. Valid values are `install` or `remove`

* Environment Variable: `WATSONX_ACTION`
* Default Value: `install`

### watsonxai_apikey

The watsonxai apikey for AI Broker role.

* Environment Variable: `WATSONXAI_APIKEY`
* Default Value: ``

### watsonxai_url

The watsonxai url for AI Broker role.

* Environment Variable: `WATSONXAI_URL`
* Default Value: ``

### watsonxai_project_id

The watsonxai project id for AI Broker role.

* Environment Variable: `WATSONXAI_PROJECT_ID`
* Default Value: ``

License
-------

EPL-2.0
