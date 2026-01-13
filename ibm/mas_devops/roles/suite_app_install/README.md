# suite_app_install

This role is used to install a specified application in Maximo Application Suite.

## Role Variables

### General

#### mas_instance_id
Defines the instance id that was used for the MAS installation.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

#### mas_app_id
Defines the kind of application that is intended for installation such as `assist`, `iot`, `facilities`, `manage`, `monitor`, `predict`, or `visualinspection`.

- **Optional**
- Environment Variable: `MAS_APP_ID`
- Default: None

#### mas_app_catalog_source
Defines the catalog to be used to install the MAS app. You can set it to `ibm-operator-catalog` for release install or `ibm-mas-{mas_app_id}-operators` for development, where {mas_app_id} will be manage for the Manage and Health app installation, for example.

- **Optional**
- Environment Variable: `MAS_APP_CATALOG_SOURCE`
- Default: `ibm-operator-catalog`

#### mas_app_channel
Defines which channel of the MAS application to subscribe to.

- **Required**
- Environment Variable: `MAS_APP_CHANNEL`
- Default: None

#### custom_labels
List of comma separated key=value pairs for setting custom labels on instance specific resources.

- **Optional**
- Environment Variable: `CUSTOM_LABELS`
- Default: None

### Pre-Release Support

#### artifactory_username
Required when using this role for development versions of the MAS application.

- **Optional**
- Environment Variable: `ARTIFACTORY_USERNAME`
- Default: None

#### artifactory_token
Required when using this role for development versions of the MAS application.

- **Optional**
- Environment Variable: `ARTIFACTORY_TOKEN`
- Default: None

#### mas_entitlement_username
Username for entitled registry. This username will be used to create the image pull secret. Set to `cp` when installing release or use your `w3Id` for dev.

- **Optional**
- Environment Variable: `MAS_ENTITLEMENT_USERNAME`
- Default: None

#### mas_entitlement_key
API Key for entitled registry. This password will be used to create the image pull secret. Set to with IBM entitlement key when installing release or use your artifactory `apikey` for dev.

- **Optional**
- Environment Variable: `MAS_ENTITLEMENT_KEY`
- Default: None

### Application Configuration

#### mas_app_spec
Use of mas_app_spec will override all other application configuration variables.

- **Optional**
- Environment Variable: None
- Default: defaults are specified in `vars/defaultspecs/{{mas_app_id}}.yml`

#### mas_app_bindings_jdbc
Set the binding scope for the application's JDBC binding (`system` or `application`).

- **Optional**
- Environment Variable: `MAS_APP_BINDINGS_JDBC`
- Default: `system`

#### mas_app_plan
Defines what plan will be used in application install. Application Support: Optimizer v8.2+ supports `full` and `limited`, defaults to `full`.

- **Optional**
- Environment Variable: `MAS_APP_PLAN`
- Default: Application-specific

#### mas_pod_templates_dir
Provide the directory where supported pod templates configuration files are defined. For application specifics read the information for `mas_pod_templates_dir` below.

- **Optional**
- Environment Variable: `MAS_POD_TEMPLATES_DIR`
- Default: None

### Visual Inspection Configuration

#### mas_app_settings_visualinspection_storage_class
Storage class used for user data. This must support ReadWriteMany(RWX).

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_VISUALINSPECTION_STORAGE_CLASS`
- Default: Auto-selected from storage classes installed in the cluster

#### mas_app_settings_visualinspection_storage_size
Size of data persistent volume.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_VISUALINSPECTION_STORAGE_SIZE`
- Default: `100Gi`

### IoT Configuration

#### mas_app_settings_iot_deployment_size
The IoT deployment size, one of `dev`, `small` or `large`. Application Support: IoT 8.6+.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_IOT_DEPLOYMENT_SIZE`
- Default: `small`

#### mas_app_settings_iot_fpl_pvc_storage_class
The persistent volume storage class used by the iot fpl component for transient state storage. The storage class can be used to dynamically provision a persistent volume with access mode RWO (ReadWriteOnce). Application Support: IoT 8.6+.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_IOT_FPL_PVC_STORAGE_CLASS`
- Default: Auto-selected from storage classes installed in the cluster

#### mas_app_settings_iot_fpl_router_pvc_size
The persistent volume size used by the iot fpl pipeline router for transient state storage. Application Support: IoT 8.6+.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_IOT_FPL_ROUTER_PVC_SIZE`
- Default: `100Gi`

#### mas_app_settings_iot_fpl_executor_pvc_size
The persistent volume size used by the iot fpl pipeline router for transient state storage. Application Support: IoT 8.6+.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_IOT_FPL_EXECUTOR_PVC_SIZE`
- Default: `100Gi`

#### mas_app_settings_iot_mqttbroker_pvc_storage_class
The persistent volume storage class used by the iot mqtt broker (messagesight). The storage class can be used to dynamically provision a persistent volume with access mode RWO (ReadWriteOnce). Application Support: IoT 8.3+.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_IOT_MQTTBROKER_PVC_STORAGE_CLASS`
- Default: Auto-selected from storage classes installed in the cluster, if a default compatible one is found

#### mas_app_settings_iot_mqttbroker_pvc_size
The persistent volume size used by the iot mqtt broker (messagesight). Application Support: IoT 8.3+.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_IOT_MQTTBROKER_PVC_SIZE`
- Default: `100Gi`

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
Provide the upgrade type to be used by Manage Workspace. The value of the environment variable should be either `regularUpgrade` or `onlineUpgrade`. For full documentation of the upgrade types refer to the [Manage Upgrade information](https://www.ibm.com/docs/en/masv-and-l/cd?topic=database-reducing-system-downtime) in the product documentation.

- **Optional**
- Environment Variable: `MAS_APPWS_UPGRADE_TYPE`
- Default: `regularUpgrade`

### Monitor Configuration

#### mas_app_settings_monitor_deployment_size
The Monitor deployment size, one of `dev`, `small` or `large`. Application Support: Monitor 8.6+.

- **Optional**
- Environment Variable: `MAS_APP_SETTINGS_MONITOR_DEPLOYMENT_SIZE`
- Default: `dev`

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
