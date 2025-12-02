cert_manager
===============================================================================
Deploy **Red Hat Certificate Manager Operator** into the target OCP cluster.  The operator will be installed into the `cert-manager-operator` namespace, the operand will be created in the `cert-manager` namespace.


Prerequisites
-------------------------------------------------------------------------------
You must have already installed the **Red Hat Operators** CatalogSource.


Role Variables
-------------------------------------------------------------------------------
### cert_manager_action
Inform the role whether to perform an `install` or an `uninstall` the Certificate Manager service, action can also be set to `none` to instruct the role to take no action.

- Optional
- Environment Variable: `CERT_MANAGER_ACTION`
- Default: `install`

**Note:** Certificate Manager is a cluster-wide dependency, therefore be really careful when uninstalling it as this might be used by several applications and dependencies installed in the cluster.

Example Playbook
-------------------------------------------------------------------------------
After installing the Ansible Collection you can include this role in your own custom playbooks.

```yaml
- hosts: localhost
  vars:
    - cert_manager_action: install
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
