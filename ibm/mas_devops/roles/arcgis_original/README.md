common_services
===============================================================================
This role will install the following operators into the `ibm-common-services` namespace of the target cluster:

- **IBM Cloud Pak Foundational Services**
- **IBM NamespaceScope Operator**
- **Operand Deployment Lifecycle Manager**

Also, an operator group will be created in the namespace if one does not already exist.


Prerequisites
-------------------------------------------------------------------------------
To run this role successfully you must have already installed a CatalogSource that contains IBM Cloud Pak Foundational Services, this can be achieved using the [ibm_catalogs](ibm_catalogs.md) role in this collection.

By default a catalog source of **ibm-operator-catalog** will be expected, but this can be customized using the `common_services_catalog_source` variable.


Role Variables
-------------------------------------------------------------------------------

### common_services_action
Inform the role whether to perform an install, upgrade or uninstall of IBM Cloud Pak Foundational Services.

- Optional
- Environment Variable: `COMMON_SERVICES_ACTION`
- Default: `install`

### common_services_catalog_source
Used to override the operator catalog source used when creating the `ibm-common-service-operator` subscription.

- Optional
- Environment Variable: `COMMON_SERVICES_CATALOG_SOURCE`
- Default Value: `ibm-operator-catalog`

### common_services_channel
Used to override the operator catalog source used when creating the `ibm-common-service-operator` subscription.

- Optional
- Environment Variable: `COMMON_SERVICES_CHANNEL`
- Default Value: Role will lookup the default channel from the operator's package manifest.


Example Playbook
-------------------------------------------------------------------------------
After installing the Ansible Collection you can include this role in your own custom playbooks.

```yaml
- hosts: localhost
  roles:
    - ibm.mas_devops.ibm_catalogs
    - ibm.mas_devops.common_services
```


Run Role Playbook
-------------------------------------------------------------------------------
After installing the Ansible Collection you can easily run the role standalone using the `run_role` playbook provided.

```bash
ROLE_NAME=common_services ansible-playbook ibm.mas_devops.run_role
```


License
-------------------------------------------------------------------------------
EPL-2.0
