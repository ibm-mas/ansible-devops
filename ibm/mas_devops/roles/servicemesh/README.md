# servicemesh

Installs and configures an instance of [Red Hat OpenShift Service Mesh](https://docs.redhat.com/en/documentation/red_hat_openshift_service_mesh) for use with IBM Maximo Application Suite.

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`servicemesh_action`](#servicemesh_action) | No | `install` |

### Service Mesh Configuration

#### servicemesh_action

Action to perform on the Service Mesh installation.

- **Optional**
- Environment Variable: `SERVICEMESH_ACTION`
- Default: `install`

Valid values are `install` (deploy the Service Mesh operator and instance, the default; the Kiali operator and instance are also deployed when `INSTALL_KIALI` env set as `true`), `install-kiali` (deploy only the Kiali operator and instance, without installing Service Mesh), and `uninstall` (remove the Service Mesh and Kiali operators and instances). The catalog channel and starting CSV for both Service Mesh and Kiali can be pinned via the `servicemesh_channel`, `servicemesh_starting_csv`, `kiali_channel`, and `kiali_starting_csv` properties, which use the operator defaults when not provided.

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
