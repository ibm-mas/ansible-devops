gencfg_mongo
============

Generate MongoDB configuration files for connecting Maximo Application Suite to external MongoDB or MongoDB-compatible databases. This role creates MongoCfg custom resources that can be applied to MAS instances to configure the system database connectivity.

The role supports various MongoDB deployments including MongoDB Community Edition, MongoDB Enterprise, IBM Cloud Databases for MongoDB, and Amazon DocumentDB, with flexible authentication mechanisms and SSL/TLS support.


Role Variables
-------------------------------------------------------------------------------

### mongodb_namespace
Namespace identifier used in the generated configuration filename.

- Optional
- Environment Variable: `MONGODB_NAMESPACE`
- Default: `mongoce`

**Purpose**: Provides a suffix for the generated configuration filename to help identify the MongoDB deployment source or environment.

**When to use**: Customize when managing multiple MongoDB configurations or to clearly identify the MongoDB deployment type (e.g., `mongoce`, `docdb`, `ibmcloud`).

**Valid values**: Alphanumeric string, typically lowercase (e.g., `mongoce`, `docdb`, `prod-mongo`, `dev-mongodb`).

**Impact**: Only affects the generated filename (`mongo-<namespace>.yml`). Does not impact the actual MongoDB connection or MAS configuration.

**Related variables**: `mas_config_dir`

**Notes**:
- Default `mongoce` indicates MongoDB Community Edition
- Use descriptive names when managing multiple MongoDB instances
- Filename helps with organization but doesn't affect functionality

### mongodb_admin_username
MongoDB administrative username for authentication.

- **Required**
- Environment Variable: `MONGODB_ADMIN_USERNAME`
- Default: None

**Purpose**: Specifies the MongoDB user account that MAS will use to connect to the MongoDB database for system data storage.

**When to use**: Always required. Must be a valid MongoDB user with appropriate permissions for MAS operations.

**Valid values**: Valid MongoDB username according to the authentication mechanism being used.

**Impact**: This user must have read/write access to the MAS databases. Insufficient permissions will cause MAS core services to fail.

**Related variables**: `mongodb_admin_password`, `mongodb_authentication_mechanism`, `mongodb_authentication_database`

**Notes**:
- For SCRAM authentication: Standard MongoDB username
- For LDAP authentication: LDAP distinguished name or username
- User must have `readWrite` role on MAS databases
- Consider using a dedicated service account rather than the MongoDB admin user

### mongodb_admin_password
MongoDB password for authentication.

- **Required**
- Environment Variable: `MONGODB_ADMIN_PASSWORD`
- Default: None

**Purpose**: Provides the password for the MongoDB user account specified in `mongodb_admin_username`.

**When to use**: Always required for MongoDB authentication.

**Valid values**: Valid password string meeting your MongoDB security requirements.

**Impact**: Stored as a Kubernetes secret in the MAS namespace. Incorrect password will prevent MAS from connecting to MongoDB.

**Related variables**: `mongodb_admin_username`, `mongodb_authentication_mechanism`

**Notes**:
- Password is stored securely in Kubernetes secrets
- Use strong passwords meeting your organization's security policies
- For Amazon DocumentDB, use the master user password or IAM authentication
- Consider implementing password rotation policies

### mongodb_authentication_mechanism
MongoDB authentication method to use for connections.

- Optional
- Environment Variable: `MONGODB_AUTHENTICATION_MECHANISM`
- Default: `DEFAULT`

**Purpose**: Specifies the authentication mechanism for connecting to MongoDB, supporting both standard MongoDB authentication and LDAP integration.

**When to use**: Set to `DEFAULT` for standard MongoDB authentication (SCRAM-SHA-256/SCRAM-SHA-1), or `PLAIN` for LDAP authentication.

**Valid values**:
- `DEFAULT` - Use MongoDB's default SCRAM authentication (SCRAM-SHA-256 or SCRAM-SHA-1)
- `PLAIN` - Use LDAP authentication (requires LDAP-enabled MongoDB)

**Impact**: Must match the authentication configuration of your MongoDB deployment. Mismatch will cause authentication failures.

**Related variables**: `mongodb_authentication_database` (must be `$external` when using `PLAIN`)

**Notes**:
- `DEFAULT` is suitable for most MongoDB deployments
- `PLAIN` requires MongoDB Enterprise with LDAP integration
- Amazon DocumentDB uses SCRAM authentication (use `DEFAULT`)
- When using `PLAIN`, ensure `mongodb_authentication_database` is set to `$external`

### mongodb_authentication_database
MongoDB database used for authentication.

- Optional
- Environment Variable: `MONGODB_AUTHENTICATION_DATABASE`
- Default: `admin`

**Purpose**: Specifies which MongoDB database contains the user credentials for authentication.

**When to use**: Use `admin` for standard MongoDB authentication, or `$external` for LDAP authentication.

**Valid values**:
- `admin` - Standard MongoDB authentication database
- `$external` - External authentication (LDAP)
- Custom database name if users are stored elsewhere

**Impact**: Must match where the user credentials are stored in MongoDB. Incorrect value will cause authentication failures.

**Related variables**: `mongodb_authentication_mechanism` (must be `PLAIN` when using `$external`)

**Notes**:
- Default `admin` is correct for most deployments
- Must be `$external` when `mongodb_authentication_mechanism` is `PLAIN`
- For Amazon DocumentDB, use `admin`
- Rarely needs to be changed from default unless using custom user databases

### mongodb_hosts
MongoDB connection endpoints including hostnames and ports.

- **Required**
- Environment Variable: `MONGODB_HOSTS`
- Default: None

