smtp
===============================================================================

Generate an SMTP configuration that can be directly applied to IBM Maximo Application Suite.

The role can be extended to support multiple SMTP types.  Currently it supports SendGrid. 
The SendGrid SMTP type assumes the SendGrid account has already been setup.


Role Variables
-------------------------------------------------------------------------------
### smtp_type

- Required
- Environment Variable: `SMTP_TYPE`
- Default: None

### mas_instance_id

- Required
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

### mas_config_dir

- Required
- Environment Variable: `MAS_CONFIG_DIR`
- Default: None

### sendgrid_primary_username

- Required
- Environment Variable: `SMTP_PRIMARY_USERNAME`
- Default: None

### sendgrid_primary_email

- Required
- Environment Variable: `SMTP_PRIMARY_EMAIL`
- Default: None

### sendgrid_subuser_username

- Required
- Environment Variable: `SMTP_SUBUSER_USERNAME`
- Default: None

### sendgrid_subuser_email

- Required
- Environment Variable: `SMTP_SUBUSER_EMAIL`
- Default: None

### sendgrid_debug

- Optional
- Environment Variable: `SENDGRID_DEBUG`
- Default: None

### sendgrid_configscope

- Required
- Environment Variable: `SENDGRID_CONFIGSCOPE`
- Default: None

### sendgrid_hostname

- Required
- Environment Variable: `SENDGRID_HOSTNAME`
- Default: None

### sendgrid_port

- Required
- Environment Variable: `SENDGRID_PORT`
- Default: None

### sendgrid_security

- Required
- Environment Variable: `SENDGRID_SECURITY`
- Default: None

### sendgrid_authentication

- Required
- Environment Variable: `SENDGRID_AUTHENTICATION`
- Default: None

### sendgrid_defaultsendername

- Required
- Environment Variable: `SENDGRID_DEFAULTSENDERNAME`
- Default: None

### sendgrid_defaultrecipientemail

- Required
- Environment Variable: `SENDGRID_DEFAULTRECIPIENTEMAIL`
- Default: None

### sendgrid_defaultshouldemailpasswords

- Optional
- Environment Variable: `SENDGRID_DEFAULTSHOULDEMAILPASSWORDS`
- Default: None

### sendgrid_api_url

- Required
- Environment Variable: `SENDGRID_API_URL`
- Default: None

### sendgrid_primary_apikey

- Required
- Environment Variable: `SENDGRID_PRIMARY_APIKEY`
- Default: None

### sendgrid_ips

- Required
- Environment Variable: `SENDGRID_IPS`
- Default: None





### sls_action
Inform the role whether to perform an install or uninstall of the Suite License Service.

- Optional
- Environment Variable: `SLS_ACTION`
- Default: `install`


### custom_labels
List of comma separated key=value pairs for setting custom labels on instance specific resources.

- Optional
- Environment Variable: `CUSTOM_LABELS`
- Default Value: None


Example Playbook
-------------------------------------------------------------------------------

### Install and generate a configuration
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
