mongodb
===============================================================================

This role currently supports provisioning of mongodb in three different providers:
 - community
 - aws (documentdb)
 - ibm

If the selected provider is `community` then the [MongoDB Community Kubernetes Operator](https://github.com/mongodb/mongodb-kubernetes-operator) will be configured and deployed into the specified namespace. By default a three member MongoDB replica set will be created.  The cluster will bind six PVCs, these provide persistence for the data and system logs across the three nodes.  Currently there is no support built-in for customizing the cluster beyond this configuration.

!!! tip
    The role will generate a yaml file containing the definition of a Secret and MongoCfg resource that can be used to configure the deployed instance as the MAS system MongoDb.

    This file can be directly applied using `oc apply -f $MAS_CONFIG_DIR/mongocfg-mongoce-system.yaml` or used in conjunction with the [suite_config](suite_config.md) role.


Prerequisites
-------------------------------------------------------------------------------
To run this role with providers as `ibm` or `aws` you must have already installed the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).
Also, you need to have AWS user credentials configured via `aws configure` command or simply export `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables with your corresponding AWS username credentials prior running this role when provider is either `ibm` or `aws`.

To run the `docdb_secret_rotate` MONGODB_ACTION when the provider is `aws` you must have already installed the [Mongo Shell](https://www.mongodb.com/docs/mongodb-shell/install/).

This role will install a GrafanaDashboard used for monitoring the MongoDB instance when the provided is `community` and you have run the [grafana role](https://ibm-mas.github.io/ansible-devops/roles/grafana/) previously. If you did not run the [grafana role](https://ibm-mas.github.io/ansible-devops/roles/grafana/) then the GrafanaDashboard won't be installed.


Role Variables - Common
-------------------------------------------------------------------------------
### mas_instance_id
The instance ID of Maximo Application Suite that the MongoCfg configuration will target.  If this or `mas_config_dir` are not set then the role will not generate a MongoCfg template.

- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### mas_config_dir
Local directory to save the generated MongoCfg resource definition.  This can be used to manually configure a MAS instance to connect to the Mongo cluster, or used as an input to the [suite_config](suite_config.md) role. If this or `mas_instance_id` are not set then the role will not generate a MongoCfg template.

- Environment Variable: `MAS_CONFIG_DIR`
- Default Value: None

### mongodb_provider
MongoDB provider, choose whether to use the MongoDb Community Edition Operator (`community`), IBM Cloud Database for MongoDb (`ibm`), or AWS DocumentDb (`aws`).

- Environment variable: `MONGODB_PROVIDER`
- Default Value: `community`


### mongodb_action
Determines which action to perform w.r.t mongodb for a specified provider:

- Environment variable: `MONGODB_ACTION`
- Default Value: `install`

Each provider supports a different set of actions:
- **community**: `install`, `uninstall`, `backup`, `restore`
- **aws**: `install`, `uninstall`, `docdb_secret_rotate`, `destroy-data`
- **ibm**: `install`, `uninstall`, `backup`, `restore`, `create-mongo-service-credentials`


Role Variables - CE Operator
-------------------------------------------------------------------------------
### mongodb_namespace
The namespace where the operator and MongoDb cluster will be deployed.

- Environment Variable: `MONGODB_NAMESPACE`
- Default Value: `mongoce`

### mongodb_version
Defines the specific mongo version to be used. Best practice would be to use the version associated with the current Maximo Application Suite catalog. However, this value can currently be overridden to 4.4.21, 5.0.21, 5.0.23, 6.0.10, 6.0.12, 7.0.12

!!! important
    It is advised to never attempt a downgrade a MongoDB instance managed by the MAS Devops Ansible Collection. Also best practices should include creating scheduled backups of any MongoDB instance.

- Optional
- Environment Variable: `MONGODB_VERSION`
- Default Value: Automatically defined by the mongo version specified in the [latest MAS case bundle available](https://github.com/ibm-mas/ansible-devops/tree/master/ibm/mas_devops/common_vars/casebundles).

### mongodb_override_spec
This forces the deploy to use the environment variables instead of maintaining spec settings for the existing installed MongoDB. By default this is False and if you upgrade or reinstall Mongo your existing settings will be preserved.

!!! important
    It is advised you check your existing Mongo installation before using this. If you do not set the environment variables to match what you have in the spec or you use defaults you may find your members, memory, and cpu reset to the default values specified in this README. Unknown settings are not preserved in the spec.

- Optional
- Environment Variable: `MONGODB_OVERRIDE_SPEC`
- Default Value: `false`

List of preserved settings

- mongodb_cpu_limits
- mongodb_mem_limits
- mongodb_cpu_requests
- mongodb_mem_requests
- mongodb_storage_class
- mongodb_storage_capacity_data
- mongodb_storage_capacity_logs
- mongodb_replicas

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

### mongodb_v5_upgrade
Set this to `true` to confirm you want to upgrade your existing Mongo instance from version 4.2 or 4.4 to version 5.

- Optional
- Environment Variable: `MONGODB_V5_UPGRADE`
- Default Value: `false`

### mongodb_v6_upgrade
Set this to `true` to confirm you want to upgrade your existing Mongo instance from version 5 to version 6.

- Optional
- Environment Variable: `MONGODB_V6_UPGRADE`
- Default Value: `false`

### mongodb_v7_upgrade
Set this to `true` to confirm you want to upgrade your existing Mongo instance from version 6 to version 7.

- Optional
- Environment Variable: `MONGODB_V7_UPGRADE`
- Default Value: `false`

### masbr_confirm_cluster
Set `true` or `false` to indicate the role whether to confirm the currently connected cluster before running the backup or restore job.

- Optional
- Environment Variable: `MASBR_CONFIRM_CLUSTER`
- Default: `false`

### masbr_copy_timeout_sec
Set the transfer files timeout in seconds.

- Optional
- Environment Variable: `MASBR_COPY_TIMEOUT_SEC`
- Default: `43200` (12 hours)

### masbr_job_timezone
Set the [time zone](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) for creating scheduled backup job. If not set a value for this variable, this role will use UTC time zone when creating a CronJob for running scheduled backup job.

- Optional
- Environment Variable: `MASBR_JOB_TIMEZONE`
- Default: None

### masbr_storage_type
Set `local` or `cloud` to indicate this role to save the backup files to local file system or cloud object storage.

- **Required**
- Environment Variable: `MASBR_STORAGE_TYPE`
- Default: None

### masbr_storage_local_folder
Set local path to save the backup files.

- **Required** only when `MASBR_STORAGE_TYPE=local`
- Environment Variable: `MASBR_STORAGE_LOCAL_FOLDER`
- Default: None

### masbr_storage_cloud_rclone_file
Set the path of `rclone.conf` file.

- **Required** only when `MASBR_STORAGE_TYPE=cloud`
- Environment Variable: `MASBR_STORAGE_CLOUD_RCLONE_FILE`
- Default: None

### masbr_storage_cloud_rclone_name
Set the configuration name defined in `rclone.conf` file.

- **Required** only when `MASBR_STORAGE_TYPE=cloud`
- Environment Variable: `MASBR_STORAGE_CLOUD_RCLONE_NAME`
- Default: None

### masbr_storage_cloud_bucket
Set the object storage bucket name for saving the backup files

- **Required** only when `MASBR_STORAGE_TYPE=cloud`
- Environment Variable: `MASBR_STORAGE_CLOUD_BUCKET`
- Default: None

### masbr_slack_enabled
Set `true` or `false` to indicate whether this role will send Slack notification messages of the backup and restore progress.  

- Optional
- Environment Variable: `MASBR_SLACK_ENABLED`
- Default: `false`

### masbr_slack_level
Set `failure`, `info` or `verbose` to indicate this role to send Slack notification messages in which backup and resore phases:

| Slack level | Backup/Restore phases                                   |
| ----------- | ------------------------------------------------------- |
| failure     | `Failed`, `PartiallyFailed`                             |
| info        | `Completed`, `Failed`, `PartiallyFailed`                |
| verbose     | `InProgress`, `Completed`, `Failed`, `PartiallyFailed`  |

- Optional
- Environment Variable: `MASBR_SLACK_LEVEL`
- Default: `info`

### masbr_slack_token
The Slack integration token.  

- **Required** only when `MASBR_SLACK_ENABLED=true`
- Environment Variable: `MASBR_SLACK_TOKEN`
- Default: None

### masbr_slack_channel
The Slack channel to send the notification messages to.

- **Required** only when `MASBR_SLACK_ENABLED=true`
- Environment Variable: `MASBR_SLACK_CHANNEL`
- Default: None

### masbr_slack_user
The sender of the Slack notification message.

- Optional
- Environment Variable: `MASBR_SLACK_USER`
- Default: `MASBR`

### masbr_backup_type
Set `full` or `incr` to indicate the role to create a full backup or incremental backup.

- Optional
- Environment Variable: `MASBR_BACKUP_TYPE`
- Default: `full`

### masbr_backup_from_version
Set the full backup version to use in the incremental backup, this will be in the format of a `YYYMMDDHHMMSS` timestamp (e.g. `20240621021316`). This variable is only valid when `MASBR_BACKUP_TYPE=incr`. If not set a value for this variable, this role will try to find the latest full backup version from the specified storage location.

- Optional
- Environment Variable: `MASBR_BACKUP_FROM_VERSION`
- Default: None

### masbr_backup_schedule
Set [Cron expression](ttps://en.wikipedia.org/wiki/Cron) to create a scheduled backup. If not set a value for this varialbe, this role will create an on-demand backup.

- Optional
- Environment Variable: `MASBR_BACKUP_SCHEDULE`
- Default: None

### masbr_restore_from_version
Set the backup version to use in the restore, this will be in the format of a `YYYMMDDHHMMSS` timestamp (e.g. `20240621021316`)

- **Required** only when `MONGODB_ACTION=restore`
- Environment Variable: `MASBR_RESTORE_FROM_VERSION`
- Default: None


Role Variables - IBM Cloud
-------------------------------------------------------------------------------
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


Role Variables - AWS DocumentDB
-------------------------------------------------------------------------------

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
Required. Prefix for DocumentDB Instance name

- Environment variable: `DOCDB_INSTANCE_IDENTIFIER_PREFIX`

### docdb_ingress_cidr
Required. IPv4 Address from which incoming connection requests will be allowed to DocumentDB cluster
e.g Provide IPv4 CIDR address of VPC where ROSA cluster is installed

- Environment variable: `DOCDB_INGRESS_CIDR`

### docdb_egress_cidr
Required. IPv4 Address at which outgoing connection requests will be allowed to DocumentDB cluster
e.g Provide IPv4 CIDR address of VPC where ROSA cluster is installed

- Environment variable: `DOCDB_EGRESS_CIDR`

### docdb_cidr_az1:

Required. Provide IPv4 CIDR address for the subnet to be created in one of the 3 availabilty zones of your VPC. If the subnet exists already then it must contain the tag of Name: {{ docdb_cluster_name }}, if the subnet doesn't exist already then one is created.

- Environment variable: `DOCDB_CIDR_AZ1`

### docdb_cidr_az2:

Required. Provide IPv4 CIDR address for the subnet to be created in one of the 3 availabilty zones of your VPC. If the subnet exists already then it must contain the tag of Name: {{ docdb_cluster_name }}, if the subnet doesn't exist already then one is created.

- Environment variable: `DOCDB_CIDR_AZ2`

### docdb_cidr_az3:

Required. Provide IPv4 CIDR address for the subnet to be created in one of the 3 availabilty zones of your VPC. If the subnet exists already then it must contain the tag of Name: {{ docdb_cluster_name }}, if the subnet doesn't exist already then one is created.

- Environment variable: `DOCDB_CIDR_AZ3`

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

AWS DocumentDB destroy-data action Variables
----------------------------------
### mas_instance_id
The specified MAS instance ID

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### mongo_username
Mongo Username

- Environment Variable: `MONGO_USERNAME`
- Default Value: None

### mongo_password
Mongo password

- Environment Variable: `MONGO_PASSWORD`
- Default Value: None

### config
Mongo Config, please refer to the below example playbook section for details

- **Required**
- Environment Variable: `CONFIG`
- Default Value: None

### certificates
Mongo Certificates, please refer to the below example playbook section for details

- **Required**
- Environment Variable: `CERTIFICATES`
- Default Value: None



Example Playbooks
-------------------------------------------------------------------------------

### Install (CE Operator)
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

### Backup (CE Operator)
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mongodb_action: backup
    mas_instance_id: masinst1
    masbr_storage_type: local
    masbr_storage_local_folder: /tmp/masbr
  roles:
    - ibm.mas_devops.mongodb
```

