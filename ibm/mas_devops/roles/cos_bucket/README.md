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

### ibmcos_bucket_name
Optional name for your IBM Cloud Object Storage bucket.

- Environment Variable: `COS_BUCKET_NAME`
- Default Value: `$MAS_INSTANCE_ID-$MAS_WORKSPACE_ID-bucket`

### ibmcos_bucket_storage_class
Optional. IBM Cloud Object Storage bucket storage class. Supported options are `smart`, `vault`, `cold` and `flex`.
For more details, see [IBM Cloud Object Storage documentation](https://cloud.ibm.com/docs/cloud-object-storage/iam?topic=cloud-object-storage-classes#classes-locationconstraint)

- Environment Variable: `COS_BUCKET_STORAGE_CLASS`
- Default Value: `smart`

### ibmcos_instance_name
Provide the Object Storage instance name, will be used to find the targeted COS instance to create/deprovision the buckets. This is only used when cos_type is set to `ibm` for IBM Cloud Object Storage.

- Environment Variable: `COS_INSTANCE_NAME`
- Default Value: None

### ibmcos_location_info
Required. The location where the COS instance is available

  - Environment Variable: `COS_LOCATION`
  - Default Value: `global`

### ibmcos_bucket_region_location_type
Required. This defines the resiliency of your COS bucket. Supported options are `cross_region_location` (Highest availability) or `region_location` (Best performance).
For more details, see [IBM Cloud Object Storage documentation](https://cloud.ibm.com/docs/cloud-object-storage/basics?topic=cloud-object-storage-endpoints)

  - Environment Variable: `COS_BUCKET_REGION_LOCATION_TYPE`
  - Default Value: `cross_region_location`

ibmcos_bucket_region_location: "{{ lookup('env', 'COS_BUCKET_REGION_LOCATION') | default(bucket_cross_reg_loc, true) }}"
### ibmcos_bucket_region_location
Required. This defines the specific region of your COS bucket.

For `cross_region_location` type, the supported regions are `us`, `ap` and `eu`.
For `region_location` type, the supported regions are `au-syd`, `eu-de`, `eu-gb`, `jp-tok`, `us-east`, `us-south`, `ca-tor`, `jp-osa` and `br-sao`.

For more details, see [IBM Cloud Object Storage documentation](https://cloud.ibm.com/docs/cloud-object-storage/basics?topic=cloud-object-storage-endpoints)

### ibmcloud_region
Optional. For cross region location type buckets, the IBM Cloud region can be used as alternative to determine which cross region location to be used while creating the buckets.
  - Environment Variable: `IBMCLOUD_REGION`
  - Default Value: `us-east`

### ibmcos_url
Required (For bucket creation). The COS region location url endpoint. Needed to specify the COS bucket region location.
  - Environment Variable: `COS_REGION_LOCATION_URL`
  - Default Value: `https://s3.us.cloud-object-storage.appdomain.cloud`

### ibmcos_plan_type
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

### mas_instance_id
The instance ID of Maximo Application Suite that the ObjectStorageCfg configuration will target.  If this or `mas_config_dir` are not set then the role will not generate a ObjectStorageCfg template.

- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### mas_config_dir
Local directory to save the generated ObjectStorageCfg resource definition.  This can be used to manually configure a MAS instance to connect to the Kafka cluster, or used as an input to the [suite_config](suite_config.md) role. If this or `mas_instance_id` are not set then the role will not generate a ObjectStorageCfg template.

- Environment Variable: `MAS_CONFIG_DIR`
- Default Value: None

### cluster ingres tls secret name
Specify the name of the cluster's ingres tls secret which contains the default router certificate.

- Optional
- Environment Variable: `OCP_INGRESS_TLS_SECRET_NAME`
- Default Value: router-certs-default


Example Playbook
----------------

Create the Ceph Object store on the existing OCS cluster and prepare the objectstorageCfg yaml to mas_config_dir.
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    cos_type: ocs
    mas_instance_id: masinst1
    mas_config_dir: ~/masconfig
  roles:
    - ibm.mas_devops.cos_setup
```
Create the IBM Cloud Object storage Instance and prepare the objectstorageCfg yaml to mas_config_dir.
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    cos_type: ibm

    # MAS instance and config dir
    mas_instance_id: masinst1
    mas_config_dir: ~/masconfig
  roles:
    - ibm.mas_devops.cos_setup
```
License
-------

EPL-2.0
