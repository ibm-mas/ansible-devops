# eck

This role provides support to install [Elastic Cloud on Kubernetes](https://www.elastic.co/guide/en/cloud-on-k8s/master/index.html) (ECK).

Elasticsearch is configured with a default user named `elastic`, you can obtain the password for this user by running the following command:

```bash
oc -n eck get secret mas-es-elastic-user -o go-template='{{.data.elastic | base64decode}}'; echo
```


## Role Variables
### eck_action
Action to perform on ECK installation.

- **Optional**
- Environment Variable: `ECK_ACTION`
- Default: `install`

**Purpose**: Specifies the action to perform on the Elastic Cloud on Kubernetes (ECK) deployment.

**When to use**:
- Use `install` (default and only supported value) to deploy ECK
- Future versions may support additional actions

**Valid values**: `install`

**Impact**: Determines the operation performed on ECK. Currently only installation is supported.

**Related variables**:
- `eck_enable_elasticsearch`: Enable Elasticsearch component
- `eck_enable_kibana`: Enable Kibana component
- `eck_enable_logstash`: Enable Logstash component
- `eck_enable_filebeat`: Enable Filebeat component

**Note**: This role installs ECK operator and optionally deploys Elasticsearch, Kibana, Logstash, and Filebeat components based on enable flags.

### eck_enable_elasticsearch
Enable Elasticsearch deployment.

- **Optional**
- Environment Variable: `ECK_ENABLE_ELASTICSEARCH`
- Default: `false`

**Purpose**: Controls whether Elasticsearch is deployed as part of the ECK installation.

**When to use**:
- Set to `true` to deploy Elasticsearch for log storage and search
- Leave as `false` if using external Elasticsearch or not needed
- Required for Kibana and Logstash functionality

**Valid values**: `true`, `false`

**Impact**:
- `true`: Deploys Elasticsearch cluster in ECK namespace
- `false`: Skips Elasticsearch deployment

**Related variables**:
- `eck_enable_kibana`: Kibana requires Elasticsearch
- `eck_enable_logstash`: Logstash can send to local or remote Elasticsearch
- `es_domain`: Custom domain for Elasticsearch access

**Note**: Default user `elastic` is created. Retrieve password with: `oc -n eck get secret mas-es-elastic-user -o go-template='{{.data.elastic | base64decode}}'`

### eck_enable_kibana
Enable Kibana deployment.

- **Optional**
- Environment Variable: `ECK_ENABLE_KIBANA`
- Default: `false`

**Purpose**: Controls whether Kibana is deployed as part of the ECK installation for log visualization and analysis.

**When to use**:
- Set to `true` to deploy Kibana for log visualization
- Leave as `false` if not using Kibana UI
- Requires Elasticsearch to be enabled

**Valid values**: `true`, `false`

**Impact**:
- `true`: Deploys Kibana instance connected to Elasticsearch
- `false`: Skips Kibana deployment

**Related variables**:
- `eck_enable_elasticsearch`: Must be `true` for Kibana to function
- `kibana_domain`: Custom domain for Kibana access
- `letsencrypt_email`: For LetsEncrypt certificate

**Note**: Kibana requires Elasticsearch. Ensure `eck_enable_elasticsearch=true` when enabling Kibana.

### eck_enable_logstash
Enable Logstash deployment.

- **Optional**
- Environment Variable: `ECK_ENABLE_LOGSTASH`
- Default: `false`

**Purpose**: Controls whether Logstash is deployed as part of the ECK installation for log processing and forwarding.

**When to use**:
- Set to `true` to deploy Logstash for log processing
- Leave as `false` if not using Logstash pipeline
- Can send logs to local or remote Elasticsearch

**Valid values**: `true`, `false`

**Impact**:
- `true`: Deploys Logstash instance for log processing
- `false`: Skips Logstash deployment

**Related variables**:
- `eck_remote_es_hosts`: Remote Elasticsearch hosts for log forwarding
- `eck_remote_es_username`: Username for remote Elasticsearch
- `eck_remote_es_password`: Password for remote Elasticsearch

**Note**: When remote Elasticsearch variables are set, Logstash forwards logs to the remote instance. Otherwise, logs are sent to local Elasticsearch (if enabled).

### eck_enable_filebeat
Enable Filebeat deployment.

- **Optional**
- Environment Variable: `ECK_ENABLE_FILEBEAT`
- Default: `false`

**Purpose**: Controls whether Filebeat is deployed as part of the ECK installation for log collection from cluster nodes.

**When to use**:
- Set to `true` to deploy Filebeat for log collection
- Leave as `false` if not collecting node logs
- Filebeat collects logs from Kubernetes nodes

**Valid values**: `true`, `false`

**Impact**:
- `true`: Deploys Filebeat DaemonSet for log collection
- `false`: Skips Filebeat deployment

**Related variables**:
- `eck_enable_elasticsearch`: Filebeat sends logs to Elasticsearch
- `eck_enable_logstash`: Alternative log processing pipeline

**Note**: Filebeat runs as a DaemonSet on cluster nodes to collect logs and forward them to Elasticsearch or Logstash.


## Role Variables - Remote Elasticsearch
When `eck_remote_es_hosts`, `eck_remote_es_username`, and `eck_remote_es_password` are all set, and `eck_enable_logstash` is `true`, the Logstash server will be configured to send log messages to the remote Elasticsearch instance defined.

### eck_remote_es_hosts
Remote Elasticsearch host list.

- **Optional** (required for remote Elasticsearch)
- Environment Variable: `ECK_REMOTE_ES_HOSTS`
- Default: None

**Purpose**: Specifies one or more remote Elasticsearch hosts for Logstash to forward logs to instead of local Elasticsearch.

**When to use**:
- Set when forwarding logs to external Elasticsearch cluster
- Required along with `eck_remote_es_username` and `eck_remote_es_password`
- Only applies when `eck_enable_logstash=true`

**Valid values**: Comma-separated list of Elasticsearch hosts (e.g., `https://es1.example.com:9200,https://es2.example.com:9200`)

**Impact**: When set with credentials, Logstash forwards logs to remote Elasticsearch instead of local instance.

**Related variables**:
- `eck_remote_es_username`: Username for remote Elasticsearch
- `eck_remote_es_password`: Password for remote Elasticsearch
- `eck_enable_logstash`: Must be `true` for remote forwarding

**Note**: All three remote Elasticsearch variables must be set together for remote forwarding to work.

### eck_remote_es_username
Remote Elasticsearch username.

- **Optional** (required for remote Elasticsearch)
- Environment Variable: `ECK_REMOTE_ES_USERNAME`
- Default: None

**Purpose**: Specifies the username for authenticating with remote Elasticsearch when forwarding logs via Logstash.

**When to use**:
- Set when forwarding logs to external Elasticsearch cluster
- Required along with `eck_remote_es_hosts` and `eck_remote_es_password`
- Only applies when `eck_enable_logstash=true`

**Valid values**: Valid Elasticsearch username string

**Impact**: Used by Logstash to authenticate with remote Elasticsearch. Without valid credentials, log forwarding will fail.

**Related variables**:
- `eck_remote_es_hosts`: Remote Elasticsearch hosts
- `eck_remote_es_password`: Password for authentication
- `eck_enable_logstash`: Must be `true` for remote forwarding

**Note**: **SECURITY** - All three remote Elasticsearch variables must be set together. Credentials are stored securely in Kubernetes secrets.

### eck_remote_es_password
Remote Elasticsearch password.

- **Optional** (required for remote Elasticsearch)
- Environment Variable: `ECK_REMOTE_ES_PASSWORD`
- Default: None

**Purpose**: Specifies the password for authenticating with remote Elasticsearch when forwarding logs via Logstash.

**When to use**:
- Set when forwarding logs to external Elasticsearch cluster
- Required along with `eck_remote_es_hosts` and `eck_remote_es_username`
- Only applies when `eck_enable_logstash=true`

**Valid values**: Valid Elasticsearch password string

**Impact**: Used by Logstash to authenticate with remote Elasticsearch. Without valid credentials, log forwarding will fail.

**Related variables**:
- `eck_remote_es_hosts`: Remote Elasticsearch hosts
- `eck_remote_es_username`: Username for authentication
- `eck_enable_logstash`: Must be `true` for remote forwarding

**Note**: **SECURITY** - Store password securely. All three remote Elasticsearch variables must be set together. Credentials are stored in Kubernetes secrets.


## Role Variables - Domains and Certificates
Elasticsearch and Kibana can be configured with a custom domain and a certificate signed by [LetsEncrypt](https://letsencrypt.org/).

### es_domain
Custom domain for Elasticsearch access.

- **Optional**
- Environment Variable: `ECK_ELASTICSEARCH_DOMAIN`
- Default: None

**Purpose**: Specifies a custom domain for accessing Elasticsearch, enabling external access with proper DNS routing.

**When to use**:
- Set when external access to Elasticsearch is required
- Must be routable to the target OCP cluster
- Used with LetsEncrypt for automatic certificate generation

**Valid values**: Valid domain name routable to the cluster (e.g., `es.example.com`)

**Impact**: When set, creates a route with custom domain for Elasticsearch access. Without it, uses default cluster route.

**Related variables**:
- `letsencrypt_email`: Required for automatic certificate generation
- `eck_enable_elasticsearch`: Must be `true`

**Note**: Domain must be routable to the cluster. When combined with `letsencrypt_email`, automatically provisions LetsEncrypt certificate using HTTP solver.

### kibana_domain
Custom domain for Kibana access.

- **Optional**
- Environment Variable: `ECK_KIBANA_DOMAIN`
- Default: None

**Purpose**: Specifies a custom domain for accessing Kibana UI, enabling external access with proper DNS routing.

**When to use**:
- Set when external access to Kibana is required
- Must be routable to the target OCP cluster
- Used with LetsEncrypt for automatic certificate generation

**Valid values**: Valid domain name routable to the cluster (e.g., `kibana.example.com`)

**Impact**: When set, creates a route with custom domain for Kibana access. Without it, uses default cluster route.

**Related variables**:
- `letsencrypt_email`: Required for automatic certificate generation
- `eck_enable_kibana`: Must be `true`

**Note**: Domain must be routable to the cluster. When combined with `letsencrypt_email`, automatically provisions LetsEncrypt certificate using HTTP solver.

### letsencrypt_email
Email for LetsEncrypt certificate registration.

- **Optional**
- Environment Variable: `LETSENCRYPT_EMAIL`
- Default: None

**Purpose**: Specifies the email address for registering LetsEncrypt certificates when using custom domains for Elasticsearch or Kibana.

**When to use**:
- Set when using custom domains (`es_domain` or `kibana_domain`)
- Required for automatic LetsEncrypt certificate provisioning
- Email receives certificate expiration notifications

**Valid values**: Valid email address

**Impact**: When set with custom domains, automatically configures LetsEncrypt Issuer and provisions certificates using HTTP solver via Cert-Manager.

**Related variables**:
- `es_domain`: Elasticsearch custom domain
- `kibana_domain`: Kibana custom domain

**Note**: Requires Cert-Manager to be installed in the cluster. The Issuer uses LetsEncrypt production environment with HTTP-01 challenge solver. Email receives important certificate notifications.


## Example Playbook

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    eck_action: install
    eck_enable_elasticsearch: true
    eck_enable_kibana: true
    eck_enable_logstash: true
  roles:
    - ibm.mas_devops.eck
```

## License

EPL-2.0
