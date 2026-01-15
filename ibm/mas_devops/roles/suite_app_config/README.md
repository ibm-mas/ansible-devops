# suite_app_config

This role is used to configure specific components of the application workspace after the application has been installed in the Maximo Application Suite.

## Role Variables

### General Variables

#### mas_instance_id
MAS instance identifier for the target installation.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

**Purpose**: Identifies which MAS instance to configure. This must match the instance ID used during MAS Core installation.

**When to use**:
- Always required when configuring application workspaces
- Must match the instance ID from suite_install role
- Used to locate the correct Suite and Workspace resources

**Valid values**: Lowercase alphanumeric string, 3-12 characters (e.g., `prod`, `dev`, `inst1`)

**Impact**: Determines which MAS instance's application workspace will be configured. Incorrect instance ID will cause configuration to fail.

**Related variables**:
- `mas_app_id`: Specifies which application to configure
- `mas_workspace_id`: Specifies which workspace to configure

**Note**: This must be an existing MAS instance. The role does not create new instances.

#### mas_app_id
MAS application to configure.

- **Required**
- Environment Variable: `MAS_APP_ID`
- Default: None

**Purpose**: Specifies which MAS application workspace to configure. Different applications have different configuration options and requirements.

**When to use**:
- Always required when configuring application workspaces
- Must match an installed application in the MAS instance
- Determines which application-specific configuration is applied

**Valid values**: `assist`, `iot`, `facilities`, `manage`, `monitor`, `optimizer`, `predict`, `visualinspection`

**Impact**: Determines which application workspace is configured and which configuration options are available. Each application has unique configuration requirements.

**Related variables**:
- `mas_instance_id`: The MAS instance containing this application
- `mas_workspace_id`: The workspace to configure
- `mas_appws_components`: Application-specific components to configure

**Note**: The application must already be installed via suite_app_install role before configuration. Different applications support different configuration variables.

#### mas_workspace_id
Workspace identifier for the application workspace to configure.

- **Required**
- Environment Variable: `MAS_WORKSPACE_ID`
- Default: None

**Purpose**: Identifies which workspace within the application to configure. Workspaces allow multiple isolated environments within a single application.

**When to use**:
- Always required when configuring application workspaces
- Must match an existing workspace created during application installation
- Typically matches the workspace ID used in suite_app_install

**Valid values**: Lowercase alphanumeric string (e.g., `masdev`, `prod`, `test`)

**Impact**: Determines which workspace is configured. Each workspace has its own configuration, data, and users.

**Related variables**:
- `mas_instance_id`: The MAS instance containing this workspace
- `mas_app_id`: The application containing this workspace
- `mas_appws_components`: Components to configure in this workspace

**Note**: The workspace must already exist (created during suite_app_install). This role configures existing workspaces, it does not create new ones.

#### aiservice_instance_id
AI Service instance ID for Manage integration (Manage only).

- **Optional**
- Environment Variable: `AISERVICE_INSTANCE_ID`
- Default: None

**Purpose**: Enables automatic AI Service integration with Manage application. When set, the role retrieves credentials, configures connection, and imports certificates.

**When to use**:
- Only when configuring Manage application (`mas_app_id=manage`)
- When you want to integrate AI Service capabilities into Manage
- Requires AI Service to be installed and running in the cluster
- Must be used together with `aiservice_tenant_id`

**Valid values**: Valid AI Service instance ID (e.g., `aiservice1`, `ai-prod`)

**Impact**: When configured, automatically:
- Retrieves API key from tenant-specific secret
- Extracts AI Service URL from aibroker route
- Imports AI Service TLS certificate into Manage
- Configures AI Service connection properties
- Verifies AI Service health before proceeding

**Related variables**:
- `aiservice_tenant_id`: Required tenant ID for the integration
- `mas_app_id`: Must be `manage` for this to apply

**Note**: AI Service must be installed and healthy before configuration. The role performs automatic health checks and credential retrieval from cluster resources.

#### aiservice_tenant_id
AI Service tenant ID for the integration (Manage only).

- **Optional**
- Environment Variable: `AISERVICE_TENANT_ID`
- Default: None

**Purpose**: Specifies which AI Service tenant to use for Manage integration. Combined with instance ID to form the fully qualified tenant identifier.

**When to use**:
- Required when `aiservice_instance_id` is set
- Only applies to Manage application
- Must match an existing tenant in the AI Service instance

**Valid values**: Valid AI Service tenant ID string (e.g., `tenant1`, `prod-tenant`)

**Impact**: Combined with `aiservice_instance_id` to locate tenant-specific resources (API key secret, configuration). Incorrect tenant ID will cause integration to fail.

**Related variables**:
- `aiservice_instance_id`: Required instance ID for the integration
- Forms secret name: `aiservice-{instance_id}-{tenant_id}----apikey-secret`

**Note**: The tenant must already exist in the AI Service instance. The role retrieves credentials from the tenant-specific secret in the cluster.

#### custom_labels
Comma-separated list of key=value labels to apply to workspace resources.

- **Optional**
- Environment Variable: `CUSTOM_LABELS`
- Default: None

