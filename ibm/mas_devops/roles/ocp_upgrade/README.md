# ocp_upgrade

This role supports the upgrade of the Openshift Cluster version for master and worker nodes in IBM Cloud provider.

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`cluster_type`](#cluster_type) | Yes | None |
| [`cluster_name`](#cluster_name) | Yes | None |
| [`ocp_version_upgrade`](#ocp_version_upgrade) | Yes | None |

### Upgrade Target

#### cluster_type

Cluster type for the upgrade operation.

- **Required**
- Environment Variable: `CLUSTER_TYPE`
- Default: None

The only supported value is `roks` (IBM Cloud Red Hat OpenShift Kubernetes Service); the role will fail for any other cluster type — use provider-specific upgrade procedures instead.

#### cluster_name

Name of the cluster to upgrade.

- **Required**
- Environment Variable: `CLUSTER_NAME`
- Default: None

Must exactly match an existing ROKS cluster name in your IBM Cloud account; verify the name before running the upgrade to avoid targeting the wrong cluster.

#### ocp_version_upgrade

Target OpenShift version for the upgrade, in ROKS version format with the `_openshift` suffix (e.g. `4.10_openshift`, `4.11_openshift`, `4.12_openshift`).

- **Required**
- Environment Variable: `OCP_VERSION_UPGRADE`
- Default: None

!!! warning
    The version must be a supported upgrade path from the current version (check IBM Cloud documentation for available versions). Upgrades cannot be rolled back and cause temporary service disruption — plan for a maintenance window.

## Example Playbook

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    cluster_name: my-ocp-cluster
    cluster_type: roks
    ocp_version_upgrade: 4.10_openshift
  roles:
    - ibm.mas_devops.ocp_upgrade
```

## License

EPL-2.0
