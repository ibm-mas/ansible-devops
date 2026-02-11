# gencfg_workspace

This role generates a Workspace custom resource configuration file for Maximo Application Suite. The generated configuration can be applied manually or automatically using the `suite_config` role. The configuration file is saved to local disk in the directory specified by `mas_config_dir`.

!!! tip
    Workspaces are logical containers in MAS that isolate data and configurations for different business units, environments, or use cases. Each workspace can have its own applications, users, and data.

## Role Variables

### mas_instance_id
MAS instance identifier for the workspace.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

**Purpose**: Identifies which MAS instance the workspace configuration will be generated for. The workspace will be associated with this instance.

**When to use**:
- Always required for workspace configuration generation
- Must match the instance ID from MAS installation
- Used to create instance-specific workspace configurations

**Valid values**: Lowercase alphanumeric string, 3-12 characters (e.g., `prod`, `dev`, `masinst1`)

**Impact**: Determines which MAS instance the workspace belongs to. The generated configuration file will be named and structured for this specific instance.

**Related variables**:
- `mas_workspace_id`: Workspace identifier within this instance
- `mas_config_dir`: Directory where instance-specific config is saved

**Note**: Multiple workspaces can exist within a single MAS instance, each with its own ID and configuration.

### mas_workspace_id
Workspace identifier.

- **Required**
- Environment Variable: `MAS_WORKSPACE_ID`
- Default: None

**Purpose**: Defines the unique identifier for the workspace within the MAS instance. This ID is used in URLs, API calls, and resource names.

**When to use**:
- Always required for workspace configuration
- Must be unique within the MAS instance
- Used as the technical identifier for the workspace

**Valid values**: Lowercase alphanumeric string, typically 3-12 characters (e.g., `prod`, `dev`, `masdev`, `qa`)

**Impact**: Determines the workspace's technical identifier. This ID appears in URLs (e.g., `https://instance.mas.com/masdev`) and Kubernetes resource names.

**Related variables**:
- `mas_instance_id`: Parent instance for this workspace
- `mas_workspace_name`: Human-readable display name

**Note**: Choose a meaningful ID that reflects the workspace purpose (e.g., `prod`, `dev`, `qa`). The ID cannot be changed after workspace creation.

### mas_workspace_name
Workspace display name.

- **Required**
- Environment Variable: `MAS_WORKSPACE_NAME`
- Default: None

**Purpose**: Defines the human-readable display name for the workspace shown in the MAS user interface.

**When to use**:
- Always required for workspace configuration
- Should be descriptive and user-friendly
- Displayed in MAS UI and documentation

**Valid values**: Any string, typically 3-50 characters (e.g., `Production`, `Development`, `MAS Development`, `QA Environment`)

**Impact**: Determines how the workspace appears to users in the MAS interface. Unlike the workspace ID, this name can include spaces and special characters.

**Related variables**:
- `mas_workspace_id`: Technical identifier for this workspace
- `mas_instance_id`: Parent instance

**Note**: Use a clear, descriptive name that helps users identify the workspace purpose. This name can be changed after creation if needed.

### mas_config_dir
Configuration output directory.

- **Required**
- Environment Variable: `MAS_CONFIG_DIR`
- Default: None

**Purpose**: Specifies the local directory path where the generated workspace configuration file will be saved.

**When to use**:
- Always required for configuration generation
- Should be a writable directory path
- Typically organized by instance ID

**Valid values**: Valid local filesystem path (e.g., `/home/user/masconfig`, `~/masconfig/inst1`)

**Impact**: Determines where the workspace configuration YAML file is written. The file can then be applied manually with `oc apply` or automatically with the `suite_config` role.

**Related variables**:
- `mas_instance_id`: Used to organize configs by instance
- `mas_workspace_id`: Used in the generated filename

**Note**: The directory will be created if it doesn't exist. Organize configs by instance ID for clarity (e.g., `/masconfig/inst1/`, `/masconfig/inst2/`).

### custom_labels
Custom Kubernetes labels for workspace resources.

- **Optional**
- Environment Variable: `CUSTOM_LABELS`
- Default: None

**Purpose**: Adds custom labels to workspace-specific Kubernetes resources for organization, tracking, or automation purposes.

**When to use**:
- Optional for most deployments
- Use for resource organization and filtering
- Helpful for cost tracking, ownership, or automation
- Common in multi-tenant or managed environments

**Valid values**: Comma-separated key=value pairs (e.g., `env=prod,team=operations,cost-center=12345`)

**Impact**: Adds the specified labels to workspace resources. Labels can be used for:
- Resource filtering and selection
- Cost allocation and tracking
- Automation and policy enforcement
- Organizational categorization

**Related variables**:
- `mas_workspace_id`: Workspace these labels apply to

**Note**: Labels must follow Kubernetes naming conventions (alphanumeric, hyphens, dots, max 63 chars per segment). Common uses include environment tags, team ownership, and cost center tracking.


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
