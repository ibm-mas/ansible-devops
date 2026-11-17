# gencfg_watsonstudio

Generate Watson Studio configuration files for connecting Maximo Application Suite to IBM Cloud Pak for Data Watson Studio instances. This role creates WatsonStudioCfg custom resources that enable MAS applications (particularly Predict and Health) to leverage Watson Studio's machine learning and analytics capabilities.

The role supports flexible configuration scoping to make Watson Studio available at system, workspace, application, or workspace-application levels within MAS.

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`mas_instance_id`](#mas_instance_id) | Yes | None |
| [`mas_config_scope`](#mas_config_scope) | No | `system` |
| [`mas_workspace_id`](#mas_workspace_id) | Conditional | None |
| [`mas_application_id`](#mas_application_id) | Conditional | None |
| [`mas_config_dir`](#mas_config_dir) | Yes | None |
| [`cpd_admin_url`](#cpd_admin_url) | Yes | None |
| [`cpd_admin_username`](#cpd_admin_username) | Yes | None |
| [`cpd_admin_password`](#cpd_admin_password) | Yes | None |
| [`custom_labels`](#custom_labels) | No | None |

`mas_workspace_id` is required only when `mas_config_scope` is `ws` or `wsapp`, and `mas_application_id` only when the scope is `app` or `wsapp`.

### MAS Configuration

#### mas_instance_id

MAS instance identifier for which the Watson Studio configuration is being generated — a valid MAS instance ID (typically 3-12 lowercase alphanumeric characters) that must match the instance ID used during MAS installation.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

The generated configuration is namespace-scoped to `mas-<instance-id>-core`; an incorrect instance ID will cause the configuration to be created in the wrong namespace. The value is case-sensitive. Watson Studio integration is primarily used by the Predict and Health applications for AI/ML model training and deployment in MAS.

#### mas_config_scope

Configuration scope level for the generated Watson Studio configuration — `system` (available to all workspaces and applications, the default), `ws` (a specific workspace), `app` (a specific application across all workspaces), or `wsapp` (a specific application in a specific workspace).

- **Optional**
- Environment Variable: `MAS_CONFIG_SCOPE`
- Default: `system`

Determines which MAS components can access the Watson Studio configuration; an incorrect scope may prevent applications from finding the Watson Studio connection. The default `system` scope is suitable for most deployments, while `wsapp` is useful for dedicated Watson Studio instances per workspace-application. The scope cannot be changed after creation — it requires recreating the configuration.

#### mas_workspace_id

MAS workspace identifier for workspace-scoped configurations — a valid MAS workspace ID, typically lowercase alphanumeric, for example `masdev`, `prod`, or `test`.

- **Required** when `mas_config_scope` is `ws` or `wsapp`
- Environment Variable: `MAS_WORKSPACE_ID`
- Default: None

The Watson Studio configuration is only available to the specified workspace; applications in other workspaces cannot access this Watson Studio instance. The workspace must exist before applying the configuration. Use workspace-scoped configs for tenant isolation in multi-tenant deployments, where each workspace can have its own Watson Studio instance for data isolation.

#### mas_application_id

MAS application identifier for application-scoped configurations — typically `predict` or `health`, the primary Watson Studio consumers.

- **Required** when `mas_config_scope` is `app` or `wsapp`
- Environment Variable: `MAS_APP_ID`
- Default: None

The Watson Studio configuration is only available to the specified application; other applications cannot access this Watson Studio instance. The application must be installed before applying the configuration. Use application-scoped configs when different applications need different Watson Studio instances.

#### mas_config_dir

Local directory path where the generated YAML configuration file will be saved — a valid directory path (absolute or relative) where the Ansible controller has write permissions.

- **Required**
- Environment Variable: `MAS_CONFIG_DIR`
- Default: None

The generated file (`watsonstudiocfg-<scope>.yml`) can be applied using `kubectl apply` or used as input to the `suite_config` role; the directory is created if it does not exist. Keep the generated files for documentation and disaster recovery purposes.

### Cloud Pak for Data Connection

#### cpd_admin_url

Cloud Pak for Data console URL for Watson Studio access — the full HTTPS URL to the CP4D console, for example `https://cpd-cpd.apps.ocp.example.com`.

- **Required**
- Environment Variable: `CPD_ADMIN_URL`
- Default: None

MAS applications use this URL to access Watson Studio APIs; an incorrect or inaccessible URL will prevent AI/ML functionality. The URL must be accessible from the OpenShift cluster where MAS is running (verify network connectivity and firewall rules) and must point to the CP4D console route, not individual service routes. For multi-cluster deployments, ensure proper routing is configured.

#### cpd_admin_username

Cloud Pak for Data administrative username for Watson Studio access — a valid Cloud Pak for Data username with Watson Studio access rights.

- **Required**
- Environment Variable: `CPD_ADMIN_USERNAME`
- Default: None

This user must have permissions to create and manage Watson Studio projects, deployments, and models; insufficient permissions will cause Predict/Health AI features to fail. Consider using a dedicated service account rather than a personal admin account, with appropriate resource quotas for ML workloads.

#### cpd_admin_password

Cloud Pak for Data password for authentication — a strong password string meeting Cloud Pak for Data security requirements.

- **Required**
- Environment Variable: `CPD_ADMIN_PASSWORD`
- Default: None

The password for the user account specified in `cpd_admin_username` is stored securely as a Kubernetes secret in the MAS namespace; an incorrect password will prevent MAS from connecting to Watson Studio. Follow your organization's password and rotation policies, and ensure the password does not expire in a way that could break the integration.

### Resource Labels

#### custom_labels

Custom Kubernetes labels to apply to the generated WatsonStudioCfg resource, as a comma-separated list of key=value pairs — for example `env=prod,team=ai-ml,cost-center=12345`.

- **Optional**
- Environment Variable: `CUSTOM_LABELS`
- Default: None

Labels must follow Kubernetes naming conventions; they can be used with label selectors for filtering, GitOps workflows, and automation scripts, and are helpful for tracking Watson Studio configurations across multiple environments.

## Example Playbook

```yaml
- hosts: localhost
  any_errors_fatal: true
  roles:
    - ibm.mas_devops.gencfg_watsonstudio
```

## License

EPL-2.0
