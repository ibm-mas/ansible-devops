kafka
=====

This role provides support to install a Kafka Cluster using [Red Hat AMQ Streams](https://www.redhat.com/en/resources/amq-streams-datasheet), IBM Event Streams or AWS MSK and generate configuration that can be directly applied to Maximo Application Suite.

> The Red Hat AMQ streams component is a massively scalable, distributed, and high-performance data streaming platform based on the Apache Kafka project. It offers a distributed backbone that allows microservices and other applications to share data with high throughput and low latency.
>
> As more applications move to Kubernetes and Red Hat OpenShift, it is increasingly important to be able to run the communication infrastructure on the same platform. Red Hat OpenShift, as a highly scalable platform, is a natural fit for messaging technologies such as Kafka. The AMQ streams component makes running and managing Apache Kafka OpenShift native through the use of powerful operators that simplify the deployment, configuration, management, and use of Apache Kafka on Red Hat OpenShift.
>
> The AMQ streams component is part of the Red Hat AMQ family, which also includes the AMQ broker, a longtime innovation leader in Java™ Message Service (JMS) and polyglot messaging, as well as the AMQ interconnect router, a wide-area, peer-to-peer messaging solution.


!!! tip
    The role will generate a yaml file containing the definition of a Secret and KafkaCfg resource that can be used to configure the deployed cluster as the MAS system Kafka.

    This file can be directly applied using `oc apply -f $MAS_CONFIG_DIR/kafkacfg-amqstreams-system.yaml` or used in conjunction with the [suite_config](suite_config.md) role.

Role Variables
--------------

### kafka_version
The version of Kafka to deploy by the operator. Before changing the kafka_version make the version is supported
by the [amq-streams operator version](https://access.redhat.com/documentation/en-us/red_hat_amq_streams).

- Environment Variable: `KAFKA_VERSION`
- Default Value: `3.3.1`

### kafka_namespace
The namespace where the operator and Kafka cluster will be deployed.

- Environment Variable: `KAFKA_NAMESPACE`
- Default Value: `amq-streams`

### kafka_cluster_name
The name of the Kafka cluster that will be created

- Environment Variable: `KAFKA_CLUSTER_NAME`
- Default Value: `maskafka`

### kafka_cluster_size
The configuration to apply, there are two configurations available: small and large.

- Environment Variable: `KAFKA_CLUSTER_SIZE`
- Default Value: `small`

### kafka_storage_class
The name of the storage class to configure the AMQStreams operator to use for persistent storage in the Kafka cluster.

- Environment Variable: `KAFKA_STORAGE_CLASS`
- Default Value: lookup supported storage classes in the cluster

### kafka_storage_size
The size of the storage to configure the AMQStreams operator to use for persistent storage in the Kafka cluster.

- Environment Variable: `KAFKA_STORAGE_SIZE`
- Default Value: `100Gi`

### zookeeper_storage_class
The name of the storage class to configure the AMQStreams operator to use for persistent storage in the Zookeeper cluster.

- Environment Variable: `ZOOKEEPER_STORAGE_CLASS`
- Default Value: lookup supported storage classes in the cluster

### zookeeper_storage_size
The size of the storage to configure the AMQStreams operator to use for persistent storage in the Zookeeper cluster.

- Environment Variable: `ZOOKEEPER_STORAGE_SIZE`
- Default Value: `10Gi`

### kafka_user_name
The name of the user to setup in the cluster for MAS.

- Environment Variable: `KAFKA_USER_NAME`
- Default Value: `masuser`

### kafka_user_password (supported in Strimzi operator verion [0.25.0](https://github.com/strimzi/strimzi-kafka-operator/blob/main/CHANGELOG.md#0250) - amq streams operator version 2.x)
The password of the user to setup in the cluster for MAS.

- Environment Variable: `KAFKA_USER_PASSWORD`
- Default Value: a randomly generated password is used if one is not specified

### mas_instance_id
The instance ID of Maximo Application Suite that the KafkaCfg configuration will target.  If this or `mas_config_dir` are not set then the role will not generate a KafkaCfg template.

- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### mas_config_dir
Local directory to save the generated KafkaCfg resource definition.  This can be used to manually configure a MAS instance to connect to the Kafka cluster, or used as an input to the [suite_config](suite_config.md) role. If this or `mas_instance_id` are not set then the role will not generate a KafkaCfg template.

- Environment Variable: `MAS_CONFIG_DIR`
- Default Value: None

### custom_labels
List of comma separated key=value pairs for setting custom labels on instance specific resources.

- Optional
- Environment Variable: `CUSTOM_LABELS`
- Default Value: None

IBM Cloud Evenstreams Role Variables
-------------------------------------

### ibmcloud_apikey
Defines IBM Cloud API Key. This API Key needs to have access to manage (provision/deprovision) IBM Cloud Event Streams.

- Required
- Environment Variable: `IBMCLOUD_APIKEY`
- Default Value: None

### eventstreams_resourcegroup
Defines the IBM Cloud Resource Group to target the Event Streams instance.

- Optional
- Environment Variable: `EVENTSTREAMS_RESOURCEGROUP`
- Default Value: `Default` or value defined by `IBMCLOUD_RESOURCEGROUP`

### eventstreams_name
Event Streams instance name.

- Required
- Environment Variable: `EVENTSTREAMS_NAME`
- Default Value: None

### eventstreams_plan
Event Streams instance plan.

- Optional
- Environment Variable: `EVENTSTREAMS_PLAN`
- Default Value: `standard`

### eventstreams_location

- Optional
- Environment Variable: `EVENTSTREAMS_LOCATION`
- Default Value: `us-east` or value defined by `IBMCLOUD_REGION`

### eventstreams_retention
Event Streams topic retention period (in miliseconds).

- Optional
- Environment Variable: `EVENTSTREAMS_RETENTION`
- Default Value: `1209600000`

### eventstreams_create_manage_jms_topic
Defines whether to create specific Manage application JMS topics by default.

- Optional
- Environment Variable: `EVENTSTREAMS_CREATE_MANAGE_JMS_TOPICS`
- Default Value: `True`

### mas_instance_id
The instance ID of Maximo Application Suite that the KafkaCfg configuration will target.  If this or `mas_config_dir` are not set then the role will not generate a KafkaCfg template.

- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### mas_config_dir
Local directory to save the generated KafkaCfg resource definition.  This can be used to manually configure a MAS instance to connect to the Kafka cluster, or used as an input to the [suite_config](suite_config.md) role. If this or `mas_instance_id` are not set then the role will not generate a KafkaCfg template.

- Environment Variable: `MAS_CONFIG_DIR`
- Default Value: None

### custom_labels
List of comma separated key=value pairs for setting custom labels on instance specific resources.

- Optional
- Environment Variable: `CUSTOM_LABELS`
- Default Value: None


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

AWS MSK Role Variables
-------------------------------------

## Prerequisites
To run this role successfully you must have already installed the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).
Also, you need to have AWS user credentials configured via `aws configure` command or simply export `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables with your corresponding AWS username credentials prior running this role.

### kafka_action
Action to be performed by Kafka role. Valid values are `install` or `uninstall`. To install AWS MSK kafka cluster, set this variable as `install`. To uninstall an existing AWS MSK kafka cluster, set this variable as `uninstall`.

- Environment Variable: `KAFKA_ACTION`
- Default Value: `install`

### kafka_provider
Valid kafka providers are `redhat`, `ibm` and `aws`. To install or uninstall AWS MSK kafka cluster, set this variable as `aws`

- Environment Variable: `KAFKA_PROVIDER`
- Default Value: `redhat`

### kafka_version
The version of Kafka to deploy.

- Environment Variable: `KAFKA_VERSION`
- Default Value: `2.7.0`

### kafka_cluster_name

- Required
- Environment Variable: `KAFKA_CLUSTER_NAME`
- Default Value: None

### aws_access_key_id

- Required
- Environment Variable: `AWS_ACCESS_KEY_ID`
- Default Value: None

### aws_secret_access_key

- Required
- Environment Variable: `AWS_SECRET_ACCESS_KEY`
- Default Value: None

### aws_region

- Required
- Environment Variable: `AWS_REGION`
- Default Value: None

### vpc_id

- Required
- Environment Variable: `VPC_ID`
- Default Value: None

### aws_msk_cidr_az1

- Required
- Environment Variable: `AWS_MSK_CIDR_AZ1`
- Default Value: None

### aws_msk_cidr_az2

- Required
- Environment Variable: `AWS_MSK_CIDR_AZ2`
- Default Value: None

### aws_msk_cidr_az3

- Required
- Environment Variable: `AWS_MSK_CIDR_AZ3`
- Default Value: None

### aws_msk_ingress_cidr

- Required
- Environment Variable: `AWS_MSK_INGRESS_CIDR`
- Default Value: None

### aws_msk_egress_cidr

- Required
- Environment Variable: `AWS_MSK_EGRESS_CIDR`
- Default Value: None

### aws_kafka_user_name

- Required
- Environment Variable: `AWS_KAFKA_USER_NAME`
- Default Value: None

### aws_kafka_user_password

- Optional
- Environment Variable: `AWS_KAFKA_USER_PASSWORD`
- Default Value: None

### aws_msk_instance_type

- Optional
- Environment Variable: `AWS_MSK_INSTANCE_TYPE`
- Default Value: `kafka.m5.large`

### aws_msk_volume_size

- Optional
- Environment Variable: `AWS_MSK_VOLUME_SIZE`
- Default Value: `100`

### aws_msk_instance_number

- Optional
- Environment Variable: `AWS_MSK_INSTANCE_NUMBER`
- Default Value: `3`

### mas_instance_id
The instance ID of Maximo Application Suite that the KafkaCfg configuration will target.  If this or `mas_config_dir` are not set then the role will not generate a KafkaCfg template.

- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### mas_config_dir
Local directory to save the generated KafkaCfg resource definition.  This can be used to manually configure a MAS instance to connect to the Kafka cluster, or used as an input to the [suite_config](suite_config.md) role. If this or `mas_instance_id` are not set then the role will not generate a KafkaCfg template.

- Environment Variable: `MAS_CONFIG_DIR`
- Default Value: None

### custom_labels
List of comma separated key=value pairs for setting custom labels on instance specific resources.

- Optional
- Environment Variable: `CUSTOM_LABELS`
- Default Value: None


Example Playbook to install AWS MSK
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    aws_region: ca-central-1
    aws_access_key_id: *****
    aws_secret_access_key: *****
    kafka_version: 2.8.1
    kafka_provider: aws
    kafka_action: install
    kafka_cluster_name: msk-abcd0zyxw
    kafka_namespace: msk-abcd0zyxw
    vpc_id: vpc-07088da510b3c35c5
    aws_kafka_user_name: mskuser-abcd0zyxw
    aws_msk_instance_type: kafka.t3.small
    aws_msk_volume_size: 100
    aws_msk_instance_number: 3
    aws_msk_cidr_az1: "10.0.128.0/20"
    aws_msk_cidr_az2: "10.0.144.0/20"
    aws_msk_cidr_az3: "10.0.160.0/20"
    aws_msk_ingress_cidr: "10.0.0.0/16"
    aws_msk_egress_cidr: "10.0.0.0/16"
    # Generate a KafkaCfg template
    mas_config_dir: /var/tmp/masconfigdir
    mas_instance_id: abcd0zyxw
  roles:
    - ibm.mas_devops.kafka
```

Example Playbook to uninstall AWS MSK
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    aws_region: ca-central-1
    aws_access_key_id: *****
    aws_secret_access_key: *****
    vpc_id: vpc-07088da510b3c35c5
    kafka_provider: aws
    kafka_action: uninstall
    kafka_cluster_name: msk-abcd0zyxw
    aws_msk_cidr_az1: "10.0.128.0/20"
    aws_msk_cidr_az2: "10.0.144.0/20"
    aws_msk_cidr_az3: "10.0.160.0/20"
  roles:
    - ibm.mas_devops.kafka
```

License
-------

EPL-2.0
