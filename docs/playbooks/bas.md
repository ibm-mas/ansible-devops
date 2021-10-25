# BAS Playbooks

## Install BAS
Before you use this playbook you will likely want to edit the `mas_config_dir` variable to supply your own configuration, instead of the sample data provided.

### Required environment variables
- `BAS_PERSISTENT_STORAGE` Storage Class To be used by BAS persistent storage
- `BAS_META_STORAGE` Storage Class To be used by BAS metadata storage
- `BAS_PASSWORD` Defines the password for your BAS instance
- `GRAFANA_PASSWORD` Defines the password for BAS Graphana dashbaord
- `BAS_CONTACT_MAIL` Defines the email for person to contact for BAS
- `BAS_CONTACT_FIRSTNAME` Defines the first name of the person to contact for BAS
- `BAS_CONTACT_LASTNAME` Defines the last name of the person to contact for BAS

### Optional environment variables
- `BAS_USERNAME` Defines the username for the BAS instance, default is `basuser` 
- `GRAFANA_USERNAME` Defines the username for the BAS Graphana instance, default is `basuser` 
- `BAS_NAMESPACE` Defines the namespace where BAS will be installed in openshift, default is `ibm-bas`

### Usage: 

```bash
export BAS_PERSISTENT_STORAGE=xxx
export BAS_META_STORAGE=xxx
export BAS_PASSWORD=xxx
export GRAFANA_PASSWORD=xxx
export BAS_CONTACT_MAIL=xxx
export BAS_CONTACT_FIRSTNAME=xxx
export BAS_CONTACT_LASTNAME=xxx

ansible-playbook playbooks/bas/install-bas.yml
```

