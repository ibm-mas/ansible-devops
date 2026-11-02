# ums
UMS (IBM Usage Metering Service) is supported on the following MAS versions:
- MAS 9.0 +

Installs [IBM Usage Metering Service](https://github.com/ibm/ibm-usage-metering-operator) in the `ibm-usage-metering` namespace (configurable). This role replaces the `dro` role, which installed the Data Reporter Operator. If `mas_instance_id` and associated parameters are provided, the role also generates a `BasCfg` configuration file that can be directly applied to IBM Maximo Application Suite.

When `ums_migrate_from_dro` is enabled (default: `true`), the role automatically detects an existing DRO installation in `dro_namespace` and uninstalls it before proceeding with UMS installation.


## Role Variables - General

### ums_action
Action to perform with the Usage Metering Service deployment.

- Optional
- Environment Variable: `UMS_ACTION`
- Default: `install`

**Valid values**:
- `install` - Deploy and configure UMS (with optional DRO migration)
- `uninstall` - Remove UMS from the cluster
- `skip` - Skip installation but still generate MAS config if `mas_config_dir` is set

**Related variables**: [`ums_namespace`](#ums_namespace)

### ums_namespace
Namespace where the Usage Metering Service operator and operand will be deployed.

- Optional
- Environment Variable: `UMS_NAMESPACE`
- Default: `ibm-usage-metering`

**Purpose**: Namespace for all UMS resources. Unlike DRO, UMS is namespace-scoped and multi-instance capable.

**Valid values**: Any valid Kubernetes namespace name (lowercase alphanumeric and hyphens)

**Related variables**: [`ums_action`](#ums_action)

### ums_migrate_from_dro
Automatically uninstall DRO before installing UMS.

- Optional
- Environment Variable: `UMS_MIGRATE_FROM_DRO`
- Default: `true`

**Purpose**: When `true`, the role checks for an existing DRO `ibm-data-reporter-operator` Subscription in `dro_namespace`. If found, DRO is fully uninstalled before UMS is installed.

**Valid values**: `true` or `false`

**Related variables**: [`dro_namespace`](#dro_namespace)

### dro_namespace
Namespace to search for an existing DRO installation when migrating.

- Optional
- Environment Variable: `DRO_NAMESPACE`
- Default: `redhat-marketplace`

**Purpose**: Used only when `ums_migrate_from_dro: true`. Specifies where to look for the DRO subscription.

**Related variables**: [`ums_migrate_from_dro`](#ums_migrate_from_dro)

### ums_catalog_image
OLM CatalogSource image for the IBM Usage Metering Service operator.

- Optional
- Environment Variable: `UMS_CATALOG_IMAGE`
- Default: `icr.io/cpopen/ibm-usage-metering-operator-catalog:latest`

**Purpose**: Specifies the catalog image used to create the CatalogSource for UMS OLM installation.

**Notes**: Pin to a specific version (e.g. `:1.0.4`) in production environments.

### ibm_entitlement_key
IBM entitlement key for accessing container images.

- **Required**
- Environment Variable: `IBM_ENTITLEMENT_KEY`
- Default: None

**Purpose**: Used to create an `ibm-entitlement-key` pull secret in `ums_namespace` for pulling UMS images from `icr.io`.

**Notes**: Obtain from [IBM Container Library](https://myibm.ibm.com/products-services/containerlibrary).


## Role Variables - Software Central Integration

### ums_software_central_enable
Enable automatic upload of usage data to IBM Software Central.

- Optional
- Environment Variable: `UMS_SOFTWARE_CENTRAL_ENABLE`
- Default: `false`

**Purpose**: When enabled, the IBMUsageMetering CR will be configured with Software Central sender integration using the `ibm-entitlement-key` secret.

**Related variables**: [`ums_software_central_anonymize`](#ums_software_central_anonymize), [`ums_software_central_frequency`](#ums_software_central_frequency)

### ums_software_central_anonymize
Anonymize payloads sent to Software Central.

- Optional
- Environment Variable: `UMS_SOFTWARE_CENTRAL_ANONYMIZE`
- Default: `false`

**Notes**: Set to `false` unless directed by the UMS team.

### ums_software_central_frequency
Upload frequency in UNIX cron format.

- Optional
- Environment Variable: `UMS_SOFTWARE_CENTRAL_FREQUENCY`
- Default: `5 0 * * *` (daily at 12:05 AM UTC)


## Role Variables - BASCfg Generation

### mas_instance_id
MAS instance identifier for BasCfg generation.

- Optional
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

**Purpose**: If set (along with `mas_config_dir`), the role generates a `BasCfg` resource file pointing to the UMS instance.

**Related variables**: [`mas_config_dir`](#mas_config_dir)

### mas_config_dir
Local directory for saving generated BasCfg resource definitions.

- Optional
- Environment Variable: `MAS_CONFIG_DIR`
- Default: None

**Related variables**: [`mas_instance_id`](#mas_instance_id)

### ums_endpoint_url
URL of an existing UMS instance to connect to (skips in-cluster route lookup).

- Optional
- Environment Variable: `UMS_ENDPOINT_URL`
- Default: None (auto-detected from route)

### ums_api_token
API token for an existing UMS instance (skips in-cluster token secret lookup).

- Optional
- Environment Variable: `UMS_API_TOKEN`
- Default: None (auto-detected from `ibm-usage-metering-upload-token` secret)

### ums_contact.email / ums_contact.first_name / ums_contact.last_name
Contact details for the generated BasCfg.

- **Required** when generating BasCfg
- Environment Variables: `UMS_CONTACT_EMAIL`, `UMS_CONTACT_FIRSTNAME`, `UMS_CONTACT_LASTNAME`
- Default: None

### ums_include_isrg_root_cert
Include the ISRG Root X1 (Let's Encrypt) certificate in the generated BasCfg.

- Optional
- Environment Variable: `UMS_INCLUDE_ISRG_ROOT_CERT`
- Default: `true`

**Notes**: Required for IBM Cloud hosted clusters using Let's Encrypt ingress certificates.

### custom_labels
Custom labels to apply to UMS instance resources.

- Optional
- Environment Variable: `CUSTOM_LABELS`
- Default: None

**Valid values**: Comma-separated key=value pairs (e.g. `env=prod,team=platform`)

### mas_pod_templates_dir
Directory containing pod template configurations.

- Optional
- Environment Variable: `MAS_POD_TEMPLATES_DIR`
- Default: None

**Notes**: The configuration file must be named `ibm-mas-umscfg.yml`.


## Example Playbook

### Install UMS (migrating from DRO) and generate MAS configuration

```bash
export IBM_ENTITLEMENT_KEY=<valid ibm entitlement key>
export UMS_CONTACT_EMAIL=xxx@xxx.com
export UMS_CONTACT_FIRSTNAME=xxx
export UMS_CONTACT_LASTNAME=xxx
export UMS_ACTION=install
export MAS_CONFIG_DIR=<valid local path to the config folder>
export MAS_INSTANCE_ID=<valid mas instance id>
export UMS_NAMESPACE=ibm-usage-metering
export UMS_MIGRATE_FROM_DRO=true
export DRO_NAMESPACE=redhat-marketplace
export ROLE_NAME='ums'

ansible-playbook playbooks/run_role.yml
```

### Install UMS without DRO migration

```bash
export IBM_ENTITLEMENT_KEY=<valid ibm entitlement key>
export UMS_CONTACT_EMAIL=xxx@xxx.com
export UMS_CONTACT_FIRSTNAME=xxx
export UMS_CONTACT_LASTNAME=xxx
export UMS_MIGRATE_FROM_DRO=false
export UMS_ACTION=install
export ROLE_NAME='ums'
ansible-playbook playbooks/run_role.yml
```

### Connect to an existing UMS instance

```bash
export UMS_ENDPOINT_URL=<valid UMS url>
export UMS_API_TOKEN=<valid UMS api token>
export UMS_CONTACT_EMAIL=xxx@xxx.com
export UMS_CONTACT_FIRSTNAME=xxx
export UMS_CONTACT_LASTNAME=xxx
export MAS_CONFIG_DIR=<valid local path to the config folder>
export MAS_INSTANCE_ID=<valid mas instance id>
export UMS_ACTION=skip
export ROLE_NAME='ums'
ansible-playbook playbooks/run_role.yml
```

### Uninstall UMS

```bash
export UMS_ACTION=uninstall
export UMS_NAMESPACE=ibm-usage-metering
export ROLE_NAME='ums'
ansible-playbook playbooks/run_role.yml
```

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_config_dir: ~/masconfig

    ums_contact:
      email: 'john@email.com'
      first_name: 'john'
      last_name: 'winter'
  roles:
  - ibm.mas_devops.ums
```

## Migration from DRO

This role is the successor to the `dro` role. The migration path is:

1. Set `ums_migrate_from_dro: true` (default) and `dro_namespace` to where DRO is installed.
2. Run the `ums` role with `ums_action: install`.
3. The role will detect the DRO subscription, uninstall DRO completely, then install UMS.
4. If `mas_config_dir` is set, a new `BasCfg` pointing at the UMS endpoint will be generated and written to `{{ mas_config_dir }}/ums.yml`.
5. Apply the generated config to MAS: `oc apply -f {{ mas_config_dir }}/ums.yml`.

## License
EPL-2.0
