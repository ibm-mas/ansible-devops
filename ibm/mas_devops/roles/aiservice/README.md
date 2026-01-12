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
Action to be performed by the AI Service role. Valid values are `install` or `remove`.

- **Optional**
- Environment Variable: `TENANT_ACTION`
- Default Value: `install`

#### tenantName
The tenant name for the AI Service role.

- **Optional**
- Environment Variable: `AISERVICE_TENANT_NAME`
- Default Value: `user`

#### app_domain
The application domain for AI Service role. Specify the domain string in the format `apps.domain`.

- **Optional**
- Environment Variable: `APP_DOMAIN`
- Default Value: None

#### aiservice_domain
Provide a custom domain for AI Service. If not specified, the default cluster domain will be used.

- **Optional**
- Environment Variable: `AISERVICE_DOMAIN`
- Default Value: None

### S3 Storage Configuration Variables

#### aiservice_s3_host
The storage host for AI Service S3-compatible object storage.

- **Optional**
- Environment Variable: `AISERVICE_S3_HOST`
- Default Value: None

#### aiservice_s3_accesskey
The storage access key for AI Service S3-compatible object storage.

- **Optional**
- Environment Variable: `AISERVICE_S3_ACCESSKEY`
- Default Value: None

#### aiservice_s3_secretkey
The storage secret key for AI Service S3-compatible object storage.

- **Optional**
- Environment Variable: `AISERVICE_S3_SECRETKEY`
- Default Value: None

#### aiservice_s3_region
The storage region for AI Service S3-compatible object storage.

- **Optional**
- Environment Variable: `AISERVICE_S3_REGION`
- Default Value: None

### WatsonX AI Configuration Variables

#### aiservice_watsonx_action
Action to be performed for WatsonX AI integration. Valid values are `install` or `remove`.

- **Optional**
- Environment Variable: `AISERVICE_WATSONX_ACTION`
- Default Value: `install`

#### aiservice_watsonxai_apikey
The WatsonX AI API key for AI Service integration.

- **Optional**
- Environment Variable: `AISERVICE_WATSONXAI_APIKEY`
- Default Value: None

#### aiservice_watsonxai_url
The WatsonX AI URL for AI Service integration.

- **Optional**
- Environment Variable: `AISERVICE_WATSONXAI_URL`
- Default Value: None

#### aiservice_watsonxai_project_id
The WatsonX AI project ID for AI Service integration.

- **Optional**
- Environment Variable: `AISERVICE_WATSONXAI_PROJECT_ID`
- Default Value: None

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
