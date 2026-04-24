# servicemesh
Installs and configures an instance of [Red Hat OpenShift Service Mesh](https://docs.redhat.com/en/documentation/red_hat_openshift_service_mesh) for use with IBM Maximo Application Suite.


## Role Variables
### servicemesh_action
Action to perform on Service Mesh installation.

- **Optional**
- Environment Variable: `SERVICEMESH_ACTION`
- Default: `install`

**Purpose**: Specifies whether to install, uninstall, or install-kiali.

**When to use**:
- Use `install` (default) for new Service Mesh deployments
- Use `install-kiali` to install only the Kiali monitoring component
- Use `uninstall` to remove Service Mesh

**Valid values**: `install`, `uninstall`, `install-kiali`

**Impact**: 
- `install`: Deploys Service Mesh operator and instance
- `install-kiali`: Deploys Service Mesh operator and instance
- `uninstall`: Removes Service Mesh and Kiali operators and instances

**Related variables**:
- `servicemesh_channel`: Catalog channel to install from (defaults if not provided)
- `servicemesh_starting_csv`: Specific CSV to install (defaults if not provided)
- `kiali_channel`: Catalog channel to install Kiali from (defaults if not provided)
- `kiali_starting_csv`: Specific CSV to install Kiali (defaults if not provided)


## Example Playbook

```yaml
- hosts: localhost
  vars:
    install_kiali: "true"
  roles:
    - ibm.mas_devops.servicemesh
```

## License

EPL-2.0
