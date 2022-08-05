suite_app_config
================

This role is used to configure specific components of the application workspace after the application has been installed in the Maximo Application Suite.

Role Variables
--------------

### mas_instance_id
Defines the instance id that was used for the MAS installation

### mas_app_id
Defines the kind of application that is intended for installation such as `assist`, `health`, `iot`, `manage`, `monitor`, `mso`, `predict`, or `safety`

### mas_workspace_id
MAS application workspace to use to configure app components

### mas_config_dir
Optional. Local directory where generated resource definitions are saved into. It is used by current role to retrieve the id of the analytics project eventually created by [cp4d_service](cp4d_service.md) role and then configure it into Health & Predict - Utilities resource.

- Optional, only supported when `mas_app_id` = `hputilities` and `cpd_ws_project_name` is informed.
- Environment Variable: `MAS_CONFIG_DIR`
- Default Value: None

### mas_appws_components
Defines the app components and versions to configure in the application workspace. Takes the form of key=value pairs seperated by a comma i.e. To install health within Manage set `base=latest,health=latest`

- Environment Variable: `MAS_APPWS_COMPONENTS`
- Default:
  For Manage the default is:
    `base=latest`

  For Health (standalone) the default is:
    `health=latest`

### mas_app_ws_spec
Optional.  The application workspace deployment spec used to configure various aspects of the application workspace configuration. Note that use of this will override anything set in `mas_appws_components`

- Environment Variable: MAS_APP_WS_SPEC
- Default: defaults are specified in `vars/defaultspecs/{{mas_app_id}}.yml`

Role Variables - Health & Predict Utilities
---------------------------------------------

### cpd_ws_project_id
Optional. It is the id of the analytics project created in Watson Studio and used to configure `hputilities` application.

- Only supported when `mas_app_id` = `hputilities`
- Environment Variable: CPD_WS_PROJECT_ID
- Default: None

### cpd_ws_project_name
Optional. It specifies the name of the file in `mas_config_dir` where the id of the analytics project is saved.

- Only supported when `mas_app_id` = `hputilities` and `mas_config_dir` is informed.
- Environment Variable: CPD_WS_PROJECT_NAME
- Default Value: `wsl-mas-${mas_instance_id}-hputilities`

Role Variables - Manage
---------------------------------------------

### mas_app_settings_aio_flag
Optional. Flag indicating if Asset Investment Optimization (AIO) resource must be loaded or not. It can be loaded only when Optimizer application is installed.

- Only supported when Optimizer application is installed.
- Environment Variable: MAS_APP_SETTINGS_AIO_FLAG
- Default: `true`

### mas_app_settings_db2_schema
Optional. Name of the schema where Manage database lives in.

- Environment Variable: MAS_APP_SETTINGS_DB2_SCHEMA') | 
- Default: `maximo`

### mas_app_settings_demodata
Optional. Flag indicating if manage demodata should be loaded or not.

- Environment Variable: MAS_APP_SETTINGS_DEMODATA
- Default: `false` (do not load demodata)


Example Playbook
----------------

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

    mas_app_ws_spec:
      bindings:
        jdbc: "{{ mas_appws_jdbc_binding | default( 'system' , true) }}"

  roles:
    - ibm.mas_devops.suite_app_config
```

License
-------

EPL-2.0
