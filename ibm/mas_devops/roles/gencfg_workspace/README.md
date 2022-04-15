gencfg_workspace
============
This role is used to generate a Workspace custom resource that can be applied to Maximo Application Suite manually, or using the `suite_config` role.  The configuration will be saved to local disk in the directory specified by the `mas_config_dir` variable.

Role Variables
--------------
### mas_instance_id
Required. The MAS instance ID that the workspace will be used in

- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### mas_workspace_id
Required.  The ID of the workspace

- Environment Variable: `MAS_WORKSPACE_ID`
- Default Value: None

### mas_workspace_name
Required.  The display name for the workspace

- Environment Variable: `MAS_WORKSPACE_NAME`
- Default Value: None

### mas_config_dir
Required. The directory to save the configuration to.

- Environment Variable: `MAS_CONFIG_DIR`
- Default Value: None


Example Playbook
----------------

```yaml
---
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: "inst1"
    mas_workspace_id: "masdev"
    mas_workspace_name: "MAS Development"

    mas_config_dir: "/home/david/masconfig/inst1"

  roles:
    - ibm.mas_devops.gencfg_workspace


```

License
-------

EPL-2.0
