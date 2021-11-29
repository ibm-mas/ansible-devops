# BAS Playbooks
Installs **IBM Behavior Analytics Services** on IBM Cloud Openshift Clusters (ROKS) and generates configuration that can be directly applied to IBM Maximo Application Suite.

## Install BAS
Before you use this playbook you will likely want to edit the `mas_config_dir` variable to supply your own configuration, instead of the sample data provided. 
This is the directory where this playbook will store BAS configurations such as BAS endpoint and username/password credentials to configure BAS in your Maximo Application Suite instance.

### Required environment variables
- `BAS_CONTACT_MAIL` Defines the email for person to contact for BAS
- `BAS_CONTACT_FIRSTNAME` Defines the first name of the person to contact for BAS
- `BAS_CONTACT_LASTNAME` Defines the last name of the person to contact for BAS

### Optional environment variables
- `BAS_USERNAME` BAS default username. If not provided, default username will be `basuser`.
- `BAS_PASSWORD` Defines the password for your BAS instance. If not provided, a random 15 character password will be generated.
- `BAS_GRAFANA_USERNAME` Defines the username for the BAS Graphana instance, default is `basuser`. 
- `BAS_GRAFANA_PASSWORD` Defines the password for BAS Graphana dashboard. If not provided, a random 15 character password will be generated
- `BAS_NAMESPACE` Defines the targetted cluster namespace/project where BAS will be installed. If not provided, default BAS namespace will be 'ibm-bas'.

### Usage: 

```bash
export BAS_NAMESPACE=ibm-bas
export BAS_USER=basuser
export BAS_PASSWORD=xxx
export BAS_GRAFANA_USER=basuser
export BAS_GRAFANA_PASSWORD=xxx
export BAS_CONTACT_MAIL=xxx@xxx.com
export BAS_CONTACT_FIRSTNAME=xxx
export BAS_CONTACT_LASTNAME=xxx

ansible-playbook playbooks/bas/install-bas.yml
```
