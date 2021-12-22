cos_setup
=========

This role provides support for Configuring Cloud Object Storage in MAS.  It currently supports two providers:

- In-cluster Ceph Object Storage leveraging OpenShift Container Storage
- IBM Cloud Object Storage


Role Variables
--------------

### cos_type
Required.  Which COS provider to use; can be set to either `ibm` for IBM Cloud Object Storage or `ocs` for OpenShift Container Storage

- Environment Variable: `COS_TYPE`
- Default Value: None

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
