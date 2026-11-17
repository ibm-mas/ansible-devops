# ocp_idms

Installs an **ImageDigestMirrorSet** (IDMS) for IBM Maximo Application Suite's Maximo Operator Catalog.
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

## Hosted Control Planes

When working with hosted control planes such as **ROSA with HCP**, management of the IDMS requires a specialized process because access to critical resources is restricted via standard Kubernetes resources. This collection has specific support for ROSA with HCP.

Before running this role, use the `ocp_config` role to:

- Add the image registry to allowed registries on the cluster
- Add the image registry's CA as an additional trusted CA

Running this role will then:

- Add each IDMS individually using the `rosa` cli commands

!!! important
    Note that on ROSA with HCP there is no way to access `MachinePoolConfigs` to figure out the state of the nodes (e.g. whether it is `updating`). Therefore, we cannot reliably determine when (or if) the changes have been successfully applied.  This is a limitation of the ROSA with HCP implementation; we recommend to wait up to an hour after running this role for the changes to be applied across all workers on a large cluster and contact ROSA support if the IDMS does not apply successfully.

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`cluster_type`](#cluster_type) | Conditional | None |
| [`product_family`](#product_family) | No | `mas` |
| [`setup_redhat_release`](#setup_redhat_release) | No | `false` |
| [`setup_redhat_catalogs`](#setup_redhat_catalogs) | No | `false` |
| [`registry_private_host`](#registry_private_host) | Yes | None |
| [`registry_private_port`](#registry_private_port) | No | None |
| [`registry_private_ca_file`](#registry_private_ca_file) | Yes | None |
| [`registry_username`](#registry_username) | Yes | None |
| [`registry_password`](#registry_password) | Yes | None |
| [`registry_prefix`](#registry_prefix) | No | None |
| [`registry_prefix_redhat`](#registry_prefix_redhat) | Conditional | None |
| [`redhat_catalogs_prefix`](#redhat_catalogs_prefix) | No | None |
| [`machine_config_multiupdate`](#machine_config_multiupdate) | No | `false` |
| [`cluster_name`](#cluster_name) | Conditional | None |
| [`ocp_idms_working_dir`](#ocp_idms_working_dir) | No | `/tmp` |
| [`rosa_token`](#rosa_token) | Conditional | None |

The ROSA HCP variables (`cluster_type`, `cluster_name`, `rosa_token`) are only required when working with a ROSA with HCP cluster, and `registry_prefix_redhat` is required when `setup_redhat_release` or `setup_redhat_catalogs` is `true`.

### Mirror Configuration

#### cluster_type

Cluster type for the ImageDigestMirrorSet configuration — `rosa-hcp` for a ROSA with HCP cluster (currently the only supported value).

- **Optional** — only used when working with a ROSA with HCP cluster
- Environment Variable: `CLUSTER_TYPE`
- Default: None

To set up the IDMS for ROSA HCP you first need to run the `ocp_config` role to configure allowed registries, and `cluster_name` must identify the target cluster.

#### product_family

Product family whose image source registries are configured — `mas` or `aiservice`.

- **Optional**
- Environment Variable: `PRODUCT_FAMILY`
- Default: `mas`

`mas` creates an IDMS for the MAS-related registries (icr.io, cp.icr.io, quay.io); `aiservice` creates an ImageTagMirrorSet for the OpenDataHub registries. The two product families use different image source registries, so the IDMS/ITMS configuration varies accordingly.

#### setup_redhat_release

Enables an ImageDigestMirrorSet for mirrored Red Hat OpenShift platform release content — `true` or `false`.

- **Optional**
- Environment Variable: `SETUP_REDHAT_RELEASE`
- Default: `false`

When `true`, creates an IDMS named `ibm-mas-redhat-release` for platform images. Only enable if you have mirrored OpenShift platform images with the `mirror_ocp` role (`mirror_redhat_platform=true`) — typically for air-gapped OpenShift installations or upgrades. Requires `registry_prefix_redhat` to be set.

#### setup_redhat_catalogs

Enables CatalogSources and an ImageDigestMirrorSet for mirrored Red Hat operator catalogs — `true` or `false`.

- **Optional**
- Environment Variable: `SETUP_REDHAT_CATALOGS`
- Default: `false`

When `true`, creates CatalogSources for certified-operator-index, community-operator-index, and redhat-operator-index, plus an IDMS named `ibm-mas-redhat-catalogs` for operator images. Required for air-gapped deployments using Red Hat operators; only enable if you mirrored operator catalogs with the `mirror_ocp` role (`mirror_redhat_operators=true`). Requires `registry_prefix_redhat` to be set.

### Target Registry

#### registry_private_host

Private hostname of the mirror registry accessible from within the OpenShift cluster — for example `registry.internal.example.com` or `10.0.0.100`.

- **Required**
- Environment Variable: `REGISTRY_PRIVATE_HOST`
- Default: None

Cluster nodes pull images from this registry via the IDMS, so an incorrect hostname causes image pull failures. It must be the hostname accessible from within the cluster, not necessarily the public hostname — in disconnected environments this is typically an internal registry.

#### registry_private_port

Private port of the mirror registry — for example `443`, `5000`, or `32500`.

- **Optional**
- Environment Variable: `REGISTRY_PRIVATE_PORT`
- Default: None

Set only if the registry uses a non-standard port; when unset, the registry URL omits the port (standard HTTPS port 443 is assumed). An incorrect port causes image pull failures.

#### registry_private_ca_file

Path to the mirror registry's CA certificate file — for example `~/registry-ca.crt` or `/tmp/registry-ca.pem`.

- **Required**
- Environment Variable: `REGISTRY_PRIVATE_CA_FILE`
- Default: None

Must be the CA certificate that signed the registry's TLS certificate — required even if the registry uses self-signed certificates. The CA is added to all cluster nodes via MachineConfig, which causes the nodes to reboot, so ensure the certificate is valid and matches the registry's TLS certificate.

#### registry_username

Username for authenticating to the mirror registry.

- **Required**
- Environment Variable: `REGISTRY_USERNAME`
- Default: None

The credentials are added to the cluster's global pull secret and must have pull permissions from the mirror registry. Keep credentials secure.

#### registry_password

Password for authenticating to the mirror registry, paired with `registry_username`.

- **Required**
- Environment Variable: `REGISTRY_PASSWORD`
- Default: None

The credentials are added to the cluster's global pull secret. Keep the password secure and never commit it to version control.

#### registry_prefix

Optional path prefix for IBM content in the mirror registry — for example `mas-241107` or `mas-241205`.

- **Optional**
- Environment Variable: `REGISTRY_PREFIX`
- Default: None

The IDMS redirects image pulls to `{host}:{port}/{prefix}/{reponame}`, so this must match the prefix used when mirroring the images. A catalog datestamp prefix is recommended to help organize multiple mirror versions in the same registry. Red Hat content uses the separate `registry_prefix_redhat`.

#### registry_prefix_redhat

Optional path prefix for Red Hat release and operator catalog content in the mirror registry — for example `ocp-412`, `ocp-414`, or `ocp-419`.

- **Required** when `setup_redhat_release` or `setup_redhat_catalogs` is `true`
- Environment Variable: `REGISTRY_PREFIX_REDHAT`
- Default: None

The IDMS redirects Red Hat image pulls to `{host}:{port}/{prefix}/{reponame}`, so this must match the prefix used when mirroring the Red Hat content with the `mirror_ocp` role. OpenShift release prefixes help organize multiple OCP versions in the same registry.

#### redhat_catalogs_prefix

Optional prefix for the Red Hat CatalogSource names — for example `ibm-mas`, `mas`, or `custom`.

- **Optional**
- Environment Variable: `REDHAT_CATALOGS_PREFIX`
- Default: None

Only applies when `setup_redhat_catalogs` is `true`. When set to `ibm-mas` it creates `ibm-mas-certified-operator-index`, `ibm-mas-community-operator-index`, and `ibm-mas-redhat-operator-index`; when unset it creates `certified-operator-index`, `community-operator-index`, and `redhat-operator-index`. Use a prefix to distinguish these CatalogSources from others in the cluster or to avoid naming conflicts.

#### machine_config_multiupdate

Enables parallel worker node updates when applying MachineConfig changes (for CA certificate installation) — `true` or `false`.

- **Optional**
- Environment Variable: `MACHINE_CONFIG_MULTIUPDATE`
- Default: `false`

!!! warning
    Only enable during initial cluster setup when nodes are lightly loaded and can be safely drained in parallel. In production, leave as `false` — MachineConfig changes cause node reboots, and updating one node at a time ensures workload availability during node updates.

### ROSA HCP

Ensure you have rosa cli `1.2.61` or greater installed.

#### cluster_name

Cluster name of the ROSA HCP cluster, used to target the cluster via the rosa cli.

- **Required** when `cluster_type` is `rosa-hcp`
- Environment Variable: `CLUSTER_NAME`
- Default: None

#### ocp_idms_working_dir

Temporary working directory where the IDMS yamls are generated so they can be applied individually to the cluster.

- **Optional**
- Environment Variable: `OCP_IDMS_WORKING_DIR`
- Default: `/tmp`

Ensure you have read and write access to the directory. Only used when running this role for a rosa-hcp cluster type.

#### rosa_token

Login token for the rosa cli, authenticating it to the ROSA cluster.

- **Required** when `cluster_type` is `rosa-hcp`
- Environment Variable: `ROSA_TOKEN`
- Default: None

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
    - ibm.mas_devops.ocp_idms
```

## License

EPL-2.0
