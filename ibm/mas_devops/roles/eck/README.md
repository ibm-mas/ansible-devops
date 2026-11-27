# eck

This role provides support to install [Elastic Cloud on Kubernetes](https://www.elastic.co/guide/en/cloud-on-k8s/master/index.html) (ECK).

Elasticsearch is configured with a default user named `elastic`, you can obtain the password for this user by running the following command:

```bash
oc -n eck get secret mas-es-elastic-user -o go-template='{{.data.elastic | base64decode}}'; echo
```

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`eck_action`](#eck_action) | No | `install` |
| [`eck_enable_elasticsearch`](#eck_enable_elasticsearch) | No | `false` |
| [`eck_enable_kibana`](#eck_enable_kibana) | No | `false` |
| [`eck_enable_logstash`](#eck_enable_logstash) | No | `false` |
| [`eck_enable_filebeat`](#eck_enable_filebeat) | No | `false` |
| [`eck_remote_es_hosts`](#eck_remote_es_hosts) | Conditional | None |
| [`eck_remote_es_username`](#eck_remote_es_username) | Conditional | None |
| [`eck_remote_es_password`](#eck_remote_es_password) | Conditional | None |
| [`es_domain`](#es_domain) | No | None |
| [`kibana_domain`](#kibana_domain) | No | None |
| [`letsencrypt_email`](#letsencrypt_email) | No | None |

The three remote Elasticsearch variables are only required when forwarding logs to a remote Elasticsearch instance, and must all be set together.

### ECK Components

#### eck_action

Action to perform on the ECK deployment — `install` (the default and currently only supported value).

- **Optional**
- Environment Variable: `ECK_ACTION`
- Default: `install`

Installs the ECK operator and, based on the enable flags below, optionally deploys Elasticsearch, Kibana, Logstash, and Filebeat components.

#### eck_enable_elasticsearch

Deploy Elasticsearch for log storage and search — `true` or `false`.

- **Optional**
- Environment Variable: `ECK_ENABLE_ELASTICSEARCH`
- Default: `false`

Leave as `false` when using an external Elasticsearch instance. Elasticsearch is required for Kibana, and for local log forwarding from Logstash and Filebeat. The default `elastic` user is created — retrieve its password with the command shown above.

#### eck_enable_kibana

Deploy Kibana for log visualization and analysis — `true` or `false`.

- **Optional**
- Environment Variable: `ECK_ENABLE_KIBANA`
- Default: `false`

Kibana requires Elasticsearch — ensure `eck_enable_elasticsearch` is `true` when enabling Kibana. A custom domain can be set with `kibana_domain`.

#### eck_enable_logstash

Deploy Logstash for log processing and forwarding — `true` or `false`.

- **Optional**
- Environment Variable: `ECK_ENABLE_LOGSTASH`
- Default: `false`

When the remote Elasticsearch variables are set, Logstash forwards logs to that remote instance; otherwise logs are sent to the local Elasticsearch (if enabled).

#### eck_enable_filebeat

Deploy Filebeat as a DaemonSet on the Kubernetes cluster nodes for log collection — `true` or `false`.

- **Optional**
- Environment Variable: `ECK_ENABLE_FILEBEAT`
- Default: `false`

Filebeat collects logs from the cluster nodes and forwards them to Elasticsearch or Logstash.

### Remote Elasticsearch

When `eck_remote_es_hosts`, `eck_remote_es_username`, and `eck_remote_es_password` are all set, and `eck_enable_logstash` is `true`, the Logstash server will be configured to send log messages to the remote Elasticsearch instance defined.

#### eck_remote_es_hosts

Remote Elasticsearch hosts for Logstash to forward logs to — a comma-separated list of hosts (e.g. `https://es1.example.com:9200,https://es2.example.com:9200`).

- **Required** for remote Elasticsearch forwarding, together with the username and password
- Environment Variable: `ECK_REMOTE_ES_HOSTS`
- Default: None

Only applies when `eck_enable_logstash` is `true`.

#### eck_remote_es_username

Username for authenticating with the remote Elasticsearch instance — a valid Elasticsearch username string.

- **Required** for remote Elasticsearch forwarding, together with the hosts and password
- Environment Variable: `ECK_REMOTE_ES_USERNAME`
- Default: None

Only applies when `eck_enable_logstash` is `true`. Without valid credentials, log forwarding will fail.

#### eck_remote_es_password

Password for authenticating with the remote Elasticsearch instance — a valid Elasticsearch password string.

- **Required** for remote Elasticsearch forwarding, together with the hosts and username
- Environment Variable: `ECK_REMOTE_ES_PASSWORD`
- Default: None

Store the password securely — it is stored in Kubernetes secrets along with the username. Without valid credentials, log forwarding will fail.

### Domains and Certificates

Elasticsearch and Kibana can be configured with a custom domain and a certificate signed by [LetsEncrypt](https://letsencrypt.org/).

#### es_domain

Custom domain for external access to Elasticsearch — a valid domain name routable to the target OCP cluster (e.g. `es.example.com`).

- **Optional**
- Environment Variable: `ECK_ELASTICSEARCH_DOMAIN`
- Default: None

When set, a route with the custom domain is created for Elasticsearch access instead of the default cluster route; combined with `letsencrypt_email`, a LetsEncrypt certificate is provisioned automatically. Requires `eck_enable_elasticsearch` to be `true`.

#### kibana_domain

Custom domain for external access to the Kibana UI — a valid domain name routable to the target OCP cluster (e.g. `kibana.example.com`).

- **Optional**
- Environment Variable: `ECK_KIBANA_DOMAIN`
- Default: None

When set, a route with the custom domain is created for Kibana access instead of the default cluster route; combined with `letsencrypt_email`, a LetsEncrypt certificate is provisioned automatically. Requires `eck_enable_kibana` to be `true`.

#### letsencrypt_email

Email address for LetsEncrypt certificate registration — a valid email address that receives certificate expiration notifications.

- **Optional**
- Environment Variable: `LETSENCRYPT_EMAIL`
- Default: None

Used together with `es_domain` and/or `kibana_domain`: configures a LetsEncrypt Issuer via Cert-Manager and provisions certificates using the HTTP-01 challenge solver. Cert-Manager must be installed in the cluster, and the Issuer uses the LetsEncrypt production environment.

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
