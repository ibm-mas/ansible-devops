eck
===============================================================================

This role provides support to install [Elastic Cloud on Kubernetes](https://www.elastic.co/guide/en/cloud-on-k8s/master/index.html) (ECK).

Elasticsearch is configured with a default user named `elastic`, you can obtain the password for this user by running the following command:

```
oc -n eck get secret mas-es-elastic-user -o go-template='{{.data.elastic | base64decode}}'; echo
```


Role Variables
-------------------------------------------------------------------------------
### eck_action
Action to be performed by the role. The only valid value currently is `install`.

- Environment Variable: `ECK_ACTION`
- Default Value: `install`

### eck_enable_elasticsearch
Whether to include Elasticsearch when performing the desired action.

- Environment Variable: `ECK_ENABLE_ELASTICSEARCH`
- Default Value: `false`

### eck_enable_kibana
Whether to include Kibana when performing the desired action.

- Environment Variable: `ECK_ENABLE_KIBANA`
- Default Value: `false`

### eck_enable_logstash
Whether to include Logstash when performing the desired action.

- Environment Variable: `ECK_ENABLE_LOGSTASH`
- Default Value: `false`

### eck_enable_filebeat
Whether to include Filebeat when performing the desired action.

- Environment Variable: `ECK_ENABLE_FILEBEAT`
- Default Value: `false`


Role Variables - Remote Elasticsearch
-------------------------------------------------------------------------------
When `eck_remote_es_hosts`, `eck_remote_es_username`, and `eck_remote_es_password` are all set, and `eck_enable_logstash` is `true`, the Logstash server will be configured to send log messages to the remote Elasticsearch instance defined.

### eck_remote_es_hosts
A list of one or more hosts for the remote Elasticsearch instance.  When using an environment varible, the value should be in the format of a comma-seperated list.

- Environment Variable: `ECK_ENABLE_FILEBEAT`
- Default Value: `false`

### eck_remote_es_username
The username that will be used to authenticate with the remote Elasticsearch instance.

- Environment Variable: `ECK_ENABLE_FILEBEAT`
- Default Value: `false`

### eck_remote_es_password
The password that will be used to authenticate with the remote Elasticsearch instance.

- Environment Variable: `ECK_ENABLE_FILEBEAT`
- Default Value: `false`


Role Variables - Domains and Certificates
-------------------------------------------------------------------------------
Elasticsearch and Kibana can be configured with a custom domain and a certificate signed by [LetsEncrypt](https://letsencrypt.org/).

### es_domain
The domain that Elasticsearch will be accessed from, must be routable to the target OCP cluster.

- Environment Variable: `ECK_ELASTICSEARCH_DOMAIN`
- Default Value: `None`

### kibana_domain
The domain that Kibana will be accessed from, must be routable to the target OCP cluster.

- Environment Variable: `ECK_KIBANA_DOMAIN`
- Default Value: `None`

### letsencrypt_email
Provide the email address which will be used to register the certificates with LetsEncrypt.  When this is provided and one or both domains are set, an `Issuer` will be configured for LetsEncrypt production using a HTTP solver that will installed automatically by Cert-Manager in the ECK namespace.

- Environment Variable: `LETSENCRYPT_EMAIL`
- Default Value: `None`


Example Playbook
----------------

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

License
-------

EPL-2.0
