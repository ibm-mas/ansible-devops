bas_install
===========

Installs **IBM Behavior Analytics Services** on IBM Cloud Openshift Clusters (ROKS) and generates configuration that can be directly applied to IBM Maximo Application Suite.

Role Variables
--------------

### bas_namespace
Optional - Defines the targetted cluster namespace/project where BAS will be installed. If not provided, default BAS namespace will be 'ibm-bas'.

- Environment Variable: `BAS_NAMESPACE`
- Default Value: `ibm-mas`

### bas_persistent_storage_class
Required - Storage class where BAS will be installed - for IBM Cloud clusters, `ibmc-file-bronze-gid` can be used.

- Environment Variable: `BAS_PERSISTENT_STORAGE_CLASS`
- Default Value: None

### bas_meta_storage_class
Required - Storage class where BAS internal components such as Kafka service will be installed - for IBM Cloud clusters, `ibmc-block-bronze` can be used.

- Environment Variable: `BAS_META_STORAGE_CLASS`
- Default Value: None

### bas_event_scheduler_frequency
Optional - Defines the frequency that BAS will collect event data. The value can be set following a [cron tab](https://crontab.guru/) format.

- Environment Variable: `BAS_EVENT_SCHEDULER_FREQUENCY`
- Default Value: `0 12 * * *` (every day at 12PM)

### bas_username
Optional - BAS default username.

- Environment Variable: `BAS_USERNAME`
- Default Value: `basuser`

### bas_password
Optional - BAS default password.

- Environment Variable: `BAS_PASSWORD`
- Default Value: random 15 character string

### bas_grafana_username
Optional - BAS default username for Grafana service.

- Environment Variable: `BAS_GRAFANA_USERNAME`
- Default Value: `basuser`

### bas_grafana_password
Optional - BAS default password for Grafana service.

- Environment Variable: `BAS_GRAFANA_PASSWORD`
- Default Value: random 15 character string

### bas_contact.email
Required - BAS default user's email

- Environment Variable: `BAS_CONTACT_MAIL`
- Default Value: None

### bas_contact.firstName
Required - BAS default user's first name

- Environment Variable: `BAS_CONTACT_FIRSTNAME`
- Default Value: None

### bas_contact.lastName
Required - BAS default user's last name

- Environment Variable: `BAS_CONTACT_LASTNAME`
- Default Value: None

### mas_instance_id
The instance ID of Maximo Application Suite that the BasCfg configuration will target.  If this or `mas_config_dir` are not set then the role will not generate a BasCfg template.

- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### mas_config_dir
Local directory to save the generated BasCfg resource definition.  This can be used to manually configure a MAS instance to connect to BAS instance, or used as an input to the [suite_config](suite_config.md) role. If this or `mas_instance_id` are not set then the role will not generate a BasCfg template.

- Environment Variable: `MAS_CONFIG_DIR`
- Default Value: None

Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    bas_persistent_storage_class: ibmc-file-bronze-gid
    bas_meta_storage_class: ibmc-block-bronze
    mas_instance_id: masinst1
    mas_config_dir: ~/masconfig
    bas_contact:
      email: 'john@email.com'
      firstName: 'john'
      lastName: 'winter'
  roles:
  - ibm.mas_devops.bas_install
```

License
-------

EPL-2.0
