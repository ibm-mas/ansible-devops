sls_install
===========

Install **IBM Suite License Service** and generate configuration that can be directly applied to IBM Maximo Application Suite.

Role Variables
--------------

###### Pre-release support
- `artifactory_username`: Required when using this role for development versions of SLS
- `artifactory_apikey` Required when using this role for development versions of SLS

###### Primary settings
- `sls_catalog_source` Defines the catalog to be used to install SLS. You can set it to      ibm-operator-catalog for release install or ibm-sls-operators for development
- `sls_channel`  Defines which channel of MAS to subscribe to
- `sls_namespace`  Defined the namespace where sls must be installed
- `sls_icr_cp` when installing release version of MAS or `wiotp-docker-local.artifactory.swg-devops.com` for dev
- `sls_icr_cpopen` when installing release version of MAS or `wiotp-docker-local.artifactory.swg-devops.com` for dev
- `sls_instance_name` Defines the instance id to be used for SLS installation
- `sls_entitlement_username` Username for entitled registry. This username will be used to create the image pull secret. Set to `cp` when installing release or use your `w3Id` for dev.
- `sls_entitlement_key`  API Key for entitled registry. This password will be used to create the image pull secret. Set to with IBM entitlement key when installing release or use your
- `sls_storage_class` Defines the Storage Class that can be used by SLS to store data

###### MongoDb settings
Use either `mongodb_cfg_file` or the `mongodb` object to configure the MongoDb for SLS to use

- `mongodb_cfg_file` Defines the path to the mongodb configuration used with MAS, when defined the SLS role will extract the configuration from there.
- `mongodb` Defines custom configuration for mongodb to be used with SLS, all the follwing facts are required when this fact is defined
    - `mongodb.hosts` Defines list of host and port pair for MongoDb to be used with SLS
    - `mongodb.username` Defines the MongoDB Username
    - `mongodb.password` Defines the MongoDb Password
- `bootstrap` Bootstrap is used to initialize SLS, provide if you do have a lic file and licenseId you want to use
    - `bootstrap.license_id` Defines the License Id to be used to bootstrap SLS
    - `bootstrap.registration_key`  Defines the Registration Key to be used to bootstrap SLS
    - `bootstrap.entitlement_file` Defines the License File to be used to bootstrap SLS

###### MAS integration
- `mas_instance_id` The instance ID of Maximo Application Suite that the KafkaCfg configuration will target, there
- `mas_config_dir` Defines the directory from where some configs can be pulled from including the entitlement file and mongo configuration
- `mas_instance_id` Used to generate a output slscfg file for MAS
- `sls_cfg_file` Defines the destination dir for the generated SLS configuration for MAS

Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    sls_catalog_source: "{{ lookup('env', 'SLS_CATALOG_SOURCE') | default('ibm-operator-catalog', true) }}"
    sls_channel: "{{ lookup('env', 'SLS_CHANNEL') | default('3.x', true) }}"
    sls_namespace: "{{ lookup('env', 'SLS_NAMESPACE') | default('ibm-sls', true) }}"
    sls_icr_cp: "{{ lookup('env', 'SLS_ICR_CP') | default('cp.icr.io/cp', true) }}"
    sls_icr_cpopen: "{{ lookup('env', 'SLS_ICR_CPOPEN') | default('icr.io/cpopen', true) }}"
    sls_instance_name: "{{ lookup('env', 'SLS_INSTANCE_NAME') | default('sls', true) }}"
    sls_entitlement_username: "{{ lookup('env', 'SLS_ENTITLEMENT_USERNAME') | default('cp', true) }}"
    sls_entitlement_key: "{{ lookup('env', 'SLS_ENTITLEMENT_KEY') }}"
    sls_storage_class: "{{ lookup('env', 'SLS_STORAGE_CLASS') }}"
    sls_domain: "{{ lookup('env', 'SLS_DOMAIN') }}"

    sls_cfg_file: "{{ mas_config_dir }}/sls.yml"

    # You can either provide a mongocfg file from MAS or provide mongo configuration manually
    mongodb_cfg_file: "{{mas_config_dir}}/mongodb.yml"

    # mongodb:
    #    hosts:
    #      - host:
    #      - port:
    #    username: "{{ lookup('env', 'MONGODB_USERNAME') }}"
    #   password: "{{ lookup('env', 'MONGODB_PASSWORD') }}"

    # Bootstrap is used to initialize SLS, provide if you do have a lic file and licenseId you want to use
    bootstrap:
      license_id: "{{ lookup('env', 'SLS_LICENSE_ID') | default('', true) }}"
      registration_key: "{{ lookup('env', 'SLS_REGISTRATION_KEY') | default('', true) }}"
      entitlement_file: "{{mas_config_dir}}/entitlement.lic"
  roles:
    - ibm.mas_devops.sls_install
```

License
-------

EPL-2.0
