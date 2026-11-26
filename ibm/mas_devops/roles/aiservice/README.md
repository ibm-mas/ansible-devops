# aiservice

This role provides support to install and configure AI Service for IBM Maximo Application Suite. AI Service enables AI-powered capabilities within MAS applications, particularly for Maximo Manage.

The role supports the following operations:

- Install AI Service API application
- Create and delete AI Service tenants
- Manage AI Service API keys
- Configure AWS S3 storage integration
- Configure WatsonX AI integration
- Update an existing instance in place (`aiservice_action=update`)

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`tenant_action`](#tenant_action) | No | `install` |
| [`tenantName`](#tenantname) | No | `user` |
| [`app_domain`](#app_domain) | No | Auto-detected from cluster |
| [`aiservice_domain`](#aiservice_domain) | No | None |
| [`ocp_enable_ipv6`](#ocp_enable_ipv6) | No | `false` |
| [`aiservice_s3_host`](#aiservice_s3_host) | Conditional | None |
| [`aiservice_s3_accesskey`](#aiservice_s3_accesskey) | Conditional | None |
| [`aiservice_s3_secretkey`](#aiservice_s3_secretkey) | Conditional | None |
| [`aiservice_s3_region`](#aiservice_s3_region) | No | `none` |
| [`aiservice_watsonx_action`](#aiservice_watsonx_action) | No | `install` |
| [`aiservice_watsonxai_apikey`](#aiservice_watsonxai_apikey) | Conditional | None |
| [`aiservice_watsonxai_url`](#aiservice_watsonxai_url) | Conditional | None |
| [`aiservice_watsonxai_project_id`](#aiservice_watsonxai_project_id) | Conditional | None |
| [`install_db2`](#install_db2) | No | `true` |
| [`aiservice_db_jdbc_url`](#aiservice_db_jdbc_url) | Conditional | None |
| [`aiservice_db_username`](#aiservice_db_username) | Conditional | None |
| [`aiservice_db_password`](#aiservice_db_password) | Conditional | None |
| [`aiservice_db_ca_cert`](#aiservice_db_ca_cert) | No | None |
| [`aiservice_certificate_issuer`](#aiservice_certificate_issuer) | No | None |
| [`aiservice_certificate_duration`](#aiservice_certificate_duration) | No | `8760h0m0s` |
| [`aiservice_certificate_renew_before`](#aiservice_certificate_renew_before) | No | `720h0m0s` |

The S3 storage variables are required together when configuring S3 storage integration, the WatsonX AI variables are required when `aiservice_watsonx_action` is `install`, and the external database variables are required when `install_db2` is `false`.

### Tenant and Domain Configuration

#### aiservice_action
Action to perform on the AI Service instance.

- **Optional**
- Environment Variable: `AISERVICE_ACTION`
- Default: `install`

**Valid values**: `install`, `update`

- `install`: Install and configure AI Service (the original behaviour of this role).
- `update`: Change the configuration of an existing instance in place. The AIServiceApp is never re-rendered, every current value is read from the cluster, so no DRO, database or WatsonX inputs are needed and the action can be re-run. Requires `AISERVICE_INSTANCE_ID`.

**What `update` does today**: if `spec.settings.s3.url` of the AIServiceApp points at the in-cluster MinIO (`minio-service.<MINIO_NAMESPACE>.svc`), the instance is switched to ODF (Ceph/NooBaa). Any other instance is left unchanged. The existing `bucketPrefix` and bucket names are kept. The switch:

1. Verifies ODF is Ready, that the ODF buckets (named `bucketPrefix` + bucket) exist, and that `noobaa-admin` and `openshift-service-ca.crt` are present
2. Updates `aiservice-s3cfg` and `km-s3-secret` (including the `ca.crt` key) with the ODF credentials and endpoint
3. Adds the ODF service CA to `spec.trustedCABundle.customCABundle` of the RHOAI `default-dsci` if it is not already there (skipped when the DSCInitialization does not exist)
4. Copies `km-s3-secret` to every `AIServiceTenant` namespace of the instance
5. Patches `spec.settings.s3.url` and `spec.settings.s3.ca` on the AIServiceApp (last, so a failed run can be repeated)
6. Restarts the km deployments and waits for the AIServiceApp to be `Successful`

The data must already be in ODF. Run the `minio` role (`MINIO_ACTION=backup`) and the `cos_bucket` role (`COS_TYPE=odf`, `COS_BUCKET_ACTION=restore`) first. `mas update --migrate-minio-to-ceph` does all three, and so does the sample playbook `playbooks/aiservice_minio_to_ceph.yml`. MinIO is not removed.

**Related variables**: `MINIO_NAMESPACE` (default `minio`), `ODF_BUCKET_NAMESPACE` (default `openshift-storage`), `AISERVICE_UPDATE_S3_SETTLE_SECONDS` (default `60`).

#### tenant_action

Action to perform on the AI Service tenant — `install` or `remove`.

- **Optional**
- Environment Variable: `TENANT_ACTION`
- Default: `install`

`install` creates the tenant with the specified configuration; `remove` deletes the tenant and associated resources. All other variables apply only when the action is `install`.

!!! warning
    The `remove` action permanently deletes the tenant and **all associated data** — ensure you have backups before removing a tenant.

#### tenantName

AI Service tenant identifier — a valid tenant name string (alphanumeric, lowercase recommended), unique within the AI Service instance.

- **Optional**
- Environment Variable: `AISERVICE_TENANT_NAME`
- Default: `user`

Tenants provide isolation between different users or environments. Use the default for single-tenant deployments, and descriptive names (e.g., `production`, `development`, `team-a`) for multi-tenant environments — the tenant name is used in resource names, API keys, generated API key secrets, and configuration.

#### app_domain

Application domain for AI Service routes — a domain string in the format `apps.domain` (e.g., `apps.mycluster.example.com`).

- **Optional**
- Environment Variable: `APP_DOMAIN`
- Default: Auto-detected from cluster

Leave unset for automatic detection from the cluster configuration, and set explicitly when the cluster domain cannot be auto-detected or for custom domain configurations. The domain determines the URL where the AI Service API is accessible — an incorrect domain will prevent API access. `aiservice_domain` takes precedence if set.

#### aiservice_domain

Custom domain override for AI Service — a valid domain string (e.g., `aiservice.example.com`).

- **Optional**
- Environment Variable: `AISERVICE_DOMAIN`
- Default: None (uses `app_domain` or cluster default)

When set, this domain is used instead of `app_domain` for AI Service routes. This is an advanced configuration option for custom DNS or external domain configurations — most deployments should use `app_domain` or cluster auto-detection, and only set this if AI Service requires a separate domain.

#### ocp_enable_ipv6

Enables SingleStack IPv6 service configuration for AI Service — `true` or `false`.

- **Optional**
- Environment Variable: `OCP_ENABLE_IPV6`
- Default: `false`

Provides a way to enable IPv6 networking for all the services that are created by the AI Service operator. Set this when installing AI Service on an IPv6 enabled environment — when set to true, all services are created with a SingleStack IPv6 configuration.

### S3 Storage Configuration

#### aiservice_s3_host

S3-compatible storage host endpoint — a valid S3 endpoint URL (e.g., `s3.amazonaws.com`, `s3.us-east-1.amazonaws.com`, or a MinIO endpoint).

- **Optional** — required when configuring S3 storage integration
- Environment Variable: `AISERVICE_S3_HOST`
- Default: None

The endpoint must be accessible from the cluster. AI Service uses this storage for persistent data (models, data, and artifacts) — without proper S3 configuration, AI Service functionality will be limited. Supports AWS S3 and S3-compatible services like MinIO and IBM Cloud Object Storage. All S3 variables (`aiservice_s3_*`) must be configured together for S3 integration.

#### aiservice_s3_accesskey

S3 storage access key ID — a valid S3 access key string obtained from your S3 provider (AWS IAM, MinIO, etc.).

- **Optional** — required when configuring S3 storage integration
- Environment Variable: `AISERVICE_S3_ACCESSKEY`
- Default: None

The key must have permissions to create/read/write buckets and objects — without valid credentials, AI Service cannot access S3 storage, limiting functionality. Keep access keys secure: do not commit them to source control, and use environment variables or secure secret management.

#### aiservice_s3_secretkey

S3 storage secret access key — a valid S3 secret access key string, paired with the corresponding `aiservice_s3_accesskey`.

- **Optional** — required when configuring S3 storage integration
- Environment Variable: `AISERVICE_S3_SECRETKEY`
- Default: None

Without valid credentials, AI Service cannot access S3 storage, limiting functionality. Keep secret keys secure — never commit them to source control or expose them in logs; use environment variables or secure secret management.

#### aiservice_s3_region

S3 storage region — a valid AWS region code (e.g., `us-east-1`, `eu-west-1`) or S3-compatible service region identifier.

- **Optional**
- Environment Variable: `AISERVICE_S3_REGION`
- Default: `none`

The region must match where your S3 buckets are located — an incorrect region will cause S3 API calls to fail. For S3-compatible services, use the region identifier provided by your service; some services may not require a region.

### WatsonX AI Configuration

#### aiservice_watsonx_action

Action to perform on the WatsonX AI integration — `install` or `remove`.

- **Optional**
- Environment Variable: `AISERVICE_WATSONX_ACTION`
- Default: `install`

`install` configures AI Service to use WatsonX AI for AI/ML capabilities; `remove` removes the WatsonX AI integration configuration. All WatsonX variables must be configured together for successful integration.

#### aiservice_watsonxai_apikey

WatsonX AI API key for authentication — a valid IBM WatsonX AI API key string, obtained from IBM Cloud IAM or WatsonX AI service credentials.

- **Optional** — required when `aiservice_watsonx_action` is `install`
- Environment Variable: `AISERVICE_WATSONXAI_APIKEY`
- Default: None

The key must have appropriate WatsonX AI permissions — without a valid API key, AI Service cannot access WatsonX AI capabilities and the integration will fail. Keep API keys secure: do not commit them to source control, and use environment variables or secure secret management.

#### aiservice_watsonxai_url

WatsonX AI service endpoint URL — a valid WatsonX AI endpoint URL (e.g., `https://us-south.ml.cloud.ibm.com`, `https://eu-de.ml.cloud.ibm.com`).

- **Optional** — required when `aiservice_watsonx_action` is `install`
- Environment Variable: `AISERVICE_WATSONXAI_URL`
- Default: None

Use the WatsonX AI endpoint for your IBM Cloud region — common endpoints are `https://us-south.ml.cloud.ibm.com` (Dallas), `https://eu-de.ml.cloud.ibm.com` (Frankfurt), and `https://jp-tok.ml.cloud.ibm.com` (Tokyo). The endpoint must be accessible from the cluster; an incorrect URL will prevent WatsonX integration.

#### aiservice_watsonxai_project_id

WatsonX AI project identifier — a valid WatsonX AI project ID in UUID format, obtained from your WatsonX AI project settings in IBM Cloud.

- **Optional** — required when `aiservice_watsonx_action` is `install`
- Environment Variable: `AISERVICE_WATSONXAI_PROJECT_ID`
- Default: None

The project organizes resources and controls access in WatsonX AI — it must have the required AI models and resources configured, and the API key must have appropriate permissions for the project. An incorrect project ID will prevent access to AI capabilities.

### Database Configuration

#### install_db2

Controls whether to install an in-cluster DB2 database for AI Service — `true` or `false`.

- **Optional**
- Environment Variable: `INSTALL_DB2`
- Default: `true`

Use `true` (default) for development, testing, or proof-of-concept deployments, and `false` for production deployments with external Oracle or DB2 databases — when `false`, you must provide external database connection details via the `aiservice_db_*` variables. External database support is available in AI Service 9.1.x only; supported external databases are Oracle and DB2.

#### aiservice_db_jdbc_url

JDBC connection URL for the external database — for example `jdbc:oracle:thin:@//hostname:1521/servicename` (Oracle) or `jdbc:db2://hostname:50000/database` (DB2).

- **Optional** — required when `install_db2` is `false`
- Environment Variable: `AISERVICE_DB_JDBC_URL`
- Default: None

AI Service uses this database for persistent storage — an incorrect URL will prevent AI Service from starting. Ensure the database exists, is accessible from the cluster, and is properly configured before installation, and that the database user has appropriate permissions to create tables and manage the schema.

#### aiservice_db_username

Database username for external database authentication — a valid database username string, preferably a dedicated service account for AI Service.

- **Optional** — required when `install_db2` is `false`
- Environment Variable: `AISERVICE_DB_USERNAME`
- Default: None

The user must have permissions to create tables, indexes, and manage schema objects — use a dedicated service account rather than a DBA account. Without valid credentials, AI Service cannot connect to the database and will fail to start.

#### aiservice_db_password

Database password for external database authentication — a valid database password string matching `aiservice_db_username`.

- **Optional** — required when `install_db2` is `false`
- Environment Variable: `AISERVICE_DB_PASSWORD`
- Default: None

Without valid credentials, AI Service cannot connect to the database and will fail to start. Never commit passwords to source control — use environment variables or secure secret management.

#### aiservice_db_ca_cert

CA certificate for external database SSL/TLS connections — the complete CA certificate content in PEM format, including the `-----BEGIN CERTIFICATE-----` and `-----END CERTIFICATE-----` markers.

- **Optional** — required when the external database uses SSL/TLS with self-signed certificates
- Environment Variable: `AISERVICE_DB_CA_CERT`
- Default: None

Provide the entire certificate content, not a file path, including all lines from `-----BEGIN CERTIFICATE-----` to `-----END CERTIFICATE-----`. Not needed for databases with publicly trusted certificates — without the CA certificate, AI Service cannot validate SSL/TLS connections to databases using self-signed certificates.

### Certificate Management

#### aiservice_certificate_issuer

Name of the cert-manager Issuer to use for automatic certificate generation — the name of any valid Issuer resource in the cluster (e.g., `prod-le-issuer`, `{mas_instance_id}-cloudflare-le-prod`).

- **Optional**
- Environment Variable: `AISERVICE_CERTIFICATE_ISSUER`
- Default: None

The Issuer defines the Certificate Authority and authentication method used for certificate issuance. Set it to the Issuer created by the `suite_dns` role for Let's Encrypt integration (e.g., `{aiservice_instance_id}-cloudflare-le-prod`), or a custom Issuer for specific certificate requirements. If the Issuer is not properly configured or lacks necessary credentials, certificate generation will fail and AI Service will not be accessible — ensure the Issuer is created and functional (test with a test Certificate resource) before installing AI Service.

#### aiservice_certificate_duration

Validity period for AI Service certificates — a duration string in the format `{hours}h{minutes}m{seconds}s` (e.g., `8760h0m0s`, `2160h0m0s`, `17520h0m0s`).

- **Optional**
- Environment Variable: `AISERVICE_CERTIFICATE_DURATION`
- Default: `8760h0m0s` (1 year)

Shorter durations increase security but require more frequent renewals; longer durations reduce renewal frequency but increase risk if certificates are compromised — cert-manager automatically renews certificates before expiration. Must be longer than `aiservice_certificate_renew_before`; only applies when using automatic certificate management and affects all AI Service certificates.

#### aiservice_certificate_renew_before

When to renew certificates before they expire — a duration string in the format `{hours}h{minutes}m{seconds}s` (e.g., `720h0m0s`, `1440h0m0s`, `168h0m0s`).

- **Optional**
- Environment Variable: `AISERVICE_CERTIFICATE_RENEW_BEFORE`
- Default: `720h0m0s` (30 days)

Longer renewal windows provide more time to resolve renewal issues but result in more frequent certificate changes; shorter windows reduce certificate churn but increase risk of expiration if renewal fails. Must be shorter than `aiservice_certificate_duration` — ensure this value provides adequate time to detect and resolve certificate renewal issues before expiration. Only applies when using automatic certificate management and affects all AI Service certificates.

## Example Playbook

After installing the Ansible Collection you can include this role in your own custom playbooks.

### Example 1: Basic Installation with In-Cluster DB2

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

### Example 2: Installation with External Oracle Database

```yaml
- hosts: localhost
  vars:
    tenant_action: install
    tenantName: production
    app_domain: apps.mycluster.example.com
    # External Database Configuration
    install_db2: false
    aiservice_db_jdbc_url: "{{ lookup('env', 'AISERVICE_DB_JDBC_URL') }}"
    aiservice_db_username: "{{ lookup('env', 'AISERVICE_DB_USERNAME') }}"
    aiservice_db_password: "{{ lookup('env', 'AISERVICE_DB_PASSWORD') }}"
    aiservice_db_ca_cert: "{{ lookup('env', 'AISERVICE_DB_CA_CERT') }}"
    # S3 and WatsonX Configuration
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
# Database Configuration (INSTALL_DB2 defaults to true for in-cluster DB2)
# For external database, set:
# export INSTALL_DB2=false
# export AISERVICE_DB_JDBC_URL=jdbc:oracle:thin:@//oracle.example.com:1521/ORCL
# export AISERVICE_DB_USERNAME=aiservice_user
# export AISERVICE_DB_PASSWORD=your_db_password
# export AISERVICE_DB_CA_CERT="-----BEGIN CERTIFICATE-----
# MIIDXTCCAkWgAwIBAgIJAKJ...
# ...certificate content...
# -----END CERTIFICATE-----"
ROLE_NAME=aiservice ansible-playbook ibm.mas_devops.run_role
```

## License

EPL-2.0
