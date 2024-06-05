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

### dro_namespace
DRO can be installed on a different namespace, on certain type of OCP clusters where redhat* namespaces have restricted access, User can configure and install DRO on a custom namespace of their choosing by supplying a name using `DRO_NAMESPACE`

- Environment Variable: `DRO_NAMESPACE`
- Default Value: redhat-marketplace

### dro_migration
To migrate from `IBM User Data Services` to `ibm-data-reporter`, set `DRO_MIGRATION` variable to `True`.

- Environment Variable: `DRO_MIGRATION`
- Default Value: False

### ibm_entitlement_key
Provide your [IBM entitlement key](https://myibm.ibm.com/products-services/containerlibrary).

- **Required**
- Environment Variable: `IBM_ENTITLEMENT_KEY`
- Default: None

### dro_storage_class
Required. Storage class where DRO will be installed. MAS ansible playbooks will automatically try to determine a rwo (Read Write Once) storage class from a cluster if DRO_STORAGE_CLASS is not supplied. If a cluster is setup with a customize storage solution, please provide a valid rwo storage class name using DRO_STORAGE_CLASS

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

### dro_endpoint_url
  DRO url from ibm-data-reporter route found in redhat-marketplace namespace, this variable is needed if you wish to connect to an existing DRO instance.

- Optional
- Environment Variable: `DRO_ENDPOINT_URL`
- Default Value: None

### dro_api_key
  DRO api_key is a token obtained from ibm-data-reporter-operator-api-token secret found in redhat-marketplace namespace, this variable is needed if you wish to connect to an existing DRO instance.

- Optional
- Environment Variable: `DRO_APIKEY`
- Default Value: None

### dro_crt_path
  DRO uses default OCP cluster ingress certificates. these can be obtained from either router-certs-default secret found in openshift-ingress namespace or trustedCA config map found in openshift-config namespace, copy the contents of tls.crt into a .pem file and provide the filepath of the .pem file to `DRO_CERTIFICATE_PATH`, this variable is needed if you wish to connect to an existing DRO instance.

- Optional
- Environment Variable: `DRO_CERTIFICATE_PATH`
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

### include_cluster_ingress_cert_chain
Optional. When set to `True`, includes the complete certificates chain in the generated MAS configuration, when a trusted certificate authority is found in your cluster's ingress.

- Optional
- Environment Variable: `INCLUDE_CLUSTER_INGRESS_CERT_CHAIN`
- Default: `False`

Example Playbook
-------------------------------------------------------------------------------

### Install in-cluster and generate MAS configuration

To install DRO
```
export IBM_ENTITLEMENT_KEY=<valid ibm entitlement key>
export DRO_CONTACT_EMAIL=xxx@xxx.com
export DRO_CONTACT_FIRSTNAME=xxx
export DRO_CONTACT_LASTNAME=xxx
export DRO_ACTION=install-dro
export MAS_CONFIG_DIR=<valid local path to the config folder>
export MAS_INSTANCE_ID=<valid mas instance id>
export DRO_STORAGE_CLASS=<valid storage class name>
export ROLE_NAME='dro'
export DRO_NAMESPACE=ibm-dro

ansible-playbook playbooks/run_role.yml
```

To connect to an existing DRO

```
export DRO_ENDPOINT_URL=<valid DRO url>
export DRO_APIKEY=<valid DRO apikey>
export DRO_CERTIFICATE_PATH=/temp/cert.pem
export IBM_ENTITLEMENT_KEY=<valid ibm entitlement key>
export DRO_CONTACT_EMAIL=xxx@xxx.com
export DRO_CONTACT_FIRSTNAME=xxx
export DRO_CONTACT_LASTNAME=xxx
export MAS_CONFIG_DIR=<valid local path to the config folder>
export MAS_INSTANCE_ID=<valid mas instance id>

export DRO_ACTION=install-dro
export ROLE_NAME='dro'
ansible-playbook playbooks/run_role.yml
```

To uninstall DRO
```
export DRO_ACTION=uninstall
export ROLE_NAME='dro'
export DRO_NAMESPACE=ibm-dro

ansible-playbook playbooks/run_role.yml

```

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
