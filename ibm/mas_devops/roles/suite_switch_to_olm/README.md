suite_switch_to_olm
=============
This role provides capabilities to switch a MAS instance from legacy deployment using mas-install.sh installer to OLM/Channel subscription install.

Role Variables
--------------
- `mas_catalog_source` Defines the catalog to be used to install MAS channel subscription. Default to be used is `ibm-operator-catalog`.
- `artifactory_username` Required when using this role for development versions of MAS.
- `artifactory_apikey` Required when using this role for development versions of MAS.
- `mas_instance_id` Defines the instance id to be used while looking up for existing MAS installation resources.
- `mas_icr_cp` Defines the entitled registry from the images should be pulled from. Set this to `cp.icr.io/cp` when installing release version of MAS or `wiotp-docker-local.artifactory.swg-devops.com` for dev.
- `mas_entitlement_username` Username for entitled registry. This username will be used to create the image pull secret. Set to `cp` when installing release or use your `w3Id` for dev.
- `mas_entitlement_key` API Key for entitled registry. This password will be used to create the image pull secret. Set to with IBM entitlement key when installing release or use your artifactory `apikey` for dev.
- `mas_upgrade_strategy` The Upgrade strategy for MAS Operator. Default is set to Manual.

Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: "inst1"
    mas_entitlement_key: "{{ lookup('env', 'IBM_ENTITLEMENT_KEY') }}"
  roles:
    - ibm.mas_devops.suite_switch_to_olm
```
