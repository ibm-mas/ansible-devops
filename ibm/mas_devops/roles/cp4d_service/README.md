cp4d_service
=============

Install one or more CloudPak for Data services.

This role supports both CP4D v3.5 and v4.0.

- With CP4D v3.5 all services will be installed to the `cpd-meta-ops` namespace.
- With CP4D v4.0 all services will be installed to the `cpd-services` namespace.

Supported Services
------------------

- **Watson Machine Learning** As part of Watson Studio, Watson Machine Learning helps data scientists and developers accelerate AI and machine learning deployment.
- **Apache Spark** Apache Spark is a runtime environment configured inside of Watson Studio similar to a Python Runtime environment.  When Spark is enabled from CP4D, you can opt to create a notebook and choose Spark as runtime to expand data modeling capabilities.
- **Watson AI OpenScale**  Watson OpenScale enables tracking AI models in production, validation and test models to mitigate operational risks.

!!! info "Application Support"
    For more information on how Predict and HP Utilities make use of Watson Studio, refer to [Predict/HP Utilities documentation](https://www.ibm.com/docs/en/mhmpmh-and-p-u/8.2.0?topic=started-getting-data-scientists)

    - [Predict](https://www.ibm.com/docs/en/mas84/8.4.0?topic=applications-maximo-predict) requires Watson Studio, Machine Learning and Spark; Openscale is an optional dependency
    - [Health & Predict Utilities](https://www.ibm.com/docs/en/mas84/8.4.0?topic=solutions-maximo-health-predict-utilities) requires Watson Studio base capability only


Role Variables
--------------

### cpd_version
Users may **optionally** pass this parameter to explicitly control the version of CP4D used, if this is not done then the role will attempt to locate the `cpd-meta-ops` namespace associated with CP4D v3.5, if this namespace if located then we will switch to CP4D v3.5 mode, in all other cases the role will assume CP4D v4 is in use.

- Environment Variable: `CPD_VERSION`
- Default Value: None

### cpd_service_storage_class
Required.  This is used to set `spec.storageClass` in all CPD v3.5 services, and many - but not all - CP4D v4.0 services.

- Environment Variable: `CPD_STORAGE_CLASS`
- Default Value: None

### cpd_wd_storage_class
Required only if installing Watson Discovery service (`wd`) on CP4D v4.0.

- Environment Variable: `CPD_WD_STORAGE_CLASS`
- Default Value: None

### cpd_instance_namespace
Only supported if `cpd_version = cpd40`, otherwise unused. For v3.5 support this value is always set to `cpd-meta-ops`.

- Environment Variable: `CPD_SERVICES_NAMESPACE`
- Default Value: `cpd-services`

### cpd_services
Required.  Provide a list of Cloud Pak for Data services to enable.

- Environment Variable: None
- Default Value: None
### cpd_wsl_project_id
Optional - Stores the CP4D Watson Studio Project ID that can be used to configure HP Utilities application in MAS.

If this property is not set, and Watson Studio is installed as part of CP4D, this role will automatically create one Watson Studio project that could be used to configure HP Utilities application in MAS instance (`mas_instance_id` and `mas_config_dir` properties must also be set in order for Watson Studio project to be created as part of this role.)

- Environment Variable: `CPD_WSL_PROJECT_ID`
- Default Value: None.

### cpd_wsl_project_name
Optional - Stores the CP4D Watson Studio Project name that can be used to configure HP Utilities application in MAS.

- Environment Variable: `CPD_WSL_PROJECT_NAME`
- Default Value: `wsl_default_project`

### cpd_wsl_project_description
Optional - Stores the CP4D Watson Studio Project description that can be used to configure HP Utilities application in MAS.

- Environment Variable: `CPD_WSL_PROJECT_DESCRIPTION`
- Default Value: `Watson Studio project to be used by HP Utilities app in MAS`
### mas_instance_id
If Watson Studio is installed as part of CP4D: The instance ID of Maximo Application Suite that the WatsonStudioCfg configuration will target.  If this or `mas_config_dir` are not set then the role will not generate a WatsonStudioCfg template.

- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### mas_config_dir
If Watson Studio is installed as part of CP4D: Local directory to save the generated WatsonStudioCfg resource definition.  This can be used to manually configure a MAS instance to connect to the Watson Studio, or used as an input to the [suite_config](suite_config.md) role. If this or `mas_instance_id` are not set then the role will not generate a WatsonStudioCfg template.

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
    cpd_wd_storage_class: ibmc-block-gold
    # Install the Db2 Warehouse & WSL services
    cpd_services:
      - db2wh
      - wsl
  roles:
    - ibm.mas_devops.cp4d_install_services

```

License
-------

EPL-2.0
