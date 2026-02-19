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
Action to perform on the AI Broker tenant.

- Optional
- Environment Variable: `TENANT_ACTION`
- Default: `install`

**Purpose**: Controls whether to create/configure or remove an AI Broker tenant.

**When to use**: Set to `install` for tenant creation/configuration. Use `remove` to delete a tenant.

**Valid values**:
- `install` - Create or configure AI Broker tenant (default)
- `remove` - Delete AI Broker tenant

**Impact**: Determines whether tenant resources are created or removed. Removal is permanent and deletes all tenant data.

**Related variables**: [`tenantID`](#tenantid)

**Notes**: **Warning** - `remove` action permanently deletes the tenant and all associated data.

### tenantID
Unique identifier for the AI Broker tenant.

- Optional
- Environment Variable: `AISERVICE_TENANT_ID`
- Default: `user`

**Purpose**: Identifies the AI Broker tenant for resource isolation and management in multi-tenant deployments.

**When to use**: Override the default when creating multiple tenants or when organizational naming conventions require specific identifiers.

**Valid values**: Alphanumeric string (e.g., `user`, `team1`, `prod-tenant`)

**Impact**: Determines the tenant context for all AI Broker resources and API keys.

**Related variables**: [`tenant_action`](#tenant_action), [`tenant_entitlement_type`](#tenant_entitlement_type)

**Notes**: The default `user` is suitable for single-tenant deployments. Use descriptive names for multi-tenant environments.

### app_domain
Application domain for AI Broker API endpoints.

- Optional
- Environment Variable: `APP_DOMAIN`
- Default: None (empty string)

**Purpose**: Specifies the base domain for AI Broker application routes and API endpoints.

**When to use**: Required for AI Broker installation. Must match the OpenShift cluster's application domain.

**Valid values**: Valid domain string in format `apps.domain` (e.g., `apps.cluster.example.com`)

**Impact**: Determines the URLs for AI Broker API endpoints. Incorrect domain will prevent API access.

**Related variables**: None

**Notes**:
- Get cluster domain: `oc get ingress.config cluster -o jsonpath='{.spec.domain}'`
- Format must be the full apps domain (e.g., `apps.mycluster.example.com`)

### aiservice_watsonx_action
Action to perform on WatsonX AI integration.

- Optional
- Environment Variable: `AISERVICE_WATSONX_ACTION`
- Default: `install`

**Purpose**: Controls whether to configure or remove WatsonX AI integration for the tenant.

**When to use**: Set to `install` to configure WatsonX AI credentials. Use `remove` to delete WatsonX AI integration.

**Valid values**:
- `install` - Configure WatsonX AI integration (default)
- `remove` - Remove WatsonX AI integration

**Impact**: Determines whether WatsonX AI API keys and configuration are created or removed for the tenant.

**Related variables**: [`aiservice_watsonxai_apikey`](#aiservice_watsonxai_apikey), [`aiservice_watsonxai_url`](#aiservice_watsonxai_url), [`aiservice_watsonxai_project_id`](#aiservice_watsonxai_project_id)

**Notes**: WatsonX AI integration enables AI model access through IBM watsonx.ai platform.

### aiservice_watsonxai_apikey
WatsonX AI API key for authentication.

- Optional
- Environment Variable: `AISERVICE_WATSONXAI_APIKEY`
- Default: None (empty string)

**Purpose**: Provides authentication credentials for accessing WatsonX AI services.

**When to use**: Required when `aiservice_watsonx_action` is `install`. Obtain from IBM Cloud watsonx.ai service.

**Valid values**: Valid WatsonX AI API key string

**Impact**: Enables AI Broker to authenticate with WatsonX AI services. Invalid key will prevent AI model access.

**Related variables**: [`aiservice_watsonx_action`](#aiservice_watsonx_action), [`aiservice_watsonxai_url`](#aiservice_watsonxai_url), [`aiservice_watsonxai_project_id`](#aiservice_watsonxai_project_id)

**Notes**:
- **Security**: Store securely, never commit to version control
- Obtain from IBM Cloud console under watsonx.ai service credentials
- API key is stored as Kubernetes secret

### aiservice_watsonxai_url
WatsonX AI service endpoint URL.

- Optional
- Environment Variable: `AISERVICE_WATSONXAI_URL`
- Default: None (empty string)

**Purpose**: Specifies the WatsonX AI API endpoint for model inference and management.

**When to use**: Required when `aiservice_watsonx_action` is `install`. Obtain from IBM Cloud watsonx.ai service details.

**Valid values**: Valid HTTPS URL to WatsonX AI endpoint (e.g., `https://us-south.ml.cloud.ibm.com`)

**Impact**: Determines which WatsonX AI region/endpoint the AI Broker connects to.

**Related variables**: [`aiservice_watsonx_action`](#aiservice_watsonx_action), [`aiservice_watsonxai_apikey`](#aiservice_watsonxai_apikey), [`aiservice_watsonxai_project_id`](#aiservice_watsonxai_project_id)

**Notes**:
- URL varies by IBM Cloud region
- Common endpoints: `https://us-south.ml.cloud.ibm.com`, `https://eu-de.ml.cloud.ibm.com`
- Verify endpoint in IBM Cloud watsonx.ai service details

### aiservice_watsonxai_project_id
WatsonX AI project identifier.

- Optional
- Environment Variable: `AISERVICE_WATSONXAI_PROJECT_ID`
- Default: None (empty string)

**Purpose**: Identifies the WatsonX AI project containing the AI models and resources to be accessed.

**When to use**: Required when `aiservice_watsonx_action` is `install`. Obtain from IBM Cloud watsonx.ai project settings.

**Valid values**: Valid WatsonX AI project ID (UUID format)

**Impact**: Determines which WatsonX AI project's models and resources are accessible to the AI Broker tenant.

**Related variables**: [`aiservice_watsonx_action`](#aiservice_watsonx_action), [`aiservice_watsonxai_apikey`](#aiservice_watsonxai_apikey), [`aiservice_watsonxai_url`](#aiservice_watsonxai_url)

**Notes**:
- Find project ID in IBM Cloud watsonx.ai project settings
- Format is typically a UUID (e.g., `12345678-1234-1234-1234-123456789012`)
- Project must exist before configuring AI Broker

## Entitlement Configuration
Configure the tenant's entitlement to the AI Service for licensing and access control.

### tenant_entitlement_type
Type of entitlement for the tenant.

- Optional
- Environment Variable: `AISERVICE_TENANT_ENTITLEMENT_TYPE`
- Default: None

**Purpose**: Specifies the entitlement type for the tenant, controlling access levels and features.

**When to use**: Set when configuring tenant entitlements for licensing or feature access control.

**Valid values**: Valid entitlement type string (specific values depend on AI Service configuration)

**Impact**: Determines which AI Service features and capacity the tenant can access.

**Related variables**: [`tenant_entitlement_start_date`](#tenant_entitlement_start_date), [`tenant_entitlement_end_date`](#tenant_entitlement_end_date)

**Notes**: Entitlement types are defined by the AI Service deployment configuration.

### tenant_entitlement_start_date
Start date for tenant entitlement period.

- Optional
- Environment Variable: `AISERVICE_TENANT_ENTITLEMENT_START_DATE`
- Default: None

**Purpose**: Defines when the tenant's entitlement becomes active.

**When to use**: Set when configuring time-bound entitlements for the tenant.

**Valid values**: Date string in format `YYYY-MM-DD` (e.g., `2024-01-01`)

**Impact**: Tenant cannot access AI Service before this date.

**Related variables**: [`tenant_entitlement_type`](#tenant_entitlement_type), [`tenant_entitlement_end_date`](#tenant_entitlement_end_date)

**Notes**: Must be in `YYYY-MM-DD` format. Ensure date is valid and in the past or present for immediate access.

### tenant_entitlement_end_date
End date for tenant entitlement period.

- Optional
- Environment Variable: `AISERVICE_TENANT_ENTITLEMENT_END_DATE`
- Default: None

**Purpose**: Defines when the tenant's entitlement expires.

**When to use**: Set when configuring time-bound entitlements for the tenant.

**Valid values**: Date string in format `YYYY-MM-DD` (e.g., `2024-12-31`)

**Impact**: Tenant cannot access AI Service after this date.

**Related variables**: [`tenant_entitlement_type`](#tenant_entitlement_type), [`tenant_entitlement_start_date`](#tenant_entitlement_start_date)

**Notes**:
- Must be in `YYYY-MM-DD` format
- Should be after `tenant_entitlement_start_date`
- Plan for entitlement renewal before expiration


License
-------

EPL-2.0
