# grafana
Installs and configures an instance of [Grafana](https://grafana.com/) for use with IBM Maximo Application Suite, using the [community grafana operator](https://github.com/grafana-operator/grafana-operator)

!!! note
    The credentials for the grafana admin user are stored in `grafana-admin-credentials` secret in the grafana namespace. A route is created in the grafana namespace to allow access to the grafana UI.

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`grafana_action`](#grafana_action) | No | `install` |
| [`grafana_major_version`](#grafana_major_version) | No | `5` |
| [`grafana_v4_namespace`](#grafana_v4_namespace) | No | `grafana` |
| [`grafana_v5_namespace`](#grafana_v5_namespace) | No | `grafana5` |
| [`grafana_instance_storage_class`](#grafana_instance_storage_class) | Conditional | Auto-detected |
| [`grafana_instance_storage_size`](#grafana_instance_storage_size) | No | `10Gi` |

`grafana_instance_storage_class` is only required when the cluster has none of the supported storage classes that the role auto-detects.

### Installation

#### grafana_action
Action to perform on the Grafana installation — one of `install` (deploy the Grafana operator and instance), `update` (upgrade from Grafana v4 to v5), or `uninstall` (remove the Grafana operator and instance).

- **Optional**
- Environment Variable: `GRAFANA_ACTION`
- Default: `install`

`update` creates a new v5 instance with a new URL; `grafana_major_version` controls the version to install or upgrade to, and `grafana_v4_namespace` / `grafana_v5_namespace` define the namespaces used by each version.

!!! warning
    When upgrading from v4 to v5, the new instance will have a different URL and will **not** inherit the user database. The admin password will be reset, user accounts must be recreated, and the v4 instance remains until manually removed.

#### grafana_major_version
Grafana operator major version to install — `4` (legacy deployments only) or `5` (the current supported version, recommended for all new deployments).

- **Optional**
- Environment Variable: `GRAFANA_MAJOR_VERSION`
- Default: `5`

Version 5 uses a different namespace (`grafana_v5_namespace`) and has breaking changes from version 4. Upgrading from v4 to v5 requires `grafana_action=update` and results in a new instance with a different URL and no user database migration.

#### grafana_v4_namespace
Namespace where the Grafana v4 operator and instance are installed — any valid Kubernetes namespace name. Only applies when `grafana_major_version` is `4`; override the default (`grafana`) only if namespace conflicts exist.

- **Optional**
- Environment Variable: `GRAFANA_NAMESPACE`
- Default: `grafana`

When upgrading from v4 to v5, both namespaces coexist: the v4 instance remains in this namespace until manually removed.

#### grafana_v5_namespace
Namespace where the Grafana v5 operator and instance are installed — any valid Kubernetes namespace name. Applies when `grafana_major_version` is `5` (the default); override the default (`grafana5`) only if namespace conflicts exist.

- **Optional**
- Environment Variable: `GRAFANA_V5_NAMESPACE`
- Default: `grafana5`

The separate namespace from `grafana_v4_namespace` allows v4 and v5 to coexist during upgrades. After upgrading, the v4 instance remains in its namespace until manually removed.

### Storage

#### grafana_instance_storage_class
Storage class for the Grafana persistent volume that stores user data, dashboards, and configurations — any storage class supporting ReadWriteOnce (RWO) access mode; ReadWriteMany (RWX) classes also work.

- **Required** if the cluster has no supported storage class available
- Environment Variable: `GRAFANA_INSTANCE_STORAGE_CLASS`
- Default: Auto-detected (`ibmc-file-gold-gid`, `ocs-storagecluster-cephfs`, or `azurefiles-premium`)

RWO access mode is sufficient for Grafana; the RWX classes listed above also work but are not required, and the role auto-detects these common classes if available. An incorrect or unavailable storage class will cause the deployment to fail.

#### grafana_instance_storage_size
Size of the persistent volume for Grafana user data, dashboards, and configurations — a Kubernetes storage size such as `10Gi`, `20Gi`, or `50Gi`.

- **Optional**
- Environment Variable: `GRAFANA_INSTANCE_STORAGE_SIZE`
- Default: `10Gi`

The default `10Gi` is sufficient for typical MAS monitoring deployments; increase it for environments with many dashboards or extensive data. When upgrading from v4 to v5, the new instance inherits the v4 storage size unless explicitly overridden.

## Example Playbook

```yaml
- hosts: localhost
  vars:
    grafana_instance_storage_class: "ibmc-file-gold-gid"
    grafana_instance_storage_size: "15Gi"
  roles:
    - ibm.mas_devops.grafana
```

To Upgrade from Grafana Operator from V4 to V5

```yaml
- hosts: localhost
  vars:
    grafana_action: "update"
  roles:
    - ibm.mas_devops.grafana
```

!!! note
    The upgraded v5 grafana inherits the storage class and size from the v4 configuration unless they are defined as environment variables.

## License

EPL-2.0