**Purpose**: Defines the MongoDB server addresses that MAS will connect to, supporting both single-node and replica set deployments.

**When to use**: Always required. Provide all replica set members for high availability deployments.

**Valid values**: Comma-separated list of `hostname:port` pairs. Examples:
- Single node: `mongodb.example.com:27017`
- Replica set: `mongo-1.example.com:27017,mongo-2.example.com:27017,mongo-3.example.com:27017`
- Amazon DocumentDB: `docdb-cluster.abc123.us-east-1.docdb.amazonaws.com:27017`

**Impact**: MAS will attempt to connect to these hosts in order. For replica sets, providing all members ensures high availability and automatic failover.

**Related variables**: `mongodb_retry_writes`, `mongodb_ca_pem_local_file`

**Notes**:
- Always include port numbers (typically 27017)
- For replica sets, list all members for redundancy
- For Amazon DocumentDB, use the cluster endpoint or individual instance endpoints
- Ensure hostnames are resolvable from the OpenShift cluster
- For cloud databases, verify network connectivity and firewall rules

### mongodb_retry_writes
Enable MongoDB retryable writes feature.

- Optional
- Environment Variable: `MONGODB_RETRY_WRITES`
- Default: `true`

**Purpose**: Controls whether MongoDB driver will automatically retry write operations that fail due to transient network errors or replica set elections.

**When to use**: Set to `true` for MongoDB 3.6+ with replica sets. Set to `false` for Amazon DocumentDB or standalone MongoDB instances.

**Valid values**:
- `true` - Enable retryable writes (recommended for MongoDB replica sets)
- `false` - Disable retryable writes (required for Amazon DocumentDB)

**Impact**: When enabled, improves reliability by automatically retrying failed writes. Amazon DocumentDB does not support this feature and will fail if enabled.

**Related variables**: `mongodb_hosts`

**Notes**:
- **Critical**: Must be `false` for Amazon DocumentDB
- Recommended to be `true` for MongoDB replica sets (3.6+)
- Standalone MongoDB instances may not support retryable writes
- Improves application resilience in replica set environments

### mongodb_ca_pem_local_file
Local file path to the MongoDB SSL/TLS CA certificate in PEM format.

- **Required**
- Environment Variable: `MONGODB_CA_PEM_LOCAL_FILE`
- Default: None

**Purpose**: Provides the SSL/TLS certificate authority certificate for secure MongoDB connections. The certificate is embedded in the generated MongoCfg resource.

**When to use**: Always required for production deployments. MongoDB connections should always use SSL/TLS encryption.

**Valid values**: Absolute or relative file path to a valid PEM-encoded CA certificate file (e.g., `/tmp/mongo-ca.pem`, `./certs/mongodb-cert.pem`).

**Impact**: Without the correct CA certificate, SSL/TLS connections will fail with certificate validation errors. MAS will not be able to connect to MongoDB.

**Related variables**: `mongodb_hosts`

**Notes**:
- The file must be accessible from the Ansible controller
- For Amazon DocumentDB, download the CA certificate from AWS
- For IBM Cloud Databases, download from the IBM Cloud console
- Certificate must be in PEM format (Base64-encoded with BEGIN/END markers)
- For self-signed certificates, this should be the CA that signed the MongoDB server certificate

### mas_instance_id
MAS instance identifier for which the MongoDB configuration is being generated.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

**Purpose**: Identifies the target MAS instance where this MongoDB configuration will be applied.

**When to use**: Always required. Must match an existing MAS instance ID.

**Valid values**: Valid MAS instance ID (typically 3-12 lowercase alphanumeric characters).

**Impact**: The generated configuration will be namespace-scoped to `mas-<instance-id>-core`. Incorrect instance ID will cause the configuration to be created in the wrong namespace.

**Related variables**: `mas_config_dir`

**Notes**:
- Must match the instance ID used during MAS installation
- Case-sensitive value
- Cannot be changed after MAS installation
- MongoDB is the system database for MAS core services

### mas_config_dir
Local directory path where the generated YAML configuration file will be saved.

- **Required**
- Environment Variable: `MAS_CONFIG_DIR`
- Default: None

**Purpose**: Specifies the output directory for the generated MongoCfg YAML file that can be applied to the MAS instance.

**When to use**: Always required. Directory must exist or be creatable by the Ansible user.

**Valid values**: Valid directory path (absolute or relative) where the Ansible controller has write permissions.

**Impact**: The generated YAML file will be created in this directory and can be applied using `kubectl apply` or the `suite_config` role.

**Related variables**: `mas_instance_id`, `mongodb_namespace`

**Notes**:
- Directory will be created if it doesn't exist
- Generated filename format: `mongo-<mongodb_namespace>.yml`
- Keep generated files for documentation and disaster recovery purposes
- Can be used as input to the `suite_config` role

### custom_labels
Custom Kubernetes labels to apply to the generated MongoCfg resource.

- Optional
- Environment Variable: `CUSTOM_LABELS`
- Default: None

**Purpose**: Adds custom labels to the MongoCfg resource for organization, filtering, or automation purposes.

**When to use**: Use when you need to tag configurations for specific purposes like environment identification, cost tracking, or automated management.

**Valid values**: Comma-separated key=value pairs (e.g., `env=prod,team=platform,cost-center=12345`).

**Impact**: Labels are applied to the Kubernetes resource and can be used for selection, filtering, and automation workflows.

**Related variables**: None

**Notes**:
- Labels must follow Kubernetes naming conventions
- Useful for GitOps workflows and resource management
- Can be used with label selectors in automation scripts

Example Playbook
----------------

```yaml
---

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

License
-------

EPL-2.0
