suite_upgrade
=============
This role will upgrade MAS Core and existing MAS Applications to the correspondent 8.7 latest patches version. 
For example, Manage will be upgraded to channel `8.3.x`

MAS 8.6 supported versions for MAS Core and MAS applications:

- MAS Core supported version: `8.6.x`
- MAS Applications target versions:
  - hputilities: `8.2.x`
  - iot: `8.4.x`
  - manage: `8.2.x`
  - monitor: `8.5.x`
  - predict: `8.4.x`
  - safety: `8.2.x`

MAS 8.7 target versions for MAS Core and MAS applications:

- MAS Core target version: `8.7.x`
- MAS Applications target versions:
  - hputilities: `8.3.x`
  - iot: `8.4.x` (no change in versions)
  - manage: `8.3.x`
  - monitor: `8.7.x`
  - predict: `8.5.x`
  - safety: `8.2.x` (no change in versions)

Note: Assist and Visual Inspection applications do not have an upgrade path from MAS 8.6 to 8.7, therefore there's no upgrade support in this role.

For more information, please refer to [Upgrading Maximo Application Suite](https://www.ibm.com/docs/en/mas87/8.7.0?topic=upgrading) documentation.

Role Variables
--------------
### mas_instance_id
Required - Defines the instance id that is used in the existing MAS installation, will be used to lookup the existing MAS JDBC configurations and make updates to the new SSL certificates generated by the CP4D upgrade.

- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### mas_catalog_source
Optional - Defines the catalog to be used to install MAS. You can set it to `ibm-operator-catalog` for release install or `ibm-mas-operators` for development.

- Environment Variable: `MAS_CATALOG_SOURCE`
- Default Value: `ibm-operator-catalog`

Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  roles:
    - ibm.mas_devops.suite_upgrade_check
    - ibm.mas_devops.cert_manager_upgrade
    - ibm.mas_devops.cert_manager_upgrade_check
    - ibm.mas_devops.suite_upgrade
```

If you have cluster issuer, and have setup CIS webhook in your existing instance, you will need also to reinstall CIS webhook in `ibm-common-services` namespace. 
Therefore, you might want to use the following playbook sample to accomplish this.

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    is_suite_upgrade: true # this will tell 'ibm.mas_devops.suite_dns' to reinstall cis webhook under 'ibm-common-services' ns if 'MAS_CUSTOM_CLUSTER_ISSUER' is set
  roles:
    - ibm.mas_devops.suite_upgrade_check
    - ibm.mas_devops.cert_manager_upgrade
    - ibm.mas_devops.suite_dns
    - ibm.mas_devops.cert_manager_upgrade_check
    - ibm.mas_devops.suite_upgrade
```