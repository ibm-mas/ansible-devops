convert_to_olm
=============
This role provides capabilities to switch MAS and its Applications from legacy deployment (via mas-install.sh installer/manual deployment) to OLM/Channel subscription install.

Role Variables
--------------

### mas_app_id
**Required**. The name of the Maximo Application Suite Application. This will be used to lookup for application namespace and resources.

- Environment Variable: `MAS_APP_ID`
- One of [`assist`, `core`, `health`, `hputilities`, `iot`, `manage`, `monitor`, `optimizer`, `predict`, `visualinspection`]
- Default: None

### mas_instance_id
**Required**. The instance ID of Maximo Application Suite. This will be used to lookup for application namespace and resources.

- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

### mas_catalog_source 
Optional. Defines the catalog to be used to install MAS channel subscription.

- Environment Variable: `MAS_CATALOG_SOURCE`
- Default: `ibm-operator-catalog`

### artifactory_username
**Required** when using this role for development versions of MAS. Defines Artifactory username.

- Environment Variable: `ARTIFACTORY_USERNAME`
- Default: None

### artifactory_apikey
**Required** when using this role for development versions of MAS. Defines Artifactory API Key.

- Environment Variable: `ARTIFACTORY_APIKEY`
- Default: None

### mas_entitlement_username
**Required**. Username for entitled registry. This username will be used to create the image pull secret. Set to `cp` when installing release or use your `w3Id` for dev.

- Environment Variable: `MAS_ENTITLEMENT_USERNAME`
- Default: `cp`

### ibm_entitlement_key
**Required**. API Key for entitled registry. This password will be used to create the image pull secret. Set to with IBM entitlement key when installing release or use your artifactory `apikey` for dev.

- Environment Variable: `IBM_ENTITLEMENT_KEY`
- Default: None

### mas_entitlement_key
**Required**. Only required when `ibm_entitlement_key` is not provided. Used for the same purpose as `ibm_entitlement_key`.

- Environment Variable: `MAS_ENTITLEMENT_KEY`
- Default: None

### mas_upgrade_strategy
Optional. The Upgrade strategy for MAS Operator.

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
    mas_entitlement_key: "{{ lookup('env', 'IBM_ENTITLEMENT_KEY') }}"
  roles:
    - ibm.mas_devops.convert_to_olm
```
