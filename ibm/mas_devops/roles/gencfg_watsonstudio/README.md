gencfg_watsonstudio
============

Generate Watson Studio configuration files for connecting Maximo Application Suite to IBM Cloud Pak for Data Watson Studio instances. This role creates WatsonStudioCfg custom resources that enable MAS applications (particularly Predict and Health) to leverage Watson Studio's machine learning and analytics capabilities.

The role supports flexible configuration scoping to make Watson Studio available at system, workspace, application, or workspace-application levels within MAS.


Role Variables
-------------------------------------------------------------------------------

### mas_instance_id
MAS instance identifier for which the Watson Studio configuration is being generated.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

**Purpose**: Identifies the target MAS instance where this Watson Studio configuration will be applied.

**When to use**: Always required when generating Watson Studio configuration. Must match an existing MAS instance ID.

**Valid values**: Valid MAS instance ID (typically 3-12 lowercase alphanumeric characters).

**Impact**: The generated configuration will be namespace-scoped to `mas-<instance-id>-core`. Incorrect instance ID will cause the configuration to be created in the wrong namespace.

**Related variables**: `mas_config_dir`, `mas_config_scope`

**Notes**:
- Must match the instance ID used during MAS installation
- Case-sensitive value
- Watson Studio integration is primarily used by Predict and Health applications
- Required for AI/ML model training and deployment in MAS

### mas_workspace_id
MAS workspace identifier for workspace-scoped configurations.

- **Required** if `mas_config_scope` is `ws` or `wsapp`
- Environment Variable: `MAS_WORKSPACE_ID`
- Default: None

**Purpose**: Specifies the target workspace when generating workspace-scoped or workspace-application-scoped Watson Studio configurations.

**When to use**: Required when `mas_config_scope` is set to `ws` or `wsapp`. Not used for `system` or `app` scopes.

**Valid values**: Valid MAS workspace ID (typically lowercase alphanumeric, e.g., `masdev`, `prod`, `test`).

**Impact**: The Watson Studio configuration will only be available to the specified workspace. Applications in other workspaces cannot access this Watson Studio instance.

**Related variables**: `mas_config_scope`, `mas_application_id`

**Notes**:
- Workspace must exist before applying the configuration
- Use workspace-scoped configs for tenant isolation in multi-tenant deployments
- Each workspace can have its own Watson Studio instance for data isolation

### mas_config_scope
Configuration scope level for the generated Watson Studio configuration.

- Optional
- Environment Variable: `MAS_CONFIG_SCOPE`
- Default: `system`

**Purpose**: Determines at what level the Watson Studio configuration will be available within MAS - system-wide, workspace-specific, application-specific, or workspace-application combination.

**When to use**: Set based on how Watson Studio will be shared across MAS components. Default `system` scope makes it available to all workspaces and applications.

**Valid values**:
- `system` - Available to all workspaces and applications (default)
- `ws` - Available only to a specific workspace
- `app` - Available only to a specific application across all workspaces
- `wsapp` - Available only to a specific application in a specific workspace

**Impact**: Determines which MAS components can access this Watson Studio configuration. Incorrect scope may prevent applications from finding the Watson Studio connection.

**Related variables**: `mas_workspace_id` (required for `ws` and `wsapp`), `mas_application_id` (required for `app` and `wsapp`)

**Notes**:
- Default `system` scope is suitable for most deployments
- Use `wsapp` scope for dedicated Watson Studio instances per workspace-application
- Scope cannot be changed after creation; requires recreation of the configuration
- Predict and Health are the primary consumers of Watson Studio

### mas_config_dir
Local directory path where the generated YAML configuration file will be saved.

- **Required**
- Environment Variable: `MAS_CONFIG_DIR`
- Default: None

**Purpose**: Specifies the output directory for the generated WatsonStudioCfg YAML file that can be applied to the MAS instance.

**When to use**: Always required. Directory must exist or be creatable by the Ansible user.

**Valid values**: Valid directory path (absolute or relative) where the Ansible controller has write permissions.

**Impact**: The generated YAML file will be created in this directory and can be applied using `kubectl apply` or the `suite_config` role.

**Related variables**: `mas_instance_id`

**Notes**:
- Directory will be created if it doesn't exist
- Generated filename format: `watsonstudiocfg-<scope>.yml`
- Keep generated files for documentation and disaster recovery purposes
- Can be used as input to the `suite_config` role

### mas_application_id
MAS application identifier for application-scoped configurations.

- **Required** if `mas_config_scope` is `app` or `wsapp`
- Environment Variable: `MAS_APP_ID`
- Default: None

