grafana
===============================================================================
Installs and configures an instance of [Grafana](https://grafana.com/) for use with IBM Maximo Application Suite, using the [community grafana operator](https://github.com/grafana-operator/grafana-operator)

!!! note
    The credentials for the grafana admin user are stored in `grafana-admin-credentials` secret in the grafana namespace. A route is created in the grafana namespace to allow access to the grafana UI.


Role Variables
-------------------------------------------------------------------------------
### grafana_action
Action to perform on Grafana installation.

- **Optional**
- Environment Variable: `GRAFANA_ACTION`
- Default: `install`

**Purpose**: Specifies whether to install, uninstall, or upgrade Grafana for use with MAS monitoring.

**When to use**:
- Use `install` (default) for new Grafana deployments
- Use `update` to upgrade from Grafana v4 to v5
- Use `uninstall` to remove Grafana

**Valid values**: `install`, `uninstall`, `update`

**Impact**: 
- `install`: Deploys Grafana operator and instance
- `update`: Upgrades from v4 to v5 (creates new instance with new URL)
- `uninstall`: Removes Grafana operator and instance

**Related variables**:
- `grafana_major_version`: Version to install/upgrade to
- `grafana_v4_namespace`/`grafana_v5_namespace`: Namespaces for different versions

**Note**: **IMPORTANT** - When upgrading from v4 to v5, the new instance will have a different URL and will NOT inherit the user database. Admin password will be reset, and user accounts must be recreated. The v4 instance remains until manually removed.

### grafana_major_version
Grafana operator major version.

- **Optional**
- Environment Variable: `GRAFANA_MAJOR_VERSION`
- Default: `5`

**Purpose**: Specifies which major version of the Grafana operator to install.

**When to use**:
- Use default (`5`) for new installations (recommended)
- Set to `4` only for legacy deployments
- Version 5 is the current supported version

**Valid values**: `4`, `5`

**Impact**: Determines which Grafana operator version is deployed. Version 5 uses a different namespace and has breaking changes from version 4.

**Related variables**:
- `grafana_action`: Use `update` to upgrade from v4 to v5
- `grafana_v4_namespace`: Namespace for v4 installation
- `grafana_v5_namespace`: Namespace for v5 installation

**Note**: Version 5 is recommended for all new deployments. Upgrading from v4 to v5 requires using `grafana_action=update` and results in a new instance with different URL and no user database migration.

### grafana_v4_namespace
Namespace for Grafana v4 installation.

- **Optional**
- Environment Variable: `GRAFANA_NAMESPACE`
- Default: `grafana`

**Purpose**: Specifies the Kubernetes namespace where Grafana operator v4 and instance are installed.

**When to use**:
- Only applies when `grafana_major_version=4`
- Use default (`grafana`) for standard deployments
- Override only if namespace conflicts exist

**Valid values**: Valid Kubernetes namespace name

**Impact**: Determines where Grafana v4 resources are created. Namespace must not conflict with v5 installation.

**Related variables**:
- `grafana_major_version`: Must be `4` for this to apply
- `grafana_v5_namespace`: Separate namespace for v5

**Note**: When upgrading from v4 to v5, both namespaces coexist. The v4 instance remains in this namespace until manually removed.

### grafana_v5_namespace
Namespace for Grafana v5 installation.

- **Optional**
- Environment Variable: `GRAFANA_V5_NAMESPACE`
- Default: `grafana5`

**Purpose**: Specifies the Kubernetes namespace where Grafana operator v5 and instance are installed.

**When to use**:
- Applies when `grafana_major_version=5` (default)
- Use default (`grafana5`) for standard deployments
- Override only if namespace conflicts exist

**Valid values**: Valid Kubernetes namespace name

**Impact**: Determines where Grafana v5 resources are created. Uses separate namespace from v4 to allow coexistence during upgrades.

**Related variables**:
- `grafana_major_version`: Must be `5` for this to apply
- `grafana_v4_namespace`: Separate namespace for v4

**Note**: The separate namespace allows v4 and v5 to coexist during upgrades. After upgrading, the v4 instance remains in its namespace until manually removed.

### grafana_instance_storage_class
Storage class for Grafana user data.

- **Required** (if supported storage class not available)
- Environment Variable: `GRAFANA_INSTANCE_STORAGE_CLASS`
- Default: Auto-detected from `ibmc-file-gold-gid`, `ocs-storagecluster-cephfs`, `azurefiles-premium`

**Purpose**: Specifies the storage class for Grafana's persistent volume that stores user data, dashboards, and configurations.

**When to use**:
- Leave unset to auto-detect from supported storage classes
- Set explicitly if none of the default classes are available
- Required if cluster has no supported storage classes

**Valid values**: Any storage class supporting ReadWriteOnce (RWO) access mode. ReadWriteMany (RWX) classes also work.

**Impact**: Determines where Grafana user data is stored. Incorrect or unavailable storage class will cause deployment to fail.

**Related variables**:
- `grafana_instance_storage_size`: Size of the storage volume

**Note**: RWO access mode is sufficient for Grafana. RWX classes (like `ibmc-file-gold-gid`, `ocs-storagecluster-cephfs`, `azurefiles-premium`) also work but are not required. The role auto-detects these common classes if available.

### grafana_instance_storage_size
Storage volume size for Grafana user data.

- **Optional**
- Environment Variable: `GRAFANA_INSTANCE_STORAGE_SIZE`
- Default: `10Gi`

**Purpose**: Specifies the size of the persistent volume used to store Grafana user data, dashboards, and configurations.

**When to use**:
- Use default (`10Gi`) for most deployments
- Increase for environments with many dashboards or extensive data
- Consider growth over time for dashboard storage

**Valid values**: Kubernetes storage size format (e.g., `10Gi`, `20Gi`, `50Gi`)

**Impact**: Determines available storage for Grafana data. Insufficient size may limit dashboard creation. Excessive size wastes storage resources.

**Related variables**:
- `grafana_instance_storage_class`: Storage class for the volume

**Note**: The default 10Gi is sufficient for typical MAS monitoring deployments. When upgrading from v4 to v5, the new instance inherits the v4 storage size unless explicitly overridden.


Example Playbook
-------------------------------------------------------------------------------

```yaml
- hosts: localhost
  vars:
    grafana_instance_storage_class: "ibmc-file-gold-gid"
    grafana_instance_storage_class: "15Gi"
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
    note that the upgraded v5 grafana inherits the storage class and size from the v4 configuration unless they are defined as environment variables.

License
-------------------------------------------------------------------------------

EPL-2.0
