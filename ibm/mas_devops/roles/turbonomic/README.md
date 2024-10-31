Turbonomic
===============================================================================
Installs [kubeturbo](https://github.com/turbonomic/kubeturbo) from any available CatalogSource, and automatically configures it to connect to a defined Turbonomic server.

!!! note
    The **Turbonomic Kubernetes Operator** does not support disconnected installation.  The **kubeturbo** deployment will be created using a tag rather than a digest, which prevents the use of an ImageContentSourcePolicy to configure a mirror registry for this image.


Role Variables
-------------------------------------------------------------------------------

| Variable       | Environment Variable | Default | Description |
| :------------- | :------------------- | :------ | :---------- |
| kubeturbo_namespace | `KUBETURBO_NAMESPACE` | `kubeturbo` | Optional.  Set the namespace where the KubeTurbo operator will be installed. |
| turbonomic_target_name | `TURBONOMIC_TARGET_NAME` | None | Required.  This is the name of the cluster as it will be seen in Turbonomic. |
| turbonomic_server_url | `TURBONOMIC_SERVER_URL` | None | Required.  The route is required to access the Turbonomics instance. Kubeturbo communicates with the Turbo Server using the supplied turbonomic route as the Turbonomic Server endpoint while configuring kubeturbo. |
| turbonomic_server_version | `TURBONOMIC_SERVER_VERSION` | None | Optional.  The version of the Turbonomic server you are connecting to. |
| turbonomic_username | `TURBONOMIC_USERNAME` | None | Required.  The username to authenticate with the Turbonomic server. |
| turbonomic_password | `TURBONOMIC_PASSWORD` | None | Required.  The password to authenticate with the Turbonomic server. |


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
