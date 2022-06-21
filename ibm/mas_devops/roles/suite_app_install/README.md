suite_app_install
=================

This role is used to install a specified application in Maximo Application Suite.

Role Variables
--------------
- `mas_app_catalog_source` Defines the catalog to be used to install the MAS app. You can set it to ibm-operator-catalog for release install or ibm-mas-{mas_app_id}-operators for development, where {mas_app_id} will be manage for the Manage and Health app installation, for example.
- `artifactory_username` Required when using this role for development versions of the MAS application
- `artifactory_apikey` Required when using this role for development versions of the MAS application
- `mas_app_channel` Defines which channel of the MAS application to subscribe to. Set to `8.x` when installing released version
- `mas_instance_id` Defines the instance id that was used for the MAS installation
- `mas_icr_cp` Defines the entitled registry from the images should be pulled from. Set this to `cp.icr.io/cp` when installing release version of MAS or `wiotp-docker-local.artifactory.swg-devops.com` for dev
- `mas_entitlement_username` Username for entitled registry. This username will be used to create the image pull secret. Set to `cp` when installing release or use your `w3Id` for dev
- `mas_entitlement_key` API Key for entitled registry. This password will be used to create the image pull secret. Set to with IBM entitlement key when installing release or use your artifactory `apikey` for dev.
- `mas_app_id` Defines the kind of application that is intended for installation such as `assist`, `health`, `iot`, `manage`, `monitor`, `mso`, `predict`, or `safety`
- `mas_app_upgrade_strategy` Defines the Upgrade strategy for the MAS Application Operator. Default is set to Automatic

### mas_app_plan
Optional. Defines what plan will be used in application install.

- Environment Variable: `MAS_APP_PLAN`
- Default: Application-specific, see details below.
- Application Support:
  - Optimizer v8.2+: `full` and `limited` are supported, defaults to `full`

### mas_app_spec
Optional. The application deployment spec used to configure different aspects of the application deployment configuration.

- Environment Variable: None
- Default: defaults are specified in vars/defaultspecs/{{mas_app_id}}.yml


Example Playbook
----------------

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

    # MAS configuration - IBM container registry configuration
    mas_icr_cp: "{{ lookup('env', 'MAS_ICR_CP') | default('cp.icr.io/cp', true) }}"

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
-------

EPL-2.0