### Restore (CE Operator)
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mongodb_action: restore
    mas_instance_id: masinst1
    masbr_restore_from_version: 20240621021316
    masbr_storage_type: local
    masbr_storage_local_folder: /tmp/masbr
  roles:
    - ibm.mas_devops.mongodb
```

### Install (IBM Cloud)
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

### Install (AWS DocumentDB)
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
    docdb_cidr_az1: 10.0.0.0/26
    docdb_cidr_az2: 10.0.0.64/26
    docdb_cidr_az3: 10.0.0.128/26
    docdb_instance_identifier_prefix: test-db-instance
    vpc_id: test-vpc-id
    aws_access_key_id: aws-key
    aws_secret_access_key: aws-access-key

  roles:
    - ibm.mas_devops.mongodb
```

### AWS DocumentDb Secret Rotation
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

### AWS DocumentDb destroy-data action

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mongodb_provider: aws
    mongodb_action: destroy-data
    mongo_username: pqradmin
    mongo_password: xyzabc
    config:
      configDb: admin
      authMechanism: DEFAULT
      retryWrites: false
      hosts:
        - host: abc-0.pqr.databases.appdomain.cloud
          port: 32250
        - host: abc-1.pqr.databases.appdomain.cloud
          port: 32250
        - host: abc-2.pqr.databases.appdomain.cloud
          port: 32250
    certificates:
      - alias: ca
        crt: |
          -----BEGIN CERTIFICATE-----
          MIIDDzCCAfegAwIBAgIJANEH58y2/kzHMA0GCSqGSIb3DQEBCwUAMB4xHDAaBgNV
          BAMME0lCTSBDbG91ZCBEYXRhYmFzZXMwHhcNMTgwNjI1MTQyOTAwWhcNMjgwNjIy
          MTQyOTAwWjAeMRwwGgYDVQQDDBNJQk0gQ2xvdWQgRGF0YWJhc2VzMIIBIjANBgkq
          1eKI2FLzYKpoKBe5rcnrM7nHgNc/nCdEs5JecHb1dHv1QfPm6pzIxwIDAQABo1Aw
          TjAdBgNVHQ4EFgQUK3+XZo1wyKs+DEoYXbHruwSpXjgwHwYDVR0jBBgwFoAUK3+X
          Zo1wyKs+DEoYXbHruwSpXjgwDAYDVR0TBAUwAwEB/zANBgkqhkiG9w0BAQsFAAOC
          doqqgGIZ2nxCkp5/FXxF/TMb55vteTQwfgBy60jVVkbF7eVOWCv0KaNHPF5hrqbN
          i+3XjJ7/peF3xMvTMoy35DcT3E2ZeSVjouZs15O90kI3k2daS2OHJABW0vSj4nLz
          +PQzp/B9cQmOO8dCe049Q3oaUA==
          -----END CERTIFICATE-----
  roles:
    - ibm.mas_devops.mongodb

