aws_documentdb_user
-----------------------
This role creates an EC2 instance in the same vpc where Document DB was installed and then create additional docdb user for the MAS instance. The role also stores the additional docdb username and password in AWS secret manager along with creating k8 Secret in specified config directory

## Prerequisites
To run this role with providers you must have already installed the [Mongo Shell](https://www.mongodb.com/docs/mongodb-shell/install/).

Role variables
=================

### aws_access_key_id
Required. AWS Account Access Key Id

- Environment Variable: `AWS_ACCESS_KEY_ID`

### aws_secret_access_key
Required. AWS Account Secret Access Key

- Environment Variable: `AWS_SECRET_ACCESS_KEY`

### aws_region
Required. AWS Region where DocumentDB and other resources will be created

- Environment Variable: `AWS_REGION`
- Default Value: `us-east-2`

### vpc_id
Required. VPC ID where the document DB was installed

- Environment Variable: `VPC_ID`

### mas_instance_id
Required.The instance ID of Maximo Application Suite required for creating docdb user credentials secret

- Environment Variable: `MAS_INSTANCE_ID`

### docdb_host
Required. AWS DocumentDB Instance Host Address

- Environment Variable: `DOCDB_HOST`

### docdb_port
Required. AWS DocumentDB Port Address

- Environment Variable: `DOCDB_PORT`

### docdb_master_username
Required. AWS DocumentDB Master Username

- Environment Variable: `DOCDB_MASTER_USERNAME`

### docdb_master_password
Required. AWS DocumentDB Master Password

- Environment Variable: `DOCDB_MASTER_PASSWORD`

### docdb_ingress_cidr
Required. IPv4 Address from which incoming connection requests will be allowed to DocumentDB cluster

- Environment Variable: `DOCDB_INGRESS_CIDR`

### docdb_egress_cidr
Required. IPv4 Address at which outgoing connection requests will be allowed to DocumentDB cluster

- Environment Variable: `DOCDB_EGRESS_CIDR`

### aws_ec2_cidr_az1
Required. Provide IPv4 CIDR address for the subnet to be created in one of the 3 availabilty zones of your VPC. If the subnet exists already then it must contain the tag of Name: {{ docdb_cluster_name }}, if the subnet doesn't exist already then one is created.
- Environment Variable: `AWS_EC2_CIDR_AZ1`

### aws_key_pair_name
Required. Provide the key pair name which will be used to create the EC2 instance

- Environment Variable: `AWS_KEY_PAIR_NAME`

### docdb_cluster_name
Required.DocumentDB Cluster Name

- Environment Variable: `DOCDB_CLUSTER_NAME`

### secret_name_mongo_instance
Optional. AWS Secret manager name where document db Instance username & password will be stored

- Environment Variable: `SECRET_NAME_MONGO_INSTANCE`

### docdb_instance_username
Optional. AWS DocumentDB Instance Username

- Environment Variable: `DOCDB_INSTANCE_USERNAME`

### docdb_instance_password
Optional. AWS DocumentDB Instance Password

- Environment Variable: `DOCDB_INSTANCE_PASSWORD`

### mas_config_dir
Local directory to save the generated K8S secret.  This can be used to manually configure a MAS instance to connect to the Mongo cluster, or used as an input to the [suite_config](suite_config.md) role. If this or `mas_instance_id` are not set then the role will not generate a K8S secret template.

- Environment Variable: `MAS_CONFIG_DIR`
- Default Value: None

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    aws_access_key_id: ***
    aws_secret_access_key: ***
    aws_region: us-east-2
    vpc_id: vpc-123dx***
    docdb_host: test1.aws-01....
    docdb_port: 27017    
    docdb_master_username: test-user
    docdb_master_password: test-pass-***
    docdb_ingress_cidr: 10.1.0.0/23
    docdb_egress_cidr: 10.1.0.0/23
    aws_ec2_cidr_az1: 10.1.1.96/27
    aws_key_pair_name: ***
    docdb_cluster_name: docdb-cluster-01
    secret_name_mongo_instance: /cluster-01/docdb/masinst1
    mas_config_dir: ~/masconfig
  roles:
    - ibm.mas_devops.aws_ec2_documentdb
```