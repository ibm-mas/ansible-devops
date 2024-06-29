cos_bucket
===
This role extends support to create or deprovision Cloud Object Storage buckets.

Role Variables
--------------
### cos_type
Required.  Which COS provider to use; can be set to either `ibm` for IBM Cloud Object Storage or `aws` for S3 bucket types (aws support under development).

- Environment Variable: `COS_TYPE`
- Default Value: None

### cos_bucket_action
Required.  Which action you want to run for the COS bucket. You can either `create` or `delete` a COS bucket.

- Environment Variable: `COS_BUCKET_ACTION`
- Default Value: `create`

Role Variables - IBM Cloud Object Storage buckets
--------------
### cos_bucket_name
Optional name for your IBM Cloud Object Storage bucket.

- Environment Variable: `COS_BUCKET_NAME`
- Default Value: `$MAS_INSTANCE_ID-$MAS_WORKSPACE_ID-bucket`

### cos_bucket_storage_class
Optional. IBM Cloud Object Storage bucket storage class. Supported options are `smart`, `vault`, `cold` and `flex`.
For more details, see [IBM Cloud Object Storage documentation](https://cloud.ibm.com/docs/cloud-object-storage/iam?topic=cloud-object-storage-classes#classes-locationconstraint)

- Environment Variable: `COS_BUCKET_STORAGE_CLASS`
- Default Value: `smart`

### cos_instance_name
Provide the Object Storage instance name, will be used to find the targeted COS instance to create/deprovision the buckets. This is only used when cos_type is set to `ibm` for IBM Cloud Object Storage.

- Environment Variable: `COS_INSTANCE_NAME`
- Default Value: None

### cos_location_info
Required. The location where the COS instance is available

  - Environment Variable: `COS_LOCATION`
  - Default Value: `global`

### cos_bucket_region_location_type
Required. This defines the resiliency of your COS bucket. Supported options are `cross_region_location` (Highest availability) or `region_location` (Best performance).
For more details, see [IBM Cloud Object Storage documentation](https://cloud.ibm.com/docs/cloud-object-storage/basics?topic=cloud-object-storage-endpoints)

  - Environment Variable: `COS_BUCKET_REGION_LOCATION_TYPE`
  - Default Value: `cross_region_location`

cos_bucket_region_location: "{{ lookup('env', 'COS_BUCKET_REGION_LOCATION') | default(bucket_cross_reg_loc, true) }}"
### cos_bucket_region_location
Required. This defines the specific region of your COS bucket.

For `cross_region_location` type, the supported regions are `us`, `ap` and `eu`.
For `region_location` type, the supported regions are `au-syd`, `eu-de`, `eu-gb`, `jp-tok`, `us-east`, `us-south`, `ca-tor`, `jp-osa` and `br-sao`.

For more details, see [IBM Cloud Object Storage documentation](https://cloud.ibm.com/docs/cloud-object-storage/basics?topic=cloud-object-storage-endpoints)

### ibmcloud_region
Optional. For cross region location type buckets, the IBM Cloud region can be used as alternative to determine which cross region location to be used while creating the buckets.
  - Environment Variable: `IBMCLOUD_REGION`
  - Default Value: `us-east`

### cos_url
Required (For bucket creation). The COS region location url endpoint. Needed to specify the COS bucket region location.
  - Environment Variable: `COS_REGION_LOCATION_URL`
  - Default Value: `https://s3.us.cloud-object-storage.appdomain.cloud`

### cos_plan_type
Required (For Provisioning). The plan type of the service
  - Environment Variable: `COS_PLAN`
  - Default Value: `standard`
### resource_key_iam_role
Provide an optional role when cos service credential is getting created during COS bucket creation.
  - Environment Variable: `RESOURCE_KEY_IAM_ROLE`
  - Default Value: `Manager` 

### ibmcloud_apikey
Required if cos_type is set to `ibm`.  Provide your IBM Cloud API Key.

- Environment Variable: `IBMCLOUD_APIKEY`
- Default Value: None

### ibmcloud_resourcegroup
Only used when cos_type is set to `ibm`.  Provide the name of the resource group which will own the COS instance for the targeted buckets.

- Environment Variable: `IBMCLOUD_RESOURCEGROUP`
- Default Value: `Default`

Role Variables - AWS S3 Buckets
--------------

To run this role successfully for AWS s3 buckets, you must have already installed the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).
Also, you need to have AWS user credentials configured via `aws configure` command or simply export `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables with your corresponding AWS username credentials prior running this role.

### aws_bucket_name
Optional name for your AWS/S3 bucket.

- Environment Variable: `COS_BUCKET_NAME`
- Default Value: `$MAS_INSTANCE_ID-$MAS_WORKSPACE_ID-bucket`

### aws_region
The region where the bucket is located.

- Required.
- Environment Variable: `AWS_REGION`
- Default Value: `us-east-2`

### aws_bucket_versioning_flag
Flag to define if versioning should be enabled for the bucket

- Optional.
- Environment Variable: `COS_BUCKET_VERSIONING_FLAG`
- Default Value: `True`

### aws_bucket_encryption
JSON formatted string to define default encryption configuration for AWS S3 bucket.

- Optional.
- Environment Variable: `COS_BUCKET_ENCRYPTION`
- Default Value: None

### aws_bucket_force_deletion_flag
Deletes S3 AWS bucket objects prior deleting the S3 bucket. This option only works if versioning **is not enabled** in the bucket.
**Note:** To delete AWS bucket, `cos_bucket_action` must be set to `delete`.

- Optional.
- Environment Variable: `COS_BUCKET_FORCE_DELETION_FLAG`
- Default Value: `True`

Example Playbook
----------------

Create the IBM Cloud Object storage bucket.
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    cos_type: ibm
    cos_bucket_action: create
    cos_bucket_name: my-ibm-bucket
    cos_instance_name: my-ibmcos-instance-name
    ibmcloud_apikey: my-ibm-cloud-apikey
  roles:
    - ibm.mas_devops.cos_bucket
```

Create the AWS S3 storage bucket.
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    cos_type: aws
    cos_bucket_action: create
    aws_bucket_name: my-aws-bucket
    aws_region: us-east-2
    aws_bucket_versioning_flag: True
    aws_bucket_encryption: '{"Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]}'
  roles:
    - ibm.mas_devops.cos_bucket
```

License
-------

EPL-2.0
