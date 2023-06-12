suite_app_install
===============================================================================

This role is used to install a specified application in Maximo Application Suite.


Role Variables - General
-------------------------------------------------------------------------------
### mas_instance_id
Defines the instance id that was used for the MAS installation

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

### mas_app_id
Defines the kind of application that is intended for installation such as `assist`, `health`, `iot`, `manage`, `monitor`, `mso`, `predict`, or `safety`

- Optional
- Environment Variable: `MAS_APP_ID`
- Default: None

### mas_app_catalog_source
Defines the catalog to be used to install the MAS app. You can set it to ibm-operator-catalog for release install or ibm-mas-{mas_app_id}-operators for development, where {mas_app_id} will be manage for the Manage and Health app installation, for example.

- Optional
- Environment Variable: `MAS_APP_CATALOG_SOURCE`
- Default: `ibm-operator-catalog`

### mas_app_channel
Defines which channel of the MAS application to subscribe to

- **Required**
- Environment Variable: `MAS_APP_CHANNEL`
- Default: None

### mas_app_upgrade_strategy
Defines the Upgrade strategy for the MAS Application Operator. Default is set to Automatic

- Optional
- Environment Variable: `MAS_APP_UPGRADE_STRATEGY`
- Default: None

### custom_labels
Optional. List of comma separated key=value pairs for setting custom labels on instance specific resources.

- Environment Variable: `CUSTOM_LABELS`
- Default: None


Role Variables - Pre-Release Support
-------------------------------------------------------------------------------
### artifactory_username
Required when using this role for development versions of the MAS application.

- Optional
- Environment Variable: `ARTIFACTORY_USERNAME`
- Default: None

### artifactory_token
Required when using this role for development versions of the MAS application

- Optional
- Environment Variable: `ARTIFACTORY_TOKEN`
- Default: None

### mas_entitlement_username
Username for entitled registry. This username will be used to create the image pull secret. Set to `cp` when installing release or use your `w3Id` for dev

- Optional
- Environment Variable: `MAS_ENTITLEMENT_USERNAME`
- Default: None

### mas_entitlement_key
API Key for entitled registry. This password will be used to create the image pull secret. Set to with IBM entitlement key when installing release or use your artifactory `apikey` for dev.

- Optional
- Environment Variable: `MAS_ENTITLEMENT_KEY`
- Default: None


Role Variables - Application Configuration
-------------------------------------------------------------------------------
### mas_app_spec
Use of mas_app_spec will override all other application configuration variables.

- Optional
- Environment Variable: None
- Default: defaults are specified in `vars/defaultspecs/{{mas_app_id}}.yml`

### mas_app_bindings_jdbc
Set the binding scope for the application's JDBC binding (`system` or `application`)

- Optional
- Environment Variable: `MAS_APP_BINDINGS_JDBC`
- Default: `system`

### mas_app_plan
Optional. Defines what plan will be used in application install.

- Environment Variable: `MAS_APP_PLAN`
- Default: Application-specific, see details below.
- Application Support:
  - Optimizer v8.2+: `full` and `limited` are supported, defaults to `full`


Role Variables - Visual Inspection Configuration
-------------------------------------------------------------------------------
### mas_app_settings_visualinspection_storage_class
Optional - Storage class used for user data. This must support ReadWriteMany

- Environment Variable: `MAS_APP_SETTINGS_VISUALINSPECTION_STORAGE_CLASS`
- Default: Auto-selected from storage classes installed in the cluster.

### mas_app_settings_visualinspection_storage_size
Optional. Size of data persistent volume.

- Environment Variable: `MAS_APP_SETTINGS_VISUALINSPECTION_STORAGE_SIZE`
- Default: `100Gi`


Role Variables - IoT Configuration
-------------------------------------------------------------------------------
### mas_app_settings_iot_deployment_size
Optional, The IoT deployment size, one of `dev`, `small` or `large`.

- Environment Variable: `MAS_APP_SETTINGS_IOT_DEPLOYMENT_SIZE`
- Default: `small`
- Application Support:
  - IoT 8.6+

### mas_app_settings_iot_fpl_pvc_storage_class
Optional. The persistent volume storage class used by the iot fpl component for transient state storage

- Environment Variable: `MAS_APP_SETTINGS_IOT_FPL_PVC_STORAGE_CLASS`
- Default: Auto-selected from storage classes installed in the cluster.
- Application Support:
  - IoT 8.6+

### mas_app_settings_iot_fpl_router_pvc_size
Optional. The persistent volume size used by the iot fpl pipeline router for transient state storage

- Environment Variable: `MAS_APP_SETTINGS_IOT_FPL_ROUTER_PVC_SIZE`
- Default: 100Gi.
- Application Support:
  - IoT 8.6+

### mas_app_settings_iot_fpl_executor_pvc_size
Optional. The persistent volume size used by the iot fpl pipeline router for transient state storage

- Environment Variable: `MAS_APP_SETTINGS_IOT_FPL_EXECUTOR_PVC_SIZE`
- Default: 100Gi.
- Application Support:
  - IoT 8.6+

### mas_app_settings_iot_mqttbroker_pvc_storage_class
Optional. The persistent volume storage class used by the iot mqtt broker (messagesight)

- Environment Variable: `MAS_APP_SETTINGS_IOT_MQTTBROKER_PVC_STORAGE_CLASS`
- Default: Auto-selected from storage classes installed in the cluster, if a default compatible one is found.
- Application Support:
  - IoT 8.3+

### mas_app_settings_iot_mqttbroker_pvc_size
Optional. The persistent volume size used by the iot mqtt broker (messagesight)

- Environment Variable: `MAS_APP_SETTINGS_IOT_MQTTBROKER_PVC_SIZE`
- Default: 100Gi.
- Application Support:
  - IoT 8.3+


Role Variables - Monitor Configuration
-------------------------------------------------------------------------------
### mas_app_settings_monitor_deployment_size
Optional, The Monitor deployment size, one of `dev`, `small` or `large`.

- Environment Variable: `MAS_APP_SETTINGS_MONITOR_DEPLOYMENT_SIZE`
- Default: `dev`
- Application Support:
  - Monitor 8.6+


Example Playbook
-------------------------------------------------------------------------------

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

    # Determine MAS Operator Upgrade Strategy Manual | Automatic
    mas_app_upgrade_strategy: "{{ lookup('env', 'MAS_APP_UPGRADE_STRATEGY') | default('Manual', true) }}"

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

License
-------------------------------------------------------------------------------

EPL-2.0
