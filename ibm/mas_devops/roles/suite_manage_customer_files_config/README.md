# suite_manage_customer_files_config

This role configures cloud object storage (IBM Cloud Object Storage or AWS S3) for storing Maximo Manage application customer files. Customer files include user-uploaded documents, images, and other files that need to be stored separately from the database.

!!! important "Prerequisites"
    This role must be executed **after** Manage application is deployed and activated. Manage must be up and running before configuring customer files features.

## What This Role Does

- Creates three S3/COS buckets for customer files management:
  - **Main bucket**: Stores active customer files
  - **Backup bucket**: Stores backup copies of customer files
  - **Recovery bucket**: Used for disaster recovery scenarios
- Configures Manage to use cloud storage for customer files
- Automatically executes `cos_bucket` role to set up buckets
- Updates ManageWorkspace CR with storage configuration

## Default Bucket Names

The role creates three buckets with these default names:
- `{mas_instance_id}-{mas_workspace_id}-custfiles`
- `{mas_instance_id}-{mas_workspace_id}-custfilesbackup`
- `{mas_instance_id}-{mas_workspace_id}-custfilesrecovery`

## Role Variables

### cos_type
Cloud object storage provider type.

- **Required**
- Environment Variable: `COS_TYPE`
- Default: None

**Purpose**: Specifies which cloud storage provider to use for Manage customer files storage.

**When to use**:
- Always required for customer files configuration
- Choose based on your cloud infrastructure
- Determines which credentials and CLI tools are needed

**Valid values**: `ibm`, `aws`
- `ibm`: IBM Cloud Object Storage
- `aws`: Amazon S3

**Impact**:
- `ibm`: Uses IBM Cloud Object Storage (requires `ibmcloud_apikey`, `cos_instance_name`)
- `aws`: Uses AWS S3 (requires AWS CLI installed and AWS credentials configured)

**Related variables**:
- `custfiles_bucketname`: Main bucket to create
- `mas_instance_id`: Used in default bucket names

