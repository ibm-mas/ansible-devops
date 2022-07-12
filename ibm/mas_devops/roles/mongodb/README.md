mongodb
=======

[MongoDb CE operator](https://github.com/mongodb/mongodb-kubernetes-operator) will be installed into the specified namespace, a 3 node cluster cluster will be created.  The cluster will bind six PVCs, these provide persistence for the data and system logs across the three nodes.  Currently there is no support built-in for customizing the cluster beyond this configuration.

!!! tip
    The role will generate a yaml file containing the definition of a Secret and MongoCfg resource that can be used to configure the deployed instance as the MAS system MongoDb.

    This file can be directly applied using `oc apply -f $MAS_CONFIG_DIR/mongocfg-mongoce-system.yaml` or used in conjunction with the [suite_config](suite_config.md) role.



Role Variables
--------------

### mongodb_namespace
The namespace where the operator and MongoDb cluster will be deployed.

- Environment Variable: `MONGODB_NAMESPACE`
- Default Value: `mongoce`

### mongodb_storage_class
Required.  The name of the storage class to configure the MongoDb operator to use for persistent storage in the MongoDb cluster.

- Environment Variable: `MONGODB_STORAGE_CLASS`
- Default Value: None

### mongodb_storage_capacity_data
The size of the PVC that will be created for data storage in the cluster.

- Environment Variable: `MONGODB_STORAGE_CAPACITY_DATA`
- Default Value: `20Gi`

### mongodb_storage_capacity_logs
The size of the PVC that will be created for log storage in the cluster.

- Environment Variable: `MONGODB_STORAGE_CAPACITY_LOGS`
- Default Value: `20Gi`

### mongodb_cpu_limits
The CPU limits on the mongod container.

- Environment Variable: `MONGODB_CPU_LIMITS`
- Default Value: `1`

### mongodb_mem_limits
The Memory limits on the mongod container.

- Environment Variable: `MONGODB_MEM_LIMITS`
- Default Value: `1Gi`

### mongodb_replicas
The number of the mongodb replica set members. Default is 3. Set to 1 for SNO Cluster.
- Environment Variable: `MONGODB_REPLICAS`
- Default Value: `3`

### mas_instance_id
The instance ID of Maximo Application Suite that the MongoCfg configuration will target.  If this or `mas_config_dir` are not set then the role will not generate a MongoCfg template.

- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### mas_config_dir
Local directory to save the generated MongoCfg resource definition.  This can be used to manually configure a MAS instance to connect to the Mongo cluster, or used as an input to the [suite_config](suite_config.md) role. If this or `mas_instance_id` are not set then the role will not generate a MongoCfg template.

- Environment Variable: `MAS_CONFIG_DIR`
- Default Value: None


Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mongodb_storage_class: ibmc-block-gold
    mas_instance_id: masinst1
    mas_config_dir: ~/masconfig
  roles:
    - ibm.mas_devops.mongodb
```

License
-------

EPL-2.0
