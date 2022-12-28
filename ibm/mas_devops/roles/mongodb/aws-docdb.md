aws documentdb
=======

Role Variables
--------------

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

### docdb_size
Required.Config File containing specs for DocumentDB

- Environment Variable: `DOCDB_SIZE`

### docdb_subnet_group_name
DocumentDB Subnet Group Name

- Value: `docdb-{{ docdb_cluster_name }}`

### docdb_security_group_name
DocumentDB Security Group Name

- Value: `docdb-{{ docdb_cluster_name }}`

### docdb_admin_credentials_secret_name
DocumentDB Admin Credentials Secret Name

- Value: `{{ docdb_cluster_name }}-admin-credentials`