**Note**: For AWS, you must install [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) and configure credentials via `aws configure` or export `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables.

### custfiles_bucketname
Main customer files bucket name.

- **Optional**
- Environment Variable: `MANAGE_CUSTFILES_BUCKET_NAME`
- Default: `{mas_instance_id}-{mas_workspace_id}-custfiles`

**Purpose**: Specifies the name of the primary S3/COS bucket where active customer files are stored.

**When to use**:
- Use default for standard naming convention
- Override for custom bucket naming requirements
- Must be unique within the storage provider

**Valid values**: Valid S3/COS bucket name (lowercase, alphanumeric, hyphens)

**Impact**: Determines where Manage stores active customer files. The bucket will be created if it doesn't exist.

**Related variables**:
- `cos_type`: Storage provider for this bucket
- `custfiles_bucketname_backup`: Related backup bucket
- `custfiles_bucketname_recovery`: Related recovery bucket

**Note**: Bucket names must be globally unique in AWS S3. For IBM COS, they must be unique within your account. The default naming includes instance and workspace IDs to ensure uniqueness.

### custfiles_bucketname_backup
Backup customer files bucket name.

- **Optional**
- Environment Variable: `MANAGE_CUSTFILES_BACKUP_BUCKET_NAME`
- Default: `{mas_instance_id}-{mas_workspace_id}-custfilesbackup`

**Purpose**: Specifies the name of the S3/COS bucket used to store backup copies of customer files.

**When to use**:
- Use default for standard naming convention
- Override for custom bucket naming requirements
- Part of the backup and recovery strategy

**Valid values**: Valid S3/COS bucket name (lowercase, alphanumeric, hyphens)

**Impact**: Determines where backup copies of customer files are stored. Used during backup operations to preserve file versions.

**Related variables**:
- `cos_type`: Storage provider for this bucket
- `custfiles_bucketname`: Main files bucket
- `custfiles_bucketname_recovery`: Recovery bucket

**Note**: Keep backup bucket separate from main bucket for data protection. The default naming appends "backup" to clearly identify the bucket purpose.

### custfiles_bucketname_recovery
Recovery customer files bucket name.

- **Optional**
- Environment Variable: `MANAGE_CUSTFILES_RECOVERY_BUCKET_NAME`
- Default: `{mas_instance_id}-{mas_workspace_id}-custfilesrecovery`

**Purpose**: Specifies the name of the S3/COS bucket used for disaster recovery of customer files.

**When to use**:
- Use default for standard naming convention
- Override for custom bucket naming requirements
- Part of the disaster recovery strategy

**Valid values**: Valid S3/COS bucket name (lowercase, alphanumeric, hyphens)

**Impact**: Determines where recovery copies of customer files are stored. Used during disaster recovery scenarios to restore files.

**Related variables**:
- `cos_type`: Storage provider for this bucket
- `custfiles_bucketname`: Main files bucket
- `custfiles_bucketname_backup`: Backup bucket

**Note**: Keep recovery bucket separate from main and backup buckets for maximum data protection. The default naming appends "recovery" to clearly identify the bucket purpose.

### mas_instance_id
MAS instance identifier.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

**Purpose**: Identifies which MAS instance contains the Manage application to configure for customer files storage.

**When to use**:
- Always required for customer files configuration
- Must match the instance ID from MAS installation
- Used in default bucket name construction

**Valid values**: Lowercase alphanumeric string, 3-12 characters (e.g., `prod`, `dev`, `masinst1`)

**Impact**: Used to construct default bucket names and locate Manage application resources.

**Related variables**:
- `mas_workspace_id`: Workspace within this instance
- `custfiles_bucketname`: Uses instance ID in default name
- `manage_workspace_cr_name`: Constructed from instance and workspace IDs

**Note**: This must match the instance ID used during Manage installation.

### mas_workspace_id
Workspace identifier for Manage application.

- **Required**
- Environment Variable: `MAS_WORKSPACE_ID`
- Default: None

**Purpose**: Identifies which workspace within the MAS instance contains the Manage application to configure for customer files storage.

**When to use**:
- Always required for customer files configuration
- Must match the workspace ID where Manage is deployed
- Used in default bucket name construction

**Valid values**: Lowercase alphanumeric string, typically 3-12 characters (e.g., `prod`, `dev`, `masdev`)

**Impact**: Used to construct default bucket names and locate Manage application resources within the specified instance.

**Related variables**:
- `mas_instance_id`: Parent instance
- `custfiles_bucketname`: Uses workspace ID in default name
- `manage_workspace_cr_name`: Constructed from instance and workspace IDs

**Note**: This must match the workspace ID used during Manage installation.

### manage_workspace_cr_name
ManageWorkspace custom resource name.

- **Optional**
- Environment Variable: `MANAGE_WORKSPACE_CR_NAME`
- Default: `{mas_instance_id}-{mas_workspace_id}`

**Purpose**: Specifies the name of the ManageWorkspace custom resource to update with customer files storage configuration.

**When to use**:
- Use default unless you have a custom CR naming convention
- Override if your ManageWorkspace CR has a non-standard name
- Required to update storage configuration

**Valid values**: Valid Kubernetes resource name

**Impact**: Determines which ManageWorkspace CR is updated with customer files bucket configuration.

**Related variables**:
- `mas_instance_id`: Used in default name construction
- `mas_workspace_id`: Used in default name construction
- `cos_type`: Storage provider being configured

**Note**: The default naming convention `{instance}-{workspace}` matches standard Manage deployments. Only override if you have custom CR names.

## Example Playbook

### Configure COS for Existing Manage Instance
The following sample can be used to configure COS for an existing Manage application instance:

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_workspace_id: masdev
    cos_type: ibm
    cos_instance_name: cos-masinst1
    ibmcloud_apikey: xxxx
  roles:
    - ibm.mas_devops.suite_manage_customer_files_config
```

### Provision and Configure IBM Cloud COS
The following sample playbook can be used to provision COS in IBM Cloud and configure COS for an existing Manage application instance:

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_workspace_id: masdev
    cos_type: ibm
    cos_instance_name: cos-masinst1
    ibmcloud_apikey: xxxx
  roles:
    - ibm.mas_devops.cos
    - ibm.mas_devops.suite_manage_customer_files_config
```

### Configure AWS S3 Buckets
The following sample can be used to configure AWS S3 buckets for an existing Manage application instance:

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_workspace_id: masdev
    cos_type: aws
  roles:
    - ibm.mas_devops.suite_manage_customer_files_config
```

## License
EPL-2.0
