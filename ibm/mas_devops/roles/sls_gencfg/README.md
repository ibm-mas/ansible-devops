sls_cfg
===========

Install **IBM Suite License Service** and generate configuration that can be directly applied to IBM Maximo Application Suite.

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
Required. TODO: Write me

- Environment Variable: None
- Default Value: None

### slscfg_url
Required. TODO: Write me

- Environment Variable: `SLSCFG_URL`
- Default Value: None

### slscfg_registration_key
Required. TODO: Write me

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
