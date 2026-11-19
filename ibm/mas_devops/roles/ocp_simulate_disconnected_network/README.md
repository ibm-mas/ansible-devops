# ocp_simulate_disconnected_network

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

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`airgap_network_exclusions`](#airgap_network_exclusions) | No | 9 default registries (see below) |
| [`registry_private_ca_file`](#registry_private_ca_file) | Conditional | None |
| [`registry_private_ca_crt`](#registry_private_ca_crt) | No | None |
| [`machine_config_multiupdate`](#machine_config_multiupdate) | No | `false` |

`registry_private_ca_file` is only required when the private/mirrored registry uses self-signed or custom CA certificates.

### Network Isolation

#### airgap_network_exclusions
Space-separated list of container registry hostnames whose DNS resolution will be blocked to simulate disconnected network access. The default list covers the common registries used by MAS and OpenShift; customize it to add or remove registries based on your testing requirements.

- **Optional**
- Environment Variable: None (hardcoded in defaults)
- Default: `quay.io registry.redhat.io registry.connect.redhat.com gcr.io nvcr.io icr.io cp.icr.io docker-na-public.artifactory.swg-devops.com docker-na-proxy-svl.artifactory.swg-devops.com docker-na-proxy-rtp.artifactory.swg-devops.com`

The default registries are `quay.io` (Red Hat Quay registry), `registry.redhat.io` (Red Hat Container Catalog), `registry.connect.redhat.com` (Red Hat Partner registry), `gcr.io` (Google Container Registry), `nvcr.io` (NVIDIA Container Registry), `icr.io` (IBM Cloud Container Registry, public), `cp.icr.io` (IBM Cloud Container Registry, entitled), and `docker-na-public.artifactory.swg-devops.com`, `docker-na-proxy-svl.artifactory.swg-devops.com`, `docker-na-proxy-rtp.artifactory.swg-devops.com` (IBM internal Artifactory and proxies). DNS resolution is blocked by adding bogus IP addresses to `/etc/hosts`; the internal OpenShift image registry is not affected, and image pulls from the listed registries will fail unless mirrored registries are configured before blocking them.

### Private Registry Trust

#### registry_private_ca_file
Local file path to the private/mirrored registry CA certificate — an absolute or relative path to a valid PEM-encoded CA certificate file (e.g. `/tmp/registry-ca.pem`, `./certs/mirror-registry-ca.crt`).

- **Required** when using a private registry with self-signed or custom CA certificates
- Environment Variable: `REGISTRY_PRIVATE_CA_FILE`
- Default: None

The file must be accessible from the Ansible controller. The certificate is added to the cluster's trusted certificate bundle, enabling nodes to trust the private registry; it is not needed if the registry uses publicly trusted certificates.

#### registry_private_ca_crt
Content of the private registry CA certificate, automatically loaded from `registry_private_ca_file` and used internally by the role — do not set it manually.

- **Optional** (derived from `registry_private_ca_file`)
- Environment Variable: None (loaded from file)
- Default: None

The PEM-encoded certificate content is embedded in a MachineConfig and distributed to all cluster nodes to configure node trust.

### MachineConfig Updates

#### machine_config_multiupdate
Whether multiple MachineConfig changes are applied together in a single operation or separately — `true` (apply together) or `false` (apply separately, the default).

- **Optional**
- Environment Variable: `MACHINE_CONFIG_MULTIUPDATE`
- Default: `false`

MachineConfig changes trigger node reboots, which are required to apply host file changes. `true` reduces the number of node reboots, saving time in development environments, but increases risk if the configuration is incorrect; `false` causes more reboots but is safer for rollback and production-like testing. Monitor progress with `oc get mcp`.

## Example Playbook

```yaml
- hosts: localhost
  vars:
    # Add required variables here
  roles:
    - ibm.mas_devops.ocp_simulate_disconnected_network
```

## License

EPL-2.0
