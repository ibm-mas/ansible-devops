ocp_setup_aws_efs
==================

This role provides support to configure AWS EFS based storageclass into Openshift cluster. EFS can be used RWX storage. 


Requirements
-------

Create an [EFS file system](https://docs.aws.amazon.com/efs/latest/ug/gs-step-two-create-efs-resources.html), configured appropriately with respect to VPC, availability zones, etc.

Role Variables:
-----------------

### AWS_REGION

required. The name of aws region where EFS locates. 
 * Environment Variable: AWS_REGION
 * Default Value: us-east-1

### FILE_SYSTEM_ID

required. The name of aws efs file system id. 
 * Environment Variable: FILE_SYSTEM_ID
 * Default Value: None

License
_________

EPL-2.0