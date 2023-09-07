smtp
===============================================================================

Generate an SMTP configuration that can be directly applied to IBM Maximo Application Suite.
The role supports the Twilio SendGrid email provider.  [Twilio SendGrid](https://docs.sendgrid.com/)

Prior to running this role, you must create an account with SendGrid.  The SendGrid account needs to support creating subusers.

!!! tip
    The role will generate a yaml file containing the definition of a Secret and SmtpCfg resource that can be used to configure the smtp email provider for MAS.
    This file can be directly applied using `oc apply -f $MAS_CONFIG_DIR/smtp-$MAS_INSTANCE_ID.yml"` or used in conjunction with the [suite_config](suite_config.md) role.

This role will create a subuser that must be validated.  An email with a validation link will be sent to the primary email address.  You need to validate the subuser using this link.  If validation fails, you can resend the email using the SendGrid admin UI.

Role Variables
-------------------------------------------------------------------------------
### smtp_type

- Required.  Specify the smtp provider. Currently the supported value is `sendgrid`.
- Environment Variable: `SMTP_TYPE`
- Default: None

### mas_instance_id
The instance ID of Maximo Application Suite that the SmtpCfg configuration will target.

- Required. If this or `mas_config_dir` are not set then the role will not generate a SmtpCfg template
- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### mas_config_dir
Local directory to save the generated SmtpCfg resource definition.  This can be used to manually configure a MAS instance to connect to smtp provider, or used as an input to the [suite_config](suite_config.md) role. If this or `mas_instance_id` are not set then the role will not generate a SmtpCfg template.

- Required. if this or `mas_config_dir` are not set then the role will not generate a SmtpCfg template
- Environment Variable: `MAS_CONFIG_DIR`
- Default Value: None

### mas_pod_templates_dir
Provide the directory where supported pod templates configuration files are defined.  This role will look for a configuration file named `ibm-mas-smtpcfg.yml` in the named directory.  The content of the configuration file should be the yaml block that you wish to be inserted into the SmtpCfg spec under a top level `podTemplates` element, e.g. `podTemplates: {object}`.

For examples refer to the [BestEfforts reference configuration in the MAS CLI](https://github.com/ibm-mas/cli/blob/master/image/cli/mascli/templates/pod-templates/best-effort/ibm-mas-smtpcfg.yml), for full documentation of the supported options refer to the [Customizing Pod Templates](https://www.ibm.com/docs/en/mas-cd/continuous-delivery?topic=configuring-customizing-workloads) in the product documentation.

- Optional
- Environment Variable: `MAS_POD_TEMPLATES_DIR`
- Default: None

### sendgrid_primary_username

- Required.  Username of the existing SendGrid account.  
- Environment Variable: `SMTP_PRIMARY_USERNAME`
- Default: None

### sendgrid_primary_email

- Required.  Email of the existing SendGrid account.
- Environment Variable: `SMTP_PRIMARY_EMAIL`
- Default: None

### sendgrid_subuser_email

- Required.  Email of the SendGrid subuser. This role creates a SendGrid subuser for sending emails [subusers](https://docs.sendgrid.com/ui/account-and-settings/subusers)
- Environment Variable: `SMTP_SUBUSER_EMAIL`
- Default: None

### sendgrid_defaultrecipientemail

- Required.  Default destination email address.
- Environment Variable: `SENDGRID_DEFAULTRECIPIENTEMAIL`
- Default: None

### sendgrid_primary_apikey

- Required.  Apikey of the existing SendGrid account.
- Environment Variable: `SENDGRID_PRIMARY_APIKEY`
- Default: None

### sendgrid_ips

- Required.  ips of the existing SendGrid account.  The primary SendGrid account has one or more IP Addresses associated with it.  Specify the list of SendGrid IP Addresses to associate with the subuser.
- Environment Variable: `SENDGRID_IPS`
- Default: None

### sendgrid_subuser_username

- Optional.  Username of the SendGrid subuser. This role creates a SendGrid subuser for sending emails [subusers](https://docs.sendgrid.com/ui/account-and-settings/subusers)
- Environment Variable: `SMTP_SUBUSER_USERNAME`
- Default:  ibm-mas_$MAS_INSTANCE_ID

### sendgrid_defaultsendername

- Optional.  Easily readable name displayed in emails sent by the subuser
- Environment Variable: `SENDGRID_DEFAULTSENDERNAME`
- Default: ''

### sendgrid_defaultshouldemailpasswords

- Optional.  Flag to indicate if the password should be sent by email.
- Environment Variable: `SENDGRID_DEFAULTSHOULDEMAILPASSWORDS`
- Default: false

### sendgrid_configscope

- Optional
- Environment Variable: `SENDGRID_CONFIGSCOPE`
- Default: system

### sendgrid_hostname

- Optional
- Environment Variable: `SENDGRID_HOSTNAME`
- Default: smtp.sendgrid.net

### sendgrid_port

- Optional
- Environment Variable: `SENDGRID_PORT`
- Default: 465

### sendgrid_security

- Optional
- Environment Variable: `SENDGRID_SECURITY`
- Default: SSL

### sendgrid_authentication

- Optional
- Environment Variable: `SENDGRID_AUTHENTICATION`
- Default: true

### sendgrid_api_url

- Optional. The api URL of the smtp email service.  This URL is used for REST calls.
- Environment Variable: `SENDGRID_API_URL`
- Default: api.sendgrid.com

### custom_labels

- Optional. List of comma separated key=value pairs for setting custom labels on instance specific resources.
- Environment Variable: `CUSTOM_LABELS`
- Default: None

### sendgrid_debug

- Optional.  When set to True, the results of the SendGrid REST calls will be displayed in the log.
- Environment Variable: `SENDGRID_DEBUG`
- Default: False


Example Playbook
-------------------------------------------------------------------------------

### Generate a configuration
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: inst1
    mas_config_dir: /home/me/masconfig
    smtp_type: sendgrid
    sendgrid_primary_username: myusername
    sendgrid_primary_email: myemail@mydomain
    sendgrid_subuser_username: mysubusername
    sendgrid_subuser_email: mysubuser@mydomain
    sendgrid_defaultrecipientemail: myemail@mydomain
    sendgrid_defaultsendername: 'My Name'
    sendgrid_primary_apikey: xxxx
    sendgrid_ips: '["XXX.XXX.XXX.XXX"]'

  roles:
    - ibm.mas_devops.smtp
```


License
-------------------------------------------------------------------------------

EPL-2.0
