# aws_documentdb_user

Create dedicated database users in AWS DocumentDB for Maximo Application Suite instances. This role automates user creation with appropriate permissions and generates Kubernetes secrets containing the credentials for MAS MongoDB configuration.

AWS DocumentDB is a MongoDB-compatible database service that can serve as the system database for MAS. This role creates instance-specific users with proper authentication credentials.

**Prerequisites**:
- MongoDB Shell (mongosh) must be installed
- AWS DocumentDB cluster must be running and accessible
- Master user credentials for DocumentDB must be available


## Role Variables

### mas_instance_id
MAS instance identifier for which the DocumentDB user will be created.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

**Purpose**: Identifies the MAS instance and is used to generate the DocumentDB username and Kubernetes secret name.

**When to use**: Always required. Must match the MAS instance that will use this DocumentDB.

**Valid values**: Valid MAS instance ID (typically 3-12 lowercase alphanumeric characters).

**Impact**: Used to create username format `<instance-id>-docdb-user` and secret name `docdb-<instance-id>-instance-credentials`.

**Related variables**: `mas_config_dir`

**Notes**:
- Username will be `<mas_instance_id>-docdb-user`
- Secret name will be `docdb-<mas_instance_id>-instance-credentials`
- Must match the instance ID used during MAS installation

### docdb_host
AWS DocumentDB cluster endpoint hostname.

- **Required** if `docdb_hosts` is not set
- Environment Variable: `DOCDB_HOST`
- Default: None

**Purpose**: Specifies the DocumentDB cluster endpoint for single-host connection configuration.

**When to use**: Use for simple single-endpoint connections. For replica sets with multiple endpoints, use `docdb_hosts` instead.

**Valid values**: Valid DocumentDB cluster endpoint hostname (e.g., `docdb-cluster.abc123.us-east-1.docdb.amazonaws.com`).

**Impact**: Combined with `docdb_port` to form the connection string. If `docdb_hosts` is also set, `docdb_hosts` takes precedence.

**Related variables**: `docdb_port`, `docdb_hosts`

**Notes**:
- Use cluster endpoint for automatic failover
- Instance endpoints can also be used but don't provide automatic failover
- `docdb_hosts` takes precedence if both are set
- Obtain from AWS DocumentDB console or CLI

### docdb_port
AWS DocumentDB connection port.

- **Required** if `docdb_hosts` is not set
- Environment Variable: `DOCDB_PORT`
- Default: None

**Purpose**: Specifies the port number for DocumentDB connections.

**When to use**: Required when using `docdb_host`. Not needed if using `docdb_hosts` (port included in hosts string).

**Valid values**: Valid port number, typically `27017` (default MongoDB port).

**Impact**: Combined with `docdb_host` to form the connection string.

**Related variables**: `docdb_host`, `docdb_hosts`

**Notes**:
- Default DocumentDB port is `27017`
- Must match the port configured in DocumentDB cluster
- Not used if `docdb_hosts` is set

### docdb_hosts
AWS DocumentDB connection string with multiple hosts and ports.

- **Required** if both `docdb_host` and `docdb_port` are not set
- Environment Variable: `DOCDB_HOSTS`
- Default: None

**Purpose**: Provides a complete connection string with multiple DocumentDB endpoints for replica set configurations.

**When to use**: Use for replica set deployments with multiple endpoints. Takes precedence over `docdb_host` and `docdb_port` if all are set.

**Valid values**: Comma-separated list of `host:port` pairs (e.g., `docdb-1.abc.us-east-1.docdb.amazonaws.com:27017,docdb-2.abc.us-east-1.docdb.amazonaws.com:27017,docdb-3.abc.us-east-1.docdb.amazonaws.com:27017`).

**Impact**: Enables connection to multiple DocumentDB instances for high availability and automatic failover.

**Related variables**: `docdb_host`, `docdb_port`

**Notes**:
- **Recommended** for production deployments
- Takes precedence over `docdb_host` and `docdb_port`
- Include all replica set members for best availability
- Format: `host1:port1,host2:port2,host3:port3`
- Obtain from AWS DocumentDB cluster details

