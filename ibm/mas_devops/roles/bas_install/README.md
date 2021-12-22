bas_install
===========

Installs **IBM Behavior Analytics Services** on IBM Cloud Openshift Clusters (ROKS) and generates configuration that can be directly applied to IBM Maximo Application Suite.

Role Variables
--------------

###### Primary settings
- `bas_namespace` Optional - Defines the targetted cluster namespace/project where BAS will be installed. If not provided, default BAS namespace will be 'ibm-bas'.
- `bas_persistent_storage_class` Required - Storage class where BAS will be installed - for IBM Cloud clusters, `ibmc-file-bronze-gid` can be used.
- `bas_meta_storage_class` Required - Storage class where BAS internal components such as Kafka service will be installed - for IBM Cloud clusters, `ibmc-block-bronze` can be used.
- `bas_username` Optional - BAS default username. If not provided, default username will be 'basuser'
- `bas_password` Optional - BAS default password. If not provided, a random 15 character password will be generated
- `bas_grafana_username` Optional - BAS default username for Grafana service. If not provided, default username will be 'basuser'
- `bas_grafana_password` Optional - BAS default password for Grafana service. If not provided, a random 15 character password will be generated
- `bas_contact.email` Required - BAS default user's email
- `bas_contact.firstName` Required - BAS default user's first name
- `bas_contact.lastName` Required - BAS default user's last name

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
    bas_persistent_storage_class: "ibmc-file-bronze-gid"
    bas_meta_storage_class: "ibmc-block-bronze"

    bas_username: "{{ lookup('env', 'BAS_USERNAME') | default('basuser', true) }}"
    bas_password: "{{ lookup('env', 'BAS_PASSWORD') | default('', true) }}"

    bas_grafana_username: "{{ lookup('env', 'BAS_GRAFANA_USERNAME') | default('basuser', true) }}"
    bas_grafana_password: "{{ lookup('env', 'BAS_GRAFANA_PASSWORD') | default('', true) }}"
    bas_contact:
      email: "{{ lookup('env', 'BAS_CONTACT_MAIL') | default('', true) }}"
      firstName: "{{ lookup('env', 'BAS_CONTACT_FIRSTNAME') | default('', true) }}"
      lastName: "{{ lookup('env', 'BAS_CONTACT_LASTNAME') | default('', true) }}"

    # MAS Configuration
    mas_instance_id: "{{ lookup('env', 'MAS_INSTANCE_ID') }}"
    mas_config_dir: "{{ lookup('env', 'MAS_CONFIG_DIR') }}"

  roles:
  - ibm.mas_devops.bas_install
```

License
-------

EPL-2.0
