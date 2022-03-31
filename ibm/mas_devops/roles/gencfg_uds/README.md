uds_cfg
===========

 This role Generate a configuration file that can be directly applied to IBM Maximo Application Suite.


Role Variables
--------------


### mas_instance_id
The instance ID of Maximo Application Suite that the BasCfg configuration will target.  If this or `mas_config_dir` are not set then the role will not generate a BasCfg template.

- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### mas_config_dir
Local directory to save the generated BasCfg resource definition.  This can be used to manually configure a MAS instance to connect to BAS instance, or used as an input to the [suite_config](suite_config.md) role. If this or `mas_instance_id` are not set then the role will not generate a BasCfg template.

- Environment Variable: `MAS_CONFIG_DIR`
- Default Value: None

### mas_segment_key
Override the biult-in segment key used by MAS when communicating with User Data Services.  This variable is only used for the generation of the BASCfg template, and in 99% of use cases you will not need to set this.

- Environment Variable: `MAS_SEGMENT_KEY`
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

### uds_tls_cr
Required when `mas_instance_id` and `mas_config_dir` are set.  Sets the UDS TLS CR used by the MAS instance's UDS configuration.

- Environment Variable: None
- Default Value: None

### uds_endpoint_url
Required when `mas_instance_id` and `mas_config_dir` are set.  Sets the UDS endpoint url used by the MAS instance's UDS configuration.
- Environment Variable: None
- Default Value: None

### uds_api_key
Required when `mas_instance_id` and `mas_config_dir` are set.  Sets the UDS api key used by the MAS instance's UDS configuration.
- Environment Variable: None
- Default Value: None

Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    uds_api_key: "xxx"
    uds_endpoint_url: "https://xxx"
    uds_tls_crt: {{ uds_certificate_lookup.resources[0].data['tls.crt'] | b64decode | regex_findall('(-----BEGIN .+?-----(?s).+?-----END .+?-----)', multiline=True, ignorecase=True) }}
    mas_instance_id: masinst1
    mas_config_dir: ~/masconfig
    uds_contact:
      email: 'john@email.com'
      firstName: 'john'
      lastName: 'winter'
  roles:
  - ibm.mas_devops.gencfg_uds
```

License
-------

EPL-2.0
