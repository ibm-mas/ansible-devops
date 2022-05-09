cp4d_service
=============

Install a chosen CloudPak for Data service.

Services Supported
------------------
These services can be deployed and configured using this role:

- [Watson Studio](https://www.ibm.com/docs/en/cloud-paks/cp-data/4.0?topic=services-watson-studio) required by [Predict](https://www.ibm.com/docs/en/mas87/8.7.0?topic=applications-maximo-predict) and [Health & Predict Utilities](https://www.ibm.com/docs/en/mas87/8.7.0?topic=solutions-maximo-health-predict-utilities)
- [Watson Machine Learning](https://www.ibm.com/docs/en/cloud-paks/cp-data/4.0?topic=services-watson-machine-learning) required by [Predict](https://www.ibm.com/docs/en/mas87/8.7.0?topic=applications-maximo-predict)
- [Analytics Service (Apache Spark)](https://www.ibm.com/docs/en/cloud-paks/cp-data/4.0?topic=services-analytics) required by [Predict](https://www.ibm.com/docs/en/mas87/8.7.0?topic=applications-maximo-predict)
- [Watson Discovery](https://www.ibm.com/docs/en/cloud-paks/cp-data/4.0?topic=services-watson-discovery) required by Assist


!!! info "Application Support"
    For more information on how Predict and HP Utilities make use of Watson Studio, refer to [Predict/HP Utilities documentation](https://www.ibm.com/docs/en/mhmpmh-and-p-u/8.2.0?topic=started-getting-data-scientists)


Role Variables - Installation
-----------------------------
### cpd_service_name
Name of the service to install, supported values are: `wsl`

- **Required**
- Environment Variable: `CPD_SERVICE_NAME`
- Default Value: None

### cpd_service_storage_class
This is used to set `spec.storageClass` in all CPD v3.5 services, and many - but not all - CP4D v4.0 services.

- **Required**, unless IBMCloud storage classes are available.
- Environment Variable: `CPD_SERVICE_STORAGE_CLASS`
- Default Value: `ibmc-file-gold-gid` if the storage class is available.

### cpd_instance_namespace
Namespace where the CP4D instance is deployed.

- Optional
- Environment Variable: `CPD_INSTANCE_NAMESPACE`
- Default Value: `ibm-cpd`

### cpd_operator_namespace
Namespace where the CP4D instance is deployed.

- Optional
- Environment Variable: `CPD_OPERATORS_NAMESPACE`
- Default Value: `ibm-cpd-operators`


Role Variables - Watson Studio
------------------------------
### cpd_wsl_project_id
Stores the CP4D Watson Studio Project ID that can be used to configure HP Utilities application in MAS.  If this property is not set, or the project identified by this ID does not already exist this role will automatically create one Watson Studio project.  **TODO: This needs to be fixed we need to key off the PROJECT_NAME to make this idempotent, user can't be expected to know the project ID upfront!**

- Optional, only supported when `cpd_service_name` = `wsl`
- Environment Variable: `CPD_WSL_PROJECT_ID`
- Default Value: None

### cpd_wsl_project_name
Stores the CP4D Watson Studio Project name that can be used to configure HP Utilities application in MAS.

- Optional, only supported when `cpd_service_name` = `wsl`
- Environment Variable: `CPD_WSL_PROJECT_NAME`
- Default Value: `wsl_default_project`

### cpd_wsl_project_description
Optional - Stores the CP4D Watson Studio Project description that can be used to configure HP Utilities application in MAS.

- Optional, only supported when `cpd_service_name` = `wsl`
- Environment Variable: `CPD_WSL_PROJECT_DESCRIPTION`
- Default Value: `Watson Studio Project for Maximo Application Suite`


Role Variables - Watson Discovery
------------------------------


Role Variables - MAS Configuration Generation
----------------------------------==---------
### mas_instance_id
The instance ID of Maximo Application Suite that a generated configuration will target.  If this or `mas_config_dir` are not set then the role will not generate a resource template.

- Optional, only supported when `cpd_service_name` = `wsl`
- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### mas_config_dir
Local directory to save the generated resource definition.  This can be used to manually configure a MAS instance, or used as an input to the [suite_config](suite_config.md) role. If this or `mas_instance_id` are not set then the role will not generate a resource template.

- Optional, only supported when `cpd_service_name` = `wsl`
- Environment Variable: `MAS_CONFIG_DIR`
- Default Value: None


Example Playbook
----------------

```yaml
---
- hosts: localhost
  any_errors_fatal: true
  vars:
    cpd_service_storage_class: ibmc-file-gold-gid
    cpd_service_name: wsl
  roles:
    - ibm.mas_devops.cp4d_service

```

License
-------

EPL-2.0




Content from cp4d_wds role that needs to be merged into here
---------------------------------------


cp4d_wds
==========

It's only for WDS 4.0.x install on the existing CP4D 4.0.x and WDS instance provisioning, and also generated WDScfg (For Assist Install) related yaml to MAS config Directory.

It's also used for WDScfg (For Assist Install) related yaml preparation if you want to use the existing external WDS instance.

Role Variables
--------------
### cp4d_username
The CP4D Admin User name used to call CP4D API to provision Discovery Instance. If you didn't change the initial admin password after CP4D install,you don't need to provide it. And the initial admin user name `admin` will be used.
- Environment Variable: `CP4D_USERNAME`
- Default Value: None

### cp4d_password
The CP4D Admin User password to call CP4D API to provision Discovery Instance. If you didn't change the initial admin password after CP4D install, you don't need to provide it.
And the initial admin user password for `admin` will be used.
- Environment Variable: `CP4D_PASSWORD`
- Default Value: None

### wdschannel
The discovery channel used by discovery install. By default the `v4.0`  will be used as channel name for discovery install.
- Environment Variable: `WDS_CHANNEL`
- Default Value: v4.0

### wdsversion
The discovery version used by discovery install. By default the discovery `4.0.6` version will be installed.
- Environment Variable: `WDS_VERSION`
- Default Value: 4.0.6

### wdsstorageclass
The specific storage class for discovery install, if not specified , the storage class used by CP4D will be auto queried in the cluster and used for discovery install.
Usually Watson Discovery uses the following storage classes. If you don't use these storage classes on your cluster, ensure that you have a storage class with an equivalent definition:
OpenShift Container Storage: `ocs-storagecluster-ceph-rbd`
IBM Cloud OCP cluster: `ibmc-block-gold`,`ibmc-block-gold-gid`
IBM Spectrum® Scale Container Native: `ibm-spectrum-scale-sc`
Portworx: `portworx-db-gp2-sc`

- Environment Variable: `WDS_STORAGE_CLASS`
- Default Value: None

### mas_instance_id
The instance ID of Maximo Application Suite that the discovery configuration will target.  If this or `mas_config_dir` are not set then the role will not generate a discovery template.

- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### mas_workspace_id
The workspace ID of Maximo Application Suite that the discovery instance name will be combined as "discovery-assist-{{ mas_workspace_id }}" if you set.
Otherwise, single discovery instance will be created named as "discovery-assist".

- Environment Variable: `MAS_WORKSPACE_ID`
- Default Value: None

### mas_config_dir
Local directory to save the generated discovery configuration files.  This can be used to manually configure a Assist instance to connect to the discovery cluster, or used as an input to the [suite_config](suite_config.md) role. If this or `mas_instance_id` are not set then the role will not generate a discovery template.

- Environment Variable: `MAS_CONFIG_DIR`
- Default Value: None

If you want to use the existing available external WDS instance(not in the cluster), the below Environment Variables are `required` to generate the Discovery configuration files. Either is missing will cause the failure to use external Discovery.
### assist_wds_url
External Discovery URL for discovery API use
- Environment Variable: `ASSIST_WDS_URL`
- Default Value: None
### assist_wds_admin
External Discovery admin User name
- Environment Variable: `ASSIST_WDS_ADMIN`
- Default Value: None
### assist_wds_pass
External Discovery admin User password
- Environment Variable: `ASSIST_WDS_PASS`
- Default Value: None

Example Playbook
----------------
WDS install and WDS instance in the OCP Env
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    # Create the MAS WDSCfg & Secret resource definitions
    mas_instance_id: "{{ lookup('env', 'MAS_INSTANCE_ID') }}"
    mas_config_dir: "{{ lookup('env', 'MAS_CONFIG_DIR') }}"
  roles:
    - mas.devops.cp4d_wds
```
Use External WDS instance in the OCP Env
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    #  Use External WDS instance for assist install
    assist_wds_url: "{{ lookup('env', 'ASSIST_WDS_URL') }}"
    assist_wds_admin: "{{ lookup('env', 'ASSIST_WDS_ADMIN') }}"
    assist_wds_pass: "{{ lookup('env', 'ASSIST_WDS_PASS') }}"

    #  Create the MAS WDSCfg & Secret resource definitions
    mas_instance_id: "{{ lookup('env', 'MAS_INSTANCE_ID') }}"
    mas_config_dir: "{{ lookup('env', 'MAS_CONFIG_DIR') }}"
  roles:
    - mas.devops.cp4d_wds
```

License
-------

EPL-2.0
