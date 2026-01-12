# cert_manager
This role deploys the Red Hat Certificate Manager Operator into the target OpenShift cluster. The operator will be installed into the `cert-manager-operator` namespace, and the operand will be created in the `cert-manager` namespace.

Certificate Manager provides certificate management capabilities for Kubernetes and OpenShift clusters, enabling automated certificate provisioning and renewal.

## Prerequisites
- Red Hat Operators CatalogSource must be installed in the cluster
- Cluster administrator access

## Role Variables

### General Variables

#### cert_manager_action
Inform the role whether to perform an `install` or `uninstall` of the Certificate Manager service. Action can also be set to `none` to instruct the role to take no action.

- **Optional**
- Environment Variable: `CERT_MANAGER_ACTION`
- Default Value: `install`

!!! warning
    Certificate Manager is a cluster-wide dependency. Be careful when uninstalling it as it might be used by several applications and dependencies installed in the cluster.

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
