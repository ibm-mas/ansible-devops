# AI Service

=====

This role provides support to install and configure AI Service:

* Install AI Service api application
* Create, delete AI Service tenant
* Create, delete AI Service API Key
* Create, delete AWS S3 API Key
* Create, delete WatsonX AI API Key

Role Variables
--------------

### tenant_action

Action to be performed by AI Service role. Valid values are `install` or `remove` .

* Environment Variable: `TENANT_ACTION`
* Default Value: `install`

### tenantName

The tenant name for AI Service role.

* Environment Variable: `AISERVICE_TENANT_NAME`
* Default Value: `user`

### app_domain

The application domain for AI Service role. Valid values is domain string `apps.domain`

* Environment Variable: `APP_DOMAIN`
* Default Value: ``

### aiservice_s3_host

The storge host for AI Service role.

* Environment Variable: `AISERVICE_S3_HOST`
* Default Value: ``

### aiservice_s3_accesskey

The storage accesskey for AI Service role.

* Environment Variable: `AISERVICE_S3_ACCESSKEY`
* Default Value: ``

### aiservice_s3_secretkey

The storage secretkey for AI Service role.

* Environment Variable: `AISERVICE_S3_SECRETKEY`
* Default Value: ``

### aiservice_s3_region

The storage region for AI Service role.

* Environment Variable: `AISERVICE_S3_REGION`
* Default Value: ``

### aiservice_watsonx_action

Action to be performed by AI Service role. Valid values are `install` or `remove`

* Environment Variable: `AISERVICE_WATSONX_ACTION`
* Default Value: `install`

### aiservice_watsonxai_apikey

The watsonxai apikey for AI Service role.

* Environment Variable: `AISERVICE_WATSONXAI_APIKEY`
* Default Value: ``

### aiservice_watsonxai_url

The watsonxai url for AI Service role.

* Environment Variable: `AISERVICE_WATSONXAI_URL`
* Default Value: ``

### aiservice_watsonxai_project_id

The watsonxai project id for AI Service role.

* Environment Variable: `AISERVICE_WATSONXAI_PROJECT_ID`
* Default Value: ``

### aiservice_domain

Provide custom domain (default value is: empty)
* Environment Variable: `AISERVICE_DOMAIN`
* Default Value: ``


License
-------

EPL-2.0
