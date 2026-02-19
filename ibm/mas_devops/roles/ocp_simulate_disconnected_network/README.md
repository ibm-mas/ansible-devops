ocp_simulate_disconnected_network
===============================================================================

Simulate an air-gapped/disconnected network environment for testing purposes by modifying DNS resolution on OpenShift cluster nodes. This role adds bogus entries to the `/etc/hosts` file on all nodes (workers and masters) to break DNS resolution for external container registries, forcing the cluster to use mirrored registries.

**Purpose**: Enable testing of disconnected/air-gapped MAS installations without physically isolating the cluster from the network. The cluster can still access other network resources, but cannot reach the specified container registries.

**Important Notes**:
- Primarily designed and tested for Fyre clusters
- May require modifications for other cluster providers
- Uses MachineConfig to modify node host files
- Changes persist across node reboots

**Verification**: Check node hosts file:
```bash
oc debug node/<node-name>
sh-4.4# cat /host/etc/hosts
```


Role Variables
-------------------------------------------------------------------------------

### airgap_network_exclusions
Space-separated list of container registry hostnames to block.

- Optional
- Environment Variable: None (hardcoded in defaults)
- Default: `quay.io registry.redhat.io registry.connect.redhat.com gcr.io nvcr.io icr.io cp.icr.io docker-na-public.artifactory.swg-devops.com docker-na-proxy-svl.artifactory.swg-devops.com docker-na-proxy-rtp.artifactory.swg-devops.com`

**Purpose**: Defines which container registry hostnames will have DNS resolution blocked to simulate disconnected network access.

**When to use**: Default list covers common registries used by MAS and OpenShift. Customize to add or remove registries based on your testing requirements.

**Valid values**: Space-separated list of valid hostnames. Default registries:
- `quay.io` - Red Hat Quay registry
- `registry.redhat.io` - Red Hat Container Catalog
- `registry.connect.redhat.com` - Red Hat Partner registry
- `gcr.io` - Google Container Registry
- `nvcr.io` - NVIDIA Container Registry
- `icr.io` - IBM Cloud Container Registry (public)
- `cp.icr.io` - IBM Cloud Container Registry (entitled)
- `docker-na-public.artifactory.swg-devops.com` - IBM internal Artifactory
- `docker-na-proxy-svl.artifactory.swg-devops.com` - IBM internal Artifactory proxy
- `docker-na-proxy-rtp.artifactory.swg-devops.com` - IBM internal Artifactory proxy

**Impact**: Listed registries will be unreachable from cluster nodes. Image pulls from these registries will fail unless mirrored registries are configured.

**Related variables**: `registry_private_ca_file`, `machine_config_multiupdate`

**Notes**:
- Blocks DNS resolution by adding bogus IP addresses to `/etc/hosts`
- Does not affect internal OpenShift image registry
- Ensure mirrored registries are configured before blocking external registries
- Add custom registries if testing with additional image sources

### registry_private_ca_file
Local file path to the private registry CA certificate.

- Optional
- Environment Variable: `REGISTRY_PRIVATE_CA_FILE`
- Default: None

**Purpose**: Provides the CA certificate for the private/mirrored registry that will be used in the disconnected environment.

**When to use**: Required when using a private registry with self-signed or custom CA certificates in the simulated air-gap environment.

**Valid values**: Absolute or relative file path to a valid PEM-encoded CA certificate file (e.g., `/tmp/registry-ca.pem`, `./certs/mirror-registry-ca.crt`).

**Impact**: The CA certificate is added to the cluster's trusted certificate bundle, enabling nodes to trust the private registry.

**Related variables**: `registry_private_ca_crt`, `airgap_network_exclusions`

**Notes**:
- Required for private registries with custom CAs
- File must be accessible from the Ansible controller
- Certificate must be in PEM format
- Not needed if using a registry with publicly trusted certificates

### registry_private_ca_crt
Content of the private registry CA certificate.

- Optional (derived from `registry_private_ca_file`)
- Environment Variable: None (loaded from file)
- Default: None

**Purpose**: Contains the actual CA certificate content loaded from `registry_private_ca_file`. Used internally by the role.

**When to use**: Automatically populated when `registry_private_ca_file` is set. Do not set manually.

**Valid values**: PEM-encoded CA certificate content.

**Impact**: Certificate content is embedded in MachineConfig and distributed to all cluster nodes.

**Related variables**: `registry_private_ca_file`

**Notes**:
- Automatically loaded from the file specified in `registry_private_ca_file`
- Do not set this variable directly
- Used internally by the role to configure node trust

### machine_config_multiupdate
Enable multiple MachineConfig updates in a single operation.

- Optional
- Environment Variable: `MACHINE_CONFIG_MULTIUPDATE`
- Default: `false`

**Purpose**: Controls whether multiple MachineConfig changes are applied together or separately, affecting node reboot behavior.

**When to use**: Set to `true` when applying multiple configuration changes to minimize node reboots. Set to `false` for safer, incremental updates.

**Valid values**:
- `true` - Apply multiple MachineConfig changes together
- `false` - Apply MachineConfig changes separately (default)

**Impact**:
- `true`: Reduces number of node reboots but increases risk if configuration is incorrect
- `false`: More node reboots but safer rollback if issues occur

**Related variables**: None

**Notes**:
- MachineConfig changes trigger node reboots
- `false` is safer for production-like testing
- `true` can save time in development environments
- Node reboots are required to apply host file changes
- Monitor MachineConfigPool status: `oc get mcp`