### docdb_master_username
AWS DocumentDB master username for administrative access.

- **Required**
- Environment Variable: `DOCDB_MASTER_USERNAME`
- Default: None

**Purpose**: Provides the master user credentials to create the MAS-specific database user.

**When to use**: Always required. Must be the master username configured during DocumentDB cluster creation.

**Valid values**: Valid DocumentDB master username.

**Impact**: Used to authenticate to DocumentDB and create the new MAS user. Must have permissions to create users and grant roles.

**Related variables**: `docdb_master_password`

**Notes**:
- This is the master user created with the DocumentDB cluster
- Credentials are only used during user creation, not stored permanently
- Ensure master user has `userAdmin` or equivalent permissions
- Obtain from AWS Secrets Manager or secure credential store

### docdb_master_password
AWS DocumentDB master password for administrative access.

- **Required**
- Environment Variable: `DOCDB_MASTER_PASSWORD`
- Default: None

**Purpose**: Provides the master user password to authenticate and create the MAS-specific database user.

**When to use**: Always required. Must be the master password configured during DocumentDB cluster creation.

**Valid values**: Valid DocumentDB master password string.

**Impact**: Used to authenticate to DocumentDB and create the new MAS user.

**Related variables**: `docdb_master_username`

**Notes**:
- Store securely and never commit to version control
- Credentials are only used during user creation
- Consider using AWS Secrets Manager for credential management
- Rotate master password regularly per security best practices

### docdb_instance_password
Password for the MAS-specific DocumentDB user being created.

- Optional
- Environment Variable: `DOCDB_INSTANCE_PASSWORD`
- Default: Auto-generated if not provided

**Purpose**: Specifies the password for the new MAS DocumentDB user. If not provided, a secure password is automatically generated.

**When to use**: Provide if you need a specific password. Otherwise, let the role generate a secure random password.

**Valid values**: Strong password string meeting DocumentDB password requirements.

**Impact**: This password will be stored in the Kubernetes secret and used by MAS to connect to DocumentDB.

**Related variables**: `mas_instance_id`, `mas_config_dir`

**Notes**:
- Auto-generation is recommended for security
- If provided, ensure it meets complexity requirements
- Password is stored in Kubernetes secret `docdb-<instance-id>-instance-credentials`
- Keep password secure and rotate regularly

### user_action
Action to perform on the DocumentDB user.

- Optional
- Environment Variable: `USER_ACTION`
- Default: `add`

**Purpose**: Controls whether to create or remove the DocumentDB user.

**When to use**: Set to `add` to create user (default), or `remove` to delete the user.

**Valid values**:
- `add` - Create the DocumentDB user (default)
- `remove` - Delete the DocumentDB user

**Impact**: Determines whether the role creates or removes the user from DocumentDB.

**Related variables**: `mas_instance_id`

**Notes**:
- Default `add` is for normal user creation
- Use `remove` when decommissioning a MAS instance
- Removing user does not delete the Kubernetes secret
- Verify user removal: `mongosh` to DocumentDB and check users

### mas_config_dir
Local directory where the generated Kubernetes secret YAML will be saved.

- Optional
- Environment Variable: `MAS_CONFIG_DIR`
- Default: None

**Purpose**: Specifies the output directory for the generated Kubernetes secret containing DocumentDB credentials.

**When to use**: Set when you want to save the generated secret YAML for later application or documentation.

**Valid values**: Valid directory path where the Ansible controller has write permissions.

**Impact**: If set, a YAML file with the DocumentDB credentials secret will be created in this directory.

**Related variables**: `mas_instance_id`

**Notes**:
- Secret filename: `docdb-<instance-id>-instance-credentials.yaml`
- Can be applied with: `oc apply -f <file>`
- Keep generated files secure as they contain credentials
- Useful for GitOps workflows or manual secret management

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

## Example Playbook

```yaml
- hosts: localhost
  vars:
    # Add required variables here
  roles:
    - ibm.mas_devops.aws_documentdb_user
```

## License

EPL-2.0
