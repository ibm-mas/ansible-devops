# suite_app_install

This role is used to install a specified application in Maximo Application Suite.

## Role Variables

### General

#### mas_instance_id
Unique identifier for the MAS instance where the application will be installed.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

**Purpose**: Identifies which MAS instance to install the application into. This must match the instance ID used during the MAS core installation to ensure the application is deployed to the correct MAS environment.

**When to use**:
- Always required for any MAS application installation
- Must match the instance ID from your MAS core installation
- Use the same value across all application installations for a given MAS instance

**Valid values**: Lowercase alphanumeric string, 3-12 characters (e.g., `prod`, `dev`, `inst1`)

**Impact**: The application will be installed into the namespace `mas-{mas_instance_id}-{mas_app_id}`. An incorrect instance ID will cause the installation to fail or create resources in the wrong namespace.

**Related variables**: Works with `mas_app_id` to determine the target namespace for the application.

**Note**: This must match the instance ID used when installing MAS core. Cannot be changed after application installation.

#### mas_app_id
Specifies which MAS application to install.

- **Required**
- Environment Variable: `MAS_APP_ID`
- Default: None

**Purpose**: Identifies the specific MAS application to be installed, determining which operator subscription is created and which application resources are deployed.

**When to use**:
- Always required for any MAS application installation
- Set to the specific application you want to install
- Each application requires a separate role execution

**Valid values**: `assist`, `iot`, `facilities`, `manage`, `monitor`, `predict`, `visualinspection`, `optimizer`, `arcgis`

**Impact**: Determines which application operator is installed and which namespace is created (`mas-{mas_instance_id}-{mas_app_id}`). Different applications have different configuration requirements and dependencies.

**Related variables**:
- `mas_app_channel`: Must be set to a valid channel for the selected application
- `mas_app_catalog_source`: Must contain the operator for the selected application
- Application-specific settings variables (e.g., `mas_app_settings_iot_*` for IoT)

**Note**: Each application has its own set of configuration variables. Refer to the application-specific sections below for additional required variables.

#### mas_app_catalog_source
Specifies the OpenShift operator catalog source containing the MAS application operator subscription.

- **Optional**
- Environment Variable: `MAS_APP_CATALOG_SOURCE`
- Default: `ibm-operator-catalog`

**Purpose**: Controls which operator catalog is used to locate and install the MAS application operator. This determines where OpenShift looks for the application operator images and metadata during installation.

**When to use**:
- Use default `ibm-operator-catalog` for production installations with official IBM releases
- Use `ibm-mas-{mas_app_id}-operators` for development builds from Artifactory (e.g., `ibm-mas-manage-operators`)
- Only change if directed to use a custom catalog for specific testing or airgap scenarios

**Valid values**: Any valid CatalogSource name present in the `openshift-marketplace` namespace

**Impact**: Changing this value affects which operator versions are available for installation. An invalid catalog source will cause the subscription to fail. Development catalogs require additional authentication via `artifactory_username` and `artifactory_token`.

**Related variables**:
- `mas_app_channel`: Works together to determine the specific operator version installed
- `artifactory_username` and `artifactory_token`: Required when using development catalogs

**Note**: For development catalogs, the naming pattern is `ibm-mas-{mas_app_id}-operators` where `{mas_app_id}` is the application name (e.g., `manage`, `monitor`).

#### mas_app_channel
Specifies the MAS application operator subscription channel, which determines the version stream you'll receive updates from.

- **Required**
- Environment Variable: `MAS_APP_CHANNEL`
- Default: None

**Purpose**: Controls which version of the MAS application will be installed and which updates will be automatically applied. The channel corresponds to major.minor version releases and determines the feature set and compatibility level of your application installation.

**When to use**:
- Set to the latest stable channel for new production deployments
- Use specific older channels when compatibility with MAS core or other applications requires it
- Consult the MAS compatibility matrix before selecting a channel
- Change channels only during planned upgrade windows as this triggers version updates

**Valid values**: Application-specific channels (e.g., `8.6.x`, `8.7.x`, `8.8.x` for Manage; check the IBM Operator Catalog for currently available channels for your application)

**Impact**: The channel determines which application version is installed and which automatic updates are applied. Changing channels after installation will trigger an upgrade to the latest version in that channel, which may require application reconfiguration and testing.

