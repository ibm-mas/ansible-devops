gencfg_watsonstudio
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

### CPD_ADMIN_USERNAME
Defines the username that is used for the WatsonStudio configure in MAS installation

- Environment Variable: `CPD_ADMIN_USERNAME`
- Default: None
- 
### CPD_ADMIN_PASSWORD
Defines the password that is used to connect to WatsonStudio in MAS installation

- Environment Variable: `CPD_ADMIN_PASSWORD`
- Default: None
- 
### CPD_URL
Defines the url that is used to connect to WatsonStudio in MAS installation

- Environment Variable: `CPD_URL`
- Default: None
- 

### custom_labels
List of comma separated key=value pairs for setting custom labels on instance specific resources.

- Optional
- Environment Variable: `CUSTOM_LABELS`
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
