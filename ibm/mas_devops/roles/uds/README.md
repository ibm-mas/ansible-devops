uds
===============================================================================

Installs [IBM User Data Services](https://www.ibm.com/docs/en/cpfs?topic=services-enabling-user-data) as part of [IBM Foundational Services](https://www.ibm.com/docs/en/cpfs?topic=312-installing-foundational-services-by-using-console) in the `ibm-common-services` namespace.  If `mas_instance_id` and the others associated parameters are provided then the role will also generate a configuration file that can be directly applied to IBM Maximo Application Suite.


| Variable       | Environment Variable | Default | Description |
| :------------- | :------------------- | :------ | :---------- |
| uds_action | `UDS_ACTION` | `install` | Optional.  Inform the role whether to perform an install or uninstall of IBM User Data Services or the Slim User Data Services. Supported values are `install`, `uninstall`, `install-suds` or `uninstall-suds`. |
| cluster_name | `CLUSTER_NAME` | None | Required only for ROSA cluster. This variable is required to extract the UDS certificates. For other clusters this variable is not used. |
| uds_storage_class | `UDS_STORAGE_CLASS` | None | Required.  Storage class where UDS will be installed.  On IBM Cloud RedHat Openshift Kubernetes Service (ROKS) `ibmc-block-bronze` is the recommended value. |
| uds_event_scheduler_frequency | `UDS_EVENT_SCHEDULER_FREQUENCY` | `@daily` | Optional.  Defines the frequency that BAS will collect event data. The value can be set following a [cron tab](https://crontab.guru/) format. |
| ocp_ingress_tls_secret_name | `OCP_INGRESS_TLS_SECRET_NAME` | `router-certs-default` | Optional.  Specify the name of the cluster's ingres tls secret which contains the default router certificate. |
| mas_instance_id | `MAS_INSTANCE_ID` | None | The instance ID of Maximo Application Suite that the BasCfg configuration will target.  If this or `mas_config_dir` are not set then the role will not generate a BasCfg template.
| mas_config_dir | `MAS_CONFIG_DIR` | None | Local directory to save the generated BasCfg resource definition.  This can be used to manually configure a MAS instance to connect to BAS instance, or used as an input to the [suite_config](suite_config.md) role. If this or `mas_instance_id` are not set then the role will not generate a BasCfg template. |
| mas_segment_key | `MAS_SEGMENT_KEY` | None | Override the built-in segment key used by MAS when communicating with User Data Services.  This variable is only used for the generation of the BASCfg template, and in 99% of use cases you will not need to set this. |
| uds_contact.email | `UDS_CONTACT_EMAIL` | None | **Required** when `mas_instance_id` and `mas_config_dir` are set.  Sets the Contact e-mail address used by the MAS instance's UDS configuration. |
| uds_contact.first_name | `UDS_CONTACT_FIRSTNAME` | None | **Required** when `mas_instance_id` and `mas_config_dir` are set.  Sets the Contact first name used by the MAS instance's UDS configuration.
| uds_contact.last_name | `UDS_CONTACT_LASTNAME` | None | **Required** when `mas_instance_id` and `mas_config_dir` are set.  Sets the Contact last name used by the MAS instance's UDS configuration.
| uds_endpoint_url | `UDS_ENDPOINT_URL` | None | Optional.  Sets the UDS endpoint url used by the MAS instance's UDS configuration. |
| uds_tls_crt | `UDS_TLS_CERT` | None | Optional.  Sets the UDS TLS CA or Server Certificate used by the MAS instance's UDS configuration. |

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

### include_cluster_ingress_cert_chain
Optional. When set to `True`, includes the complete certificates chain in the generated MAS configuration, when a trusted certificate authority is found in your cluster's ingress.

- Optional
- Environment Variable: `INCLUDE_CLUSTER_INGRESS_CERT_CHAIN`
- Default: `False`

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
