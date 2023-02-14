suite_manage_customer_files_config
===
This role extends support for configuring S3 / Cloud Object Storage to store **Manage** application customer files.
**Note:** This role should be executed **after** Manage application is deployed and activated as it needs Manage up and running prior configuring customer files features.

You can run `cos` role to provision an IBM Cloud Object Storage or you can provide existing IBM Cloud Object Storage or AWS S3 information to use it as storage for Manage application customer files.

As part of this role, three defaulted buckets will be created:

- "{{ mas_instance_id }}-{{ mas_workspace_id }}-custfiles"
- "{{ mas_instance_id }}-{{ mas_workspace_id }}-custfilesbackup"
- "{{ mas_instance_id }}-{{ mas_workspace_id }}-custfilesrecovery"

These buckets will be used to store Manage's customer documents and files, and also will be used on the backup and recovery process.

Role Variables
--------------
### cos_type
Required. Defines the storage provider type to be used to store Manage application's customer files.
Currently available options are:

  - `ibm`: Configures IBM Cloud Object Storage as storage system for Manage attachments. 
  - `aws`: Configures Amazon S3 buckets as storage system for Manage attachments. 
  
  **Note:** If using `ibm` or `aws` as attachments provider, the [`cos_bucket`](../roles/cos_bucket.md) role will be executed to setup a new or existing targeted COS bucket to be used to store Manage attachments, therefore make sure you set the expected variables to customize your COS bucket for Manage attachments.

To run this role successfully for AWS S3 buckets, you must have already installed the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).
Also, you need to have AWS user credentials configured via `aws configure` command or simply export `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables with your corresponding AWS username credentials prior running this role.

- Environment Variable: `COS_TYPE`
- Default Value: None.

### custfiles_bucketname
Optional. The main customer files bucket name.

- Environment Variable: `MANAGE_CUSTFILES_BUCKET_NAME`
- Default Value: `{{ mas_instance_id }}-{{ mas_workspace_id }}-custfiles`

### custfiles_bucketname_backup
Optional. The customer files bucket name used for backup.

- Environment Variable: `MANAGE_CUSTFILES_BACKUP_BUCKET_NAME`
- Default Value: `{{ mas_instance_id }}-{{ mas_workspace_id }}-custfilesbackup`

### custfiles_bucketname_recovery
Optional. The customer files bucket name used for recovery.

- Environment Variable: `MANAGE_CUSTFILES_RECOVERY_BUCKET_NAME`
- Default Value: `{{ mas_instance_id }}-{{ mas_workspace_id }}-custfilesrecovery`

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
    ibmcloud_apikey: xxxx
  roles:
    - ibm.mas_devops.suite_manage_customer_files_config
```

The following sample playbook can be used to provision COS in IBM Cloud and configure COS for an existing Manage application instance.

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_workspace_id: masdev
    cos_type: ibm
    cos_instance_name: cos-masinst1
    ibmcloud_apikey: xxxx
  roles:
    - ibm.mas_devops.cos
    - ibm.mas_devops.suite_manage_customer_files_config
```

The following sample can be used to configure AWS S3 buckets for an existing Manage application instance.

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_workspace_id: masdev
    cos_type: aws
  roles:
    - ibm.mas_devops.suite_manage_customer_files_config
```

License
-------

EPL-2.0
