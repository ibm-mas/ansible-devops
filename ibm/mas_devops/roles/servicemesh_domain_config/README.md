# servicemesh_domain_config
Configures Routes, Services, Gateway deployments and Istio configuration to route external requests to MAS Core through an installed [Red Hat OpenShift Service Mesh](https://docs.redhat.com/en/documentation/red_hat_openshift_service_mesh) instance.


## Role Variables
### mas_domain
The external domain URL for which request handling will be configured.

- **Required**
- Environment Variable: `MAS_DOMAIN`
- Default: None

**Purpose**: Specifies the domain URL for which routes should be configured.

### mas_instance
The instance of MAS to which requests will be routed.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

**Purpose**: Specifies the MAS instance installed on this cluster to which requests will be routed. The `domain` specified in this MAS instance must match the `mas_domain` variable defined here or requests will be incorrectly routed.
Note that multiple MAS Instances may be configured on a cluster with the same domain and so traffic to a domain may be switched from one instance to another.

### servicemesh_gateway_namespace
The namespace into which the service mesh domain configuration will be installed..

- **Optional**
- Environment Variable: `SERVICEMESH_GATEWAY_NAMESPACE`
- Default: 'mas-{mas_instance}-servicemesh'

**Purpose**: If we are wishing to control traffic between multiple MAS instances, this variable allows us to configure an independent namespace for the routing configuration without using the name of either instance.


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
