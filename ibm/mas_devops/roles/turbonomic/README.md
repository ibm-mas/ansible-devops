# turbonomic

Installs and configures [kubeturbo](https://github.com/turbonomic/kubeturbo) to connect your OpenShift cluster to a Turbonomic Application Resource Management (ARM) server. Kubeturbo is an agent that collects cluster resource utilization data and sends it to Turbonomic for analysis and optimization recommendations.

!!! warning "Disconnected Installation Not Supported"
    The **Turbonomic Kubernetes Operator** does not support disconnected/air-gapped installation. The **kubeturbo** deployment uses image tags rather than digests, preventing the use of ImageContentSourcePolicy to configure a mirror registry.

## What This Role Does

- Installs the Turbonomic Kubernetes Operator from available CatalogSource
- Deploys kubeturbo agent in the specified namespace
- Configures kubeturbo to connect to your Turbonomic server
- Sets up authentication credentials for server communication

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`kubeturbo_namespace`](#kubeturbo_namespace) | No | `kubeturbo` |
| [`kubeturbo_package_name`](#kubeturbo_package_name) | No | `kubeturbo-certified` |
| [`turbonomic_target_name`](#turbonomic_target_name) | Yes | None |
| [`turbonomic_server_url`](#turbonomic_server_url) | Yes | None |
| [`turbonomic_server_version`](#turbonomic_server_version) | No | None |
| [`turbonomic_username`](#turbonomic_username) | Yes | None |
| [`turbonomic_password`](#turbonomic_password) | Yes | None |

### KubeTurbo Installation

#### kubeturbo_namespace
OpenShift namespace where the KubeTurbo operator and agent are installed — a valid Kubernetes namespace name (lowercase alphanumeric and hyphens). All operator and agent components are created in this namespace, which is created if it doesn't exist.

- **Optional**
- Environment Variable: `KUBETURBO_NAMESPACE`
- Default: `kubeturbo`

Using the default `kubeturbo` namespace is recommended for consistency; override it only for multi-tenant or custom namespace requirements.

#### kubeturbo_package_name
Name of the kubeturbo package in the CatalogSource, used to locate the PackageManifest for the operator subscription.

- **Optional**
- Environment Variable: None (hardcoded in defaults)
- Default: `kubeturbo-certified`

### Turbonomic Server

#### turbonomic_target_name
Name by which this cluster is identified in the Turbonomic ARM server — typically the cluster name or identifier, for example `prod-ocp-cluster` or `dev-cluster-01`.

- **Required**
- Environment Variable: `TURBONOMIC_TARGET_NAME`
- Default: None

The kubeturbo agent uses this name when registering and sending data to Turbonomic; it determines how the cluster appears in Turbonomic dashboards and reports. Choose a unique, descriptive name that follows your cluster naming conventions and is unique across all clusters managed by the same Turbonomic server.

#### turbonomic_server_url
URL of the Turbonomic ARM server that kubeturbo connects to for sending cluster data and receiving optimization actions — a full URL including the protocol, for example `https://turbonomic.example.com` or `https://turbo-server.company.com:8080`.

- **Required**
- Environment Variable: `TURBONOMIC_SERVER_URL`
- Default: None

The server must be reachable from the OpenShift cluster network for kubeturbo to function properly — kubeturbo establishes its connection to this endpoint for all communication.

#### turbonomic_server_version
Version of the Turbonomic server being connected to — a Turbonomic version string such as `8.9.4`, `8.10.0`, or `8.11.2`, used for version-specific compatibility and feature enablement.

- **Optional**
- Environment Variable: `TURBONOMIC_SERVER_VERSION`
- Default: None

If not specified, kubeturbo attempts to detect the server version automatically; specify only to enforce specific version compatibility, which may affect feature availability between the kubeturbo agent and the server.

#### turbonomic_username
Username for authenticating the kubeturbo agent with the Turbonomic server — a valid Turbonomic username with permissions to register targets and send data.

- **Required**
- Environment Variable: `TURBONOMIC_USERNAME`
- Default: None

!!! tip
    Use a dedicated service account rather than a personal user account, and ensure it has the appropriate permissions in Turbonomic for target registration and data submission.

#### turbonomic_password
Password for authenticating the kubeturbo agent with the Turbonomic server — must match the password for `turbonomic_username`; authentication must succeed for data transmission.

- **Required**
- Environment Variable: `TURBONOMIC_PASSWORD`
- Default: None

!!! warning
    Keep the password secure and do not commit it to version control. Store it in a secure secret management system and use strong passwords following your organization's security policies.

## Example Playbook

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

## License
EPL-2.0
