# suite_manage_attachments_config

This role configures storage for Maximo Manage application attachments, supporting multiple storage providers including IBM Cloud Object Storage, AWS S3, and persistent file storage. The role updates Manage configuration either through the ManageWorkspace custom resource or directly via database SQL updates.

!!! important "Prerequisites"
    This role must be executed **after** Manage application is deployed and activated. Manage must be up and running before configuring attachment features.

## Storage Provider Options

The role supports three storage providers:

- **filestorage** (default): Uses cluster's default file storage system (PVC)
- **ibm**: Uses IBM Cloud Object Storage buckets
- **aws**: Uses Amazon S3 buckets

For cloud storage providers (`ibm` or `aws`), the `cos_bucket` role is automatically executed to set up the bucket configuration.

## Role Variables

### mas_manage_attachments_provider
Storage provider type for Manage attachments.

- **Optional**
- Environment Variable: `MAS_MANAGE_ATTACHMENTS_PROVIDER`
- Default: `filestorage`

**Purpose**: Determines which storage backend is used to store Manage application attachments (documents, images, files).

**When to use**:
- Use default `filestorage` for simple deployments with PVC storage
- Use `ibm` when leveraging IBM Cloud Object Storage for scalability
- Use `aws` when using AWS S3 for cloud-native storage

**Valid values**: `filestorage`, `ibm`, `aws`

**Impact**:
- `filestorage`: Attachments stored in cluster file storage (PVC mount)
- `ibm`: Attachments stored in IBM Cloud Object Storage (requires COS credentials)
- `aws`: Attachments stored in AWS S3 (requires AWS credentials and CLI)

**Related variables**:
- `mas_manage_attachment_configuration_mode`: How configuration is applied
- `db2_instance_name`: Required for database configuration mode

**Note**: For `ibm` or `aws` providers, ensure you set COS/S3 credentials (`COS_APIKEY`, `COS_INSTANCE_NAME` for IBM, or `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` for AWS). AWS provider requires [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) to be installed.

### mas_manage_attachment_configuration_mode
Configuration method for attachment properties.

- **Optional**
- Environment Variable: `MAS_MANAGE_ATTACHMENT_CONFIGURATION_MODE`
- Default: `db`

**Purpose**: Determines how attachment configuration properties are applied to Manage - either through Kubernetes custom resource or direct database updates.

**When to use**:
- Use `db` (default) for direct database configuration (faster, simpler)
- Use `cr` for GitOps workflows or when database access is restricted

**Valid values**: `db`, `cr`

**Impact**:
- `db`: Updates attachment properties via SQL directly in Manage database (requires `db2_instance_name`, `db2_namespace`, `db2_dbname`)
- `cr`: Updates attachment properties in ManageWorkspace custom resource under `bundleProperties` (requires `manage_workspace_cr_name`)

**Related variables**:
- `db2_instance_name`: Required when mode is `db`
- `manage_workspace_cr_name`: Required when mode is `cr`

**Note**: The `db` mode is recommended for most deployments as it's more direct. Use `cr` mode for declarative/GitOps approaches.

### mas_instance_id
MAS instance identifier.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

**Purpose**: Identifies which MAS instance contains the Manage application to configure.

**When to use**:
- Always required for attachment configuration
- Must match the instance ID from MAS installation

**Valid values**: Lowercase alphanumeric string, 3-12 characters (e.g., `prod`, `dev`, `masinst1`)

**Impact**: Used to locate Manage application resources and construct resource names.

**Related variables**:
- `mas_workspace_id`: Workspace within this instance
- `manage_workspace_cr_name`: Constructed from instance and workspace IDs

**Note**: This must match the instance ID used during Manage installation.

### mas_workspace_id
Workspace identifier for Manage application.

- **Required**
- Environment Variable: `MAS_WORKSPACE_ID`
- Default: None

**Purpose**: Identifies which workspace within the MAS instance contains the Manage application to configure.

**When to use**:
- Always required for attachment configuration
- Must match the workspace ID where Manage is deployed

**Valid values**: Lowercase alphanumeric string, typically 3-12 characters (e.g., `prod`, `dev`, `masdev`)

**Impact**: Used to locate Manage application resources within the specified instance.

**Related variables**:
- `mas_instance_id`: Parent instance
- `manage_workspace_cr_name`: Constructed from instance and workspace IDs

**Note**: This must match the workspace ID used during Manage installation.

### manage_workspace_cr_name
ManageWorkspace custom resource name.

- **Optional** (Required when `mas_manage_attachment_configuration_mode=cr`)
- Environment Variable: `MANAGE_WORKSPACE_CR_NAME`
- Default: `{mas_instance_id}-{mas_workspace_id}`

**Purpose**: Specifies the name of the ManageWorkspace custom resource to update when using CR configuration mode.

**When to use**:
- Required only when `mas_manage_attachment_configuration_mode=cr`
- Use default unless you have a custom CR naming convention
- Override if your ManageWorkspace CR has a non-standard name

**Valid values**: Valid Kubernetes resource name

**Impact**: Determines which ManageWorkspace CR is updated with attachment properties in `bundleProperties` section.