**Purpose**: Adds Kubernetes labels to application workspace resources for organization, selection, and filtering. Labels enable resource tracking, cost allocation, and custom automation.

**When to use**:
- Use to add organizational metadata (e.g., `cost-center=engineering`, `environment=production`)
- Use to enable resource tracking and cost allocation
- Use to support custom automation or monitoring tools
- Use to comply with organizational labeling standards

**Valid values**: Comma-separated list of `key=value` pairs (e.g., `env=prod,team=platform,app=manage`)

**Impact**: Labels are applied to workspace-specific resources and can be used for filtering with `oc get` commands, monitoring queries, and automation scripts. Labels do not affect workspace functionality.

**Related variables**: Works alongside Kubernetes resource labels for comprehensive resource management.

**Note**: Labels help with resource organization and are especially useful in multi-tenant or multi-workspace environments.

### Workspace Configuration Variables

#### mas_appws_spec
Custom workspace deployment specification (overrides component-based configuration).

- **Optional**
- Environment Variable: `MAS_APPWS_SPEC`
- Default: Application-specific defaults in `vars/defaultspecs/{mas_app_id}.yml`

**Purpose**: Provides complete control over workspace deployment specification. Allows advanced customization beyond what component-based configuration offers.

**When to use**:
- Use for advanced workspace customization
- Use when you need full control over the workspace spec
- Use when component-based configuration is insufficient
- Leave unset for standard deployments using `mas_appws_components`

**Valid values**: Valid workspace specification YAML/JSON matching the application's workspace CR schema

**Impact**: **WARNING** - Overrides all settings from `mas_appws_components`. Provides complete control but requires deep knowledge of workspace CR structure. Incorrect specs can cause deployment failures.

**Related variables**:
- `mas_appws_components`: Simpler component-based configuration (overridden by this)
- Application-specific default specs in `vars/defaultspecs/`

**Note**: Use `mas_appws_components` for standard deployments. Only use this variable when you need advanced customization or have specific requirements not covered by component-based configuration.

#### mas_appws_bindings_jdbc
JDBC binding scope for the workspace.

- **Optional**
- Environment Variable: `MAS_APPWS_BINDINGS_JDBC`
- Default: `system`

**Purpose**: Controls the scope of JDBC database binding for the workspace. Different scopes provide different levels of isolation and sharing.

**When to use**:
- Use `system` (default) for shared system-level database configuration
- Use `application` for application-level database configuration
- Use `workspace` for workspace-specific database configuration
- Use `workspace-application` for Maximo Real Estate and Facilities (recommended)

**Valid values**: `system`, `application`, `workspace`, `workspace-application`

**Impact**: 
- `system`: Uses system-level JDBC configuration (shared across all workspaces)
- `application`: Uses application-level JDBC configuration
- `workspace`: Uses workspace-specific JDBC configuration
- `workspace-application`: Combines workspace and application scopes

**Related variables**: JDBC configuration must exist at the specified scope level.

**Note**: **IMPORTANT** - For Maximo Real Estate and Facilities applications, use `workspace-application` scope. The default `system` scope is suitable for most other applications.

#### mas_appws_components
Application components and versions to configure in the workspace.

- **Optional**
- Environment Variable: `MAS_APPWS_COMPONENTS`
- Default: Application-specific defaults

**Purpose**: Specifies which application components to configure and their versions. Different applications have different available components.

**When to use**:
- Use to enable specific application components
- Use to control component versions
- Leave unset to use application-specific defaults
- Overridden by `mas_appws_spec` if that is set

**Valid values**: Comma-separated `component=version` pairs (e.g., `base=latest,health=latest`, `base=latest,civil=latest`)

**Impact**: Determines which components are configured in the workspace. Available components vary by application (e.g., Manage has base, health, civil, etc.).

**Related variables**:
- `mas_appws_spec`: Overrides this if set
- `mas_app_id`: Determines available components

**Note**: Component availability depends on the application. For Manage: `base`, `health`, `civil`, etc. Refer to application documentation for available components. Use `latest` for most recent version or specify exact version.

#### mas_pod_templates_dir
Directory containing pod template configuration files (Manage only).

- **Optional**
- Environment Variable: `MAS_POD_TEMPLATES_DIR`
- Default: None

**Purpose**: Specifies a directory containing pod template YAML files for customizing Manage workspace and component workloads. Enables resource requests/limits, node selectors, tolerations, and other pod-level customizations.

**When to use**:
- Only for Manage application (`mas_app_id=manage`)
- Use to customize pod resources (CPU, memory)
- Use to apply node selectors or tolerations
- Use to configure pod-level settings beyond defaults

**Valid values**: Absolute path to directory containing pod template files

**Impact**: Pod templates from this directory are merged into the ManageWorkspace CR. Files are applied to specific components or the workspace itself based on filename.

**Related variables**:
- `mas_app_id`: Must be `manage` for this to apply
- Files must follow specific naming convention

**Note**: Expected filenames:
- `ibm-mas-manage-manageworkspace.yml` → workspace-level pod templates
- `ibm-mas-manage-imagestitching.yml` → civil component pod templates
- `ibm-mas-manage-slackproxy.yml` → component pod templates
- `ibm-mas-manage-healthextworkspace.yml` → health component pod templates

