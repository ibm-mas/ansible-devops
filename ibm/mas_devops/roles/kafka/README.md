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

## Prerequisites

To run this role successfully you must have already installed the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).
Also, you need to have AWS user credentials configured via `aws configure` command or simply export `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables with your corresponding AWS username credentials prior running this role.

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`kafka_action`](#kafka_action) | No | `install` |
| [`kafka_provider`](#kafka_provider) | No | `strimzi` |
| [`mas_instance_id`](#mas_instance_id) | Conditional | None |
| [`mas_config_dir`](#mas_config_dir) | Conditional | None |
| [`kafka_version`](#kafka_version) | No | Provider-specific |
| [`kafka_namespace`](#kafka_namespace) | No | Provider-specific |
| [`kafka_cluster_name`](#kafka_cluster_name) | No | `maskafka` |
| [`kafka_cluster_size`](#kafka_cluster_size) | No | `small` |
| [`kafka_storage_class`](#kafka_storage_class) | No | Auto-detected (RWO) |
| [`kafka_storage_size`](#kafka_storage_size) | No | `100Gi` |
| [`zookeeper_storage_class`](#zookeeper_storage_class) | No | Auto-detected (RWO) |
| [`zookeeper_storage_size`](#zookeeper_storage_size) | No | `10Gi` |
| [`kafka_user_name`](#kafka_user_name) | No | `masuser` |
| [`kafka_user_password`](#kafka_user_password) | No | Auto-generated |
| [`custom_labels`](#custom_labels) | No | None |
| [`ibmcloud_apikey`](#ibmcloud_apikey) | Conditional | None |
| [`eventstreams_resourcegroup`](#eventstreams_resourcegroup) | No | `Default` / `IBMCLOUD_RESOURCEGROUP` |
| [`eventstreams_name`](#eventstreams_name) | Conditional | None |
| [`eventstreams_plan`](#eventstreams_plan) | No | `standard` |
| [`eventstreams_location`](#eventstreams_location) | No | `us-east` / `IBMCLOUD_REGION` |
| [`eventstreams_retention`](#eventstreams_retention) | No | `1209600000` |
| [`eventstreams_create_manage_jms_topics`](#eventstreams_create_manage_jms_topics) | No | `True` |
| [`aws_region`](#aws_region) | Conditional | None |
| [`vpc_id`](#vpc_id) | Conditional | None |
| [`aws_msk_cidr_az1`](#aws_msk_cidr_az1) | Conditional | None |
| [`aws_msk_cidr_az2`](#aws_msk_cidr_az2) | Conditional | None |
| [`aws_msk_cidr_az3`](#aws_msk_cidr_az3) | Conditional | None |
| [`aws_msk_ingress_cidr`](#aws_msk_ingress_cidr) | Conditional | None |
| [`aws_msk_egress_cidr`](#aws_msk_egress_cidr) | Conditional | None |
| [`aws_kafka_user_name`](#aws_kafka_user_name) | Conditional | None |
| [`aws_kafka_user_password`](#aws_kafka_user_password) | No | None |
| [`aws_msk_instance_type`](#aws_msk_instance_type) | No | `kafka.m5.large` |
| [`aws_msk_volume_size`](#aws_msk_volume_size) | No | `100` |
| [`aws_msk_instance_number`](#aws_msk_instance_number) | No | `3` |
| [`aws_msk_secret`](#aws_msk_secret) | No | `AmazonMSK_SECRET_{{kafka_cluster_name}}` |

`mas_instance_id` and `mas_config_dir` are required together to generate the MAS KafkaCfg configuration. The IBM Event Streams variables marked conditional are required when `kafka_provider` is `ibm`, and the AWS MSK variables marked conditional are required when `kafka_provider` is `aws`.

### Actions and Providers

#### kafka_action

Specifies which operation to perform on the Kafka cluster — `install`, `upgrade`, or `uninstall`.

- **Optional**
- Environment Variable: `KAFKA_ACTION`
- Default: `install`

`install` deploys the Kafka operator and creates the cluster, `upgrade` upgrades an existing Kafka cluster, and `uninstall` removes the Kafka cluster and operator. The `upgrade` action is only available for the `strimzi` and `redhat` providers — IBM Event Streams and AWS MSK do not support in-place upgrades through this role. When upgrading, `kafka_version` defines the target version.

#### kafka_allow_rollback
Enables automatic operator rollback during ZooKeeper to KRaft migration (Red Hat AMQ Streams only).

- **Optional**
- Environment Variable: `KAFKA_ALLOW_ROLLBACK`
- Default Value: `false`

**Purpose**: Enables automatic operator rollback when upgrading a ZooKeeper-based Kafka cluster with a KRaft-only (3.x) operator. This is required because AMQ Streams 3.x operators cannot manage ZooKeeper clusters or perform migrations.

**When to use**:
- **Required** when you have a 3.x operator and a ZooKeeper-based cluster
- Use when the operator auto-upgraded to 3.x before migration completed
- Not needed for 2.x operators (they support both ZooKeeper and KRaft)
- Not needed if cluster is already in KRaft mode

**Valid values**: `true`, `false`

**Impact**:
- `false` (default): Upgrade fails with helpful error message if 3.x operator + ZooKeeper cluster detected
- `true`: Automatically performs three-phase upgrade:
  1. Rollback operator from 3.x to 2.9.x (migration-compatible)
  2. Migrate cluster from ZooKeeper to KRaft
  3. Upgrade operator back to 3.x
  4. Update Kafka version to 4.1.0 (3.x operator requirement)

**Related variables**:
- `kafka_action`: Must be set to `upgrade`
- `kafka_provider`: Only applies to `redhat` provider (uses OLM)
- `kafka_version`: Automatically updated to 4.1.0 after operator upgrade

**Example scenarios**:

**Scenario 1: 3.x Operator + ZooKeeper Cluster (Stuck State)**
```bash
# Without rollback - fails with instructions
KAFKA_ACTION=upgrade
# Error: "AMQ Streams 3.x operators do NOT support ZooKeeper clusters"