**Related variables**:
- `mas_manage_attachment_configuration_mode`: Must be `cr` for this to be used
- `mas_instance_id`: Used in default name construction
- `mas_workspace_id`: Used in default name construction

**Note**: The default naming convention `{instance}-{workspace}` matches standard Manage deployments. Only override if you have custom CR names.

### db2_instance_name
Db2 Warehouse instance name.

- **Optional** (Required when `mas_manage_attachment_configuration_mode=db`)
- Environment Variable: `DB2_INSTANCE_NAME`
- Default: None

**Purpose**: Identifies the Db2 Warehouse instance that stores Manage application data for direct database configuration updates.

**When to use**:
- Required when `mas_manage_attachment_configuration_mode=db`
- Must match the Db2 instance name used by Manage
- Used to connect to database for SQL updates

**Valid values**: Valid Db2 instance name (e.g., `db2w-manage`, `db2u-iot`)

**Impact**: Determines which Db2 instance is accessed to update attachment configuration via SQL.

**Related variables**:
- `mas_manage_attachment_configuration_mode`: Must be `db` for this to be used
- `db2_namespace`: Namespace containing this instance
- `db2_dbname`: Database name within the instance

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
- Only relevant when `mas_manage_attachment_configuration_mode=db`

**Valid values**: Valid Kubernetes namespace name

**Impact**: Determines where to look for the Db2 instance when connecting for database updates.

**Related variables**:
- `db2_instance_name`: Instance to find in this namespace
- `mas_manage_attachment_configuration_mode`: Must be `db` for this to be relevant

**Note**: The default `db2u` namespace is used by most Db2 Warehouse deployments. Only change if you have a custom deployment.

### db2_dbname
Database name within Db2 instance.

- **Optional**
- Environment Variable: `DB2_DBNAME`
- Default: `BLUDB`

**Purpose**: Specifies the database name within the Db2 instance where Manage tables are stored.

**When to use**:
- Use default (`BLUDB`) for standard Manage deployments
- Override if Manage uses a custom database name
- Only relevant when `mas_manage_attachment_configuration_mode=db`

**Valid values**: Valid Db2 database name

**Impact**: Determines which database within the Db2 instance is updated with attachment configuration.

**Related variables**:
- `db2_instance_name`: Instance containing this database
- `mas_manage_attachment_configuration_mode`: Must be `db` for this to be relevant

**Note**: `BLUDB` is the default database name for Manage deployments. Only change if you have a custom database configuration.

## Example Playbook

### Configure COS via ManageWorkspace CR
The following sample can be used to configure COS for an existing Manage application instance's attachments via ManageWorkspace CR update (note `cr` as configuration mode + `mas_instance_id` and `mas_workspace_id`, which will be used to infer the CR name):

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_manage_attachment_configuration_mode: cr
    mas_instance_id: masinst1
    mas_workspace_id: masdev
    cos_instance_name: cos-masinst1
    cos_bucket_name: manage-attachments-bucket
    ibmcloud_apikey: xxxx
    mas_manage_attachments_provider: ibm
  roles:
    - ibm.mas_devops.suite_manage_attachments_config
```

### Provision COS and Configure via Database
The following sample playbook can be used to provision COS in IBM Cloud and configure COS for an existing Manage application instance's attachments via SQL updates in database (note `db` as configuration mode + `db2_instance_name`):

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_manage_attachment_configuration_mode: db
    mas_instance_id: masinst1
    mas_workspace_id: masdev
    db2_instance_name: db2w-manage
    cos_instance_name: cos-masinst1
    cos_bucket_name: manage-attachments-bucket
    ibmcloud_apikey: xxxx
    mas_manage_attachments_provider: ibm
  roles:
    - ibm.mas_devops.cos
    - ibm.mas_devops.suite_manage_attachments_config
```

### Configure File Storage for Attachments
The following sample playbook can be used to deploy Manage with default persistent storage for Manage attachments (PVC mount path `/DOCLINKS`), and configure Manage system properties with the corresponding attachments settings via SQL updates in database:

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_manage_attachment_configuration_mode: db
    mas_app_id: manage
    mas_app_channel: 8.4.x
    mas_instance_id: masinst1
    mas_workspace_id: masdev
    db2_instance_name: db2w-manage
    mas_app_settings_persistent_volumes_flag: true
    mas_manage_attachments_provider: filestorage
  roles:
    - ibm.mas_devops.db2
    - ibm.mas_devops.suite_db2_setup_for_manage
    - ibm.mas_devops.suite_config
    - ibm.mas_devops.suite_app_install
    - ibm.mas_devops.suite_app_config
    - ibm.mas_devops.suite_manage_attachments_config
```

### Configure AWS S3 Buckets
The following sample can be used to configure AWS S3 buckets for an existing Manage application instance's attachments:

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_workspace_id: masdev
    db2_instance_name: db2w-manage
    aws_bucket_name: manage-attachments-bucket
    mas_manage_attachments_provider: aws
  roles:
    - ibm.mas_devops.suite_manage_attachments_config
```

## License
EPL-2.0
