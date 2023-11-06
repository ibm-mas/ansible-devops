ocp_config
===============================================================================
This role can perform the following configuration:

- Tune the `IngressController` to avoid request failures due to timeout for long running requests
- Update `APIServer` and `IngressController` to set a custom `tlsSecurityProfile` to accommodate ciphers supported by IBM Java Semeru runtime. This is required for allowing the Java applications using Semeru runtime to run in FIPS mode.  The following cipers will be enabled:
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


Role Variables - API Server
-------------------------------------------------------------------------------
### ocp_update_ciphers_for_semeru
Set to `True` if you want to configure the API Server and Ingress Controller to use a custom set of ciphers that are compatible with IBM Java Semeru in FIPS mode.

- Optional
- Environment Variable: `OCP_UPDATE_CIPHERS_FOR_SEMERU`
- Default Value: `False`


Role Variables - Ingress Controller
-------------------------------------------------------------------------------
### ocp_ingress_update_timeouts
Set to `True` if you want to customize the Ingress's client and server timeout values

- Optional
- Environment Variable: `OCP_INGRESS_UPDATE_TIMEOUTS`
- Default Value: `False`

### ocp_ingress_client_timeout
Specifies how long a connection is held open while waiting for a client response

- Optional
- Environment Variable: `OCP_INGRESS_CLIENT_TIMEOUT`
- Default Value: `30s`

### ocp_ingress_server_timeout
Specifies how long a connection is held open while waiting for a server response

- Optional
- Environment Variable: `OCP_INGRESS_SERVER_TIMEOUT`
- Default Value: `30s`


Role Variables - OperatorHub
-------------------------------------------------------------------------------
### ocp_operatorhub_disable_redhat_sources
Set to `True` if you want to disable the default Red Hat catalog sources

- Optional
- Environment Variable: `OCP_OPERATORHUB_DISABLE_REDHAT_SOURCES`
- Default Value: `False`

!!! note
    Setting this to `False` will not enable the default catalog sources if they are currently disabled, it will just instruct this role to take no action.

Example Playbook
-------------------------------------------------------------------------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    ocp_update_ciphers_for_semeru: True
    ocp_ingress_update_timeouts: True
    ocp_ingress_client_timeout: 30s
    ocp_ingress_server_timeout: 30s
    ocp_operatorhub_disable_redhat_sources: True
  roles:
    - ibm.mas_devops.ocp_config
```


License
-------------------------------------------------------------------------------
EPL-2.0
