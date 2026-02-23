# suite_manage_birt_report_config

This role configures BIRT (Business Intelligence and Reporting Tools) reporting in Maximo Manage application by setting up a dedicated report bundle server workload. This enables scalable report generation by offloading report processing to dedicated pods.

## What This Role Does

- Configures dedicated report bundle server for BIRT report generation
- Sets up Manage report route endpoint for generated reports
- Updates Manage system properties for all bundles:
  - `mxe.report.birt.viewerurl`: Points to dedicated report server route
  - `mxe.report.birt.disablequeuemanager`: Enables queue manager only on report bundle (0 for report bundle, 1 for others)
- Forwards report workload to dedicated report-type bundle pods

!!! tip "Performance Optimization"
    Using a dedicated report bundle server improves Manage performance by isolating resource-intensive report generation from other Manage operations.

## Role Variables

### mas_instance_id
MAS instance identifier.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

**Purpose**: Identifies which MAS instance contains the Manage application to configure for BIRT reporting.

**When to use**:
- Always required for BIRT report configuration
- Must match the instance ID from MAS installation
- Used to locate Manage resources

**Valid values**: Lowercase alphanumeric string, 3-12 characters (e.g., `prod`, `dev`, `masinst1`)

**Impact**: Determines which MAS instance's Manage application is configured with BIRT report server.

**Related variables**:
- `mas_workspace_id`: Workspace within this instance
- `manage_workspace_cr_name`: Constructed from instance and workspace IDs

**Note**: This must match the instance ID used during Manage installation.

### mas_workspace_id
Workspace identifier for Manage application.

- **Required**
- Environment Variable: `MAS_WORKSPACE_ID`
- Default: None

**Purpose**: Identifies which workspace within the MAS instance contains the Manage application to configure for BIRT reporting.

**When to use**:
- Always required for BIRT report configuration
- Must match the workspace ID where Manage is deployed
- Used in report route URL construction

**Valid values**: Lowercase alphanumeric string, typically 3-12 characters (e.g., `prod`, `dev`, `main`)

**Impact**: Used to construct the report server route URL: `https://{workspace_id}-{report_bundle_name}.manage.{domain}`

**Related variables**:
- `mas_instance_id`: Parent instance
- `manage_report_bundle_server_name`: Report bundle name in route URL
- `manage_workspace_cr_name`: Constructed from instance and workspace IDs

**Note**: This must match the workspace ID used during Manage installation.

### manage_workspace_cr_name
ManageWorkspace custom resource name.

- **Optional**
- Environment Variable: `MANAGE_WORKSPACE_CR_NAME`
- Default: `{mas_instance_id}-{mas_workspace_id}`

**Purpose**: Specifies the name of the ManageWorkspace custom resource to update with BIRT report configuration.

**When to use**:
- Use default unless you have a custom CR naming convention
- Override if your ManageWorkspace CR has a non-standard name
- Required to update bundle properties

**Valid values**: Valid Kubernetes resource name

**Impact**: Determines which ManageWorkspace CR is updated with report bundle configuration and system properties.

**Related variables**:
- `mas_instance_id`: Used in default name construction
- `mas_workspace_id`: Used in default name construction
- `manage_report_bundle_server_name`: Report bundle to configure

**Note**: The default naming convention `{instance}-{workspace}` matches standard Manage deployments. Only override if you have custom CR names.

### manage_report_bundle_server_name
Report bundle server name.

- **Optional**
- Environment Variable: `MANAGE_REPORT_BUNDLE_SERVER_NAME`
- Default: `rpt`

**Purpose**: Defines the name of the dedicated report bundle server and its corresponding route for BIRT report generation.

**When to use**:
- Use default (`rpt`) for standard deployments
- Override for custom naming conventions
- Not needed if report bundle server is already configured

**Valid values**: Valid Kubernetes resource name (lowercase alphanumeric and hyphens)

**Impact**:
- Determines the report bundle server name in Manage configuration
- Used in report route URL: `https://{workspace_id}-{this_name}.manage.{domain}`
- Identifies which bundle pods handle report generation

**Related variables**:
- `mas_workspace_id`: Used in route URL construction
- `manage_workspace_cr_name`: CR to update with this bundle configuration

**Note**: The default `rpt` is a common abbreviation for "report". Choose a meaningful name that clearly identifies the report bundle server purpose.

## Example Playbook

The following sample can be used to configure BIRT report for an existing Manage application instance.

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_workspace_id: main
  roles:
    - ibm.mas_devops.suite_manage_birt_report_config
```

## Run Role Playbook
After installing the Ansible Collection you can easily run the role standalone using the `run_role` playbook provided.

```bash
export MAS_INSTANCE_ID=masinst1
export MAS_WORKSPACE_ID=main
export MANAGE_REPORT_BUNDLE_SERVER_NAME=report
ROLE_NAME='suite_manage_birt_report_config' ansible-playbook playbooks/run_role.yml
```

## License

EPL-2.0
