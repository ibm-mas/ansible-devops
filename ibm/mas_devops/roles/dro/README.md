# dro
DRO will be supported on the following MAS versions

- MAS 8.10.6 +
- MAS 8.11.2 +
- MAS 9.0 +

Installs [Data Reporter Operator](https://github.com/redhat-marketplace/redhat-marketplace-operator/tree/develop/datareporter/v2) in the `redhat-marketplace` namespace. If `mas_instance_id` and the other associated parameters are provided then the role will also generate a configuration file that can be directly applied to IBM Maximo Application Suite.

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`dro_action`](#dro_action) | No | `install` |
| [`dro_namespace`](#dro_namespace) | No | `redhat-marketplace` |
| [`ibm_entitlement_key`](#ibm_entitlement_key) | Yes | None |
| [`dro_storage_class`](#dro_storage_class) | No | Auto-detected |
| [`dro_endpoint_url`](#dro_endpoint_url) | No | None |
| [`dro_api_key`](#dro_api_key) | No | None |
| [`dro_crt_path`](#dro_crt_path) | No | None |
| [`mas_instance_id`](#mas_instance_id) | No | None |
| [`mas_config_dir`](#mas_config_dir) | No | None |
| [`dro_contact.email`](#dro_contactemail) | Conditional | None |
| [`dro_contact.first_name`](#dro_contactfirst_name) | Conditional | None |
| [`dro_contact.last_name`](#dro_contactlast_name) | Conditional | None |
| [`dro_include_isrg_root_cert`](#dro_include_isrg_root_cert) | No | `true` |
| [`custom_labels`](#custom_labels) | No | None |
| [`mas_pod_templates_dir`](#mas_pod_templates_dir) | No | None |

Some variables are conditionally required: generating a BasCfg requires both `mas_instance_id` and `mas_config_dir` (plus the `dro_contact` fields), and connecting to an existing DRO instance requires all three of `dro_endpoint_url`, `dro_api_key`, and `dro_crt_path`.

### Installation

#### dro_action

Action to perform with the Data Reporter Operator deployment — `install` (deploy and configure DRO) or `uninstall` (remove DRO from the cluster). The `uninstall` action removes all DRO resources from the specified namespace.

- **Optional**
- Environment Variable: `DRO_ACTION`
- Default: `install`

DRO is supported on MAS 8.10.6+, 8.11.2+, and 9.0+. The namespace must be specified during uninstall operations (see [`dro_namespace`](#dro_namespace)).

#### dro_namespace

Namespace where the Data Reporter Operator will be deployed — any valid Kubernetes namespace name (lowercase alphanumeric and hyphens).

- **Optional**
- Environment Variable: `DRO_NAMESPACE`
- Default: `redhat-marketplace`

Override the default on OCP clusters where `redhat*` namespaces have restricted access, or when organizational policies require custom namespace naming. Ensure the namespace has appropriate permissions for DRO operator deployment.

#### ibm_entitlement_key

IBM entitlement key for accessing container images — obtain from the [IBM Container Library](https://myibm.ibm.com/products-services/containerlibrary).

- **Required**
- Environment Variable: `IBM_ENTITLEMENT_KEY`
- Default: None

Authenticates access to the IBM container registry for pulling DRO operator images; without a valid key the images cannot be pulled and installation will fail. Keep the key secure and do not commit it to version control.

#### dro_storage_class

Storage class for DRO persistent volumes — any storage class available in your cluster that supports ReadWriteOnce (RWO) access mode, for example `ibmc-block-gold` / `ibmc-block-silver` (IBM Cloud ROKS), `gp2` / `gp3` (AWS), or `managed-premium` (Azure).

- **Optional** (auto-detected if not provided)
- Environment Variable: `DRO_STORAGE_CLASS`
- Default: None (automatically determined)

Provides persistent storage for DRO data and metrics. Specify explicitly when using customized storage solutions or when automatic detection fails; verify available storage classes with `oc get storageclass`.

### Connecting to an Existing DRO Instance

#### dro_endpoint_url

URL of an existing DRO instance to connect to — a valid HTTPS URL such as `https://ibm-data-reporter.apps.cluster.domain.com`, obtained from the `ibm-data-reporter` route in the DRO namespace.

- **Optional**
- Environment Variable: `DRO_ENDPOINT_URL`
- Default: None

When set, the role will not install DRO but will generate configuration to connect to the existing instance. All three of `dro_endpoint_url`, `dro_api_key`, and `dro_crt_path` must be provided to connect to an existing DRO instance.

#### dro_api_key

API token for authenticating to an existing DRO instance, obtained from the `ibm-data-reporter-operator-api-token` secret in the DRO namespace.

- **Optional**
- Environment Variable: `DRO_APIKEY`
- Default: None

Extract the token with `oc get secret ibm-data-reporter-operator-api-token -n <dro-namespace> -o jsonpath='{.data.token}' | base64 -d`. Keep the API key secure.

#### dro_crt_path

Path to the DRO certificate file (.pem) used for TLS verification when connecting to an existing DRO instance. DRO uses the default OCP cluster ingress certificates.

- **Optional**
- Environment Variable: `DRO_CERTIFICATE_PATH`
- Default: None

Obtain the certificate from the `router-certs-default` secret in the `openshift-ingress` namespace or the `trustedCA` configmap in the `openshift-config` namespace, for example `oc get secret router-certs-default -n openshift-ingress -o jsonpath='{.data.tls\.crt}' | base64 -d > /tmp/dro-cert.pem`. Without the certificate, TLS verification will fail.

### BASCfg Generation

#### mas_instance_id

MAS instance identifier (lowercase alphanumeric, max 12 characters) that the generated DRO BasCfg configuration will target.

- **Optional**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

Required when generating MAS configuration files. If not set (along with `mas_config_dir`), no BasCfg template will be generated — both must be set to generate BasCfg templates.

#### mas_config_dir

Local directory (with write permissions) for saving the generated BasCfg resource definitions.

- **Optional**
- Environment Variable: `MAS_CONFIG_DIR`
- Default: None

Required when generating MAS configuration files. The generated file can be manually applied or used as input to the [`suite_config`](suite_config.md) role; if not set (along with `mas_instance_id`), no BasCfg template will be generated.

#### dro_contact.email

Contact email address (valid email format) for the DRO configuration, used for administrative and support purposes.

- **Required** when generating BasCfg (when `mas_instance_id` and `mas_config_dir` are set)
- Environment Variable: `DRO_CONTACT_EMAIL`
- Default: None

Use a monitored email address for receiving DRO-related notifications.

#### dro_contact.first_name

Contact first name for the DRO configuration, used for administrative identification purposes.

- **Required** when generating BasCfg (when `mas_instance_id` and `mas_config_dir` are set)
- Environment Variable: `DRO_CONTACT_FIRSTNAME`
- Default: None

Required for BasCfg generation along with email and last name.

#### dro_contact.last_name

Contact last name for the DRO configuration, used for administrative identification purposes.

- **Required** when generating BasCfg (when `mas_instance_id` and `mas_config_dir` are set)
- Environment Variable: `DRO_CONTACT_LASTNAME`
- Default: None

Required for BasCfg generation along with email and first name.

#### dro_include_isrg_root_cert

Whether to include the ISRG Root X1 (the default root certificate used by Let's Encrypt) in the generated BasCfg — `true` or `false`.

- **Optional**
- Environment Variable: `DRO_INCLUDE_ISRG_ROOT_CERT`
- Default: `true`

Mainly needed for IBM Cloud hosted services, where including the root certificate ensures proper TLS trust validation for DRO connections.

#### custom_labels

Custom labels to apply to DRO instance resources, as a comma-separated list of key=value pairs (e.g., `env=prod,team=platform,cost-center=12345`).

- **Optional**
- Environment Variable: `CUSTOM_LABELS`
- Default: None

Labels must follow Kubernetes label syntax (alphanumeric, hyphens, underscores, dots) and are useful for cost allocation, resource queries, and automation scripts.

#### mas_pod_templates_dir

Directory containing pod template configurations for DRO — must contain a file named `ibm-mas-bascfg.yml` whose content is a YAML block for the `podTemplates` element.

- **Optional**
- Environment Variable: `MAS_POD_TEMPLATES_DIR`
- Default: None

The pod template configuration is inserted into the BasCfg spec under the `podTemplates` element, customizing resource limits, node selectors, tolerations, and other pod-level settings. See the [BestEfforts reference configuration](https://github.com/ibm-mas/cli/blob/master/image/cli/mascli/templates/pod-templates/best-effort/ibm-mas-bascfg.yml) for examples and [Customizing Pod Templates](https://www.ibm.com/docs/en/mas-cd/continuous-delivery?topic=configuring-customizing-workloads) for full documentation.

## Example Playbook

### Install in-cluster and generate MAS configuration

To install DRO

```bash
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

```bash
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

```bash
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

## License

EPL-2.0
