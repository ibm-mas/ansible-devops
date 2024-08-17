suite_install
===============================================================================
This role install Maximo Application Suite. It internally resolve the namespace based on the `mas_instance_id` as `mas-{mas_instance_id}-core`.


Role Variables - Basic Install
-------------------------------------------------------------------------------
### mas_catalog_source
Defines the catalog to be used to install MAS. You can set it to ibm-operator-catalog for both release as well as for development install

### mas_channel
Defines which channel of MAS to subscribe to


Role Variables - Basic Configuration
-------------------------------------------------------------------------------
### mas_domain
Optional fact, if not provided the role will use the default cluster subdomain

### mas_instance_id
Defines the instance id to be used for MAS installation

### mas_entitlement_key
API Key for entitled registry. This password will be used to create the image pull secret. Set to with IBM entitlement key when installing release or use your artifactory `apikey` for dev.

### mas_config_dir
Directory containing configuration files (`*.yaml` and `*.yml`) to be applied to the MAS installation.  Intended for creating the various MAS custom resources to configure the suite post-install, but can be used to apply any kubernetes resource you need to customize any aspect of your cluster.


Role Variables - Advanced Configuration
-------------------------------------------------------------------------------
### certManager.namespace
The namespace containing the cert-manager to be used by MAS

### mas_annotations
Provide a list of comma-separated key=value pairs which will be applied as labels on all resources created.  This variable takes a comma separated list of annotations. For example, to deploy your suite in non production mode, set this to `mas.ibm.com/operationalMode=nonproduction`
or set `MAS_ANNOTATIONS` environment variable as `export MAS_ANNOTATIONS=mas.ibm.com/operationalMode=nonproduction`

- Optional
- Environment Variable: `MAS_ANNOTATIONS`
- Default: None

### mas_img_pull_policy
Sets `spec.settings.imagePullPolicy`, controlling the pod image pull policies in the suite (`Always`, `IfNotPresent`, `Never`).  When not set the built-in operator default image pull policy will be used.

- Optional
- Environment Variable: `MAS_IMG_PULL_POLICY`
- Default: None

### custom_labels
Provide a list of comma-separated key=value pairs which will be applied as labels on all resources created.

- Optional
- Environment Variable: `CUSTOM_LABELS`
- Default: None

### mas_manual_cert_mgmt
Boolean variable that, when set to True, enable manual certificate management.

- Optional
- Environment Variable: `MAS_MANUAL_CERT_MGMT`
- Default: False

### mas_trust_default_cas
Boolean variable that defines whether default Certificate Authorities are included in MAS trust stores. This only has an effect with IBM Maximo Application Suite version 8.11 and above

- Optional
- Environment Variable: `MAS_TRUST_DEFAULT_CAS`
- Default: True

### mas_pod_templates_dir
Provide the directory where supported pod templates configuration files are defined. This role will look for a configuration files named `ibm-mas-suite.yml`, `ibm-mas-coreidp.yml` and `ibm-data-dictionary-assetdatadictionary.yml` in the named directory.  The content of the configuration file should be the yaml block that you wish to be inserted into the Suite spec under a top level `podTemplates` element, e.g. `podTemplates: {object}`. For ibm-data-dictionary the podTemplates will be inserted into the Suite spec under `settings->dataDictionary->podTemplates`. The ibm-mas-suite operator will then pass this on to the AssetDataDictionary CR when available.

For examples refer to the [BestEfforts reference configuration in the MAS CLI](https://github.com/ibm-mas/cli/blob/master/image/cli/mascli/templates/pod-templates/best-effort/ibm-mas-suite.yml), for full documentation of the supported options refer to the [Customizing Pod Templates](https://www.ibm.com/docs/en/mas-cd/continuous-delivery?topic=configuring-customizing-workloads) in the product documentation.

- Optional
- Environment Variable: `MAS_POD_TEMPLATES_DIR`
- Default: None

### enable_IPv6
Boolean variable that indicates whether it is to install in an IPv6-enabled environment.  If it is true, the suite CR will have the SingleStack for ipFamilyPolicy and ["IPv6"] for ipFamilies.  These ipFamily properties will be populated to all the services. This is currently available only in internal fyre clusters at the RTP site for testing purpose.

- Optional
- Environment Variable: `ENABLE_IPv6`
- Default: False

### eck_enable_logstash
When set to `true` will result in the creation of `filebeat-output` Secret in the MAS Core namespace which will reconfigure all pods to send their logs to an instance of Logstash installed by the [eck role](eck.md) **instead of** sending them to the pod log.

- Optional
- Environment Variable: `ECK_ENABLE_LOGSTASH`
- Default: `false`

### mas_enable_walkme
Boolean variable that indicates whether to enable guided tour.

- Optional
- Environment Variable: `MAS_ENABLE_WALKME`
- Default: `true`

Role Variables - Superuser Account
-------------------------------------------------------------------------------
The MAS Superuser account username and password can be customized during the install by setting **both** of these variable.

### mas_superuser_username

- Optional
- Environment Variable: `MAS_SUPERUSER_USERNAME`
- Default: None

### mas_superuser_password

- Optional
- Environment Variable: `MAS_SUPERUSER_PASSWORD`
- Default: None


Role Variables - Developer Mode
-------------------------------------------------------------------------------
### artifactory_username
Required when using this role with development builds on Artifactory

### artifactory_token
Required when using this role with development builds on Artifactory

### mas_icr_cp
Defines the entitled registry from the images should be pulled from. Set this to `cp.icr.io/cp` when installing release version of MAS, `docker-na-public.artifactory.swg-devops.com/wiotp-docker-local` for dev, unless when on FYRE in which case use `docker-na-proxy-svl.artifactory.swg-devops.com/wiotp-docker-local` or `docker-na-proxy-rtp.artifactory.swg-devops.com/wiotp-docker-local` as appropriate.

### mas_icr_cpopen
Defines the registry for non-entitled images, such as operators. Set this to `icr.io/cpopen` when installing release version of MAS or `docker-na-public.artifactory.swg-devops.com/wiotp-docker-local/cpopen` for dev (or corresponding FYRE proxies as appropriate).

### mas_entitlement_username
Username for the IBM entitled registry. This username will be used to create the image pull secret. Set to `cp` when installing release or use your `w3Id` when using Artifactory.


Example Playbook
-------------------------------------------------------------------------------

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


License
-------

EPL-2.0
