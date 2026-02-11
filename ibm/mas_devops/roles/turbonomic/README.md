# turbonomic

Installs and configures [kubeturbo](https://github.com/turbonomic/kubeturbo) to connect your OpenShift cluster to a Turbonomic Application Resource Management (ARM) server. Kubeturbo is an agent that collects cluster resource utilization data and sends it to Turbonomic for analysis and optimization recommendations.

!!! warning "Disconnected Installation Not Supported"
    The **Turbonomic Kubernetes Operator** does not support disconnected/air-gapped installation. The **kubeturbo** deployment uses image tags rather than digests, preventing the use of ImageContentSourcePolicy to configure a mirror registry.

## What This Role Does

- Installs the Turbonomic Kubernetes Operator from available CatalogSource
- Deploys kubeturbo agent in the specified namespace
- Configures kubeturbo to connect to your Turbonomic server
- Sets up authentication credentials for server communication

## Role Variables - KubeTurbo Configuration

### kubeturbo_namespace
Namespace for KubeTurbo operator installation.

- **Optional**
- Environment Variable: `KUBETURBO_NAMESPACE`
- Default: `kubeturbo`

**Purpose**: Specifies the OpenShift namespace where the KubeTurbo operator and agent will be installed.

**When to use**:
- Use default (`kubeturbo`) for standard installations
- Override for custom namespace requirements
- Useful for multi-tenant or organized deployments

**Valid values**: Valid Kubernetes namespace name (lowercase alphanumeric and hyphens)

**Impact**: Determines where kubeturbo resources are deployed. All operator and agent components will be created in this namespace.

**Related variables**:
- `turbonomic_target_name`: Cluster identifier in Turbonomic

**Note**: The namespace will be created if it doesn't exist. Using the default `kubeturbo` namespace is recommended for consistency.

## Role Variables - Turbonomic Server Configuration

### turbonomic_target_name
Cluster name in Turbonomic server.

- **Required**
- Environment Variable: `TURBONOMIC_TARGET_NAME`
- Default: None

**Purpose**: Defines the name by which this cluster will be identified in the Turbonomic ARM server. The kubeturbo agent uses this name when registering and sending data to Turbonomic.

**When to use**:
- Always required for kubeturbo installation
- Should be unique across all clusters managed by Turbonomic
- Use descriptive names for easy identification

**Valid values**: String, typically cluster name or identifier (e.g., `prod-ocp-cluster`, `dev-cluster-01`)

**Impact**: Determines how the cluster appears in Turbonomic dashboards and reports. This name is used for all resource tracking and optimization recommendations.

**Related variables**:
- `turbonomic_server_url`: Server to register with
- `kubeturbo_namespace`: Where agent is deployed

**Note**: Choose a meaningful name that clearly identifies the cluster in your Turbonomic environment. This name should match your cluster naming conventions.

### turbonomic_server_url
Turbonomic server URL.

- **Required**
- Environment Variable: `TURBONOMIC_SERVER_URL`
- Default: None

**Purpose**: Specifies the URL of the Turbonomic ARM server that kubeturbo will connect to for sending cluster data and receiving optimization actions.

**When to use**:
- Always required for kubeturbo installation
- Must be accessible from the OpenShift cluster
- Should include protocol (https://)

**Valid values**: Full URL to Turbonomic server (e.g., `https://turbonomic.example.com`, `https://turbo-server.company.com:8080`)

**Impact**: Determines which Turbonomic server receives cluster data. Kubeturbo establishes connection to this endpoint for all communication.

**Related variables**:
- `turbonomic_username`/`turbonomic_password`: Authentication credentials
- `turbonomic_server_version`: Optional version specification
- `turbonomic_target_name`: Cluster identifier on this server

**Note**: Ensure the URL is accessible from the cluster network. The server must be reachable for kubeturbo to function properly.

### turbonomic_server_version
Turbonomic server version.

- **Optional**
- Environment Variable: `TURBONOMIC_SERVER_VERSION`
- Default: None

**Purpose**: Specifies the version of the Turbonomic server being connected to. Used for version-specific compatibility and feature enablement.

**When to use**:
- Optional for most installations
- Specify when connecting to specific Turbonomic versions
- May be required for version-specific features or compatibility

**Valid values**: Turbonomic version string (e.g., `8.9.4`, `8.10.0`, `8.11.2`)

**Impact**: May affect feature availability or compatibility checks between kubeturbo agent and Turbonomic server.

**Related variables**:
- `turbonomic_server_url`: Server being connected to

**Note**: If not specified, kubeturbo will attempt to detect server version automatically. Specify only if you need to enforce specific version compatibility.

### turbonomic_username
Turbonomic server username.

- **Required**
- Environment Variable: `TURBONOMIC_USERNAME`
- Default: None

**Purpose**: Provides the username for authenticating kubeturbo agent with the Turbonomic server.

**When to use**:
- Always required for kubeturbo installation
- Should be a service account or dedicated user
- Requires appropriate permissions in Turbonomic

**Valid values**: Valid Turbonomic username string

**Impact**: Used for authentication when kubeturbo connects to Turbonomic server. The user must have permissions to register targets and send data.

**Related variables**:
- `turbonomic_password`: Password for this username
- `turbonomic_server_url`: Server to authenticate with
- `turbonomic_target_name`: Cluster this user will register

**Note**: **SECURITY** - Use a dedicated service account rather than a personal user account. Ensure the account has appropriate permissions in Turbonomic for target registration and data submission.

### turbonomic_password
Turbonomic server password.

- **Required**
- Environment Variable: `TURBONOMIC_PASSWORD`
- Default: None

**Purpose**: Provides the password for authenticating kubeturbo agent with the Turbonomic server.

**When to use**:
- Always required for kubeturbo installation
- Must match the password for `turbonomic_username`
- Used for secure authentication

**Valid values**: Valid password string for the specified username

**Impact**: Used for authentication when kubeturbo connects to Turbonomic server. Authentication must succeed for data transmission.

**Related variables**:
- `turbonomic_username`: Username for this password
- `turbonomic_server_url`: Server to authenticate with

**Note**: **SECURITY** - Password should be kept secure and not committed to version control. Store in secure secret management systems. Use strong passwords following your organization's security policies.


Example Playbook
-------------------------------------------------------------------------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    turbonomic_server_url: https://myturbonomicserver.com
    turbonomic_server_version: "8.9.4"
    turbonomic_username: user
    turbonomic_password: passw0rd
    turbonomic_target_name: myocp
  roles:
    - ibm.mas_devops.turbonomic
```

License
-------------------------------------------------------------------------------
EPL-2.0
