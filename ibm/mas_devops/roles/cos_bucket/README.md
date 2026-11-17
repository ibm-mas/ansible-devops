# cos_bucket
This role extends support to create or deprovision Cloud Object Storage buckets.

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`cos_type`](#cos_type) | Yes | None |
| [`cos_bucket_action`](#cos_bucket_action) | No | `create` |
| [`cos_bucket_name`](#cos_bucket_name) | No | `<mas_instance_id>-<mas_workspace_id>-bucket` |
| [`cos_bucket_storage_class`](#cos_bucket_storage_class) | No | `smart` |
| [`cos_instance_name`](#cos_instance_name) | Conditional | None |
| [`cos_location_info`](#cos_location_info) | No | `global` |
| [`cos_bucket_region_location_type`](#cos_bucket_region_location_type) | No | `cross_region_location` |
| [`cos_bucket_region_location`](#cos_bucket_region_location) | No | Derived from `ibmcloud_region` |
| [`ibmcloud_region`](#ibmcloud_region) | No | `us-east` |
| [`cos_url`](#cos_url) | No | `https://s3.<region>.cloud-object-storage.appdomain.cloud` |
| [`cos_resource_key_iam_role`](#cos_resource_key_iam_role) | No | `Manager` |
| [`ibmcloud_apikey`](#ibmcloud_apikey) | Conditional | None |
| [`ibmcloud_resourcegroup`](#ibmcloud_resourcegroup) | No | `Default` |
| [`cos_bucket_versioning_flag`](#cos_bucket_versioning_flag) | No | `True` |
| [`cos_bucket_expire_rule_id`](#cos_bucket_expire_rule_id) | No | `delete_files` |
| [`cos_bucket_expire_rule_enable_flag`](#cos_bucket_expire_rule_enable_flag) | No | `True` |
| [`cos_bucket_expire_rule_days`](#cos_bucket_expire_rule_days) | No | `60` |
| [`cos_service_credentials_name`](#cos_service_credentials_name) | No | `{mas_instance_id}-{mas_workspace_id}-{cos_resource_key_iam_role lowercase}-key` |
| [`aws_bucket_name`](#aws_bucket_name) | No | `<mas_instance_id>-<mas_workspace_id>-bucket` |
| [`aws_region`](#aws_region) | No | `us-east-2` |
| [`aws_url`](#aws_url) | No | `https://s3.{aws_region}.amazonaws.com` |
| [`aws_bucket_versioning_flag`](#aws_bucket_versioning_flag) | No | `True` |
| [`aws_bucket_encryption`](#aws_bucket_encryption) | No | None |
| [`aws_bucket_force_deletion_flag`](#aws_bucket_force_deletion_flag) | No | `True` |

Variables marked Conditional are required only when `cos_type` is `ibm` (`cos_instance_name` and `ibmcloud_apikey`); when `cos_type` is `aws`, AWS credentials must be provided via environment variables or AWS CLI configuration.

### Bucket Provider and Action

#### cos_type

The Cloud Object Storage provider for bucket operations — `ibm` (IBM Cloud Object Storage) or `aws` (AWS S3).

- **Required**
- Environment Variable: `COS_TYPE`
- Default: None

The provider determines which set of configuration variables is required: `ibm` requires `ibmcloud_apikey`, `cos_instance_name`, and the IBM COS bucket settings below, while `aws` requires AWS credentials (via environment variables or AWS CLI configuration) and `aws_region`. Bucket names must be globally unique within each provider; IBM COS buckets support the smart, vault, cold, and flex storage classes, and AWS S3 buckets support versioning and encryption configurations.

#### cos_bucket_action

The action to perform on the bucket — `create` (create a new bucket with the specified storage class, region, and lifecycle settings) or `delete` (delete an existing bucket).

- **Optional**
- Environment Variable: `COS_BUCKET_ACTION`
- Default: `create`

!!! warning
    Bucket deletion is irreversible — all data in the bucket will be lost. Back up data before deleting, and verify the bucket name to avoid removing the wrong bucket. IBM COS bucket deletion may fail if the bucket contains objects; for AWS, deletion behavior depends on `aws_bucket_force_deletion_flag`.

### IBM Cloud Object Storage Buckets

#### cos_bucket_name

The name for the IBM Cloud Object Storage bucket — 3-63 characters, lowercase letters, numbers, hyphens, and periods only, starting and ending with a letter or number, and globally unique across all IBM Cloud COS (e.g. `prod-mas-workspace1-bucket`, `dev-maximo-data-bucket`).

- **Optional** (IBM COS only)
- Environment Variable: `COS_BUCKET_NAME`
- Default: `<mas_instance_id>-<mas_workspace_id>-bucket`

The default naming includes the MAS instance and workspace IDs for uniqueness. The name cannot be changed after creation (it requires recreation), appears in S3 API endpoints and URLs, and is globally visible — avoid including sensitive information.

#### cos_bucket_storage_class

The IBM Cloud COS storage class for the bucket — `smart` (automatically transitions data between hot and cool tiers based on access patterns; recommended and default), `vault` (data accessed less than once per month), `cold` (data accessed less than once per year), or `flex` (dynamic workloads with unpredictable access patterns).

- **Optional** (IBM COS only)
- Environment Variable: `COS_BUCKET_STORAGE_CLASS`
- Default: `smart`

The class determines storage pricing and data retrieval costs — lower-tier classes (vault, cold) have higher retrieval costs and latency. It cannot be changed after bucket creation, and availability varies by location type (`cos_bucket_region_location_type`).

#### cos_instance_name

The name of the IBM Cloud COS instance where the bucket will be created — must match an existing, case-sensitive COS instance name in your account (e.g. `mas-cos-instance`).

- **Required** when `cos_type` is `ibm`
- Environment Variable: `COS_INSTANCE_NAME`
- Default: None

The instance must exist in the specified resource group before running this role — use the `cos` role to provision it first. An incorrect name will cause bucket creation to fail.

#### cos_location_info

The geographic location of the IBM Cloud COS instance — `global`, a specific region code (`us-south`, `us-east`, `eu-gb`, `eu-de`), or a cross-region (`us`, `eu`, `ap`).

- **Optional** (IBM COS only)
- Environment Variable: None
- Default: `global`

Must match the location used when the COS instance was created; a mismatch will cause bucket operations to fail. The default `global` works for most deployments.

#### cos_bucket_region_location_type

The resiliency type for the IBM Cloud COS bucket — `cross_region_location` (data replicated across multiple regions; highest availability, ~99.99%; default), `region_location` (data stored in a single region; best performance, ~99.95%), or `single_site_location` (single data center; lowest cost and availability).

- **Optional** (IBM COS only)
- Environment Variable: `COS_BUCKET_REGION_LOCATION_TYPE`
- Default: `cross_region_location`

Determines which values are valid for `cos_bucket_region_location` and cannot be changed after bucket creation. `cross_region_location` is recommended for production MAS workloads; `region_location` suits performance-sensitive workloads.

#### cos_bucket_region_location

The specific region(s) for the IBM Cloud COS bucket — `us`, `eu`, or `ap` for `cross_region_location`; `us-south`, `us-east`, `eu-gb`, `eu-de`, `jp-tok`, `au-syd`, `ca-tor`, `jp-osa`, or `br-sao` for `region_location`; specific data center codes for `single_site_location`.

- **Optional** (IBM COS only)
- Environment Variable: `COS_BUCKET_REGION_LOCATION`
- Default: Derived from `ibmcloud_region` (e.g. `us`, `eu`, `ap`)

Determines the physical location of data storage, affecting data residency compliance (GDPR, data sovereignty) and network latency. Must be compatible with `cos_bucket_region_location_type`, cannot be changed after bucket creation, and should align with `cos_url` for optimal performance.

#### ibmcloud_region

The IBM Cloud region used to derive the default cross-region location — e.g. `us-east`, `us-south`, `eu-gb`, `eu-de`, `jp-tok`.

- **Optional** (IBM COS only)
- Environment Variable: `IBMCLOUD_REGION`
- Default: `us-east`

Only used when `cos_bucket_region_location_type` is `cross_region_location` and `cos_bucket_region_location` is not explicitly set: `us-*` regions derive the `us` cross-region, `eu-*` derive `eu`, and `jp-*` / `au-*` derive `ap`.

#### cos_url

The IBM Cloud COS S3 API endpoint URL — regional endpoints such as `https://s3.<region>.cloud-object-storage.appdomain.cloud`, cross-region endpoints such as `https://s3.us.cloud-object-storage.appdomain.cloud`, or private/direct endpoints (`https://s3.private.<region>.cloud-object-storage.appdomain.cloud`, `https://s3.direct.<region>.cloud-object-storage.appdomain.cloud`).

- **Optional** (IBM COS only)
- Environment Variable: `COS_REGION_LOCATION_URL`
- Default: `https://s3.<region>.cloud-object-storage.appdomain.cloud` (constructed from `cos_bucket_region_location`)

Should match the bucket's region location for best performance; private endpoints provide better security and lower costs for in-cloud access and are recommended for OpenShift clusters in IBM Cloud. Not applicable for AWS buckets (see `aws_url`).

#### cos_resource_key_iam_role

The IAM role for COS service credentials created during bucket setup — `Manager` (full access to buckets and objects; default), `Writer` (read and write access to objects), or `Reader` (read-only access to objects).

- **Optional** (IBM COS only)
- Environment Variable: `COS_RESOURCE_KEY_IAM_ROLE`
- Default: `Manager`

Lower privilege roles may limit functionality — the `Manager` role is required for full bucket management.

#### ibmcloud_apikey

The IBM Cloud API key for bucket operations — a 44-character alphanumeric key with COS bucket management and resource group access permissions.

- **Required** when `cos_type` is `ibm`
- Environment Variable: `IBMCLOUD_APIKEY`
- Default: None

Authenticates all IBM Cloud COS operations and determines which account owns the bucket. It can alternatively be provided via the `COS_APIKEY` environment variable (`cos_apikey`), which falls back to this key when unset. Store API keys securely and never commit them to version control.

#### ibmcloud_resourcegroup

The IBM Cloud resource group containing the COS instance — any existing, case-sensitive resource group name in your account (e.g. `Default`, `Production`, `MAS-Resources`).

- **Optional** (IBM COS only)
- Environment Variable: `IBMCLOUD_RESOURCEGROUP`
- Default: `Default`

Must match the resource group used when creating the COS instance (the same one used in the `cos` role), and the API key must have access to it. It can alternatively be provided via the `COS_RESOURCEGROUP` environment variable (`cos_resourcegroup`), which falls back to this value when unset.

#### cos_bucket_versioning_flag

Controls whether to enable object versioning for the IBM Cloud COS bucket.

- **Optional** (IBM COS only)
- Environment Variable: `COS_BUCKET_VERSIONING_FLAG`
- Default: `True`

#### cos_bucket_expire_rule_id

Identifier for the rule that expires the current version of objects in the IBM Cloud COS bucket.

- **Optional** (IBM COS only)
- Environment Variable: `COS_BUCKET_EXPIRE_RULE_ID`
- Default: `delete_files`

The expiry rule removes the current version of objects after `cos_bucket_expire_rule_days` days when `cos_bucket_expire_rule_enable_flag` is enabled — see the [IBM Cloud COS expiry documentation](https://cloud.ibm.com/docs/cloud-object-storage?topic=cloud-object-storage-expiry).

#### cos_bucket_expire_rule_enable_flag

Whether to enable the object expiry rule for the IBM Cloud COS bucket.

- **Optional** (IBM COS only)
- Environment Variable: `COS_BUCKET_EXPIRE_RULE_ENABLE_FLAG`
- Default: `True`

#### cos_bucket_expire_rule_days

Number of days after which the current version of objects in the IBM Cloud COS bucket expires.

- **Optional** (IBM COS only)
- Environment Variable: `COS_BUCKET_EXPIRE_RULE_DAYS`
- Default: `60`

#### cos_service_credentials_name

The name of the COS service credentials created and retrieved for the bucket.

- **Optional** (IBM COS only)
- Environment Variable: `COS_SERVICE_CREDENTIALS_NAME`
- Default: `{mas_instance_id}-{mas_workspace_id}-{cos_resource_key_iam_role lowercase}-key`

For IBM Cloud, the username in the generated service credentials corresponds to this credentials name.

### AWS S3 Buckets

To run this role successfully for AWS s3 buckets, you must have already installed the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).
Also, you need to have AWS user credentials configured via `aws configure` command or simply export `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables with your corresponding AWS username credentials prior running this role.

#### aws_bucket_name

The name for the AWS S3 bucket — 3-63 characters, lowercase letters, numbers, hyphens, and periods only, starting and ending with a letter or number, globally unique across all AWS S3, without consecutive periods or underscores, and not formatted as an IP address (e.g. `prod-mas-workspace1-bucket`, `dev-maximo-data-bucket`).

- **Optional** (AWS S3 only)
- Environment Variable: `COS_BUCKET_NAME`
- Default: `<mas_instance_id>-<mas_workspace_id>-bucket`

The default naming includes the MAS instance and workspace IDs for uniqueness. The name cannot be changed after creation (it requires recreation), appears in S3 API endpoints and URLs, and is globally visible — avoid including sensitive information. Not used for IBM COS buckets (see `cos_bucket_name`).

#### aws_region

The AWS region where the S3 bucket will be created — e.g. `us-east-1`, `us-east-2`, `us-west-2`, `eu-west-1`, `eu-central-1`, `ap-southeast-1`.

- **Optional** (AWS S3 only)
- Environment Variable: `AWS_REGION`
- Default: `us-east-2`

Choose a region close to your OpenShift cluster and users for optimal performance, considering data residency compliance (GDPR, data sovereignty) — pricing varies by region, some regions may have capacity constraints, and the region cannot be changed after bucket creation.

#### aws_url

The AWS S3 API endpoint URL used for bucket operations.

- **Optional** (AWS S3 only)
- Environment Variable: `COS_REGION_LOCATION_URL`
- Default: `https://s3.{aws_region}.amazonaws.com`

Should match the bucket's region.

#### aws_bucket_versioning_flag

Controls whether to enable versioning for the AWS S3 bucket.

- **Optional** (AWS S3 only)
- Environment Variable: `COS_BUCKET_VERSIONING_FLAG`
- Default: `True`

Versioning keeps multiple variants of each object in the bucket, providing rollback protection against accidental deletion or overwrite (recommended for production) at the cost of increased storage, since all versions consume space. Once enabled, versioning cannot be fully disabled (only suspended), and versioned buckets cannot be force-deleted (see `aws_bucket_force_deletion_flag`).

#### aws_bucket_encryption

The default server-side encryption configuration for the AWS S3 bucket, as a JSON-formatted string — e.g. `'{"Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]}'` for S3-managed keys, or `'{"Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "aws:kms", "KMSMasterKeyID": "arn:aws:kms:region:account:key/key-id"}}]}'` for KMS-managed keys.

- **Optional** (AWS S3 only)
- Environment Variable: `COS_BUCKET_ENCRYPTION`
- Default: None

When set, all objects uploaded to the bucket are automatically encrypted. `AES256` is simpler and has no additional cost; `aws:kms` provides better key management and audit trails but incurs additional costs. Encryption can be changed after bucket creation.

#### aws_bucket_force_deletion_flag

Controls whether to force-delete bucket contents before deleting the AWS S3 bucket — `True` (default) automatically deletes all objects first; `False` fails if the bucket contains any objects (safer, requires manual cleanup).

- **Optional** (AWS S3 only)
- Environment Variable: `COS_BUCKET_FORCE_DELETION_FLAG`
- Default: `True`

Only takes effect when `cos_bucket_action` is `delete`, and only works if versioning is disabled — versioned buckets cannot be force-deleted (`aws_bucket_versioning_flag` must be `False`).

!!! warning
    Force deletion permanently removes all data in the bucket and is irreversible. Back up data before force deletion.

## Example Playbook

Create the IBM Cloud Object storage bucket.

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    cos_type: ibm
    cos_bucket_action: create
    cos_bucket_name: my-ibm-bucket
    cos_instance_name: my-ibmcos-instance-name
    ibmcloud_apikey: my-ibm-cloud-apikey
  roles:
    - ibm.mas_devops.cos_bucket
```

Create the AWS S3 storage bucket.

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    cos_type: aws
    cos_bucket_action: create
    aws_bucket_name: my-aws-bucket
    aws_region: us-east-2
    aws_bucket_versioning_flag: True
    aws_bucket_encryption: '{"Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]}'
  roles:
    - ibm.mas_devops.cos_bucket
```

## License

EPL-2.0
