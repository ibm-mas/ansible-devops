suite_manage_doclinks_config
===
This role extends support for configuring IBM Cloud Object Storage to storage **Manage** application doclinks.
**Note:** This role should be executed **after** Manage application is deployed and activated as it needs Manage up and running prior configuring logging features.

The default for Manage logging configuration is to use IBM Cloud Object Storage as persistent storage for Manage logging. You can run `cos` role to provision an IBM Cloud Object Storage or you can provide existing IBM Cloud Object Storage information to use it as storage for Manage application logs.

Role Variables
--------------
### cos_type
Required. Defines the storage provider type to be used to store Manage application's doclinks.
Currently available options are:

  - `ibm`: Configures IBM Cloud Object Storage as storage system for Manage doclinks.

When running this role, the [`cos_bucket`](../roles/cos_bucket.md) role will be executed underneath the covers to setup a new or existing targeted IBM Cloud object bucket to be used to store Manage docklinks, therefore make sure you set the expected variables to customize your Object Storage bucket accordingly to the desired provider.

- Environment Variable: `COS_TYPE`
- Default Value: None.

### mas_instance_id
Required. The instance ID of Maximo Application Suite. This will be used to lookup for Manage application resources.

- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### mas_workspace_id
Required. The workspace ID of Maximo Application Suite. This will be used to lookup for Manage application resources.

- Environment Variable: `MAS_WORKSPACE_ID`
- Default Value: None

### manage_workspace_cr_name
Optional. Name of the `ManageWorkspace` Custom Resource that will be targeted to configure the new PVC definitions.

- Environment Variable: `MANAGE_WORKSPACE_CR_NAME`
- Default Value: `$MAS_INSTANCE_ID-$MAS_WORKSPACE_ID`

Example Playbook
----------------
The following sample can be used to configure COS for an existing Manage application instance.

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_workspace_id: masdev
    cos_type: ibm
    cos_instance_name: cos-masinst1
    ibmcos_bucket_name: manage-doclinks-bucket
    ibmcloud_apikey: xxxx
  roles:
    - ibm.mas_devops.suite_manage_doclinks_config
```

The following sample playbook can be used to provision COS in IBM Cloud and configure COS for an existing Manage application instance.

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_workspace_id: masdev
    db2_instance_name: db2w-manage
    cos_type: ibm
    cos_instance_name: cos-masinst1
    ibmcos_bucket_name: manage-logs-bucket
    ibmcloud_apikey: xxxx
  roles:
    - ibm.mas_devops.cos
    - ibm.mas_devops.suite_manage_doclinks_config
```

License
-------

EPL-2.0
