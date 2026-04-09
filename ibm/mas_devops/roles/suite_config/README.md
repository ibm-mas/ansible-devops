# suite_config

This role applies configuration files to a Maximo Application Suite installation. It searches for YAML configuration files in a specified directory and applies them to the cluster using the Kubernetes API. This is typically used after installing MAS to configure various aspects of the suite such as workspace configurations, JDBC configurations, SMTP settings, and other custom resources.

## Role Variables

### mas_instance_id
Unique identifier for the MAS instance to apply configurations to.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

**Purpose**: Identifies which MAS instance to target when applying configuration files. This ensures configurations are applied to the correct MAS installation when multiple instances exist in the cluster.

**When to use**:
- Always required for any MAS configuration operation
- Must match the instance ID used during MAS core installation
- Use the same value across all configuration operations for a given MAS instance

**Valid values**: Lowercase alphanumeric string, 3-12 characters (e.g., `prod`, `dev`, `inst1`)

**Impact**: Configurations will be applied to the namespace `mas-{mas_instance_id}-core` and related application namespaces. An incorrect instance ID will cause configurations to be applied to the wrong MAS instance or fail if the instance doesn't exist.

**Related variables**: Works with `mas_config_dir` to determine which configuration files to apply.

**Note**: This must match the instance ID used when installing MAS core. Verify the instance ID before applying configurations to avoid misconfiguration.

### mas_config_dir
Local directory path containing MAS configuration YAML files to apply to the cluster.

- **Required**
- Environment Variable: `MAS_CONFIG_DIR`
- Default: None

**Purpose**: Specifies the directory containing MAS configuration files (MongoCfg, JdbcCfg, BASCfg, SLSCfg, etc.) that will be automatically applied to configure the MAS instance. This enables automated configuration of MAS dependencies and settings.

**When to use**:
- Always required when using this role to apply configurations
- Use the same directory where dependency roles (mongodb, db2, sls) generate their configuration files
- Typically set to a consistent location across all MAS setup roles (e.g., `/home/user/masconfig`)

**Valid values**: Any valid local filesystem path containing YAML configuration files (e.g., `/home/user/masconfig`, `~/masconfig`, `./config`)

**Impact**: The role recursively searches this directory for all `*.yaml` and `*.yml` files and applies them to the cluster using `oc apply`. Invalid YAML files or incorrect configurations will cause the role to fail. Files matching `jdbc-aiservice*.yml` or `jdbc-aiservice*.yaml` patterns are automatically excluded from processing.

**Related variables**: 
- `mas_instance_id`: Determines which MAS instance receives the configurations
- Used by dependency roles (mongodb, db2, sls) as output directory for generated configs

**Note**: Ensure all YAML files in this directory are valid Kubernetes resources intended for this MAS instance. The role applies all matching files, so remove or move any files not intended for application. AI Service JDBC configurations are excluded as they require special handling.

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
