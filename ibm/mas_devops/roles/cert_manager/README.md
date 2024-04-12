cert_manager
===============================================================================
Deploy **IBM Certificate Manager Operator** or ****Red Hat Certificate Manager Operator** into the target OCP cluster.

- IBM Certificate Manager Operator and Operand will be installed into the `ibm-common-services` namespace
- Red Hat Certificate Manager Operatos will be installed into the `cert-manager-operator` namespace and the Operand will be created in the `cert-manager` namespace.

The role supports migrtation from an existing IBM Certificate Manager install to the Red Hat Certificate Manager, and will configure the cluster resources namespace to `ibm-common-services` in this case to ensure compatibility with all existing `ClusterIssuers`.


Prerequisites
-------------------------------------------------------------------------------
### IBM Certificate Manager
You must have already installed a CatalogSource that contains IBM Certificate Manager and installed the **IBM Cloud Pak Foundational Services Operator**.  These tasks can be achieved using the [ibm_catalogs](ibm_catalogs.md) and [common_services](common_services.md) roles in this collection.


### Red Hat Certificate Manager
You must have already installed the **Red Hat Operators** CatalogSource.


Role Variables
-------------------------------------------------------------------------------
### cert_manager_action
Inform the role whether to perform an `install` or an `uninstall` the Certificate Manager service, action can also be set to `none` to instruct the role to take no action.

- Optional
- Environment Variable: `CERT_MANAGER_ACTION`
- Default: `install`

### cert_manager_provider
Choose which flavour of Certificate Manager to install; IBM (`ibm`), or Red Hat (`redhat`)

- Optional
- Environment Variable: `CERT_MANAGER_PROVIDER`
- Default: `redhat`

**Note:** Certificate Manager is a cluster-wide dependency, therefore be really careful when uninstalling it as this might be used by several applications and dependencies installed in the cluster.

Example Playbook
-------------------------------------------------------------------------------
After installing the Ansible Collection you can include this role in your own custom playbooks.

### IBM Certificate Manager
```yaml
- hosts: localhost
  vars:
    - cert_manager_action: install
    - cert_manager_provider: ibm
  roles:
    - ibm.mas_devops.ibm_catalogs
    - ibm.mas_devops.common_services
    - ibm.mas_devops.cert_manager
```

### Red Hat Certificate Manager
```yaml
- hosts: localhost
  vars:
    - cert_manager_action: install
    - cert_manager_provider: redhat
  roles:
    - ibm.mas_devops.cert_manager
```


Run Role Playbook
-------------------------------------------------------------------------------
After installing the Ansible Collection you can easily run the role standalone using the `run_role` playbook provided.

```bash
ROLE_NAME=cert_manager ansible-playbook ibm.mas_devops.run_role
```


License
-------------------------------------------------------------------------------
EPL-2.0