# With rollback - automatic migration
KAFKA_ALLOW_ROLLBACK=true KAFKA_ACTION=upgrade
# Success: Rollback → Migrate → Upgrade → Update version
```

**Scenario 2: 2.x Operator + ZooKeeper Cluster**
```bash
# Rollback not needed - 2.x supports migration
KAFKA_ACTION=upgrade
# Success: Migrate to KRaft (operator stays on 2.x)
```

**Scenario 3: Any Operator + KRaft Cluster**
```bash
# Rollback not needed - already in KRaft mode
KAFKA_ACTION=upgrade
# Success: Standard operator upgrade
```

**Technical details**:
- Uses OLM (Operator Lifecycle Manager) to manage operator versions
- Stores original channel for restoration after migration
- Validates cluster remains in KRaft mode throughout process
- Automatically cleans up deprecated ZooKeeper-specific fields

**Note**: This feature is **Red Hat AMQ Streams only** because it requires OLM for operator version management. Strimzi community operator doesn't use OLM, so users must manually manage operator versions. The three-phase upgrade process ensures safe migration even when the operator has auto-upgraded to a KRaft-only version.

#### kafka_provider

Specifies which Kafka provider to use for deployment — `strimzi`, `redhat`, `ibm`, or `aws`.

- **Optional**
- Environment Variable: `KAFKA_PROVIDER`
- Default: `strimzi`

`strimzi` (default, recommended) deploys open-source Kafka on OpenShift using the Strimzi operator with no additional license, `redhat` deploys AMQ Streams (requires a separate Red Hat AMQ license not included with MAS), `ibm` provisions IBM Event Streams in IBM Cloud (managed service, requires an IBM Cloud account and incurs costs), and `aws` provisions AWS MSK in your AWS account (managed service, requires an AWS account and incurs costs). Different providers require different additional variables, and `kafka_action=upgrade` is only supported for `strimzi` and `redhat`.

!!! important
    The MAS license does not include entitlement for Red Hat AMQ Streams — Strimzi is recommended for open-source Kafka.

### MAS Configuration Generation

#### mas_instance_id

MAS instance ID for generating the KafkaCfg configuration — a lowercase alphanumeric string of 3-12 characters (e.g., `prod`, `dev`, `inst1`).

- **Optional** — required together with `mas_config_dir` for KafkaCfg generation
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

Must match the instance ID of your MAS installation. When set along with `mas_config_dir`, the role generates a KafkaCfg YAML file targeting this MAS instance; if either variable is not set, no KafkaCfg template is generated and you will need to configure MAS manually.

#### mas_config_dir

Local directory path where the generated KafkaCfg will be saved — any valid local filesystem path (e.g., `/home/user/masconfig`, `~/masconfig`, `./config`).

- **Optional** — required together with `mas_instance_id` for KafkaCfg generation
- Environment Variable: `MAS_CONFIG_DIR`
- Default: None

When set with `mas_instance_id`, generates `kafkacfg-{provider}-system.yaml` in this directory; the file can be applied with `oc apply` or used with the suite_config role. Use the same directory across all MAS setup roles for consistency, and ensure the directory exists and is writable. If either `mas_instance_id` or `mas_config_dir` is not set, no KafkaCfg template is generated.

### Red Hat AMQ Streams & Strimzi Variables

#### kafka_version

Kafka version to deploy — a valid Kafka version supported by the operator (e.g., `3.8.0`, `3.9.0`).

- **Optional**
- Environment Variable: `KAFKA_VERSION`
- Default: `3.9.0` for Strimzi, `3.8.0` for Red Hat AMQ Streams, `3.3.1` for AWS MSK

For Strimzi, the supported versions for strimzi-cluster-operator.v0.45.0 are `3.8.0`, `3.8.1`, and `3.9.0`. Before changing this value, verify the version is supported by your [AMQ Streams operator](https://access.redhat.com/documentation/en-us/red_hat_amq_streams) or [Strimzi operator](https://strimzi.io/downloads/) — incompatible versions will cause deployment failures. This variable only applies to the Strimzi, Red Hat AMQ Streams, and AWS MSK providers, not IBM Event Streams.

#### kafka_namespace

OpenShift namespace where the Kafka operator and cluster will be deployed — any valid Kubernetes namespace name (e.g., `strimzi`, `amq-streams`, `kafka-prod`).

- **Optional**
- Environment Variable: `KAFKA_NAMESPACE`
- Default: `strimzi` for the Strimzi provider, `amq-streams` for Red Hat AMQ Streams

All Kafka resources (operator, cluster, topics, users) are created in this namespace. Use the default for standard single-cluster deployments, and set a custom namespace (unique per cluster) when organizing multiple Kafka deployments. This variable only applies to the Strimzi and Red Hat providers.

#### kafka_cluster_name

Name for the Kafka cluster resource — a valid Kubernetes resource name (lowercase alphanumeric with hyphens, e.g., `maskafka`, `kafka-prod`, `mas-kafka`).

- **Optional**
- Environment Variable: `KAFKA_CLUSTER_NAME`
- Default: `maskafka`

This name is used throughout the Kafka deployment in resource names (services, pods, secrets) and appears in the generated KafkaCfg for MAS. For AWS MSK it is also used in the generated AWS resource names (security group, cluster configuration, KMS key, and secret). Choose a meaningful name — the default `maskafka` is suitable for single-cluster MAS deployments.

#### kafka_cluster_size

Predefined configuration size for the Kafka cluster — `small` or `large`.

- **Optional**
- Environment Variable: `KAFKA_CLUSTER_SIZE`
- Default: `small`

`small` allocates fewer resources, suitable for development, test, or small workloads; `large` allocates more resources (CPU, memory, replicas) for production workloads with higher throughput requirements. `kafka_storage_size` and `zookeeper_storage_size` should align with the cluster size — production environments typically require the `large` configuration for adequate performance and reliability.

#### kafka_storage_class

Storage class for Kafka broker persistent storage, where Kafka stores message logs and data — any storage class name supporting ReadWriteOnce (RWO) access mode.

- **Optional**
- Environment Variable: `KAFKA_STORAGE_CLASS`
- Default: Auto-detected from available storage classes in the cluster

Leave unset for automatic detection (recommended), or set explicitly when you need a specific storage class. Kafka broker performance depends heavily on storage performance — block-based storage classes (e.g., `ibmc-block-gold`, `ocs-storagecluster-ceph-rbd`) typically provide better performance and are recommended for production workloads. A storage class that does not support RWO will cause the deployment to fail. This variable only applies to the Strimzi and Red Hat AMQ Streams providers.

#### kafka_storage_size

Size of persistent storage for Kafka brokers, where Kafka stores all message logs and topic data — Kubernetes storage size format (e.g., `100Gi`, `500Gi`, `1Ti`, `2Ti`).

- **Optional**
- Environment Variable: `KAFKA_STORAGE_SIZE`
- Default: `100Gi`

The default is suitable for small deployments only — production environments typically require 500Gi or more depending on message volume and retention (plan storage based on daily message volume × retention days). Insufficient storage will cause Kafka to stop accepting messages when volumes fill up; monitor usage and expand as needed.

#### zookeeper_storage_class

Storage class for Zookeeper persistent storage, where Zookeeper stores cluster metadata and coordination data — any storage class name supporting ReadWriteOnce (RWO) access mode.

- **Optional**
- Environment Variable: `ZOOKEEPER_STORAGE_CLASS`
- Default: Auto-detected from available storage classes in the cluster

Leave unset for automatic detection (recommended), or set explicitly when you need a specific storage class — it can be the same as or different from `kafka_storage_class`. Zookeeper is critical for Kafka cluster coordination, so reliable storage is essential; a storage class that does not support RWO will cause the deployment to fail. This variable only applies to the Strimzi and Red Hat AMQ Streams providers.

#### zookeeper_storage_size

Size of persistent storage for Zookeeper nodes, which store cluster metadata, configuration, and coordination data — Kubernetes storage size format (e.g., `10Gi`, `20Gi`, `50Gi`).

- **Optional**
- Environment Variable: `ZOOKEEPER_STORAGE_SIZE`
- Default: `10Gi`

The default is sufficient for most deployments — Zookeeper storage requirements are typically much smaller than Kafka broker storage and grow slowly with cluster size. Increase only for very large Kafka clusters with a very large number of topics and partitions.

#### kafka_user_name

Username for MAS to authenticate with Kafka — a valid Kafka username string (e.g., `masuser`, `mas-kafka-user`), unique within the Kafka cluster.

- **Optional**
- Environment Variable: `KAFKA_USER_NAME`
- Default: `masuser`

This user is created in Kafka with the necessary permissions for MAS operations, and its credentials are included in the generated KafkaCfg when `mas_instance_id` is provided. Set a custom name when organizational policies require specific usernames. This variable only applies to the Strimzi and Red Hat AMQ Streams providers.

#### kafka_user_password

Password for the Kafka user, used for SCRAM-SHA authentication — a strong password string meeting security requirements.

- **Optional**
- Environment Variable: `KAFKA_USER_PASSWORD`
- Default: Randomly generated if not specified

Leave unset for automatic random password generation (recommended for security); this feature requires Strimzi operator [0.25.0](https://github.com/strimzi/strimzi-kafka-operator/blob/main/CHANGELOG.md#0250) or AMQ Streams 2.x+. The password is stored in Kafka secrets and included in the generated KafkaCfg for MAS — keep passwords secure and do not commit them to source control.

#### custom_labels

Comma-separated list of `key=value` labels to apply to Kafka resources (e.g., `env=prod,team=platform,component=kafka`).

- **Optional**
- Environment Variable: `CUSTOM_LABELS`
- Default: None

Use for organizational metadata (e.g., `cost-center=engineering`, `environment=production`), resource tracking, cost allocation, and custom automation or monitoring. Labels can be used for filtering with `oc get` commands, monitoring queries, and automation scripts, but do not affect Kafka functionality. This variable applies to the Strimzi and Red Hat AMQ Streams providers, and is especially useful in multi-tenant environments.

### IBM Event Streams Variables

#### ibmcloud_apikey

IBM Cloud API Key — must have access to manage (provision/deprovision) IBM Cloud Event Streams.

- **Required** when `kafka_provider` is `ibm`
- Environment Variable: `IBMCLOUD_APIKEY`
- Default: None

#### eventstreams_resourcegroup

IBM Cloud Resource Group to target the Event Streams instance.

- **Optional**
- Environment Variable: `EVENTSTREAMS_RESOURCEGROUP`
- Default: `Default` or the value defined by `IBMCLOUD_RESOURCEGROUP`

#### eventstreams_name

Event Streams instance name.

- **Required** when `kafka_provider` is `ibm`
- Environment Variable: `EVENTSTREAMS_NAME`
- Default: None

#### eventstreams_plan

Event Streams instance plan.

- **Optional**
- Environment Variable: `EVENTSTREAMS_PLAN`
- Default: `standard`

#### eventstreams_location

IBM Cloud location where the Event Streams instance will be provisioned.

- **Optional**
- Environment Variable: `EVENTSTREAMS_LOCATION`
- Default: `us-east` or the value defined by `IBMCLOUD_REGION`

#### eventstreams_retention

Event Streams topic retention period, in milliseconds.

- **Optional**
- Environment Variable: `EVENTSTREAMS_RETENTION`
- Default: `1209600000`

#### eventstreams_create_manage_jms_topics

Defines whether to create specific Manage application JMS topics by default.

- **Optional**
- Environment Variable: `EVENTSTREAMS_CREATE_MANAGE_JMS_TOPICS`
- Default: `True`

### AWS MSK Variables

See [`kafka_version`](#kafka_version) (default `3.3.1` for AWS MSK) and [`kafka_cluster_name`](#kafka_cluster_name) (used in the generated AWS resource names) — both apply to AWS MSK as well.

#### aws_region

AWS region where the MSK cluster will be deployed.

- **Required** when `kafka_provider` is `aws`
- Environment Variable: `AWS_REGION`
- Default: None

#### vpc_id

The AWS Virtual Private Cloud identifier (VPC ID) where the MSK instance will be hosted.

- **Required** when `kafka_provider` is `aws`
- Environment Variable: `VPC_ID`
- Default: None

#### aws_msk_cidr_az1

The CIDR address for the first Availability Zone subnet. This information is found in the subnet details under your VPC.

- **Required** when `kafka_provider` is `aws`
- Environment Variable: `AWS_MSK_CIDR_AZ1`
- Default: None

#### aws_msk_cidr_az2

The CIDR address for the second Availability Zone subnet. This information is found in the subnet details under your VPC.

- **Required** when `kafka_provider` is `aws`
- Environment Variable: `AWS_MSK_CIDR_AZ2`
- Default: None

#### aws_msk_cidr_az3

The CIDR address for the third Availability Zone subnet. This information is found in the subnet details under your VPC.

- **Required** when `kafka_provider` is `aws`
- Environment Variable: `AWS_MSK_CIDR_AZ3`
- Default: None

#### aws_msk_ingress_cidr

The IPv4 CIDR address for ingress connection. This information is found in the subnet details under your VPC.

- **Required** when `kafka_provider` is `aws`
- Environment Variable: `AWS_MSK_INGRESS_CIDR`
- Default: None

#### aws_msk_egress_cidr

The IPv4 CIDR address for egress connection. This information is found in the subnet details under your VPC.

- **Required** when `kafka_provider` is `aws`
- Environment Variable: `AWS_MSK_EGRESS_CIDR`
- Default: None

#### aws_kafka_user_name

The name of the user to setup in the cluster for MAS.

- **Required** when `kafka_provider` is `aws`
- Environment Variable: `AWS_KAFKA_USER_NAME`
- Default: None

#### aws_kafka_user_password

The password of the user to setup in the cluster for MAS.

- **Optional**
- Environment Variable: `AWS_KAFKA_USER_PASSWORD`
- Default: None

#### aws_msk_instance_type

The type/flavor of your MSK instance.

- **Optional**
- Environment Variable: `AWS_MSK_INSTANCE_TYPE`
- Default: `kafka.m5.large`

#### aws_msk_volume_size

The storage/volume size of your MSK instance.

- **Optional**
- Environment Variable: `AWS_MSK_VOLUME_SIZE`
- Default: `100`

#### aws_msk_instance_number

The number of broker/instances of your MSK instance.

- **Optional**
- Environment Variable: `AWS_MSK_INSTANCE_NUMBER`
- Default: `3`

#### aws_msk_secret

AWS MSK Secret name — the secret name must begin with the prefix `AmazonMSK_`.

- **Optional**
- Environment Variable: `AWS_MSK_SECRET`
- Default: `AmazonMSK_SECRET_{{kafka_cluster_name}}`

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
