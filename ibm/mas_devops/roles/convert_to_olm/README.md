convert_to_olm
=============
This role provides capabilities to switch MAS and its Applications from legacy deployment (using mas-install.sh installer/manual deployment) to OLM/Channel subscription install.

Role Variables
--------------
### mas_catalog_source 
Optional. Defines the catalog to be used to install MAS channel subscription.

- Environment Variable: `MAS_CATALOG_SOURCE`
- Default: `ibm-operator-catalog`

### artifactory_username
Required when using this role for development versions of MAS. Defines Artifactory username.

- Environment Variable: `ARTIFACTORY_USERNAME`
- Default: None

### artifactory_apikey
Required when using this role for development versions of MAS. Defines Artifactory API Key.

- Environment Variable: `ARTIFACTORY_APIKEY`
- Default: None

### mas_instance_id
Required. The instance ID of Maximo Application Suite. This will be used to lookup for Manage application resources.

- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### mas_icr_cp
Defines the entitled registry from the images should be pulled from. Set this to `cp.icr.io/cp` when installing release version of MAS or `wiotp-docker-local.artifactory.swg-devops.com` for dev.

- Environment Variable: `MAS_ICR_CP`
- Default: `cp.icr.io/cp`

### mas_icr_cpopen
Defines the registry for non entitled images, such as operators. Set this to `icr.io/cpopen` when installing release version of MAS or `wiotp-docker-local.artifactory.swg-devops.com/cpopen` for dev

- Environment Variable: `MAS_ICR_CPOPEN`
- Default: `icr.io/cpopen`

### mas_entitlement_username
Required. Username for entitled registry. This username will be used to create the image pull secret. Set to `cp` when installing release or use your `w3Id` for dev.

- Environment Variable: `MAS_ENTITLEMENT_USERNAME`
- Default Value: `cp`

### mas_entitlement_key
Required. API Key for entitled registry. This password will be used to create the image pull secret. Set to with IBM entitlement key when installing release or use your artifactory `apikey` for dev.

- Environment Variable: `MAS_ENTITLEMENT_KEY` (or `IBM_ENTITLEMENT_KEY`)
- Default Value: None

### mas_upgrade_strategy
Optional. The Upgrade strategy for MAS Operator.

- Environment Variable: `MAS_UPGRADE_STRATEGY`
- Default Value: `Manual`

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
