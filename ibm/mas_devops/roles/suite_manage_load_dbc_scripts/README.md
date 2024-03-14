suite_manage_load_dbc_scripts
================

This role allows to load and execute one or more ad-hoc DBC script files into Manage/Health server. Only `dbc` format files will be accepted. 
The role will assert if each script executed successfully and fail in case of errors while locating the DBC scripts or executing them against the Manage/Health server.

Role Variables
--------------

### mas_instance_id
Required. Defines the instance id that was used for the MAS installation. It is used to lookup the Manage/Health namespace.
- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### mas_app_id
Required.
- Environment Variable: `MAS_APP_ID`
- One of [`health`, `manage`]
- Default Value: None

### dbc_script_path_local
Optional. Defines the local path/folder where the DBC script files should be located in order to be loaded onto the Manage/Health server.

- Environment Variable: `DBC_SCRIPT_PATH_LOCAL`
- Default Value: `suite_manage_load_dbc_scripts/files`

Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: "{{ lookup('env', 'MAS_INSTANCE_ID') }}"
    dbc_script_path_local: "{{ lookup('env', 'DBC_SCRIPT_PATH_LOCAL') }}"
  roles:
    - ibm.mas_devops.suite_manage_load_dbc_scripts
```

License
-------

EPL-2.0
