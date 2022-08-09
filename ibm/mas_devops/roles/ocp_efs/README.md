ocp_efs
=========

This role provides support to install aws-efs on aws using `aws cli` and connect that to ROSA using `oc` CLI. This role create a new inbound rule in the security group of the ec2 instance where rosa is installed and then creates a new EFS instance and adds access points and network mounts to access EFS from ROSA.

Role Variables
--------------

### aws_access_key_id
The aws access key will be used to login to aws cli.

- **Required**
- Environment Variable: `AWS_ACCESS_KEY_ID`
- Default: None

### aws_secret_access_key
The aws access secret key will be used to login to aws cli.

- **Required**
- Environment Variable: `AWS_SECRET_ACCESS_KEY`
- Default: None

### aws_region
The aws region will be used to login to aws cli to target the particular location. this should be same as where we are deploying rosa

- **Required**
- Environment Variable: `AWS_DEFAULT_REGION`
- Default: `eu-west-2`

### aws_output
The aws output will be used to login to aws cli. This will be used to determine the output of the aws cli commands

- Environment Variable: `AWS_DEFAULT_OUTPUT`
- Default: json

### cluster_name
The name of the cluster to login to.  This will be used to lookup the actual login credentials of the system.

- **Required**
- Environment Variable: `CLUSTER_NAME`
- Default: None

### rosa_cluster_admin_password
The password for the cluster-admin account (created when the cluster was provisioned).

- **Required**
- Environment Variable: `ROSA_CLUSTER_ADMIN_PASSWORD`
- Default: None

### rosa_cluster_url
The rosa cluster url used to login to cluster-admin account.  (created when the cluster was provisioned).
- **Required**
- Environment Variable: `ROSA_CLUSTER_URL`
- Default: None


License
-------

EPL-2.0
