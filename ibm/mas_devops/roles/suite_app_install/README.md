# suite_app_install

This role is used to install a specified application in Maximo Application Suite.

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`mas_instance_id`](#mas_instance_id) | Yes | None |
| [`mas_app_id`](#mas_app_id) | Yes | None |
| [`mas_app_catalog_source`](#mas_app_catalog_source) | No | `ibm-operator-catalog` |
| [`mas_app_channel`](#mas_app_channel) | No | `8.x` |
| [`custom_labels`](#custom_labels) | No | None |
| [`artifactory_username`](#artifactory_username) | Conditional | None |
| [`artifactory_token`](#artifactory_token) | Conditional | None |
| [`mas_entitlement_username`](#mas_entitlement_username) | No | `cp` |
| [`mas_entitlement_key`](#mas_entitlement_key) | Conditional | None |
| [`mas_app_spec`](#mas_app_spec) | No | Application-specific defaults |
| [`mas_app_bindings_jdbc`](#mas_app_bindings_jdbc) | No | `system` |
| [`mas_app_plan`](#mas_app_plan) | No | Application-specific |
| [`mas_pod_templates_dir`](#mas_pod_templates_dir) | No | None |
| [`mas_app_settings_visualinspection_storage_class`](#mas_app_settings_visualinspection_storage_class) | No | Auto-detected (RWX) |
| [`mas_app_settings_visualinspection_storage_size`](#mas_app_settings_visualinspection_storage_size) | No | `100Gi` |
| [`mas_app_settings_iot_deployment_size`](#mas_app_settings_iot_deployment_size) | No | `small` |
| [`mas_app_settings_iot_fpl_pvc_storage_class`](#mas_app_settings_iot_fpl_pvc_storage_class) | Conditional | Auto-detected (RWO) |
| [`mas_app_settings_iot_fpl_router_pvc_size`](#mas_app_settings_iot_fpl_router_pvc_size) | No | `100Gi` |
| [`mas_app_settings_iot_fpl_executor_pvc_size`](#mas_app_settings_iot_fpl_executor_pvc_size) | No | `100Gi` |
| [`mas_app_settings_iot_mqttbroker_pvc_storage_class`](#mas_app_settings_iot_mqttbroker_pvc_storage_class) | Conditional | Auto-detected (RWO) |
| [`mas_app_settings_iot_mqttbroker_pvc_size`](#mas_app_settings_iot_mqttbroker_pvc_size) | No | `100Gi` |
| [`mas_appws_upgrade_type`](#mas_appws_upgrade_type) | No | `regularUpgrade` |
| [`mas_app_settings_monitor_deployment_size`](#mas_app_settings_monitor_deployment_size) | No | `dev` |
| [`mas_app_settings_predict_deployment_size`](#mas_app_settings_predict_deployment_size) | No | `small` |

The Artifactory credentials are only required when `mas_app_catalog_source` is set to a development catalog, and `mas_entitlement_key` is only required for production installations using official IBM releases. The IoT storage class variables are only required when auto-detection cannot find a suitable storage class (and always when `mas_app_settings_iot_deployment_size` is not `dev`).

### Core Installation Settings

#### mas_instance_id

Unique identifier for the MAS instance where the application will be installed — a lowercase alphanumeric string of 3-12 characters (e.g., `prod`, `dev`, `inst1`).

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

This must match the instance ID used when installing MAS core, cannot be changed after application installation, and should use the same value across all application installations for a given MAS instance. The application is installed into the namespace `mas-{mas_instance_id}-{mas_app_id}`, so an incorrect instance ID will cause the installation to fail or create resources in the wrong namespace.

#### mas_app_id

Specifies which MAS application to install — one of `assist`, `iot`, `facilities`, `manage`, `monitor`, `predict`, `visualinspection`, `optimizer`, or `arcgis`.

- **Required**
- Environment Variable: `MAS_APP_ID`
- Default: None

Each application requires a separate role execution, determines which application operator is installed and which namespace is created (`mas-{mas_instance_id}-{mas_app_id}`), and has its own set of configuration variables (e.g., `mas_app_settings_iot_*` for IoT). `mas_app_channel` must be set to a valid channel and `mas_app_catalog_source` must contain the operator for the selected application.

#### mas_app_catalog_source

OpenShift operator catalog source containing the MAS application operator subscription — any valid CatalogSource name present in the `openshift-marketplace` namespace.

- **Optional**
- Environment Variable: `MAS_APP_CATALOG_SOURCE`
- Default: `ibm-operator-catalog`

Use the default `ibm-operator-catalog` for production installations with official IBM releases, and `ibm-mas-{mas_app_id}-operators` (e.g., `ibm-mas-manage-operators`) for development builds from Artifactory — development catalogs require additional authentication via `artifactory_username` and `artifactory_token`. An invalid catalog source will cause the subscription to fail.

#### mas_app_channel

MAS application operator subscription channel, which determines the version stream you will receive updates from — application-specific channels such as `8.6.x`, `8.7.x`, or `8.8.x` for Manage (check the IBM Operator Catalog for currently available channels for your application).

- **Optional**
- Environment Variable: `MAS_APP_CHANNEL`
- Default: `8.x`

The channel determines which application version is installed and which automatic updates are applied. Consult the MAS compatibility matrix before selecting a channel to ensure compatibility with your MAS core version, and change channels only during planned upgrade windows — changing channels after installation triggers an upgrade to the latest version in the new channel, which may require reconfiguration and testing.

#### custom_labels

Comma-separated list of `key=value` labels to apply to MAS application resources (e.g., `env=prod,team=platform,app=manage`).

- **Optional**
- Environment Variable: `CUSTOM_LABELS`
- Default: None

Use for organizational metadata (e.g., `cost-center=engineering`, `environment=production`), resource tracking, cost allocation, and custom automation or monitoring. Labels can be used for filtering with `oc get` commands, monitoring queries, and automation scripts, but do not affect application functionality.

### Entitlement and Registry Credentials

#### artifactory_username

Username for authenticating to IBM Artifactory to access development builds of MAS applications — typically your IBM w3Id.

- **Optional** — required when `mas_app_catalog_source` is set to a development catalog (e.g., `ibm-mas-manage-operators`)
- Environment Variable: `ARTIFACTORY_USERNAME`
- Default: None

Without valid credentials, development catalog subscriptions will fail to pull operator images. Not needed for production installations using `ibm-operator-catalog`, which use `mas_entitlement_key` instead. Must be set together with `artifactory_token`.

#### artifactory_token

API token for authenticating to IBM Artifactory to access development builds of MAS applications.

- **Optional** — required when `mas_app_catalog_source` is set to a development catalog (e.g., `ibm-mas-manage-operators`)
- Environment Variable: `ARTIFACTORY_TOKEN`
- Default: None

Without a valid token, development catalog subscriptions will fail to pull operator images. Must be set together with `artifactory_username`; production installations use `mas_entitlement_key` instead.

!!! warning
    Keep this token secure and do not commit it to source control. Use environment variables or secure secret management.

#### mas_entitlement_username

Username for authenticating to IBM Container Registry to pull MAS application images — `cp` for production installations with an IBM entitlement key, or your IBM w3Id for development builds.

- **Optional**
- Environment Variable: `MAS_ENTITLEMENT_USERNAME`
- Default: `cp` for production installations

Used together with `mas_entitlement_key` to create image pull secrets for the application namespace; an incorrect username will cause image pull authentication failures.

#### mas_entitlement_key

IBM entitlement key for authenticating access to IBM Container Registry to pull MAS application images — a valid, non-expired key with MAS product entitlements, typically starting with `eyJ...`.

- **Optional** — required for production installations using official IBM releases
- Environment Variable: `MAS_ENTITLEMENT_KEY`
- Default: None (falls back to `ibm_entitlement_key` / `IBM_ENTITLEMENT_KEY`)

Obtain the key from the IBM Container Library at https://myibm.ibm.com/products-services/containerlibrary; for development builds, use your Artifactory API key instead. The key is stored in a Kubernetes secret and used to create image pull secrets for all application pods — invalid or expired keys will cause image pull failures during application installation.

!!! warning
    Keep this key secure and do not commit it to source control. Use environment variables or secure secret management.

### Application Configuration

#### mas_app_spec

Custom YAML specification to override default application configuration settings — a valid YAML dictionary matching the application's Custom Resource specification.

- **Optional**
- Environment Variable: None
- Default: Application-specific defaults in `vars/defaultspecs/{{mas_app_id}}.yml`

Use for advanced customization scenarios not covered by the standard `mas_app_settings_*` and `mas_app_bindings_*` variables; leave unset for standard installations.

!!! warning
    When set, this completely overrides all other application configuration variables (`mas_app_settings_*`, `mas_app_bindings_*`) — the role uses this specification directly in the application CR. Incorrect specifications can cause installation failures, so this requires deep knowledge of the application's Custom Resource specification.

#### mas_app_bindings_jdbc

Scope for JDBC database configuration binding — either `system` (shared across all applications) or `application` (dedicated to this application).

- **Optional**
- Environment Variable: `MAS_APP_BINDINGS_JDBC`
- Default: `system`

With `system`, the application uses the JDBC configuration defined at the MAS instance level (JdbcCfg with scope=system); with `application`, the application requires its own application-scoped JdbcCfg resource. Most deployments use `system` for simplified management. Changing this after installation may require reconfiguration of database connections — ensure the appropriate JdbcCfg resource exists at the corresponding scope before changing this value.

#### mas_app_plan

Licensing plan/tier for the application installation — application-specific; for example Optimizer supports `full` and `limited` (v8.2+, defaulting to `full`).

- **Optional**
- Environment Variable: `MAS_APP_PLAN`
- Default: Application-specific (varies by application)

The plan determines which features are available in the application. Set it according to your license entitlements — using a plan not covered by your license may result in compliance issues, with some features disabled or unavailable. Consult your IBM license agreement or contact IBM if you're unsure which plan to use.

#### mas_pod_templates_dir

Local directory path containing pod template customization files for the application, enabling control over resource limits, node affinity, tolerations, security contexts, and service accounts.

- **Optional**
- Environment Variable: `MAS_POD_TEMPLATES_DIR`
- Default: None

`mas_app_id` determines which pod template files are expected — see the [IoT](#iot-configuration) and [Manage](#manage-configuration) sections below for the file names each application looks for. The files are applied to the application's Custom Resource, affecting how application pods are scheduled and configured; invalid templates can cause pod scheduling failures. For full documentation, see [Customizing Pod Templates](https://www.ibm.com/docs/en/mas-cd/continuous-delivery?topic=configuring-customizing-workloads) in the product documentation.

### Visual Inspection Configuration

#### mas_app_settings_visualinspection_storage_class

Storage class for Visual Inspection user data persistent volumes (uploaded images, trained models, and inspection results) — any valid storage class name in your cluster that supports ReadWriteMany (RWX) access mode.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_VISUALINSPECTION_STORAGE_CLASS`
- Default: Auto-selected from available ReadWriteMany (RWX) storage classes in the cluster

Set explicitly when you have multiple RWX storage classes and want to control which is used, or when auto-selection doesn't choose your preferred class.

!!! important
    ReadWriteMany (RWX) support is **required** for Visual Inspection to function correctly. Verify your storage class supports RWX with `oc get storageclass` before deployment — common RWX storage classes include NFS, CephFS, and cloud provider file storage.

#### mas_app_settings_visualinspection_storage_size

Size of the persistent volume for Visual Inspection user data — any valid Kubernetes storage size (e.g., `100Gi`, `500Gi`, `1Ti`, `2Ti`).

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_VISUALINSPECTION_STORAGE_SIZE`
- Default: `100Gi`

Increase for production environments with large image datasets, many trained models, or long data retention; use the default for development, testing, or small deployments. Insufficient storage will prevent uploading new images or training models — plan for growth, monitor storage usage, and check whether your storage class supports PVC expansion before deployment.

### IoT Configuration

#### mas_app_settings_iot_deployment_size

Deployment size profile for MAS IoT, which determines resource allocations and scaling characteristics — `dev`, `small`, or `large`.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_IOT_DEPLOYMENT_SIZE`
- Default: `small`

`dev` allocates minimal resources suitable for development only, `small` moderate resources suitable for small to medium production deployments, and `large` maximum resources suitable for large-scale production deployments. Application support: IoT 8.6+. Ensure your cluster has sufficient resources for the selected size — this cannot be easily changed after deployment without reinstallation.

#### mas_app_settings_iot_fpl_pvc_storage_class

Storage class for IoT Function Pipeline (FPL) component persistent volumes, which store transient state for pipeline processing — any valid storage class name in your cluster that supports ReadWriteOnce (RWO) access mode.

- **Optional** — always required when `mas_app_settings_iot_deployment_size` is not `dev`
- Environment Variable: `MAS_APP_SETTINGS_IOT_FPL_PVC_STORAGE_CLASS`
- Default: Auto-selected from available ReadWriteOnce (RWO) storage classes in the cluster

Set explicitly when you have multiple RWO storage classes and want to control which is used, or when auto-selection doesn't choose your preferred class. The storage class determines I/O performance for pipeline state operations. Application support: IoT 8.6+ — verify with `oc get storageclass` before deployment.

#### mas_app_settings_iot_fpl_router_pvc_size

Size of the persistent volume for the IoT FPL pipeline router component's transient state storage — any valid Kubernetes storage size (e.g., `50Gi`, `100Gi`, `200Gi`, `500Gi`).

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_IOT_FPL_ROUTER_PVC_SIZE`
- Default: `100Gi`

Increase for production environments with high pipeline throughput, many concurrent pipelines, or complex pipeline logic; use the default for development, testing, or moderate workloads. Application support: IoT 8.6+. Insufficient storage may cause pipeline execution failures — monitor storage usage and check whether your storage class supports PVC expansion.

#### mas_app_settings_iot_fpl_executor_pvc_size

Size of the persistent volume for the IoT FPL pipeline executor component's transient state and intermediate data — any valid Kubernetes storage size (e.g., `50Gi`, `100Gi`, `200Gi`, `500Gi`).

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_IOT_FPL_EXECUTOR_PVC_SIZE`
- Default: `100Gi`

Increase for production environments with high data processing volumes or pipelines that process large datasets; use the default for development, testing, or moderate workloads. Application support: IoT 8.6+. Insufficient storage may cause pipeline execution or data processing failures — monitor storage usage and check whether your storage class supports PVC expansion.

#### mas_app_settings_iot_mqttbroker_pvc_storage_class

Storage class for IoT MQTT broker (MessageSight) persistent volumes, which store message queues, broker state, and retained messages — any valid storage class name in your cluster that supports ReadWriteOnce (RWO) access mode.

- **Optional** — always required when `mas_app_settings_iot_deployment_size` is not `dev`
- Environment Variable: `MAS_APP_SETTINGS_IOT_MQTTBROKER_PVC_STORAGE_CLASS`
- Default: Auto-selected from available ReadWriteOnce (RWO) storage classes in the cluster

Set explicitly when you have multiple RWO storage classes, when auto-selection doesn't choose your preferred class, or when you need specific performance characteristics for MQTT message handling. Application support: IoT 8.3+ — verify with `oc get storageclass` before deployment.

#### mas_app_settings_iot_mqttbroker_pvc_size

Size of the persistent volume for the IoT MQTT broker (MessageSight) component — any valid Kubernetes storage size (e.g., `50Gi`, `100Gi`, `200Gi`, `500Gi`).

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_IOT_MQTTBROKER_PVC_SIZE`
- Default: `100Gi`

Increase for production environments with many connected devices, high message volumes, long message retention, or devices that frequently disconnect and require message queuing; use the default for development, testing, or moderate device counts. Application support: IoT 8.3+. Insufficient storage may cause message loss, device connection failures, or broker instability — monitor storage usage to prevent message queue overflow.

**IoT pod templates**: when `mas_app_id` is `iot`, [`mas_pod_templates_dir`](#mas_pod_templates_dir) is used with configuration files named `ibm-mas-iot-iot.yml`, `ibm-mas-iot-actions.yml`, `ibm-mas-iot-auth.yml`, `ibm-mas-iot-datapower.yml`, `ibm-mas-iot-devops.yml`, `ibm-mas-iot-dm.yml`, `ibm-mas-iot-dsc.yml`, `ibm-mas-iot-edgeconfig.yml`, `ibm-mas-iot-fpl.yml`, `ibm-mas-iot-guardian.yml`, `ibm-mas-iot-mbgx.yml`, `ibm-mas-iot-mfgx.yml`, `ibm-mas-iot-monitor.yml`, `ibm-mas-iot-orgmgmt.yml`, `ibm-mas-iot-provision.yml`, `ibm-mas-iot-registry.yml`, `ibm-mas-iot-state.yml`, and `ibm-mas-iot-webui.yml`. The content of each file should be the YAML block you wish to be inserted into the IoT CR: `ibm-mas-iot-iot.yml` is inserted into the main IoT CR `spec -> podTemplates`, whereas the component ones (e.g., `ibm-mas-iot-actions.yml`) go under `spec -> components -> {componentName} -> podTemplates`. The ibm-mas-iot operator then passes this on to the corresponding component CR when available. See the [BestEfforts reference configuration in the MAS CLI](https://github.com/ibm-mas/cli/blob/master/image/cli/mascli/templates/pod-templates/best-effort/ibm-mas-iot-actions.yml) for an example of one of the components (actions), and [Customizing Pod Templates](https://www.ibm.com/docs/en/mas-cd/continuous-delivery?topic=configuring-customizing-workloads) in the product documentation for full documentation of the supported options.

### Manage Configuration

**Manage pod templates**: when `mas_app_id` is `manage`, [`mas_pod_templates_dir`](#mas_pod_templates_dir) is used with a configuration file named `ibm-mas-manage-manageapp.yml`. The content of the file should be the YAML block you wish to be inserted into the ManageApp CR: it is inserted into the ManageApp CR `spec -> podTemplates`, and the ibm-mas-manage operator then passes this on to the corresponding deployments when available. For full documentation of the supported options refer to [Customizing Pod Templates](https://www.ibm.com/docs/en/mas-cd/continuous-delivery?topic=configuring-customizing-workloads) in the product documentation.

#### mas_appws_upgrade_type

Upgrade strategy for Manage workspace database schema updates — `regularUpgrade` (standard upgrade with full system downtime) or `onlineUpgrade` (minimized downtime, requires additional resources and time).

- **Optional**
- Environment Variable: `MAS_APPWS_UPGRADE_TYPE`
- Default: `regularUpgrade`

`regularUpgrade` gives a shorter upgrade time but requires full system downtime; `onlineUpgrade` takes longer but minimizes downtime and requires additional database resources during the upgrade. Applies to Manage application upgrades only — online upgrades require careful planning. For full documentation of upgrade types and requirements, refer to the [Manage Upgrade information](https://www.ibm.com/docs/en/masv-and-l/cd?topic=database-reducing-system-downtime) in the product documentation.

### Monitor Configuration

#### mas_app_settings_monitor_deployment_size

Deployment size profile for MAS Monitor, which determines resource allocations and scaling characteristics — `dev`, `small`, or `large`.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_MONITOR_DEPLOYMENT_SIZE`
- Default: `dev`

`dev` allocates minimal resources suitable for development only, `small` moderate resources suitable for small to medium production deployments, and `large` maximum resources suitable for large-scale production deployments with extensive monitoring. Application support: Monitor 8.6+. Ensure your cluster has sufficient resources for the selected size — this cannot be easily changed after deployment without reinstallation.

### Predict Configuration

#### mas_app_settings_predict_deployment_size

Deployment size profile for MAS Predict, which determines resource allocations and scaling characteristics — `developer` (1 replica, no high availability), `small` (2 replicas, basic high availability), `medium` (3 replicas), or `large` (higher replica count, if supported).

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_PREDICT_DEPLOYMENT_SIZE` (the legacy `PREDICT_DEPLOYMENT_SIZE` is also still supported)
- Default: `small`

Used in the default Predict application spec; it has no effect when you provide your own [`mas_app_spec`](#mas_app_spec). The `developer` size is suitable only for development and testing. The workspace-level size is set separately with [`mas_appws_settings_deployment_size`](../suite_app_config/README.md#mas_appws_settings_deployment_size).

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
