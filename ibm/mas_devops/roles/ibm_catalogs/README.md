# ibm_catalogs
This role installs the **IBM Maximo Operator Catalog**, which is a curated Operator Catalog derived from the **IBM Operator Catalog**, with all content certified compatible with IBM Maximo Application Suite:

Additional, for IBM employees only, the pre-release development operator catalog can be installed, this is achieved by setting both the `artifactory_username` and `artifactory_token` variables.


## Role Variables

### General Variables

#### mas_catalog_version
Version of the IBM Maximo Operator Catalog to install.

- **Optional**
- Environment Variable: `MAS_CATALOG_VERSION`
- Default Value: `@@MAS_LATEST_CATALOG@@`

### Development Variables

#### artifactory_username
Username for Artifactory access to enable installation of development catalog sources for pre-release installation. For IBM employees only.

- **Optional**
- Environment Variable: `ARTIFACTORY_USERNAME`
- Default Value: None

#### artifactory_token
API token for Artifactory access to enable installation of development catalog sources for pre-release installation. For IBM employees only.

- **Optional**
- Environment Variable: `ARTIFACTORY_TOKEN`
- Default Value: None

## Example Playbook
After installing the Ansible Collection you can include this role in your own custom playbooks.

```yaml
- hosts: localhost
  roles:
    - ibm.mas_devops.ibm_catalogs
```


## Run Role Playbook
After installing the Ansible Collection you can easily run the role standalone using the `run_role` playbook provided.

```bash
ROLE_NAME=ibm_catalogs ansible-playbook ibm.mas_devops.run_role
```


## License
EPL-2.0
