# ocp_idms
Installs an **ImageDigestMirrorSet** (IDMS)for IBM Maximo Application Suite's Maximo Operator Catalog.
Also install IDMS suitable for the Red Hat Operator Catalogs created by [mirror_ocp](mirror_ocp.md).
If there are legacy **ImageContentSourcePolicies** installed by previous versions of this role, they will be deleted.

If PRODUCT_FAMILY is aiservice then it will install an **ImageTagMirrorSet** for OpenDataHub

!!! warning
    This role doesn't work on IBMCloud ROKS.  IBM Cloud RedHat OpenShift Service does not implement support for `ImageDigestMirrorSet`.  If you want to use image mirroring you must manually configure each worker node individually using the IBM Cloud command line tool.


IBM Maximo Operator Catalog Content
All content used in the MAS install is sourced from three registries: **icr.io**, **cp.icr.io**, & **quay.io**:

- **icr.io/cpopen** All IBM operators
- **icr.io/ibm-truststore-mgr** IBM truststore manager worker image
- **icr.io/ibm-sls** IBM SLS content
- **icr.io/db2u** IBM Db2 Universal operator content
- **cp.icr.io/cp** All IBM entitled container images
- **quay.io/opencloudio** IBM common services
- **quay.io/mongodb** MongoDb Community Edition Operator & associated container images
- **quay.io/amlen** Eclipse Amlen - Message Broker for IoT/Mobile/Web
- **quay.io/ibmmas** Non-product IBM Maximo Application Suite images (e.g. MAS CLI)

Red Hat Operator Catalog Content
All content from the subset of the Red Hat operator catalogs supported by [mirror_ocp](mirror_ocp.md) is sourced from eight registries: **icr.io**, **docker.io**, **quay.io**, **gcr.io**, **ghcr.io**, **nvcr.io**, **registry.connect.redhat.com**, and **registry.redhat.io**:

- **icr.io/cpopen**
- **docker.io/grafana**
- **quay.io/community-operator-pipeline-prod**
- **quay.io/operator-pipeline-prod**
- **quay.io/openshift-community-operators**
- **quay.io/strimzi**
- **quay.io/rh-marketplace**
- **gcr.io/kubebuilder**
- **ghcr.io/grafana**
- **ghcr.io/open-telemetry**
- **nvcr.io/nvidia**
- **registry.connect.redhat.com/crunchydata**
- **registry.connect.redhat.com/nvidia**
- **registry.connect.redhat.com/turbonomic**
- **registry.connect.redhat.com/rh-marketplace**
- **registry.redhat.io/openshift4**
- **registry.redhat.io/source-to-image**
- **registry.redhat.io/odf4**
- **registry.redhat.io/cert-manager**
- **registry.redhat.io/rhceph**
- **registry.redhat.io/amq-streams**
- **registry.redhat.io/ubi8**
- **registry.redhat.io/openshift-pipelines**
- **registry.redhat.io/openshift-serverless-1**
- **registry.redhat.io/lvms4**

!!! note
    A content source policy for this content is only configured when **setup_redhat_catalogs** is set to `True`.

If you are managing the Red Hat Operator Catalogs yourself the content therein may well be different depending how you have configured mirroring.


## Role Variables
### product_family
Product family for ImageDigestMirrorSet configuration.

- **Optional**
- Environment Variable: `PRODUCT_FAMILY`
- Default: `mas`

**Purpose**: Specifies which product family's ImageDigestMirrorSet (IDMS) to create. Different product families have different image source registries.

**When to use**:
- Use default (`mas`) for IBM Maximo Application Suite deployments
- Set to `aiservice` for AI Service deployments (creates ImageTagMirrorSet for OpenDataHub)
- Determines which image registries are configured in the IDMS

**Valid values**: `mas`, `aiservice`

**Impact**:
- `mas`: Creates IDMS for MAS-related registries (icr.io, cp.icr.io, quay.io)
- `aiservice`: Creates ImageTagMirrorSet for OpenDataHub registries

