mongodb
===============================================================================

This role currently supports provisioning of mongodb in three different providers:
 - community
 - aws (documentdb)
 - ibm


If selected provider is `community` [MongoDb CE operator](https://github.com/mongodb/mongodb-kubernetes-operator) will be installed into the specified namespace, a 3 node cluster cluster will be created.  The cluster will bind six PVCs, these provide persistence for the data and system logs across the three nodes.  Currently there is no support built-in for customizing the cluster beyond this configuration.

!!! tip
    The role will generate a yaml file containing the definition of a Secret and MongoCfg resource that can be used to configure the deployed instance as the MAS system MongoDb.

    This file can be directly applied using `oc apply -f $MAS_CONFIG_DIR/mongocfg-mongoce-system.yaml` or used in conjunction with the [suite_config](suite_config.md) role.

## Prerequisites
To run this role with providers as `ibm` or `aws` you must have already installed the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).
Also, you need to have AWS user credentials configured via `aws configure` command or simply export `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables with your corresponding AWS username credentials prior running this role when provider is either `ibm` or `aws`.

Common Role Variables for all providers 
----------------------------------------
### mas_instance_id
The instance ID of Maximo Application Suite that the MongoCfg configuration will target.  If this or `mas_config_dir` are not set then the role will not generate a MongoCfg template.

- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### mas_config_dir
Local directory to save the generated MongoCfg resource definition.  This can be used to manually configure a MAS instance to connect to the Mongo cluster, or used as an input to the [suite_config](suite_config.md) role. If this or `mas_instance_id` are not set then the role will not generate a MongoCfg template.

- Environment Variable: `MAS_CONFIG_DIR`
- Default Value: None

### mongodb_provider
MongoDB provider 

- Environment variable: `MONGODB_PROVIDER`
- Defult Value: `community`
- Supported providers: `community`,`aws`,`ibm`

### mongodb_action
Determines which action needs to be performed w.r.t mongodb for a specfied `provider`

- Environment variable: `MONGODB_ACTION`
- Default Value: `install`
  ```
  Following Providers supports below mentioned MONGODB_ACTION values:
  1. Provider : community 
  Supported MONGODB_ACTION values : install,uninstall
  2. Provider: aws
  Supported MONGODB_ACTION values : install,uninstall,docdb_secret_rotate
  3. Provider: ibm
  Supported MONGODB_ACTION values : install,uninstall,backup,restore,create-mongo-service-credentials
  ```
 

Community MongoDB Role Variables
---------------------------------
Role Variables
-------------------------------------------------------------------------------

### mongodb_ce_version
Set the version of the MongoDb Community Edition Operator to install in the namespace. Supported options are `0.7.0`, `0.7.8` and `0.7.9`. Selecting `0.7.0` will deploy the MongoDb version of `4.2.23`, deploying `0.7.8` or `0.7.9` will result in MongoDb version `4.4.21` being used. Upgrading upwards with these versions is supported, so if you previously deployed using `0.7.0` you can run this role again with the `0.7.9` option (which is also the default) and the MongoDb Community Edition Operator will be upgraded as well as the underlying MongoDb replicaset without lose of service.

- Optional
- Environment Variable: `MONGODB_CE_VERSION`
- Default: `0.7.9`


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

IBM Cloud MongoDB Role Variables
----------------------------------
### ibm_mongo_name
Required. IBM Cloud Mongo database instance name.

- Environment Variable: `IBM_MONGO_NAME`
- Default Value: `mongo-${MAS_INSTANCE_ID}`

### ibm_mongo_admin_password
Optional. Sets IBM Cloud Mongo database administrator user password.
If not set, an auto-generated 20 character length string will be used.

- Environment Variable: `IBM_MONGO_ADMIN_PASSWORD`
- Default Value: None.

### ibm_mongo_admin_credentials_secret_name
Secret for MongoDB Admin credentials.

- Secret Name: `<mongo-name>-admin-credentials`

### ibm_mongo_service_credentials_secret_name
Secret for MongoDB Service credentials.

- Secret Name: `<mongo-name>-service-credentials`

### ibm_mongo_resourcegroup
Required.IBM Cloud Resource Group under which resource group will be created.

- Environment Variable: `IBM_MONGO_RESOURCEGROUP`
- Default Value: `Default`

### ibm_mongo_region
Required.IBM Cloud region where MongoDB resources will be created.

- Environment Variable: `IBM_MONGO_REGION`
- Default Value: `us-east`

### ibmcloud_apikey
Required.IBM Cloud API Key.

- Environment Variable: `IBMCLOUD_APIKEY`

### ibm_mongo_plan
Plan name for this IBMCloud Service.

- Environment Variable: `IBM_MONGO_PLAN`
- Default Value: `standard`

### ibm_mongo_service
IBMCloud Offering name for MongoDB Database

- Value: `databases-for-mongodb`


### ibm_mongo_service_endpoints
MongoDB Service Endpoints type can be either public or private

- Environment Variable: `IBM_MONGO_SERVICE_ENDPOINTS`
- Default Value: `public`

### ibm_mongo_version
Specify MongoDB version to be deployed

- Environment Variable: `IBM_MONGO_VERSION`
- Default Value: `4.2`

### ibm_mongo_memory
Specify MongoDB Memory size

- Environment Variable: `IBM_MONGO_MEMORY`
- Default Value: `3840`

### ibm_mongo_disk
Specify MongoDB Disk size

- Environment Variable: `IBM_MONGO_DISK`
- Default Value: `30720`

### ibm_mongo_cpu
Specify MongoDB CPU

- Environment Variable: `IBM_MONGO_CPU`
- Default Value: `0`

### ibm_mongo_name
Resource Name in IBMCloud for MongoDB

- Value: `mongo-{{mas_instance_id}}`

### ibm_mongo_backup_id
Required only if `is_restore` is `True` CRN ID for backup resource

- Environment Variable: `IBM_MONGO_BACKUP_ID`
- Default Value: ``

### is_restore
Whether want to restore from an existing backup resource or not.

- Environment Variable: `IS_RESTORE`
- Default Value: `false`

### restored_mongodb_service_name
Required only If `is_restore` is `True`.MongoDB Service Name

- Environment Variable: `RESTORED_MONGODB_SERVICE_NAME`

Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_config_dir: ~/masconfig
    mongodb_provider: ibm
    ibmcloud_apikey: apikey****
    ibmcloud_resource_group: mas-test
  roles:
    - ibm.mas_devops.mongodb
```

