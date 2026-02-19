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
Action to perform with the Data Reporter Operator deployment.

- Optional
- Environment Variable: `DRO_ACTION`
- Default: `install`

**Purpose**: Controls whether to install or uninstall the Data Reporter Operator.

**When to use**: Set to `uninstall` when removing DRO from the cluster. Use default `install` for normal deployment.

**Valid values**:
- `install` - Deploy and configure DRO
- `uninstall` - Remove DRO from the cluster

**Impact**: The `uninstall` action removes all DRO resources from the specified namespace.

**Related variables**: [`dro_namespace`](#dro_namespace)

**Notes**: DRO is supported on MAS 8.10.6+, 8.11.2+, and 9.0+.

### dro_namespace
Namespace where the Data Reporter Operator will be deployed.

- Optional
- Environment Variable: `DRO_NAMESPACE`
- Default: `redhat-marketplace`

**Purpose**: Allows DRO installation in a custom namespace when the default `redhat-marketplace` namespace has restricted access.

**When to use**: Override the default on OCP clusters where `redhat*` namespaces have restricted access or when organizational policies require custom namespace naming.

**Valid values**: Any valid Kubernetes namespace name (lowercase alphanumeric and hyphens)

**Impact**: All DRO resources will be created in this namespace. The namespace must be specified during uninstall operations.

**Related variables**: [`dro_action`](#dro_action)

**Notes**: Ensure the namespace has appropriate permissions for DRO operator deployment.

### ibm_entitlement_key
IBM entitlement key for accessing container images.

- **Required**
- Environment Variable: `IBM_ENTITLEMENT_KEY`
- Default: None

**Purpose**: Authenticates access to IBM container registry for pulling DRO operator images.

**When to use**: Required for all DRO installations. Obtain from [IBM Container Library](https://myibm.ibm.com/products-services/containerlibrary).

**Valid values**: Valid IBM entitlement key string from your IBM account.

**Impact**: Without a valid key, the DRO operator images cannot be pulled and installation will fail.

**Related variables**: None

**Notes**:
- Keep the entitlement key secure and do not commit it to version control
- The key is associated with your IBM ID and product entitlements
- Verify key validity before deployment to avoid installation failures

### dro_storage_class
Storage class for DRO persistent volumes.

- Optional (auto-detected if not provided)
- Environment Variable: `DRO_STORAGE_CLASS`
- Default: None (automatically determined)

**Purpose**: Provides persistent storage for DRO data and metrics.

**When to use**: Specify explicitly when using customized storage solutions or when automatic detection fails. The playbooks will attempt to auto-detect a suitable RWO storage class if not provided.

**Valid values**: Any storage class name available in your cluster that supports ReadWriteOnce (RWO) access mode. Common examples:
- IBM Cloud ROKS: `ibmc-block-gold`, `ibmc-block-silver`
- AWS: `gp2`, `gp3`
- Azure: `managed-premium`
- On-premises: Depends on your storage provider

**Impact**: Determines where DRO stores its operational data. Must support RWO access mode.

**Related variables**: None

**Notes**:
- Verify the storage class exists: `oc get storageclass`
- The storage class must support RWO (Read Write Once) access mode
- Auto-detection works for most standard cluster configurations

Role Variables - BASCfg Generation
-------------------------------------------------------------------------------
### mas_instance_id
MAS instance identifier for BasCfg generation.

- Optional
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

**Purpose**: Identifies which MAS instance the DRO BasCfg configuration will target.

**When to use**: Required when generating MAS configuration files. If not set (along with `mas_config_dir`), no BasCfg template will be generated.

**Valid values**: Valid MAS instance ID (lowercase alphanumeric, max 12 characters)

**Impact**: Determines the target MAS instance for the generated DRO configuration.

**Related variables**: [`mas_config_dir`](#mas_config_dir), [`dro_contact.email`](#dro_contactemail), [`dro_contact.first_name`](#dro_contactfirst_name), [`dro_contact.last_name`](#dro_contactlast_name)

**Notes**: Both `mas_instance_id` and `mas_config_dir` must be set to generate BasCfg templates.

### mas_config_dir
Local directory for saving generated BasCfg resource definitions.

- Optional
- Environment Variable: `MAS_CONFIG_DIR`
- Default: None

**Purpose**: Specifies where to save the generated DRO BasCfg configuration file for MAS.

**When to use**: Required when generating MAS configuration files. The generated file can be manually applied or used as input to the [`suite_config`](suite_config.md) role.

**Valid values**: Any valid local filesystem path with write permissions

**Impact**: If not set (along with `mas_instance_id`), no BasCfg template will be generated.

**Related variables**: [`mas_instance_id`](#mas_instance_id)

**Notes**: Ensure the directory exists and has appropriate write permissions.

### dro_endpoint_url
URL of an existing DRO instance to connect to.

- Optional
- Environment Variable: `DRO_ENDPOINT_URL`
- Default: None

**Purpose**: Enables connection to an existing DRO deployment instead of installing a new one.

**When to use**: When you want to configure MAS to use an already-deployed DRO instance. Obtain from the `ibm-data-reporter` route in the DRO namespace.

**Valid values**: Valid HTTPS URL to the DRO endpoint (e.g., `https://ibm-data-reporter.apps.cluster.domain.com`)

**Impact**: When set, the role will not install DRO but will generate configuration to connect to the existing instance.

**Related variables**: [`dro_api_key`](#dro_api_key), [`dro_crt_path`](#dro_crt_path)

**Notes**: All three variables (`dro_endpoint_url`, `dro_api_key`, `dro_crt_path`) must be provided to connect to an existing DRO instance.

### dro_api_key
API token for authenticating to an existing DRO instance.

- Optional
- Environment Variable: `DRO_APIKEY`
- Default: None

**Purpose**: Provides authentication credentials for connecting to an existing DRO deployment.

**When to use**: Required when connecting to an existing DRO instance. Obtain from the `ibm-data-reporter-operator-api-token` secret in the DRO namespace.

**Valid values**: Valid DRO API token string

**Impact**: Without a valid API key, MAS cannot authenticate to the existing DRO instance.

**Related variables**: [`dro_endpoint_url`](#dro_endpoint_url), [`dro_crt_path`](#dro_crt_path)

**Notes**:
- Extract from secret: `oc get secret ibm-data-reporter-operator-api-token -n <dro-namespace> -o jsonpath='{.data.token}' | base64 -d`
- Keep the API key secure

### dro_crt_path
Path to DRO certificate file for TLS verification.

- Optional
- Environment Variable: `DRO_CERTIFICATE_PATH`
- Default: None

**Purpose**: Provides the certificate for secure TLS communication with an existing DRO instance.

**When to use**: Required when connecting to an existing DRO instance. DRO uses default OCP cluster ingress certificates.

**Valid values**: Valid filesystem path to a .pem certificate file

**Impact**: Without the certificate, TLS verification will fail when connecting to the existing DRO instance.

**Related variables**: [`dro_endpoint_url`](#dro_endpoint_url), [`dro_api_key`](#dro_api_key)

**Notes**:
- Obtain certificate from `router-certs-default` secret in `openshift-ingress` namespace or `trustedCA` configmap in `openshift-config` namespace
- Extract and save tls.crt contents to a .pem file
- Example: `oc get secret router-certs-default -n openshift-ingress -o jsonpath='{.data.tls\.crt}' | base64 -d > /tmp/dro-cert.pem`

### dro_contact.email
Contact email address for DRO configuration.

- **Required** when generating BasCfg (when `mas_instance_id` and `mas_config_dir` are set)
- Environment Variable: `DRO_CONTACT_EMAIL`
- Default: None

**Purpose**: Provides contact information for the DRO deployment in MAS configuration.

**When to use**: Required for BasCfg generation. Used for administrative and support purposes.

**Valid values**: Valid email address format

**Impact**: This email will be associated with the DRO configuration in MAS.

**Related variables**: [`dro_contact.first_name`](#dro_contactfirst_name), [`dro_contact.last_name`](#dro_contactlast_name), [`mas_instance_id`](#mas_instance_id), [`mas_config_dir`](#mas_config_dir)

**Notes**: Use a monitored email address for receiving DRO-related notifications.

### dro_contact.first_name
Contact first name for DRO configuration.

- **Required** when generating BasCfg (when `mas_instance_id` and `mas_config_dir` are set)
- Environment Variable: `DRO_CONTACT_FIRSTNAME`
- Default: None

**Purpose**: Provides contact information for the DRO deployment in MAS configuration.

**When to use**: Required for BasCfg generation along with email and last name.

**Valid values**: Any string representing a first name

**Impact**: This name will be associated with the DRO configuration in MAS.

**Related variables**: [`dro_contact.email`](#dro_contactemail), [`dro_contact.last_name`](#dro_contactlast_name)

**Notes**: Used for administrative identification purposes.

### dro_contact.last_name
Contact last name for DRO configuration.

- **Required** when generating BasCfg (when `mas_instance_id` and `mas_config_dir` are set)
- Environment Variable: `DRO_CONTACT_LASTNAME`
- Default: None

**Purpose**: Provides contact information for the DRO deployment in MAS configuration.

**When to use**: Required for BasCfg generation along with email and first name.

**Valid values**: Any string representing a last name

**Impact**: This name will be associated with the DRO configuration in MAS.

**Related variables**: [`dro_contact.email`](#dro_contactemail), [`dro_contact.first_name`](#dro_contactfirst_name)

**Notes**: Used for administrative identification purposes.

### custom_labels
Custom labels to apply to DRO instance resources.

- Optional
- Environment Variable: `CUSTOM_LABELS`
- Default: None

**Purpose**: Enables tagging of DRO resources with custom metadata for organization, tracking, or automation purposes.

**When to use**: When you need to apply organizational labels for cost tracking, environment identification, or resource management.

**Valid values**: Comma-separated list of key=value pairs (e.g., `env=prod,team=platform,cost-center=12345`)

**Impact**: Labels are applied to instance-specific DRO resources for identification and filtering.

**Related variables**: None

**Notes**:
- Labels must follow Kubernetes label syntax (alphanumeric, hyphens, underscores, dots)
- Useful for cost allocation, resource queries, and automation scripts

### mas_pod_templates_dir
Directory containing pod template configurations for DRO.

- Optional
- Environment Variable: `MAS_POD_TEMPLATES_DIR`
- Default: None

**Purpose**: Allows customization of DRO pod specifications through template files.

**When to use**: When you need to customize resource limits, node selectors, tolerations, or other pod-level configurations for DRO.

**Valid values**: Valid filesystem path to a directory containing `ibm-mas-bascfg.yml`

**Impact**: The pod template configuration will be inserted into the BasCfg spec under the `podTemplates` element, customizing DRO workload behavior.

**Related variables**: None

**Notes**:
- The configuration file must be named `ibm-mas-bascfg.yml`
- Content should be a YAML block for the `podTemplates` element
- See [BestEfforts reference configuration](https://github.com/ibm-mas/cli/blob/master/image/cli/mascli/templates/pod-templates/best-effort/ibm-mas-bascfg.yml) for examples
- Full documentation: [Customizing Pod Templates](https://www.ibm.com/docs/en/mas-cd/continuous-delivery?topic=configuring-customizing-workloads)

### include_cluster_ingress_cert_chain
Include complete certificate chain in MAS configuration.

- Optional
- Environment Variable: `INCLUDE_CLUSTER_INGRESS_CERT_CHAIN`
- Default: `False`

**Purpose**: Controls whether to include the full certificate chain from the cluster ingress in the generated MAS configuration.

**When to use**: Set to `True` when your cluster uses a trusted certificate authority and you need the complete certificate chain for proper TLS validation.

**Valid values**: `True` or `False`

**Impact**: When enabled, the complete certificate chain is included in the BasCfg, ensuring proper TLS trust validation for DRO connections.

**Related variables**: [`dro_crt_path`](#dro_crt_path)

**Notes**: Only applicable when a trusted CA is found in your cluster's ingress configuration.

Example Playbook
-------------------------------------------------------------------------------

### Install in-cluster and generate MAS configuration

To install DRO
```
export IBM_ENTITLEMENT_KEY=<valid ibm entitlement key>
export DRO_CONTACT_EMAIL=xxx@xxx.com
export DRO_CONTACT_FIRSTNAME=xxx
export DRO_CONTACT_LASTNAME=xxx
export DRO_ACTION=install
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

export DRO_ACTION=install
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
