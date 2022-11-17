mas_load_dbc_scripts
================

This role allows to load and execute one or more ad-hoc DBC script files into Manage server.
The DBC script files to be executed should be placed under the `mas_load_dbc_scripts/files` prior running this role. 
Only `dbc` format files will be accepted. 
The role will assert if each script executed successfully and fail in case of errors while locating the DBC scripts or executing them against the Manage server.

Role Variables
--------------

### mas_instance_id
Required. Defines the instance id that was used for the MAS installation. It is used to lookup the Manage namespace.

Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    # MAS configuration
    mas_instance_id: "{{ lookup('env', 'MAS_INSTANCE_ID') }}"

  roles:
    - ibm.mas_devops.mas_load_dbc_scripts
```

License
-------

EPL-2.0
