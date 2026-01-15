# aiservice
This role provides support to install and configure AI Service for IBM Maximo Application Suite. AI Service enables AI-powered capabilities within MAS applications, particularly for Maximo Manage.

The role supports the following operations:
- Install AI Service API application
- Create and delete AI Service tenants
- Manage AI Service API keys
- Configure AWS S3 storage integration
- Configure WatsonX AI integration

## Role Variables

### General Variables

#### tenant_action
Action to perform on AI Service tenant.

- **Optional**
- Environment Variable: `TENANT_ACTION`
- Default: `install`

**Purpose**: Specifies whether to install or remove an AI Service tenant. Controls tenant lifecycle management.

**When to use**:
- Use `install` (default) to create a new AI Service tenant
- Use `remove` to delete an existing AI Service tenant
- Required for tenant management operations

**Valid values**: `install`, `remove`

**Impact**: 
- `install`: Creates tenant with specified configuration
- `remove`: Deletes tenant and associated resources

**Related variables**:
- `tenantName`: Name of tenant to install/remove
- All other variables apply only when action is `install`

**Note**: **WARNING** - `remove` action permanently deletes the tenant and all associated data. Ensure you have backups before removing a tenant.

#### tenantName
AI Service tenant identifier.

- **Optional**
- Environment Variable: `AISERVICE_TENANT_NAME`
- Default: `user`

**Purpose**: Specifies the name/identifier for the AI Service tenant. Tenants provide isolation between different users or environments.

**When to use**:
- Use default (`user`) for single-tenant deployments
- Set custom name for multi-tenant environments
- Use descriptive names (e.g., `production`, `development`, `team-a`)

**Valid values**: Valid tenant name string (alphanumeric, lowercase recommended)

**Impact**: Tenant name is used in resource names, API keys, and configuration. Must be unique within the AI Service instance.

**Related variables**:
- `tenant_action`: Whether to install or remove this tenant
- Tenant name is used in generated API key secrets

**Note**: Choose meaningful tenant names for multi-tenant scenarios. The default `user` is suitable for single-tenant deployments.

#### app_domain
Application domain for AI Service routes.

- **Optional**
- Environment Variable: `APP_DOMAIN`
- Default: Auto-detected from cluster

**Purpose**: Specifies the application domain for AI Service routes and endpoints. Used to construct the full URL for AI Service API access.

**When to use**:
- Leave unset for automatic detection from cluster configuration
- Set explicitly when cluster domain cannot be auto-detected
- Required for custom domain configurations

**Valid values**: Domain string in format `apps.domain` (e.g., `apps.mycluster.example.com`)

**Impact**: Determines the URL where AI Service API is accessible. Incorrect domain will prevent API access.

**Related variables**:
- `aiservice_domain`: Custom domain override (takes precedence if set)

**Note**: The role automatically detects the cluster's application domain. Only set this if auto-detection fails or you need a custom domain. Format must be `apps.<domain>`.

#### aiservice_domain
Custom domain override for AI Service.

- **Optional**
- Environment Variable: `AISERVICE_DOMAIN`
- Default: None (uses `app_domain` or cluster default)

**Purpose**: Provides a custom domain specifically for AI Service, overriding the general application domain. Useful for custom DNS configurations.

**When to use**:
- Leave unset to use `app_domain` or cluster default
- Set when AI Service needs a different domain than other applications
- Required for custom DNS or external domain configurations

**Valid values**: Valid domain string (e.g., `aiservice.example.com`)

**Impact**: When set, this domain is used instead of `app_domain` for AI Service routes. Takes precedence over `app_domain`.

**Related variables**:
- `app_domain`: General application domain (used if this is not set)

**Note**: This is an advanced configuration option. Most deployments should use `app_domain` or cluster auto-detection. Only set this if AI Service requires a separate domain.

### S3 Storage Configuration Variables

#### aiservice_s3_host
S3-compatible storage host endpoint.

- **Optional**
- Environment Variable: `AISERVICE_S3_HOST`
- Default: None

**Purpose**: Specifies the endpoint URL for S3-compatible object storage used by AI Service for storing models, data, and artifacts.

**When to use**:
- Required when configuring S3 storage integration
- Set to AWS S3 endpoint (e.g., `s3.amazonaws.com`) or compatible service
- Must be accessible from the cluster

**Valid values**: Valid S3 endpoint URL (e.g., `s3.amazonaws.com`, `s3.us-east-1.amazonaws.com`, MinIO endpoint)

**Impact**: AI Service uses this storage for persistent data. Without proper S3 configuration, AI Service functionality will be limited.

**Related variables**:
- `aiservice_s3_accesskey`: Access credentials for this host
- `aiservice_s3_secretkey`: Secret credentials for this host
- `aiservice_s3_region`: Region for this host

