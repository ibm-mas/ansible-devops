# suite_install

This role installs Maximo Application Suite. It internally resolves the namespace based on the `mas_instance_id` as `mas-{mas_instance_id}-core`.

## Role Variables

### Basic Install

#### mas_catalog_source
Defines the catalog to be used to install MAS. You can set it to `ibm-operator-catalog` for both release as well as for development install.

- **Optional**
- Environment Variable: `MAS_CATALOG_SOURCE`
- Default: `ibm-operator-catalog`

#### mas_channel
Defines which channel of MAS to subscribe to.

- **Required**
- Environment Variable: `MAS_CHANNEL`
- Default: None

### Basic Configuration

#### mas_domain
Optional fact, if not provided the role will use the default cluster subdomain.

- **Optional**
- Environment Variable: `MAS_DOMAIN`
- Default: None

#### mas_instance_id
Defines the instance id to be used for MAS installation.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

#### mas_entitlement_key
API Key for entitled registry. This password will be used to create the image pull secret. Set to with IBM entitlement key when installing release or use your artifactory `apikey` for dev.

- **Required**
- Environment Variable: `MAS_ENTITLEMENT_KEY`
- Default: Value of `IBM_ENTITLEMENT_KEY` if set

#### mas_config_dir
Directory containing configuration files (`*.yaml` and `*.yml`) to be applied to the MAS installation. Intended for creating the various MAS custom resources to configure the suite post-install, but can be used to apply any kubernetes resource you need to customize any aspect of your cluster.

- **Optional**
- Environment Variable: `MAS_CONFIG_DIR`
- Default: None

### Advanced Configuration

#### mas_annotations
Provide a list of comma-separated key=value pairs which will be applied as annotations on all resources created. This variable takes a comma separated list of annotations. For example, to deploy your suite in non production mode, set this to `mas.ibm.com/operationalMode=nonproduction`.

- **Optional**
- Environment Variable: `MAS_ANNOTATIONS`
- Default: None

#### mas_img_pull_policy
Sets `spec.settings.imagePullPolicy`, controlling the pod image pull policies in the suite (`Always`, `IfNotPresent`, `Never`). When not set the built-in operator default image pull policy will be used.

- **Optional**
- Environment Variable: `MAS_IMG_PULL_POLICY`
- Default: None

#### custom_labels
Provide a list of comma-separated key=value pairs which will be applied as labels on all resources created.

- **Optional**
- Environment Variable: `CUSTOM_LABELS`
- Default: None

#### mas_manual_cert_mgmt
Boolean variable that, when set to True, enable manual certificate management.

- **Optional**
- Environment Variable: `MAS_MANUAL_CERT_MGMT`
- Default: `False`

#### mas_routing_mode
String variable either `path` or `subdomain` that defines the routing mode used for the suite.

- **Optional**
- Environment Variable: `MAS_ROUTING_MODE`
- Default: `subdomain`

#### mas_trust_default_cas
Boolean variable that defines whether default Certificate Authorities are included in MAS trust stores. This only has an effect with IBM Maximo Application Suite version 8.11 and above.

- **Optional**
- Environment Variable: `MAS_TRUST_DEFAULT_CAS`
- Default: `True`

#### mas_pod_templates_dir
Provide the directory where supported pod templates configuration files are defined. This role will look for configuration files named `ibm-mas-suite.yml`, `ibm-mas-coreidp.yml` and `ibm-data-dictionary-assetdatadictionary.yml` in the named directory. The content of the configuration file should be the yaml block that you wish to be inserted into the Suite spec under a top level `podTemplates` element, e.g. `podTemplates: {object}`. For ibm-data-dictionary the podTemplates will be inserted into the Suite spec under `settings->dataDictionary->podTemplates`. The ibm-mas-suite operator will then pass this on to the AssetDataDictionary CR when available.