**Related variables**:
- `registry_prefix`: Prefix for IBM content in target registry

**Note**: MAS and AI Service have different image source registries. The IDMS/ITMS configuration varies based on the product family.

### setup_redhat_release
Enable ImageDigestMirrorSet for Red Hat release content.

- **Optional**
- Environment Variable: `SETUP_REDHAT_RELEASE`
- Default: `false`

**Purpose**: Controls whether to create an ImageDigestMirrorSet for mirrored Red Hat OpenShift platform release content. Required when using mirrored OpenShift platform images.

**When to use**:
- Set to `true` when you've mirrored OpenShift platform images with `mirror_ocp` role
- Leave as `false` (default) if not using mirrored platform images
- Only needed for air-gapped OpenShift installations or upgrades

**Valid values**: `true`, `false`

**Impact**:
- `true`: Creates IDMS named `ibm-mas-redhat-release` for platform images
- `false`: No IDMS created for platform images

**Related variables**:
- `registry_prefix_redhat`: Prefix for Red Hat content in target registry
- `setup_redhat_catalogs`: Related but separate (for operator catalogs)

**Note**: This creates an additional IDMS policy. Only enable if you've mirrored OpenShift platform images using the `mirror_ocp` role with `mirror_redhat_platform=true`.

### setup_redhat_catalogs
Enable CatalogSources and ImageDigestMirrorSet for Red Hat operator catalogs.

- **Optional**
- Environment Variable: `SETUP_REDHAT_CATALOGS`
- Default: `false`

**Purpose**: Controls whether to create CatalogSources and ImageDigestMirrorSet for mirrored Red Hat operator catalog content. Required when using mirrored Red Hat operators.

**When to use**:
- Set to `true` when you've mirrored Red Hat operator catalogs with `mirror_ocp` role
- Leave as `false` (default) if not using mirrored operator catalogs
- Required for air-gapped deployments using Red Hat operators

**Valid values**: `true`, `false`

**Impact**:
- `true`: Creates CatalogSources and IDMS named `ibm-mas-redhat-catalogs` for operator images
- `false`: No CatalogSources or IDMS created for operator catalogs

**Related variables**:
- `registry_prefix_redhat`: Prefix for Red Hat content in target registry
- `redhat_catalogs_prefix`: Optional prefix for CatalogSource names
- `setup_redhat_release`: Related but separate (for platform images)

**Note**: This creates CatalogSources for certified-operator-index, community-operator-index, and redhat-operator-index. Only enable if you've mirrored operator catalogs using the `mirror_ocp` role with `mirror_redhat_operators=true`.


Role Variables - Target Registry
### registry_private_host
Private hostname for the mirror registry.

- **Required**
- Environment Variable: `REGISTRY_PRIVATE_HOST`
- Default: None

**Purpose**: Specifies the private/internal hostname of the mirror registry accessible from within the OpenShift cluster. Used in ImageDigestMirrorSet to redirect image pulls.

**When to use**:
- Always required for IDMS configuration
- Must be the hostname accessible from cluster nodes
- Typically an internal/private hostname or IP address

**Valid values**: Valid hostname or IP address accessible from cluster (e.g., `registry.internal.example.com`, `10.0.0.100`)

**Impact**: Cluster nodes will pull images from this registry. Incorrect hostname will cause image pull failures.

**Related variables**:
- `registry_private_port`: Port for this registry
- `registry_private_ca_file`: CA certificate for this registry

**Note**: This must be the hostname accessible from within the cluster, not necessarily the public hostname. For disconnected environments, this is typically an internal registry.

### registry_private_port
Private port for the mirror registry.

- **Optional**
- Environment Variable: `REGISTRY_PRIVATE_PORT`
- Default: None

**Purpose**: Specifies the private/internal port of the mirror registry accessible from within the OpenShift cluster.

