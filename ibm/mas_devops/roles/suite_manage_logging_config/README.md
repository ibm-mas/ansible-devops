# suite_manage_logging_config

This role extends support for configuring IBM Cloud Object Storage to store **Manage** application server logs.

**Note:** This role should be executed **after** Manage application is deployed and activated as it needs Manage up and running prior configuring logging features.

The default for Manage logging configuration is to use IBM Cloud Object Storage as persistent storage for Manage logging. You can run `cos` role to provision an IBM Cloud Object Storage or you can provide existing IBM Cloud Object Storage information to use it as storage for Manage application logs.

In addition, you can also define an AWS S3 bucket as storage system for Manage logs.

## Role Variables

### Storage Configuration

#### cos_type
Defines the storage provider type to be used to store Manage application's logs. Available options are `ibm` or `aws`.

- **Required**
- Environment Variable: `COS_TYPE`
- Default Value: None

**Provider Options:**
- `ibm`: Configures IBM Cloud Object Storage as storage system for Manage logging.
- `aws`: Configures AWS S3 buckets as storage system for Manage logging.

**Note:** When running this role, the [`cos_bucket`](../roles/cos_bucket.md) role will be executed underneath the covers to setup a new or existing targeted IBM Cloud object or AWS S3 storage bucket to be used to store Manage logs, therefore make sure you set the expected variables to customize your Object Storage bucket accordingly to the desired provider.

### MAS Configuration

#### mas_instance_id
The instance ID of Maximo Application Suite. This will be used to lookup for Manage application resources.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

#### mas_workspace_id
The workspace ID of Maximo Application Suite. This will be used to lookup for Manage application resources.

- **Required**
- Environment Variable: `MAS_WORKSPACE_ID`
- Default Value: None

### Database Configuration

#### db2_instance_name
The DB2 Warehouse instance name that stores your Manage application tables and data. This will be used to lookup for Manage application database and update it with the Object Storage configuration.

- **Required**
- Environment Variable: `DB2_INSTANCE_NAME`
- Default Value: None

#### db2_namespace
The namespace in your cluster that hosts the DB2 Warehouse instance name. This will be used to lookup for Manage application database and update it with the Object Storage configuration. If you do not provide it, the role will try to find the Db2 Warehouse in `db2u` namespace.

- **Optional**
- Environment Variable: `DB2_NAMESPACE`
- Default Value: `db2u`

#### db2_dbname
Name of the database within the instance.

- **Optional**
- Environment Variable: `DB2_DBNAME`
- Default Value: `BLUDB`

## Example Playbook

### Configure IBM Cloud COS for Existing Manage Instance
The following sample can be used to configure COS for an existing Manage application instance:

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_workspace_id: masdev
    cos_type: ibm
    db2_instance_name: db2w-manage
    cos_instance_name: cos-masinst1
    cos_bucket_name: manage-logs-bucket
    ibmcloud_apikey: xxxx
  roles:
    - ibm.mas_devops.suite_manage_logging_config
```

### Configure AWS S3 for Existing Manage Instance
The following sample can be used to configure AWS S3 for an existing Manage application instance:

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

### Provision and Configure IBM Cloud COS
The following sample playbook can be used to provision COS in IBM Cloud and configure COS for an existing Manage application instance:

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_workspace_id: masdev
    db2_instance_name: db2w-manage
    cos_type: ibm
    cos_instance_name: cos-masinst1
    cos_bucket_name: manage-logs-bucket
    ibmcloud_apikey: xxxx
  roles:
    - ibm.mas_devops.cos
    - ibm.mas_devops.suite_manage_logging_config
```

## License
EPL-2.0
