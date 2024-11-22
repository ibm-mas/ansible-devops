ocp_efs
===============================================================================

This role provides support to install aws-efs on aws using `aws cli` and connect that to ROSA using `oc` CLI. This role create a new inbound rule in the security group of the ec2 instance where rosa is installed and then creates a new EFS instance and adds access points and network mounts to access EFS from ROSA.

Role Variables
-------------------------------------------------------------------------------

### aws_access_key_id
The AWS access key will be used to login to aws cli.

- **Required**
- Environment Variable: `AWS_ACCESS_KEY_ID`
- Default: None

### aws_secret_access_key
The AWS access secret key will be used to login to aws cli.

- **Required**
- Environment Variable: `AWS_SECRET_ACCESS_KEY`
- Default: None

### AWS_region
The aws region where you wish to provision the EFS instance.

- **Required**
- Environment Variable: `AWS_DEFAULT_REGION`
- Default: `eu-west-2`

### cluster_name
The name of the cluster we are going to attach the EFS storage to.

- **Required**
- Environment Variable: `CLUSTER_NAME`
- Default: None

### efs_unique_id
Any unique identifier like mas instance id which will be used as EFS storage class name. If this parameter is not set, then cluster_name will be used

- **Optional**
- Environment Variable: `EFS_UNIQUE_ID`
- Default: None

### creation_token_prefix
CreationTokens associated for AWS resources are built by concatenating creation_token_prefix and efs_unique_id.

- **Optional**
- Environment Variable: `CREATION_TOKEN_PREFIX`
- Default: 'mas_devops.'

### create_storage_class
If true, a StorageClass for the EFS instance named `efs<efs_unique_id>` will be automatically created in the cluster.

- **Optional**
- Environment Variable: `CREATE_STORAGE_CLASS`. Unset implies `true`, otherwise Ansible's `bool` filter is used to interpret the value as a boolean.
- Default: true

License
-------

EPL-2.0