**Related variables**:
- `mas_app_catalog_source`: Works together to determine available channels
- `mas_instance_id`: Application must be compatible with the MAS core version

**Note**: Each MAS application has its own set of available channels. Ensure the selected channel is compatible with your MAS core version. Review the application upgrade documentation before changing this value.

#### custom_labels
Comma-separated list of key=value labels to apply to MAS application resources.

- **Optional**
- Environment Variable: `CUSTOM_LABELS`
- Default: None

**Purpose**: Adds Kubernetes labels to application resources for organization, selection, and filtering. Labels enable resource tracking, cost allocation, and custom automation.

**When to use**:
- Use to add organizational metadata (e.g., `cost-center=engineering`, `environment=production`)
- Use to enable resource tracking and cost allocation
- Use to support custom automation or monitoring tools
- Use to comply with organizational labeling standards

**Valid values**: Comma-separated list of `key=value` pairs (e.g., `env=prod,team=platform,app=manage`)

**Impact**: Labels are applied to application resources and can be used for filtering with `oc get` commands, monitoring queries, and automation scripts. Labels do not affect application functionality.

**Related variables**: Works alongside Kubernetes resource labels for comprehensive resource management.

### Pre-Release Support

#### artifactory_username
Username for authenticating to IBM Artifactory to access development builds of MAS applications.

- **Optional**
- Environment Variable: `ARTIFACTORY_USERNAME`
- Default: None

**Purpose**: Provides authentication credentials to pull development/pre-release MAS application operator images from IBM's Artifactory registry. Required only when installing development builds for testing or early access.

**When to use**:
- Required when `mas_app_catalog_source` is set to a development catalog (e.g., `ibm-mas-manage-operators`)
- Not needed for production installations using `ibm-operator-catalog`
- Use your IBM w3Id username for development builds

**Valid values**: Valid IBM Artifactory username (typically your w3Id)

**Impact**: Without valid credentials, development catalog subscriptions will fail to pull operator images. This variable is ignored when using production catalogs.

**Related variables**:
- `artifactory_token`: Must be set together with this username
- `mas_app_catalog_source`: Determines if Artifactory credentials are needed
- `mas_entitlement_username`: Used for production installations instead

**Note**: Only required for development/pre-release builds. Production installations use `mas_entitlement_key` instead.

#### artifactory_token
API token for authenticating to IBM Artifactory to access development builds of MAS applications.

- **Optional**
- Environment Variable: `ARTIFACTORY_TOKEN`
- Default: None

**Purpose**: Provides the API token/password credential to authenticate with IBM's Artifactory registry when pulling development/pre-release MAS application operator images.

**When to use**:
- Required when `mas_app_catalog_source` is set to a development catalog (e.g., `ibm-mas-manage-operators`)
- Not needed for production installations using `ibm-operator-catalog`
- Use your IBM Artifactory API key for development builds

**Valid values**: Valid IBM Artifactory API token

**Impact**: Without a valid token, development catalog subscriptions will fail to pull operator images. This variable is ignored when using production catalogs.

**Related variables**:
- `artifactory_username`: Must be set together with this token
- `mas_app_catalog_source`: Determines if Artifactory credentials are needed
- `mas_entitlement_key`: Used for production installations instead

**Note**: Only required for development/pre-release builds. Production installations use `mas_entitlement_key` instead. Keep this token secure and do not commit to source control.

#### mas_entitlement_username
Username for authenticating to IBM Container Registry to pull MAS application images.

- **Optional**
- Environment Variable: `MAS_ENTITLEMENT_USERNAME`
- Default: `cp` for production installations

**Purpose**: Provides the username credential for authenticating with IBM's entitled container registry when pulling MAS application operator and component images.

**When to use**:
- Set to `cp` for production installations using IBM entitlement keys
- Set to your w3Id for development builds from Artifactory
- Usually can be left at default for production installations

**Valid values**: 
- `cp` - For production installations with IBM entitlement key
- Your IBM w3Id - For development builds

**Impact**: Used together with `mas_entitlement_key` to create image pull secrets for the application namespace. Incorrect username will cause image pull authentication failures.

**Related variables**:
- `mas_entitlement_key`: Must be set together with this username
- `artifactory_username`: Alternative for development builds

**Note**: For production installations, the default value `cp` is typically correct when used with an IBM entitlement key.

