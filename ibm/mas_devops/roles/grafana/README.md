grafana
===============================================================================
Installs and configures an instance of [Grafana](https://grafana.com/) for use with IBM Maximo Application Suite, using the [community grafana operator](https://github.com/grafana-operator/grafana-operator)

!!! note
    The credentials for the grafana admin user are stored in `grafana-admin-credentials` secret in the grafana namespace. A route is created in the grafana namespace to allow access to the grafana UI.


Role Variables
-------------------------------------------------------------------------------
### grafana_action
Inform the role whether to perform an `install`, `uninstall`, or `update` of Grafana.

!!! note
    When using this role to upgrade from Grafana 4 to 5, the Grafana 5 instance will have a new URL and will not inherit the user database from the old v4 installation, the admin password will be new, and user accounts set up in the v4 instance will need to be recreated in the v5 instance.

- Optional
- Environment Variable: `GRAFANA_ACTION`
- Default: `install`

### grafana_major_version
Sets the major version of the grafana operator to install. `4` or `5`

- Optional
- Environment Variable: `GRAFANA_MAJOR_VERSION`
- Default Value: `5`

### grafana_v4_namespace
Sets the namespace to install the grafana operator V4 and grafana instance

- Optional
- Environment Variable: `GRAFANA_NAMESPACE`
- Default Value: `grafana`

### grafana_v5_namespace
Sets the namespace to install the grafana operator V5 and grafana instance

- Optional
- Environment Variable: `GRAFANA_V5_NAMESPACE`
- Default Value: `grafana5`

### grafana_instance_storage_class
Declare the storage class for Grafana Instance user data persistent volume.

- **Required** if one of the known supported storage classes is not installed in the cluster.
- Environment Variable: `GRAFANA_INSTANCE_STORAGE_CLASS`
- Default Value: `ibmc-file-gold-gid`, `ocs-storagecluster-cephfs`, `azurefiles-premium` (if available)

### grafana_instance_storage_size
Adjust the size of the volume used to store Grafana user data.

- Optional
- Environment Variable: `GRAFANA_INSTANCE_STORAGE_SIZE`
- Default Value: `10Gi`


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
