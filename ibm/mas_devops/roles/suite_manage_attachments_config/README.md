suite_manage_attachments_config
===

This role extends support for configuring IBM Cloud Object Storage or Persistent Volume/File Storages for **Manage** application attachments.
**Note:** This role should be executed **after** Manage application is deployed and activated as it needs Manage up and running prior configuring attachments features.


The default for Manage attachments configuration is to use your cluster's default file storage system as persistent storage.

Although, you can optionally define IBM Cloud Object Storage.
You can run `cos` role to provision an IBM Cloud Object Storage or you can provide existing IBM Cloud Object Storage information to use it as storage for Manage application attachments

Role Variables
--------------
### mas_manage_attachments_provider
Required. Defines the storage provider type to be used to store Manage application's attachments.
Available options are:

  - `filestorage` (default option): Configures cluster's file storage system for Manage attachments.
  - `ibm`: Configures IBM Cloud Object Storage as storage system for Manage attachments. 
  - `aws`: Configures Amazon S3 buckets as storage system for Manage attachments.
  
  **Note:** If using `ibm` or `aws` as attachments provider, the [`cos_bucket`](../roles/cos_bucket.md) role will be executed to setup a new or existing targeted COS bucket to be used to store Manage attachments, therefore make sure you set the expected variables to customize your COS bucket for Manage attachments.

To run this role successfully for AWS s3 buckets, you must have already installed the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).
Also, you need to have AWS user credentials configured via `aws configure` command or simply export `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables with your corresponding AWS username credentials prior running this role.

- Environment Variable: `MAS_MANAGE_ATTACHMENTS_PROVIDER`
- Default Value: `filestorage`

### mas_instance_id
Required. The instance ID of Maximo Application Suite. This will be used to lookup for Manage application resources.

- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### mas_workspace_id
Required. The workspace ID of Maximo Application Suite. This will be used to lookup for Manage application resources.

- Environment Variable: `MAS_WORKSPACE_ID`
- Default Value: None

### db2_instance_name
Required. The DB2 Warehouse instance name that stores your Manage application tables and data. This will be used to lookup for Manage application database and update it with the IBM Object Storage configuration.

- Environment Variable: `DB2_INSTANCE_NAME` # e.g. db2u-iot or db2wh-1658148844550964
- Default Value: None

### db2_namespace
Optional. The namespace in your cluster that hosts the DB2 Warehouse instance name. This will be used to lookup for Manage application database and update it with the IBM Object Storage configuration. If you do not provide it, the role will try to find the Db2 Warehouse in `db2u` namespace.

- Environment Variable: `DB2_NAMESPACE` # e.g. db2u
- Default Value: `db2u`

### db2_dbname
 Name of the database within the instance.

- Optional
- Environment Variable: `DB2_DBNAME`
- Default: `BLUDB`

Example Playbook
----------------
The following sample can be used to configure COS for an existing Manage application instance.

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_workspace_id: masdev
    db2_instance_name: db2w-manage
    cos_instance_name: cos-masinst1
    ibmcos_bucket_name: manage-attachments-bucket
    ibmcloud_apikey: xxxx
    mas_manage_attachments_provider: ibm
  roles:
    - ibm.mas_devops.suite_manage_attachments_config
```

The following sample playbook can be used to provision COS in IBM Cloud and configure COS for an existing Manage application instance's attachments.

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_workspace_id: masdev
    db2_instance_name: db2w-manage
    cos_instance_name: cos-masinst1
    ibmcos_bucket_name: manage-attachments-bucket
    ibmcloud_apikey: xxxx
    mas_manage_attachments_provider: ibm
  roles:
    - ibm.mas_devops.cos
    - ibm.mas_devops.suite_manage_attachments_config
```

The following sample playbook can be used to deploy Manage with default persistent storage for Manage attachments (PVC mount path `/DOCLINKS`), and configure Manage system properties with the corresponding attachments settings.

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
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
