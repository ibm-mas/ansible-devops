# servicemesh_domain_config

Configures Routes, Services, Gateway deployments and Istio configuration to route external requests to MAS Core through an installed [Red Hat OpenShift Service Mesh](https://docs.redhat.com/en/documentation/red_hat_openshift_service_mesh) instance.

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`mas_domain`](#mas_domain) | Yes | None |
| [`mas_instance`](#mas_instance) | Yes | None |
| [`servicemesh_gateway_namespace`](#servicemesh_gateway_namespace) | No | `mas-{mas_instance}-servicemesh` |

### Domain Routing

#### mas_domain

The external domain URL for which request handling will be configured.

- **Required**
- Environment Variable: `MAS_DOMAIN`
- Default: None

#### mas_instance

The instance of MAS to which requests will be routed.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

The `domain` specified in this MAS instance must match `mas_domain`, or requests will be incorrectly routed. Multiple MAS instances may be configured on a cluster with the same domain, allowing traffic to a domain to be switched from one instance to another.

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
