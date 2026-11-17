# servicemesh

Installs and configures an instance of [Red Hat OpenShift Service Mesh](https://docs.redhat.com/en/documentation/red_hat_openshift_service_mesh) for use with IBM Maximo Application Suite.

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`servicemesh_action`](#servicemesh_action) | No | `install` |
| [`servicemesh_channel`](#servicemesh_channel) | No | `stable-3.5` |
| [`servicemesh_starting_csv`](#servicemesh_starting_csv) | No | `servicemeshoperator3.v3.5.0` |
| [`servicemesh_namespace`](#servicemesh_namespace) | No | `istio-system` |
| [`servicemesh_cni_namespace`](#servicemesh_cni_namespace) | No | `istio-cni` |
| [`istio_version`](#istio_version) | No | `v1.31.1` |
| [`servicemesh_catalog_source`](#servicemesh_catalog_source) | No | Detected from the PackageManifest |
| [`servicemesh_catalog_source_namespace`](#servicemesh_catalog_source_namespace) | No | `openshift-marketplace` |
| [`install_kiali`](#install_kiali) | No | `false` |
| [`kiali_channel`](#kiali_channel) | No | `stable` |
| [`kiali_starting_csv`](#kiali_starting_csv) | No | `kiali-operator.v2.33.1` |

### Service Mesh Configuration

#### servicemesh_action

Action to perform on the Service Mesh installation.

- **Optional**
- Environment Variable: `SERVICEMESH_ACTION`
- Default: `install`

Valid values are `install` (deploy the Service Mesh operator and instance, the default; the Kiali operator and instance are also deployed when `install_kiali` is set to `true`, either as a playbook variable or through the `INSTALL_KIALI` environment variable), `install-kiali` (deploy only the Kiali operator and instance, without installing Service Mesh), and `uninstall` (remove the Service Mesh and Kiali operators and instances). The catalog channel and starting CSV for both Service Mesh and Kiali can be pinned via the `servicemesh_channel`, `servicemesh_starting_csv`, `kiali_channel`, and `kiali_starting_csv` properties, which use the operator defaults when not provided.

#### servicemesh_channel

OLM subscription channel for the Service Mesh operator.

- **Optional**
- Environment Variable: `SERVICEMESH_CHANNEL`
- Default: `stable-3.5`

#### servicemesh_starting_csv

Starting ClusterServiceVersion (CSV) for the Service Mesh operator subscription.

- **Optional**
- Environment Variable: `SERVICEMESH_CSV`
- Default: `servicemeshoperator3.v3.5.0`

#### servicemesh_namespace

Namespace where the Istio control plane (and the Kiali instance) is deployed.

- **Optional**
- Environment Variable: `SERVICEMESH_NAMESPACE`
- Default: `istio-system`

The namespace is created by the `install` action and deleted by the `uninstall` action.

#### servicemesh_cni_namespace

Namespace where the Istio CNI plugin is deployed.

- **Optional**
- Environment Variable: `SERVICEMESH_CNI_NAMESPACE`
- Default: `istio-cni`

The namespace is created by the `install` action and deleted by the `uninstall` action.

#### istio_version

Istio version used for the IstioCNI resource.

- **Optional**
- Environment Variable: `ISTIO_VERSION`
- Default: `v1.31.1`

### Catalog Source

#### servicemesh_catalog_source

Catalog source to install the Service Mesh and Kiali operators from.

- **Optional**
- Environment Variable: `SERVICEMESH_CATALOG_SOURCE`
- Default: detected from the PackageManifest

When left empty, the catalog is detected from the PackageManifest, so the role works with the built-in `redhat-operators` catalog and with a mirrored catalog on a disconnected (airgap) cluster.

#### servicemesh_catalog_source_namespace

Namespace of the catalog source used for the Service Mesh and Kiali operators.

- **Optional**
- Environment Variable: `SERVICEMESH_CATALOG_SOURCE_NAMESPACE`
- Default: `openshift-marketplace`

The role waits for the `servicemeshoperator3` and `kiali-ossm` PackageManifests in this namespace before creating the subscriptions.

### Kiali Configuration

#### install_kiali

Whether the `install` action also deploys the Kiali operator and instance.

- **Optional**
- Environment Variable: `INSTALL_KIALI`
- Default: `false`

Has no effect on the `install-kiali` action, which always deploys Kiali.

#### kiali_channel

OLM subscription channel for the Kiali operator.

- **Optional**
- Environment Variable: `KIALI_CHANNEL`
- Default: `stable`

#### kiali_starting_csv

Starting ClusterServiceVersion (CSV) for the Kiali operator subscription.

- **Optional**
- Environment Variable: `KIALI_CSV`
- Default: `kiali-operator.v2.33.1`

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
