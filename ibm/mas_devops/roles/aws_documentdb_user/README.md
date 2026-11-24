# aws_documentdb_user

Create dedicated database users in AWS DocumentDB for Maximo Application Suite instances. This role automates user creation with appropriate permissions and generates Kubernetes secrets containing the credentials for MAS MongoDB configuration.

AWS DocumentDB is a MongoDB-compatible database service that can serve as the system database for MAS. This role creates instance-specific users with proper authentication credentials.

## Prerequisites

- MongoDB Shell (mongosh) must be installed
- AWS DocumentDB cluster must be running and accessible
- Master user credentials for DocumentDB must be available

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`mas_instance_id`](#mas_instance_id) | Yes | None |
| [`mas_config_dir`](#mas_config_dir) | No | None |
| [`docdb_host`](#docdb_host) | Conditional | None |
| [`docdb_port`](#docdb_port) | Conditional | None |
| [`docdb_hosts`](#docdb_hosts) | Conditional | None |
| [`docdb_master_username`](#docdb_master_username) | Yes | None |
| [`docdb_master_password`](#docdb_master_password) | Yes | None |
| [`user_action`](#user_action) | No | `add` |
| [`docdb_instance_password`](#docdb_instance_password) | No | Auto-generated |

Either `docdb_hosts` or both `docdb_host` and `docdb_port` must be set to define the DocumentDB connection; if all are set, `docdb_hosts` takes precedence.

### MAS Integration

#### mas_instance_id

MAS instance identifier for which the DocumentDB user will be created — a valid MAS instance ID (typically 3-12 lowercase alphanumeric characters) that must match the instance ID used during MAS installation.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

Determines the generated username (`<mas_instance_id>-docdb-user`) and the Kubernetes secret name (`docdb-<mas_instance_id>-instance-credentials`).

#### mas_config_dir

Local directory where the generated Kubernetes secret YAML will be saved — a valid directory path where the Ansible controller has write permissions.

- **Optional**
- Environment Variable: `MAS_CONFIG_DIR`
- Default: None

When set, a YAML file with the DocumentDB credentials secret (`docdb-<instance-id>-instance-credentials.yaml`) is created in this directory, which can be applied with `oc apply -f <file>`. Useful for GitOps workflows or manual secret management — keep the generated files secure as they contain credentials.

### Connection Details

#### docdb_host

AWS DocumentDB cluster endpoint hostname, for single-host connections — for example `docdb-cluster.abc123.us-east-1.docdb.amazonaws.com`.

- **Required** when `docdb_hosts` is not set
- Environment Variable: `DOCDB_HOST`
- Default: None

Combined with `docdb_port` to form the connection string; `docdb_hosts` takes precedence if both are set. Use the cluster endpoint for automatic failover — instance endpoints can also be used but do not provide it. Obtain from the AWS DocumentDB console or CLI.

#### docdb_port

Port number for DocumentDB connections, typically `27017` (the default MongoDB/DocumentDB port).

- **Required** when `docdb_hosts` is not set
- Environment Variable: `DOCDB_PORT`
- Default: None

Combined with `docdb_host` to form the connection string. Not used when `docdb_hosts` is set (the port is included in the hosts string). Must match the port configured in the DocumentDB cluster.

#### docdb_hosts

Complete DocumentDB connection string with multiple endpoints for replica set configurations, as a comma-separated list of `host:port` pairs — for example `docdb-1.abc.us-east-1.docdb.amazonaws.com:27017,docdb-2.abc.us-east-1.docdb.amazonaws.com:27017,docdb-3.abc.us-east-1.docdb.amazonaws.com:27017`.

- **Required** when both `docdb_host` and `docdb_port` are not set
- Environment Variable: `DOCDB_HOSTS`
- Default: None

Enables connection to multiple DocumentDB instances for high availability and automatic failover, and takes precedence over `docdb_host` and `docdb_port` when all are set. Recommended for production deployments — include all replica set members for best availability.

### Master Credentials

#### docdb_master_username

AWS DocumentDB master username for administrative access — the master username configured during DocumentDB cluster creation.

- **Required**
- Environment Variable: `DOCDB_MASTER_USERNAME`
- Default: None

Used to authenticate to DocumentDB and create the new MAS user, so it must have `userAdmin` or equivalent permissions to create users and grant roles. Credentials are only used during user creation, not stored permanently — obtain from AWS Secrets Manager or a secure credential store.

#### docdb_master_password

AWS DocumentDB master password for administrative access — the master password configured during DocumentDB cluster creation.

- **Required**
- Environment Variable: `DOCDB_MASTER_PASSWORD`
- Default: None

Used together with `docdb_master_username` to authenticate and create the MAS-specific database user. Store it securely, never commit it to version control, and rotate it regularly per security best practices.

### User Management

#### user_action

Action to perform on the DocumentDB user — `add` (create the user, default) or `remove` (delete the user).

- **Optional**
- Environment Variable: `USER_ACTION`
- Default: `add`

Use `remove` when decommissioning a MAS instance; note that removing the user does not delete the Kubernetes secret. User removal can be verified by connecting to DocumentDB with `mongosh` and checking the users.

#### docdb_instance_password

Password for the MAS-specific DocumentDB user being created — a strong password string meeting DocumentDB password requirements.

- **Optional**
- Environment Variable: `DOCDB_INSTANCE_PASSWORD`
- Default: Auto-generated

If not provided, a secure random password is generated (recommended). The password is stored in the Kubernetes secret `docdb-<instance-id>-instance-credentials` and used by MAS to connect to DocumentDB — keep it secure and rotate it regularly.

## Example Playbook

### Single-host connection

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    docdb_master_username: test-user
    docdb_master_password: test-pass-***
    docdb_host: test1.aws-01....
    docdb_port: 27017

  roles:
    - ibm.mas_devops.aws_documentdb_user
```

### Replica set connection

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    docdb_master_username: test-user
    docdb_master_password: test-pass-***
    docdb_hosts: test1.aws-01:27017,test1.aws-02:27017,test1.aws-03:27017

  roles:
    - ibm.mas_devops.aws_documentdb_user
```

## License

EPL-2.0
