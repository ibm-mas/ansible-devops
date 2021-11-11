cp4d_db2wh
==========

TODO: Add intro

Role Variables
--------------

TODO: Finish documentation


Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    # Configuration for the Db2 cluster
    db2wh_version: 11.5.6.0-cn3
    db2wh_username: db2inst1
    db2wh_instance_id: db2wh-dbansible
    db2wh_table_org: ROW
    db2wh_dbname: BLUDB
    db2wh_cpu_limits: 6100m # default: 6.1 CPUs
    db2wh_memory_limits: 18Gi # default: 18.0 GiB
    db2wh_system_storage_class: ibmc-file-silver-gid
    db2wh_system_storage_size: 100Gi
    db2wh_user_storage_class: ibmc-file-gold-gid
    db2wh_user_storage_size: 512Gi
    db2wh_logs_storage_class: ibmc-file-silver-gid
    db2wh_logs_storage_size: 100Gi
    db2wh_temp_storage_class: ibmc-file-silver-gid
    db2wh_temp_storage_size: 100Gi

    # Create the MAS JdbcCfg & Secret resource definitions
    mas_instance_id: "{{ lookup('env', 'MAS_INSTANCE_ID') }}"
    mas_config_dir: "{{ lookup('env', 'MAS_CONFIG_DIR') }}"
    db2wh_cfg_file: /tmp/jdbccfg-cp4ddb2wh-system.yaml
  roles:
    - ibm.mas_devops.cp4d40_db2wh
```

License
-------

EPL-2.0
