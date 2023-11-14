dro [Data Reporter Operator]
===============================================================================
DRO will be supported on the following MAS versions
- MAS 8.10.6 +
- MAS 8.11.2 +
- MAS 9.0 +

Installs [Data Reporter Operator](https://github.com/redhat-marketplace/redhat-marketplace-operator/tree/develop/datareporter/v2) in the `redhat-marketplace` namespace.  If `mas_instance_id` and the others associated parameters are provided then the role will also generate a configuration file that can be directly applied to IBM Maximo Application Suite.


Role Variables - Installation
-------------------------------------------------------------------------------
### dro_action
Inform the role whether to perform an install or uninstall of Data Reporter Operator. Supported values are `install-dro` and `uninstall`.

- Optional
- Environment Variable: `DRO_ACTION`
- Default: `install-dro`

!!! note
    The install verb for `dro_action` is chosen to avoid conflict with the existing `uds_action` variable from the `uds` role (`install`) to ease migration from UDS to DRO, this allows the value of `uds_action` and `dro_action` to be set once and provide clarity around which dependency should be installed.

    The `uninstall` action works across both `uds` and `dro` roles.

### ibm_entitlement_key
Provide your [IBM entitlement key](https://myibm.ibm.com/products-services/containerlibrary).

- **Required**
- Environment Variable: `IBM_ENTITLEMENT_KEY`
- Default: None

### dro_version
Provide particular StartingCSV version of DRO. Default value is picked from Stable channel.

- Optional
- Environment Variable: `DRO_VERSION`
- Default Value: None

### dro_storage_class
Default Storage class. Set this variable if there's no storage class with default annotation.

- Optional
- Environment Variable: `DRO_STORAGE_CLASS`
- Default Value: None

Role Variables - BASCfg Generation
-------------------------------------------------------------------------------
### mas_instance_id
The instance ID of Maximo Application Suite that the BasCfg configuration will target.  If this or `mas_config_dir` are not set then the role will not generate a BasCfg template.

- Optional
- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### mas_config_dir
Local directory to save the generated BasCfg resource definition.  This can be used to manually configure a MAS instance to connect to BAS instance, or used as an input to the [suite_config](suite_config.md) role. If this or `mas_instance_id` are not set then the role will not generate a BasCfg template.

- Optional
- Environment Variable: `MAS_CONFIG_DIR`
- Default Value: None

### dro_contact.email
Sets the Contact e-mail address used by the MAS instance's DRO configuration.

- **Required** when `mas_instance_id` and `mas_config_dir` are set
- Environment Variable: `DRO_CONTACT_EMAIL`
- Default Value: None

### dro_contact.first_name
Sets the Contact first name used by the MAS instance's DRO configuration.

- **Required** when `mas_instance_id` and `mas_config_dir` are set
- Environment Variable: `DRO_CONTACT_FIRSTNAME`
- Default Value: None

### dro_contact.last_name
Sets the Contact last name used by the MAS instance's DRO configuration.

- **Required** when `mas_instance_id` and `mas_config_dir` are set
- Environment Variable: `DRO_CONTACT_LASTNAME`
- Default Value: None

### custom_labels
List of comma separated key=value pairs for setting custom labels on instance specific resources.

- Optional
- Environment Variable: `CUSTOM_LABELS`
- Default Value: None

### mas_pod_templates_dir
Provide the directory where supported pod templates configuration files are defined.  This role will look for a configuration file named `ibm-mas-bascfg.yml` in the named directory.  The content of the configuration file should be the yaml block that you wish to be inserted into the BasCfg spec under a top level `podTemplates` element, e.g. `podTemplates: {object}`.

For examples refer to the [BestEfforts reference configuration in the MAS CLI](https://github.com/ibm-mas/cli/blob/master/image/cli/mascli/templates/pod-templates/best-effort/ibm-mas-bascfg.yml), for full documentation of the supported options refer to the [Customizing Pod Templates](https://www.ibm.com/docs/en/mas-cd/continuous-delivery?topic=configuring-customizing-workloads) in the product documentation.

- Optional
- Environment Variable: `MAS_POD_TEMPLATES_DIR`
- Default: None

Example Playbook
-------------------------------------------------------------------------------

### Install in-cluster and generate MAS configuration
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_config_dir: ~/masconfig

    dro_contact:
      email: 'john@email.com'
      first_name: 'john'
      last_name: 'winter'
  roles:
  - ibm.mas_devops.dro
```
License
-------------------------------------------------------------------------------
EPL-2.0
