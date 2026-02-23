# smtp

Generate an SMTP configuration that can be directly applied to IBM Maximo Application Suite.
The role supports the Twilio SendGrid email provider.  [Twilio SendGrid](https://docs.sendgrid.com/)

Prior to running this role, you must create an account with SendGrid.  The SendGrid account needs to support creating subusers.

!!! tip
    The role will generate a yaml file containing the definition of a Secret and SmtpCfg resource that can be used to configure the smtp email provider for MAS.
    This file can be directly applied using `oc apply -f $MAS_CONFIG_DIR/smtp-$MAS_INSTANCE_ID.yml"` or used in conjunction with the [suite_config](suite_config.md) role.

This role will create a subuser that must be validated.  An email with a validation link will be sent to the primary email address.  You need to validate the subuser using this link.  If validation fails, you can resend the email using the SendGrid admin UI.

## Role Variables

### smtp_type
SMTP email provider type for MAS email notifications.

- **Required**
- Environment Variable: `SMTP_TYPE`
- Default: None

**Purpose**: Specifies which SMTP email service provider to use for sending MAS notifications and alerts.

**When to use**: Always required when configuring SMTP for MAS. Currently only SendGrid is supported.

**Valid values**: `sendgrid` (only supported provider)

**Impact**: Determines which SMTP provider configuration will be created and which API endpoints will be used.

**Related variables**: [`sendgrid_primary_apikey`](#sendgrid_primary_apikey), [`sendgrid_hostname`](#sendgrid_hostname)

**Notes**:
- SendGrid is currently the only supported SMTP provider
- Requires an active SendGrid account with subuser support
- Future versions may support additional SMTP providers

### mas_instance_id
MAS instance identifier for SMTP configuration.

- **Required** (if generating SmtpCfg)
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

**Purpose**: Identifies which MAS instance the SMTP configuration will be applied to.

**When to use**: Required when generating SmtpCfg resource. If not set along with `mas_config_dir`, the role will not generate configuration files.

**Valid values**: Valid MAS instance ID (3-12 lowercase alphanumeric characters, e.g., `prod`, `dev`, `masinst1`)

**Impact**: Used to name the generated SmtpCfg resource and target the correct MAS instance.

**Related variables**: [`mas_config_dir`](#mas_config_dir), [`sendgrid_subuser_username`](#sendgrid_subuser_username)

**Notes**:
- Must match the instance ID used during MAS installation
- Used in default subuser username: `ibm-mas_{mas_instance_id}`
- Both this and `mas_config_dir` must be set to generate configuration

### mas_config_dir
Local directory for generated SMTP configuration files.

- **Required** (if generating SmtpCfg)
- Environment Variable: `MAS_CONFIG_DIR`
- Default: None

**Purpose**: Specifies where to save the generated SmtpCfg resource YAML file containing SMTP configuration and credentials.

**When to use**: Required when generating SmtpCfg resource. If not set along with `mas_instance_id`, the role will not generate configuration files.

**Valid values**: Valid local filesystem path (e.g., `~/masconfig`, `/opt/mas/config`)

**Impact**: SmtpCfg YAML file will be created in this directory as `smtp-{mas_instance_id}.yml`.

**Related variables**: [`mas_instance_id`](#mas_instance_id)

**Notes**:
- Can be applied manually: `oc apply -f $MAS_CONFIG_DIR/smtp-$MAS_INSTANCE_ID.yml`
- Can be used with [`suite_config`](suite_config.md) role for automated configuration
- Both this and `mas_instance_id` must be set to generate configuration
- Use consistent directory across all MAS DevOps roles

### mas_pod_templates_dir
Directory containing pod template customizations for SMTP.

- Optional
- Environment Variable: `MAS_POD_TEMPLATES_DIR`
- Default: None

**Purpose**: Provides custom pod template configurations for the SMTP service pods, allowing resource limits, node selectors, and other Kubernetes pod specifications.

**When to use**: Set when you need to customize SMTP pod resources, scheduling, or other pod-level configurations.

**Valid values**: Valid directory path containing `ibm-mas-smtpcfg.yml` file

**Impact**: Pod template configuration is inserted into SmtpCfg spec under `podTemplates` element.

**Related variables**: None

**Notes**:
- File must be named `ibm-mas-smtpcfg.yml`
- See [BestEfforts reference](https://github.com/ibm-mas/cli/blob/master/image/cli/mascli/templates/pod-templates/best-effort/ibm-mas-smtpcfg.yml)
- Full documentation: [Customizing Pod Templates](https://www.ibm.com/docs/en/mas-cd/continuous-delivery?topic=configuring-customizing-workloads)
- Optional - only needed for custom resource requirements

### sendgrid_primary_username
Primary SendGrid account username.

- **Required**
- Environment Variable: `SMTP_PRIMARY_USERNAME`
- Default: None

**Purpose**: Identifies the primary SendGrid account that will be used to create a subuser for MAS email operations.

**When to use**: Always required. Must be the username of an existing SendGrid account with subuser creation permissions.

**Valid values**: Valid SendGrid account username

**Impact**: Used to authenticate to SendGrid API for subuser creation and management.

**Related variables**: [`sendgrid_primary_apikey`](#sendgrid_primary_apikey), [`sendgrid_primary_email`](#sendgrid_primary_email)

**Notes**:
- Must have permissions to create subusers in SendGrid
- Primary account credentials are only used during setup, not stored in MAS
- Subuser will be created under this primary account

### sendgrid_primary_email
Primary SendGrid account email address.

- **Required**
- Environment Variable: `SMTP_PRIMARY_EMAIL`
- Default: None

**Purpose**: Provides the email address associated with the primary SendGrid account. Validation emails will be sent to this address.

**When to use**: Always required. Must match the email registered with the SendGrid primary account.

**Valid values**: Valid email address registered with SendGrid account

**Impact**: Subuser validation emails will be sent to this address. You must validate the subuser using the link in the email.

**Related variables**: [`sendgrid_primary_username`](#sendgrid_primary_username), [`sendgrid_subuser_email`](#sendgrid_subuser_email)

**Notes**:
- Validation email will be sent after subuser creation
- Must validate subuser before it can send emails
- Can resend validation email from SendGrid admin UI if needed

### sendgrid_subuser_email
Email address for the SendGrid subuser.

- **Required**
- Environment Variable: `SMTP_SUBUSER_EMAIL`
- Default: None

**Purpose**: Specifies the email address for the SendGrid subuser that will be created for MAS email operations.

**When to use**: Always required. This subuser will be dedicated to sending MAS notifications.

**Valid values**: Valid email address (can be same as primary or different)

**Impact**: This email will be associated with the subuser account and used for subuser-specific operations.

**Related variables**: [`sendgrid_subuser_username`](#sendgrid_subuser_username), [`sendgrid_primary_email`](#sendgrid_primary_email)

**Notes**:
- Subuser provides isolation from primary account
- See [SendGrid subusers documentation](https://docs.sendgrid.com/ui/account-and-settings/subusers)
- Can use same email as primary account if desired

### sendgrid_defaultrecipientemail
Default recipient email address for MAS notifications.

- **Required**
- Environment Variable: `SENDGRID_DEFAULTRECIPIENTEMAIL`
- Default: None

**Purpose**: Specifies the default destination email address for MAS notifications when no specific recipient is configured.

**When to use**: Always required. This is the fallback email address for system notifications.

**Valid values**: Valid email address

**Impact**: MAS will send notifications to this address when no other recipient is specified in the notification configuration.

**Related variables**: None

**Notes**:
- Acts as fallback for unconfigured notifications
- Can be overridden per notification type in MAS
- Typically set to admin or operations team email

### sendgrid_primary_apikey
API key for the primary SendGrid account.

- **Required**
- Environment Variable: `SENDGRID_PRIMARY_APIKEY`
- Default: None

**Purpose**: Provides authentication credentials for SendGrid API to create and configure the subuser.

**When to use**: Always required. Must be an API key from the primary SendGrid account with subuser management permissions.

**Valid values**: Valid SendGrid API key with appropriate permissions

**Impact**: Used to authenticate SendGrid API calls for subuser creation and IP assignment.

**Related variables**: [`sendgrid_primary_username`](#sendgrid_primary_username)

**Notes**:
- Store securely, never commit to version control
- Requires permissions: subuser creation, IP management
- Only used during setup, not stored in MAS configuration
- Generate from SendGrid console: Settings > API Keys

### sendgrid_ips
SendGrid IP addresses to assign to the subuser.

- **Required**
- Environment Variable: `SENDGRID_IPS`
- Default: None

**Purpose**: Specifies which SendGrid IP addresses should be assigned to the subuser for sending emails.

**When to use**: Always required. Must be IP addresses already allocated to your primary SendGrid account.

**Valid values**: JSON array of IP addresses (e.g., `'["192.0.2.1", "192.0.2.2"]'`)

**Impact**: Subuser will send emails from these IP addresses. Affects email deliverability and reputation.

**Related variables**: [`sendgrid_primary_apikey`](#sendgrid_primary_apikey)

**Notes**:
- IPs must already be allocated to primary account
- Find IPs in SendGrid console: Settings > IP Addresses
- Format as JSON array string
- IP reputation affects email deliverability

### sendgrid_subuser_username
Username for the SendGrid subuser.

- Optional
- Environment Variable: `SMTP_SUBUSER_USERNAME`
- Default: `ibm-mas_{mas_instance_id}`

**Purpose**: Specifies the username for the SendGrid subuser that will be created for MAS.

**When to use**: Override default if you need a specific naming convention or have multiple MAS instances sharing a SendGrid account.

**Valid values**: Valid SendGrid username (alphanumeric, hyphens, underscores)

**Impact**: Subuser will be created with this username in SendGrid.

**Related variables**: [`mas_instance_id`](#mas_instance_id), [`sendgrid_subuser_email`](#sendgrid_subuser_email)

**Notes**:
- Default includes MAS instance ID for uniqueness
- Must be unique within the SendGrid account
- See [SendGrid subusers documentation](https://docs.sendgrid.com/ui/account-and-settings/subusers)

### sendgrid_defaultsendername
Display name for emails sent by MAS.

- Optional
- Environment Variable: `SENDGRID_DEFAULTSENDERNAME`
- Default: Empty string

**Purpose**: Provides a human-readable sender name that appears in email clients when MAS sends notifications.

**When to use**: Set to provide a friendly sender name like "MAS Production Alerts" or "Maximo Notifications".

**Valid values**: Any string (e.g., `MAS Notifications`, `Maximo Production`)

**Impact**: This name appears as the sender in email clients, making emails more recognizable to recipients.

**Related variables**: None

**Notes**:
- Improves email recognition and trust
- Recommended for production deployments
- Can be left empty for default behavior

### sendgrid_defaultshouldemailpasswords
Enable password delivery via email.

- Optional
- Environment Variable: `SENDGRID_DEFAULTSHOULDEMAILPASSWORDS`
- Default: `false`

**Purpose**: Controls whether MAS should send user passwords via email when creating or resetting accounts.

**When to use**: Set to `true` only if your security policy allows password transmission via email.

**Valid values**:
- `true` - Send passwords via email
- `false` - Do not send passwords via email (recommended)

**Impact**: When `true`, new user passwords and password resets will be emailed. When `false`, passwords must be communicated through other means.

**Related variables**: None

**Notes**:
- **Security**: Sending passwords via email is generally not recommended
- Default `false` follows security best practices
- Consider alternative password delivery methods

### sendgrid_configscope
Configuration scope for SMTP settings.

- Optional
- Environment Variable: `SENDGRID_CONFIGSCOPE`
- Default: `system`

**Purpose**: Defines the scope level for SMTP configuration in MAS.

**When to use**: Use default `system` for system-wide SMTP configuration. Other scopes may be supported in future versions.

**Valid values**: `system` (currently only supported value)

**Impact**: Determines which MAS components can use this SMTP configuration.

**Related variables**: None

**Notes**:
- System scope makes SMTP available to all MAS components
- Future versions may support workspace or application scopes

### sendgrid_hostname
SendGrid SMTP server hostname.

- Optional
- Environment Variable: `SENDGRID_HOSTNAME`
- Default: `smtp.sendgrid.net`

**Purpose**: Specifies the SendGrid SMTP server hostname for email transmission.

**When to use**: Use default unless SendGrid changes their SMTP endpoint or you're using a custom configuration.

**Valid values**: Valid SendGrid SMTP hostname

**Impact**: MAS will connect to this hostname for sending emails via SMTP protocol.

**Related variables**: [`sendgrid_port`](#sendgrid_port), [`sendgrid_security`](#sendgrid_security)

**Notes**:
- Default is SendGrid's standard SMTP endpoint
- Rarely needs to be changed
- Verify with SendGrid documentation if unsure

### sendgrid_port
SendGrid SMTP server port.

- Optional
- Environment Variable: `SENDGRID_PORT`
- Default: `465`

**Purpose**: Specifies the port number for SMTP connections to SendGrid.

**When to use**: Use default `465` for SSL/TLS connections. Change only if using different security configuration.

**Valid values**:
- `465` - SMTP with SSL/TLS (recommended, default)
- `587` - SMTP with STARTTLS
- `25` - Unencrypted SMTP (not recommended)

**Impact**: Determines which port MAS uses to connect to SendGrid SMTP server.

**Related variables**: [`sendgrid_hostname`](#sendgrid_hostname), [`sendgrid_security`](#sendgrid_security)

**Notes**:
- Port 465 is recommended for secure connections
- Must match the security setting
- Port 25 is often blocked by ISPs

### sendgrid_security
SMTP connection security protocol.

- Optional
- Environment Variable: `SENDGRID_SECURITY`
- Default: `SSL`

**Purpose**: Specifies the security protocol for SMTP connections to SendGrid.

**When to use**: Use default `SSL` for secure connections on port 465. Change to `STARTTLS` if using port 587.

**Valid values**:
- `SSL` - SSL/TLS encryption (recommended, default)
- `STARTTLS` - Upgrade to TLS after initial connection
- `NONE` - No encryption (not recommended)

**Impact**: Determines how SMTP connections are encrypted.

**Related variables**: [`sendgrid_port`](#sendgrid_port), [`sendgrid_hostname`](#sendgrid_hostname)

**Notes**:
- SSL on port 465 is recommended
- STARTTLS on port 587 is also secure
- Never use NONE in production

### sendgrid_authentication
Enable SMTP authentication.

- Optional
- Environment Variable: `SENDGRID_AUTHENTICATION`
- Default: `true`

**Purpose**: Controls whether SMTP authentication is required for SendGrid connections.

**When to use**: Always use default `true`. Authentication is required by SendGrid.

**Valid values**:
- `true` - Enable authentication (required)
- `false` - Disable authentication (will fail)

**Impact**: When `true`, MAS will authenticate using subuser credentials. When `false`, connection will fail.

**Related variables**: [`sendgrid_subuser_username`](#sendgrid_subuser_username)

**Notes**:
- Must be `true` for SendGrid
- Authentication uses subuser credentials
- Do not change from default

### sendgrid_api_url
SendGrid API endpoint URL.

- Optional
- Environment Variable: `SENDGRID_API_URL`
- Default: `api.sendgrid.com`

**Purpose**: Specifies the SendGrid API endpoint for REST API calls during subuser creation and management.

**When to use**: Use default unless SendGrid changes their API endpoint or you're using a custom configuration.

**Valid values**: Valid SendGrid API hostname

**Impact**: Role will make REST API calls to this endpoint for subuser management.

**Related variables**: [`sendgrid_primary_apikey`](#sendgrid_primary_apikey)

**Notes**:
- Default is SendGrid's standard API endpoint
- Used during role execution, not by MAS
- Rarely needs to be changed

### custom_labels
Custom labels for MAS SMTP resources.

- Optional
- Environment Variable: `CUSTOM_LABELS`
- Default: None

**Purpose**: Allows adding custom key-value labels to SMTP-related Kubernetes resources for organization and automation.

**When to use**: Set when you need to tag resources for cost tracking, environment identification, or automation purposes.

**Valid values**: Comma-separated key=value pairs (e.g., `environment=production,team=platform,cost-center=engineering`)

**Impact**: Labels are applied to generated SmtpCfg and related resources.

**Related variables**: None

**Notes**:
- Useful for resource organization and tracking
- Can be used by automation tools for resource discovery
- Follow Kubernetes label naming conventions

### sendgrid_debug
Enable debug logging for SendGrid API calls.

- Optional
- Environment Variable: `SENDGRID_DEBUG`
- Default: `False`

**Purpose**: Controls whether detailed SendGrid REST API call results are displayed in Ansible logs.

**When to use**: Set to `True` when troubleshooting SendGrid integration issues or subuser creation problems.

**Valid values**:
- `True` - Display API call results in logs
- `False` - Normal logging (default)

**Impact**: When `True`, detailed API responses are logged, which may include sensitive information.

**Related variables**: None

**Notes**:
- Use only for troubleshooting
- May expose sensitive data in logs
- Disable after troubleshooting is complete


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
