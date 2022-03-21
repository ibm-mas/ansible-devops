suite_config_workspace
============
This role is used to configure  Maximo Application Suite workspace.

Role Variables
--------------
### mas_instance_id
Defines the instance id that was used for the MAS installation

### mas_workspace_id
MAS application workspace to use to configure app components

### mas_namespace
The namespace where the app components will be deployed.

#
Example Playbook
----------------

```yaml
---
- hosts: localhost
  any_errors_fatal: true
  vars:
    # Choose which catalog source to use for the MAS install, default to the IBM operator catalog
    mas_catalog_source: "{{ lookup('env', 'MAS_CATALOG_SOURCE') | default('ibm-operator-catalog', true) }}"

    # MAS configuration
    mas_instance_id: "{{ lookup('env', 'MAS_INSTANCE_ID') }}"
    mas_workspace_id: "{{ lookup('env', 'MAS_WORKSPACE_ID') }}"

    mas_config_dir: "{{ lookup('env', 'MAS_CONFIG_DIR') }}"
    mas_app_workspace_configure: "{{ lookup('env', 'MAS_WORKSPACE_CONFIG') | default('templates/workspace.yml.j2', true) }}"

  roles:

    - ibm.mas_devops.suite_config_workspace
    

```

License
-------

EPL-2.0