#### mas_entitlement_key
IBM entitlement key for authenticating access to IBM Container Registry to pull MAS application images.

- **Optional**
- Environment Variable: `MAS_ENTITLEMENT_KEY`
- Default: None

**Purpose**: Provides authentication credentials to pull MAS application container images from IBM's entitled registry. This key is tied to your IBM Cloud account and product entitlements, proving you have the right to use MAS application software.

**When to use**:
- Required for production installations using official IBM releases
- Obtain from IBM Container Library at https://myibm.ibm.com/products-services/containerlibrary
- For development builds, use your Artifactory API key instead
- Key must be valid and have active MAS application entitlements

**Valid values**:
- IBM entitlement key string (typically starts with "eyJ...")
- Must be a valid, non-expired key with MAS product entitlements
- For development: Artifactory API key

**Impact**: Invalid or expired keys will cause image pull failures during application installation. The key is stored in a Kubernetes secret and used to create image pull secrets for all application pods.

**Related variables**:
- `mas_entitlement_username`: Username paired with this key (default: `cp`)
- `artifactory_token`: Alternative for development builds

**Note**: Keep this key secure. Do not commit it to source control. Use environment variables or secure secret management.

### Application Configuration

#### mas_app_spec
Custom YAML specification to override default application configuration settings.

- **Optional**
- Environment Variable: None
- Default: Application-specific defaults in `vars/defaultspecs/{{mas_app_id}}.yml`

**Purpose**: Allows advanced users to provide a complete custom specification for the application installation, bypassing individual configuration variables. This enables fine-grained control over application settings not exposed through standard variables.

**When to use**:
- Use for advanced customization scenarios not covered by standard variables
- Use when you need to set application-specific settings not exposed as role variables
- Use with caution as it overrides all other configuration variables
- Leave unset for standard installations using individual configuration variables

**Valid values**: Valid YAML dictionary matching the application's Custom Resource specification

**Impact**: When set, this completely overrides all other application configuration variables (e.g., `mas_app_settings_*`, `mas_app_bindings_*`). The role will use this specification directly in the application CR.

**Related variables**: Overrides all `mas_app_settings_*` and `mas_app_bindings_*` variables when set.

**Note**: Requires deep knowledge of the application's Custom Resource specification. Incorrect specifications can cause installation failures. Use individual configuration variables unless you have specific advanced requirements.

#### mas_app_bindings_jdbc
Specifies the scope for JDBC database configuration binding.

- **Optional**
- Environment Variable: `MAS_APP_BINDINGS_JDBC`
- Default: `system`

**Purpose**: Controls whether the application uses system-level JDBC configuration (shared across all applications) or application-specific JDBC configuration. This determines which database configuration the application will use.

**When to use**:
- Use `system` (default) when all applications share the same database configuration
- Use `application` when this application needs its own dedicated database configuration
- Most deployments use `system` for simplified management

**Valid values**: `system`, `application`

**Impact**: 
- `system`: Application uses the JDBC configuration defined at the MAS instance level (JdbcCfg with scope=system)
- `application`: Application requires its own application-scoped JDBC configuration (JdbcCfg with scope=application)

**Related variables**: Requires corresponding JdbcCfg resource to be configured at the appropriate scope.

**Note**: Changing this after installation may require reconfiguration of database connections. Ensure the appropriate JdbcCfg resource exists before changing this value.

#### mas_app_plan
Specifies the licensing plan/tier for the application installation.

- **Optional**
- Environment Variable: `MAS_APP_PLAN`
- Default: Application-specific (varies by application)

**Purpose**: Determines which feature set and licensing tier is activated for the application. Different plans may enable or restrict certain features based on your license entitlements.

**When to use**:
- Set according to your license entitlements
- Consult your IBM license agreement for available plans
- Leave as default if you have standard licensing

**Valid values**: Application-specific
- **Optimizer**: `full`, `limited` (v8.2+, defaults to `full`)
- Other applications may have different plan options

**Impact**: The plan determines which features are available in the application. Using a plan not covered by your license may result in compliance issues. Some features may be disabled or unavailable depending on the selected plan.

**Related variables**: Must align with your IBM license entitlements for the application.

**Note**: Ensure the selected plan matches your license agreement. Contact IBM if you're unsure which plan to use.

