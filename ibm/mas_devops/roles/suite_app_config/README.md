suite_app_config
===============================================================================

This role is used to configure specific components of the application workspace after the application has been installed in the Maximo Application Suite.


Role Variables - General
-------------------------------------------------------------------------------
### mas_instance_id
Defines the instance id that was used for the MAS installation

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

### mas_app_id
Defines the application that is will be configured, valid settings are: `assist`, `hputilities`, `iot`, `manage`, `monitor`, `optimizer`, `predict`, and `visualinspection`.

- **Required**
- Environment Variable: `MAS_APP_ID`
- Default: None

### mas_workspace_id
MAS application workspace to use to configure app components

- **Required**
- Environment Variable: `MAS_WORKSPACE_ID`
- Default: None

### custom_labels
List of comma separated key=value pairs for setting custom labels on instance specific resources.

- Optional
- Environment Variable: `CUSTOM_LABELS`
- Default: None


Role Variables - Workspace Configuration
-------------------------------------------------------------------------------
### mas_appws_spec
The application workspace deployment spec used to configure various aspects of the application workspace configuration. Note that use of this will override anything set in `mas_appws_components`

- Optional
- Environment Variable: `MAS_APPWS_SPEC`
- Default: defaults are specified in `vars/defaultspecs/{mas_app_id}.yml`

### mas_appws_bindings_jdbc
Set the binding scope for the application workspace's JDBC binding (`system`, `application`, `workspace`, or `workspace-application`)

- Optional
- Environment Variable: `MAS_APPWS_BINDINGS_JDBC`
- Default: `system`

### mas_appws_components
Defines the app components and versions to configure in the application workspace. Takes the form of key=value pairs seperated by a comma i.e. To install health within Manage set `base=latest,health=latest`

- Optional
- Environment Variable: `MAS_APPWS_COMPONENTS`
- Default: Application specific


Role Variables - Predict Configuration
-------------------------------------------------------------------------------
### mas_appws_settings_deployment_size
Controls the workload size of predict containers. Avaliable options are `developer`, `small`, `medium` and `small`

    | Deployment_size        | Replica |
    | ---------------------- | :--: |
    | developer              |  1 |
    | small                  |  2 |
    | medium                 |  3 |

- Optional, only supported when configuring **Predict**
- Environment Variable: `MAS_APPWS_SETTINGS_DEPLOYMENT_SIZE`
- Default: `small`


Role Variables - Watson Studio Local
-------------------------------------------------------------------------------
These variables are only used when using this role to configure **Predict**, or **Health & Predict Utilities**.

### cpd_wsl_project_id
The ID of the analytics project created in Watson Studio and used to configure `hputilities` application.

- **Required** unless `cpd_wsl_project_name` and `mas_config_dir` are set.
- Environment Variable: `CPD_WSL_PROJECT_ID`
- Default: None

### cpd_wsl_project_name
Specifies the name of the file in `mas_config_dir` where the id of the analytics project is saved.  Must be used in conjunction with `mas_config_dir` as an alternative to `cpd_wsl_project_id`.

- Optional
- Environment Variable: `CPD_WSL_PROJECT_NAME`
- Default Value: `wsl-mas-${mas_instance_id}-hputilities`

### mas_config_dir
Local directory where generated resource definitions are saved into. Used in conjunction with `cpd_wsl_project_name` to retrieve the ID of a Watson Studio project previously created by the [cp4d_service](cp4d_service.md) role.

- Optional
- Environment Variable: `MAS_CONFIG_DIR`
- Default Value: None


Role Variables - Watson Machine Learning
-------------------------------------------------------------------------------
These variables are only used when using this role to configure **Predict**.

### cpd_product_version
The version of Cloud Pak for Data installed in the cluster, which is used to infer the version of Watson Machine Learning that must be passed into the Predict workspace configuration.

- **Required**
- Environment Variable: `CPD_PRODUCT_VERSION`
- Default: None

### cpd_wml_instance_id
Identifier of wml instance to be configured in Predict.

- Optional
- Environment Variable: `CPD_WML_INSTANCE_ID`
- Default: `openshift`

### cpd_wml_url
URL to access WML service (same as Cloud Pak for Data URL).

- Optional
- Environment Variable: `CPD_WML_URL`
- Default: `https://internal-nginx-svc.ibm-cpd.svc:12443` (assumes CPD WML is installed the `ibm-cpd` namespace)


Role Variables - Manage Workspace
-------------------------------------------------------------------------------
### mas_app_settings_aio_flag
Optional. Flag indicating if Asset Investment Optimization (AIO) resource must be loaded or not. It can be loaded only when Optimizer application is installed.

- Only supported when Optimizer application is installed.
- Environment Variable: `MAS_APP_SETTINGS_AIO_FLAG`
- Default: `true`

### mas_app_settings_db2_schema
Optional. Name of the schema where Manage database lives in.

- Environment Variable: MAS_APP_SETTINGS_DB2_SCHEMA') |
- Default: `maximo`

### mas_app_settings_demodata
Optional. Flag indicating if manage demodata should be loaded or not.

- Environment Variable: `MAS_APP_SETTINGS_DEMODATA`
- Default: `false` (do not load demodata)

### mas_app_settings_tablespace
Optional. Name of the Manage database tablespace

- Environment Variable: `MAS_APP_SETTINGS_TABLESPACE`
- Default: `MAXDATA`

### mas_app_settings_indexspace
Optional. Name of the Manage database indexspace

