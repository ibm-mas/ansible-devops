suite_manage_logging_config
===
This role extends support for configuring IBM Cloud Object Storage to storage **Manage** application server logs.
**Note:** This role should be executed **after** Manage application is deployed and activated as it needs Manage up and running prior configuring logging features.

The default for Manage logging configuration is to use IBM Cloud Object Storage as persistent storage for Manage logging. You can run `cos` role to provision an IBM Cloud Object Storage or you can provide existing IBM Cloud Object Storage information to use it as storage for Manage application logs.

In addition, you can also define a AWS S3 bucket as storage system for Manage logs.

Role Variables
--------------
### cos_type
Required. Defines the storage provider type to be used to store Manage application's logs.
Available options are:

  - `ibm`: Configures IBM Cloud Object Storage as storage system for Manage logging.
  - `aws`: Configures AWS S3 buckets as storage system for Manage logging.

When running this role, the [`cos_bucket`](../roles/cos_bucket.md) role will be executed underneath the covers to setup a new or existing targeted IBM Cloud object or AWS S3 storage bucket to be used to store Manage logs, therefore make sure you set the expected variables to customize your Object Storage bucket accordingly to the desired provider.

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
    cos_type: ibm
    db2_instance_name: db2w-manage
    cos_instance_name: cos-masinst1
    ibmcos_bucket_name: manage-logs-bucket
    ibmcloud_apikey: xxxx
  roles:
    - ibm.mas_devops.suite_manage_logging_config
```

The following sample can be used to configure AWS S3 for an existing Manage application instance.

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_workspace_id: masdev
    cos_type: aws
    cos_bucket_action: create
    aws_bucket_name: manage-logs-bucket
    aws_region: us-east-2
    aws_bucket_versioning_flag: True
    aws_bucket_encryption: '{"Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]}'
    db2_instance_name: db2w-manage
  roles:
    - ibm.mas_devops.suite_manage_logging_config
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
    - ibm.mas_devops.suite_manage_logging_config
```

License
-------

EPL-2.0
