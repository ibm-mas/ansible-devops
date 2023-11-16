uds
===============================================================================

Installs [IBM User Data Services](https://www.ibm.com/docs/en/cpfs?topic=services-enabling-user-data) as part of [IBM Foundational Services](https://www.ibm.com/docs/en/cpfs?topic=312-installing-foundational-services-by-using-console) in the `ibm-common-services` namespace.  If `mas_instance_id` and the others associated parameters are provided then the role will also generate a configuration file that can be directly applied to IBM Maximo Application Suite.


Role Variables - Installation
-------------------------------------------------------------------------------
### uds_action
Inform the role whether to perform an install or uninstall of IBM User Data Services or the Slim User Data Services. Supported values are `install`, `uninstall`, `install-suds` or `uninstall-suds`

- Optional
- Environment Variable: `UDS_ACTION`
- Default: `install`

### cluster_name
Required only for ROSA cluster. This variable is required to extract the UDS certificates. For other clusters this variable is not used.

- Environment Variable: `CLUSTER_NAME`
- Default Value: None

### uds_storage_class
Required.  Storage class where UDS will be installed.  On IBM Cloud RedHat Openshift Kubernetes Service (ROKS) `ibmc-block-bronze` is the recommended value.

- Environment Variable: `UDS_STORAGE_CLASS`
- Default Value: None

### uds_event_scheduler_frequency
Defines the frequency that BAS will collect event data. The value can be set following a [cron tab](https://crontab.guru/) format.

- Environment Variable: `UDS_EVENT_SCHEDULER_FREQUENCY`
- Default Value: `@daily`

### cluster ingres tls secret name
Specify the name of the cluster's ingres tls secret which contains the default router certificate.

- Optional
- Environment Variable: `OCP_INGRESS_TLS_SECRET_NAME`
- Default Value: router-certs-default


Role Variables - BASCfg Generation
-------------------------------------------------------------------------------
### mas_instance_id
The instance ID of Maximo Application Suite that the BasCfg configuration will target.  If this or `mas_config_dir` are not set then the role will not generate a BasCfg template.

- Optional
- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### mas_config_dir
Local directory to save the generated BasCfg resource definition.  This can be used to manually configure a MAS instance to connect to BAS instance, or used as an input to the [suite_config](suite_config.md) role. If this or `mas_instance_id` are not set then the role will not generate a BasCfg template.

- Optional
- Environment Variable: `MAS_CONFIG_DIR`
- Default Value: None

### mas_segment_key
Override the built-in segment key used by MAS when communicating with User Data Services.  This variable is only used for the generation of the BASCfg template, and in 99% of use cases you will not need to set this.

- Optional
- Environment Variable: `MAS_SEGMENT_KEY`
- Default Value: None

### uds_contact.email
Sets the Contact e-mail address used by the MAS instance's UDS configuration.

- **Required** when `mas_instance_id` and `mas_config_dir` are set
- Environment Variable: `UDS_CONTACT_EMAIL`
- Default Value: None

### uds_contact.first_name
Sets the Contact first name used by the MAS instance's UDS configuration.

- **Required** when `mas_instance_id` and `mas_config_dir` are set
- Environment Variable: `UDS_CONTACT_FIRSTNAME`
- Default Value: None

### uds_contact.last_name
Sets the Contact last name used by the MAS instance's UDS configuration.

- **Required** when `mas_instance_id` and `mas_config_dir` are set
- Environment Variable: `UDS_CONTACT_LASTNAME`
- Default Value: None

### uds_endpoint_url
Sets the UDS endpoint url used by the MAS instance's UDS configuration.

- Optional, used to instruct the role to set up MAS for an existing UDS instance.
- Environment Variable: `UDS_ENDPOINT_URL`
- Default Value: None

### uds_tls_crt
Sets the UDS TLS CA or Server Certificate used by the MAS instance's UDS configuration.

- Optional, used to instruct the role to set up MAS for an existing UDS instance.
- Environment Variable: `UDS_TLS_CERT`
- Default Value: None

### uds_tls_crt_local_file_path
The path on the local system to a file containing the TLS CA certificate of the AnalyticsProxy to be used when the Maximo Application Suite is registered with UDS.  This variable is only used if `uds_tls_crt` has not been set.

- Optional, used to instruct the role to set up MAS for an existing SLS instance.
- Environment Variable: `UDS_TLS_CERT_LOCAL_FILE`
- Default Value: None

### uds_api_key
Sets the UDS api key used by the MAS instance's UDS configuration.

- Optional, used to instruct the role to set up MAS for an existing UDS instance.
- Environment Variable: `UDS_API_KEY`
- Default Value: None

### custom_labels
List of comma separated key=value pairs for setting custom labels on instance specific resources.

- Optional
- Environment Variable: `CUSTOM_LABELS`
- Default Value: None

### mas_pod_templates_dir
Provide the directory where supported pod templates configuration files are defined.  This role will look for a configuration file named `ibm-mas-bascfg.yml` in the named directory.  The content of the configuration file should be the yaml block that you wish to be inserted into the BasCfg spec under a top level `podTemplates` element, e.g. `podTemplates: {object}`.

For examples refer to the [BestEfforts reference configuration in the MAS CLI](https://github.com/ibm-mas/cli/blob/master/image/cli/mascli/templates/pod-templates/best-effort/ibm-mas-bascfg.yml), for full documentation of the supported options refer to the [Customizing Pod Templates](https://www.ibm.com/docs/en/mas-cd/continuous-delivery?topic=configuring-customizing-workloads) in the product documentation.

- Optional
- Environment Variable: `MAS_POD_TEMPLATES_DIR`
- Default: None

Example Playbook
-------------------------------------------------------------------------------

### Install in-cluster and generate MAS configuration
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    uds_storage_class: ibmc-block-bronze

    mas_instance_id: masinst1
    mas_config_dir: ~/masconfig

    uds_contact:
      email: 'john@email.com'
      first_name: 'john'
      last_name: 'winter'
  roles:
  - ibm.mas_devops.uds
```

### Generate MAS configuration for existing installation
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_config_dir: ~/masconfig

    uds_endpoint_url: "https://xxx"
    uds_api_key: "xxx"
    uds_tls_crt_local_file_path: "/path/to/uds.crt"

    uds_contact:
      email: 'john@email.com'
      first_name: 'john'
      last_name: 'winter'
  roles:
  - ibm.mas_devops.uds
```

License
-------------------------------------------------------------------------------

EPL-2.0