**When to use**:
- Set if registry uses a non-standard port
- Leave unset if registry uses standard HTTPS port (443)
- Must match the port accessible from cluster nodes

**Valid values**: Valid port number (e.g., `443`, `5000`, `32500`)

**Impact**: Cluster nodes will pull images from this port. Incorrect port will cause image pull failures.

**Related variables**:
- `registry_private_host`: Hostname for this registry

**Note**: If unset, the registry URL will not include a port (assumes standard HTTPS port 443).

### registry_private_ca_file
Path to registry CA certificate file.

- **Required**
- Environment Variable: `REGISTRY_PRIVATE_CA_FILE`
- Default: None

**Purpose**: Specifies the path to the CA certificate file for the mirror registry. Required for cluster nodes to trust the registry's TLS certificate.

**When to use**:
- Always required for IDMS configuration
- Must be the CA certificate that signed the registry's TLS certificate
- Required even if registry uses self-signed certificates

**Valid values**: Absolute path to CA certificate file (e.g., `~/registry-ca.crt`, `/tmp/registry-ca.pem`)

**Impact**: CA certificate is added to cluster nodes' trust store. Without it, nodes cannot pull images from the registry.

**Related variables**:
- `registry_private_host`: Registry using this CA certificate

**Note**: The CA certificate is added to all cluster nodes via MachineConfig. This causes nodes to reboot. Ensure the certificate is valid and matches the registry's TLS certificate.

### registry_username
Username for mirror registry authentication.

- **Required**
- Environment Variable: `REGISTRY_USERNAME`
- Default: None

**Purpose**: Provides the username for authenticating to the mirror registry. Used to create pull secrets for cluster nodes.

**When to use**:
- Always required for IDMS configuration
- Must have pull permissions from the mirror registry
- Credentials are stored in cluster pull secret

**Valid values**: Valid username for the mirror registry

**Impact**: Used to authenticate image pulls from the mirror registry. Without valid credentials, image pulls will fail.

**Related variables**:
- `registry_password`: Password paired with this username

**Note**: Credentials are added to the cluster's global pull secret. Keep credentials secure.

### registry_password
Password for mirror registry authentication.

- **Required**
- Environment Variable: `REGISTRY_PASSWORD`
- Default: None

**Purpose**: Provides the password for authenticating to the mirror registry. Used to create pull secrets for cluster nodes.

**When to use**:
- Always required for IDMS configuration
- Must correspond to the provided username
- Credentials are stored in cluster pull secret

**Valid values**: Valid password for the mirror registry

**Impact**: Used to authenticate image pulls from the mirror registry. Without valid credentials, image pulls will fail.

**Related variables**:
- `registry_username`: Username paired with this password

**Note**: Credentials are added to the cluster's global pull secret. Keep passwords secure. Never commit to version control.

### registry_prefix
Path prefix for IBM content in mirror registry.

- **Optional**
- Environment Variable: `REGISTRY_PREFIX`
- Default: None

**Purpose**: Specifies an optional path prefix for IBM Maximo Operator Catalog images in the mirror registry. Helps organize registry content.

**When to use**:
- Leave unset if images are at registry root
- Set to match the prefix used when mirroring with `mirror_images` role
- Recommended: Use catalog datestamp (e.g., `mas-241107`, `mas-241205`)

**Valid values**: Valid registry path (e.g., `mas-241107`, `mas-241205`, `ibm-mas`)

**Impact**: IDMS will redirect image pulls to `{host}:{port}/{prefix}/{reponame}`. Must match the actual image locations in the registry.

**Related variables**:
- `registry_private_host`: Registry containing these images
- `registry_prefix_redhat`: Separate prefix for Red Hat content

**Note**: Must match the prefix used when mirroring images. Using datestamp prefixes helps organize multiple mirror versions in the same registry.

### registry_prefix_redhat
Path prefix for Red Hat content in mirror registry.

