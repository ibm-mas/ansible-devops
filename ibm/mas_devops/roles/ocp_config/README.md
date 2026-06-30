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



## Role Variables - General

### cluster_type
The deployment model of OpenShift.

- **Optional**
- Environment Variable: `CLUSTER_TYPE`
- Default Value: `default`

**Purpose**: Specifies the deployment model of OpenShift to run model specific tasks.

**When to use**: Currently only used for `rosa_hcp`.

**Valid values**:
- `default`  - Currently not in use
- `rosa_hcp` - AWS ROSA HCP

**Impact**: Runs tasks specific to the deployment model.

**Related variables**: None

**Notes**:
- Most OpenShift clusters use only the `default` deployment model

### cluster_name
The name of the OpenShift cluster.

- **Optional**
- Environment Variable: `CLUSTER_NAME`
- Default Value: Not set

**Purpose**: Specifies the name of the OpenShift cluster.

**When to use**: Currently only used for `rosa_hcp`.

**Impact**: Runs tasks against cluster name.

**Related variables**: None

**Notes**:
- This is used as the target cluster for when using rosa cli commands.


## Role Variables - API Server

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
- `ocp_enable_ipv6`: Required for RTP site

**Note**: SVL (San Jose Valley) is the default site. RTP (Research Triangle Park) requires IPv6 enablement.

### ocp_enable_ipv6

Enable IPv6 for Fyre RTP site.

- **Optional**
- Environment Variable: `OCP_ENABLE_IPV6`
- Default: `false`

**Purpose**: Enables IPv6 networking for Fyre clusters at the RTP (Research Triangle Park) site.

**When to use**:

- Set to `true` only for Fyre RTP site clusters
- Leave as `false` for all other sites (including SVL)
- Only applies when `cluster_type=fyre`

**Valid values**: `true`, `false`

**Impact**: Configures network settings for IPv6 connectivity to RTP site clusters.

**Related variables**:

- `cluster_type`: Must be `fyre`
- `fyre_site`: Should be `rtp` when this is `true`

**Note**: Only required for Fyre RTP site. SVL and other sites use IPv4.


## Role Variables - Allowed Registries

### ocp_update_allowed_registries
Update allowed registries in the cluster.

- Optional
- Environment Variable: `OCP_UPDATE_ALLOWED_REGISTRIES`
- Default: `false`

**Purpose**: Restricting access to only registries in the allowed registries list.

**When to use**: Required for air-gapped/disconnected environments.

**Valid values**:
- `true` - Update allowed registries
- `false` - Leave allowed registries unchanged

**Impact**: When `true`, updates the allowed registries to the list provided via `ocp_allowed_registries`, `ocp_add_mas_registries` and/or `ocp_add_rh_registries`. All other registries not defined will be blocked.

**Notes**:
- **Important**: Currently works with ROSA HCP only
- **Important**: Setting to `false` does NOT remove allowed registries list
- Required for disconnected/air-gapped MAS installations
- ROSA HCP automatically adds RH required registries: `'image-registry.openshift-image-registry.svc:5000'`, `quay.io`, and `registry.redhat.io`


### ocp_allowed_registries
List of allowed registries to be added to the cluster.

- Optional
- Environment Variable: `OCP_ALLOWED_REGISTRIES`
- Default: `[]`

**Purpose**: Providing allowed registries beyond what is defined by MAS and RedHat.

**When to use**: Required for air-gapped/disconnected environments. Provide the domain to your own image registry or registries.

**Impact**: Pods in the cluster can pull images from the list of registries defined.

**Notes**:
- **Important**: Currently works with ROSA HCP only
- **Important**: Setting to `[]` does NOT remove allowed registries list
- Required for disconnected/air-gapped MAS installations when using custom image registry


### ocp_add_mas_registries
Adds MAS specific registries on top of what is defined in `ocp_allowed_registries`.

- Optional
- Environment Variable: `OCP_ADD_MAS_REGISTRIES`
- Default: `true`