AWS DocumentDB Role Variables
----------------------------------

### aws_access_key_id
Required.AWS Account Access Key Id

- Environment Variable: `AWS_ACCESS_KEY_ID`

### aws_secret_access_key
Required.AWS Account Secret Access Key

- Environment Variable: `AWS_SECRET_ACCESS_KEY`

### aws_region
Required.AWS Region where DocumentDB and other resources will be created

- Environment Variable: `AWS_REGION`
- Default Value: `us-east-2`

### vpc_id
Required.AWS VPC ID under which documentdb,subnets and security group will be created

- Environment Variable: `VPC_ID`

### docdb_cluster_name
Required.DocumentDB Cluster Name

- Environment Variable: `DOCDB_CLUSTER_NAME`

### docdb_subnet_group_name
DocumentDB Subnet Group Name

- Value: `docdb-{{ docdb_cluster_name }}`

### docdb_security_group_name
DocumentDB Security Group Name

- Value: `docdb-{{ docdb_cluster_name }}`

### docdb_admin_credentials_secret_name
DocumentDB Admin Credentials Secret Name

- Value: `{{ docdb_cluster_name }}-admin-credentials`

### docdb_engine_version
DocumentDB Engine version

- Environment variable: `DOCDB_ENGINE_VERSION`
- Default Value: `4.0.0`

### docdb_master_username
DocumentDB master username

- Environment variable: `DOCDB_MASTER_USERNAME`
- Default Value: `docdbadmin`

### docdb_instance_class
DocumentDB Instance Class

- Environment variable: `DOCDB_INSTANCE_CLASS`
- Default Value: `db.t3.medium`

### docdb_instance_number
Number of instances required for DocumentDB

- Environment variable: `DOCDB_INSTANCE_NUMBER`
- Default Value: `3`

### docdb_instance_identifier_prefix
Prefix for DocumentDB Instance name

- Environment variable: `DOCDB_INSTANCE_IDENTIFIER_PREFIX`

### docdb_ingress_cidr
Required. IPv4 Address from which incoming connection requests will be allowed to DocumentDB cluster
e.g Provide IPv4 CIDR address of VPC where ROSA cluster is installed

- Environment variable: `DOCDB_INGRESS_CIDR`


### docdb_egress_cidr
Required. IPv4 Address at which outgoing connection requests will be allowed to DocumentDB cluster
e.g Provide IPv4 CIDR address of VPC where ROSA cluster is installed

- Environment variable: `DOCDB_EGRESS_CIDR`

Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_config_dir: ~/masconfig
    mongodb_provider: aws
    mongodb_action: provision
    docdb_size: ~/docdb-config.yml
    docdb_cluster_name: test-db
    docdb_ingress_cidr: 10.0.0.0/16
    docdb_egress_cidr: 10.0.0.0/16
    docdb_instance_identifier_prefix: test-db-instance
    vpc_id: test-vpc-id
    aws_access_key_id: aws-key
    aws_secret_access_key: aws-access-key

  roles:
    - ibm.mas_devops.mongodb
```

AWS DocumentDB Secret Rotate role Variables
----------------------------------
### docdb_mongo_instance_name
Required. DocumentDB Instance Name

- Environment variable: `DOCDB_MONGO_INSTANCE_NAME`

### docdb_host
Required. Any one Host Address out of multiple documentDB Instances

- Environment variable: `DOCDB_HOST`

### docdb_port
Required. Corresponding port address of DocumentDB Instance Host

- Environment variable: `DOCDB_PORT`

### docdb_instance_username
Required. Specify username for which password is being changed

- Environment variable: `DOCDB_INSTANCE_USERNAME`

### docdb_instance_password_old
Required. Specify the old user password

- Environment variable: `DOCDB_PASSWORD_OLD`

### docdb_master_password
Required. DocumentDB Master Username

- Environment variable: `DOCDB_MASTER_PASSWORD`

### docdb_master_username
Required. DocumentDB Master Password

- Environment variable: `DOCDB_MASTER_USERNAME`


Example Playbook
----------------
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_config_dir: ~/masconfig
    mongodb_provider: aws
    mongodb_action: docdb_secret_rotate
    docdb_mongo_instance_name: test-db-instance
    db_host: aws.test1.host7283-*****
    db_port: 27017
    docdb_master_username: admin
    docdb_master_password: pass***
    docdb_instance_password_old: oldpass****
    docdb_instance_username: testuser
    aws_access_key_id: aws-key
    aws_secret_access_key: aws-access-key

  roles:
    - ibm.mas_devops.mongodb
```


License
-------------------------------------------------------------------------------

EPL-2.0