Refer to [MAS CLI BestEfforts templates](https://github.com/ibm-mas/cli/blob/master/image/cli/mascli/templates/pod-templates/best-effort/) and [Customizing Pod Templates](https://www.ibm.com/docs/en/mas-cd/continuous-delivery?topic=configuring-customizing-workloads) documentation.

### Predict Configuration Variables

#### mas_appws_settings_deployment_size
Workload size for Predict containers (Predict only).

- **Optional** (Predict only)
- Environment Variable: `MAS_APPWS_SETTINGS_DEPLOYMENT_SIZE`
- Default: `small`

**Purpose**: Controls the deployment size and replica count for Predict application containers. Different sizes provide different levels of availability and performance.

**When to use**:
- Only for Predict application (`mas_app_id=predict`)
- Use `developer` for single-node development environments
- Use `small` (default) for standard production deployments
- Use `medium` for higher availability requirements
- Use `large` for maximum availability (if supported)

**Valid values**: `developer`, `small`, `medium`, `large`

**Impact**: 
- `developer`: 1 replica (no high availability)
- `small`: 2 replicas (basic high availability)
- `medium`: 3 replicas (enhanced high availability)
- `large`: Higher replica count (if supported)

**Related variables**:
- `mas_app_id`: Must be `predict` for this to apply

**Note**: The `developer` size is suitable only for development/testing. Production environments should use `small` or larger for high availability.

### Watson Studio Local Variables

These variables are only used when using this role to configure **Predict**, or **Health & Predict Utilities**.

#### cpd_wsl_project_id
Watson Studio analytics project ID (Predict/HP Utilities only).

- **Required** (unless `cpd_wsl_project_name` and `mas_config_dir` are set)
- Environment Variable: `CPD_WSL_PROJECT_ID`
- Default: None

**Purpose**: Specifies the ID of the Watson Studio analytics project to use for Predict or Health & Predict Utilities configuration.

**When to use**:
- Required for Predict or HP Utilities configuration
- Use when you know the project ID directly
- Alternative: use `cpd_wsl_project_name` + `mas_config_dir` to retrieve ID from saved file

**Valid values**: Valid Watson Studio project ID (UUID format)

**Impact**: Links the MAS application to the specified Watson Studio project for analytics capabilities. Incorrect project ID will cause configuration to fail.

**Related variables**:
- `cpd_wsl_project_name`: Alternative method using project name
- `mas_config_dir`: Required with `cpd_wsl_project_name`

**Note**: The project must already exist in Watson Studio (created by cp4d_service role). Either provide this ID directly or use the name-based alternative.

#### cpd_wsl_project_name
Filename containing Watson Studio project ID (Predict/HP Utilities only).

- **Optional**
- Environment Variable: `CPD_WSL_PROJECT_NAME`
- Default: `wsl-mas-${mas_instance_id}-hputilities`

**Purpose**: Specifies the filename in `mas_config_dir` where the Watson Studio project ID is saved. Alternative to providing `cpd_wsl_project_id` directly.

**When to use**:
- Use with `mas_config_dir` as alternative to `cpd_wsl_project_id`
- Use when project ID was saved by cp4d_service role
- Allows retrieving project ID from saved configuration

**Valid values**: Filename (without path) where project ID is stored

**Impact**: Role reads the project ID from this file in `mas_config_dir`. File must exist and contain valid project ID.

**Related variables**:
- `mas_config_dir`: Required directory containing this file
- `cpd_wsl_project_id`: Alternative direct ID specification

**Note**: The default filename matches the pattern used by cp4d_service role. The file should contain the Watson Studio project ID created during CP4D service setup.

#### mas_config_dir
Local directory for configuration files (Predict/HP Utilities only).

- **Optional**
- Environment Variable: `MAS_CONFIG_DIR`
- Default: None

**Purpose**: Specifies directory containing configuration files, particularly Watson Studio project ID files. Used with `cpd_wsl_project_name` to retrieve project IDs.

**When to use**:
- Use with `cpd_wsl_project_name` to retrieve Watson Studio project ID
- Use when project ID was saved by cp4d_service role
- Should match the directory used in cp4d_service role

**Valid values**: Absolute path to existing directory (e.g., `/home/user/masconfig`, `~/masconfig`)

**Impact**: Role reads Watson Studio project ID from files in this directory. Directory must exist and contain the specified project file.

**Related variables**:
- `cpd_wsl_project_name`: Filename to read from this directory
- `cpd_wsl_project_id`: Alternative direct ID specification

**Note**: Use the same directory across all MAS setup roles for consistency. The cp4d_service role saves project IDs here, and this role retrieves them.

### Watson Machine Learning Variables

These variables are only used when using this role to configure **Predict**.

#### cpd_product_version
Cloud Pak for Data version (Predict only).

- **Required** (Predict only)
- Environment Variable: `CPD_PRODUCT_VERSION`
- Default: None

**Purpose**: Specifies the CP4D version to infer the correct Watson Machine Learning version for Predict workspace configuration.

**When to use**:
- Required when configuring Predict application
- Must match the installed CP4D version in the cluster
- Used to determine compatible WML version

**Valid values**: Valid CP4D version string (e.g., `4.8.0`, `4.8.5`, `5.0.0`)

**Impact**: Determines which Watson Machine Learning version is configured in Predict. Incorrect version may cause compatibility issues.

**Related variables**:
- `cpd_wml_instance_id`: WML instance to configure
- `cpd_wml_url`: WML service URL
- `mas_app_id`: Must be `predict` for this to apply

**Note**: This must match the actual CP4D version installed in your cluster. The role uses this to select the appropriate WML version for Predict configuration.

#### cpd_wml_instance_id
Watson Machine Learning instance identifier (Predict only).

- **Optional** (Predict only)
- Environment Variable: `CPD_WML_INSTANCE_ID`
- Default: `openshift`

**Purpose**: Specifies the Watson Machine Learning instance identifier to configure in Predict workspace.

**When to use**:
- Only for Predict application configuration
- Use default (`openshift`) for standard deployments
- Set custom value if using non-default WML instance

**Valid values**: Valid WML instance identifier string

**Impact**: Identifies which WML instance Predict will use for machine learning operations. Must match an existing WML instance in CP4D.

**Related variables**:
- `cpd_product_version`: CP4D version for WML compatibility
- `cpd_wml_url`: WML service URL
- `mas_app_id`: Must be `predict` for this to apply

**Note**: The default `openshift` value is suitable for most deployments. Only change if you have a specific WML instance identifier.

#### cpd_wml_url
Watson Machine Learning service URL (Predict only).

- **Optional** (Predict only)
- Environment Variable: `CPD_WML_URL`
- Default: `https://internal-nginx-svc.ibm-cpd.svc:12443`

**Purpose**: Specifies the URL to access Watson Machine Learning service. Typically the same as the Cloud Pak for Data URL.

**When to use**:
- Only for Predict application configuration
- Use default if CP4D is in `ibm-cpd` namespace
- Set custom URL if CP4D is in different namespace or uses custom service name

**Valid values**: Valid HTTPS URL to WML service (e.g., `https://internal-nginx-svc.{namespace}.svc:12443`)

**Impact**: Determines how Predict connects to Watson Machine Learning. Incorrect URL will prevent Predict from accessing WML services.

**Related variables**:
- `cpd_product_version`: CP4D version
- `cpd_wml_instance_id`: WML instance identifier
- `mas_app_id`: Must be `predict` for this to apply

**Note**: The default assumes CP4D is installed in the `ibm-cpd` namespace. If CP4D is in a different namespace, update the URL accordingly (e.g., `https://internal-nginx-svc.my-cpd-namespace.svc:12443`).

### Manage Workspace Variables

### AI Service Integration

#### aiservice_instance_id
AI Service instance ID to integrate with Manage application.

- **Optional**
- Environment Variable: `AISERVICE_INSTANCE_ID`
- Default: None

When configured, the role will:
- Retrieve AI Service API key from the tenant-specific secret
- Extract AI Service URL from the aibroker route
- Import AI Service TLS certificate into Manage
- Configure AI Service connection properties in Manage encryption secret
- Verify AI Service health status before proceeding

#### aiservice_tenant_id
AI Service tenant ID to use for the integration. This is combined with the instance ID to form the fully qualified tenant name.

- **Required** when `aiservice_instance_id` is set
- Environment Variable: `AISERVICE_TENANT_ID`
- Default: None

**Note:** The AI Service integration automatically retrieves the following from the cluster:
- API key from secret: `aiservice-{instance_id}-{tenant_id}----apikey-secret`
- Service URL from route: `aibroker` in namespace `aiservice-{instance_id}`
- TLS certificate from secret: `{instance_id}-public-aibroker-tls`

The integration also performs a health check to verify AI Service is running before completing the configuration.

### Health Integration

#### mas_appws_bindings_health_wsl_flag
Enable Watson Studio binding for Health (Manage only).

- **Optional** (Manage Health only)
- Environment Variable: `MAS_APPWS_BINDINGS_HEALTH_WSL_FLAG`
- Default: `false`

**Purpose**: Controls whether Watson Studio should be bound to the Manage Health component. Requires a system-level WatsonStudioCfg to be applied in the cluster.

**When to use**:
- Only for Manage application with Health component
- Set to `true` to enable Watson Studio integration with Health
- Leave as `false` (default) if Watson Studio integration is not needed

**Valid values**: `true`, `false`

**Impact**: When `true`, binds Watson Studio to Health component, enabling advanced analytics capabilities. Requires Watson Studio to be configured at system level.

**Related variables**:
- `mas_appws_bindings_health_wsl`: Binding scope (typically `system`)
- `mas_app_id`: Must be `manage` with Health component

**Note**: A system-level WatsonStudioCfg must exist in the cluster before enabling this. Watson Studio must be installed and configured via CP4D.

#### mas_appws_bindings_health_wsl
Watson Studio binding scope for Health (Manage only).

- **Optional** (Manage Health only)
- Environment Variable: `MAS_APPWS_BINDINGS_HEALTH_WSL`
- Default: None

**Purpose**: Specifies the binding scope for Watson Studio integration with Manage Health component.

**When to use**:
- Only for Manage application with Health component
- Set to `system` when Watson Studio is configured at system level
- Used together with `mas_appws_bindings_health_wsl_flag=true`

**Valid values**: `system`

**Impact**: Binds Watson Studio at the specified scope to Health component, enabling advanced analytics and AI capabilities.

**Related variables**:
- `mas_appws_bindings_health_wsl_flag`: Must be `true` to enable binding
- `mas_app_id`: Must be `manage` with Health component

**Note**: Watson Studio must be installed and configured via CP4D with a system-level WatsonStudioCfg before using this binding.
- Environment Variable: `MAS_APPWS_BINDINGS_HEALTH_WSL`
- Default: None

#### mas_app_settings_aio_flag
Flag indicating if Asset Investment Optimization (AIO) resource must be loaded or not. It can be loaded only when Optimizer application is installed.

- **Optional**, only supported when Optimizer application is installed
- Environment Variable: `MAS_APP_SETTINGS_AIO_FLAG`
- Default: `true`

### DB2 Settings

#### mas_app_settings_db_schema
Name of the schema where Manage database lives in. Code also supports deprecated `mas_app_settings_db2_schema` variable name.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_DB_SCHEMA`
- Default: `maximo`

#### mas_app_settings_demodata
Flag indicating if manage demodata should be loaded or not.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_DEMODATA`
- Default: `false` (do not load demodata)

#### mas_app_settings_db2vargraphic
Flag indicating if VARGRAPHIC (if true) or VARCHAR (if false) is used. Details: https://www.ibm.com/docs/en/mas-cd/continuous-delivery?topic=deploy-language-support

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_DB2VARGRAPHIC`
- Default: `true`

#### mas_app_settings_tablespace
Name of the Manage database tablespace.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_TABLESPACE`
- Default: `MAXDATA`

#### mas_app_settings_indexspace
Name of the Manage database indexspace.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_INDEXSPACE`
- Default: `MAXINDEX`

### Persistent Volumes

#### mas_app_settings_persistent_volumes_flag
Flag indicating if persistent volumes should be configured by default during Manage Workspace activation. There are two defaulted File Storage Persistent Volumes Claim resources that will be created out of the box for Manage if this flag is set to `true`:

- `/DOCLINKS`: Persistent volume used to store doclinks/attachments
- `/bim`: Persistent volume used to store Building Information Models related artifacts (models, docs and import)

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_PERSISTENT_VOLUMES_FLAG`
- Default: `false`

### JMS Queues

The following properties can be defined to customize the persistent volumes for the JMS queues setup for Manage.

#### mas_app_settings_jms_queue_pvc_storage_class
Provide the persistent volume storage class to be used for JMS queue configuration. Both `ReadWriteOnce` (if using a block storage class) or `ReadWriteMany` (if using file storage class) access modes are supported. **Note:** JMS configuration will only be done if `mas_app_settings_server_bundles_size` property is set to `jms`.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_JMS_QUEUE_PVC_STORAGE_CLASS`
- Default: None - If not set, a default storage class will be auto defined accordingly to your cluster's available storage classes

#### mas_app_settings_jms_queue_pvc_name
Provide the persistent volume claim name to be used for JMS queue configuration. **Note:** JMS configuration will only be done if `mas_app_settings_server_bundles_size` property is set to `jms`.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_JMS_QUEUE_PVC_NAME`
- Default: `manage-jms`

#### mas_app_settings_jms_queue_pvc_size
Provide the persistent volume claim size to be used for JMS queue configuration. **Note:** JMS configuration will only be done if `mas_app_settings_server_bundles_size` property is set to `jms`.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_JMS_QUEUE_PVC_SIZE`
- Default: `20Gi`

#### mas_app_settings_jms_queue_mount_path
Provide the persistent volume storage mount path to be used for JMS queue configuration. **Note:** JMS configuration will only be done if `mas_app_settings_server_bundles_size` property is set to `jms`.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_JMS_QUEUE_MOUNT_PATH`
- Default: `/jms`

#### mas_app_settings_jms_queue_pvc_accessmode
Provide the persistent volume storage access-mode to be used for JMS queue configuration. Typically you would either choose between `ReadWriteOnce` (if using a block storage class) or `ReadWriteMany` (if using file storage class).

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_JMS_QUEUE_PVC_ACCESSMODE`
- Default: `ReadWriteMany`

#### mas_app_settings_default_jms
Set this to `true` if you want to have JMS continuous queues configured.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_DEFAULT_JMS`
- Default: `false`

### Doclinks/Attachments

The following properties can be defined to customize the persistent volumes for the Doclinks/Attachments setup for Manage.

#### mas_app_settings_doclinks_pvc_storage_class
Provide the persistent volume storage class to be used for doclinks/attachments configuration. Both `ReadWriteOnce` (if using a block storage class) or `ReadWriteMany` (if using file storage class) are supported.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_DOCLINKS_PVC_STORAGE_CLASS`
- Default: None - If not set, a default storage class will be auto defined accordingly to your cluster's available storage classes

#### mas_app_settings_doclinks_pvc_name
Provide the persistent volume claim name to be used for doclinks/attachments configuration.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_DOCLINKS_PVC_NAME`
- Default: `manage-doclinks`

#### mas_app_settings_doclinks_pvc_size
Provide the persistent volume claim size to be used for doclinks/attachments configuration.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_DOCLINKS_PVC_SIZE`
- Default: `20Gi`

#### mas_app_settings_doclinks_mount_path
Provide the persistent volume storage mount path to be used for doclinks/attachments configuration.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_DOCLINKS_MOUNT_PATH`
- Default: `/DOCLINKS`

#### mas_app_settings_doclinks_pvc_accessmode
Provide the persistent volume storage access-mode to be used for doclinks/attachments configuration. Typically you would either choose between `ReadWriteOnce` (if using a block storage class) or `ReadWriteMany` (if using file storage class).

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_DOCLINKS_PVC_ACCESSMODE`
- Default: `ReadWriteMany`

### BIM (Building Information Models)

The following properties can be defined to customize the persistent volumes for the Building Information Models setup for Manage.

#### mas_app_settings_bim_pvc_storage_class
Provide the persistent volume storage class to be used for Building Information Models configuration. Both `ReadWriteOnce` (if using a block storage class) or `ReadWriteMany` (if using file storage class) are supported.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_BIM_PVC_STORAGE_CLASS`
- Default: None - If not set, a default storage class will be auto defined accordingly to your cluster's available storage classes

#### mas_app_settings_bim_pvc_name
Provide the persistent volume claim name to be used for Building Information Models configuration.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_BIM_PVC_NAME`
- Default: `manage-bim`

#### mas_app_settings_bim_pvc_size
Provide the persistent volume claim size to be used for Building Information Models configuration.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_BIM_PVC_SIZE`
- Default: `20Gi`

#### mas_app_settings_bim_mount_path
Provide the persistent volume storage mount path to be used for Building Information Models configuration.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_BIM_MOUNT_PATH`
- Default: `/bim`

#### mas_app_settings_bim_pvc_accessmode
Provide the persistent volume storage access-mode to be used for Building Information Models configuration. Typically you would either choose between `ReadWriteOnce` (if using a block storage class) or `ReadWriteMany` (if using file storage class).

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_BIM_PVC_ACCESSMODE`
- Default: `ReadWriteMany`

### Supported Languages

#### mas_app_settings_base_lang
Provide the base language for Manage application. For a full list of supported languages for Manage application and its corresponding language codes, please refer to [Language Support](https://www.ibm.com/docs/en/maximo-manage/continuous-delivery?topic=deploy-language-support) documentation.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_BASE_LANG`
- Default: `EN` (English)

#### mas_app_settings_secondary_langs
Provide a list of additional secondary languages for Manage application.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_SECONDARY_LANGS`
- Default: None

Note: The more languages you add, the longer Manage will take to install and activate.

Export the `MAS_APP_SETTINGS_SECONDARY_LANGS` variable with the language codes as comma-separated values. For a full list of supported languages for Manage application and its corresponding language codes, please refer to [Language Support](https://www.ibm.com/docs/en/maximo-manage/continuous-delivery?topic=deploy-language-support) documentation.

For example, use the following to enable Manage application with Arabic, Deutsch and Japanese as secondary languages:
`export MAS_APP_SETTINGS_SECONDARY_LANGS='AR,DE,JA'`

### Server Bundle Configuration

#### mas_app_settings_server_bundles_size
Provides different flavors of server bundle configuration to handle workload for Manage application.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_SERVER_BUNDLES_SIZE`
- Default: `dev`

For more details about Manage application server bundle configuration, refer to [Setting the server bundles for Manage application](https://www.ibm.com/docs/en/maximo-manage/continuous-delivery?topic=manage-setting-server-bundles).

Currently supported server bundle sizes are:
- `dev` - Deploys Manage with the default server bundle configuration (i.e just 1 bundle pod handling `all` Manage application workload)
- `small` - Deploys Manage with the most common deployment configuration (i.e 4 bundle pods, each one handling workload for each main capabilities: `mea`, `cron`, `report` and `ui`)
- `jms` - Can be used for Manage 8.4 and above. Same server bundle configuration as `small` and includes `jms` bundle pod. Enabling JMS pod workload will also configure Manage to use default JMS messaging queues to be stored in `/{{ mas_app_settings_jms_queue_mount_path }}/jmsstore` persistent volume mount path
- `snojms` - Can be used for Manage 8.4 and above. Includes `all` and `jms` bundle pods. Enabling JMS pod workload will also configure Manage to use default JMS messaging queues to be stored in `/{{ mas_app_settings_jms_queue_mount_path }}/jmsstore` persistent volume mount path

### Customization Archive Settings

#### mas_app_settings_customization_archive_url
Provide a custom archive/file path to be included as part of Manage deployment.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_CUSTOMIZATION_ARCHIVE_URL`
- Default: None

#### mas_app_settings_customization_archive_name
Provide a custom archive file name to be associated with the archive/file path provided. Only used when `mas_app_settings_customization_archive_url` is defined.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_CUSTOMIZATION_ARCHIVE_NAME`
- Default: `manage-custom-archive`

### Database Encryption and AI Service Secrets

**Note:** The encryption secret stores both database encryption keys and AI Service integration properties when `aiservice_instance_id` is configured. The secret will contain:
- Database encryption keys: `MXE_SECURITY_CRYPTO_KEY`, `MXE_SECURITY_CRYPTOX_KEY`, `MXE_SECURITY_OLD_CRYPTO_KEY`, `MXE_SECURITY_OLD_CRYPTOX_KEY`
- AI Service connection details: `mxe.int.aibrokerapikey`, `mxe.int.aibrokerapiurl`, `mxe.int.aibrokertenantid`

#### mas_manage_encryptionsecret_crypto_key
This defines the `MXE_SECURITY_CRYPTO_KEY` value if you want to customize your Manage database encryption keys. For more details, refer to [Manage database encryption](https://www.ibm.com/docs/en/mas-cd/continuous-delivery?topic=encryption-database-scenarios) documentation.

- **Optional**
- Environment Variable: `MAS_MANAGE_ENCRYPTIONSECRET_CRYPTO_KEY`
- Default: Auto-generated

#### mas_manage_encryptionsecret_cryptox_key
This defines the `MXE_SECURITY_CRYPTOX_KEY` value if you want to customize your Manage database encryption keys. For more details, refer to [Manage database encryption](https://www.ibm.com/docs/en/mas-cd/continuous-delivery?topic=encryption-database-scenarios) documentation.

- **Required** if `mas_manage_encryptionsecret_crypto_key` is set
- Environment Variable: `MAS_MANAGE_ENCRYPTIONSECRET_CRYPTOX_KEY`
- Default: Auto-generated

#### mas_manage_encryptionsecret_old_crypto_key
This defines the `MXE_SECURITY_OLD_CRYPTO_KEY` value if you want to customize your Manage database encryption keys. For more details, refer to [Manage database encryption](https://www.ibm.com/docs/en/mas-cd/continuous-delivery?topic=encryption-database-scenarios) documentation.

- **Optional**
- Environment Variable: `MAS_MANAGE_ENCRYPTIONSECRET_OLD_CRYPTO_KEY`
- Default: None

#### mas_manage_encryptionsecret_old_cryptox_key
This defines the `MXE_SECURITY_OLD_CRYPTOX_KEY` value if you want to customize your Manage database encryption keys. For more details, refer to [Manage database encryption](https://www.ibm.com/docs/en/mas-cd/continuous-delivery?topic=encryption-database-scenarios) documentation.

- **Required** if `mas_manage_encryptionsecret_old_crypto_key` is set
- Environment Variable: `MAS_MANAGE_ENCRYPTIONSECRET_OLD_CRYPTOX_KEY`
- Default: None

#### mas_manage_encryptionsecret_aiservice_apikey
The AI Service API key to configure in the encryption secret. When set along with the URL and FQN, the role will add these properties to the encryption secret.

- **Optional**
- Environment Variable: `MAS_MANAGE_ENCRYPTIONSECRET_AISERVICE_APIKEY`
- Default: Auto-retrieved from AI Service tenant secret when `aiservice_instance_id` is configured

#### mas_manage_encryptionsecret_aiservice_url
The AI Service broker URL to configure in the encryption secret.

- **Required** if `mas_manage_encryptionsecret_aiservice_apikey` is set
- Environment Variable: `MAS_MANAGE_ENCRYPTIONSECRET_AISERVICE_URL`
- Default: Auto-retrieved from AI Service route when `aiservice_instance_id` is configured

#### mas_manage_encryptionsecret_aiservice_fqn
The fully qualified AI Service tenant name (format: `{instance_id}.{tenant_id}`) to configure in the encryption secret.

- **Required** if `mas_manage_encryptionsecret_aiservice_apikey` is set
- Environment Variable: `MAS_MANAGE_ENCRYPTIONSECRET_AISERVICE_FQN`
- Default: Auto-generated from `aiservice_instance_id` and `aiservice_tenant_id` when configured

### Server Timezone Setting

#### mas_app_settings_server_timezone
Sets the Manage server timezone. If you also want to have the Manage's DB2 database aligned with the same timezone, you must set `DB2_TIMEZONE` while provisioning the corresponding DB2 instance using `db2` role.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_SERVER_TIMEZONE`
- Default: `GMT`

### Facilities Workspace Variables

#### mas_ws_facilities_size
Sets the size of deployment.

- **Optional**
- Environment Variable: `MAS_FACILITIES_SIZE`
- Default: `small` Available options are `small`, `medium` and `large`

#### mas_ws_facilities_pull_policy
Sets the `imagePullPolicy` strategy for all deployments. The default is set to `IfNotPresent` to reduce the pulling operations in the cluster.

- **Optional**
- Environment Variable: `MAS_FACILITIES_PULL_POLICY`
- Default: `IfNotPresent`

#### mas_ws_facilities_liberty_extension_xml_secret_name
Provide the secret name of the secret which contains additional XML tags that needs to be added into the existing Liberty Server XML to configure the application accordingly.

**NOTE:** The Secret name MUST be `<workspaceId>-facilities-lexml--sn`

- **Optional**
- Environment Variable: `MAS_FACILITIES_LIBERTY_EXTENSION_XML_SECRET_NAME`
- Default: None

Sample Secret Template:

```bash
cat <<EOF | oc create -f -
kind: Secret
apiVersion: v1
metadata:
  name: <MAS_FACILITIES_LIBERTY_EXTENSION_XML_SECRET_NAME>
  namespace: mas-<instanceId>-facilities
data:
  extensions.xml: <!-- Custom XML tags -->
type: Opaque
EOF
```

#### mas_ws_facilities_vault_secret_name
Provide the name of the secret which contains a password to the vault with AES Encryption key. By default, this secret will be generated automatically.

**NOTE:** The Secret name MUST be `<workspaceId>-facilities-vs--sn`

- **Optional**
- Environment Variable: `MAS_FACILITIES_VAULT_SECRET_NAME`
- Default: None

Sample Secret Template:

```bash
cat <<EOF | oc create -f -
kind: Secret
apiVersion: v1
metadata:
  name: <MAS_FACILITIES_VAULT_SECRET_NAME>
  namespace: mas-<instanceId>-facilities
data:
  pwd: <your password>
type: Opaque
EOF
```

#### mas_ws_facilities_dwfagents
Allows the user to add dedicated workflow agents (DWFA) to MREF. To specify a DWFA it's required to specify a JSON with a unique `name` and `members`. Each member has a unique `name` and `class` that can be classified as `user` or `group`. Below an example of the structure of the JSON:

```bash
export MAS_FACILITIES_DWFAGENTS='[{"name":"dwfa1","members":[{"name": "u1", "class": "user"}]}, {"name":"dwfa2","members":[{"name": "u2", "class": "user"},{"name":"g1", "class":"group"}]}]'
```

- **Optional**
- Environment Variable: `MAS_FACILITIES_DWFAGENTS`
- Default: `[]`

### Facilities Database Settings

#### mas_ws_facilities_db_maxconnpoolsize
Sets the maximum connection pool size for database.

- **Optional**
- Environment Variable: `MAS_FACILITIES_DB_MAX_POOLSIZE`
- Default: `200`

### Facilities Routes Settings

#### mas_ws_facilities_db_timout
Sets the timeout of the application. It is a string with the structure `<timeout_value><time_unit>`, where `timeout_value` is any non zero unsigned integer number and the supported `time_unit` are microseconds (us), milliseconds (ms), seconds (s), minutes (m), hours (h), or days (d).

- **Optional**
- Environment Variable: `MAS_FACILITIES_ROUTES_TIMEOUT`
- Default: `600s`

### Facilities Storage Settings

#### mas_ws_facilities_storage_log_class
Sets the storage class name for the Log Persistent Volume Claim used for MREF agents.

- **Optional**
- Environment Variable: `MAS_FACILITIES_STORAGE_LOG_CLASS`
- Default: None - If not set, a default storage class will be auto defined accordingly to your cluster's available storage classes

#### mas_ws_facilities_storage_log_mode
Sets the attach mode of the Log PVC. Both `ReadWriteOnce` (if using a block storage class) or `ReadWriteMany` (if using file storage class) are supported.

- **Optional**
- Environment Variable: `MAS_FACILITIES_STORAGE_LOG_MODE`
- Default: `ReadWriteOnce`

#### mas_ws_facilities_storage_log_size
Sets the size of the Log PVC. Defaults to 30 Gigabytes.

- **Optional**
- Environment Variable: `MAS_FACILITIES_STORAGE_LOG_SIZE`
- Default: `30`

#### mas_ws_facilities_storage_userfiles_class
Sets the storage class name for the Userfiles PVC used for MREF agents.

- **Optional**
- Environment Variable: `MAS_FACILITIES_STORAGE_USERFILES_CLASS`
- Default: None - If not set, a default storage class will be auto defined accordingly to your cluster's available storage classes

#### mas_ws_facilities_storage_userfiles_mode
Sets the attach mode of the Userfiles PVC. Both `ReadWriteOnce` (if using a block storage class) or `ReadWriteMany` (if using file storage class) are supported.

- **Optional**
- Environment Variable: `MAS_FACILITIES_STORAGE_USERFILES_MODE`
- Default: `ReadWriteOnce`

#### mas_ws_facilities_storage_userfiles_size
Sets the size of the Log PVC. Defaults to 50 Gigabytes.

- **Optional**
- Environment Variable: `MAS_FACILITIES_STORAGE_USERFILES_SIZE`
- Default: `50`

## Example Playbook

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    # MAS configuration
    mas_instance_id: "{{ lookup('env', 'MAS_INSTANCE_ID') }}"

    # MAS workspace configuration
    mas_workspace_id: "{{ lookup('env', 'MAS_WORKSPACE_ID') }}"

    # MAS application configuration
    mas_app_id: "{{ lookup('env', 'MAS_APP_ID') }}"

    mas_appws_spec:
      bindings:
        jdbc: "{{ mas_appws_jdbc_binding | default( 'system' , true) }}"

  roles:
    - ibm.mas_devops.suite_app_config
```

## License

EPL-2.0
