Turbonomic
===============================================================================
Installs [kubeturbo](https://github.com/turbonomic/kubeturbo) from any available CatalogSource, and automatically configures it to connect to a defined Turbonomic server.


Role Variables - KubeTurbo Configuration
-------------------------------------------------------------------------------
### kubeturbo_namespace
Set the namespace where the KubeTurbo operator will be installed.

- Optional
- Environment Variable: `KUBETURBO_NAMESPACE`
- Default: `kubeturbo`


Role Variables - Turbonomic Server Configuration
-------------------------------------------------------------------------------
### turbonomic_target_name
The cluster name is required to install Kubeturbo. The agent component is deployed onto target Kubernetes and OpenShift cluster which then send data to the Turbonomic ARM server.

- **Required**
- Environment Variable: `TURBONOMIC_TARGET_NAME`
- Default: None

### turbonomic_server_url
The route is required to access the Turbonomics instance. Kubeturbo communicates with the Turbo Server using the supplied turbonomic route as the Turbonomic Server endpoint while configuring kubeturbo.

- **Required**
- Environment Variable: `TURBONOMIC_SERVER_URL`
- Default: None

### turbonomic_server_version
The version of the Turbonomic server you are connecting to.

- Optional
- Environment Variable: `TURBONOMIC_SERVER_VERSION`
- Default: None

### turbonomic_username
The username to authenticate with the Turbonomic server.

- **Required**
- Environment Variable: `TURBONOMIC_USERNAME`
- Default: None

### turbonomic_password
The password to authenticate with the Turbonomic server.

- **Required**
- Environment Variable: `TURBONOMIC_PASSWORD`
- Default: None


Example Playbook
-------------------------------------------------------------------------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    turbonomic_server_url: https://myturbonomicserver.com
    turbonomic_server_version: "8.9.4"
    turbonomic_username: user
    turbonomic_password: passw0rd
    turbonomic_target_name: myocp
  roles:
    - ibm.mas_devops.turbonomic
```

License
-------------------------------------------------------------------------------
EPL-2.0
