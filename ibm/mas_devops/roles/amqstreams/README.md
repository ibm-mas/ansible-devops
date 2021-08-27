amqstreams
==========

This role provides support to install a Kafka Cluster using [Red Hat AMQ Streams](https://www.redhat.com/en/resources/amq-streams-datasheet) and generate configuration that can be directly applied to Maximo Application Suite.

> The Red Hat AMQ streams component is a massively scalable, distributed, and high-performance data streaming platform based on the Apache Kafka project. It offers a distributed backbone that allows microservices and other applications to share data with high throughput and low latency.
>
> As more applications move to Kubernetes and Red Hat OpenShift, it is increasingly important to be able to run the communication infrastructure on the same platform. Red Hat OpenShift, as a highly scalable platform, is a natural fit for messaging technologies such as Kafka. The AMQ streams component makes running and managing Apache Kafka OpenShift native through the use of powerful operators that simplify the deployment, configuration, management, and use of Apache Kafka on Red Hat OpenShift.
>
> The AMQ streams component is part of the Red Hat AMQ family, which also includes the AMQ broker, a longtime innovation leader in Java™ Message Service (JMS) and polyglot messaging, as well as the AMQ interconnect router, a wide-area, peer-to-peer messaging solution.

Role Variables
--------------

- `mas_instance_id` The instance ID of Maximo Application Suite that the KafkaCfg configuration will target, there is no default value for this, it must be passed into the role when invoked.
- `kafka_namespace` The namespace where the operator and Kafka cluster will be deployed, defaults to `amq-streams`
- `kafka_cluster_name` The name of the Kafka cluster that will be created, defaults to `maskafka`
- `kafka_cluster_size` The configuration to apply, there are two configurations available: small and large.  Defaults to `small`
- `kafka_user_name` The name of the user to setup in the cluster for MAS, defaults to `masuser`
- `kafka_cfg_file` The location on the local filesystem where the template for the KafkaCfg and associated Secret will be saved.  Defaults to `/tmp/kafkacfg-amqstreams-system.yaml`


Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    kafka_namespace: "{{ lookup('env', 'KAFKA_NAMESPACE') }}"
    kafka_cluster_name: "{{ lookup('env', 'KAFKA_CLUSER_NAME') }}"
    kafka_cluster_size: "{{ lookup('env', 'KAFKA_CLUSTER_SIZE') }}"
    kafka_storage_class: "{{ lookup('env', 'KAFKA_STORAGE_CLASS') }}"
    kafka_user_name: "{{ lookup('env', 'KAFKA_USER_NAME') }}"
    mas_instance_id: "{{ lookup('env', 'MAS_INSTANCE_ID') }}"
    mas_config_dir: "{{ lookup('env', 'MAS_CONFIG_DIR') }}"
  roles:
    - ibm.mas_devops.amqstreams
```

License
-------

EPL-2.0
