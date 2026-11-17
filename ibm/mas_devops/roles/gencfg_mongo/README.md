# gencfg_mongo

Generate MongoDB configuration files for connecting Maximo Application Suite to external MongoDB or MongoDB-compatible databases. This role creates MongoCfg custom resources that can be applied to MAS instances to configure the system database connectivity.

The role supports various MongoDB deployments including MongoDB Community Edition, MongoDB Enterprise, IBM Cloud Databases for MongoDB, and Amazon DocumentDB, with flexible authentication mechanisms and SSL/TLS support.


## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`mongodb_admin_username`](#mongodb_admin_username) | Yes | None |
| [`mongodb_admin_password`](#mongodb_admin_password) | Yes | None |
| [`mongodb_hosts`](#mongodb_hosts) | Yes | None |
| [`mongodb_authentication_mechanism`](#mongodb_authentication_mechanism) | No | `DEFAULT` |
| [`mongodb_authentication_database`](#mongodb_authentication_database) | No | `admin` |
| [`mongodb_retry_writes`](#mongodb_retry_writes) | No | `true` |
| [`mongodb_ca_pem_local_file`](#mongodb_ca_pem_local_file) | Yes | None |
| [`mongodb_namespace`](#mongodb_namespace) | No | `mongoce` |
| [`mas_instance_id`](#mas_instance_id) | Yes | None |
| [`mas_config_dir`](#mas_config_dir) | Yes | None |
| [`custom_labels`](#custom_labels) | No | None |

### MongoDB Connection

#### mongodb_admin_username

MongoDB user account that MAS will use to connect to the MongoDB system database — for SCRAM authentication a standard MongoDB username, for LDAP authentication an LDAP distinguished name or username.

- **Required**
- Environment Variable: `MONGODB_ADMIN_USERNAME`
- Default: None

The user must have read/write access (`readWrite` role) to the MAS databases; insufficient permissions will cause MAS core services to fail. Consider using a dedicated service account rather than the MongoDB admin user.

#### mongodb_admin_password

Password for the MongoDB user account specified in `mongodb_admin_username`.

- **Required**
- Environment Variable: `MONGODB_ADMIN_PASSWORD`
- Default: None

The password is stored as a Kubernetes secret in the MAS namespace. For Amazon DocumentDB, use the master user password or IAM authentication.

#### mongodb_hosts

MongoDB connection endpoints as a comma-separated list of `hostname:port` pairs — for example `mongodb.example.com:27017` for a single node, `mongo-1.example.com:27017,mongo-2.example.com:27017,mongo-3.example.com:27017` for a replica set, or `docdb-cluster.abc123.us-east-1.docdb.amazonaws.com:27017` for Amazon DocumentDB.

- **Required**
- Environment Variable: `MONGODB_HOSTS`
- Default: None

Always include the port number (typically 27017) and list all replica set members for redundancy and automatic failover. Hostnames must be resolvable from the OpenShift cluster, and for cloud databases verify network connectivity and firewall rules.

#### mongodb_authentication_mechanism

Authentication mechanism for connecting to MongoDB — `DEFAULT` for MongoDB's standard SCRAM authentication (SCRAM-SHA-256 or SCRAM-SHA-1), or `PLAIN` for LDAP authentication (requires MongoDB Enterprise with LDAP integration).

- **Optional**
- Environment Variable: `MONGODB_AUTHENTICATION_MECHANISM`
- Default: `DEFAULT`

Must match the authentication configuration of your MongoDB deployment. Amazon DocumentDB uses SCRAM authentication, so use `DEFAULT`; when using `PLAIN`, ensure `mongodb_authentication_database` is set to `$external`.

#### mongodb_authentication_database

MongoDB database that contains the user credentials for authentication — `admin` for standard MongoDB authentication, `$external` for LDAP authentication, or a custom database name if users are stored elsewhere.

- **Optional**
- Environment Variable: `MONGODB_AUTHENTICATION_DATABASE`
- Default: `admin`

Must be `$external` when `mongodb_authentication_mechanism` is `PLAIN`; for Amazon DocumentDB use `admin`. Rarely needs changing from the default unless using custom user databases.

#### mongodb_retry_writes

Whether the MongoDB driver automatically retries write operations that fail due to transient network errors or replica set elections — `true` or `false`.

- **Optional**
- Environment Variable: `MONGODB_RETRY_WRITES`
- Default: `true`

Recommended `true` for MongoDB 3.6+ replica sets; standalone MongoDB instances may not support retryable writes.

!!! warning
    Must be set to `false` for Amazon DocumentDB — DocumentDB does not support retryable writes, and connections will fail if this is enabled.

#### mongodb_ca_pem_local_file

Local file path to the MongoDB SSL/TLS CA certificate in PEM format — for example `/tmp/mongo-ca.pem` or `./certs/mongodb-cert.pem`.

- **Required**
- Environment Variable: `MONGODB_CA_PEM_LOCAL_FILE`
- Default: None

MongoDB connections should always use SSL/TLS encryption. The certificate is embedded in the generated MongoCfg resource; without the correct CA certificate, SSL/TLS connections will fail with certificate validation errors. The file must be accessible from the Ansible controller and be in PEM format (Base64-encoded with BEGIN/END markers). For Amazon DocumentDB download the CA certificate from AWS, for IBM Cloud Databases from the IBM Cloud console, and for self-signed certificates provide the CA that signed the MongoDB server certificate.

### Configuration Generation

#### mongodb_namespace

Namespace identifier used as a suffix in the generated configuration filename (`mongo-<namespace>.yml`) — for example `mongoce`, `docdb`, or `prod-mongo`.

- **Optional**
- Environment Variable: `MONGODB_NAMESPACE`
- Default: `mongoce`

Only affects the generated filename, not the MongoDB connection or MAS configuration; the default `mongoce` indicates MongoDB Community Edition. Use descriptive names when managing multiple MongoDB instances.

#### mas_instance_id

MAS instance identifier that the MongoDB configuration is being generated for — typically 3-12 lowercase alphanumeric characters, case-sensitive, matching the instance ID used during MAS installation.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

The generated configuration is namespace-scoped to `mas-<instance_id>-core`; an incorrect instance ID will cause the configuration to be created in the wrong namespace. MongoDB is the system database for MAS core services.

#### mas_config_dir

Local directory path where the generated MongoCfg YAML file will be saved — the directory is created if it doesn't exist.

- **Required**
- Environment Variable: `MAS_CONFIG_DIR`
- Default: None

The generated file is named `mongo-<mongodb_namespace>.yml` and can be applied using `kubectl apply` or used as input to the [suite_config](suite_config.md) role; keep generated files for documentation and disaster recovery purposes.

### Resource Labels

#### custom_labels

Custom Kubernetes labels to apply to the generated MongoCfg resource, as comma-separated key=value pairs — for example `env=prod,team=platform,cost-center=12345`.

- **Optional**
- Environment Variable: `CUSTOM_LABELS`
- Default: None

Labels are useful for environment identification, cost tracking, GitOps workflows, and selection with label selectors in automation scripts; they must follow Kubernetes naming conventions.

## Example Playbook

```yaml

- hosts: localhost
  any_errors_fatal: true
  vars:
    mongodb_namespace: mongoce
    mongodb_admin_username: mongoadmin
    mongodb_admin_password: mongo-strong-password
    mongodb_hosts: docdb-1.abc.ca-central-1.docdb.amazonaws.com:27017,docdb-2.def.ca-central-1.docdb.amazonaws.com:27017
    mongodb_retry_writes: false
    mongodb_ca_pem_local_file: /tmp/mongo-ca.pem
    mas_instance_id: masinst1
    mas_config_dir: ~/masconfig
  roles:
    - ibm.mas_devops.gencfg_mongo
```

## License

EPL-2.0
