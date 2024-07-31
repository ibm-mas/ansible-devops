suite_manage_attachments_config
===

This role extends support for configuring IBM Cloud Object Storage or Persistent Volume/File Storages for **Manage** application attachments.

**Note:** This role should be executed **after** Manage application is deployed and activated as it needs Manage up and running prior configuring attachments features.

By default, Manage attachments configuration uses `filestorage` provider; it corresponds to your cluster's default file storage system to persist the files. Alternatively, you can provide an existing IBM Cloud Object Storage by using `ibm` provider, or even provision a new instance by using `cos` role. Finally, an existing AWS S3 service can also be provided via `aws` provider by this same role (see details in the Role Varilables below)

Role Variables
--------------

### mas_manage_attachments_provider
Required. Defines the storage provider type to be used to store Manage application's attachments.
Available options are:

  - `filestorage` (default option): Configures cluster's file storage system for Manage attachments.
  - `ibm`: Configures IBM Cloud Object Storage as storage system for Manage attachments. 
  - `aws`: Configures Amazon S3 buckets as storage system for Manage attachments.
  
  **Note:** If using `ibm` or `aws` as attachments provider, the [`cos_bucket`](../roles/cos_bucket.md) role will be executed to setup a new or existing targeted COS bucket to be used to store Manage attachments, therefore make sure you set the expected variables to customize your COS bucket for Manage attachments, i.e. `IBMCLOUD_APIKEY` and `COS_INSTANCE_NAME`.

  **Note about S3:** To run this role successfully for AWS s3 buckets, you must have already installed the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).Also, you need to have AWS user credentials configured via `aws configure` command or simply export `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables with your corresponding AWS username credentials prior running this role.

  - Environment Variable: `MAS_MANAGE_ATTACHMENTS_PROVIDER`
  - Default Value: `filestorage`

### mas_manage_attachment_configuration_mode
Required. Defines how attachment properties will be configured in Manage. Possible values are `cr` and `db`.

When `cr` is selected, attachment properties will be entered in ManageWorkspace CR for each bundle, under `bundleProperties` key. For this mode, `manage_workspace_cr_name` must be informed;

When `db` is selected, attachment properties will be updated directly in the database via SQL updates. For this mode, `db2_instance_name`, `db2_namespace` and `db2_dbname` must be informed.

- Environment Variable: `MAS_MANAGE_ATTACHMENT_CONFIGURATION_MODE`
- Default Value: `db`

### mas_instance_id
Required. The instance ID of Maximo Application Suite. This will be used to lookup for Manage application resources.

- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### mas_workspace_id
Required. The workspace ID of Maximo Application Suite. This will be used to lookup for Manage application resources.

- Environment Variable: `MAS_WORKSPACE_ID`
- Default Value: None

### manage_workspace_cr_name
Optional. Required when `mas_manage_attachment_configuration_mode` is set as `cr`. Name of the `ManageWorkspace` Custom Resource that will be targeted to configure the new PVC definitions.

- Environment Variable: `MANAGE_WORKSPACE_CR_NAME`
- Default Value: `$MAS_INSTANCE_ID-$MAS_WORKSPACE_ID`

### db2_instance_name
Optional. Required when `mas_manage_attachment_configuration_mode` is set as `db`. The DB2 Warehouse instance name that stores your Manage application tables and data. This will be used to lookup for Manage application database and update it with the IBM Object Storage configuration.

  **Note**: in order to obtain the value for this variable, go to the namespace where db2 is installed and look for the pod where `label=engine`. Select/describe the pod representing your database, and look for the value of label `app`. That is your db2 instance name.

- Environment Variable: `DB2_INSTANCE_NAME` # e.g. db2u-iot or db2wh-1658148844550964
- Default Value: None

### db2_namespace
Optional. Required when `mas_manage_attachment_configuration_mode` is set as `db`. The namespace in your cluster that hosts the DB2 Warehouse instance name. This will be used to lookup for Manage application database and update it with the IBM Object Storage configuration. If you do not provide it, the role will try to find the Db2 Warehouse in `db2u` namespace.

- Environment Variable: `DB2_NAMESPACE` # e.g. db2u
- Default Value: `db2u`

### db2_dbname
Optional. Required when `mas_manage_attachment_configuration_mode` is set as `db`. Name of the database within the instance.

- Environment Variable: `DB2_DBNAME`
- Default: `BLUDB`

Example Playbook
----------------
The following sample can be used to configure COS for an existing Manage application instance's attachments via ManageWorkspace CR update (note `cr` as configuration mode + `ma_instance_id` and `mas_workspace_id`, which will be used to infer the CR name):

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_manage_attachment_configuration_mode: cr
    mas_instance_id: masinst1
    mas_workspace_id: masdev
    cos_instance_name: cos-masinst1
    cos_bucket_name: manage-attachments-bucket
    ibmcloud_apikey: xxxx
    mas_manage_attachments_provider: ibm
  roles:
    - ibm.mas_devops.suite_manage_attachments_config
```

The following sample playbook can be used to provision COS in IBM Cloud and configure COS for an existing Manage application instance's attachments via SQL updates in database (note `db` as configuration mode + `db2_instance_name`):

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_manage_attachment_configuration_mode: db
    mas_instance_id: masinst1
    mas_workspace_id: masdev
    db2_instance_name: db2w-manage
    cos_instance_name: cos-masinst1
    cos_bucket_name: manage-attachments-bucket
    ibmcloud_apikey: xxxx
    mas_manage_attachments_provider: ibm
  roles:
    - ibm.mas_devops.cos
    - ibm.mas_devops.suite_manage_attachments_config
```

The following sample playbook can be used to deploy Manage with default persistent storage for Manage attachments (PVC mount path `/DOCLINKS`), and configure Manage system properties with the corresponding attachments settings; via SQL updates in database:

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_manage_attachment_configuration_mode: db
    mas_app_id: manage
    mas_app_channel: 8.4.x
    mas_instance_id: masinst1
    mas_workspace_id: masdev
    db2_instance_name: db2w-manage
    mas_app_settings_persistent_volumes_flag: true
    mas_manage_attachments_provider: filestorage
  roles:
    - ibm.mas_devops.db2
    - ibm.mas_devops.suite_db2_setup_for_manage
    - ibm.mas_devops.suite_config
    - ibm.mas_devops.suite_app_install
    - ibm.mas_devops.suite_app_config
    - ibm.mas_devops.suite_manage_attachments_config
```

The following sample can be used to configure AWS S3 buckets for an existing Manage application instance's attachments.

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_workspace_id: masdev
    db2_instance_name: db2w-manage
    aws_bucket_name: manage-attachments-bucket
    mas_manage_attachments_provider: aws
  roles:
    - ibm.mas_devops.suite_manage_attachments_config
```

License
-------

EPL-2.0
