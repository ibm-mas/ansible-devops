# suite_app_config

This role is used to configure specific components of the application workspace after the application has been installed in the Maximo Application Suite.

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`mas_instance_id`](#mas_instance_id) | Yes | None |
| [`mas_app_id`](#mas_app_id) | Yes | None |
| [`mas_workspace_id`](#mas_workspace_id) | Yes | None |
| [`custom_labels`](#custom_labels) | No | None |
| [`mas_appws_spec`](#mas_appws_spec) | No | Application-specific defaults |
| [`mas_appws_bindings_jdbc`](#mas_appws_bindings_jdbc) | No | `system` |
| [`mas_appws_components`](#mas_appws_components) | No | Application-specific defaults |
| [`mas_pod_templates_dir`](#mas_pod_templates_dir) | No | None |
| [`mas_appws_settings_deployment_size`](#mas_appws_settings_deployment_size) | No | `small` |
| [`cpd_wsl_project_id`](#cpd_wsl_project_id) | Conditional | None |
| [`cpd_wsl_project_name`](#cpd_wsl_project_name) | No | `wsl-mas-${mas_instance_id}-hputilities` |
| [`mas_config_dir`](#mas_config_dir) | No | None |
| [`cpd_product_version`](#cpd_product_version) | Conditional | None |
| [`cpd_wml_instance_id`](#cpd_wml_instance_id) | No | `openshift` |
| [`cpd_wml_url`](#cpd_wml_url) | No | `https://internal-nginx-svc.ibm-cpd.svc:12443` |
| [`aiservice_instance_id`](#aiservice_instance_id) | No | None |
| [`aiservice_tenant_id`](#aiservice_tenant_id) | Conditional | None |
| [`mas_appws_bindings_health_wsl_flag`](#mas_appws_bindings_health_wsl_flag) | No | `false` |
| [`mas_appws_bindings_health_wsl`](#mas_appws_bindings_health_wsl) | No | None |
| [`mas_app_settings_aio_flag`](#mas_app_settings_aio_flag) | No | `true` |
| [`mas_app_settings_db_schema`](#mas_app_settings_db_schema) | No | `maximo` |
| [`mas_app_settings_demodata`](#mas_app_settings_demodata) | No | `false` |
| [`mas_app_settings_db2vargraphic`](#mas_app_settings_db2vargraphic) | No | `true` |
| [`mas_app_settings_tablespace`](#mas_app_settings_tablespace) | No | `MAXDATA` |
| [`mas_app_settings_indexspace`](#mas_app_settings_indexspace) | No | `MAXINDEX` |
| [`mas_app_settings_persistent_volumes_flag`](#mas_app_settings_persistent_volumes_flag) | No | `false` |
| [`mas_app_settings_jms_queue_pvc_storage_class`](#mas_app_settings_jms_queue_pvc_storage_class) | No | Auto-detected |
| [`mas_app_settings_jms_queue_pvc_name`](#mas_app_settings_jms_queue_pvc_name) | No | `manage-jms` |
| [`mas_app_settings_jms_queue_pvc_size`](#mas_app_settings_jms_queue_pvc_size) | No | `20Gi` |
| [`mas_app_settings_jms_queue_mount_path`](#mas_app_settings_jms_queue_mount_path) | No | `/jms` |
| [`mas_app_settings_jms_queue_pvc_accessmode`](#mas_app_settings_jms_queue_pvc_accessmode) | No | `ReadWriteMany` |
| [`mas_app_settings_default_jms`](#mas_app_settings_default_jms) | No | `false` |
| [`mas_app_settings_doclinks_pvc_storage_class`](#mas_app_settings_doclinks_pvc_storage_class) | No | Auto-detected |
| [`mas_app_settings_doclinks_pvc_name`](#mas_app_settings_doclinks_pvc_name) | No | `manage-doclinks` |
| [`mas_app_settings_doclinks_pvc_size`](#mas_app_settings_doclinks_pvc_size) | No | `20Gi` |
| [`mas_app_settings_doclinks_mount_path`](#mas_app_settings_doclinks_mount_path) | No | `/DOCLINKS` |
| [`mas_app_settings_doclinks_pvc_accessmode`](#mas_app_settings_doclinks_pvc_accessmode) | No | `ReadWriteMany` |
| [`mas_manage_kafkaimageprocessor_pvc_storageclass`](#mas_manage_kafkaimageprocessor_pvc_storageclass) | No | Auto-detected |
| [`mas_manage_kafkaimageprocessor_pvc_size`](#mas_manage_kafkaimageprocessor_pvc_size) | No | `10Gi` |
| [`mas_app_settings_bim_pvc_storage_class`](#mas_app_settings_bim_pvc_storage_class) | No | Auto-detected |
| [`mas_app_settings_bim_pvc_name`](#mas_app_settings_bim_pvc_name) | No | `manage-bim` |
| [`mas_app_settings_bim_pvc_size`](#mas_app_settings_bim_pvc_size) | No | `20Gi` |
| [`mas_app_settings_bim_mount_path`](#mas_app_settings_bim_mount_path) | No | `/bim` |
| [`mas_app_settings_bim_pvc_accessmode`](#mas_app_settings_bim_pvc_accessmode) | No | `ReadWriteMany` |
| [`mas_app_settings_base_lang`](#mas_app_settings_base_lang) | No | `EN` |
| [`mas_app_settings_secondary_langs`](#mas_app_settings_secondary_langs) | No | None |
| [`mas_app_settings_server_bundles_size`](#mas_app_settings_server_bundles_size) | No | `dev` |
| [`mas_app_settings_customization_archive_url`](#mas_app_settings_customization_archive_url) | No | None |
| [`mas_app_settings_customization_archive_name`](#mas_app_settings_customization_archive_name) | No | `manage-custom-archive` |
| [`mas_manage_encryptionsecret_crypto_key`](#mas_manage_encryptionsecret_crypto_key) | No | Auto-generated |
| [`mas_manage_encryptionsecret_cryptox_key`](#mas_manage_encryptionsecret_cryptox_key) | Conditional | Auto-generated |
| [`mas_manage_encryptionsecret_old_crypto_key`](#mas_manage_encryptionsecret_old_crypto_key) | No | None |
| [`mas_manage_encryptionsecret_old_cryptox_key`](#mas_manage_encryptionsecret_old_cryptox_key) | Conditional | None |
| [`mas_manage_encryptionsecret_aiservice_apikey`](#mas_manage_encryptionsecret_aiservice_apikey) | No | Auto-retrieved |
| [`mas_manage_encryptionsecret_aiservice_url`](#mas_manage_encryptionsecret_aiservice_url) | Conditional | Auto-retrieved |
| [`mas_manage_encryptionsecret_aiservice_fqn`](#mas_manage_encryptionsecret_aiservice_fqn) | Conditional | Auto-generated |
| [`mas_app_settings_server_timezone`](#mas_app_settings_server_timezone) | No | `GMT` |
| [`mas_ws_facilities_size`](#mas_ws_facilities_size) | No | `small` |
| [`mas_ws_facilities_app_om_upgrade_mode`](#mas_ws_facilities_app_om_upgrade_mode) | No | `manual` |
| [`mas_ws_facilities_pull_policy`](#mas_ws_facilities_pull_policy) | No | `IfNotPresent` |
| [`mas_ws_facilities_liberty_extension_XML`](#mas_ws_facilities_liberty_extension_xml) | No | None |
| [`mas_ws_facilities_server_timezone`](#mas_ws_facilities_server_timezone) | No | `UTC` |
| [`mas_ws_facilities_vault_secret`](#mas_ws_facilities_vault_secret) | No | None |
| [`mas_ws_facilities_dwfagents`](#mas_ws_facilities_dwfagents) | No | `[]` |
| [`mas_ws_facilities_custom_properties`](#mas_ws_facilities_custom_properties) | No | `false` |
| [`mas_ws_facilities_properties_file_local`](#mas_ws_facilities_properties_file_local) | No | None |
| [`mas_ws_facilities_properties_secret_name`](#mas_ws_facilities_properties_secret_name) | No | `custom-facilities-properties` |
| [`mas_ws_facilities_db_maxconnpoolsize`](#mas_ws_facilities_db_maxconnpoolsize) | No | `200` |
| [`mas_ws_facilities_routes_timeout`](#mas_ws_facilities_routes_timeout) | No | `600s` |
| [`mas_ws_facilities_storage_log_class`](#mas_ws_facilities_storage_log_class) | No | Auto-detected |
| [`mas_ws_facilities_storage_log_mode`](#mas_ws_facilities_storage_log_mode) | No | `ReadWriteOnce` |
| [`mas_ws_facilities_storage_log_size`](#mas_ws_facilities_storage_log_size) | No | `30` |
| [`mas_ws_facilities_storage_userfiles_class`](#mas_ws_facilities_storage_userfiles_class) | No | Auto-detected |
| [`mas_ws_facilities_storage_userfiles_mode`](#mas_ws_facilities_storage_userfiles_mode) | No | `ReadWriteOnce` |
| [`mas_ws_facilities_storage_userfiles_size`](#mas_ws_facilities_storage_userfiles_size) | No | `50` |
| [`mas_ws_facilities_dataconnectagent_deploymentmode`](#mas_ws_facilities_dataconnectagent_deploymentmode) | No | `''` |
| [`mas_ws_facilities_extendedformulaagent_deploymentmode`](#mas_ws_facilities_extendedformulaagent_deploymentmode) | No | `''` |
| [`mas_ws_facilities_formularecalcagent_deploymentmode`](#mas_ws_facilities_formularecalcagent_deploymentmode) | No | `''` |
| [`mas_ws_facilities_incomingmailagent_deploymentmode`](#mas_ws_facilities_incomingmailagent_deploymentmode) | No | `''` |
| [`mas_ws_facilities_objectmigrationagent_deploymentmode`](#mas_ws_facilities_objectmigrationagent_deploymentmode) | No | `''` |
| [`mas_ws_facilities_objectpublishagent_deploymentmode`](#mas_ws_facilities_objectpublishagent_deploymentmode) | No | `''` |
| [`mas_ws_facilities_maintenanceagent_deploymentmode`](#mas_ws_facilities_maintenanceagent_deploymentmode) | No | `''` |
| [`mas_ws_facilities_reportqueueagent_deploymentmode`](#mas_ws_facilities_reportqueueagent_deploymentmode) | No | `''` |
| [`mas_ws_facilities_wfagent_deploymentmode`](#mas_ws_facilities_wfagent_deploymentmode) | No | `''` |
| [`mas_ws_facilities_wffutureagent_deploymentmode`](#mas_ws_facilities_wffutureagent_deploymentmode) | No | `''` |
| [`mas_ws_facilities_wfnotificationagent_deploymentmode`](#mas_ws_facilities_wfnotificationagent_deploymentmode) | No | `''` |
| [`mas_ws_facilities_reservesmtpagent_deploymentmode`](#mas_ws_facilities_reservesmtpagent_deploymentmode) | No | `''` |
| [`mas_ws_facilities_scheduleragent_deploymentmode`](#mas_ws_facilities_scheduleragent_deploymentmode) | No | `''` |

Variables marked as Conditional are only required in specific circumstances: `aiservice_tenant_id` and the AI Service encryption secret properties apply when AI Service integration is enabled, `cpd_wsl_project_id` and `cpd_product_version` apply to Predict / Health & Predict Utilities configuration, and the `cryptox_key` properties apply when the corresponding crypto key is set.

### Instance and Workspace Variables

#### mas_instance_id

MAS instance identifier for the target installation — a lowercase alphanumeric string of 3-12 characters (e.g. `prod`, `dev`, `inst1`).

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

Must match the instance ID used during MAS Core installation (suite_install role). The role uses it to locate the correct Suite and Workspace resources; it must be an existing instance — this role does not create new instances.

#### mas_app_id

MAS application whose workspace to configure — one of `assist`, `iot`, `facilities`, `manage`, `monitor`, `optimizer`, `predict`, `visualinspection`.

- **Required**
- Environment Variable: `MAS_APP_ID`
- Default: None

The application must already be installed via the suite_app_install role. Each application supports a different set of configuration variables.

#### mas_workspace_id

Identifier of the workspace within the application to configure — a lowercase alphanumeric string (e.g. `masdev`, `prod`, `test`).

- **Required**
- Environment Variable: `MAS_WORKSPACE_ID`
- Default: None

Must match a workspace created during application installation, typically the workspace ID used in suite_app_install. This role configures existing workspaces — it does not create new ones.

#### custom_labels

Comma-separated list of `key=value` labels to apply to workspace resources (e.g. `env=prod,team=platform,app=manage`).

- **Optional**
- Environment Variable: `CUSTOM_LABELS`
- Default: None

Labels are useful for resource organization, tracking, cost allocation, and custom automation — especially in multi-tenant or multi-workspace environments. They can be used for filtering with `oc get` commands and monitoring queries, and do not affect workspace functionality.

### Workspace Configuration Variables

#### mas_appws_spec

Custom workspace deployment specification, overriding the component-based configuration. Must be valid YAML/JSON matching the application's workspace CR schema.

- **Optional**
- Environment Variable: `MAS_APPWS_SPEC`
- Default: Application-specific defaults in `vars/defaultspecs/{mas_app_id}.yml`

!!! warning
    Setting `mas_appws_spec` overrides **all** settings from `mas_appws_components`. It provides complete control over the workspace spec but requires deep knowledge of the workspace CR structure — incorrect specs can cause deployment failures.

Use `mas_appws_components` for standard deployments; only use this variable when you need advanced customization beyond what component-based configuration offers.

#### mas_appws_bindings_jdbc

JDBC binding scope for the workspace — `system` (shared system-level database configuration), `application`, `workspace`, or `workspace-application` (combines workspace and application scopes).

- **Optional**
- Environment Variable: `MAS_APPWS_BINDINGS_JDBC`
- Default: `system`

!!! important
    For Maximo Real Estate and Facilities applications, use the `workspace-application` scope. The default `system` scope is suitable for most other applications.

JDBC configuration must exist at the specified scope level.

#### mas_appws_components

Application components and versions to configure in the workspace, as comma-separated `component=version` pairs (e.g. `base=latest,health=latest`).

- **Optional**
- Environment Variable: `MAS_APPWS_COMPONENTS`
- Default: Application-specific defaults

Available components depend on the application (e.g. Manage supports `base`, `health`, `civil`, etc.); use `latest` for the most recent version or specify an exact version. Overridden by `mas_appws_spec` when that is set.

#### mas_pod_templates_dir

Directory containing pod template YAML files for customizing Manage workspace and component workloads (Manage only) — enabling resource requests/limits, node selectors, tolerations, and other pod-level settings.

- **Optional**
- Environment Variable: `MAS_POD_TEMPLATES_DIR`
- Default: None

Pod templates from this directory are merged into the ManageWorkspace CR and applied to specific components or the workspace itself based on filename:

- `ibm-mas-manage-manageworkspace.yml` — workspace-level pod templates
- `ibm-mas-manage-imagestitching.yml` — civil component pod templates
- `ibm-mas-manage-slackproxy.yml` — component pod templates
- `ibm-mas-manage-healthextworkspace.yml` — health component pod templates

Refer to the [MAS CLI BestEfforts templates](https://github.com/ibm-mas/cli/blob/master/image/cli/mascli/templates/pod-templates/best-effort/) and [Customizing Pod Templates](https://www.ibm.com/docs/en/mas-cd/continuous-delivery?topic=configuring-customizing-workloads) documentation.

### Predict Configuration Variables

#### mas_appws_settings_deployment_size

Workload size for Predict containers — `developer` (1 replica, no high availability), `small` (2 replicas, basic high availability), `medium` (3 replicas), or `large` (higher replica count, if supported).

- **Optional** (Predict only)
- Environment Variable: `MAS_APPWS_SETTINGS_DEPLOYMENT_SIZE`
- Default: `small`

The `developer` size is suitable only for development and testing; production environments should use `small` or larger for high availability.

### Watson Studio Local Variables

These variables are only used when using this role to configure **Predict**, or **Health & Predict Utilities**.

#### cpd_wsl_project_id

Watson Studio analytics project ID to use for Predict or Health & Predict Utilities configuration, in UUID format.

- **Required** unless `cpd_wsl_project_name` and `mas_config_dir` are set
- Environment Variable: `CPD_WSL_PROJECT_ID`
- Default: None

The project must already exist in Watson Studio (created by the cp4d_service role). Either provide this ID directly, or use the name-based alternative (`cpd_wsl_project_name` + `mas_config_dir`).

#### cpd_wsl_project_name

Filename (without path) in `mas_config_dir` where the Watson Studio project ID is saved, as an alternative to providing `cpd_wsl_project_id` directly.

- **Optional**
- Environment Variable: `CPD_WSL_PROJECT_NAME`
- Default: `wsl-mas-${mas_instance_id}-hputilities`

The default filename matches the pattern used by the cp4d_service role. The file must exist in `mas_config_dir` and contain a valid project ID.

#### mas_config_dir

Local directory containing configuration files, particularly the Watson Studio project ID files (e.g. `/home/user/masconfig`).

- **Optional**
- Environment Variable: `MAS_CONFIG_DIR`
- Default: None

Use the same directory across all MAS setup roles for consistency — the cp4d_service role saves project IDs here, and this role retrieves them.

### Watson Machine Learning Variables

These variables are only used when using this role to configure **Predict**.

#### cpd_product_version

Cloud Pak for Data version (e.g. `4.8.0`, `4.8.5`, `5.0.0`) used to infer the correct Watson Machine Learning version for the Predict workspace configuration.

- **Required** (Predict only)
- Environment Variable: `CPD_PRODUCT_VERSION`
- Default: None

Must match the CP4D version actually installed in the cluster; an incorrect version may cause WML compatibility issues.

#### cpd_wml_instance_id

Watson Machine Learning instance identifier to configure in the Predict workspace.

- **Optional** (Predict only)
- Environment Variable: `CPD_WML_INSTANCE_ID`
- Default: `openshift`

The default suits most deployments; a custom value must match an existing WML instance in CP4D.

#### cpd_wml_url

Watson Machine Learning service URL — typically the same as the Cloud Pak for Data URL (e.g. `https://internal-nginx-svc.{namespace}.svc:12443`).

- **Optional** (Predict only)
- Environment Variable: `CPD_WML_URL`
- Default: `https://internal-nginx-svc.ibm-cpd.svc:12443`

The default assumes CP4D is installed in the `ibm-cpd` namespace; if CP4D is in a different namespace, update the URL accordingly (e.g. `https://internal-nginx-svc.my-cpd-namespace.svc:12443`).

### AI Service Integration

These variables configure the AI Service integration with the **Manage** application.

#### aiservice_instance_id

AI Service instance ID to integrate with the Manage application (e.g. `aiservice1`, `ai-prod`).

- **Optional**
- Environment Variable: `AISERVICE_INSTANCE_ID`
- Default: None

Must be used together with `aiservice_tenant_id`. When set, the role automatically retrieves the API key from the tenant-specific secret `aiservice-{instance_id}-{tenant_id}----apikey-secret`, extracts the service URL from the `aibroker` route in namespace `aiservice-{instance_id}`, imports the TLS certificate from secret `{instance_id}-public-aibroker-tls`, configures the connection properties in the Manage encryption secret, and verifies AI Service health before proceeding.

#### aiservice_tenant_id

AI Service tenant ID to use for the integration (e.g. `tenant1`, `prod-tenant`), combined with the instance ID to form the fully qualified tenant name.

- **Required** when `aiservice_instance_id` is set
- Environment Variable: `AISERVICE_TENANT_ID`
- Default: None

The tenant must already exist in the AI Service instance; the role retrieves credentials from the tenant-specific secret in the cluster.

### Health Integration

#### mas_appws_bindings_health_wsl_flag

Whether to bind Watson Studio to the Manage Health component — `true` or `false`.

- **Optional** (Manage Health only)
- Environment Variable: `MAS_APPWS_BINDINGS_HEALTH_WSL_FLAG`
- Default: `false`

Setting this to `true` enables Watson Studio integration with Health, providing advanced analytics capabilities. A system-level WatsonStudioCfg must exist in the cluster before enabling this (Watson Studio installed and configured via CP4D). Used together with `mas_appws_bindings_health_wsl`.

#### mas_appws_bindings_health_wsl

Watson Studio binding scope for the Manage Health component — set to `system` when Watson Studio is configured at system level.

- **Optional** (Manage Health only)
- Environment Variable: `MAS_APPWS_BINDINGS_HEALTH_WSL`
- Default: None

Used together with `mas_appws_bindings_health_wsl_flag=true`; Watson Studio must be installed and configured via CP4D with a system-level WatsonStudioCfg before using this binding.

### Manage Application Settings

#### mas_app_settings_aio_flag

Whether the Asset Investment Optimization (AIO) resource must be loaded into Manage — only supported when the Optimizer application is installed.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_AIO_FLAG`
- Default: `true`

### DB2 Settings

#### mas_app_settings_db_schema

Name of the schema where the Manage database lives; the deprecated `mas_app_settings_db2_schema` variable name is also supported.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_DB_SCHEMA`
- Default: `maximo`

#### mas_app_settings_demodata

Whether Manage demo data should be loaded.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_DEMODATA`
- Default: `false` (do not load demodata)

#### mas_app_settings_db2vargraphic

Whether VARGRAPHIC (`true`) or VARCHAR (`false`) is used — see [Language Support](https://www.ibm.com/docs/en/mas-cd/continuous-delivery?topic=deploy-language-support) for details.

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

Whether persistent volumes are configured by default during Manage Workspace activation.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_PERSISTENT_VOLUMES_FLAG`
- Default: `false`

When set to `true`, two defaulted file storage Persistent Volume Claim resources are created out of the box for Manage:

- `/DOCLINKS` — persistent volume used to store doclinks/attachments
- `/bim` — persistent volume used to store Building Information Models related artifacts (models, docs and import)

### JMS Queues

The following properties can be defined to customize the persistent volume for the JMS queues setup for Manage. JMS configuration is only performed when `mas_app_settings_server_bundles_size` is set to `jms` or `snojms`.

#### mas_app_settings_jms_queue_pvc_storage_class

Persistent volume storage class for the JMS queue configuration. Both `ReadWriteOnce` (block storage class) and `ReadWriteMany` (file storage class) access modes are supported.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_JMS_QUEUE_PVC_STORAGE_CLASS`
- Default: None — a default storage class is auto-defined according to your cluster's available storage classes

#### mas_app_settings_jms_queue_pvc_name

Persistent volume claim name for the JMS queue configuration.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_JMS_QUEUE_PVC_NAME`
- Default: `manage-jms`

#### mas_app_settings_jms_queue_pvc_size

Persistent volume claim size for the JMS queue configuration.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_JMS_QUEUE_PVC_SIZE`
- Default: `20Gi`

#### mas_app_settings_jms_queue_mount_path

Persistent volume storage mount path for the JMS queue configuration.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_JMS_QUEUE_MOUNT_PATH`
- Default: `/jms`

#### mas_app_settings_jms_queue_pvc_accessmode

Persistent volume storage access mode for the JMS queue configuration — typically `ReadWriteOnce` (block storage class) or `ReadWriteMany` (file storage class).

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_JMS_QUEUE_PVC_ACCESSMODE`
- Default: `ReadWriteMany`

#### mas_app_settings_default_jms

Whether JMS continuous queues are configured.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_DEFAULT_JMS`
- Default: `false`

### Doclinks/Attachments

The following properties can be defined to customize the persistent volumes for the Doclinks/Attachments setup for Manage.

#### mas_app_settings_doclinks_pvc_storage_class

Persistent volume storage class for the doclinks/attachments configuration. Both `ReadWriteOnce` (block storage class) and `ReadWriteMany` (file storage class) are supported.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_DOCLINKS_PVC_STORAGE_CLASS`
- Default: None — a default storage class is auto-defined according to your cluster's available storage classes

#### mas_app_settings_doclinks_pvc_name

Persistent volume claim name for the doclinks/attachments configuration.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_DOCLINKS_PVC_NAME`
- Default: `manage-doclinks`

#### mas_app_settings_doclinks_pvc_size

Persistent volume claim size for the doclinks/attachments configuration.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_DOCLINKS_PVC_SIZE`
- Default: `20Gi`

#### mas_app_settings_doclinks_mount_path

Persistent volume storage mount path for the doclinks/attachments configuration.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_DOCLINKS_MOUNT_PATH`
- Default: `/DOCLINKS`

#### mas_app_settings_doclinks_pvc_accessmode

Persistent volume storage access mode for the doclinks/attachments configuration — typically `ReadWriteOnce` (block storage class) or `ReadWriteMany` (file storage class).

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_DOCLINKS_PVC_ACCESSMODE`
- Default: `ReadWriteMany`

### Kafka Image Processor (Civil Component)

The following properties configure the persistent volume for the Kafka Image Processor component when the Civil Infrastructure component is enabled.

!!! important
    As of Manage 9.2, these properties are **required** when the Civil Infrastructure component is enabled. They are not supported in earlier releases. The role automatically detects the Manage version and only includes these settings when Manage >= 9.2.

#### mas_manage_kafkaimageprocessor_pvc_storageclass

Persistent volume storage class for the Kafka Image Processor configuration. The PVC is created with `ReadWriteMany` access mode, as it must be shared between the Manage/Civil and KafkaImageProcessor deployments.

- **Optional** (automatically included when the Civil component is enabled in Manage 9.2+)
- Environment Variable: `MAS_MANAGE_KAFKAIMAGEPROCESSOR_PVC_STORAGECLASS`
- Default: None — a default storage class is auto-defined according to your cluster's available storage classes

#### mas_manage_kafkaimageprocessor_pvc_size

Persistent volume claim size for the Kafka Image Processor configuration.

- **Optional** (automatically included when the Civil component is enabled in Manage 9.2+)
- Environment Variable: `MAS_MANAGE_KAFKAIMAGEPROCESSOR_PVC_SIZE`
- Default: `10Gi`

### BIM (Building Information Models)

The following properties can be defined to customize the persistent volumes for the Building Information Models setup for Manage.

#### mas_app_settings_bim_pvc_storage_class

Persistent volume storage class for the Building Information Models configuration. Both `ReadWriteOnce` (block storage class) and `ReadWriteMany` (file storage class) are supported.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_BIM_PVC_STORAGE_CLASS`
- Default: None — a default storage class is auto-defined according to your cluster's available storage classes

#### mas_app_settings_bim_pvc_name

Persistent volume claim name for the Building Information Models configuration.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_BIM_PVC_NAME`
- Default: `manage-bim`

#### mas_app_settings_bim_pvc_size

Persistent volume claim size for the Building Information Models configuration.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_BIM_PVC_SIZE`
- Default: `20Gi`

#### mas_app_settings_bim_mount_path

Persistent volume storage mount path for the Building Information Models configuration.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_BIM_MOUNT_PATH`
- Default: `/bim`

#### mas_app_settings_bim_pvc_accessmode

Persistent volume storage access mode for the Building Information Models configuration — typically `ReadWriteOnce` (block storage class) or `ReadWriteMany` (file storage class).

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_BIM_PVC_ACCESSMODE`
- Default: `ReadWriteMany`

### Supported Languages

#### mas_app_settings_base_lang

Base language for the Manage application. For a full list of supported languages and their corresponding language codes, refer to the [Language Support](https://www.ibm.com/docs/en/maximo-manage/continuous-delivery?topic=deploy-language-support) documentation.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_BASE_LANG`
- Default: `EN` (English)

#### mas_app_settings_secondary_langs

Additional secondary languages for the Manage application, as comma-separated language codes.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_SECONDARY_LANGS`
- Default: None

For example, use the following to enable the Manage application with Arabic, Deutsch, and Japanese as secondary languages:

```bash
export MAS_APP_SETTINGS_SECONDARY_LANGS='AR,DE,JA'
```

The more languages you add, the longer Manage will take to install and activate. For a full list of supported languages and their corresponding language codes, refer to the [Language Support](https://www.ibm.com/docs/en/maximo-manage/continuous-delivery?topic=deploy-language-support) documentation.

### Server Bundle Configuration

#### mas_app_settings_server_bundles_size

Flavor of server bundle configuration used to handle workload for the Manage application.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_SERVER_BUNDLES_SIZE`
- Default: `dev`

Currently supported server bundle sizes:

- `dev` — deploys Manage with the default server bundle configuration (a single bundle pod handling `all` Manage application workload)
- `small` — deploys Manage with the most common deployment configuration (4 bundle pods, each handling workload for one main capability: `mea`, `cron`, `report`, and `ui`)
- `jms` — Manage 8.4 and above; same server bundle configuration as `small` plus a `jms` bundle pod. Enabling the JMS pod workload also configures Manage to use default JMS messaging queues stored in the `{{ mas_app_settings_jms_queue_mount_path }}/jmsstore` persistent volume mount path
- `snojms` — Manage 8.4 and above; includes `all` and `jms` bundle pods. Enabling the JMS pod workload also configures Manage to use default JMS messaging queues stored in the `{{ mas_app_settings_jms_queue_mount_path }}/jmsstore` persistent volume mount path

For more details about the Manage application server bundle configuration, refer to [Setting the server bundles for Manage application](https://www.ibm.com/docs/en/maximo-manage/continuous-delivery?topic=manage-setting-server-bundles).

### Customization Archive Settings

#### mas_app_settings_customization_archive_url

Custom archive/file path to be included as part of the Manage deployment.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_CUSTOMIZATION_ARCHIVE_URL`
- Default: None

#### mas_app_settings_customization_archive_name

Custom archive file name to associate with the archive/file path provided; only used when `mas_app_settings_customization_archive_url` is defined.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_CUSTOMIZATION_ARCHIVE_NAME`
- Default: `manage-custom-archive`

### Database Encryption and AI Service Secrets

The encryption secret stores both database encryption keys and AI Service integration properties when `aiservice_instance_id` is configured. The secret contains:

- Database encryption keys: `MXE_SECURITY_CRYPTO_KEY`, `MXE_SECURITY_CRYPTOX_KEY`, `MXE_SECURITY_OLD_CRYPTO_KEY`, `MXE_SECURITY_OLD_CRYPTOX_KEY`
- AI Service connection details: `mxe.int.aibrokerapikey`, `mxe.int.aibrokerapiurl`, `mxe.int.aibrokertenantid`

#### mas_manage_encryptionsecret_crypto_key

Custom value for the `MXE_SECURITY_CRYPTO_KEY` Manage database encryption key. For more details, refer to the [Manage database encryption](https://www.ibm.com/docs/en/mas-cd/continuous-delivery?topic=encryption-database-scenarios) documentation.

- **Optional**
- Environment Variable: `MAS_MANAGE_ENCRYPTIONSECRET_CRYPTO_KEY`
- Default: Auto-generated

#### mas_manage_encryptionsecret_cryptox_key

Custom value for the `MXE_SECURITY_CRYPTOX_KEY` Manage database encryption key. For more details, refer to the [Manage database encryption](https://www.ibm.com/docs/en/mas-cd/continuous-delivery?topic=encryption-database-scenarios) documentation.

- **Required** if `mas_manage_encryptionsecret_crypto_key` is set
- Environment Variable: `MAS_MANAGE_ENCRYPTIONSECRET_CRYPTOX_KEY`
- Default: Auto-generated

#### mas_manage_encryptionsecret_old_crypto_key

Custom value for the `MXE_SECURITY_OLD_CRYPTO_KEY` Manage database encryption key. For more details, refer to the [Manage database encryption](https://www.ibm.com/docs/en/mas-cd/continuous-delivery?topic=encryption-database-scenarios) documentation.

- **Optional**
- Environment Variable: `MAS_MANAGE_ENCRYPTIONSECRET_OLD_CRYPTO_KEY`
- Default: None

#### mas_manage_encryptionsecret_old_cryptox_key

Custom value for the `MXE_SECURITY_OLD_CRYPTOX_KEY` Manage database encryption key. For more details, refer to the [Manage database encryption](https://www.ibm.com/docs/en/mas-cd/continuous-delivery?topic=encryption-database-scenarios) documentation.

- **Required** if `mas_manage_encryptionsecret_old_crypto_key` is set
- Environment Variable: `MAS_MANAGE_ENCRYPTIONSECRET_OLD_CRYPTOX_KEY`
- Default: None

#### mas_manage_encryptionsecret_aiservice_apikey

AI Service API key to configure in the encryption secret. When set along with the URL and FQN, the role adds these properties to the encryption secret.

- **Optional**
- Environment Variable: `MAS_MANAGE_ENCRYPTIONSECRET_AISERVICE_APIKEY`
- Default: Auto-retrieved from the AI Service tenant secret when `aiservice_instance_id` is configured

#### mas_manage_encryptionsecret_aiservice_url

AI Service broker URL to configure in the encryption secret.

- **Required** if `mas_manage_encryptionsecret_aiservice_apikey` is set
- Environment Variable: `MAS_MANAGE_ENCRYPTIONSECRET_AISERVICE_URL`
- Default: Auto-retrieved from the AI Service route when `aiservice_instance_id` is configured

#### mas_manage_encryptionsecret_aiservice_fqn

Fully qualified AI Service tenant name (format: `{instance_id}.{tenant_id}`) to configure in the encryption secret.

- **Required** if `mas_manage_encryptionsecret_aiservice_apikey` is set
- Environment Variable: `MAS_MANAGE_ENCRYPTIONSECRET_AISERVICE_FQN`
- Default: Auto-generated from `aiservice_instance_id` and `aiservice_tenant_id` when configured

### Server Timezone Setting

#### mas_app_settings_server_timezone

Timezone for the Manage server.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_SERVER_TIMEZONE`
- Default: `GMT`

If you also want the Manage DB2 database aligned with the same timezone, you must set `DB2_TIMEZONE` while provisioning the corresponding DB2 instance using the `db2` role.

### Facilities Workspace Variables

#### mas_ws_facilities_size

Size of the Facilities deployment — `small`, `medium`, or `large`.

- **Optional**
- Environment Variable: `MAS_FACILITIES_SIZE`
- Default: `small`

#### mas_ws_facilities_app_om_upgrade_mode

Application Object Migration mode — `manual`, `load-only`, or `automatic`.

- **Optional**
- Environment Variable: `MAS_FACILITIES_APP_OM_UPGRADE_MODE`
- Default: `manual`

!!! warning
    Application upgrades can overwrite your custom changes — do not select `automatic` if you have customized your application. Currently supported Maximo Real Estate and Facilities release versions are `9.2.x` and above.

#### mas_ws_facilities_pull_policy

`imagePullPolicy` strategy for all deployments. The default `IfNotPresent` reduces the pulling operations in the cluster.

- **Optional**
- Environment Variable: `MAS_FACILITIES_PULL_POLICY`
- Default: `IfNotPresent`

#### mas_ws_facilities_liberty_extension_XML

Name of the secret containing additional XML tags to be added into the existing Liberty Server XML to configure the application accordingly. The secret **must** be named `<workspaceId>-facilities-lexml--sn`.

- **Optional**
- Environment Variable: `MAS_FACILITIES_LIBERTY_EXTENSION_XML_SECRET_NAME`
- Default: None

Sample secret template:

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

#### mas_ws_facilities_server_timezone

Timezone for the Facilities application servers. Set this only if your Facilities database is running with a timezone other than UTC.

- **Optional**
- Environment Variable: `MAS_FACILITIES_SERVER_TIMEZONE`
- Default: `UTC`

If you are creating your Facilities database using the `db2` role, you must set the `DB2_TIMEZONE` property to the same value while provisioning the corresponding DB2 instance.

#### mas_ws_facilities_vault_secret

Name of the secret containing the password to the vault with the AES encryption key. The secret **must** be named `<workspaceId>-facilities-vs--sn`; by default it is generated automatically.

- **Optional**
- Environment Variable: `MAS_FACILITIES_VAULT_SECRET_NAME`
- Default: None

Sample secret template:

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

Dedicated workflow agents (DWFA) to add to MREF, as a JSON array where each DWFA has a unique `name` and `members`; each member has a unique `name` and a `class` of either `user` or `group`.

- **Optional**
- Environment Variable: `MAS_FACILITIES_DWFAGENTS`
- Default: `[]`

Example of the structure:

```bash
export MAS_FACILITIES_DWFAGENTS='[{"name":"dwfa1","members":[{"name": "u1", "class": "user"}]}, {"name":"dwfa2","members":[{"name": "u2", "class": "user"},{"name":"g1", "class":"group"}]}]'
```

#### mas_ws_facilities_custom_properties

Whether a custom FACILITIES.properties file is being used. When set to `true`, the role creates a secret from the provided file; when `false` or not provided, the operator uses its default FACILITIES.properties configuration. Currently supported Maximo Real Estate and Facilities release versions are `9.2.x` and above.

- **Optional**
- Environment Variable: `MAS_FACILITIES_CUSTOM_PROPERTIES`
- Default: `false`

#### mas_ws_facilities_properties_file_local

Path to the custom FACILITIES.properties file; the file is read and used to create a secret in the Facilities namespace. Only used when `mas_ws_facilities_custom_properties` is set to `true`. Currently supported Maximo Real Estate and Facilities release versions are `9.2.x` and above; for reference, see the sample file at `ansible-devops/docs/samples/FACILITIES.properties`.

- **Optional**
- Environment Variable: `MAS_FACILITIES_PROPERTIES_FILE_LOCAL`
- Default: None

#### mas_ws_facilities_properties_secret_name

Name of the secret created in the `mas-<instanceId>-facilities` namespace containing the custom FACILITIES.properties file. Only used when a custom properties file is provided. Currently supported Maximo Real Estate and Facilities release versions are `9.2.x` and above.

- **Optional**
- Environment Variable: `MAS_FACILITIES_PROPERTIES_SECRET_NAME`
- Default: `custom-facilities-properties`

### Facilities Database Settings

#### mas_ws_facilities_db_maxconnpoolsize

Maximum connection pool size for the database.

- **Optional**
- Environment Variable: `MAS_FACILITIES_DB_MAX_POOLSIZE`
- Default: `200`

### Facilities Routes Settings

#### mas_ws_facilities_routes_timeout

Timeout of the application, as a string with the structure `<timeout_value><time_unit>` where `timeout_value` is any non-zero unsigned integer and the supported `time_unit` values are microseconds (us), milliseconds (ms), seconds (s), minutes (m), hours (h), or days (d).

- **Optional**
- Environment Variable: `MAS_FACILITIES_ROUTES_TIMEOUT`
- Default: `600s`

### Facilities Storage Settings

#### mas_ws_facilities_storage_log_class

Storage class name for the Log Persistent Volume Claim used for MREF agents.

- **Optional**
- Environment Variable: `MAS_FACILITIES_STORAGE_LOG_CLASS`
- Default: None — a default storage class is auto-defined according to your cluster's available storage classes

#### mas_ws_facilities_storage_log_mode

Attach mode of the Log PVC. Both `ReadWriteOnce` (block storage class) and `ReadWriteMany` (file storage class) are supported.

- **Optional**
- Environment Variable: `MAS_FACILITIES_STORAGE_LOG_MODE`
- Default: `ReadWriteOnce`

#### mas_ws_facilities_storage_log_size

Size of the Log PVC, in Gigabytes.

- **Optional**
- Environment Variable: `MAS_FACILITIES_STORAGE_LOG_SIZE`
- Default: `30`

#### mas_ws_facilities_storage_userfiles_class

Storage class name for the Userfiles PVC used for MREF agents.

- **Optional**
- Environment Variable: `MAS_FACILITIES_STORAGE_USERFILES_CLASS`
- Default: None — a default storage class is auto-defined according to your cluster's available storage classes

#### mas_ws_facilities_storage_userfiles_mode

Attach mode of the Userfiles PVC. Both `ReadWriteOnce` (block storage class) and `ReadWriteMany` (file storage class) are supported.

- **Optional**
- Environment Variable: `MAS_FACILITIES_STORAGE_USERFILES_MODE`
- Default: `ReadWriteOnce`

#### mas_ws_facilities_storage_userfiles_size

Size of the Userfiles PVC, in Gigabytes.

- **Optional**
- Environment Variable: `MAS_FACILITIES_STORAGE_USERFILES_SIZE`
- Default: `50`

### Facilities Agents Deployment Flexibility Settings

Agents Deployment Flexibility enables you to override the default agent deployment strategy defined by the size attribute. This feature is activated when at least one of the following 13 agent deployment properties is set to a valid, non-empty value. Once activated, any properties that are empty or contain invalid values will be interpreted as if they were equal to `shared`.

#### mas_ws_facilities_dataconnectagent_deploymentmode

Whether the `dataconnectagent` agent is activated in the shared `multiagents` pod, in a dedicated pod, or is disabled — allowed non-empty values are `dedicated`, `disabled`, and `shared`.

- **Optional**
- Environment Variable: `MAS_FACILITIES_DATACONNECTAGENT_DEPLOYMENTMODE`
- Default: `''`

#### mas_ws_facilities_extendedformulaagent_deploymentmode

Whether the `extendedformulaagent` agent is activated in the shared `multiagents` pod, in a dedicated pod, or is disabled — allowed non-empty values are `dedicated`, `disabled`, and `shared`.

- **Optional**
- Environment Variable: `MAS_FACILITIES_EXTENDEDFORMULAAGENT_DEPLOYMENTMODE`
- Default: `''`

#### mas_ws_facilities_formularecalcagent_deploymentmode

Whether the `formularecalcagent` agent is activated in the shared `multiagents` pod, in a dedicated pod, or is disabled — allowed non-empty values are `dedicated`, `disabled`, and `shared`.

- **Optional**
- Environment Variable: `MAS_FACILITIES_FORMULARECALCAGENT_DEPLOYMENTMODE`
- Default: `''`

#### mas_ws_facilities_incomingmailagent_deploymentmode

Whether the `incomingmailagent` agent is activated in the shared `multiagents` pod, in a dedicated pod, or is disabled — allowed non-empty values are `dedicated`, `disabled`, and `shared`.

- **Optional**
- Environment Variable: `MAS_FACILITIES_INCOMINGMAILAGENT_DEPLOYMENTMODE`
- Default: `''`

#### mas_ws_facilities_objectmigrationagent_deploymentmode

Whether the `objectmigrationagent` agent is activated in the shared `multiagents` pod, in a dedicated pod, or is disabled — allowed non-empty values are `dedicated`, `disabled`, and `shared`.

- **Optional**
- Environment Variable: `MAS_FACILITIES_OBJECTMIGRATIONAGENT_DEPLOYMENTMODE`
- Default: `''`

#### mas_ws_facilities_objectpublishagent_deploymentmode

Whether the `objectpublishagent` agent is activated in the shared `multiagents` pod, in a dedicated pod, or is disabled — allowed non-empty values are `dedicated`, `disabled`, and `shared`.

- **Optional**
- Environment Variable: `MAS_FACILITIES_OBJECTPUBLISHAGENT_DEPLOYMENTMODE`
- Default: `''`

#### mas_ws_facilities_maintenanceagent_deploymentmode

Whether the `maintenanceagent` agent is activated in the shared `multiagents` pod, in a dedicated pod, or is disabled — allowed non-empty values are `dedicated`, `disabled`, and `shared`.

- **Optional**
- Environment Variable: `MAS_FACILITIES_MAINTENANCEAGENT_DEPLOYMENTMODE`
- Default: `''`

#### mas_ws_facilities_reportqueueagent_deploymentmode

Whether the `reportqueueagent` agent is activated in the shared `multiagents` pod or in a dedicated pod — allowed non-empty values are `dedicated` and `shared`; this agent cannot be disabled.

- **Optional**
- Environment Variable: `MAS_FACILITIES_REPORTQUEUEAGENT_DEPLOYMENTMODE`
- Default: `''`

#### mas_ws_facilities_wfagent_deploymentmode

Whether the `wfagent` agent is activated in the shared `multiagents` pod or in a dedicated pod — allowed non-empty values are `dedicated` and `shared`; this agent cannot be disabled.

- **Optional**
- Environment Variable: `MAS_FACILITIES_WFAGENT_DEPLOYMENTMODE`
- Default: `''`

#### mas_ws_facilities_wffutureagent_deploymentmode

Whether the `wffutureagent` agent is activated in the shared `multiagents` pod, in a dedicated pod, or is disabled — allowed non-empty values are `dedicated`, `disabled`, and `shared`.

- **Optional**
- Environment Variable: `MAS_FACILITIES_WFFUTUREAGENT_DEPLOYMENTMODE`
- Default: `''`

#### mas_ws_facilities_wfnotificationagent_deploymentmode

Whether the `wfnotificationagent` agent is activated in the shared `multiagents` pod, in a dedicated pod, or is disabled — allowed non-empty values are `dedicated`, `disabled`, and `shared`.

- **Optional**
- Environment Variable: `MAS_FACILITIES_WFNOTIFICATIONAGENT_DEPLOYMENTMODE`
- Default: `''`

#### mas_ws_facilities_reservesmtpagent_deploymentmode

Whether the `reservesmtpagent` agent is activated in the shared `multiagents` pod, in a dedicated pod, or is disabled — allowed non-empty values are `dedicated`, `disabled`, and `shared`.

- **Optional**
- Environment Variable: `MAS_FACILITIES_RESERVESMTPAGENT_DEPLOYMENTMODE`
- Default: `''`

#### mas_ws_facilities_scheduleragent_deploymentmode

Whether the `scheduleragent` agent is activated in the shared `multiagents` pod, in a dedicated pod, or is disabled — allowed non-empty values are `dedicated`, `disabled`, and `shared`.

- **Optional**
- Environment Variable: `MAS_FACILITIES_SCHEDULERAGENT_DEPLOYMENTMODE`
- Default: `''`

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
