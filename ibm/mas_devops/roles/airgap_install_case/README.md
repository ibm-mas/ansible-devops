airgap_install_case
===================

This role uses a CASE bundle and the `cloudctl` tool to run the airgap installation of the CASE operator.


Prereqs
-------

- `cloudctl` tool must be installed

Role Variables
--------------

- `cluster_name` Gives a name for the provisioned cluster
- `cluster_type` quickburn
- `username` username for fyre api
- `password` password for fyre api
- `case_name` the name of the CASE bundle to be installed
- `case_bundle_dir` the location of the CASE bundle
- `case_archive_dir` the location to store cloudctl working files, typically `./archive` under the `case_bundle_dir`
- `case_inventory_name`:` the name of the Setup inventory within the CASE bundle
- `target_namespace` the namespace targetted for airgap installation
- `catalog_type` development | production

#### Optional facts
- `debugs`: comma separated string of debug output to print


Example Playbook
----------------

```yaml
- hosts: localhost
  vars:
    # General configuration
    cluster_name: "{{ lookup('env', 'CLUSTER_NAME') }}"
    cluster_type: quickburn
    username: "{{ lookup('env', 'FYRE_USERNAME') }}"
    password: "{{ lookup('env', 'FYRE_APIKEY') }}"
    # Case config
    case_name: "{{ lookup('env', 'CASE_NAME') }}"
    case_bundle_dir: "{{ lookup('env', 'CASE_BUNDLE_DIR') }}"
    case_archive_dir: "{{ lookup('env', 'CASE_BUNDLE_DIR') }}/archive"
    case_inventory_name: "{{ lookup('env', 'CASE_INV_NAME') }}"
    # Airgap control parameters:
    target_namespace: "mas-{{ lookup('env', 'MAS_INSTANCE_ID') }}-core"
    catalog_type: development
    debugs: "_oc_status,installOperatorResult"

  roles:
    - ibm.mas_devops.airgap_install_case

```

License
-------

EPL-2.0
