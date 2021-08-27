suite_install
=============

TODO: Summarize role

Role Variables
--------------
- `mas_catalog_source` Defines the catalog to be used to install MAS. You can set it to      ibm-operator-catalog for release install or ibm-mas-operators for development
- `artifactory_username` Required when using this role for development versions of MAS
- `artifactory_apikey` Required when using this role for development versions of MAS
- `mas_channel` Defines which channel of MAS to subscribe to
- `mas_domain` Opitional fact, if not provided the role will use the default cluster subdomain
- `mas_instance_id` Defines the instance id to be used for MAS installation
- `mas_icr_cp` Defines the entitled registry from the images should be pulled from. Set this to `cp.icr.io/cp` when installing release version of MAS or `wiotp-docker-local.artifactory.swg-devops.com` for dev
- `mas_icr_cpopen` Defines the registry for non entitled images, such as operators. Set this to `icr.io/cpopen` when installing release version of MAS or `wiotp-docker-local.artifactory.swg-devops.com` for dev
- `mas_entitlement_username` Username for entitled registry. This username will be used to create the image pull secret. Set to `cp` when installing release or use your `w3Id` for dev.
- `mas_entitlement_key` API Key for entitled registry. This password will be used to create the image pull secret. Set to with IBM entitlement key when installing release or use your artifactory `apikey` for dev.
- `mas_config` List of configuration files to be applied to configure the MAS installation


Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    # Which MAS channel to subscribe to
    mas_channel: "{{ lookup('env', 'MAS_CHANNEL') | default('8.x', true) }}"

    # MAS configuration
    custom_domain: "{{ lookup('env', 'MAS_DOMAIN') | default(None)}}"
    mas_instance_id: "{{ lookup('env', 'MAS_INSTANCE_ID') }}"

    # MAS configuration - Entitlement
    mas_entitlement_key: "{{ lookup('env', 'MAS_ENTITLEMENT_KEY') }}"

    mas_config_dir: "{{ lookup('env', 'MAS_CONFIG_DIR') }}"

  roles:
    - ibm.mas_devops.suite_install
    - ibm.mas_devops.suite_config
    - ibm.mas_devops.suite_verify
```

License
-------

EPL-2.0
