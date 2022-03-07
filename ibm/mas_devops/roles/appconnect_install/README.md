appconnect_install
===========

Installs **IBM AppConnect** on IBM Cloud Openshift Clusters (ROKS) and generates configuration that can be directly applied to IBM Maximo Application Suite.
This dependency is required by HP Utilities application.

Role Variables
--------------

### appconnect_namespace
Optional - Defines the targetted cluster namespace/project where AppConnect will be installed. If not provided, default AppConnect namespace will be 'ibm-app-connect'.

- Environment Variable: `APPCONNECT_NAMESPACE`
- Default Value: `ibm-app-connect`

### appconnect_channel
Optional - AppConnect subscription channel to be installed. For MAS 8.7, default `v3.0` channel is used. Ensure the supported dashboard version and license ID according to the AppConnect operator/channel version. 

- MAS 8.4 uses AppConnect channel subscription v1.4 and license id = L-APEH-BSVCHU
- MAS 8.5 uses AppConnect channel subscription v2.0 and license id = L-KSBM-BZWEAT
- MAS 8.6 uses AppConnect channel subscription v2.0 and license id = L-KSBM-C37J2R
- MAS 8.7 uses AppConnect channel subscription v3.0 and license id = L-KSBM-C87FU2

For more details: https://www.ibm.com/support/knowledgecenter/SSTTDS_11.0.0/com.ibm.ace.icp.doc/certc_licensingreference.html

- Environment Variable: `APPCONNECT_CHANNEL`
- Default Value: `v3.0`

### appconnect_dashboard_name
Optional - AppConnect Dashboard instance name. Default to `dashboard-12020r2` as a reference to AppConnect Dashboard version `12.0.2.0-r2` that is compatible with AppConnect Channel subscription `v3.0` and license ID `L-KSBM-C87FU2` (MAS 8.7 compatible)

For More details: https://www.ibm.com/docs/en/app-connect/containers_cd?topic=resources-licensing-reference-app-connect-operator

- Environment Variable: `APPCONNECT_DASHBOARD_NAME`
- Default Value: `dashboard-12020r2`

### appconnect_license_id
Optional - AppConnect license ID.

- Environment Variable: `APPCONNECT_LICENSE_ID`
- Default Value: `L-KSBM-C87FU2` (Which is compatible with AppConnect `v3.0` operator/channel)

### appconnect_storage_class
Required - Storage class where AppConnect will be installed - for IBM Cloud clusters, `ibmc-file-gold-gid` can be used.

- Environment Variable: `APPCONNECT_STORAGE_CLASS`
- Default Value: None

### appconnect_entitlement_username
Optional - Holds your IBM Entitlement username.

- Environment Variable: `APPCONNECT_ENTITLEMENT_USERNAME`
- Default Value: `cp`

### appconnect_entitlement_key
Required - Holds your IBM Entitlement key.

- Environment Variable: `APPCONNECT_ENTITLEMENT_KEY`
- Default Value: None

### mas_instance_id
Optional - The instance ID of Maximo Application Suite that the AppConnect configuration will target.  If this or `mas_config_dir` are not set then the role will not generate an AppConnect template.

- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### mas_config_dir
Optional - Local directory to save the generated AppConnect resource definition.  This can be used to manually configure a MAS instance to connect to AppConnect instance, or used as an input to the [suite_config](suite_config.md) role. If this or `mas_instance_id` are not set then the role will not generate an AppConnect template.

- Environment Variable: `MAS_CONFIG_DIR`
- Default Value: None

Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  roles:
  - ibm.mas_devops.bas_appconnect
```

License
-------

EPL-2.0
