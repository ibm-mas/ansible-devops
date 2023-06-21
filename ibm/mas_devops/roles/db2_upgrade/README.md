db2_update
=========

This role updates the common services operator and the Db2u operator. Then it updates the version of Db2 in the Db2uCluster instance.  In order to begin the update process, the required variables indicated below.

Role Variables
--------------
### db2_instance_name
Name of the Db2uCluster instance that will be updated to the newer version after the subcription update.

- **Required**
- Environment Variable: `DB2_INSTANCE_NAME`
- Default: None

### db2_version
The package version or Db2u operator engine version. For example s11.5.8.0, s11.5.8.0-cn2, etc.

Note: Db2 version must match the db2 channel and must be included in the catalog source for the upgrade to be successful.

- **Required**
- Environment Variable: `DB2_VERSION`
- Default: None

!!! Tip:
      Use [table 1](https://www.ibm.com/docs/en/db2/11.5?topic=1158-upgrading-updating) to match db2 channels with their engine versions for a smooth db2 upgrade

### common_services_channel:
This is the Common Services subscription channel to upgrade to. This is not required as we have an option to use the default channel from the Catalog Source running in the cluster.

- Optional
- Environment Variable: `COMMON_SERVICES_CHANNEL`
- Default: default common services channel in package manifest

### db2_namespace
Name of the namespace where Db2 will be updated

- Optional
- Environment Variable: `DB2_NAMESPACE`
- Default: `db2u`

### db2_channel
This is the Db2 subcription channel to upgrade to. This is not required as we have an option to use the default channel from the Catalog Source running in the cluster.

- Optional
- Environment Variable: `DB2_CHANNEL`
- Default: default db2u-operator channel in package manifest


Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    # Upgrade db2 to channel v110508.0
    db2_channel: "v110508.0"
    db2_instance_name: "db2w-shared"
    db2_version: "s11.5.8.0"

  roles:
    - ibm.mas_devops.db2_upgrade
```

License
-------

EPL-2.0
