suite_config
============

This role is used to configure WatsonStudio in Maximo Application Suite.

Role Variables
--------------

### mas_instance_id
Providing this and `mas_config_dir` will instruct the role to generate a WatsonStudioCfg template that can be used to configure MAS to connect to WatsonStudio.

- Environment Variable: `MAS_INSTANCE_ID`
- Default: None
- 
### mas_workspace_id
This is only used when both `mas_config_dir` and `mas_instance_id` are set, and `mas_config_scope` is set to either `ws` or `wsapp`

- Environment Variable: `MAS_WORKSPACE_ID`
- Default: None

### ws_username
Defines the username that is used for the WatsonStudio configure in MAS installation

- Environment Variable: `WS_USER`
- Default: None
- 
### ws_password
Defines the password that is used to connect to WatsonStudio in MAS installation

- Environment Variable: `WS_PASSWORD`
- Default: None
- 
### ws_url
Defines the url that is used to connect to WatsonStudio in MAS installation

- Environment Variable: `WS_URL`
- Default: None
- 
### ws_pem_file
Defines the location of the pem file used for WatsonStudio connection in MAS installation

- Environment Variable: `WS_CERT_LOCAL_FILE`
- Default: None

Example Playbook
----------------

```yaml
---

- hosts: localhost
  any_errors_fatal: true  
  roles:
    - ibm.mas_devops.gencfg_watsonstudio
```

License
-------

EPL-2.0
