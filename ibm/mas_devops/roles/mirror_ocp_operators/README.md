ocp_operators_mirror
====================
This role uses the specifed Red Hat OpenShift Operator version to mirror the standard OpenShift catalog container images to a mirror registry and configure the cluster to pull images from this mirror.

When mirroring is complete, you can view the content of your registry:

```bash
curl -k https://$REGISTRY_PUBLIC_HOST/v2/_catalog | jq
```

Requirements
------------
- `oc` tool must be installed


Role Variables
--------------
### openshift_operators_version
The version of the operator catalogs to be mirrored in major.minor format, e.g. `4.8`.

- **Required**
- Environment Variable: `OPENSHIFT_OPERATORS_VERSION`
- Default: None

### log_dir
The directory to write output log.

- **Required**
- Environment Variable: `LOG_DIR`
- Default: `/tmp`


Role Variables - Red Hat Authentication
---------------------------------------
### redhat_connect_username
The username for accessing Red Hat docker images.

- **Required**
- Environment Variable: `REDHAT_CONNECT_USERNAME`
- Default: None

### redhat_connect_password
The password for accessing Red Hat docker images.

- **Required**
- Environment Variable: `REDHAT_CONNECT_PASSWORD`
- Default: None


Role Variables - Target Registry
--------------------------------
### registry_public_host
The public hostname for the target registry

- **Required**
- Environment Variable: `REGISTRY_PUBLIC_HOST`
- Default: None

### registry_public_port
The public port number for the target registry

- **Required**
- Environment Variable: `REGISTRY_PUBLIC_PORT`
- Default: None

### registry_username
The username for the target registry, if the target registry requires authentication.

- Optional
- Environment Variable: `REGISTRY_USERNAME`
- Default: None

### registry_password
The password for the target registry, if the target registry requires authentication.

- Optional
- Environment Variable: `REGISTRY_PASSWORD`
- Default: None


Example Playbook
----------------

```yaml
- hosts: localhost
  vars:
    openshift_operators_version: 4.8
    registry_public_host: myocp-5f1320191125833da1cac8216c06779e-0000.us-south.containers.appdomain.cloud
    registry_public_port: 32500

  roles:
    - ibm.mas_airgap.ocp_operators_mirror
```


License
-------

EPL-2.0