#### mas_pod_templates_dir
Local directory path containing pod template customization files for the application.

- **Optional**
- Environment Variable: `MAS_POD_TEMPLATES_DIR`
- Default: None

**Purpose**: Allows customization of pod specifications for application workloads, enabling control over resource limits, node affinity, tolerations, and other Kubernetes pod settings. This is essential for production deployments with specific infrastructure requirements.

**When to use**:
- Use to set custom resource limits (CPU, memory) for application pods
- Use to configure node affinity or anti-affinity rules
- Use to add tolerations for tainted nodes
- Use to apply custom security contexts or service accounts
- Leave unset for default pod configurations

**Valid values**: Any valid local filesystem path containing application-specific pod template YAML files

**Impact**: Pod template files in this directory will be applied to the application's Custom Resource, affecting how application pods are scheduled and configured. Invalid templates can cause pod scheduling failures.

**Related variables**: 
- `mas_app_id`: Determines which pod template files are expected
- See application-specific sections below for required file names

**Note**: Each application expects specific file names. Refer to the application-specific `mas_pod_templates_dir` documentation below for details. For full documentation, see [Customizing Pod Templates](https://www.ibm.com/docs/en/mas-cd/continuous-delivery?topic=configuring-customizing-workloads) in the product documentation.

### Visual Inspection Configuration

#### mas_app_settings_visualinspection_storage_class
Storage class for Visual Inspection user data persistent volumes.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_VISUALINSPECTION_STORAGE_CLASS`
- Default: Auto-selected from available ReadWriteMany (RWX) storage classes in the cluster

**Purpose**: Specifies which storage class provides persistent volumes for Visual Inspection user data, including uploaded images, trained models, and inspection results. This storage must support concurrent access from multiple pods.

**When to use**:
- Set explicitly when you have multiple RWX storage classes and want to control which is used
- Set when the auto-selection doesn't choose your preferred storage class
- Leave unset to allow automatic selection of an appropriate RWX storage class

**Valid values**: Any valid storage class name in your cluster that supports ReadWriteMany (RWX) access mode

**Impact**: Affects performance and reliability of Visual Inspection data storage. The storage class must support RWX access mode for Visual Inspection to function correctly.

**Related variables**: `mas_app_settings_visualinspection_storage_size` - Determines the size of the PVC using this storage class.

**Note**: **ReadWriteMany (RWX) support is required**. Verify your storage class supports RWX with `oc get storageclass` before deployment. Common RWX storage classes include NFS, CephFS, and cloud provider file storage.

#### mas_app_settings_visualinspection_storage_size
Size of the persistent volume for Visual Inspection user data.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_VISUALINSPECTION_STORAGE_SIZE`
- Default: `100Gi`

**Purpose**: Determines the amount of disk space allocated for Visual Inspection user data, including uploaded images, trained AI models, inspection results, and datasets. Proper sizing prevents storage exhaustion.

**When to use**:
- Increase for production environments with large image datasets
- Increase for environments with many trained models or long data retention
- Use default (100Gi) for development, testing, or small deployments
- Consider your data retention policies and expected growth

**Valid values**: Any valid Kubernetes storage size (e.g., `100Gi`, `500Gi`, `1Ti`, `2Ti`)

**Impact**: Larger values consume more cluster storage resources. Insufficient storage will prevent uploading new images or training models. PVC expansion capability depends on the storage class.

**Related variables**: `mas_app_settings_visualinspection_storage_class` - Must support volume expansion if you plan to increase size later.

**Note**: Plan for growth when setting initial size. Monitor storage usage to avoid running out of space. Check if your storage class supports PVC expansion before deployment.

### IoT Configuration

#### mas_app_settings_iot_deployment_size
Specifies the deployment size profile for MAS IoT, which determines resource allocations and scaling characteristics.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_IOT_DEPLOYMENT_SIZE`
- Default: `small`

**Purpose**: Controls the resource allocation profile for IoT components, affecting CPU, memory, and replica counts. Different sizes are optimized for different workload scales and environments.

**When to use**:
- Use `dev` for development and testing environments with minimal resource requirements
- Use `small` for production environments with moderate device counts and data volumes
- Use `large` for production environments with high device counts, data volumes, or throughput requirements

**Valid values**: `dev`, `small`, `large`

**Impact**: 
- `dev`: Minimal resources, suitable for development only
- `small`: Moderate resources, suitable for small to medium production deployments
- `large`: Maximum resources, suitable for large-scale production deployments

**Related variables**: Affects overall cluster resource consumption for IoT components.

**Note**: **Application Support: IoT 8.6+**. Ensure your cluster has sufficient resources for the selected size. Cannot be easily changed after deployment without reinstallation.

#### mas_app_settings_iot_fpl_pvc_storage_class
Storage class for IoT Function Pipeline (FPL) component persistent volumes.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_IOT_FPL_PVC_STORAGE_CLASS`
- Default: Auto-selected from available ReadWriteOnce (RWO) storage classes in the cluster

**Purpose**: Specifies which storage class provides persistent volumes for IoT FPL component transient state storage. FPL processes IoT data pipelines and requires persistent storage for state management.

**When to use**:
- Set explicitly when you have multiple RWO storage classes and want to control which is used
- Set when the auto-selection doesn't choose your preferred storage class
- Leave unset to allow automatic selection of an appropriate RWO storage class

**Valid values**: Any valid storage class name in your cluster that supports ReadWriteOnce (RWO) access mode

**Impact**: Affects performance and reliability of IoT data pipeline processing. The storage class determines I/O performance for pipeline state operations.

**Related variables**: 
- `mas_app_settings_iot_fpl_router_pvc_size` - Size for FPL router PVC
- `mas_app_settings_iot_fpl_executor_pvc_size` - Size for FPL executor PVC

**Note**: **Application Support: IoT 8.6+**. ReadWriteOnce (RWO) access mode is required. Verify with `oc get storageclass` before deployment.

#### mas_app_settings_iot_fpl_router_pvc_size
Size of the persistent volume for IoT FPL pipeline router component.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_IOT_FPL_ROUTER_PVC_SIZE`
- Default: `100Gi`

**Purpose**: Determines the amount of disk space allocated for the IoT Function Pipeline router component's transient state storage. The router manages pipeline execution and requires persistent storage for state management.

**When to use**:
- Increase for production environments with high pipeline throughput
- Increase for environments with many concurrent pipelines or complex pipeline logic
- Use default (100Gi) for development, testing, or moderate workloads
- Consider your pipeline complexity and execution frequency

**Valid values**: Any valid Kubernetes storage size (e.g., `50Gi`, `100Gi`, `200Gi`, `500Gi`)

**Impact**: Larger values consume more cluster storage resources. Insufficient storage may cause pipeline execution failures or state management issues.

**Related variables**: 
- `mas_app_settings_iot_fpl_pvc_storage_class` - Storage class for this PVC
- `mas_app_settings_iot_fpl_executor_pvc_size` - Size for FPL executor component

**Note**: **Application Support: IoT 8.6+**. Monitor storage usage and adjust as needed. Check if your storage class supports PVC expansion.

#### mas_app_settings_iot_fpl_executor_pvc_size
Size of the persistent volume for IoT FPL pipeline executor component.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_IOT_FPL_EXECUTOR_PVC_SIZE`
- Default: `100Gi`

**Purpose**: Determines the amount of disk space allocated for the IoT Function Pipeline executor component's transient state storage. The executor runs pipeline logic and requires persistent storage for intermediate data and state.

**When to use**:
- Increase for production environments with high data processing volumes
- Increase for pipelines that process large datasets or generate significant intermediate data
- Use default (100Gi) for development, testing, or moderate workloads
- Consider your pipeline data processing requirements

**Valid values**: Any valid Kubernetes storage size (e.g., `50Gi`, `100Gi`, `200Gi`, `500Gi`)

**Impact**: Larger values consume more cluster storage resources. Insufficient storage may cause pipeline execution failures or data processing issues.

**Related variables**: 
- `mas_app_settings_iot_fpl_pvc_storage_class` - Storage class for this PVC
- `mas_app_settings_iot_fpl_router_pvc_size` - Size for FPL router component

**Note**: **Application Support: IoT 8.6+**. Monitor storage usage and adjust as needed. Check if your storage class supports PVC expansion.

#### mas_app_settings_iot_mqttbroker_pvc_storage_class
Storage class for IoT MQTT broker (MessageSight) persistent volumes.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_IOT_MQTTBROKER_PVC_STORAGE_CLASS`
- Default: Auto-selected from available ReadWriteOnce (RWO) storage classes in the cluster

**Purpose**: Specifies which storage class provides persistent volumes for the IoT MQTT broker component. The MQTT broker handles device connectivity and message routing, requiring persistent storage for message queues and broker state.

**When to use**:
- Set explicitly when you have multiple RWO storage classes and want to control which is used
- Set when the auto-selection doesn't choose your preferred storage class
- Set when you need specific performance characteristics for MQTT message handling
- Leave unset to allow automatic selection of an appropriate RWO storage class

**Valid values**: Any valid storage class name in your cluster that supports ReadWriteOnce (RWO) access mode

**Impact**: Affects performance and reliability of IoT device connectivity and message routing. The storage class determines I/O performance for message queue operations.

**Related variables**: `mas_app_settings_iot_mqttbroker_pvc_size` - Determines the size of the PVC using this storage class.

**Note**: **Application Support: IoT 8.3+**. ReadWriteOnce (RWO) access mode is required. Verify with `oc get storageclass` before deployment.

#### mas_app_settings_iot_mqttbroker_pvc_size
Size of the persistent volume for IoT MQTT broker (MessageSight) component.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_IOT_MQTTBROKER_PVC_SIZE`
- Default: `100Gi`

**Purpose**: Determines the amount of disk space allocated for the IoT MQTT broker's persistent storage, including message queues, broker state, and retained messages. Proper sizing ensures reliable device connectivity and message handling.

**When to use**:
- Increase for production environments with many connected devices
- Increase for environments with high message volumes or long message retention
- Increase if devices frequently disconnect and require message queuing
- Use default (100Gi) for development, testing, or moderate device counts

**Valid values**: Any valid Kubernetes storage size (e.g., `50Gi`, `100Gi`, `200Gi`, `500Gi`)

**Impact**: Larger values consume more cluster storage resources. Insufficient storage may cause message loss, device connection failures, or broker instability.

**Related variables**: `mas_app_settings_iot_mqttbroker_pvc_storage_class` - Storage class for this PVC.

**Note**: **Application Support: IoT 8.3+**. Monitor storage usage to prevent message queue overflow. Check if your storage class supports PVC expansion.

#### mas_pod_templates_dir (IoT)
This role will look for configuration files named: `ibm-mas-iot-iot.yml`, `ibm-mas-iot-actions.yml`, `ibm-mas-iot-auth.yml`, `ibm-mas-iot-datapower.yml`, `ibm-mas-iot-devops.yml`, `ibm-mas-iot-dm.yml`, `ibm-mas-iot-dsc.yml`, `ibm-mas-iot-edgeconfig.yml`, `ibm-mas-iot-fpl.yml`, `ibm-mas-iot-guardian.yml`, `ibm-mas-iot-mbgx.yml`, `ibm-mas-iot-mfgx.yml`, `ibm-mas-iot-monitor.yml`, `ibm-mas-iot-orgmgmt.yml`, `ibm-mas-iot-provision.yml`, `ibm-mas-iot-registry.yml`, `ibm-mas-iot-state.yml`, `ibm-mas-iot-webui.yml`. The content of the configuration file should be the yaml block that you wish to be inserted into the IoT CR. `ibm-mas-iot-iot.yml` will be inserted into the main IoT CR `spec -> podTemplates` whereas the component ones e.g, `ibm-mas-iot-actions.yml` will be under `spec -> components -> {componentName} -> podTemplates`. The ibm-mas-iot operator will then pass this on to the corresponding component CR when available. This is an example of one of the components (actions) - refer to the [BestEfforts reference configuration in the MAS CLI](https://github.com/ibm-mas/cli/blob/master/image/cli/mascli/templates/pod-templates/best-effort/ibm-mas-iot-actions.yml). For full documentation of the supported options refer to the [Customizing Pod Templates](https://www.ibm.com/docs/en/mas-cd/continuous-delivery?topic=configuring-customizing-workloads) in the product documentation.

- **Optional**
- Environment Variable: `MAS_POD_TEMPLATES_DIR`
- Default: None

### Manage Configuration

#### mas_pod_templates_dir (Manage)
This role will look for a configuration file named `ibm-mas-manage-manageapp.yml`. The content of the configuration file should be the yaml block that you wish to be inserted into the ManageApp CR. `ibm-mas-manage-manageapp.yml` will be inserted into the ManageApp CR `spec -> podTemplates`. The ibm-mas-manage operator will then pass this on to the corresponding deployments when available. For full documentation of the supported options refer to the [Customizing Pod Templates](https://www.ibm.com/docs/en/mas-cd/continuous-delivery?topic=configuring-customizing-workloads) in the product documentation.

- **Optional**
- Environment Variable: `MAS_POD_TEMPLATES_DIR`
- Default: None

#### mas_appws_upgrade_type
Specifies the upgrade strategy for Manage workspace database schema updates.

- **Optional**
- Environment Variable: `MAS_APPWS_UPGRADE_TYPE`
- Default: `regularUpgrade`

**Purpose**: Controls how Manage performs database schema upgrades during application updates, balancing between system downtime and upgrade complexity. Different strategies offer different trade-offs between availability and upgrade duration.

**When to use**:
- Use `regularUpgrade` for standard upgrades with planned downtime windows
- Use `onlineUpgrade` to minimize downtime during upgrades (requires more resources and time)
- Consider your maintenance window constraints and availability requirements

**Valid values**: 
- `regularUpgrade` - Standard upgrade with full system downtime
- `onlineUpgrade` - Minimized downtime upgrade (requires additional resources)

**Impact**: 
- `regularUpgrade`: Shorter upgrade time but requires full system downtime
- `onlineUpgrade`: Longer upgrade time but minimizes system downtime; requires additional database resources during upgrade

**Related variables**: Applies to Manage application upgrades only.

**Note**: For full documentation of upgrade types and requirements, refer to the [Manage Upgrade information](https://www.ibm.com/docs/en/masv-and-l/cd?topic=database-reducing-system-downtime) in the product documentation. Online upgrades require careful planning and additional resources.

### Monitor Configuration

#### mas_app_settings_monitor_deployment_size
Specifies the deployment size profile for MAS Monitor, which determines resource allocations and scaling characteristics.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_MONITOR_DEPLOYMENT_SIZE`
- Default: `dev`

**Purpose**: Controls the resource allocation profile for Monitor components, affecting CPU, memory, and replica counts. Different sizes are optimized for different workload scales and environments.

**When to use**:
- Use `dev` for development and testing environments with minimal resource requirements
- Use `small` for production environments with moderate monitoring requirements
- Use `large` for production environments with extensive monitoring, dashboards, or high data volumes

**Valid values**: `dev`, `small`, `large`

**Impact**: 
- `dev`: Minimal resources, suitable for development only
- `small`: Moderate resources, suitable for small to medium production deployments
- `large`: Maximum resources, suitable for large-scale production deployments with extensive monitoring

**Related variables**: Affects overall cluster resource consumption for Monitor components.

**Note**: **Application Support: Monitor 8.6+**. Ensure your cluster has sufficient resources for the selected size. Cannot be easily changed after deployment without reinstallation.

## Example Playbook

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    # Choose which catalog source to use for the MAS install, default to the IBM operator catalog
    mas_app_catalog_source: "{{ lookup('env', 'MAS_APP_CATALOG_SOURCE') | default('ibm-operator-catalog', true) }}"

    # Which MAS channel to subscribe to
    mas_app_channel: "{{ lookup('env', 'MAS_APP_CHANNEL') | default('8.x', true) }}"

    # MAS configuration
    mas_instance_id: "{{ lookup('env', 'MAS_INSTANCE_ID') }}"

    # MAS configuration - Entitlement
    mas_entitlement_username: "{{ lookup('env', 'MAS_ENTITLEMENT_USERNAME') | default('cp', true) }}"
    mas_entitlement_key: "{{ lookup('env', 'MAS_ENTITLEMENT_KEY') }}"

    # MAS application configuration
    mas_app_id: "{{ lookup('env', 'MAS_APP_ID') }}"

    # Application Configuration - Spec
    mas_app_spec:
      bindings:
        jdbc: system
        mongo: system
        kafka: system
      settings:
        messagesight:
          storage:
            class: block1000p
            size: 100Gi
        deployment:
          size: medium

    # Application Configuration - Install Plan
    mas_app_plan: "{{ lookup('env', 'MAS_APP_PLAN') | default('full', true) }}"

  roles:
    - ibm.mas_devops.suite_app_install
```

## License

EPL-2.0
