mirror_ocp
===============================================================================
This role supports mirroring the Red Hat Platform and **selected content from the Red Hat operator catalogs**.  Only content in the Red Hat catalogs directly used by IBM Maximo Application Suite is mirrored.

Four actions are supported:

- `direct` Directly mirror content to your target registry
- `to-filesystem` Mirror content to the local filesystem
- `from-filesystem` Mirror content from the local filesystem to your target registry
- `install-catalogs` Install CatalogSources for the mirrored content.

Two **CatalogSources** are created by the `install-catalogs` action in the `openshift-marketplace` namespace, containing the following content:

### certified-operator-index
- crunchy-postgres-operator (required by ibm.mas_devops.uds role)

### redhat-operator-index
- amq-streams (required by ibm.mas_devops.kafka role)
- openshift-pipelines-operator-rh (required by the MAS CLI)

!!! note
    We are limited to the content we can support mirroring for today due to bug with Red Hat's support for OCI images, this prevents the mirroring of the following packages (which are all optional dependencies):

    - **kubeturbo-certified**
    - **grafana-operator**
    - **opentelemetry-operator**

    For more information refer to [solution 6997884](https://access.redhat.com/solutions/6997884) and [CFE 780](https://issues.redhat.com/browse/CFE-780).


Requirements
-------------------------------------------------------------------------------
- `oc` tool must be installed
- `oc-mirror` plugin must be installed


Role Variables
-------------------------------------------------------------------------------
### mirror_mode
Set the action to perform (`direct`, `to-filesystem`, `from-filesystem`)

- **Required**
- Environment Variable: `MIRROR_MODE`
- Default: None


Role Variables - Mirror Actions
-------------------------------------------------------------------------------
### mirror_working_dir
Set the working directory for the mirror operations

- **Required**
- Environment Variable: `MIRROR_WORKING_DIR`
- Default: None

### mirror_redhat_platform
Enable mirroring of the Red Hat platform images.

- **Optional**
- Environment Variable: `MIRROR_REDHAT_PLATFORM`
- Default: `False`

### mirror_redhat_operators
Enable mirroring of **selected content** from the Red Hat operator catalogs.

- **Optional**
- Environment Variable: `MIRROR_REDHAT_OPERATORS`
- Default: `False`

### redhat_pullsecret
Path to your Red Hat pull secret, available from: [https://console.redhat.com/openshift/install/pull-secret](https://console.redhat.com/openshift/install/pull-secret).

- **Required**
- Environment Variable: `REDHAT_PULLSECRET`
- Default: None


Role Variables - OpenShift Version
-------------------------------------------------------------------------------
### ocp_release
The Red Hat release you are mirroring content for, e.g. `4.12`.

- **Required**
- Environment Variable: `OCP_RELEASE`
- Default: None

### ocp_min_version
The minimum version of the Red Hat release to mirror platform content for, e.g. `4.12.0`.

- **Optional**
- Environment Variable: `OCP_MIN_VERSION`
- Default: None

### ocp_max_version
The maximimum version of the Red Hat release to mirror platform content for, e.g. `4.12.18`.

- **Optional**
- Environment Variable: `OCP_MAX_VERSION`
- Default: None


Role Variables - Target Registry
-------------------------------------------------------------------------------
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
The username for the target registry.

- **Required**
- Environment Variable: `REGISTRY_USERNAME`
- Default: None

### registry_password
The password for the target registry.

- **Required**
- Environment Variable: `REGISTRY_PASSWORD`
- Default: None


Example Playbook
-------------------------------------------------------------------------------

```yaml
- hosts: localhost
  vars:
    registry_public_host: myocp-5f1320191125833da1cac8216c06779e-0000.us-south.containers.appdomain.cloud
    registry_public_port: 32500
    registry_username: admin
    registry_password: 8934jk77s862!  # Not a real password, don't worry security folks

    mirror_mode: direct
    mirror_working_dir: /tmp/mirror
    mirror_redhat_platform: false
    mirror_redhat_operators: true

    ocp_release: 4.12
    redhat_pullsecret: ~/pull-secret.json

  roles:
    - ibm.mas_devops.mirror_ocp
```


License
-------------------------------------------------------------------------------

EPL-2.0
