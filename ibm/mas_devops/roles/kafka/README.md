# kafka

This role provides support to install a Kafka Cluster using [Strimzi](https://strimzi.io/), [Red Hat AMQ Streams](https://www.redhat.com/en/resources/amq-streams-datasheet), [IBM Event Streams](https://www.ibm.com/cloud/event-streams) or [AWS MSK](https://aws.amazon.com/msk/) and generate configuration that can be directly applied to Maximo Application Suite.

> Both Strimzi and Red Hat AMQ streams component are massively scalable, distributed, and high-performance data streaming platform based on the Apache Kafka project. Both offer a distributed backbone that allows microservices and other applications to share data with high throughput and low latency.
>
> As more applications move to Kubernetes and Red Hat OpenShift, it is increasingly important to be able to run the communication infrastructure on the same platform. Red Hat OpenShift, as a highly scalable platform, is a natural fit for messaging technologies such as Kafka. The AMQ streams component makes running and managing Apache Kafka OpenShift native through the use of powerful operators that simplify the deployment, configuration, management, and use of Apache Kafka on Red Hat OpenShift.
>
> The AMQ streams component is part of the Red Hat AMQ family, which also includes the AMQ broker, a longtime innovation leader in Java™ Message Service (JMS) and polyglot messaging, as well as the AMQ interconnect router, a wide-area, peer-to-peer messaging solution. Under the covers, AMQ streams leverages Strimzi's architecture, resources and configurations.

**Note:** The MAS license does not include entitlement for AMQ streams. The MAS Devops Collection supports this Kafka deployment as an example only. Therefore, we recommend the use of Strimzi for an opensource Kafka provider.

!!! tip
    The role will generate a yaml file containing the definition of a Secret and KafkaCfg resource that can be used to configure the deployed cluster as the MAS system Kafka.

    This file can be directly applied using `oc apply -f $MAS_CONFIG_DIR/kafkacfg-amqstreams-system.yaml` or used in conjunction with the [suite_config](suite_config.md) role.

## Role Variables

### General Variables

#### kafka_action
Specifies which operation to perform on the Kafka cluster.

- **Optional**
- Environment Variable: `KAFKA_ACTION`
- Default Value: `install`

**Purpose**: Controls what action the role executes against Kafka deployments. This allows the same role to handle installation, upgrades, and removal of Kafka clusters.

**When to use**:
- Use `install` (default) for initial Kafka deployment
- Use `upgrade` to upgrade existing Kafka cluster (Strimzi and Red Hat AMQ Streams only)
- Use `uninstall` to remove Kafka cluster and operator

**Valid values**: `install`, `upgrade`, `uninstall`

**Impact**: 
- `install`: Deploys Kafka operator and creates cluster
- `upgrade`: Upgrades existing Kafka cluster (only for Strimzi and Red Hat providers)
- `uninstall`: Removes Kafka cluster and operator

**Related variables**:
- `kafka_provider`: Upgrade action only supported for `strimzi` and `redhat` providers
- `kafka_version`: Target version when upgrading

**Note**: The `upgrade` action is only available for Strimzi and Red Hat AMQ Streams providers. IBM Event Streams and AWS MSK do not support in-place upgrades through this role.

#### kafka_provider
Specifies which Kafka provider to use for deployment.

- **Optional**
- Environment Variable: `KAFKA_PROVIDER`
- Default Value: `strimzi`

**Purpose**: Determines which Kafka implementation to deploy. Different providers offer different features, licensing models, and deployment targets (on-cluster vs cloud-managed).

**When to use**:
- Use `strimzi` (default) for open-source Kafka on OpenShift (recommended, no additional license required)
- Use `redhat` for Red Hat AMQ Streams (requires separate license not included with MAS)
- Use `ibm` for IBM Event Streams on IBM Cloud (managed service, additional cost)
- Use `aws` for AWS MSK (managed service, additional cost)

**Valid values**: `strimzi`, `redhat`, `ibm`, `aws`

**Impact**: 
- `strimzi`: Deploys open-source Kafka using Strimzi operator (no additional license)
- `redhat`: Deploys AMQ Streams (requires Red Hat AMQ license)
- `ibm`: Provisions IBM Event Streams in IBM Cloud (requires IBM Cloud account and incurs costs)
- `aws`: Provisions AWS MSK in AWS account (requires AWS account and incurs costs)

**Related variables**:
- Different providers require different additional variables
- `kafka_action=upgrade` only supported for `strimzi` and `redhat`

**Note**: **IMPORTANT** - MAS license does NOT include entitlement for Red Hat AMQ Streams. Strimzi is recommended for open-source Kafka. IBM and AWS providers provision managed cloud services with additional costs.

### Red Hat AMQ Streams & Strimzi Variables

#### kafka_version
Kafka version to deploy (Strimzi and Red Hat AMQ Streams only).

- **Optional**
- Environment Variable: `KAFKA_VERSION`
- Default Value: `3.8.0` for AMQ Streams, `3.9.0` for Strimzi

**Purpose**: Specifies which Apache Kafka version to deploy when using Strimzi or Red Hat AMQ Streams providers. The version must be supported by the installed operator.

**When to use**:
- Leave as default for standard deployments
- Set explicitly when you need a specific Kafka version
- Verify version compatibility with operator before changing

**Valid values**: Valid Kafka version supported by the operator (e.g., `3.8.0`, `3.9.0`)

**Impact**: Determines which Kafka version is deployed. Incompatible versions will cause deployment failures.

**Related variables**:
- `kafka_provider`: Only applies to `strimzi` and `redhat` providers
- Operator version determines available Kafka versions

**Note**: Before changing this value, verify the version is supported by your [AMQ Streams operator](https://access.redhat.com/documentation/en-us/red_hat_amq_streams) or [Strimzi operator](https://strimzi.io/downloads/). This variable does not apply to IBM Event Streams or AWS MSK providers.

### kafka_namespace
OpenShift namespace where Kafka operator and cluster will be deployed.

- **Optional**
- Environment Variable: `KAFKA_NAMESPACE`
- Default Value: `amq-streams` for AMQ Streams, `strimzi` for Strimzi

**Purpose**: Specifies the namespace for deploying the Kafka operator and Kafka cluster resources. This isolates Kafka resources from other applications.

**When to use**:
- Use default for standard single-cluster deployments
- Set to custom namespace when organizing multiple Kafka deployments
- Must be unique if deploying multiple Kafka clusters

**Valid values**: Any valid Kubernetes namespace name (e.g., `strimzi`, `amq-streams`, `kafka-prod`)

**Impact**: All Kafka resources (operator, cluster, topics, users) are created in this namespace.

**Related variables**:
- `kafka_provider`: Default namespace depends on provider (`strimzi` or `amq-streams`)
- `kafka_cluster_name`: Cluster created within this namespace

**Note**: The default namespace differs by provider: `strimzi` for Strimzi provider, `amq-streams` for Red Hat AMQ Streams. This variable only applies to Strimzi and Red Hat providers.

### kafka_cluster_name
Name for the Kafka cluster resource.

- **Optional**
- Environment Variable: `KAFKA_CLUSTER_NAME`
- Default Value: `maskafka`

**Purpose**: Defines the name of the Kafka custom resource that will be created. This name is used to identify the Kafka cluster and is embedded in resource names.

**When to use**:
- Use default (`maskafka`) for standard MAS deployments
- Set to custom name when deploying multiple Kafka clusters
- Use descriptive names for multi-cluster environments

**Valid values**: Valid Kubernetes resource name (lowercase alphanumeric with hyphens, e.g., `maskafka`, `kafka-prod`, `mas-kafka`)

**Impact**: This name is used throughout the Kafka deployment in resource names (services, pods, secrets). It appears in the generated KafkaCfg for MAS.

**Related variables**:
- `kafka_namespace`: Cluster created within this namespace
- Used in generated KafkaCfg when `mas_instance_id` is provided

**Note**: Choose a meaningful name as it appears in many resource names. The default `maskafka` is suitable for single-cluster MAS deployments.

### kafka_cluster_size
Predefined configuration size for the Kafka cluster.

- **Optional**
- Environment Variable: `KAFKA_CLUSTER_SIZE`
- Default Value: `small`

**Purpose**: Selects a predefined resource configuration for the Kafka cluster. Different sizes allocate different amounts of CPU, memory, and replicas for Kafka brokers and Zookeeper nodes.

**When to use**:
- Use `small` (default) for development, test, or small production environments
- Use `large` for production environments with higher throughput requirements
- Choose based on expected message volume and performance needs

**Valid values**: `small`, `large`

**Impact**: 
- `small`: Fewer resources, suitable for dev/test or small workloads
- `large`: More resources (CPU, memory, replicas) for production workloads

**Related variables**:
- `kafka_storage_size`: Storage size should align with cluster size
- `zookeeper_storage_size`: Zookeeper storage should align with cluster size

**Note**: The `small` configuration is suitable for development and testing. Production environments typically require the `large` configuration for adequate performance and reliability.

### kafka_storage_class
Storage class for Kafka broker persistent storage (must support ReadWriteOnce).

- **Optional**
- Environment Variable: `KAFKA_STORAGE_CLASS`
- Default Value: Auto-detected from available storage classes in cluster

**Purpose**: Specifies the storage class for Kafka broker persistent storage, which requires ReadWriteOnce (RWO) access mode. This is where Kafka stores message logs and data.

**When to use**:
- Leave unset for automatic detection (recommended)
- Set explicitly when you need a specific storage class
- Must be a storage class supporting RWO access mode
- Typically block-based storage for performance

**Valid values**: Any storage class name supporting ReadWriteOnce access mode

**Impact**: Kafka broker performance depends heavily on storage performance. Choose high-performance storage for production workloads. Incorrect storage class or one not supporting RWO will cause deployment to fail.

**Related variables**:
- `kafka_storage_size`: Size of storage for Kafka brokers
- `zookeeper_storage_class`: Separate storage class for Zookeeper

**Note**: Block-based storage classes typically provide better performance for Kafka (e.g., `ibmc-block-gold`, `ocs-storagecluster-ceph-rbd`). This variable only applies to Strimzi and Red Hat AMQ Streams providers.

### kafka_storage_size
Size of persistent storage for Kafka brokers.

- **Optional**
- Environment Variable: `KAFKA_STORAGE_SIZE`
- Default Value: `100Gi`

**Purpose**: Specifies the size of persistent volumes for Kafka broker storage. This is where Kafka stores all message logs and topic data.

**When to use**:
- Use default (`100Gi`) for development/test environments
- Increase significantly for production based on message volume and retention
- Plan for message throughput and retention period
- Monitor usage and expand as needed

**Valid values**: Kubernetes storage size format (e.g., `100Gi`, `500Gi`, `1Ti`, `2Ti`)

**Impact**: Insufficient storage will cause Kafka to stop accepting messages when volumes fill up. Size appropriately for your message volume and retention requirements.

**Related variables**:
- `kafka_storage_class`: Storage class for these volumes
- `kafka_cluster_size`: Larger clusters may need more storage
- Message retention settings affect storage requirements

**Note**: The default `100Gi` is suitable for small deployments only. Production environments typically require 500Gi or more depending on message volume and retention. Plan storage based on daily message volume × retention days.

### zookeeper_storage_class
Storage class for Zookeeper persistent storage (must support ReadWriteOnce).

- **Optional**
- Environment Variable: `ZOOKEEPER_STORAGE_CLASS`
- Default Value: Auto-detected from available storage classes in cluster

**Purpose**: Specifies the storage class for Zookeeper persistent storage, which requires ReadWriteOnce (RWO) access mode. Zookeeper stores cluster metadata and coordination data.

**When to use**:
- Leave unset for automatic detection (recommended)
- Set explicitly when you need a specific storage class
- Must be a storage class supporting RWO access mode
- Can be same as or different from `kafka_storage_class`

**Valid values**: Any storage class name supporting ReadWriteOnce access mode

**Impact**: Zookeeper is critical for Kafka cluster coordination. Reliable storage is essential. Incorrect storage class or one not supporting RWO will cause deployment to fail.

**Related variables**:
- `zookeeper_storage_size`: Size of storage for Zookeeper
- `kafka_storage_class`: Separate storage class for Kafka brokers

**Note**: Zookeeper storage requirements are typically much smaller than Kafka broker storage. This variable only applies to Strimzi and Red Hat AMQ Streams providers.

### zookeeper_storage_size
Size of persistent storage for Zookeeper nodes.

- **Optional**
- Environment Variable: `ZOOKEEPER_STORAGE_SIZE`
- Default Value: `10Gi`

**Purpose**: Specifies the size of persistent volumes for Zookeeper storage. Zookeeper stores cluster metadata, configuration, and coordination data.

**When to use**:
- Use default (`10Gi`) for most deployments
- Increase only for very large Kafka clusters with many topics/partitions
- Zookeeper storage needs are typically much smaller than Kafka broker storage

**Valid values**: Kubernetes storage size format (e.g., `10Gi`, `20Gi`, `50Gi`)

**Impact**: Insufficient Zookeeper storage can cause cluster coordination issues. However, Zookeeper storage requirements are typically modest.

**Related variables**:
- `zookeeper_storage_class`: Storage class for these volumes
- `kafka_storage_size`: Kafka broker storage (typically much larger)

**Note**: The default `10Gi` is sufficient for most deployments. Zookeeper storage requirements grow slowly with cluster size. Only increase if you have a very large number of topics and partitions.

### kafka_user_name
Username for MAS to authenticate with Kafka.

- **Optional**
- Environment Variable: `KAFKA_USER_NAME`
- Default Value: `masuser`

**Purpose**: Defines the Kafka user that will be created for MAS to authenticate with the Kafka cluster. This user is configured with appropriate permissions for MAS operations.

**When to use**:
- Use default (`masuser`) for standard MAS deployments
- Set to custom name when organizational policies require specific usernames
- Must be unique within the Kafka cluster

**Valid values**: Valid Kafka username string (e.g., `masuser`, `mas-kafka-user`)

**Impact**: This user is created in Kafka with necessary permissions and credentials are included in the generated KafkaCfg for MAS.

**Related variables**:
- `kafka_user_password`: Password for this user (Strimzi 0.25.0+/AMQ Streams 2.x+)
- Used in generated KafkaCfg when `mas_instance_id` is provided

**Note**: The default `masuser` is suitable for most deployments. This variable only applies to Strimzi and Red Hat AMQ Streams providers.

### kafka_user_password
Password for the Kafka user (Strimzi 0.25.0+/AMQ Streams 2.x+).

- **Optional**
- Environment Variable: `KAFKA_USER_PASSWORD`
- Default Value: Randomly generated if not specified

**Purpose**: Sets the password for the Kafka user specified in `kafka_user_name`. This password is used for SCRAM-SHA authentication.

**When to use**:
- Leave unset for automatic random password generation (recommended)
- Set explicitly when you need a specific password
- Requires Strimzi operator 0.25.0+ or AMQ Streams 2.x+

**Valid values**: Strong password string meeting security requirements

**Impact**: This password is stored in Kafka secrets and included in the generated KafkaCfg for MAS. If not set, a secure random password is generated automatically.

**Related variables**:
- `kafka_user_name`: User for which this password is set
- Used in generated KafkaCfg when `mas_instance_id` is provided

**Note**: Automatic password generation is recommended for security. This feature requires Strimzi operator version [0.25.0](https://github.com/strimzi/strimzi-kafka-operator/blob/main/CHANGELOG.md#0250) or AMQ Streams 2.x+. Keep passwords secure and do not commit to source control.

### mas_instance_id
MAS instance ID for generating KafkaCfg configuration.

- **Optional**
- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

**Purpose**: Identifies which MAS instance the generated KafkaCfg will target. When set (along with `mas_config_dir`), the role generates a KafkaCfg resource for configuring MAS to use this Kafka cluster.

**When to use**:
- Set when you want to generate MAS configuration automatically
- Must match the instance ID of your MAS installation
- Required together with `mas_config_dir` for KafkaCfg generation

**Valid values**: Lowercase alphanumeric string, 3-12 characters (e.g., `prod`, `dev`, `inst1`)

**Impact**: When set with `mas_config_dir`, generates a KafkaCfg YAML file that can be applied to configure MAS. Without this, no MAS configuration is generated.

**Related variables**:
- `mas_config_dir`: Required together with this for KafkaCfg generation
- Generated KafkaCfg targets this MAS instance

**Note**: If either `mas_instance_id` or `mas_config_dir` is not set, the role will not generate a KafkaCfg template. You'll need to configure MAS manually.

### mas_config_dir
Local directory path where generated KafkaCfg will be saved.

- **Optional**
- Environment Variable: `MAS_CONFIG_DIR`
- Default Value: None

**Purpose**: Specifies where to save the generated KafkaCfg YAML file. This file can be manually applied to configure MAS or used with the suite_config role for automated configuration.

**When to use**:
- Set when you want to generate MAS configuration automatically
- Use the same directory across all MAS setup roles for consistency
- Required together with `mas_instance_id` for KafkaCfg generation

**Valid values**: Any valid local filesystem path (e.g., `/home/user/masconfig`, `~/masconfig`, `./config`)

**Impact**: When set with `mas_instance_id`, generates `kafkacfg-{provider}-system.yaml` in this directory. The file can be applied with `oc apply` or used with suite_config role.

**Related variables**:
- `mas_instance_id`: Required together with this for KafkaCfg generation
- `kafka_provider`: Affects the generated filename

**Note**: If either `mas_instance_id` or `mas_config_dir` is not set, no KafkaCfg template is generated. Ensure the directory exists and is writable.

### custom_labels
Comma-separated list of key=value labels to apply to Kafka resources.

- **Optional**
- Environment Variable: `CUSTOM_LABELS`
- Default Value: None

**Purpose**: Adds Kubernetes labels to Kafka-related resources for organization, selection, and filtering. Labels enable resource tracking, cost allocation, and custom automation.

**When to use**:
- Use to add organizational metadata (e.g., `cost-center=engineering`, `environment=production`)
- Use to enable resource tracking and cost allocation
- Use to support custom automation or monitoring tools
- Use to comply with organizational labeling standards

**Valid values**: Comma-separated list of `key=value` pairs (e.g., `env=prod,team=platform,component=kafka`)

**Impact**: Labels are applied to Kafka-related resources and can be used for filtering with `oc get` commands, monitoring queries, and automation scripts. Labels do not affect Kafka functionality.

**Related variables**: Works alongside Kubernetes resource labels for comprehensive resource management.

**Note**: This variable applies to Strimzi and Red Hat AMQ Streams providers. Labels help with resource organization and are especially useful in multi-tenant environments.

IBM Cloud Evenstreams Role Variables

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


## Example Playbook

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

### AWS MSK Variables

## Prerequisites
To run this role successfully you must have already installed the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).
Also, you need to have AWS user credentials configured via `aws configure` command or simply export `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables with your corresponding AWS username credentials prior running this role.

### kafka_version
The version of Kafka to deploy for AWS MSK.

- Environment Variable: `KAFKA_VERSION`
- Default Value: `3.3.1`

### kafka_cluster_name
The name of the Kafka cluster that will be created

- Required
- Environment Variable: `KAFKA_CLUSTER_NAME`
- Default Value: `maskafka`

### aws_region

- Required
- Environment Variable: `AWS_REGION`
- Default Value: None

### vpc_id
The AWS Virtual Private Cloud identifier (VPC ID) where the MSK instance will be hosted.

- Required
- Environment Variable: `VPC_ID`
- Default Value: None

### aws_msk_cidr_az1
The CIDR address for the first Availability Zone subnet. This information is found in the subnet details under your VPC.

- Required
- Environment Variable: `AWS_MSK_CIDR_AZ1`
- Default Value: None

### aws_msk_cidr_az2
The CIDR address for the second Availability Zone subnet. This information is found in the subnet details under your VPC.

- Required
- Environment Variable: `AWS_MSK_CIDR_AZ2`
- Default Value: None

### aws_msk_cidr_az3
The CIDR address for the third Availability Zone subnet. This information is found in the subnet details under your VPC.

- Required
- Environment Variable: `AWS_MSK_CIDR_AZ3`
- Default Value: None

### aws_msk_ingress_cidr
The IPv4 CIDR address for ingress connection. This information is found in the subnet details under your VPC.

- Required
- Environment Variable: `AWS_MSK_INGRESS_CIDR`
- Default Value: None

### aws_msk_egress_cidr
The IPv4 CIDR address for egress connection. This information is found in the subnet details under your VPC.

- Required
- Environment Variable: `AWS_MSK_EGRESS_CIDR`
- Default Value: None

### aws_kafka_user_name
The name of the user to setup in the cluster for MAS.

- Required
- Environment Variable: `AWS_KAFKA_USER_NAME`
- Default Value: None

### aws_kafka_user_password
The password of the user to setup in the cluster for MAS.

- Optional
- Environment Variable: `AWS_KAFKA_USER_PASSWORD`
- Default Value: None

### aws_msk_instance_type
The type/flavor of your MSK instance.

- Optional
- Environment Variable: `AWS_MSK_INSTANCE_TYPE`
- Default Value: `kafka.m5.large`

### aws_msk_volume_size
The storage/volume size of your MSK instance.

- Optional
- Environment Variable: `AWS_MSK_VOLUME_SIZE`
- Default Value: `100`

### aws_msk_instance_number
The number of broker/instances of your MSK instance.

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

### aws_msk_secret
AWS MSK Secret name. The secret name must begin with the prefix AmazonMSK_. If this is not set, then default secret name will be AmazonMSK_SECRET_{{kafka_cluster_name}}

- Optional
- Environment Variable: `AWS_MSK_SECRET`
- Default Value: `AmazonMSK_SECRET_{{kafka_cluster_name}}'`

### Install AWS MSK

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    aws_region: ca-central-1
    aws_access_key_id: *****
    aws_secret_access_key: *****
    kafka_version: 3.3.1
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

### Uninstall AWS MSK

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

## Run Role Playbook

```bash
export KAFKA_STORAGE_CLASS=ibmc-block-gold
export MAS_INSTANCE_ID=masinst1
export MAS_CONFIG_DIR=~/masconfig
ansible-playbook ibm.mas_devops.run_role
```

## License

EPL-2.0
