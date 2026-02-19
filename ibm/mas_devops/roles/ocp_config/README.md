# ocp_config

Configure OpenShift Container Platform cluster-level settings for optimal MAS deployment. This role provides essential tuning for ingress timeouts, TLS cipher compatibility with IBM Java Semeru FIPS mode, and OperatorHub catalog source management.

Key capabilities:
- **Ingress timeout tuning**: Prevent request failures for long-running operations
- **FIPS-compatible TLS ciphers**: Enable IBM Java Semeru runtime in FIPS mode
- **Catalog source management**: Disable default Red Hat catalogs for air-gapped environments
- **Path-based routing**: Configure namespace ownership for multi-namespace route support

This role configures:
- Tune the `IngressController` to avoid request failures due to timeout for long running requests
- Configure the `IngressController` namespace ownership for path-based routing support
- Update `APIServer` and `IngressController` to set a custom `tlsSecurityProfile` to accommodate ciphers supported by IBM Java Semeru runtime. This is required for allowing the Java applications using Semeru runtime to run in FIPS mode. The following ciphers will be enabled:
    - `TLS_AES_128_GCM_SHA256`
    - `TLS_AES_256_GCM_SHA384`
    - `TLS_CHACHA20_POLY1305_SHA256`
    - `ECDHE-ECDSA-AES128-GCM-SHA256`
    - `ECDHE-RSA-AES128-GCM-SHA256`
    - `ECDHE-ECDSA-AES256-GCM-SHA384`
    - `ECDHE-RSA-AES256-GCM-SHA384`
    - `ECDHE-ECDSA-CHACHA20-POLY1305`
    - `ECDHE-RSA-CHACHA20-POLY1305`
    - `DHE-RSA-AES128-GCM-SHA256`
    - `DHE-RSA-AES256-GCM-SHA384`
    - `ECDHE-RSA-AES128-SHA256`
    - `ECDHE-RSA-AES128-SHA`
    - `ECDHE-RSA-AES256-SHA`
- Disable the default Red Hat `CatalogSources`:
    - `certified-operators`
    - `community-operators`
    - `redhat-operators`


## Role Variables - API Server

## Role Variables

### ocp_update_ciphers_for_semeru
Enable custom TLS cipher configuration for IBM Java Semeru FIPS mode compatibility.

- Optional
- Environment Variable: `OCP_UPDATE_CIPHERS_FOR_SEMERU`
- Default: `false`

**Purpose**: Configures the API Server and Ingress Controller with a custom TLS security profile that includes ciphers compatible with IBM Java Semeru runtime in FIPS mode.

**When to use**: Required when running MAS applications (particularly Manage) in FIPS mode with IBM Java Semeru runtime.

**Valid values**:
- `true` - Apply custom cipher configuration
- `false` - Use default OpenShift cipher configuration

**Impact**: When enabled, updates the `tlsSecurityProfile` on both APIServer and IngressController resources to include the following ciphers:
- TLS 1.3: `TLS_AES_128_GCM_SHA256`, `TLS_AES_256_GCM_SHA384`, `TLS_CHACHA20_POLY1305_SHA256`
- TLS 1.2: `ECDHE-ECDSA-AES128-GCM-SHA256`, `ECDHE-RSA-AES128-GCM-SHA256`, `ECDHE-ECDSA-AES256-GCM-SHA384`, `ECDHE-RSA-AES256-GCM-SHA384`, `ECDHE-ECDSA-CHACHA20-POLY1305`, `ECDHE-RSA-CHACHA20-POLY1305`, `DHE-RSA-AES128-GCM-SHA256`, `DHE-RSA-AES256-GCM-SHA384`, `ECDHE-RSA-AES128-SHA256`, `ECDHE-RSA-AES128-SHA`, `ECDHE-RSA-AES256-SHA`

**Related variables**: None

**Notes**:
- Required for FIPS-compliant MAS deployments using Semeru runtime
- Changes affect cluster-wide TLS configuration
- May require cluster restart to fully apply
- Verify compatibility with other applications in the cluster


## Role Variables - Ingress Controller
### ocp_ingress_controller_name
The name of the Ingress Controller to configure.

- **Optional**
- Environment Variable: `OCP_INGRESS_CONTROLLER_NAME`
- Default Value: `default`

**Purpose**: Specifies which Ingress Controller instance to configure. This applies to both timeout and namespace ownership settings.

**When to use**: Use the default value unless you have multiple Ingress Controllers in your cluster and need to configure a specific one.

**Valid values**:
- `default` - The default cluster Ingress Controller (most common)
- Any custom Ingress Controller name in your cluster

**Impact**: All timeout and namespace ownership configurations will be applied to this specific Ingress Controller.

