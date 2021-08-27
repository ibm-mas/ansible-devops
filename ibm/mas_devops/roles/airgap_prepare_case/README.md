airgap_prepare_case
===================

Prepare the specified CASE bundle for airgap installation. It can download the CASE bundle from an internet archive or take a case bundle in a local directory.

Role Variables
--------------

TODO: Finish documentation


Example Playbook
----------------

```yaml
- hosts: localhost
  vars:
    # Case config
    case_name: "{{ lookup('env', 'CASE_NAME') }}"
    case_source: "{{ lookup('env', 'CASE_SOURCE') }}"
    case_bundle_dir: "{{ lookup('env', 'CASE_BUNDLE_DIR') }}"
    case_archive_dir: "{{ lookup('env', 'CASE_BUNDLE_DIR') }}/archive"
    case_inventory_name: "{{ lookup('env', 'CASE_INV_NAME') }}"
    debugs: "registryHosts,mirrorImageResult,configureClusterResult"

  roles:
    - ibm.mas_devops.airgap_prepare_case
```

License
-------

EPL-2.0