**Purpose**: Restricting access to only registries in the allowed registries list.

**When to use**: Required for air-gapped/disconnected environments.

**Valid values**:
- `true` - Add MAS registries to `ocp_allowed_registries`
- `false` - Leave `ocp_allowed_registries` unchanged

**Impact**: When `true`, appends the `ocp_allowed_registries` list with `icr.io`, `cp.icr.io`, `quay.io`, and `gcr.io`

**Notes**:
- **Important**: Currently works with ROSA HCP only
- Required for disconnected/air-gapped MAS installations in ROSA HCP


### ocp_add_rh_registries
Adds RedHat specific registries on top of what is defined in `ocp_allowed_registries`.

- Optional
- Environment Variable: `OCP_ADD_RH_REGISTRIES`
- Default: `true`

**Purpose**: Restricting access to only registries in the allowed registries list.

**When to use**: Required for air-gapped/disconnected environments.

**Valid values**:
- `true` - Add RedHat registries to `ocp_allowed_registries`
- `false` - Leave `ocp_allowed_registries` unchanged

**Impact**: When `true`, appends the `ocp_allowed_registries` list with `icr.io`, `registry.redhat.io`, `registry.connect.redhat.com`, `ghcr.io`, `docker.io`, `nvcr.io`, and `gcr.io`

**Notes**:
- **Important**: Currently works with ROSA HCP only
- Required for disconnected/air-gapped MAS installations in ROSA HCP


## Role Variables - Additional Trusted CA

### ocp_update_additional_trusted_ca
Update additional trusted CAs in the cluster.

- Optional
- Environment Variable: `OCP_UPDATE_ADDITIONAL_TRUSTED_CA`
- Default: `false`

**Purpose**: Adding the CAs of the image registries to be used for air-gapped/disconnected environments so that the cluster can trust them.

**When to use**: Required for air-gapped/disconnected environments.

**Valid values**:
- `true` - Update additional trusted CAs
- `false` - Leave additional trusted CAs unchanged

**Impact**: When `true`, adds or removes additional trusted CAs in the cluster.

**Related variables**: None

**Notes**:
- **Important**: Currently works with ROSA HCP only
- **Important**: Setting to `false` does NOT remove additional trusted CAs
- Required for disconnected/air-gapped MAS installations.
- If `ocp_additional_trusted_ca_dir` has no files in it then an empty json will be generated and uploaded to the cluster which will remove all additional trusted CAs from the cluster

### ocp_additional_trusted_ca_dir
The path to the additional trusted CAs.

- Optional
- Environment Variable: `OCP_ADDITIONAL_TRUSTED_CA_DIR`
- Default: `/tmp`

**Purpose**: Directory containing additional trusted CAs to be configured in the cluster.

**When to use**: Required for trusting image registries when setting up air-gapped/disconnected environments.

**Related variables**: `ocp_update_additional_trusted_ca` (must be `true`)

**Notes**:
- **Important**: Currently works with ROSA HCP only
- **Important**: CA file names must match the registry URL and end with `.crt` e.g., `ibm.com.crt`
- You can have none, one or more CAs in the directory
- A JSON file named `additional_trusted_ca.json` is created in the same path and then deleted at the end


## Example Playbook

### Example Playbook
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
    ocp_enable_ipv6: True
  roles:
    - ibm.mas_devops.ocp_config
```

### Setting Additional Trusted CA and Allowed Registries in Rosa HCP
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    cluster_type: "rosa_hcp"
    cluster_name: "rosa-dev-cluster"
    ocp_update_allowed_registries: True
    ocp_allowed_registries:
        - ibm.com
        - mas.io
    ocp_add_mas_registries: True
    ocp_add_rh_registries: True
    ocp_update_additional_trusted_ca: True
    ocp_additional_trusted_ca_dir: /mnt/home/additional_trusted_ca
  roles:
    - ibm.mas_devops.ocp_config
```


## License

EPL-2.0
