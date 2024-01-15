sls
===============================================================================

Install **IBM Suite License Service** and generate a configuration that can be directly applied to IBM Maximo Application Suite.

The role assumes that you have already installed the Certificate Manager in the target cluster.  This action is performed by the [cert_manager](cert_manager.md) role if you want to use this collection to install the cert-manager operator.


Role Variables
-------------------------------------------------------------------------------
### sls_action
Inform the role whether to perform an install or uninstall of the Suite License Service.

- Optional
- Environment Variable: `SLS_ACTION`
- Default: `install`


Role Variables - Installation
-------------------------------------------------------------------------------
If `sls_url` is set then the role will skip the installation of an SLS instance and simply generate the SLSCfg resource for the SLS instance defined.

### artifactory_username
Provide your artifactory username, primarily used to update the image pull secret in development.

- Optional
- Environment Variable: `ARTIFACTORY_USERNAME`
- Default: None

### artifactory_token
Provide your artifactory api key, primarily used to update the image pull secret in development.

- Optional
- Environment Variable: `ARTIFACTORY_TOKEN`
- Default: None

### sls_catalog_source
Defines the OLM catalog to be used to install SLS. Set to `ibm-sls-operators` if you want to deploy pre-release development builds of SLS or leave as the default `ibm-operator-catalog` for the released versions.

- Optional
- Environment Variable: `SLS_CATALOG_SOURCE`
- Default: `ibm-operator-catalog`

### sls_channel
The SLS OLM subscription channel to be installed.

- Optional
- Environment Variable: `SLS_CHANNEL`
- Default: `3.x`

### sls_namespace
Define the namespace where sls must be installed.

- Optional
- Environment Variable: `SLS_NAMESPACE`
- Default: `ibm-sls`

### sls_icr_cpopen
The container registry source for all container images deployed by the SLS operator. From SLS 3.8.0 onwards this will be the only variable to set the registry. Override to use development images.

- Optional
- Environment Variable: `SLS_ICR_CPOPEN`
- Default: `icr.io/cpopen`

### sls_instance_name
Defines the instance ID to be used for SLS installation.

- Optional
- Environment Variable: `SLS_INSTANCE_NAME`
- Default: `sls`

### sls_icr_cp [Deprecated in SLS 3.8.0]
The container registry source for all container images deployed by the SLS operator. The api-licensing container image has moved to `icr.io/cpopen` in SLS 3.8.0. Set this variable for SLS 3.7.0 and lower. Override to use development images.

- Optional
- Environment Variable: `SLS_ICR_CP`
- Default: `cp.icr.io/cp`

