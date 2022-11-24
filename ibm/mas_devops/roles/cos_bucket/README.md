cos_bucket
===

Role Variables
--------------

### cos_type
Required.  Which COS provider to use; can be set to either `ibm` for IBM Cloud Object Storage or `ocs` for OpenShift Container Storage

- Environment Variable: `COS_TYPE`
- Default Value: None

### cos_instance_name
Provide an optional name for the Object Storage instance.  This is only used when cos_type is set to `ibm` for IBM Cloud Object Storage.

- Environment Variable: `COS_INSTANCE_NAME`
- Default Value: `Object Storage for MAS`, if `mas_instance_id` is set the MAS instance ID will be appended to this name.

### cos_action
Required. Which action to perform for COS. Can be set either to `provision` or `deprovision`
  - Environment Variable: `COS_ACTION`
  - Default Value: `provision` 

### cos_service
The name of the service offering like cloud-object-storage, kms etc
  - Environment Variable: `COS_SERVICE`
  - Default Value: `cloud-object-storage`

### ibmcos_location_info
Required. The location where the instance available
  - Environment Variable: `COS_LOCATION`
  - Default Value: `global`

### ibmcos_plan_type
Required (For Provisioning). The plan type of the service
  - Environment Variable: `COS_PLAN`
  - Default Value: `standard`
### resource_key_iam_role
Provide an optional role when cos service credential is getting created during COS provisioning .
  - Environment Variable: `RESOURCE_KEY_IAM_ROLE`
  - Default Value: `Manager` 

### ibmcloud_apikey
Required if cos_type is set to `ibm`.  Provide your IBM Cloud API Key.

- Environment Variable: `IBMCLOUD_APIKEY`
- Default Value: None

### ibmcloud_resourcegroup
Only used when cos_type is set to `ibm`.  Provide the name of the resource group which will own the COS instance.

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
