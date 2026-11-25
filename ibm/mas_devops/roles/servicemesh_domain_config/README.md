# servicemesh_domain_config

Configures Routes, Services, Gateway deployments and Istio configuration to route external requests to MAS through an installed [Red Hat OpenShift Service Mesh](https://docs.redhat.com/en/documentation/red_hat_openshift_service_mesh) instance.

This role is **standalone**: it is not run by the MAS install pipelines. Run it yourself, after MAS has been installed with Service Mesh enabled (`mas_use_service_mesh=true`, which implies `mas_manual_route_mgmt=true`) and Red Hat OpenShift Service Mesh has been installed (see the `servicemesh` role). It can also be run against an existing MAS instance.

The role reads the `routeref-*` ConfigMaps that MAS creates in each application namespace (because MAS does not create Routes when manual route management is enabled) and, for each one, creates a gateway Deployment, Service, Istio Gateway, VirtualService and OpenShift Route in the gateway namespace. It also applies the mesh observability resources (Telemetry, istiod ServiceMonitor, istio-proxy PodMonitors and Kiali monitoring access) and the NetworkPolicies required by the mesh.

The role fails if no Istio control plane is found in `servicemesh_namespace`, or if it is not `Ready`.

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`mas_instance`](#mas_instance) | Yes | None |
| [`mas_domain`](#mas_domain) | No | None |
| [`mas_app_id`](#mas_app_id) | No | All MAS namespaces |
| [`servicemesh_namespace`](#servicemesh_namespace) | No | `istio-system` |
| [`servicemesh_gateway_namespace`](#servicemesh_gateway_namespace) | No | `mas-{mas_instance}-servicemesh` |

### Domain Routing

#### mas_domain

The external domain URL for which request handling will be configured.

- **Optional**
- Environment Variable: `MAS_DOMAIN`
- Default: None but task resolves MAS_DOMAIN as `{mas_instance}.{cluster ingress domain}` from `ingresses.config.openshift.io/cluster`

#### mas_app_id

Limit the configuration to a single MAS application namespace (`mas-{mas_instance}-{mas_app_id}`), for example `manage` or `core`.

- **Optional**
- Environment Variable: `MAS_APP_ID`
- Default: None (the `core`, `facilities`, `iot`, `manage`, `monitor`, `optimizer` and `predict` namespaces are all configured)

Namespaces that have no `routeref-*` ConfigMaps are skipped.

#### mas_instance

The instance of MAS to which requests will be routed.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

The `domain` specified in this MAS instance must match `mas_domain`, or requests will be incorrectly routed. Multiple MAS instances may be configured on a cluster with the same domain, allowing traffic to a domain to be switched from one instance to another.

#### servicemesh_namespace

The namespace in which the Istio control plane is deployed.

- **Optional**
- Environment Variable: `SERVICEMESH_NAMESPACE`
- Default: `istio-system`

#### servicemesh_gateway_namespace

The namespace into which the service mesh domain configuration will be installed.

- **Optional**
- Environment Variable: `SERVICEMESH_GATEWAY_NAMESPACE`
- Default: `mas-{mas_instance}-servicemesh`

When controlling traffic between multiple MAS instances, this variable allows an independent namespace for the routing configuration to be used, without using the name of either instance.

## Example Playbook

```yaml
- hosts: localhost
  vars:
    mas_domain: "test92.apps.servicemesh-489.cp.fyre.ibm.com"
    mas_instance: "test92"
  roles:
    - ibm.mas_devops.servicemesh_domain_config
```

## License

EPL-2.0