- **Optional** (Required when `setup_redhat_release=true` or `setup_redhat_catalogs=true`)
- Environment Variable: `REGISTRY_PREFIX_REDHAT`
- Default: None

**Purpose**: Specifies an optional path prefix for Red Hat Release and Operator Catalog images in the mirror registry. Helps organize registry content.

**When to use**:
- Required when `setup_redhat_release=true` or `setup_redhat_catalogs=true`
- Set to match the prefix used when mirroring with `mirror_ocp` role
- Recommended: Use OpenShift release (e.g., `ocp-412`, `ocp-414`)

**Valid values**: Valid registry path (e.g., `ocp-412`, `ocp-414`, `ocp-419`)

**Impact**: IDMS will redirect Red Hat image pulls to `{host}:{port}/{prefix}/{reponame}`. Must match the actual image locations in the registry.

**Related variables**:
- `setup_redhat_release`: Whether to create IDMS for platform images
- `setup_redhat_catalogs`: Whether to create IDMS for operator catalogs
- `registry_prefix`: Separate prefix for IBM content

**Note**: Must match the prefix used when mirroring Red Hat content with `mirror_ocp` role. Using OpenShift release prefixes helps organize multiple OCP versions in the same registry.

### redhat_catalogs_prefix
Prefix for Red Hat CatalogSource names.

- **Optional**
- Environment Variable: `REDHAT_CATALOGS_PREFIX`
- Default: None

**Purpose**: Specifies an optional prefix for the CatalogSource names created for Red Hat operator catalogs. Helps avoid naming conflicts.

**When to use**:
- Leave unset for default CatalogSource names
- Set to add a prefix to CatalogSource names (e.g., `ibm-mas`)
- Only applies when `setup_redhat_catalogs=true`

**Valid values**: Valid Kubernetes resource name prefix (e.g., `ibm-mas`, `mas`, `custom`)

**Impact**:
- When set to `ibm-mas`: Creates `ibm-mas-certified-operator-index`, `ibm-mas-community-operator-index`, `ibm-mas-redhat-operator-index`
- When unset: Creates `certified-operator-index`, `community-operator-index`, `redhat-operator-index`

**Related variables**:
- `setup_redhat_catalogs`: Must be `true` for this to apply

**Note**: Use a prefix if you need to distinguish these CatalogSources from others in the cluster or to avoid naming conflicts.

### machine_config_multiupdate
Enable parallel node updates during MachineConfig application.

- **Optional**
- Environment Variable: `MACHINE_CONFIG_MULTIUPDATE`
- Default: `false`

**Purpose**: Controls whether multiple worker nodes can be updated in parallel when applying MachineConfig changes (for CA certificate installation). Speeds up initial setup but requires careful consideration.

**When to use**:
- Leave as `false` (default) for production environments
- Set to `true` only during initial cluster setup with lightly loaded nodes
- Only recommended when nodes can be safely drained in parallel

**Valid values**: `true`, `false`

**Impact**:
- `true`: Multiple worker nodes updated in parallel (faster but riskier)
- `false`: Worker nodes updated one at a time (slower but safer)

**Related variables**:
- `registry_private_ca_file`: CA certificate that triggers MachineConfig updates

**Note**: **WARNING** - Only enable during initial setup when nodes are lightly loaded. In production, leave as `false` to ensure workload availability during node updates. MachineConfig changes cause node reboots.

## Example Playbook

```yaml
- hosts: localhost
  vars:
    registry_private_host: myocp-5f1320191125833da1cac8216c06779e-0000.us-south.containers.appdomain.cloud
    registry_private_port: 32500
    registry_private_ca_file: ~/registry-ca.crt

    registry_username: admin
    registry_password: 8934jk77s862!  # Not a real password, don't worry security folks

    setup_redhat_catalogs: true

  roles:
    - ibm.mas_devops.ocp_contentsourcepolicy
```


## License

EPL-2.0
