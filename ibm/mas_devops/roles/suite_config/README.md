# suite_config

This role applies configuration files to a Maximo Application Suite installation. It searches for YAML configuration files in a specified directory and applies them to the cluster using the Kubernetes API. This is typically used after installing MAS to configure various aspects of the suite such as workspace configurations, JDBC configurations, SMTP settings, and other custom resources.

## Role Variables

### mas_instance_id
The instance ID of the MAS installation to configure. This is used to target the correct MAS instance when applying configurations.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

### mas_config_dir
Directory containing configuration files (`*.yaml` and `*.yml`) to be applied to the MAS installation. The role will recursively search this directory for YAML files and apply them to the cluster. Files matching the pattern `jdbc-aiservice*.yml` or `jdbc-aiservice*.yaml` are excluded from processing.

- **Required**
- Environment Variable: `MAS_CONFIG_DIR`
- Default: None

## Example Playbook

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: "inst1"
    mas_config_dir: "/home/user/masconfig"

  roles:
    - ibm.mas_devops.suite_config
```

## License

EPL-2.0