- Environment Variable: `MAS_APP_SETTINGS_INDEXSPACE`
- Default: `MAXINDEX`

### mas_app_settings_persistent_volumes_flag
Optional. Flag indicating if persistent volumes should be configured by default during Manage Workspace activation.
There are two defaulted File Storage Persistent Volumes Claim resources that will be created out of the box for Manage if this flag is set to `true`:

- `/DOCLINKS`: Persistent volume used to store doclinks/attachments.
- `/bim`: Persistent volume used to store Building Information Models related artifacts (models, docs and import).

- Environment Variable: `MAS_APP_SETTINGS_PERSISTENT_VOLUMES_FLAG`
- Default: `false`

### mas_app_settings_base_language
Optional. Provide the base language for Manage application.
For a full list of supported languages for Manage application and its corresponding language codes, please refer to [Language Support](https://www.ibm.com/docs/en/maximo-manage/continuous-delivery?topic=deploy-language-support) documentation.

- Environment Variable: `MAS_APP_SETTINGS_BASE_LANG`
- Default: `EN` (English)

### mas_app_settings_secondary_languages
Optional. Provide a list of additional secondary languages for Manage application.

Note: The more languages you add, the longer Manage will take to install and activate.

Export the `MAS_APP_SETTINGS_SECONDARY_LANGS` variable with the language codes as comma-separated values.
For a full list of supported languages for Manage application and its corresponding language codes, please refer to [Language Support](https://www.ibm.com/docs/en/maximo-manage/continuous-delivery?topic=deploy-language-support) documentation.

- Environment Variable: `MAS_APP_SETTINGS_SECONDARY_LANGS`
- Default: None

 For example, use the following to enable Manage application with Arabic, Deutsch and Japanese as secondary languages:
`export MAS_APP_SETTINGS_SECONDARY_LANGS='AR,DE,JA'`

### mas_app_settings_server_bundles_size
Optional. Provides different flavors of server bundle configuration to handle workload for Manage application.
For more details about Manage application server bundle configuration, refer to [Setting the server bundles for Manage application](https://www.ibm.com/docs/en/maximo-manage/continuous-delivery?topic=manage-setting-server-bundles).

Currently supported server bundle sizes are:

- `dev` - Deploys Manage with the default server bundle configuration.
  - i.e just 1 bundle pod handling `all` Manage application workload.
- `small` - Deploys Manage with the most common deployment configuration.
  - i.e 4 bundle pods, each one handling workload for each main capabilities: `mea`, `cron`, `report` and `ui`
- `jms` - Can be used for Manage 8.4 and above. Same server bundle configuration as `small` and includes `jms` bundle pod.
  - Enabling JMS pod workload will also configure Manage to use default JMS messaging queues to be stored in `/{{ mas_app_settings_jms_queue_mount_path }}/jmsstore` persistent volume mount path.

- Environment Variable: `MAS_APP_SETTINGS_SERVER_BUNDLES_SIZE`
- Default: `dev`

### mas_app_settings_jms_queue_pvc_storage_class
Optional. Provide the persistent volume storage class to be used for JMS queue configuration.
**Note:** JMS configuration will only be done if `mas_app_settings_server_bundles_size` property is set to `jms`.

- Environment Variable: `MAS_APP_SETTINGS_JMS_QUEUE_PVC_STORAGE_CLASS`
- Default: None - If not set, a default storage class will be auto defined accordingly to your cluster's available storage classes.

### mas_app_settings_jms_queue_pvc_name
Optional. Provide the persistent volume claim name to be used for JMS queue configuration.
**Note:** JMS configuration will only be done if `mas_app_settings_server_bundles_size` property is set to `jms`.

- Environment Variable: `MAS_APP_SETTINGS_JMS_QUEUE_PVC_NAME`
- Default: `manage-jms`

### mas_app_settings_jms_queue_pvc_size
Optional. Provide the persistent volume claim size to be used for JMS queue configuration.
**Note:** JMS configuration will only be done if `mas_app_settings_server_bundles_size` property is set to `jms`.

- Environment Variable: `MAS_APP_SETTINGS_JMS_QUEUE_PVC_SIZE`
- Default: `20Gi`

### mas_app_settings_jms_queue_mount_path
Optional. Provide the persistent volume storage mount path to be used for JMS queue configuration.
**Note:** JMS configuration will only be done if `mas_app_settings_server_bundles_size` property is set to `jms`.

- Environment Variable: `MAS_APP_SETTINGS_JMS_QUEUE_MOUNT_PATH`
- Default: `/jms`

### mas_app_settings_customization_archive_url
Optional. Provide a custom archive/file path to be included as part of Manage deployment.

- Environment Variable: `MAS_APP_SETTINGS_CUSTOMIZATION_ARCHIVE_URL`
- Default: None

### mas_app_settings_customization_archive_name
Optional. Provide a custom archive file name to be associated with the archive/file path provided. Only used when `mas_app_settings_customization_archive_url` is defined. 

- Environment Variable: `MAS_APP_SETTINGS_CUSTOMIZATION_ARCHIVE_NAME`
- Default: `manage-custom-archive`

### mas_appws_bindings_health_wsl
Optional. Set as `system` to indicate Watson Studio must be installed and bound to Heath

- Environment Variable: `MAS_APPWS_BINDINGS_HEALTH_WSL`
- Default: None


Example Playbook
-------------------------------------------------------------------------------

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

License
-------------------------------------------------------------------------------

EPL-2.0
