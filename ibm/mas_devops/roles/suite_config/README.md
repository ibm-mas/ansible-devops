# suite_config

This role applies configuration files to a Maximo Application Suite installation. It searches for YAML configuration files in a specified directory and applies them to the cluster using the Kubernetes API. This is typically used after installing MAS to configure various aspects of the suite such as workspace configurations, JDBC configurations, SMTP settings, and other custom resources.

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`mas_instance_id`](#mas_instance_id) | Yes | None |
| [`mas_config_dir`](#mas_config_dir) | Yes | None |

### Instance Configuration

#### mas_instance_id

Unique identifier for the MAS instance to apply configurations to (lowercase alphanumeric, 3-12 characters, e.g. `prod`, `dev`, `inst1`).

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

Must match the instance ID used during MAS core installation. Configurations are applied to the `mas-{mas_instance_id}-core` namespace and related application namespaces; an incorrect instance ID will apply configurations to the wrong instance or fail if it doesn't exist.

#### mas_config_dir

Local directory path containing MAS configuration YAML files to apply to the cluster.

- **Required**
- Environment Variable: `MAS_CONFIG_DIR`
- Default: None

The role recursively searches this directory for all `*.yaml` and `*.yml` files and applies them to the cluster. Use the same directory where dependency roles (mongodb, db2, sls) generate their configuration files — typically a consistent location across all MAS setup roles such as `~/masconfig`. Files matching `jdbc-aiservice*.yml` / `jdbc-aiservice*.yaml` are automatically excluded, as AI Service JDBC configurations require special handling. Ensure the directory contains only Kubernetes resources intended for this MAS instance.

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
