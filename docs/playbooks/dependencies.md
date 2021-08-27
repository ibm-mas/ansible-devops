# Depedencies Playbooks

## Install AMQ Streams

### Required environment variables
- `KAFKA_STORAGE_CLASS` sets the storage class to use for both Kafka and Zookeeper
- `MAS_INSTANCE_ID` sets the instance ID of the MAS install that we are configuring

### Optional environment variables
- `KAFKA_NAMESPACE` overrides the Kubernetes namespace where the AMQ streams operator will be installed, this will default to `amq-streams`
- `KAFKA_CLUSER_NAME` overrides the name Kafka cluster, this will default `maskafka`
- `KAFKA_CLUSTER_SIZE` provides a choice between a small and large cluster configuration, this will default to `small`
- `KAFKA_USER_NAME` configures the user that will be created for MAS, will default to `masuser`


### Example usage
AMQ Streams operator will be installed into the `amq-streams` namespace, a cluster named `maskafka` will be created using the small configuration and `ibmc-block-gold` as the storage class.

```bash
export KAFKA_STORAGE_CLASS=ibmc-block-gold
export MAS_INSTANCE_ID=masdev1

ansible-playbook playbooks/dependencies/install-amqstreams.yml
```

!!! tip
    The playbook will generate a yaml file containing the definition of a Secret and KafkaCfg resource that can be used to configure the deployed cluster as the MAS system Kafka.

    This file can be directly applied using `oc apply -f /tmp/kafkacfg-amqstreams-system.yaml` or added to the `mas_config` list variable used by the `ibm.mas_devops.suite_install` role to deploy and configure MAS.

## Install MongoDb (CE)

### Required environment variables
- `MAS_INSTANCE_ID` sets the instance ID of the MAS install that we are configuring

### Optional environment variables
- `MONGODB_NAMESPACE` overrides the Kubernetes namespace where the MongoDb CE operator will be installed, this will default to `mongoce`

### Example usage
MongoDb CE operator will be installed into the `mongoce` namespace, a 3 node cluster cluster will be created.  The cluster will bind six 20GB PVCs of the default storage class, these provide persistence for the data and system logs across the three nodes.

```bash
export MAS_INSTANCE_ID=masdev1

ansible-playbook playbooks/dependencies/install-mongodb-ce.yml
```

!!! tip
    The playbook will generate a yaml file containing the definition of a Secret and MongoCfg resource that can be used to configure the deployed instance as the MAS system MongoDb.

    This file can be directly applied using `oc apply -f /tmp/mongocfg-mongoce-system.yaml` or added to the `mas_config` list variable used by the `ibm.mas_devops.suite_install` role to deploy and configure MAS.
