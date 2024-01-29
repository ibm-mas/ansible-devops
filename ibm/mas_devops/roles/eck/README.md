eck
=====

This role provides support to install Elastic Cluster for Kubernetes (ECK)

Role Variables
--------------
### kafka_action
Action to be performed by Kafka role. Valid values are `install`, `upgrade` or `uninstall`.  The `upgrade` action applies only to the `strimzi` and `redhat` providers.

- Environment Variable: `KAFKA_ACTION`
- Default Value: `install`



Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    # Set storage class suitable for use on IBM Cloud ROKS
    kafka_storage_class: ibmc-block-gold

    # Generate a KafkaCfg template
    mas_instance_id: masinst1
    mas_config_dir: ~/masconfig
  roles:
    - ibm.mas_devops.kafka
```


License
-------

EPL-2.0
