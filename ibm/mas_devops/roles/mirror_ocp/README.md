mirror_ocp
===============================================================================
This role supports mirroring the Red Hat Platform and **selected content from the Red Hat operator catalogs**.  Only content in the Red Hat catalogs directly used by IBM Maximo Application Suite is mirrored.

Four actions are supported:

- `direct` Directly mirror content to your target registry
- `to-filesystem` Mirror content to the local filesystem
- `from-filesystem` Mirror content from the local filesystem to your target registry

Three **Catalogs** are mirrored, containing the following content:

### certified-operator-index
1. gpu-operator-certified (required by ibm.mas_devops.nvidia_gpu role)
2. kubeturbo-certified (required by ibm.mas_devops.kubeturbo role)
3. ibm-metrics-operator (required by ibm.mas_devops.dro role)
4. ibm-data-reporter-operator (required by ibm.mas_devops.dro role)

### community-operator-index
1. grafana-operator (required by ibm.mas_devops.grafana role)
2. opentelemetry-operator (required by ibm.mas_devops.opentelemetry role)
3. strimzi-kafka-operator (required by ibm.mas_devops.kafka role)

### redhat-operator-index
1. amq-streams (required by ibm.mas_devops.kafka role)
2. openshift-pipelines-operator-rh (required by the MAS CLI)
3. nfd (required by ibm.mas_devops.nvidia_gpu role)
4. aws-efs-csi-driver-operator (required by ibm.mas_devops.ocp_efs role)
5. local-storage-operator (required by ibm.mas_devops.ocs role)
6. odf-operator (required by ibm.mas_devops.ocs role)
7. openshift-cert-manager-operator (required by ibm.mas_devops.cert_manager role)
8. lvms-operator (not directly used, but often used in SNO environments)

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

### registry_prefix
The prefix used for the target registry.  The images will not be mirrored to the registry at this time but will define the final destination in the form: {host}:{port}/{prefix}/{reponame}

- Environment Variable: `REGISTRY_PREFIX`
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
    registry_public_host: myregistry.mycompany.com
    registry_public_port: 5000
    registry_prefix: projectName
    registry_username: user1
    registry_password: 8934jk77s862!  # Not a real password, don't worry security folks

    mirror_mode: direct
    mirror_working_dir: /tmp/mirror
    mirror_redhat_platform: false
    mirror_redhat_operators: true

    ocp_release: 4.15
    redhat_pullsecret: ~/pull-secret.json

  roles:
    - ibm.mas_devops.mirror_ocp
```


License
-------------------------------------------------------------------------------

EPL-2.0
