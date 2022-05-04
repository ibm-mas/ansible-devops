ibm_catalogs
============

This role installs the following operator catalogs:

- IBM Operator Catalog (icr.io/cpopen/ibm-operator-catalog)
- IBM CloudPak Foundational Services Catalog (docker.io/ibmcom/ibm-common-service-catalog)

Optionally, the MAS pre-release development operator catalogs can be installed as as well, if `artifactory_username` and `artifactory_apikey` are both set.


Role Variables
--------------
### artifactory_username
Use to enable the install of development catalog sources for pre-release installation.

- Optional
- Environment Variable: `W3_USERNAME`
- Default Value: None

### artifactory_apikey
Use to enable the install of development catalog sources for pre-release installation.

- Optional
- Environment Variable: `ARTIFACTORY_APIKEY`
- Default Value: None

Example Playbook
----------------

```yaml
- hosts: localhost
  roles:
    - ibm.mas_devops.ibm_catalogs
```


License
-------

EPL-2.0
