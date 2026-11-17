# suite_app_uninstall

Uninstall Maximo Application Suite applications from a MAS instance. This role provides a clean removal process for MAS applications, removing all application-specific resources, configurations, and namespaces while preserving the MAS core platform and other applications.

The role supports uninstallation of all MAS applications including Assist, Health, IoT, Manage, Monitor, Optimizer, Predict, Visual Inspection, and Facilities (TRIRIGA).

!!! warning
    Application uninstallation is permanent and cannot be undone. Back up any critical data before proceeding — data in external databases (for example the Manage database) is **not** removed by this role, but everything in the application namespace is.

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`mas_instance_id`](#mas_instance_id) | Yes | None |
| [`mas_app_id`](#mas_app_id) | Yes | None |

### Application Selection

#### mas_instance_id

MAS instance identifier from which the application will be uninstalled (typically 3-12 lowercase alphanumeric characters).

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

Must match the instance ID used during MAS installation; the value is case-sensitive. The uninstall targets the application in the `mas-<instance-id>-<app-id>` namespace — all resources in that namespace are removed. Other applications in the same instance are not affected.

#### mas_app_id

MAS application identifier to be uninstalled.

- **Required**
- Environment Variable: `MAS_APP_ID`
- Default: None

Valid values: `assist` (Maximo Assist), `health` (Maximo Health, formerly Predict), `iot` (Maximo IoT), `manage` (Maximo Manage), `monitor` (Maximo Monitor), `optimizer` (Maximo Optimizer), `predict` (Maximo Predict), `visualinspection` (Maximo Visual Inspection), `facilities` (Maximo Facilities, TRIRIGA).

Uninstalling removes the application namespace and all contained resources, application custom resources (e.g. ManageApp, IoTApp), application-specific configurations, and workspaces. If you may need to reinstall later, consider deactivating the application instead.

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
