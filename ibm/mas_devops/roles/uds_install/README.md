uds_install
===========

Installs [IBM User Data Services](https://www.ibm.com/docs/en/cpfs?topic=services-enabling-user-data) as part of [IBM Foundational Services](https://www.ibm.com/docs/en/cpfs?topic=312-installing-foundational-services-by-using-console) in the `ibm-common-services` namespace.  If `mas_instance_id` and the others associated parameters are provided then the role will also generate a configuration file that can be directly applied to IBM Maximo Application Suite.


Role Variables
--------------

### uds_storage_class
Required.  Storage class where BAS will be installed.  On IBM Cloud RedHat Openshift Kubernetes Service (ROKS) `ibmc-block-bronze` is the recommended value.

- Environment Variable: `UDS_STORAGE_CLASS`
- Default Value: None


### uds_event_scheduler_frequency
Defines the frequency that BAS will collect event data. The value can be set following a [cron tab](https://crontab.guru/) format, however support in UDS is limited to the following subset of valid cron formats: `@annually`, `@yearly`, `@monthly`, `@weekly`, `@daily`, `@hourly`.

- Environment Variable: `UDS_EVENT_SCHEDULER_FREQUENCY`
- Default Value: `@daily`

### mas_instance_id
The instance ID of Maximo Application Suite that the BasCfg configuration will target.  If this or `mas_config_dir` are not set then the role will not generate a BasCfg template.

- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### mas_config_dir
Local directory to save the generated BasCfg resource definition.  This can be used to manually configure a MAS instance to connect to BAS instance, or used as an input to the [suite_config](suite_config.md) role. If this or `mas_instance_id` are not set then the role will not generate a BasCfg template.

- Environment Variable: `MAS_CONFIG_DIR`
- Default Value: None

### uds_contact.email
Required when `mas_instance_id` and `mas_config_dir` are set.  Sets the Contact e-mail address used by the MAS instance's UDS configuration.

- Environment Variable: `UDS_CONTACT_EMAIL`
- Default Value: None

### uds_contact.first_name
Required when `mas_instance_id` and `mas_config_dir` are set.  Sets the Contact first name used by the MAS instance's UDS configuration.

- Environment Variable: `UDS_CONTACT_FIRSTNAME`
- Default Value: None

### uds_contact.last_name
Required when `mas_instance_id` and `mas_config_dir` are set.  Sets the Contact last name used by the MAS instance's UDS configuration.

- Environment Variable: `UDS_CONTACT_LASTNAME`
- Default Value: None

Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    uds_meta_storage_class: ibmc-block-bronze
    mas_instance_id: masinst1
    mas_config_dir: ~/masconfig
    uds_contact:
      email: 'john@email.com'
      firstName: 'john'
      lastName: 'winter'
  roles:
  - ibm.mas_devops.uds_install
```

License
-------

EPL-2.0
