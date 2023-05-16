suite_install
===============================================================================

This role install Maximo Application Suite. It internally resolve the namespace based on the `mas_instance_id` as `mas-{mas_instance_id}-core`. By default this role install MAS Operator using Manual Upgrade Strategy. Set `MAS_UPGRADE_STRATEGY` environment variable to Automatic to override it. In the `Manual` upgrade mode, IBM Common Services operators requested by MAS will inherit the upgrade strategy from MAS and their pending install plans approved.


Role Variables
-------------------------------------------------------------------------------
### mas_catalog_source
Defines the catalog to be used to install MAS. You can set it to ibm-operator-catalog for both release as well as for development install

### artifactory_username
Required when using this role for development versions of MAS

### artifactory_token
Required when using this role for development versions of MAS

### mas_channel
Defines which channel of MAS to subscribe to

### mas_domain
Opitional fact, if not provided the role will use the default cluster subdomain

### mas_instance_id
Defines the instance id to be used for MAS installation

### mas_icr_cp
Defines the entitled registry from the images should be pulled from. Set this to `cp.icr.io/cp` when installing release version of MAS or `docker-na-public.artifactory.swg-devops.com/wiotp-docker-local` for dev

### mas_icr_cpopen
Defines the registry for non entitled images, such as operators. Set this to `icr.io/cpopen` when installing release version of MAS or `docker-na-public.artifactory.swg-devops.com/wiotp-docker-local/cpopen` for dev

### mas_entitlement_username
Username for entitled registry. This username will be used to create the image pull secret. Set to `cp` when installing release or use your `w3Id` for dev.

### mas_entitlement_key
API Key for entitled registry. This password will be used to create the image pull secret. Set to with IBM entitlement key when installing release or use your artifactory `apikey` for dev.

### mas_config_dir
Directory containing configuration files (`*.yaml` and `*.yml`) to be applied to the MAS installation.  Intended for creating the various MAS custom resources to configure the suite post-install, but can be used to apply any kubernetes resource you need to customize any aspect of your cluster.

### certManager.namespace
The namespace containing the cert-manager to be used by MAS

### mas_upgrade_strategy
The Upgrade strategy for MAS Operator. Default is set to Automatic

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
- Environment Variable: `CUSTOM_LABELS`,
- Default: None

### mas_manual_cert_mgmt
Boolean variable that, when set to True, enable manual certificate management.

- Optional
- Environment Variable: `MAS_MANUAL_CERT_MGMT`,
- Default: False


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
