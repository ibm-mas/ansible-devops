# suite_app_config

This role is used to configure specific components of the application workspace after the application has been installed in the Maximo Application Suite.

## Role Variables

### General Variables

#### mas_instance_id
Defines the instance id that was used for the MAS installation.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

#### mas_app_id
Defines the application that will be configured, valid settings are: `assist`, `iot`, `facilities`, `manage`, `monitor`, `optimizer`, `predict`, and `visualinspection`.

- **Required**
- Environment Variable: `MAS_APP_ID`
- Default: None

#### mas_workspace_id
MAS application workspace to use to configure app components.

- **Required**
- Environment Variable: `MAS_WORKSPACE_ID`
- Default: None

#### aiservice_instance_id
AI Service instance ID to integrate with Manage application. When set, the role will automatically configure AI Service integration including API key retrieval, URL configuration, and TLS certificate import.

- **Optional**
- Environment Variable: `AISERVICE_INSTANCE_ID`
- Default: None

#### aiservice_tenant_id
AI Service tenant ID to use for the integration. Required when `aiservice_instance_id` is set.

- **Optional**
- Environment Variable: `AISERVICE_TENANT_ID`
- Default: None

#### custom_labels
List of comma separated key=value pairs for setting custom labels on instance specific resources.

- **Optional**
- Environment Variable: `CUSTOM_LABELS`
- Default: None

### Workspace Configuration Variables

#### mas_appws_spec
The application workspace deployment spec used to configure various aspects of the application workspace configuration. Note that use of this will override anything set in `mas_appws_components`.

- **Optional**
- Environment Variable: `MAS_APPWS_SPEC`
- Default: defaults are specified in `vars/defaultspecs/{mas_app_id}.yml`

#### mas_appws_bindings_jdbc
Set the binding scope for the application workspace's JDBC binding (`system`, `application`, `workspace`, or `workspace-application`). Note: For Maximo Real estate and facilities, we recommend to use workspace-application.

- **Optional**
- Environment Variable: `MAS_APPWS_BINDINGS_JDBC`
- Default: `system`

#### mas_appws_components
Defines the app components and versions to configure in the application workspace. Takes the form of key=value pairs separated by a comma i.e. To install health within Manage set `base=latest,health=latest`.

- **Optional**
- Environment Variable: `MAS_APPWS_COMPONENTS`
- Default: Application specific

#### mas_pod_templates_dir
This role will look for configuration files in the specified directory.

- **Optional**
- Environment Variable: `MAS_POD_TEMPLATES_DIR`
- Default: None

Configuration files named:
- `ibm-mas-manage-manageworkspace.yml`
- `ibm-mas-manage-imagestitching.yml`
- `ibm-mas-manage-slackproxy.yml`
- `ibm-mas-manage-healthextworkspace.yml`

The content of the configuration file should be the yaml block that you wish to be inserted into the ManageWorkspace CR. `ibm-mas-manage-manageworkspace.yml` will be inserted into the ManageWorkspace CR `spec -> podTemplates` whereas the component ones e.g, `ibm-mas-manage-imagestitching.yml` will be under `spec -> components -> civil -> podTemplates`. The ibm-mas-manage-ws operator will then pass this on to the corresponding component CR when available.

This is an example of one of the components (civil) - refer to the [BestEfforts reference configuration in the MAS CLI](https://github.com/ibm-mas/cli/blob/master/image/cli/mascli/templates/pod-templates/best-effort/ibm-mas-manage-imagestitching.yml). For full documentation of the supported options refer to the [Customizing Pod Templates](https://www.ibm.com/docs/en/mas-cd/continuous-delivery?topic=configuring-customizing-workloads) in the product documentation.

### Predict Configuration Variables

#### mas_appws_settings_deployment_size
Controls the workload size of predict containers. Available options are `developer`, `small`, `medium` and `large`.

- **Optional**, only supported when configuring **Predict**
- Environment Variable: `MAS_APPWS_SETTINGS_DEPLOYMENT_SIZE`
- Default: `small`

| Deployment_size | Replica |
| --------------- | :-----: |
| developer       |    1    |
| small           |    2    |
| medium          |    3    |

### Watson Studio Local Variables

These variables are only used when using this role to configure **Predict**, or **Health & Predict Utilities**.

#### cpd_wsl_project_id
The ID of the analytics project created in Watson Studio and used to configure `hputilities` application.

- **Required** unless `cpd_wsl_project_name` and `mas_config_dir` are set
- Environment Variable: `CPD_WSL_PROJECT_ID`
- Default: None

#### cpd_wsl_project_name
Specifies the name of the file in `mas_config_dir` where the id of the analytics project is saved. Must be used in conjunction with `mas_config_dir` as an alternative to `cpd_wsl_project_id`.

- **Optional**
- Environment Variable: `CPD_WSL_PROJECT_NAME`
- Default: `wsl-mas-${mas_instance_id}-hputilities`

#### mas_config_dir
Local directory where generated resource definitions are saved into. Used in conjunction with `cpd_wsl_project_name` to retrieve the ID of a Watson Studio project previously created by the [cp4d_service](cp4d_service.md) role.

- **Optional**
- Environment Variable: `MAS_CONFIG_DIR`
- Default: None

### Watson Machine Learning Variables

These variables are only used when using this role to configure **Predict**.

#### cpd_product_version
The version of Cloud Pak for Data installed in the cluster, which is used to infer the version of Watson Machine Learning that must be passed into the Predict workspace configuration.

- **Required**
- Environment Variable: `CPD_PRODUCT_VERSION`
- Default: None

#### cpd_wml_instance_id
Identifier of wml instance to be configured in Predict.

- **Optional**
- Environment Variable: `CPD_WML_INSTANCE_ID`
- Default: `openshift`

#### cpd_wml_url
URL to access WML service (same as Cloud Pak for Data URL).

- **Optional**
- Environment Variable: `CPD_WML_URL`
- Default: `https://internal-nginx-svc.ibm-cpd.svc:12443` (assumes CPD WML is installed the `ibm-cpd` namespace)

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
Boolean value indicating if Watson Studio must be bound to Manage. It is expected a system level WatsonStudioCfg applied in the cluster.

- **Optional**
- Environment Variable: `MAS_APPWS_BINDINGS_HEALTH_WSL_FLAG`
- Default: `false`

#### mas_appws_bindings_health_wsl
Set as `system` to indicate Watson Studio must be installed and bound to Health.

- **Optional**
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