**Note**: All S3 variables (`aiservice_s3_*`) must be configured together for S3 integration. Supports AWS S3 and S3-compatible services like MinIO, IBM Cloud Object Storage.

#### aiservice_s3_accesskey
S3 storage access key ID.

- **Optional**
- Environment Variable: `AISERVICE_S3_ACCESSKEY`
- Default: None

**Purpose**: Provides the access key ID for authenticating to S3-compatible object storage. Part of the credential pair for S3 access.

**When to use**:
- Required when configuring S3 storage integration
- Obtain from your S3 provider (AWS IAM, MinIO, etc.)
- Must have permissions to create/read/write buckets and objects

**Valid values**: Valid S3 access key ID string

**Impact**: Without valid credentials, AI Service cannot access S3 storage, limiting functionality.

**Related variables**:
- `aiservice_s3_secretkey`: Secret key paired with this access key
- `aiservice_s3_host`: S3 endpoint to authenticate against
- `aiservice_s3_region`: Region for the S3 service

**Note**: **SECURITY** - Keep access keys secure. Do not commit to source control. Use environment variables or secure secret management. Ensure the access key has appropriate S3 permissions for AI Service operations.

#### aiservice_s3_secretkey
S3 storage secret access key.

- **Optional**
- Environment Variable: `AISERVICE_S3_SECRETKEY`
- Default: None

**Purpose**: Provides the secret access key for authenticating to S3-compatible object storage. Part of the credential pair for S3 access.

**When to use**:
- Required when configuring S3 storage integration
- Obtain from your S3 provider (AWS IAM, MinIO, etc.)
- Must be paired with corresponding `aiservice_s3_accesskey`

**Valid values**: Valid S3 secret access key string

**Impact**: Without valid credentials, AI Service cannot access S3 storage, limiting functionality.

**Related variables**:
- `aiservice_s3_accesskey`: Access key ID paired with this secret key
- `aiservice_s3_host`: S3 endpoint to authenticate against
- `aiservice_s3_region`: Region for the S3 service

**Note**: **SECURITY** - Keep secret keys secure. Never commit to source control or expose in logs. Use environment variables or secure secret management. The secret key must match the access key ID.

#### aiservice_s3_region
S3 storage region.

- **Optional**
- Environment Variable: `AISERVICE_S3_REGION`
- Default: None

**Purpose**: Specifies the AWS region or region identifier for S3-compatible object storage. Required for proper S3 API operations.

**When to use**:
- Required when configuring S3 storage integration
- Set to AWS region (e.g., `us-east-1`, `eu-west-1`) or compatible service region
- Must match the region where your S3 buckets are located

**Valid values**: Valid AWS region code or S3-compatible service region identifier

**Impact**: Incorrect region will cause S3 API calls to fail. Must match the actual bucket location.

**Related variables**:
- `aiservice_s3_host`: S3 endpoint (may include region in URL)
- `aiservice_s3_accesskey`: Access credentials for this region
- `aiservice_s3_secretkey`: Secret credentials for this region

**Note**: For AWS S3, use standard region codes (e.g., `us-east-1`). For S3-compatible services, use the region identifier provided by your service. Some services may not require a region.

### WatsonX AI Configuration Variables

#### aiservice_watsonx_action
Action to perform on WatsonX AI integration.

- **Optional**
- Environment Variable: `AISERVICE_WATSONX_ACTION`
- Default: `install`

**Purpose**: Specifies whether to install or remove WatsonX AI integration with AI Service. Controls WatsonX integration lifecycle.

**When to use**:
- Use `install` (default) to configure WatsonX AI integration
- Use `remove` to delete WatsonX AI integration
- Required for WatsonX integration management

**Valid values**: `install`, `remove`

**Impact**: 
- `install`: Configures AI Service to use WatsonX AI for AI/ML capabilities
- `remove`: Removes WatsonX AI integration configuration

**Related variables**:
- `aiservice_watsonxai_apikey`: API key for WatsonX (required for install)
- `aiservice_watsonxai_url`: WatsonX endpoint (required for install)
- `aiservice_watsonxai_project_id`: WatsonX project (required for install)

**Note**: WatsonX AI integration enables advanced AI capabilities in AI Service. All WatsonX variables must be configured together for successful integration.

#### aiservice_watsonxai_apikey
WatsonX AI API key for authentication.

- **Optional**
- Environment Variable: `AISERVICE_WATSONXAI_APIKEY`
- Default: None

**Purpose**: Provides the API key for authenticating AI Service with IBM WatsonX AI platform. Required for WatsonX AI integration.

**When to use**:
- Required when `aiservice_watsonx_action` is `install`
- Obtain from IBM Cloud WatsonX AI service
- Must have appropriate WatsonX AI permissions

