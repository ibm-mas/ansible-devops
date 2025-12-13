suite_manage_aiservice_config
===============================================================================

This role configures AI Service integration for Maximo Manage by:
1. Retrieving AI Service connection details (API key, URL, tenant ID)
2. Patching these properties into the Manage encryption secret
3. Importing AI Service TLS certificate into Manage truststore
4. Verifying AI Service health and connectivity

Role Variables
-------------------------------------------------------------------------------

### Required Variables

- `mas_instance_id`: MAS instance ID
- `mas_workspace_id`: MAS workspace ID
- `aiservice_instance_id`: AI Service instance ID

### Optional Variables

- `mas_app_id`: Application ID (default: `manage`)

Example Playbook
-------------------------------------------------------------------------------

```yaml
- hosts: localhost
  vars:
    mas_instance_id: "mymas"
    mas_workspace_id: "masdev"
    aiservice_instance_id: "mymas"
  roles:
    - ibm.mas_devops.suite_manage_aiservice_config
```

Environment Variables
-------------------------------------------------------------------------------

- `MAS_INSTANCE_ID`: MAS instance ID
- `MAS_WORKSPACE_ID`: MAS workspace ID
- `AISERVICE_INSTANCE_ID`: AI Service instance ID
- `MAS_APP_ID`: Application ID (default: `manage`)

License
-------------------------------------------------------------------------------
EPL-2.0