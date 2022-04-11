gencfg_sls
===========

This role is used to generate a SLSCfg Custom Resource that can be applied to Maximo Application Suite manually, or using the `suite_config` role.  The configuration will be saved to local disk in the directory specified by the `mas_config_dir` variable.

If `mas_instance_id` and `mas_config_dir` are not both set, then the role will simply print a debug message containing the configuration information.


Role Variables
--------------

### mas_instance_id
The instance ID of Maximo Application Suite that the SlsCfg configuration will target.  If this or `mas_config_dir` are not set then the role will not generate a SlsCfg template.

- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### mas_config_dir
Local directory to save the generated SlsCfg resource definition.  This can be used to manually configure a MAS instance to connect to SLS instance, or used as an input to the [suite_config](suite_config.md) role. If this or `mas_instance_id` are not set then the role will not generate a SlsCfg template.

- Environment Variable: `MAS_CONFIG_DIR`
- Default Value: None

### slscfg_tls_crt
Required. The TLS CA certiticate of the LicenseService to be used when the Maximo Application Suite is registered with SLS.

- Environment Variable: None
- Default Value: None

### slscfg_url
Required. The URL of the LicenseService to be called when the Maximo Application Suite is registered with SLS.

- Environment Variable: `SLSCFG_URL`
- Default Value: None

### slscfg_registration_key
Required. The Registration key of the LicenseService instance to be used when the Maximo Application Suite is registered with SLS.

- Environment Variable: `SLSCFG_REGISTRATION_KEY`
- Default Value: None


Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: inst1
    mas_config_dir: /home/me

    slscfg_tls_crt: "{{ lookup('file', '/home/me/sls.crt') }}"
    slscfg_url: "https://xxx"
    slscfg_registration_key: "xxx"

  roles:
    - ibm.mas_devops.sls_gencfg
```


License
-------

EPL-2.0
