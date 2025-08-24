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

### aiservice_s3_action

Action to be performed by AI Broker role. Valid values are `install` or `remove`

* Environment Variable: `AISERVICE_S3_ACTION`
* Default Value: `install`

### aiservice_s3_host

The storge host for AI Broker role.

* Environment Variable: `AISERVICE_S3_HOST`
* Default Value: ``

### aiservice_s3_accesskey

The storage accesskey for AI Broker role.

* Environment Variable: `AISERVICE_S3_ACCESSKEY`
* Default Value: ``

### aiservice_s3_secretkey

The storage secretkey for AI Broker role.

* Environment Variable: `AISERVICE_S3_SECRETKEY`
* Default Value: ``

### aiservice_s3_region

The storage region for AI Broker role.

* Environment Variable: `AISERVICE_S3_REGION`
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

## S3
The following variables configure S3-compatible storage (e.g. AWS, Minio). Similar variables
can also be defined in the `aiservice` role for setting shared configuration
across all tenants. Configuration defined here at the tenant-level will take precedence.

### aiservice_s3_region

Set the S3 region.

* Environment Variable: `AISERVICE_TENANT_S3_REGION`
* Default Value: ``

### aiservice_s3_endpoint_url

Set the S3 endpoint URL.

* Environment Variable: `AISERVICE_TENANT_S3_ENDPOINT_URL`
* Default Value: ``

### aiservice_s3_bucket_prefix

Set the S3 bucket prefix.

* Environment Variable: `AISERVICE_TENANT_S3_BUCKET_PREFIX`
* Default Value: ``

### aiservice_s3_access_key

Set the S3 access key ID.

* Environment Variable: `AISERVICE_TENANT_S3_ACCESS_KEY`

### aiservice_s3_secret_key

Set the S3 secret access key.

* Environment Variable: `AISERVICE_TENANT_S3_SECRET_KEY`


License
-------

EPL-2.0