**Purpose**: Specifies the target application when generating application-scoped or workspace-application-scoped Watson Studio configurations.

**When to use**: Required when `mas_config_scope` is set to `app` or `wsapp`. Not used for `system` or `ws` scopes.

**Valid values**: Valid MAS application ID, typically `predict` or `health` (the primary Watson Studio consumers).

**Impact**: The Watson Studio configuration will only be available to the specified application. Other applications cannot access this Watson Studio instance.

**Related variables**: `mas_config_scope`, `mas_workspace_id`

**Notes**:
- Application must be installed before applying the configuration
- Predict and Health are the main applications that use Watson Studio
- Use application-scoped configs when different applications need different Watson Studio instances

### cpd_admin_username
Cloud Pak for Data administrative username for Watson Studio access.

- **Required**
- Environment Variable: `CPD_ADMIN_USERNAME`
- Default: None

**Purpose**: Specifies the Cloud Pak for Data user account that MAS will use to connect to Watson Studio for AI/ML operations.

**When to use**: Always required. Must be a valid CP4D user with appropriate Watson Studio permissions.

**Valid values**: Valid Cloud Pak for Data username with Watson Studio access rights.

**Impact**: This user must have permissions to create and manage Watson Studio projects, deployments, and models. Insufficient permissions will cause Predict/Health AI features to fail.

**Related variables**: `cpd_admin_password`, `cpd_admin_url`

**Notes**:
- User must have Watson Studio service access
- Requires permissions to create projects and deploy models
- Consider using a dedicated service account rather than a personal admin account
- User should have appropriate resource quotas for ML workloads

### cpd_admin_password
Cloud Pak for Data password for authentication.

- **Required**
- Environment Variable: `CPD_ADMIN_PASSWORD`
- Default: None

**Purpose**: Provides the password for the Cloud Pak for Data user account specified in `cpd_admin_username`.

**When to use**: Always required for CP4D authentication.

**Valid values**: Valid password string meeting Cloud Pak for Data security requirements.

**Impact**: Stored as a Kubernetes secret in the MAS namespace. Incorrect password will prevent MAS from connecting to Watson Studio.

**Related variables**: `cpd_admin_username`, `cpd_admin_url`

**Notes**:
- Password is stored securely in Kubernetes secrets
- Use strong passwords meeting your organization's security policies
- Consider implementing password rotation policies
- Ensure password doesn't expire or require periodic changes that could break integration

### cpd_admin_url
Cloud Pak for Data console URL for Watson Studio access.

- **Required**
- Environment Variable: `CPD_ADMIN_URL`
- Default: None

**Purpose**: Defines the Cloud Pak for Data web console URL that MAS will use to connect to Watson Studio services.

**When to use**: Always required. Must be the accessible URL to the CP4D console.

**Valid values**: Valid HTTPS URL to the Cloud Pak for Data console (e.g., `https://cpd-cpd.apps.ocp.example.com`).

**Impact**: MAS applications will use this URL to access Watson Studio APIs. Incorrect or inaccessible URL will prevent AI/ML functionality.

**Related variables**: `cpd_admin_username`, `cpd_admin_password`

**Notes**:
- Must be the full HTTPS URL including protocol
- URL must be accessible from the OpenShift cluster where MAS is running
- Verify network connectivity and firewall rules
- For multi-cluster deployments, ensure proper routing is configured
- URL should point to the CP4D console route, not individual service routes

### custom_labels
Custom Kubernetes labels to apply to the generated WatsonStudioCfg resource.

- Optional
- Environment Variable: `CUSTOM_LABELS`
- Default: None

**Purpose**: Adds custom labels to the WatsonStudioCfg resource for organization, filtering, or automation purposes.

**When to use**: Use when you need to tag configurations for specific purposes like environment identification, cost tracking, or automated management.

**Valid values**: Comma-separated key=value pairs (e.g., `env=prod,team=ai-ml,cost-center=12345`).

**Impact**: Labels are applied to the Kubernetes resource and can be used for selection, filtering, and automation workflows.

**Related variables**: None

**Notes**:
- Labels must follow Kubernetes naming conventions
- Useful for GitOps workflows and resource management
- Can be used with label selectors in automation scripts
- Helpful for tracking Watson Studio configurations across multiple environments


Example Playbook
----------------

```yaml
---

- hosts: localhost
  any_errors_fatal: true
  roles:
    - ibm.mas_devops.gencfg_watsonstudio
```

License
-------

EPL-2.0