For examples refer to the [BestEfforts reference configuration in the MAS CLI](https://github.com/ibm-mas/cli/blob/master/image/cli/mascli/templates/pod-templates/best-effort/ibm-mas-suite.yml), for full documentation of the supported options refer to the [Customizing Pod Templates](https://www.ibm.com/docs/en/mas-cd/continuous-delivery?topic=configuring-customizing-workloads) in the product documentation.

- **Optional**
- Environment Variable: `MAS_POD_TEMPLATES_DIR`
- Default: None

#### enable_ipv6
Boolean variable that indicates whether it is to install in an IPv6-enabled environment. If it is true, the suite CR will have the SingleStack for ipFamilyPolicy and ["IPv6"] for ipFamilies. These ipFamily properties will be populated to all the services. This is currently available only in internal fyre clusters at the RTP site for testing purpose.

- **Optional**
- Environment Variable: `ENABLE_IPV6`
- Default: `False`

#### mas_special_characters
Set this to `true` to permit special characters in user IDs and usernames. The suite configuration record (CR) will include a property named `userDataValidation` with the option `allowSpecialChars` configured.

- **Optional**
- Environment Variable: `MAS_SPECIAL_CHARACTERS`
- Default: None

#### eck_enable_logstash
When set to `true` will result in the creation of `filebeat-output` Secret in the MAS Core namespace which will reconfigure all pods to send their logs to an instance of Logstash installed by the [eck role](eck.md) **instead of** sending them to the pod log.

- **Optional**
- Environment Variable: `ECK_ENABLE_LOGSTASH`
- Default: `false`

#### mas_enable_walkme
Boolean variable that indicates whether to enable guided tour.

- **Optional**
- Environment Variable: `MAS_ENABLE_WALKME`
- Default: `true`

### Certificate Management

#### mas_cluster_issuer
Defines the cluster issuer to use for certificate management.

- **Optional**
- Environment Variable: `MAS_CLUSTER_ISSUER`
- Default: None

#### mas_certificate_duration
Defines the duration for certificates.

- **Optional**
- Environment Variable: `MAS_CERTIFICATE_DURATION`
- Default: `8760h0m0s`

#### mas_certificate_renew_before
Defines when to renew certificates before expiration.

- **Optional**
- Environment Variable: `MAS_CERTIFICATE_RENEW_BEFORE`
- Default: `720h0m0s`

### SSO Configuration

#### idle_timeout
Defines the idle timeout for SSO sessions.

- **Optional**
- Environment Variable: `IDLE_TIMEOUT`
- Default: None

#### idp_session_timeout
Defines the IDP session timeout.

- **Optional**
- Environment Variable: `IDP_SESSION_TIMEOUT`
- Default: None

#### access_token_timeout
Defines the access token timeout.

- **Optional**
- Environment Variable: `ACCESS_TOKEN_TIMEOUT`
- Default: None

#### refresh_token_timeout
Defines the refresh token timeout.

- **Optional**
- Environment Variable: `REFRESH_TOKEN_TIMEOUT`
- Default: None

#### default_idp
Defines the default identity provider.

- **Optional**
- Environment Variable: `DEFAULT_IDP`
- Default: None

#### seamless_login
Enables seamless login functionality.

- **Optional**
- Environment Variable: `SEAMLESS_LOGIN`
- Default: None

#### sso_cookie_name
Defines the SSO cookie name.

- **Optional**
- Environment Variable: `SSO_COOKIE_NAME`
- Default: None

#### allow_default_sso_cookie_name
Allows the use of default SSO cookie name.

- **Optional**
- Environment Variable: `ALLOW_DEFAULT_SSO_COOKIE_NAME`
- Default: None

#### use_only_custom_cookie_name
Forces the use of only custom cookie name.

- **Optional**
- Environment Variable: `USE_ONLY_CUSTOM_COOKIE_NAME`
- Default: None

#### disable_ltpa_cookie
Disables LTPA cookie.

- **Optional**
- Environment Variable: `DISABLE_LDAP_COOKIE`
- Default: None

#### allow_custom_cache_key
Allows custom cache key.

- **Optional**
- Environment Variable: `ALLOW_CUSTOM_CACHE_KEY`
- Default: None

### Superuser Account

The MAS Superuser account username and password can be customized during the install by setting **both** of these variables.

#### mas_superuser_username
Defines the superuser username.

- **Optional**
- Environment Variable: `MAS_SUPERUSER_USERNAME`
- Default: None

#### mas_superuser_password
Defines the superuser password.

- **Optional**
- Environment Variable: `MAS_SUPERUSER_PASSWORD`
- Default: None

### Data Dictionary

#### mas_add_catalog
Defines the catalog to be used for the data dictionary add-on.

- **Optional**
- Environment Variable: `MAS_ADD_CATALOG`
- Default: `ibm-operator-catalog`

#### mas_add_channel
Defines the channel for the data dictionary add-on.

- **Optional**
- Environment Variable: `MAS_ADD_CHANNEL`
- Default: None

### Developer Mode

#### artifactory_username
Required when using this role with development builds on Artifactory.

- **Optional**
- Environment Variable: `ARTIFACTORY_USERNAME`
- Default: None

#### artifactory_token
Required when using this role with development builds on Artifactory.

- **Optional**
- Environment Variable: `ARTIFACTORY_TOKEN`
- Default: None

#### mas_icr_cp
Defines the entitled registry from which the images should be pulled from. Set this to `cp.icr.io/cp` when installing release version of MAS, `docker-na-public.artifactory.swg-devops.com/wiotp-docker-local` for dev, unless when on FYRE in which case use `docker-na-proxy-svl.artifactory.swg-devops.com/wiotp-docker-local` or `docker-na-proxy-rtp.artifactory.swg-devops.com/wiotp-docker-local` as appropriate.

- **Optional**
- Environment Variable: `MAS_ICR_CP`
- Default: `cp.icr.io/cp`

#### mas_icr_cpopen
Defines the registry for non-entitled images, such as operators. Set this to `icr.io/cpopen` when installing release version of MAS or `docker-na-public.artifactory.swg-devops.com/wiotp-docker-local/cpopen` for dev (or corresponding FYRE proxies as appropriate).

- **Optional**
- Environment Variable: `MAS_ICR_CPOPEN`
- Default: `icr.io/cpopen`

#### mas_entitlement_username
Username for the IBM entitled registry. This username will be used to create the image pull secret. Set to `cp` when installing release or use your `w3Id` when using Artifactory.

- **Optional**
- Environment Variable: `MAS_ENTITLEMENT_USERNAME`
- Default: `cp`

## Example Playbook

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: "inst1"
    mas_config_dir: "/home/david/masconfig"
    mas_entitlement_key: "{{ lookup('env', 'IBM_ENTITLEMENT_KEY') }}"

  roles:
    - ibm.mas_devops.suite_install
    - ibm.mas_devops.suite_config
    - ibm.mas_devops.suite_verify
```

## License

EPL-2.0
