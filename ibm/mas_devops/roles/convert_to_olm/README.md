convert_to_olm
=============
This role provides capabilities to switch MAS and its Applications from legacy deployment (via mas-install.sh installer/manual deployment) to OLM/Channel subscription install.

Role Variables
--------------

### mas_app_id
The name of the Maximo Application Suite Application. This will be used to lookup for application namespace and resources.

- **Required**
- Environment Variable: `MAS_APP_ID`
- One of [`assist`, `core`, `health`, `hputilities`, `iot`, `manage`, `monitor`, `optimizer`, `predict`, `visualinspection`]
- Default: None

### mas_instance_id
The instance ID of Maximo Application Suite. This will be used to lookup for application namespace and resources.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

### mas_catalog_source 
Defines the catalog to be used to install MAS channel subscription.

- Optional
- Environment Variable: `MAS_CATALOG_SOURCE`
- Default: `ibm-operator-catalog`

### artifactory_username
Provide your artifactory username, primarily used to update the image pull secret in development.

- **Required** when using this role for development versions of MAS
- Environment Variable: `ARTIFACTORY_USERNAME`
- Default: None

### artifactory_apikey
Provide your artifactory api key, primarily used to update the image pull secret in development.

- **Required** when using this role for development versions of MAS
- Environment Variable: `ARTIFACTORY_APIKEY`
- Default: None

### mas_entitlement_username
Username for entitled registry. This username will be used to create the image pull secret. Set to `cp` when installing release or use your `w3Id` for dev.

- **Required**
- Environment Variable: `MAS_ENTITLEMENT_USERNAME`
- Default: `cp`

### ibm_entitlement_key
 API Key for entitled registry. This password will be used to create the image pull secret. Set to with IBM entitlement key when installing release or use your artifactory `apikey` for dev.

- **Required**
- Environment Variable: `IBM_ENTITLEMENT_KEY`
- Default: None

### mas_entitlement_key
 Used for the same purpose as `ibm_entitlement_key`.

- **Required** when `ibm_entitlement_key` is not provided
- Environment Variable: `MAS_ENTITLEMENT_KEY`
- Default: None

### mas_upgrade_strategy
The Upgrade strategy for MAS Operator.

- Optional
- Environment Variable: `MAS_UPGRADE_STRATEGY`
- Default: `Manual`

Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_app_id: "core"
    mas_instance_id: "inst1"
    mas_entitlement_username: "cp"
    mas_entitlement_key: "apikey..."
  roles:
    - ibm.mas_devops.convert_to_olm
```
