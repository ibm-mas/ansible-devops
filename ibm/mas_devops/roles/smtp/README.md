# smtp

Generate an SMTP configuration that can be directly applied to IBM Maximo Application Suite.
The role supports the [Twilio SendGrid](https://docs.sendgrid.com/) email provider.

Prior to running this role, you must create an account with SendGrid.  The SendGrid account needs to support creating subusers.

!!! tip
    The role will generate a yaml file containing the definition of a Secret and SmtpCfg resource that can be used to configure the smtp email provider for MAS.
    This file can be directly applied using `oc apply -f $MAS_CONFIG_DIR/smtp-$MAS_INSTANCE_ID.yml"` or used in conjunction with the [suite_config](suite_config.md) role.

This role will create a subuser that must be validated.  An email with a validation link will be sent to the primary email address.  You need to validate the subuser using this link.  If validation fails, you can resend the email using the SendGrid admin UI.

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`smtp_type`](#smtp_type) | Yes | None |
| [`mas_instance_id`](#mas_instance_id) | Yes | None |
| [`mas_config_dir`](#mas_config_dir) | Yes | None |
| [`mas_pod_templates_dir`](#mas_pod_templates_dir) | No | None |
| [`custom_labels`](#custom_labels) | No | None |
| [`sendgrid_primary_username`](#sendgrid_primary_username) | Yes | None |
| [`sendgrid_primary_email`](#sendgrid_primary_email) | Yes | None |
| [`sendgrid_primary_apikey`](#sendgrid_primary_apikey) | Yes | None |
| [`sendgrid_ips`](#sendgrid_ips) | Yes | None |
| [`sendgrid_subuser_username`](#sendgrid_subuser_username) | No | `ibm-mas_{mas_instance_id}` |
| [`sendgrid_subuser_email`](#sendgrid_subuser_email) | Yes | None |
| [`sendgrid_defaultrecipientemail`](#sendgrid_defaultrecipientemail) | Yes | None |
| [`sendgrid_defaultsendername`](#sendgrid_defaultsendername) | No | Empty string |
| [`sendgrid_defaultshouldemailpasswords`](#sendgrid_defaultshouldemailpasswords) | No | `false` |
| [`sendgrid_configscope`](#sendgrid_configscope) | No | `system` |
| [`sendgrid_hostname`](#sendgrid_hostname) | No | `smtp.sendgrid.net` |
| [`sendgrid_port`](#sendgrid_port) | No | `465` |
| [`sendgrid_security`](#sendgrid_security) | No | `SSL` |
| [`sendgrid_authentication`](#sendgrid_authentication) | No | `true` |
| [`sendgrid_api_url`](#sendgrid_api_url) | No | `api.sendgrid.com` |
| [`sendgrid_debug`](#sendgrid_debug) | No | `False` |

### SMTP Provider

#### smtp_type

SMTP email provider type for MAS email notifications — `sendgrid` is currently the only supported provider.

- **Required**
- Environment Variable: `SMTP_TYPE`
- Default: None

Determines which SMTP provider configuration is created and which API endpoints are used. Requires an active SendGrid account with subuser support; future versions may support additional SMTP providers.

### MAS Configuration

#### mas_instance_id

MAS instance identifier the SMTP configuration applies to — a valid MAS instance ID (e.g. `prod`, `dev`, `masinst1`).

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

Must match the instance ID used during MAS installation. Used to name the generated SmtpCfg resource and in the default subuser username `ibm-mas_{mas_instance_id}`.

#### mas_config_dir

Local directory where the generated SMTP configuration files are saved — any valid local filesystem path (e.g. `~/masconfig`, `/opt/mas/config`).

- **Required**
- Environment Variable: `MAS_CONFIG_DIR`
- Default: None

The SmtpCfg YAML file (containing the Secret and SmtpCfg resources) is created as `smtp-{mas_instance_id}.yml` in this directory. Apply it manually with `oc apply -f $MAS_CONFIG_DIR/smtp-$MAS_INSTANCE_ID.yml` or use it with the [suite_config](suite_config.md) role for automated configuration. Use a consistent directory across all MAS DevOps roles.

#### mas_pod_templates_dir

Directory containing pod template customizations for the SMTP service pods — must contain a file named `ibm-mas-smtpcfg.yml`.

- **Optional**
- Environment Variable: `MAS_POD_TEMPLATES_DIR`
- Default: None

The pod template configuration is inserted into the SmtpCfg spec under the `podTemplates` element. See the [BestEfforts reference](https://github.com/ibm-mas/cli/blob/master/image/cli/mascli/templates/pod-templates/best-effort/ibm-mas-smtpcfg.yml) and the [Customizing Pod Templates](https://www.ibm.com/docs/en/mas-cd/continuous-delivery?topic=configuring-customizing-workloads) documentation.

#### custom_labels

Custom key-value labels applied to the generated SMTP resources — comma-separated `key=value` pairs (e.g. `environment=production,team=platform,cost-center=engineering`).

- **Optional**
- Environment Variable: `CUSTOM_LABELS`
- Default: None

Useful for resource organization, cost tracking, environment identification, and automation-driven resource discovery. Follow Kubernetes label naming conventions.

### SendGrid Primary Account

#### sendgrid_primary_username

Username of the primary SendGrid account used to create the subuser for MAS email operations.

- **Required**
- Environment Variable: `SENDGRID_PRIMARY_USERNAME`
- Default: None

The account must have permissions to create subusers. Primary account credentials are only used during setup and are not stored in MAS.

#### sendgrid_primary_email

Email address registered with the primary SendGrid account.

- **Required**
- Environment Variable: `SENDGRID_PRIMARY_EMAIL`
- Default: None

Subuser validation emails are sent to this address — you must validate the subuser using the link in the email before it can send emails. The validation email can be resent from the SendGrid admin UI if needed.

#### sendgrid_primary_apikey

API key for the primary SendGrid account, with subuser creation and IP management permissions.

- **Required**
- Environment Variable: `SENDGRID_PRIMARY_APIKEY`
- Default: None

Generate the key from the SendGrid console (Settings > API Keys). Store it securely and never commit it to version control; it is only used during setup for subuser creation and IP assignment, not stored in MAS configuration.

#### sendgrid_ips

SendGrid IP addresses to assign to the subuser — a JSON array string such as `'["192.0.2.1", "192.0.2.2"]'`.

- **Required**
- Environment Variable: `SENDGRID_IPS`
- Default: None

The IPs must already be allocated to the primary account (find them in the SendGrid console: Settings > IP Addresses). The subuser sends emails from these addresses, so their reputation affects email deliverability.

### SendGrid Subuser

#### sendgrid_subuser_username

Username for the SendGrid subuser created for MAS — alphanumeric, with hyphens and underscores allowed.

- **Optional**
- Environment Variable: `SENDGRID_SUBUSER_USERNAME`
- Default: `ibm-mas_{mas_instance_id}`

Must be unique within the SendGrid account. Override the default if you need a specific naming convention or share one SendGrid account across multiple MAS instances. See the [SendGrid subusers documentation](https://docs.sendgrid.com/ui/account-and-settings/subusers).

#### sendgrid_subuser_email

Email address for the SendGrid subuser dedicated to sending MAS notifications — can be the same as or different from the primary account email.

- **Required**
- Environment Variable: `SENDGRID_SUBUSER_EMAIL`
- Default: None

The subuser provides isolation from the primary account. See the [SendGrid subusers documentation](https://docs.sendgrid.com/ui/account-and-settings/subusers).

### Email Defaults

#### sendgrid_defaultrecipientemail

Default recipient email address for MAS notifications when no specific recipient is configured — typically an admin or operations team email.

- **Required**
- Environment Variable: `SENDGRID_DEFAULTRECIPIENTEMAIL`
- Default: None

Acts as the fallback for unconfigured notifications and can be overridden per notification type in MAS.

#### sendgrid_defaultsendername

Display name shown as the sender in email clients when MAS sends notifications — any string, e.g. `MAS Notifications` or `Maximo Production`.

- **Optional**
- Environment Variable: `SENDGRID_DEFAULTSENDERNAME`
- Default: Empty string

Improves email recognition and trust; recommended for production deployments and can be left empty for default behavior.

#### sendgrid_defaultshouldemailpasswords

Controls whether MAS sends user passwords via email when creating or resetting accounts — `true` or `false`.

- **Optional**
- Environment Variable: `SENDGRID_DEFAULTSHOULDEMAILPASSWORDS`
- Default: `false`

!!! warning
    Sending passwords via email is generally not recommended — the default `false` follows security best practices. Only set to `true` if your security policy allows password transmission via email, and consider alternative password delivery methods.

#### sendgrid_configscope

Configuration scope for the SMTP settings — `system` is currently the only supported value.

- **Optional**
- Environment Variable: `SENDGRID_CONFIGSCOPE`
- Default: `system`

System scope makes the SMTP configuration available to all MAS components; workspace or application scopes may be supported in future versions.

### SMTP Connection

#### sendgrid_hostname

SendGrid SMTP server hostname that MAS connects to for sending emails.

- **Optional**
- Environment Variable: `SENDGRID_HOSTNAME`
- Default: `smtp.sendgrid.net`

This is SendGrid's standard SMTP endpoint and rarely needs to be changed — verify with the SendGrid documentation if unsure.

#### sendgrid_port

SendGrid SMTP server port: `465` (SMTP with SSL/TLS, recommended default), `587` (SMTP with STARTTLS), or `25` (unencrypted, not recommended — often blocked by ISPs).

- **Optional**
- Environment Variable: `SENDGRID_PORT`
- Default: `465`

Must match `sendgrid_security` — port 465 pairs with `SSL` and port 587 with `STARTTLS`.

#### sendgrid_security

SMTP connection security protocol: `SSL` (recommended, default), `STARTTLS` (upgrade to TLS after initial connection), or `NONE` (no encryption, not recommended).

- **Optional**
- Environment Variable: `SENDGRID_SECURITY`
- Default: `SSL`

`SSL` on port 465 is recommended and `STARTTLS` on port 587 is also secure — never use `NONE` in production.

#### sendgrid_authentication

Enables SMTP authentication for SendGrid connections — `true` or `false`.

- **Optional**
- Environment Variable: `SENDGRID_AUTHENTICATION`
- Default: `true`

Must remain `true`: authentication is required by SendGrid and uses the subuser credentials — disabling it will cause the connection to fail.

#### sendgrid_api_url

SendGrid REST API endpoint used by the role for subuser creation and management — a valid SendGrid API hostname.

- **Optional**
- Environment Variable: `SENDGRID_API_URL`
- Default: `api.sendgrid.com`

This is SendGrid's standard API endpoint and rarely needs to be changed. It is used during role execution only, not by MAS itself.

### Debugging

#### sendgrid_debug

Enables display of detailed SendGrid REST API call results in Ansible logs — `True` or `False`.

- **Optional**
- Environment Variable: `SENDGRID_DEBUG`
- Default: `False`

!!! warning
    Use only for troubleshooting and disable it afterwards — when `True`, detailed API responses are logged, which may include sensitive information.

## Example Playbook

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

## License

EPL-2.0
