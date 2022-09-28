appconnect
===============================================================================

Installs **IBM AppConnect** and generates configuration that can be directly applied to IBM Maximo Application Suite.

This dependency is required by the Health and Predict Utilities application:

- HP Utilities v8.4 requires support for `12.0.4.0-r2` AppConnect dashboards (License ID `L-APEH-C9NCK6`)
- HP Utilities v8.3 requires support for `12.0.2.0-r2` AppConnect dashboards (License ID `L-KSBM-C87FU2`)
- HP Utilities v8.2 requires support for `12.0.1.0-r2` AppConnect dashboards (license ID `L-KSBM-C37J2R`)

| HP Utilities | AppConnect   | License       | Dashboard Versions       |
| ------------ | ------------ | ------------- | ------------------------ |
| v8.4         | v4.1 - v5.2  | L-APEH-C9NCK6 | 12.0.4.0-r1, 12.0.4.0-r2 |
| v8.3         | v3.0 - v4.2  | L-KSBM-C87FU2 | 12.0.2.0-r2              |
| v8.2         | v1.5 - v3.1  | L-KSBM-C37J2R | 12.0.1.0-r1, 12.0.1.0-r2 |

For more information review the [licensing reference for IBM App Connect Operator](https://www.ibm.com/docs/en/app-connect/containers_cd?topic=resources-licensing-reference-app-connect-operator).

!!! important
    All defaults in this role are currently set for compatability with HP Utilities version 8.4.  If you are installing App Connect for use with older release of HP Utilities then you must set the `appconnect_channel` and `appconnect_license_id` variables (and it would be sensible to customize `appconnect_dashboard_name` as well).


Role Variables - Installation
-------------------------------------------------------------------------------
### ibm_entitlement_key
Provide your [IBM entitlement key](https://myibm.ibm.com/products-services/containerlibrary).

- **Required**
- Environment Variable: `IBM_ENTITLEMENT_KEY`
- Default: None

### appconnect_entitlement_username
An IBM entitlement key specific for AppConnect installation, primarily used to override `ibm_entitlement_key` in development.

- Optional
- Environment Variable: `APPCONNECT_ENTITLEMENT_USERNAME`
- Default: None

### appconnect_namespace
Defines the targetted cluster namespace/project where AppConnect will be installed. If not provided, default AppConnect namespace will be `ibm-app-connect`.

- Optional
- Environment Variable: `APPCONNECT_NAMESPACE`
- Default Value: `ibm-app-connect`

### appconnect_channel
Subscription channel, this must align with the version of HP Utilities (see table above).

- Optional
- Environment Variable: `APPCONNECT_CHANNEL`
- Default Value: `v5.2`


Role Variables - Configuration
-------------------------------------------------------------------------------
### appconnect_storage_class
Storage class where AppConnect will be installed - for IBM Cloud clusters, `ibmc-file-gold-gid` must be used as per [documentation](https://www.ibm.com/docs/en/app-connect/containers_cd?topic=resources-dashboard-reference#storage).

- **Required**
- Environment Variable: `APPCONNECT_STORAGE_CLASS`
- Default Value: None

### appconnect_dashboard_name
AppConnect dashboard instance name. Defaults to `dashboard-12040r2` as a reference to AppConnect Dashboard version `12.0.4.0-r2` that is compatible with the default subscription channel and license ID.

- Optional
- Environment Variable: `APPCONNECT_DASHBOARD_NAME`
- Default Value: `dashboard-12040r2`

### appconnect_dashboard_version
AppConnect dashboard version, this must align with the License ID used.

- Optional
- Environment Variable: `APPCONNECT_DASHBOARD_VERSION`
- Default Value: `12.0.4.0-r2`

### appconnect_license_id
AppConnect license ID.

- Optional
- Environment Variable: `APPCONNECT_LICENSE_ID`
- Default Value: `L-KSBM-C37J2R`


Role Variables - MAS Configuration
-------------------------------------------------------------------------------
### mas_instance_id
The instance ID of Maximo Application Suite that the AppConnect configuration will target.  If this or `mas_config_dir` are not set then the role will not generate an AppConnect template.

- Optional
- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### mas_config_dir
Local directory to save the generated AppConnect resource definition.  This can be used to manually configure a MAS instance to connect to AppConnect instance, or used as an input to the [suite_config](suite_config.md) role. If this or `mas_instance_id` are not set then the role will not generate an AppConnect template.

- Optional
- Environment Variable: `MAS_CONFIG_DIR`
- Default Value: None


Example Playbooks
-------------------------------------------------------------------------------
### Install IBM App Connect for the latest release of HP Utilties (v8.4)
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    ibm_entitlement_key: xxx
  roles:
    - ibm.mas_devops.ibm_catalogs
    - ibm.mas_devops.appconnect
```

### Install IBM App Connect for HP Utilties v8.3
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    ibm_entitlement_key: xxx
    appconnect_channel: v4.2
    appconnect_license_id: L-KSBM-C87FU2
    appconnect_dashboard_name: dashboard-12020r2
  roles:
    - ibm.mas_devops.ibm_catalogs
    - ibm.mas_devops.appconnect
```

License
-------------------------------------------------------------------------------

EPL-2.0
