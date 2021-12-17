cp4d_wds
==========

It's only for WDS 4.0.x install on the existing CP4D 4.0.x and WDS instance provisioning, and also generated WDScfg (For Assist Install) related yaml to MAS config Directory.

It's also used for WDScfg (For Assist Install) related yaml preparation if you want to use the existing external WDS instance. 

Role Variables
--------------

- `useexternalwd` Set to `true` if you want to use existing WDS, `false` by default 
- `ASSIST_WDS_URL` External WDS instance URL  
- `ASSIST_WDS_ADMIN` External CP4D ADMIN User name
- `ASSIST_WDS_PASS` External CP4D ADMIN User password
- `MAS_CONFIG_DIR` Provide the MAS Config Dir to Save the WDS related Config yaml
- `MAS_INSTANCE_ID` Provide the MAS instance ID that will be used in any generated MAS configuration files



Example Playbook
----------------
WDS install and WDS instance in the OCP Env 
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    # Create the MAS WDSCfg & Secret resource definitions
    mas_instance_id: "{{ lookup('env', 'MAS_INSTANCE_ID') }}"
    mas_config_dir: "{{ lookup('env', 'MAS_CONFIG_DIR') }}"
  roles:
    - mas.devops.cp4d_wds
```
Use External WDS instance in the OCP Env 
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    #  Use External WDS instance for assist install
    useexternalwds: true
    assist_wds_url: "{{ lookup('env', 'ASSIST_WDS_URL') }}"
    assist_wds_admin: "{{ lookup('env', 'ASSIST_WDS_ADMIN') }}"
    assist_wds_pass: "{{ lookup('env', 'ASSIST_WDS_PASS') }}"

    #  Create the MAS WDSCfg & Secret resource definitions
    mas_instance_id: "{{ lookup('env', 'MAS_INSTANCE_ID') }}"
    mas_config_dir: "{{ lookup('env', 'MAS_CONFIG_DIR') }}"
  roles:
    - mas.devops.cp4d_wds
```

License
-------

EPL-2.0