```

Troubleshooting
-------------------------------------------------------------------------------

!!! important
    Please be cautious while performing any of the troubleshooting steps outlined below. It is important to understand that the MongoDB Community operator persists data within Persistent Volume Claims. These claims should not be removed inadvertent deletion of the `mongoce` namespace could result in data loss.

### MongoDB Replica Set Pods Will Not Start

MongoDB 5 has introduced new platform specific requirements. Please consult the [Platform Support Notes](https://www.mongodb.com/docs/manual/administration/production-notes/#x86_64) for detailed information.

It is of particular importance to confirm that the AVX instruction set is exposed or available to the MongoDB workloads. This can easily be determined by entering any running pod on the same OpenShift cluster where MongoDB replica set members are failing to start. Once inside of a running pod the following command can be executed to confirm if the AVX instruction set is available:

```bash
cat /proc/cpuinfo | grep flags | grep avx
```

If `avx` is not found in the available `flags` then either the physical processor hosting the OpenShift cluster does not provide the AVX instruction set or the virtual host configuration is not exposing the AVX instruction set. If the latter is suspected the virtual hosting documentation should be referenced for details on how to expose the AVX instruction set.

### LDAP Authentication

If authenticating via LDAP with PLAIN specified for `authMechanism` then `configDb` must be set to `$external` in the MongoCfg. The field `configDb` in the MongoCfg refers to the authentication database. 

### CA Certificate Renewal

!!! warning
    If the MongoDB CA Certificate expires the MongoDB replica set will become unusable. Replica set members will not be able to communicate with each other and client applications (i.e. Maximo Application Suite components) will not be to connect.


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
oc project mongoce
oc delete deployment mongodb-kubernetes-operator
```

!!! important
    Make sure the MongoDB Community operator pod has terminated before proceeding.


```bash
oc delete statefulset mas-mongo-ce

```

!!! important
    Make sure all pods in the `mongoce` namespace have terminated before proceeding


Remove expired CA Certificate and Server Certificate resources. Clean up MongoDB Community configuration and then run the `mongodb` role.

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
