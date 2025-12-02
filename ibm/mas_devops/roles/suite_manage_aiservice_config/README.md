suite_manage_aiservice_config
===
This role configures **Maximo Manage** to connect to **Maximo AI Service** by retrieving AI Service connection details, importing the AI Service CA certificate, and patching connection properties into the Manage encryption secret.

**Note:** This role should be executed **after** both Manage and AI Service applications are deployed and activated, as it requires both services to be up and running.

The role performs the following steps:
1. Retrieves the AI Service CA certificate from the TLS secret
2. Imports the CA certificate into the Manage workspace
3. Retrieves the AI Service API key from the OpenShift secret
4. Gets the AI Service URL from the `aibroker` route
5. Retrieves the tenant ID from the `AIServiceTenant` custom resource
6. Patches these values into Manage's encryption secret

Role Variables
--------------

### mas_instance_id
**Required**. The instance ID of Maximo Application Suite. This will be used to lookup Manage application resources.

- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### aiservice_instance_id
**Required**. The instance ID of the AI Service installation. This will be used to lookup AI Service resources.

- Environment Variable: `AISERVICE_INSTANCE_ID`
- Default Value: None

### mas_workspace_id
Optional. The workspace ID of Maximo Application Suite. This will be used to identify the Manage encryption secret.

- Environment Variable: `MAS_WORKSPACE_ID`
- Default Value: `masdev`

What This Role Does
-------------------

This role configures the following in Manage:

### 1. Certificate Import
Imports the AI Service CA certificate into the Manage workspace truststore. This allows Manage to trust SSL/TLS connections to AI Service.

- Source: `{mas_instance_id}-public-aibroker-tls` secret in namespace `mas-{mas_instance_id}-broker`
- Certificate alias: `aiservice-ca1`

### 2. Connection Properties
Configures the following properties in the Manage encryption secret (`{mas_workspace_id}-manage-encryptionsecret`):

- `mxe.int.aibrokerapikey` - API key for authenticating with AI Service
- `mxe.int.aibrokerapiurl` - URL endpoint for AI Service API
- `mxe.int.aibrokertenantid` - Tenant ID for AI Service

After these properties are configured, Manage will automatically restart to apply the changes.

Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_workspace_id: masdev
    aiservice_instance_id: aisvc
  roles:
    - ibm.mas_devops.suite_manage_aiservice_config
```

Run Role Playbook
----------------
After installing the Ansible Collection you can easily run the role standalone using the `run_role` playbook provided.

```bash
export MAS_INSTANCE_ID=masinst1
export MAS_WORKSPACE_ID=masdev
export AISERVICE_INSTANCE_ID=aisvc
ROLE_NAME=suite_manage_aiservice_config ansible-playbook ibm.mas_devops.run_role
```

Prerequisites
-------------

1. OpenShift CLI (`oc`) must be installed and configured
2. You must be logged into the OpenShift cluster
3. Maximo Manage must be deployed and activated
4. Maximo AI Service must be deployed and activated
5. The following resources must exist:
   - Secret: `{mas_instance_id}-public-aibroker-tls` in namespace `mas-{mas_instance_id}-broker`
   - Secret: `aiservice-{AISERVICE_INSTANCE_ID}-user----apikey-secret` in namespace `aiservice-{AISERVICE_INSTANCE_ID}`
   - Route: `aibroker` in namespace `aiservice-{AISERVICE_INSTANCE_ID}`
   - Custom Resource: `AIServiceTenant` in namespace `aiservice-{AISERVICE_INSTANCE_ID}`
   - Secret: `{MAS_WORKSPACE_ID}-manage-encryptionsecret` in namespace `mas-{MAS_INSTANCE_ID}-manage`

Troubleshooting
---------------

### AI Service TLS certificate secret not found
Ensure the AI Service is fully deployed and the secret `{mas_instance_id}-public-aibroker-tls` exists in the `mas-{mas_instance_id}-broker` namespace. Some systems may not require this certificate if AI Service is already accessible.

### AI Service API key secret not found
Ensure the AI Service is fully deployed and the secret `aiservice-{AISERVICE_INSTANCE_ID}-user----apikey-secret` exists in the `aiservice-{AISERVICE_INSTANCE_ID}` namespace.

### aibroker route not found
Ensure the AI Service is fully deployed and the `aibroker` route exists in the `aiservice-{AISERVICE_INSTANCE_ID}` namespace.

### AIServiceTenant not found
Ensure the AI Service tenant is created. Check for `AIServiceTenant` custom resources in the `aiservice-{AISERVICE_INSTANCE_ID}` namespace.

### Manage encryption secret not found
Ensure Manage is fully deployed and activated. The encryption secret is created during Manage workspace activation.

### Certificate import fails
If certificate import fails, check:
- The `suite_manage_import_certs_config` role is available in your Ansible collection
- The Manage workspace is in a ready state
- You have sufficient permissions to modify the ManageWorkspace custom resource

License
-------

EPL-2.0
