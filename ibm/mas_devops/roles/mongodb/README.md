mongodb
===============================================================================

[MongoDb CE operator](https://github.com/mongodb/mongodb-kubernetes-operator) will be installed into the specified namespace, a 3 node cluster cluster will be created.  The cluster will bind six PVCs, these provide persistence for the data and system logs across the three nodes.  Currently there is no support built-in for customizing the cluster beyond this configuration.

!!! tip
    The role will generate a yaml file containing the definition of a Secret and MongoCfg resource that can be used to configure the deployed instance as the MAS system MongoDb.

    This file can be directly applied using `oc apply -f $MAS_CONFIG_DIR/mongocfg-mongoce-system.yaml` or used in conjunction with the [suite_config](suite_config.md) role.


Role Variables
-------------------------------------------------------------------------------
### mongodb_action
Inform the role whether to perform an install or uninstall of MongoDb.

- Optional
- Environment Variable: `MONGODB_ACTION`
- Default: `install`

### mongodb_ce_version
Set the version of the MongoDb Community Edition Operator to install in the namespace.

- Optional
- Environment Variable: `MONGODB_CE_VERSION`
- Default: `0.7.0`


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
The CPU limits on the mongodb container.

- Environment Variable: `MONGODB_CPU_LIMITS`
- Default Value: `1`

### mongodb_mem_limits
The Memory limits on the mongodb container.

- Environment Variable: `MONGODB_MEM_LIMITS`
- Default Value: `1Gi`

### mongodb_cpu_requests
The CPU requests on the mongodb container.

- Environment Variable: `MONGODB_CPU_REQUESTS`
- Default Value: `500m`

### mongodb_mem_requests
The Memory requests on the mongodb container.

- Environment Variable: `MONGODB_MEM_REQUESTS`
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

### custom_labels
List of comma separated key=value pairs for setting custom labels on instance specific resources.

- Optional
- Environment Variable: `CUSTOM_LABELS`
- Default Value: None


Example Playbook
-------------------------------------------------------------------------------

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

!!! warning
    If the MongoDB CA Certificate expires the MongoDB replica set will become unusable. Replica set members will not be able to communicate with each other and client applications (i.e. Maximo Application Suite components) will not be to connect.

CA Certificate Renewal
-------------------------------------------------------------------------------

In order to renew the CA Certificate used by the MongoDB replica set the following steps must be taken:

- Delete the CA Certificate resource
- Delete the MongoDB server Certificate resource
- Delete the Secrets resources associated with both the CA Certificate and Server Certificate
- Delete the Secret resource which contains the MongoDB configuration parameters
- Delete the ConfigMap resources which contains the CA certificate
- Delete the Secret resource which contains the sever certificate and private key

The following steps illustrate the process required to renew the CA Certificate, sever certificate and reconfigure the MongoDB replica set with the new CA and server certificates.

The first step is to stop the Mongo replica set and MongoDb CE Operator pod.

```bash
#!/bin/bash

oc project mongoce

oc delete deployment mongodb-kubernetes-operator
oc delete statefulset mas-mongo-ce
```
Make sure all pods in the `mongoce` namespace have terminated and then execute the following to remove
the old Mongo configuration:

```bash
oc delete certificate mongo-ca-crt
oc delete certificate mongo-server
oc delete secret mongo-ca-secret
oc delete secret mongo-server-cert

oc delete secret mas-mongo-ce-config
oc delete configmap  mas-mongo-ce-cert-map
oc delete secret mas-mongo-ce-server-certificate-key

export ROLE_NAME=mongodb
ansible-playbook ibm.mas_devops.run_role
```

Once the `mongodb` role has completed the MongoDb CE Operator pod and Mongo replica set should be configured.

After the CA and server Certificates have been renewed you must ensure that that MongoCfg Suite CR is updated with the new CA Certificate. First obtain the CA Certificate from the Secret resource `mongo-ca-secret`. Then edit the Suite MongoCfg CR in the Maximo Application Suite core namespace. This is done by updating the appropriate certificate under `.spec.certificates` in the MongoCfg CR:

```yaml
  spec:
    certificates:
    - alias: ca
      crt: |
        -----BEGIN CERTIFICATE-----

        -----END CERTIFICATE-----

```

If an IBM Suite Licensing Service (SLS) is also connecting to the MongoDB replica set the LicenseService CR must also be updated to reflect the new MongoDB CA. This can be added to the `.spec.mongo.certificates` section of the LicenseService CR.

```yaml
    mongo:
      certificates:
      - alias: mongoca
        crt: |
          -----BEGIN CERTIFICATE-----

          -----END CERTIFICATE-----
```

Once the CA certificate has been updated for the MongoCfg and LicenseService CRs several pods in the core and SLS namespaces might need to be restarted to pick up the changes. This would include but is not limited to coreidp, coreapi, api-licensing.

License
-------------------------------------------------------------------------------

EPL-2.0
