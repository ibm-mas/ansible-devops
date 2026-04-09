# suite_manage_logging_config

This role configures cloud object storage (IBM Cloud Object Storage or AWS S3) for storing Maximo Manage application server logs. Storing logs in object storage enables centralized log management, long-term retention, and analysis without consuming cluster storage.

!!! important "Prerequisites"
    Manage application must be deployed and activated before configuring logging storage.

## What This Role Does

- Configures cloud storage bucket for Manage server logs
- Updates Manage database with logging storage configuration
- Automatically executes `cos_bucket` role to set up bucket
- Enables log shipping from Manage pods to object storage
- Supports both IBM Cloud Object Storage and AWS S3

## Role Variables

### cos_type
Cloud object storage provider type.

- **Required**
- Environment Variable: `COS_TYPE`
- Default: None

**Purpose**: Specifies which cloud storage provider to use for Manage application server logs.

**When to use**:
- Always required for logging configuration
- Choose based on your cloud infrastructure
- Determines which credentials and configuration are needed

**Valid values**: `ibm`, `aws`
- `ibm`: IBM Cloud Object Storage
- `aws`: Amazon S3

**Impact**:
- `ibm`: Uses IBM Cloud Object Storage (requires `ibmcloud_apikey`, `cos_instance_name`, `cos_bucket_name`)
- `aws`: Uses AWS S3 (requires AWS credentials and bucket configuration)

**Related variables**:
- `mas_instance_id`: Instance whose logs are stored
- `db2_instance_name`: Database to update with logging config

**Note**: The `cos_bucket` role is automatically executed to set up the bucket. Ensure you provide the required variables for your chosen provider (e.g., `cos_instance_name` and `ibmcloud_apikey` for IBM, or AWS credentials for S3).

### mas_instance_id
MAS instance identifier.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

**Purpose**: Identifies which MAS instance contains the Manage application whose logs will be stored in object storage.

**When to use**:
- Always required for logging configuration
- Must match the instance ID from MAS installation
- Used to locate Manage resources

**Valid values**: Lowercase alphanumeric string, 3-12 characters (e.g., `prod`, `dev`, `masinst1`)

**Impact**: Determines which MAS instance's Manage application is configured for log storage in object storage.

**Related variables**:
- `mas_workspace_id`: Workspace within this instance
- `db2_instance_name`: Database for this Manage instance

**Note**: This must match the instance ID used during Manage installation.

### mas_workspace_id
Workspace identifier for Manage application.

- **Required**
- Environment Variable: `MAS_WORKSPACE_ID`
- Default: None

**Purpose**: Identifies which workspace within the MAS instance contains the Manage application whose logs will be stored.

**When to use**:
- Always required for logging configuration
- Must match the workspace ID where Manage is deployed
- Used to locate Manage resources

**Valid values**: Lowercase alphanumeric string, typically 3-12 characters (e.g., `prod`, `dev`, `masdev`)

**Impact**: Determines which workspace's Manage application is configured for log storage.

**Related variables**:
- `mas_instance_id`: Parent instance
- `db2_instance_name`: Database for this workspace's Manage

**Note**: This must match the workspace ID used during Manage installation.

### db2_instance_name
Db2 Warehouse instance name.

- **Required**
- Environment Variable: `DB2_INSTANCE_NAME`
- Default: None

**Purpose**: Identifies the Db2 Warehouse instance that stores Manage application data, which will be updated with logging storage configuration.

**When to use**:
- Always required for logging configuration
- Must match the Db2 instance name used by Manage
- Used to connect to database for configuration updates

**Valid values**: Valid Db2 instance name (e.g., `db2w-manage`, `db2u-manage`)

**Impact**: Determines which Db2 instance is accessed to update logging configuration via SQL.

**Related variables**:
- `db2_namespace`: Namespace containing this instance
- `db2_dbname`: Database name within the instance
- `mas_instance_id`: MAS instance using this database

**Note**: To find the instance name, go to the Db2 namespace and look for pods with `label=engine`. Describe the pod and find the `app` label value - that's your instance name.

### db2_namespace
Db2 Warehouse namespace.

- **Optional**
- Environment Variable: `DB2_NAMESPACE`
- Default: `db2u`

**Purpose**: Specifies the OpenShift namespace where the Db2 Warehouse instance is deployed.

**When to use**:
- Use default (`db2u`) for standard Db2 deployments
- Override if Db2 is deployed in a custom namespace
- Required to locate the Db2 instance

**Valid values**: Valid Kubernetes namespace name

**Impact**: Determines where to look for the Db2 instance when connecting for logging configuration updates.

**Related variables**:
- `db2_instance_name`: Instance to find in this namespace
- `db2_dbname`: Database within the instance

**Note**: The default `db2u` namespace is used by most Db2 Warehouse deployments. Only change if you have a custom deployment.

### db2_dbname
Database name within Db2 instance.

- **Optional**
- Environment Variable: `DB2_DBNAME`
- Default: `BLUDB`

**Purpose**: Specifies the database name within the Db2 instance where Manage tables and logging configuration are stored.

**When to use**:
- Use default (`BLUDB`) for standard Manage deployments
- Override if Manage uses a custom database name
- Required for database connection

**Valid values**: Valid Db2 database name

**Impact**: Determines which database within the Db2 instance is updated with logging storage configuration.

**Related variables**:
- `db2_instance_name`: Instance containing this database
- `db2_namespace`: Namespace of the instance

**Note**: `BLUDB` is the default database name for Manage deployments. Only change if you have a custom database configuration.

## Example Playbook

### Configure IBM Cloud COS for Existing Manage Instance
The following sample can be used to configure COS for an existing Manage application instance:

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_workspace_id: masdev
    cos_type: ibm
    db2_instance_name: db2w-manage
    cos_instance_name: cos-masinst1
    cos_bucket_name: manage-logs-bucket
    ibmcloud_apikey: xxxx
  roles:
    - ibm.mas_devops.suite_manage_logging_config
```

### Configure AWS S3 for Existing Manage Instance
The following sample can be used to configure AWS S3 for an existing Manage application instance:

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_workspace_id: masdev
    cos_type: aws
    cos_bucket_action: create
    aws_bucket_name: manage-logs-bucket
    aws_region: us-east-2
    aws_bucket_versioning_flag: True
    aws_bucket_encryption: '{"Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]}'
    db2_instance_name: db2w-manage
  roles:
    - ibm.mas_devops.suite_manage_logging_config
```

### Provision and Configure IBM Cloud COS
The following sample playbook can be used to provision COS in IBM Cloud and configure COS for an existing Manage application instance:

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_workspace_id: masdev
    db2_instance_name: db2w-manage
    cos_type: ibm
    cos_instance_name: cos-masinst1
    cos_bucket_name: manage-logs-bucket
    ibmcloud_apikey: xxxx
  roles:
    - ibm.mas_devops.cos
    - ibm.mas_devops.suite_manage_logging_config
```

## License
EPL-2.0
