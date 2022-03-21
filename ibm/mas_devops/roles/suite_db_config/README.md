suite_config
============

This role is used to configure db in Maximo Application Suite.

Role Variables
--------------

ole Variables
--------------
- `db_instance_id` Defines the jdbc db instance id to be used to install the MAS app. 
- `mas_instance_id` Defines the instance id that was used for the db configure in MAS installation
- `mas_workspace_id` Defines mas  workspace id used to install the MAS app.
- `db_username` This username will be used to configure the DB in MAS.
- `jdbc_instance_password` This password will be used connect to DB in Maximo Application Suite.
- `jdbc_url`
- `db_pem_file`
- `jdbc_template`


Example Playbook
----------------

```yaml
---
- hosts: localhost
  any_errors_fatal: true
  vars:
    db_instance_id: "{{ lookup('env', 'DB_INSTANCE_ID') | default('dbinst', True) }}"
    mas_instance_id: "{{ lookup('env', 'MAS_INSTANCE_ID') }}"
    mas_workspace_id: "{{ lookup('env', 'MAS_WORKSPACE_ID') }}"
    db_username: "{{ lookup('env', 'MAS_JDBC_USER') }}"
    jdbc_instance_password: "{{ lookup('env', 'MAS_JDBC_PASSWORD') }}"
    jdbc_url: "{{ lookup('env', 'MAS_JDBC_URL') }}"
    db_pem_file: "{{ lookup('env', 'MAS_JDBC_CERT_LOCAL_FILE') }}"
    jdbc_template:  "{{ lookup('env', 'MAS_JDBC_CONFIG') | default('templates/jdbccfg-workspace-application.yml.j2', true) }}"

  roles:
    - ibm.mas_devops.suite_db_config
```

License
-------

EPL-2.0
