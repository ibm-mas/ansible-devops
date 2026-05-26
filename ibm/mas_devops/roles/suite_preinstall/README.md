# suite_preinstall

Apply pre-install RBAC (Role-Based Access Control) for IBM Maximo Application Suite. This role calls the Python module from the python-devops repository to configure the necessary permissions before installing MAS components.

## Role Variables

### Required Variables

- `mas_instance_id`: MAS instance identifier
- `mas_version`: MAS version for RBAC manifests (e.g., "9.0")

### Optional Variables

- `mas_preinstall_permission_mode`: Permission mode for RBAC application
  - Valid values: `minimal`, `namespaced`, `cluster`
  - Default: `namespaced`
  - `minimal`: Essential roles applied by each operator
  - `namespaced`: Roles applied per namespace
  - `cluster`: Cluster-wide roles

- `mas_preinstall_selected_apps`: Applications to configure RBAC for
  - Can be a comma-separated string or list
  - Valid values: `core`, `aiservice`, `arcgis`, `facilities`, `iot`, `manage`, `monitor`, `optimizer`, `predict`, `visualinspection`
  - Default: empty (no apps selected)
  - Required for `namespaced` mode

- `mas_preinstall_rbac_root_dir`: Root directory containing RBAC manifests
  - Default: `/opt/app-root/rbac` (defined in Python module)

- `mas_preinstall_check_permissions`: Whether to check permissions before applying RBAC
  - Default: `true`

## Environment Variables

All role variables can be set via environment variables:

- `MAS_INSTANCE_ID`
- `MAS_VERSION`
- `MAS_PREINSTALL_PERMISSION_MODE`
- `MAS_PREINSTALL_SELECTED_APPS`
- `MAS_PREINSTALL_RBAC_ROOT_DIR`
- `MAS_PREINSTALL_CHECK_PERMISSIONS`

## Dependencies

- Python module: `/c/wksp/python-devops/src/mas/devops/pre_install.py`
- Python packages: `kubernetes`, `openshift`, `jinja2`, `pyyaml`
- Kubernetes/OpenShift cluster access

## Example Playbook

### Minimal Mode
```yaml
- hosts: localhost
  roles:
    - role: ibm.mas_devops.suite_preinstall
      vars:
        mas_instance_id: "inst1"
        mas_version: "9.0"
        mas_preinstall_permission_mode: "minimal"
```

### Namespaced Mode with Selected Apps
```yaml
- hosts: localhost
  roles:
    - role: ibm.mas_devops.suite_preinstall
      vars:
        mas_instance_id: "inst1"
        mas_version: "9.0"
        mas_preinstall_permission_mode: "namespaced"
        mas_preinstall_selected_apps:
          - core
          - manage
          - iot
```

### Cluster Mode
```yaml
- hosts: localhost
  roles:
    - role: ibm.mas_devops.suite_preinstall
      vars:
        mas_instance_id: "inst1"
        mas_version: "9.0"
        mas_preinstall_permission_mode: "cluster"
```

### With Custom RBAC Directory
```yaml
- hosts: localhost
  roles:
    - role: ibm.mas_devops.suite_preinstall
      vars:
        mas_instance_id: "inst1"
        mas_version: "9.0"
        mas_preinstall_permission_mode: "namespaced"
        mas_preinstall_selected_apps: "core,manage,iot"
        mas_preinstall_rbac_root_dir: "/custom/rbac/path"
```

## Permission Checks

When `mas_preinstall_check_permissions` is `true` (default), the role will verify that the current user/service account has the necessary permissions to create and manage RBAC resources:

- Create namespaces
- Create/update ClusterRoles
- Create/update ClusterRoleBindings

If any required permissions are missing, the role will fail before attempting to apply RBAC.

## License

EPL-2.0