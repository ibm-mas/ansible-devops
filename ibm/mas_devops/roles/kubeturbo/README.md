Kubeturbo
============
Installs a kubeturbo instance and sends data to a defined Turbonomic instance under the cluster name.

Role Variables
--------------

### cluster_name
Required. The cluster name is required to install Kubeturbo. The agent component is deployed onto target Kubernetes and OpenShift cluster which then send data to the Turbonomic ARM server.

- Environment Variable: `CLUSTER_NAME`
- Default: None

### turbonomic_username: 
Required. The username is required to access the Turbonomics instance.

- Environment Variable: `TURBONOMIC_USERNAME`
- Default: None

### turbonomic_password: 
Required. The password is required to access the Turbonomics instance.

- Environment Variable: `TURBONOMIC_PASSWORD`
- Default: None

### turbonomic_route
Required. The route is required to access the Turbonomics instance. Kubeturbo communicates with the Turbo Server using the supplied turbonomic route as the Turbonomic Server endpoint while configuring kubeturbo.

- Environment Variable: `TURBONOMIC_ROUTE`
- Default: None

### kubeturbo_namespace

- Optional
- Environment Variable: `KUBETURBO_NAMESPACE`
- Default: KUBETURBO 

### kubeturbo_channel

- Optional
- Environment Variable: `KUBETURBO_CHANNEL`
- Default: STABLE

### kubeturbo_cr_name

- Optional
- Environment Variable: `KUBETURBO_CR_NAME`
- Default: KUBETURBO-RELEASE

### kubeturbo_tag_release

- Optional
- Environment Variable: `KUBETURBO_TAG_RELEASE`
- Default: 8.7.5

Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    cluster_name: "cluster1"
    turbonomic_username: "user01"
    turbonomic_password: ******
    turbonomic_route: "https://turbo.com"

  roles:
    - ibm.mas_devops.kubeturbo
```

License
-------

EPL-2.0
