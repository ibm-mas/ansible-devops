bas_install
===========

Install **IBM Behavior Analytics Services** and generate configuration that can be directly applied to IBM Maximo Application Suite.

Role Variables
--------------

###### Primary settings
- `bas_namespace` Optional - Defines the targetted cluster namespace/project where BAS will be installed, a default "ibm-bas" namespace will be created if none provided.
- `bas_persistent_storage` Required - Storage class where BAS will be installed - for IBM Cloud clusters, `ibmc-file-bronze-gid` can be used.
- `bas_meta_storage_class`: Required - Storage class where BAS internal components such as Kafka service will be installed - for IBM Cloud, `ibmc-block-bronze` can be used.
- `bas_username` Optional - BAS default username
- `bas_password` Optional - BAS default password
- `grafana_username` Optional - BAS default username for Grafana service.
- `grafana_password` Optional - BAS default password for Grafana service.
- `email` Optional - BAS default user's email
- `firstName` Optional - BAS default user's first name
- `lastName` Optional - BAS default user's last name

###### MAS integration

- `mas_config_dir` Defines the directory where BAS configuration will be stored to be used in MAS
- `mas_instance_id` Used to generate a output bascfg.yaml file to be used in a MAS instance

Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    # BAS Configuration
    bas_namespace: "{{ lookup('env', 'BAS_NAMESPACE') | default('ibm-bas', true) }}"
    bas_persistent_storage: "{{ lookup('env', 'BAS_PERSISTENT_STORAGE') | default('', true) }}"
    bas_meta_storage_class: "{{ lookup('env', 'BAS_META_STORAGE') | default('', true) }}"

    bas_username: "{{ lookup('env', 'BAS_USERNAME') | default('basuser', true) }}"
    bas_password: "{{ lookup('env', 'BAS_PASSWORD') | default('password', true) }}"

    grafana_username: "{{ lookup('env', 'GRAPHANA_USERNAME') | default('basuser', true) }}"
    grafana_password: "{{ lookup('env', 'GRAPHANA_PASSWORD') | default('password', true) }}"
    contact:
      email: "{{ lookup('env', 'BAS_CONTACT_MAIL') | default('john@mycompany.com', true) }}"
      firstName: "{{ lookup('env', 'BAS_CONTACT_FIRSTNAME') | default('John', true) }}"
      lastName: "{{ lookup('env', 'BAS_CONTACT_LASTNAME') | default('Barnes', true) }}"

    # MAS Configuration
    mas_instance_id: "{{ lookup('env', 'MAS_INSTANCE_ID') }}"
    mas_config_dir: "{{ lookup('env', 'MAS_CONFIG_DIR') }}"

  roles:
  - ibm.mas_devops.bas_install
```

License
-------

EPL-2.0