**Related variables**:
- [`ocp_ingress_update_timeouts`](#ocp_ingress_update_timeouts) - Timeout settings apply to this controller
- [`ocp_ingress_namespace_ownership`](#ocp_ingress_namespace_ownership) - Namespace policy applies to this controller

**Notes**:
- Most OpenShift clusters use only the `default` Ingress Controller
- Custom Ingress Controllers are rare and typically used for advanced routing scenarios
- Verify the controller name exists before configuring

### ocp_ingress_update_timeouts
Enable custom timeout configuration for the OpenShift Ingress Controller.

- Optional
- Environment Variable: `OCP_INGRESS_UPDATE_TIMEOUTS`
- Default: `false`

**Purpose**: Controls whether to apply custom client and server timeout values to the Ingress Controller.

**When to use**: Enable when experiencing timeout issues with long-running MAS operations such as large file uploads, report generation, or data imports.

**Valid values**:
- `true` - Apply custom timeout values
- `false` - Use default OpenShift timeout values (30s)

**Impact**: When enabled, updates the IngressController with the values specified in `ocp_ingress_client_timeout` and `ocp_ingress_server_timeout`.

**Related variables**: `ocp_ingress_client_timeout`, `ocp_ingress_server_timeout`

**Notes**:
- Default 30s timeout may be insufficient for MAS Manage operations
- Recommended to enable for production MAS deployments
- Changes apply to all routes in the cluster

### ocp_ingress_client_timeout
Client-side timeout duration for ingress connections.

- Optional
- Environment Variable: `OCP_INGRESS_CLIENT_TIMEOUT`
- Default: `30s`

**Purpose**: Specifies how long a connection is held open while waiting for a client to send data or complete a request.

**When to use**: Increase when clients need more time to upload large files or send data to MAS applications.

**Valid values**: Duration string with unit suffix (e.g., `30s`, `5m`, `1h`). Common values:
- `30s` - Default, suitable for most operations
- `5m` - Recommended for MAS Manage file uploads
- `10m` - For very large file operations

**Impact**: Connections from clients will be kept alive for this duration while waiting for data. Too short may cause upload failures; too long may consume resources.

**Related variables**: `ocp_ingress_update_timeouts` (must be `true`), `ocp_ingress_server_timeout`

**Notes**:
- Only applies when `ocp_ingress_update_timeouts` is `true`
- Consider network latency and file sizes when setting
- Affects all routes in the cluster
- Balance between user experience and resource consumption

### ocp_ingress_server_timeout
Server-side timeout duration for ingress connections.

- Optional
- Environment Variable: `OCP_INGRESS_SERVER_TIMEOUT`
- Default: `30s`

**Purpose**: Specifies how long a connection is held open while waiting for a server (backend application) to respond.

**When to use**: Increase when MAS applications perform long-running operations like report generation, data processing, or complex queries.

**Valid values**: Duration string with unit suffix (e.g., `30s`, `5m`, `1h`). Common values:
- `30s` - Default, suitable for most operations
- `5m` - Recommended for MAS Manage report generation
- `10m` - For complex data processing operations
- `30m` - For very long-running batch operations

**Impact**: Backend connections will be kept alive for this duration while waiting for responses. Too short may cause operation failures; too long may mask application issues.

**Related variables**: `ocp_ingress_update_timeouts` (must be `true`), `ocp_ingress_client_timeout`

**Notes**:
- Only applies when `ocp_ingress_update_timeouts` is `true`
- Critical for MAS Manage report generation and data imports
- Affects all routes in the cluster
- Monitor application logs to determine appropriate values

### ocp_ingress_namespace_ownership
Specifies the namespace ownership policy for the Ingress Controller. Set to `InterNamespaceAllowed` to enable path-based routing support, which allows routes to claim the same hostname across different namespaces.

- Optional
- Environment Variable: `OCP_INGRESS_NAMESPACE_OWNERSHIP`
- Default Value: Not set (empty string)

!!! note
    When both timeout settings and namespace ownership are configured, they will be applied in a single atomic operation to the IngressController resource.


## Role Variables - OperatorHub

### ocp_operatorhub_disable_redhat_sources
Disable default Red Hat OperatorHub catalog sources.

- Optional
- Environment Variable: `OCP_OPERATORHUB_DISABLE_REDHAT_SOURCES`
- Default: `false`

**Purpose**: Disables the default Red Hat catalog sources (`certified-operators`, `community-operators`, `redhat-operators`) in OperatorHub.

**When to use**: Required for air-gapped/disconnected environments where external catalog sources are not accessible. Also useful to enforce use of mirrored catalogs only.

**Valid values**:
- `true` - Disable default Red Hat catalog sources
- `false` - Leave catalog sources unchanged (default)

**Impact**: When `true`, disables the three default Red Hat catalog sources. Operators must be installed from custom or mirrored catalogs.

**Related variables**: None

**Notes**:
- **Important**: Setting to `false` does NOT re-enable disabled sources
- Required for disconnected/air-gapped MAS installations
- Ensure custom catalogs are configured before disabling defaults
- Affects all operator installations in the cluster
- Cannot install operators from Red Hat catalogs after disabling

## Example Playbook

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    ocp_update_ciphers_for_semeru: True
    ocp_ingress_update_timeouts: True
    ocp_ingress_client_timeout: 30s
    ocp_ingress_server_timeout: 30s
    ocp_ingress_namespace_ownership: InterNamespaceAllowed
    ocp_ingress_controller_name: default
    ocp_operatorhub_disable_redhat_sources: True
  roles:
    - ibm.mas_devops.ocp_config
```


## License
EPL-2.0
