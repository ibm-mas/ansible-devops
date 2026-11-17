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

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`ocp_update_ciphers_for_semeru`](#ocp_update_ciphers_for_semeru) | No | `false` |
| [`ocp_ingress_controller_name`](#ocp_ingress_controller_name) | No | `default` |
| [`ocp_ingress_update_timeouts`](#ocp_ingress_update_timeouts) | No | `false` |
| [`ocp_ingress_client_timeout`](#ocp_ingress_client_timeout) | No | `30s` |
| [`ocp_ingress_server_timeout`](#ocp_ingress_server_timeout) | No | `30s` |
| [`ocp_ingress_namespace_ownership`](#ocp_ingress_namespace_ownership) | No | Not set |
| [`ocp_operatorhub_disable_redhat_sources`](#ocp_operatorhub_disable_redhat_sources) | No | `false` |
| [`ocp_enable_ipv6`](#ocp_enable_ipv6) | No | `false` |
| [`cluster_type`](#cluster_type) | No | None |
| [`cluster_name`](#cluster_name) | No | Not set |
| [`rosa_token`](#rosa_token) | Conditional | None |
| [`ocp_update_allowed_registries`](#ocp_update_allowed_registries) | No | `false` |
| [`ocp_allowed_registries`](#ocp_allowed_registries) | No | `[]` |
| [`ocp_add_mas_registries`](#ocp_add_mas_registries) | No | `true` |
| [`ocp_add_rh_registries`](#ocp_add_rh_registries) | No | `true` |
| [`ocp_update_additional_trusted_ca`](#ocp_update_additional_trusted_ca) | No | `false` |
| [`ocp_additional_trusted_ca_dir`](#ocp_additional_trusted_ca_dir) | No | `/tmp` |

`rosa_token` is only required when `cluster_type=rosa-hcp`; the allowed registries and additional trusted CA settings currently work with ROSA HCP clusters only.

### API Server

#### ocp_update_ciphers_for_semeru
Apply a custom TLS security profile — including ciphers compatible with the IBM Java Semeru runtime — to both the `APIServer` and `IngressController` resources. Required when running MAS applications (particularly Manage) in FIPS mode with IBM Java Semeru runtime.

- **Optional**
- Environment Variable: `OCP_UPDATE_CIPHERS_FOR_SEMERU`
- Default: `false`

When enabled, the `tlsSecurityProfile` on both resources is updated to enable TLS 1.3 ciphers `TLS_AES_128_GCM_SHA256`, `TLS_AES_256_GCM_SHA384`, and `TLS_CHACHA20_POLY1305_SHA256`, plus TLS 1.2 ciphers `ECDHE-ECDSA-AES128-GCM-SHA256`, `ECDHE-RSA-AES128-GCM-SHA256`, `ECDHE-ECDSA-AES256-GCM-SHA384`, `ECDHE-RSA-AES256-GCM-SHA384`, `ECDHE-ECDSA-CHACHA20-POLY1305`, `ECDHE-RSA-CHACHA20-POLY1305`, `DHE-RSA-AES128-GCM-SHA256`, `DHE-RSA-AES256-GCM-SHA384`, `ECDHE-RSA-AES128-SHA256`, `ECDHE-RSA-AES128-SHA`, and `ECDHE-RSA-AES256-SHA`.

!!! warning
    Changes affect the cluster-wide TLS configuration, may require a cluster restart to fully apply, and should be verified for compatibility with other applications in the cluster.

### Ingress Controller

#### ocp_ingress_controller_name
Name of the Ingress Controller to configure — `default` (the default cluster Ingress Controller, most common) or any custom Ingress Controller name in your cluster.

- **Optional**
- Environment Variable: `OCP_INGRESS_CONTROLLER_NAME`
- Default: `default`

Both the timeout settings ([`ocp_ingress_update_timeouts`](#ocp_ingress_update_timeouts)) and the namespace ownership policy ([`ocp_ingress_namespace_ownership`](#ocp_ingress_namespace_ownership)) are applied to this controller. Custom Ingress Controllers are rare and typically used for advanced routing scenarios — verify the controller name exists before configuring.

#### ocp_ingress_update_timeouts
Whether to apply custom client and server timeout values to the Ingress Controller — enable when experiencing timeout issues with long-running MAS operations such as large file uploads, report generation, or data imports.

- **Optional**
- Environment Variable: `OCP_INGRESS_UPDATE_TIMEOUTS`
- Default: `false`

When enabled, the IngressController is updated with the values from [`ocp_ingress_client_timeout`](#ocp_ingress_client_timeout) and [`ocp_ingress_server_timeout`](#ocp_ingress_server_timeout). The default OpenShift timeout (30s) may be insufficient for MAS Manage operations — enabling this is recommended for production MAS deployments. Changes apply to all routes in the cluster.

#### ocp_ingress_client_timeout
Client-side timeout duration for ingress connections — how long a connection is held open while waiting for a client to send data or complete a request. A duration string with unit suffix (e.g. `30s`, `5m`, `1h`).

- **Optional**
- Environment Variable: `OCP_INGRESS_CLIENT_TIMEOUT`
- Default: `30s`

Common values: `30s` (default, suitable for most operations), `5m` (recommended for MAS Manage file uploads), `10m` (very large file operations). Only applies when [`ocp_ingress_update_timeouts`](#ocp_ingress_update_timeouts) is `true`; affects all routes in the cluster. Consider network latency and file sizes when setting — too short may cause upload failures, too long may consume resources.

#### ocp_ingress_server_timeout
Server-side timeout duration for ingress connections — how long a connection is held open while waiting for a backend application to respond. A duration string with unit suffix (e.g. `30s`, `5m`, `1h`).

- **Optional**
- Environment Variable: `OCP_INGRESS_SERVER_TIMEOUT`
- Default: `30s`

Common values: `30s` (default, suitable for most operations), `5m` (recommended for MAS Manage report generation), `10m` (complex data processing operations), `30m` (very long-running batch operations). Only applies when [`ocp_ingress_update_timeouts`](#ocp_ingress_update_timeouts) is `true`; affects all routes in the cluster — monitor application logs to determine appropriate values.

#### ocp_ingress_namespace_ownership
Namespace ownership policy for the Ingress Controller — set to `InterNamespaceAllowed` to enable path-based routing support, which allows routes to claim the same hostname across different namespaces.

- **Optional**
- Environment Variable: `OCP_INGRESS_NAMESPACE_OWNERSHIP`
- Default: Not set

!!! note
    When both timeout settings and namespace ownership are configured, they are applied in a single atomic operation to the IngressController resource.

### OperatorHub

#### ocp_operatorhub_disable_redhat_sources
Whether to disable the default Red Hat OperatorHub catalog sources (`certified-operators`, `community-operators`, `redhat-operators`) — required for air-gapped/disconnected environments where external catalog sources are not accessible, and useful to enforce the use of mirrored catalogs only.

- **Optional**
- Environment Variable: `OCP_OPERATORHUB_DISABLE_REDHAT_SOURCES`
- Default: `false`

When `true`, the three default Red Hat catalog sources are disabled and operators must be installed from custom or mirrored catalogs — ensure custom catalogs are configured before disabling the defaults. Affects all operator installations in the cluster.

!!! warning
    Setting to `false` does **not** re-enable disabled sources. Operators cannot be installed from Red Hat catalogs after disabling.

### IPv6 Networking

#### ocp_enable_ipv6
Enable dual-stack IPv4/IPv6 networking on the cluster — adds an IPv6 cluster network (`fd01::/48`) and service network (`fd02::/112`), then waits for all cluster operators and nodes to become healthy, verifies all workers have IPv6 configured, and approves any pending node CSRs.

- **Optional**
- Environment Variable: `OCP_ENABLE_IPV6`
- Default: `false`

Only required for Fyre clusters at the RTP (Research Triangle Park) site — SVL (San Jose/Silicon Valley, the default site) and other sites use IPv4.

### ROSA-HCP Settings

#### cluster_type
Deployment model of OpenShift — currently only used for `rosa-hcp` (AWS ROSA HCP), which triggers the deployment-model-specific tasks such as updating allowed registries and additional trusted CAs.

- **Optional**
- Environment Variable: `CLUSTER_TYPE`
- Default: None

#### cluster_name
Name of the OpenShift cluster — used as the target cluster for rosa CLI commands.

- **Optional**
- Environment Variable: `CLUSTER_NAME`
- Default: Not set

Currently only used for `rosa-hcp`.

#### rosa_token
ROSA login token for the rosa CLI, authenticating it against the ROSA cluster.

- **Required** (when `cluster_type=rosa-hcp`)
- Environment Variable: `ROSA_TOKEN`
- Default: None

### Allowed Registries

#### ocp_update_allowed_registries
Whether to update the cluster's allowed registries list, restricting image pulls to only the defined registries — required for air-gapped/disconnected environments.

- **Optional**
- Environment Variable: `OCP_UPDATE_ALLOWED_REGISTRIES`
- Default: `false`

When `true`, the allowed registries are set from [`ocp_allowed_registries`](#ocp_allowed_registries), optionally extended by [`ocp_add_mas_registries`](#ocp_add_mas_registries) and [`ocp_add_rh_registries`](#ocp_add_rh_registries); all other registries are blocked. ROSA HCP automatically adds the Red Hat required registries `image-registry.openshift-image-registry.svc:5000`, `quay.io`, and `registry.redhat.io`.

!!! warning
    Currently works with ROSA HCP only. Setting to `false` does **not** remove the allowed registries list.

#### ocp_allowed_registries
List of allowed registries to add to the cluster, beyond those defined by MAS and Red Hat — for air-gapped/disconnected environments, provide the domain(s) of your own image registry or registries.

- **Optional**
- Environment Variable: `OCP_ALLOWED_REGISTRIES`
- Default: `[]`

Pods in the cluster can pull images only from the registries in the defined list.

!!! warning
    Currently works with ROSA HCP only. Setting to `[]` does **not** remove the allowed registries list. When exporting `OCP_ALLOWED_REGISTRIES`, use a comma-separated string — for example `export OCP_ALLOWED_REGISTRIES=mas.ibm.com,abc.com`.

#### ocp_add_mas_registries
Whether to add the MAS-specific registries `icr.io`, `cp.icr.io`, `quay.io`, and `gcr.io` on top of those defined in [`ocp_allowed_registries`](#ocp_allowed_registries).

- **Optional**
- Environment Variable: `OCP_ADD_MAS_REGISTRIES`
- Default: `true`

!!! warning
    Currently works with ROSA HCP only.

#### ocp_add_rh_registries
Whether to add the Red Hat-specific registries `icr.io`, `registry.redhat.io`, `registry.connect.redhat.com`, `ghcr.io`, `docker.io`, `nvcr.io`, and `gcr.io` on top of those defined in [`ocp_allowed_registries`](#ocp_allowed_registries).

- **Optional**
- Environment Variable: `OCP_ADD_RH_REGISTRIES`
- Default: `true`

!!! warning
    Currently works with ROSA HCP only.

### Additional Trusted CA

#### ocp_update_additional_trusted_ca
Whether to update the cluster's additional trusted CAs — adding the CAs of the image registries to be used so that the cluster can trust them. Required for air-gapped/disconnected environments.

- **Optional**
- Environment Variable: `OCP_UPDATE_ADDITIONAL_TRUSTED_CA`
- Default: `false`

!!! warning
    Currently works with ROSA HCP only, and setting to `false` does **not** remove additional trusted CAs. If [`ocp_additional_trusted_ca_dir`](#ocp_additional_trusted_ca_dir) contains no files, an empty JSON is generated and uploaded to the cluster, which **removes all** additional trusted CAs.

#### ocp_additional_trusted_ca_dir
Path to the directory containing the additional trusted CAs to configure in the cluster — it can contain none, one, or more CAs.

- **Optional**
- Environment Variable: `OCP_ADDITIONAL_TRUSTED_CA_DIR`
- Default: `/tmp`

CA file names must match the registry URL and end with `.crt` (e.g. `ibm.com.crt`). A JSON file named `additional_trusted_ca.json` is created in the same path and deleted at the end. Only applies when [`ocp_update_additional_trusted_ca`](#ocp_update_additional_trusted_ca) is `true`; currently works with ROSA HCP only.

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
    ocp_enable_ipv6: True
  roles:
    - ibm.mas_devops.ocp_config
```

### Setting Additional Trusted CA and Allowed Registries in Rosa HCP

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    cluster_type: "rosa-hcp"
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