**Valid values**: Valid IBM WatsonX AI API key string

**Impact**: Without valid API key, AI Service cannot access WatsonX AI capabilities. Integration will fail.

**Related variables**:
- `aiservice_watsonxai_url`: WatsonX AI endpoint to authenticate against
- `aiservice_watsonxai_project_id`: WatsonX project to access
- `aiservice_watsonx_action`: Whether to install or remove integration

**Note**: **SECURITY** - Keep API keys secure. Do not commit to source control. Use environment variables or secure secret management. Obtain from IBM Cloud IAM or WatsonX AI service credentials.

#### aiservice_watsonxai_url
WatsonX AI service endpoint URL.

- **Optional**
- Environment Variable: `AISERVICE_WATSONXAI_URL`
- Default: None

**Purpose**: Specifies the endpoint URL for IBM WatsonX AI service. Required for AI Service to connect to WatsonX AI platform.

**When to use**:
- Required when `aiservice_watsonx_action` is `install`
- Set to your WatsonX AI region endpoint
- Must be accessible from the cluster

**Valid values**: Valid WatsonX AI endpoint URL (e.g., `https://us-south.ml.cloud.ibm.com`, `https://eu-de.ml.cloud.ibm.com`)

**Impact**: AI Service uses this URL to access WatsonX AI APIs. Incorrect URL will prevent WatsonX integration.

**Related variables**:
- `aiservice_watsonxai_apikey`: API key for authenticating to this endpoint
- `aiservice_watsonxai_project_id`: Project to access at this endpoint
- `aiservice_watsonx_action`: Whether to install or remove integration

**Note**: Use the WatsonX AI endpoint for your IBM Cloud region. Common endpoints: `https://us-south.ml.cloud.ibm.com` (Dallas), `https://eu-de.ml.cloud.ibm.com` (Frankfurt), `https://jp-tok.ml.cloud.ibm.com` (Tokyo).

#### aiservice_watsonxai_project_id
WatsonX AI project identifier.

- **Optional**
- Environment Variable: `AISERVICE_WATSONXAI_PROJECT_ID`
- Default: None

**Purpose**: Specifies the WatsonX AI project ID that AI Service will use for AI/ML operations. Projects organize resources and control access in WatsonX AI.

**When to use**:
- Required when `aiservice_watsonx_action` is `install`
- Obtain from your WatsonX AI project in IBM Cloud
- Project must have appropriate models and resources configured

**Valid values**: Valid WatsonX AI project ID (UUID format)

**Impact**: AI Service uses this project for accessing WatsonX AI models and resources. Incorrect project ID will prevent access to AI capabilities.

**Related variables**:
- `aiservice_watsonxai_apikey`: API key must have access to this project
- `aiservice_watsonxai_url`: WatsonX endpoint where this project exists
- `aiservice_watsonx_action`: Whether to install or remove integration

**Note**: The project ID is found in your WatsonX AI project settings in IBM Cloud. Ensure the API key has appropriate permissions for the project. The project should have the required AI models and resources configured.

## Example Playbook
After installing the Ansible Collection you can include this role in your own custom playbooks.

```yaml
- hosts: localhost
  vars:
    tenant_action: install
    tenantName: production
    app_domain: apps.mycluster.example.com
    aiservice_s3_host: s3.amazonaws.com
    aiservice_s3_accesskey: "{{ lookup('env', 'AWS_ACCESS_KEY') }}"
    aiservice_s3_secretkey: "{{ lookup('env', 'AWS_SECRET_KEY') }}"
    aiservice_s3_region: us-east-1
    aiservice_watsonxai_apikey: "{{ lookup('env', 'WATSONX_API_KEY') }}"
    aiservice_watsonxai_url: https://us-south.ml.cloud.ibm.com
    aiservice_watsonxai_project_id: my-project-id
  roles:
    - ibm.mas_devops.aiservice
```

## Run Role Playbook
After installing the Ansible Collection you can easily run the role standalone using the `run_role` playbook provided.

```bash
export TENANT_ACTION=install
export AISERVICE_TENANT_NAME=production
export APP_DOMAIN=apps.mycluster.example.com
export AISERVICE_S3_HOST=s3.amazonaws.com
export AISERVICE_S3_ACCESSKEY=your_access_key
export AISERVICE_S3_SECRETKEY=your_secret_key
export AISERVICE_S3_REGION=us-east-1
export AISERVICE_WATSONXAI_APIKEY=your_watsonx_api_key
export AISERVICE_WATSONXAI_URL=https://us-south.ml.cloud.ibm.com
export AISERVICE_WATSONXAI_PROJECT_ID=my-project-id
ROLE_NAME=aiservice ansible-playbook ibm.mas_devops.run_role
```

## License
EPL-2.0
