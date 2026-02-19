# suite_app_uninstall

Uninstall Maximo Application Suite applications from a MAS instance. This role provides a clean removal process for MAS applications, removing all application-specific resources, configurations, and namespaces while preserving the MAS core platform and other applications.

The role supports uninstallation of all MAS applications including Assist, Health, IoT, Manage, Monitor, Optimizer, Predict, Visual Inspection, and Facilities (TRIRIGA).


## Role Variables

### mas_instance_id
MAS instance identifier from which the application will be uninstalled.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

**Purpose**: Identifies the target MAS instance containing the application to be removed.

**When to use**: Always required. Must match an existing MAS instance with the application installed.

**Valid values**: Valid MAS instance ID (typically 3-12 lowercase alphanumeric characters).

**Impact**: The uninstall operation will target the application in the `mas-<instance-id>-<app-id>` namespace. All resources in this namespace will be removed.

**Related variables**: `mas_app_id`

**Notes**:
- Must match the instance ID used during MAS installation
- Case-sensitive value
- **Critical**: Uninstallation is permanent and cannot be undone
- Always backup application data before uninstalling
- Other applications in the same instance are not affected

### mas_app_id
MAS application identifier to be uninstalled.

- **Required**
- Environment Variable: `MAS_APP_ID`
- Default: None

**Purpose**: Specifies which MAS application will be removed from the instance.

**When to use**: Always required. Must be a valid, installed application.

**Valid values**:
- `assist` - Maximo Assist
- `health` - Maximo Health (formerly Predict)
- `iot` - Maximo IoT
- `manage` - Maximo Manage
- `monitor` - Maximo Monitor
- `optimizer` - Maximo Optimizer
- `predict` - Maximo Predict
- `visualinspection` - Maximo Visual Inspection
- `facilities` - Maximo Facilities (TRIRIGA)

**Impact**: The specified application and all its resources will be permanently removed. This includes:
- Application namespace and all contained resources
- Application custom resources (e.g., ManageApp, IoTApp)
- Application-specific configurations
- Application workspaces (if any)
- Application data stored in the namespace

**Related variables**: `mas_instance_id`

**Notes**:
- **Warning**: Uninstallation is irreversible
- Application data in external databases is NOT removed
- Backup all critical data before uninstalling
- Application must be installed before it can be uninstalled
- Uninstalling Manage does not remove the Manage database
- Consider using application deactivation instead of uninstall if you may need to reinstall
- Uninstalling an application does not affect other applications in the same instance

## Example Playbook

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    # MAS configuration
    mas_instance_id: "{{ lookup('env', 'MAS_INSTANCE_ID') }}"

    # MAS application configuration
    mas_app_id: "{{ lookup('env', 'MAS_APP_ID') }}"

  roles:
    - ibm.mas_devops.suite_app_uninstall
```

## License

EPL-2.0