### ibm_entitlement_key [Deprecated in SLS 3.8.0]
Provide your [IBM entitlement key](https://myibm.ibm.com/products-services/containerlibrary). This is now deprecated in SLS 3.8.0. Provide this only for versions up to 3.7.0.

- **Required** unless `sls_url` is provided
- Environment Variable: `IBM_ENTITLEMENT_KEY`
- Default: None

### sls_entitlement_username [Deprecated in SLS 3.8.0]
Username for entitled registry. This username will be used to create the image pull secret. This is now deprecated in SLS 3.8.0. Provide this only for versions up to 3.7.0.

- Optional
- Environment Variable: `SLS_ENTITLEMENT_USERNAME`
- Default: `cp`

### sls_entitlement_key [Deprecated in SLS 3.8.0]
An IBM entitlement key specific for SLS installation, primarily used to override `ibm_entitlement_key` in development. This is now deprecated in SLS 3.8.0. Provide this only for versions up to 3.7.0.

- Optional
- Environment Variable: `SLS_ENTITLEMENT_KEY`
- Default: None


Role Variables - Configuration
-------------------------------------------------------------------------------
### sls_domain
SLS can be configured to be externally accessible through a route by setting the domain. Set the domain if SLS is used by application suites that are installed in separate OpenShift clusters.

- Optional
- Environment Variable: `SLS_DOMAIN`
- Default: None

### sls_auth_enforce
Determines whether authorization is enforced. If set to true, clients must use mTLS with certificates generated from the client registration flow for SLS API calls.

- Optional
- Environment Variable: `SLS_AUTH_ENFORCE`
- Default: `True`

### sls_mongo_retrywrites
Set to true if MongoDB support retryable writes. In case if retryable writes is not supported (like in case of Amazon DocumentDB), set to false

- Optional
- Environment Variable: `SLS_MONGO_RETRYWRITES`
- Default: `true`

### sls_compliance_enforce
Determines whether compliance is enforced. If there are not enough tokens to support the request. If compliance is not enforced, license checkout requests will be allowed even if there are not enough tokens to support the request.

- Optional
- Environment Variable: `SLS_COMPLIANCE_ENFORCE`
- Default: `True`

### sls_registration_open
Determines whether registration is open. If set to true, clients will be able to register themselves with SLS and use SLS APIs.

- Optional
- Environment Variable: `SLS_REGISTRATION_OPEN`
- Default: `True`

### sls_mongodb_cfg_file
Location of a MAS MongoCfg definition (as generated by the `mongodb` role).  If provided the role will use the information in that config file to configure SLS.

- Either `sls_mongodb_cfg_file` or the `sls_mongodb` object are required to install SLS.
- Environment Variable: `SLS_MONGODB_CFG_FILE`
- Default: None

### sls_mongodb.hosts
Defines list of host and port pair for MongoDb to be used with SLS.

- Either `sls_mongodb_cfg_file` or the `sls_mongodb` object are required to install SLS.
- Environment Variable: None
- Default: None

### sls_mongodb.certificates
Defines list of Certificates for MongoDb to be used with SLS.

- Either `sls_mongodb_cfg_file` or the `sls_mongodb` object are required to install SLS.
- Environment Variable: None
- Default: None

### sls_mongodb.username
Defines the MongoDB Username.

- Either `sls_mongodb_cfg_file` or the `sls_mongodb` object are required to install SLS.
- Environment Variable: None
- Default: None

### sls_mongodb.password
Defines the MongoDb Password.

- Either `sls_mongodb_cfg_file` or the `sls_mongodb` object are required to install SLS.
- Environment Variable: None
- Default: None

### mas_pod_templates_dir
Provide the directory where supported pod templates configuration files are defined.  This role will look for a configuration file named `ibm-sls-licenseservice.yml` in the named directory.  The content of the configuration file should be the yaml block that you wish to be inserted into the LicenseService spec under a top level `podTemplates` element, e.g. `podTemplates: {object}`.

For examples refer to the [BestEfforts reference configuration in the MAS CLI](https://github.com/ibm-mas/cli/blob/master/image/cli/mascli/templates/pod-templates/best-effort/ibm-sls-licenseservice.yml), for full documentation of the supported options refer to the [Customizing Pod Templates](https://www.ibm.com/docs/en/mas-cd/continuous-delivery?topic=sls-supported-pods-workload-customization-in-suite-license-service) in the product documentation.

- Optional
- Environment Variable: `MAS_POD_TEMPLATES_DIR`
- Default: None


Role Variables - Bootstrap [SLS 3.7.0 and higher]
-------------------------------------------------------------------------------

### entitlement_file
Defines the License File to be used to bootstrap SLS. Don't set if you wish to setup entitlement later on.

- Optional
- Environment Variable: `SLS_ENTITLEMENT_FILE`
- Default: None


Role Variables - Bootstrap [Partly deprecated in SLS 3.7.0]
-------------------------------------------------------------------------------
### bootstrap.license_file [Deprecated in SLS 3.7.0]
Defines the License File to be used to bootstrap SLS. Don't set if you wish to setup entitlement later on. Note: this variable used to be called bootstrap.entitlement_file and defaulted to `{{mas_config_dir}}/entitlement.lic`, this is no longer the case and `SLS_LICENSE_FILE` has to be set in order to bootstrap. This is now deprecated in SLS 3.7.0. Use this only for versions up to 3.6.0.

- Optional
- Environment Variable: `SLS_LICENSE_FILE`
- Default: None

### bootstrap.license_id [Deprecated in SLS 3.7.0]
Defines the License Id to be used to bootstrap SLS. This must be set when `bootstrap.license_file` is also set and should match the licenseId from the license file. Don't set if you wish to setup entitlement later on. Note: this is now deprecated in SLS 3.7.0. Use this only for versions up to 3.6.0.

- Optional unless `bootstrap.license_file` is set
- Environment Variable: `SLS_LICENSE_ID`
- Default: None

### bootstrap.registration_key
Defines the Registration Key to be used to bootstrap SLS. Don't set if you wish to setup entitlement later on

- Optional
- Environment Variable: `SLS_REGISTRATION_KEY`
- Default: None


Role Variables - SLSCfg
-------------------------------------------------------------------------------
### mas_instance_id
The instance ID of Maximo Application Suite that the SlsCfg configuration will target.

- Optional, if this or `mas_config_dir` are not set then the role will not generate a SlsCfg template
- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### mas_config_dir
Local directory to save the generated SlsCfg resource definition.  This can be used to manually configure a MAS instance to connect to SLS instance, or used as an input to the [suite_config](suite_config.md) role. If this or `mas_instance_id` are not set then the role will not generate a SlsCfg template.

- Optional, if this or `mas_config_dir` are not set then the role will not generate a SlsCfg template
- Environment Variable: `MAS_CONFIG_DIR`
- Default Value: None

### sls_url
The URL of the LicenseService to be called when the Maximo Application Suite is registered with SLS.

- Optional, used to instruct the role to set up MAS for an existing SLS instance.
- Environment Variable: `SLS_URL`
- Default Value: None

### mas_license_sync_frequency
The sync frequency of user license sync cronjob between Maximo Application Suite and SLS.

- Optional
- Environment Variable: `MAS_LICENSE_SYNC_FREQUENCY`
- Default Value: `*/30 * * * *`

### sls_tls_crt
The TLS CA certificate of the LicenseService to be used when the Maximo Application Suite is registered with SLS.  Takes precedence over  `sls_tls_crt_local_file_path`.

- Optional, used to instruct the role to set up MAS for an existing SLS instance.
- Environment Variable: `SLS_TLS_CERT`
- Default Value: None

### sls_tls_crt_local_file_path
The path on the local system to a file containing the TLS CA certificate of the LicenseService to be used when the Maximo Application Suite is registered with SLS.  This variable is only used if `sls_tls_crt` has not been set.

- Optional, used to instruct the role to set up MAS for an existing SLS instance.
- Environment Variable: `SLS_TLS_CERT_LOCAL_FILE`
- Default Value: None

### sls_registration_key
The Registration key of the LicenseService instance to be used when the Maximo Application Suite is registered with SLS.

- Optional
- Environment Variable: `SLS_REGISTRATION_KEY`
- Default Value: None

### custom_labels
List of comma separated key=value pairs for setting custom labels on instance specific resources.

- Optional
- Environment Variable: `CUSTOM_LABELS`
- Default Value: None

### mas_pod_templates_dir
Provide the directory where supported pod templates configuration files are defined.  This role will look for a configuration file named `ibm-mas-slscfg.yml` in the named directory.  The content of the configuration file should be the yaml block that you wish to be inserted into the SlsCfg spec under a top level `podTemplates` element, e.g. `podTemplates: {object}`.

For examples refer to the [BestEfforts reference configuration in the MAS CLI](https://github.com/ibm-mas/cli/blob/master/image/cli/mascli/templates/pod-templates/best-effort/ibm-mas-slscfg.yml), for full documentation of the supported options refer to the [Customizing Pod Templates](https://www.ibm.com/docs/en/mas-cd/continuous-delivery?topic=configuring-customizing-workloads) in the product documentation.

- Optional
- Environment Variable: `MAS_POD_TEMPLATES_DIR`
- Default: None

Example Playbook
-------------------------------------------------------------------------------

### Install and generate a configuration [up to SLS 3.6.0]
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    ibm_entitlement_key: xxxx
    mas_instance_id: inst1
    mas_config_dir: /home/me/masconfig
    sls_mongodb_cfg_file: "/etc/mas/mongodb.yml"

    bootstrap:
      license_id: "aa78dd65ef10"
      license_file: "/etc/mas/entitlement.lic"
      registration_key: xxxx

  roles:
    - ibm.mas_devops.sls
```

### Install and upload license file [SLS 3.7.0]
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    ibm_entitlement_key: xxxx
    mas_instance_id: inst1
    sls_mongodb_cfg_file: "/etc/mas/mongodb.yml"
    entitlement_file: "/etc/mas/entitlement.lic"

  roles:
    - ibm.mas_devops.sls
```

### Install and upload license file [from SLS 3.8.0]
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: inst1
    sls_mongodb_cfg_file: "/etc/mas/mongodb.yml"
    entitlement_file: "/etc/mas/entitlement.lic"

  roles:
    - ibm.mas_devops.sls
```

### Generate a configuration for an existing installation
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: inst1
    mas_config_dir: /home/me/masconfig

    sls_tls_crt_local_file_path: "/home/me/sls.crt"
    slscfg_url: "https://xxx"
    slscfg_registration_key: "xxx"

  roles:
    - ibm.mas_devops.sls
```


License
-------------------------------------------------------------------------------

EPL-2.0
