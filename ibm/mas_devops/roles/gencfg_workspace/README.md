# gencfg_workspace

This role generates a Workspace custom resource configuration file for Maximo Application Suite. The generated configuration can be applied manually or automatically using the `suite_config` role. The configuration file is saved to local disk in the directory specified by `mas_config_dir`.

!!! tip
    Workspaces are logical containers in MAS that isolate data and configurations for different business units, environments, or use cases. Each workspace can have its own applications, users, and data.

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`mas_instance_id`](#mas_instance_id) | Yes | None |
| [`mas_workspace_id`](#mas_workspace_id) | Yes | None |
| [`mas_workspace_name`](#mas_workspace_name) | Yes | None |
| [`mas_config_dir`](#mas_config_dir) | Yes | None |
| [`custom_labels`](#custom_labels) | No | None |

### Workspace Definition

#### mas_instance_id
MAS instance identifier the workspace will be associated with — a lowercase alphanumeric string, 3-12 characters (e.g. `prod`, `dev`, `masinst1`), matching the instance ID from the MAS installation.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

The generated configuration file is named and structured for this specific instance. Multiple workspaces can exist within a single MAS instance, each with its own ID and configuration.

#### mas_workspace_id
Unique technical identifier for the workspace within the MAS instance — a lowercase alphanumeric string, typically 3-12 characters (e.g. `prod`, `dev`, `masdev`, `qa`).

- **Required**
- Environment Variable: `MAS_WORKSPACE_ID`
- Default: None

This ID is used in URLs (e.g. `https://instance.mas.com/masdev`), API calls, Kubernetes resource names, and the generated filename. Choose a meaningful ID that reflects the workspace purpose — it cannot be changed after workspace creation.

#### mas_workspace_name
Human-readable display name for the workspace, shown in the MAS user interface — any string, typically 3-50 characters (e.g. `Production`, `Development`, `MAS Development`, `QA Environment`).

- **Required**
- Environment Variable: `MAS_WORKSPACE_NAME`
- Default: None

Unlike the workspace ID, this name can include spaces and special characters, and it can be changed after creation if needed.

### Configuration Output

#### mas_config_dir
Local directory where the generated workspace configuration YAML file is written — a valid, writable local filesystem path such as `/home/user/masconfig` or `~/masconfig/inst1`.

- **Required**
- Environment Variable: `MAS_CONFIG_DIR`
- Default: None

The directory is created if it doesn't exist. The generated file can then be applied manually with `oc apply` or automatically with the `suite_config` role; organizing configs by instance ID (e.g. `/masconfig/inst1/`, `/masconfig/inst2/`) keeps things clear.

#### custom_labels
Custom Kubernetes labels to add to the generated workspace resources — comma-separated key=value pairs (e.g. `env=prod,team=operations,cost-center=12345`).

- **Optional**
- Environment Variable: `CUSTOM_LABELS`
- Default: None

Useful for resource organization and filtering, cost allocation and tracking, automation and policy enforcement, and organizational categorization — common in multi-tenant or managed environments. Labels must follow Kubernetes naming conventions (alphanumeric, hyphens, dots, max 63 chars per segment); common uses include environment tags, team ownership, and cost center tracking.

## Example Playbook

```yaml
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

## License

EPL-2.0
