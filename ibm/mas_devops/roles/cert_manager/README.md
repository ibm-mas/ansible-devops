# cert_manager
This role deploys the Red Hat Certificate Manager Operator into the target OpenShift cluster. The operator will be installed into the `cert-manager-operator` namespace, and the operand will be created in the `cert-manager` namespace.

Certificate Manager provides certificate management capabilities for Kubernetes and OpenShift clusters, enabling automated certificate provisioning and renewal.

## Prerequisites
- Red Hat Operators CatalogSource must be installed in the cluster
- Cluster administrator access

## Role Variables

### General Variables

#### cert_manager_action
Specifies which operation to perform on the Certificate Manager operator.

- **Optional**
- Environment Variable: `CERT_MANAGER_ACTION`
- Default Value: `install`

**Purpose**: Controls what action the role executes against the Certificate Manager operator. This allows the same role to handle installation, removal, or no action on the cert-manager deployment.

**When to use**:
- Use `install` (default) for initial deployment or to ensure cert-manager is present
- Use `uninstall` to remove cert-manager (use with extreme caution)
- Use `none` to skip cert-manager operations while running broader playbooks

**Valid values**: `install`, `uninstall`, `none`

**Impact**: 
- `install`: Deploys Red Hat Certificate Manager Operator to `cert-manager-operator` namespace and creates operand in `cert-manager` namespace
- `uninstall`: Removes cert-manager operator and operand (destructive operation)
- `none`: Role takes no action

**Related variables**: None

**Note**: **WARNING** - Certificate Manager is a cluster-wide dependency used by MAS, SLS, and other components. Uninstalling it will break certificate management for all dependent applications. Only use `uninstall` if you are certain no applications depend on it.

## Example Playbook
After installing the Ansible Collection you can include this role in your own custom playbooks.

```yaml
- hosts: localhost
  vars:
    cert_manager_action: install
  roles:
    - ibm.mas_devops.cert_manager
```

## Run Role Playbook
After installing the Ansible Collection you can easily run the role standalone using the `run_role` playbook provided.

```bash
export CERT_MANAGER_ACTION=install
ROLE_NAME=cert_manager ansible-playbook ibm.mas_devops.run_role
```

## License
EPL-2.0
