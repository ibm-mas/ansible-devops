# DNS Setup Role

This role will manage MAS and DNS provider integration.  IBM Cloud Internet Services is the only supported DNS provider currently.

## Cloud Internet Services (CIS)

### DNS Management
This role will create DNS entries automatically in the CIS service instance.  Two different modes are available:

#### Top Level DNS entries
This mode will create the entries directly using your DNS zone value. It is usually recommended when you have 1x1 relationship between MAS Instance -> CIS service. e.g: mas.whirlpool.com, where the domain matches exactly the CIS zone name.

#### Subdomain DNS entries
This mode will create entries using a subdomain. It allows you to have multiple MAS instances using same CIS service. e.g: dev.mas.whirlpool.com, where 'dev' is the subdomain.

### Webhook

The Webhook Task will deploy a cert-manager webhook for CIS integration.
The webhook is responsible for managent the certificate challenge requests from letsencrypt and CIS.
This task will also create two ClusterIssuers by default, pointing to either Staging or Production letsencrypt servers.

!!! warning "Important"
    Your IBM Cloud apikey will be stored in a secret. The webhook will use it to create challenge request files in your DNS. Tailor the IBM Cloud apikey permissions to limit its access to your IBM Cloud Account.

