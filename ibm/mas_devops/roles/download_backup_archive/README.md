# download_backup_archive
Downloads and extracts MAS backup archives from AWS S3 or Artifactory.

This role automates the process of downloading MAS backup archives from remote storage locations and extracting them to a local directory for restore operations. It supports downloading from both AWS S3 (or S3-compatible storage) and Artifactory repositories. The role handles archive verification, extraction, and cleanup operations.

Key features:

- Downloads compressed tar.gz archives from AWS S3 or S3-compatible storage
- Downloads compressed tar.gz archives from Artifactory repositories
- **Support for downloading multiple archives in a single operation**
- **Auto-generation of archive names based on component versions**
- **Archive management option to keep downloaded archives organized**
- Automatic extraction of downloaded archives
- Configurable download timeouts for large archives
- **Optional** cleanup of temporary files after extraction
- Verification of downloaded archive integrity

## Prerequisites

### For S3 Download

- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) or boto3 Python library must be installed
- `amazon.aws` Ansible collection must be installed
- AWS credentials with S3 read permissions
- S3 bucket must exist and be accessible

### For Artifactory Download

- `curl` command-line tool must be installed
- Artifactory API token with download permissions
- Artifactory repository must exist and be accessible

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`mas_instance_id`](#mas_instance_id) | Yes | None |
| [`mas_restore_dir`](#mas_restore_dir) | Yes | None |
| [`backup_version`](#backup_version) | Yes | None |
| [`backup_archive_names`](#backup_archive_names) | No | Auto-generated from component versions |
| [`ibm_catalogs_backup_version`](#ibm_catalogs_backup_version) | No | Value of `backup_version` |
| [`certmanager_backup_version`](#certmanager_backup_version) | No | Value of `backup_version` |
| [`mongodb_backup_version`](#mongodb_backup_version) | No | Value of `backup_version` |
| [`sls_backup_version`](#sls_backup_version) | No | Value of `backup_version` |
| [`suite_backup_version`](#suite_backup_version) | No | Value of `backup_version` |
| [`manage_backup_version`](#manage_backup_version) | No | Value of `backup_version` |
| [`manage_db2_backup_version`](#manage_db2_backup_version) | No | Value of `backup_version` |
| [`facilities_backup_version`](#facilities_backup_version) | No | Value of `backup_version` |
| [`facilities_db2_backup_version`](#facilities_db2_backup_version) | No | Value of `backup_version` |
| [`aws_access_key_id`](#aws_access_key_id) | Conditional | None |
| [`aws_secret_access_key`](#aws_secret_access_key) | Conditional | None |
| [`s3_bucket_name`](#s3_bucket_name) | Conditional | None |
| [`s3_region`](#s3_region) | No | `us-east-1` |
| [`s3_endpoint_url`](#s3_endpoint_url) | No | None (uses AWS S3 endpoints) |
| [`artifactory_username`](#artifactory_username) | Conditional | None |
| [`artifactory_token`](#artifactory_token) | Conditional | None |
| [`artifactory_repository`](#artifactory_repository) | Conditional | None |
| [`artifactory_url`](#artifactory_url) | No | `https://na.artifactory.swg-devops.com/artifactory` |
| [`backup_temp_dir`](#backup_temp_dir) | No | `<mas_restore_dir>/mas-<mas_instance_id>-restore-<backup_version>` |
| [`download_timeout`](#download_timeout) | No | `10800` |
| [`extract_archive`](#extract_archive) | No | `true` |
| [`cleanup_archive`](#cleanup_archive) | No | `true` |
| [`include_sls_archive`](#include_sls_archive) | No | `true` |
| [`include_mongo_archive`](#include_mongo_archive) | No | `true` |
| [`include_manage_app_archive`](#include_manage_app_archive) | No | `true` |
| [`include_manage_db_archive`](#include_manage_db_archive) | No | `true` |
| [`include_facilities_app_archive`](#include_facilities_app_archive) | No | `true` |
| [`include_facilities_db_archive`](#include_facilities_db_archive) | No | `true` |

The download source determines which credentials are required: provide the S3 variables to download from AWS S3 or S3-compatible storage, or the Artifactory variables to download from Artifactory. If S3 credentials are provided, S3 download takes precedence over Artifactory.

### Restore Target

#### mas_instance_id

Instance ID of the MAS instance, used to identify the backup directories.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

#### mas_restore_dir

Directory where the backup archive will be downloaded and extracted — the parent directory where all component backup directories will be restored.

- **Required**
- Environment Variable: `MAS_RESTORE_DIR`
- Default: None

### Backup Selection

#### backup_version

Version identifier for the backup to download. This must match the version used when the backup was created; when downloading multiple archives it is used as the default version for all components unless specific component versions are provided.

- **Required**
- Environment Variable: `BACKUP_VERSION`
- Default: None

#### backup_archive_names

List of archive names to download, provided either as a comma-separated string (`"archive1.tar.gz,archive2.tar.gz"`) or as a list (`["archive1.tar.gz", "archive2.tar.gz"]`).

- **Optional**
- Environment Variable: `BACKUP_ARCHIVE_NAMES`
- Default: Auto-generated from component versions

When not provided, the role auto-generates archive names based on `mas_instance_id` and the component backup versions (for example `mas-<mas_instance_id>-backup-<version>-suite.tar.gz`), filtered by the `include_*_archive` variables.

### Component-Specific Backup Versions

#### ibm_catalogs_backup_version

Backup version for the IBM catalogs component, used to auto-generate the `-catalog.tar.gz` archive name when `backup_archive_names` is not provided.

- **Optional**
- Environment Variable: `IBM_CATALOGS_BACKUP_VERSION`
- Default: Value of `backup_version`

#### certmanager_backup_version

Backup version for the cert-manager component, used to auto-generate the `-certmanager.tar.gz` archive name when `backup_archive_names` is not provided.

- **Optional**
- Environment Variable: `CERTMANAGER_BACKUP_VERSION`
- Default: Value of `backup_version`

#### mongodb_backup_version

Backup version for the MongoDB component, used to auto-generate the `-mongoce.tar.gz` archive name when `backup_archive_names` is not provided.

- **Optional**
- Environment Variable: `MONGODB_BACKUP_VERSION`
- Default: Value of `backup_version`

#### sls_backup_version

Backup version for the SLS (Suite License Service) component, used to auto-generate the `-sls.tar.gz` archive name when `backup_archive_names` is not provided.

- **Optional**
- Environment Variable: `SLS_BACKUP_VERSION`
- Default: Value of `backup_version`

#### suite_backup_version

Backup version for the MAS Suite component, used to auto-generate the `-suite.tar.gz` archive name when `backup_archive_names` is not provided.

- **Optional**
- Environment Variable: `SUITE_BACKUP_VERSION`
- Default: Value of `backup_version`

#### manage_backup_version

Backup version for the Manage application component, used to auto-generate the `-app-manage.tar.gz` archive name when `backup_archive_names` is not provided.

- **Optional**
- Environment Variable: `MANAGE_BACKUP_VERSION`
- Default: Value of `backup_version`

#### manage_db2_backup_version

Backup version for the Manage Db2 component, used to auto-generate the `-db2u-manage.tar.gz` archive name when `backup_archive_names` is not provided.

- **Optional**
- Environment Variable: `MANAGE_DB2_BACKUP_VERSION`
- Default: Value of `backup_version`

#### facilities_backup_version

Backup version for the Facilities application component, used to auto-generate the `-app-facilities.tar.gz` archive name when `backup_archive_names` is not provided.

- **Optional**
- Environment Variable: `FACILITIES_BACKUP_VERSION`
- Default: Value of `backup_version`

#### facilities_db2_backup_version

Backup version for the Facilities Db2 component, used to auto-generate the `-db2u-facilities.tar.gz` archive name when `backup_archive_names` is not provided.

- **Optional**
- Environment Variable: `FACILITIES_DB2_BACKUP_VERSION`
- Default: Value of `backup_version`

### S3 Download

#### aws_access_key_id

AWS access key ID for authentication to S3 or S3-compatible storage.

- **Required** for S3 download
- Environment Variable: `S3_ACCESS_KEY_ID`
- Default: None

#### aws_secret_access_key

AWS secret access key for authentication to S3 or S3-compatible storage.

- **Required** for S3 download
- Environment Variable: `S3_SECRET_ACCESS_KEY`
- Default: None

#### s3_bucket_name

Name of the S3 bucket where the archive is stored.

- **Required** for S3 download
- Environment Variable: `S3_BUCKET_NAME`
- Default: None

#### s3_region

AWS region where the S3 bucket is located.

- **Optional**
- Environment Variable: `S3_REGION`
- Default: `us-east-1`

#### s3_endpoint_url

Custom S3 endpoint URL for S3-compatible storage services (e.g., MinIO, Wasabi, IBM Cloud Object Storage).

- **Optional**
- Environment Variable: `S3_ENDPOINT_URL`
- Default: None (uses AWS S3 endpoints)

### Artifactory Download

#### artifactory_username

Artifactory username for authentication.

- **Required** for Artifactory download
- Environment Variable: `ARTIFACTORY_USERNAME`
- Default: None

#### artifactory_token

Artifactory API token for authentication.

- **Required** for Artifactory download
- Environment Variable: `ARTIFACTORY_TOKEN`
- Default: None

#### artifactory_repository

Name of the Artifactory repository where the archive is stored.

- **Required** for Artifactory download
- Environment Variable: `ARTIFACTORY_REPOSITORY`
- Default: None

#### artifactory_url

Base URL of the Artifactory server (e.g., `https://artifactory.example.com/artifactory`).

- **Optional**
- Environment Variable: `ARTIFACTORY_URL`
- Default: `https://na.artifactory.swg-devops.com/artifactory`

### Download and Extraction Behavior

#### backup_temp_dir

Temporary directory where the archive will be downloaded before extraction. The directory is created if it doesn't exist and can be cleaned up after extraction.

- **Optional**
- Environment Variable: None
- Default: `<mas_restore_dir>/mas-<mas_instance_id>-restore-<backup_version>`

#### download_timeout

Maximum time in seconds to wait for the download to complete — useful for large archives or slow network connections.

- **Optional**
- Environment Variable: `DOWNLOAD_TIMEOUT_SECS`
- Default: `10800` (3 hours)

#### extract_archive

Whether to automatically extract the downloaded archive. Set to `false` to only download the archive without extracting it.

- **Optional**
- Environment Variable: `EXTRACT_ARCHIVE`
- Default: `true`

#### cleanup_archive

Whether to remove the archive file and temporary directory after successful extraction. Set to `false` to keep the downloaded archive.

- **Optional**
- Environment Variable: `CLEANUP_ARCHIVE`
- Default: `true`

### Component Archive Selection

#### include_sls_archive

Whether to download the SLS archive (`-sls.tar.gz`) from S3 or Artifactory. When set to `false`, the role automatically skips it, preventing unnecessary downloads when the SLS component restore is not needed.

- **Optional**
- Environment Variable: `INCLUDE_SLS_ARCHIVE`
- Default: `true`

#### include_mongo_archive

Whether to download the Mongo archive (`-mongoce.tar.gz`) from S3 or Artifactory. When set to `false`, the role automatically skips it, preventing unnecessary downloads when the Mongo component restore is not needed.

- **Optional**
- Environment Variable: `INCLUDE_MONGO_ARCHIVE`
- Default: `true`

#### include_manage_app_archive

Whether to download the Manage app archive (`-app-manage.tar.gz`) from S3 or Artifactory. When set to `false`, the role automatically skips it, preventing unnecessary downloads when the Manage component restore is not needed.

- **Optional**
- Environment Variable: `INCLUDE_MANAGE_APP_ARCHIVE`
- Default: `true`

#### include_manage_db_archive

Whether to download the Manage DB2 archive (`-db2u-manage.tar.gz`) from S3 or Artifactory. When set to `false`, the role automatically skips it, preventing unnecessary downloads when the Manage component restore is not needed.

- **Optional**
- Environment Variable: `INCLUDE_MANAGE_DB_ARCHIVE`
- Default: `true`

#### include_facilities_app_archive

Whether to download the Facilities app archive (`-app-facilities.tar.gz`) from S3 or Artifactory. When set to `false`, the role automatically skips it, preventing unnecessary downloads when the Facilities component restore is not needed.

- **Optional**
- Environment Variable: `INCLUDE_FACILITIES_APP_ARCHIVE`
- Default: `true`

#### include_facilities_db_archive

Whether to download the Facilities DB2 archive (`-db2u-facilities.tar.gz`) from S3 or Artifactory. When set to `false`, the role automatically skips it, preventing unnecessary downloads when the Facilities component restore is not needed.

- **Optional**
- Environment Variable: `INCLUDE_FACILITIES_DB_ARCHIVE`
- Default: `true`

## Example Playbook

### Download Multiple Archives from S3 (Auto-generated names)
After installing the Ansible Collection you can include this role in your own custom playbooks.

```yaml
- hosts: localhost
  vars:
    mas_instance_id: inst1
    mas_restore_dir: /restore/mas
    backup_version: "20260117-191500"
    aws_access_key_id: "{{ lookup('env', 'AWS_ACCESS_KEY_ID') }}"
    aws_secret_access_key: "{{ lookup('env', 'AWS_SECRET_ACCESS_KEY') }}"
    s3_bucket_name: my-mas-backups
    s3_region: us-west-2
  roles:
    - ibm.mas_devops.download_backup_archive
```

### Download Specific Archives from S3

```yaml
- hosts: localhost
  vars:
    mas_instance_id: inst1
    mas_restore_dir: /restore/mas
    backup_version: "20260117-191500"
    backup_archive_names:
      - mas-inst1-backup-20260117-191500-catalog.tar.gz
      - mas-inst1-backup-20260117-191500-suite.tar.gz
      - mas-inst1-backup-20260117-191500-manage.tar.gz
    aws_access_key_id: "{{ lookup('env', 'AWS_ACCESS_KEY_ID') }}"
    aws_secret_access_key: "{{ lookup('env', 'AWS_SECRET_ACCESS_KEY') }}"
    s3_bucket_name: my-mas-backups
    s3_region: us-west-2
  roles:
    - ibm.mas_devops.download_backup_archive
```

### Download with Different Component Versions

```yaml
- hosts: localhost
  vars:
    mas_instance_id: inst1
    mas_restore_dir: /restore/mas
    backup_version: "20260117-191500"
    mongodb_backup_version: "20260116-120000"
    manage_db2_backup_version: "20260115-100000"
    aws_access_key_id: "{{ lookup('env', 'AWS_ACCESS_KEY_ID') }}"
    aws_secret_access_key: "{{ lookup('env', 'AWS_SECRET_ACCESS_KEY') }}"
    s3_bucket_name: my-mas-backups
    s3_region: us-west-2
  roles:
    - ibm.mas_devops.download_backup_archive
```

### Artifactory Download

```yaml
- hosts: localhost
  vars:
    mas_instance_id: inst1
    mas_restore_dir: /restore/mas
    backup_version: "20260117-191500"
    artifactory_username: "{{ lookup('env', 'ARTIFACTORY_USERNAME') }}"
    artifactory_token: "{{ lookup('env', 'ARTIFACTORY_TOKEN') }}"
    artifactory_url: https://artifactory.example.com/artifactory
    artifactory_repository: mas-backups
  roles:
    - ibm.mas_devops.download_backup_archive
```

### S3-Compatible Storage (IBMcloud, MinIO, Wasabi, etc.)

```yaml
- hosts: localhost
  vars:
    mas_instance_id: inst1
    mas_restore_dir: /restore/mas
    backup_version: "20260117-191500"
    aws_access_key_id: "{{ lookup('env', 'S3_ACCESS_KEY') }}"
    aws_secret_access_key: "{{ lookup('env', 'S3_SECRET_KEY') }}"
    s3_bucket_name: mas-backups
    s3_region: us-east-1
    s3_endpoint_url: https://s3.example.com
  roles:
    - ibm.mas_devops.download_backup_archive
```

### Download Without Extraction

```yaml
- hosts: localhost
  vars:
    mas_instance_id: inst1
    mas_restore_dir: /restore/mas
    backup_version: "20260117-191500"
    extract_archive: false
    cleanup_archive: false
    aws_access_key_id: "{{ lookup('env', 'AWS_ACCESS_KEY_ID') }}"
    aws_secret_access_key: "{{ lookup('env', 'AWS_SECRET_ACCESS_KEY') }}"
    s3_bucket_name: my-mas-backups
  roles:
    - ibm.mas_devops.download_backup_archive
```

### Download with Archive Management - without Manage DB2 archives

```yaml
- hosts: localhost
  vars:
    mas_instance_id: inst1
    mas_restore_dir: /restore/mas
    backup_version: "20260117-191500"
    include_manage_db_archive: false
    aws_access_key_id: "{{ lookup('env', 'AWS_ACCESS_KEY_ID') }}"
    aws_secret_access_key: "{{ lookup('env', 'AWS_SECRET_ACCESS_KEY') }}"
    s3_bucket_name: my-mas-backups
  roles:
    - ibm.mas_devops.download_backup_archive
```

## Run Role Playbook
After installing the Ansible Collection you can easily run the role standalone using the `run_role` playbook provided.

### Download Multiple Archives from S3 (Auto-generated)

```bash
export MAS_INSTANCE_ID=inst1
export MAS_RESTORE_DIR=/restore/mas
export BACKUP_VERSION=20260117-191500
export S3_ACCESS_KEY_ID=your_access_key
export S3_SECRET_ACCESS_KEY=your_secret_key
export S3_BUCKET_NAME=my-mas-backups
export S3_REGION=us-west-2
ROLE_NAME=download_backup_archive ansible-playbook ibm.mas_devops.run_role
```

### Download Specific Archives from S3

```bash
export MAS_INSTANCE_ID=inst1
export MAS_RESTORE_DIR=/restore/mas
export BACKUP_VERSION=20260117-191500
export BACKUP_ARCHIVE_NAMES="mas-inst1-backup-20260117-191500-catalog.tar.gz,mas-inst1-backup-20260117-191500-suite.tar.gz"
export S3_ACCESS_KEY_ID=your_access_key
export S3_SECRET_ACCESS_KEY=your_secret_key
export S3_BUCKET_NAME=my-mas-backups
export S3_REGION=us-west-2
ROLE_NAME=download_backup_archive ansible-playbook ibm.mas_devops.run_role
```

### Download with Archive Management

```bash
export MAS_INSTANCE_ID=inst1
export MAS_RESTORE_DIR=/restore/mas
export BACKUP_VERSION=20260117-191500
export INCLUDE_MANAGE_DB_ARCHIVE=false
export S3_ACCESS_KEY_ID=your_access_key
export S3_SECRET_ACCESS_KEY=your_secret_key
export S3_BUCKET_NAME=my-mas-backups
export S3_REGION=us-west-2
ROLE_NAME=download_backup_archive ansible-playbook ibm.mas_devops.run_role
```

### Artifactory Download

```bash
export MAS_INSTANCE_ID=inst1
export MAS_RESTORE_DIR=/restore/mas
export BACKUP_VERSION=20260117-191500
export ARTIFACTORY_USERNAME=your_username
export ARTIFACTORY_TOKEN=your_token
export ARTIFACTORY_URL=https://artifactory.example.com/artifactory
export ARTIFACTORY_REPOSITORY=mas-backups
ROLE_NAME=download_backup_archive ansible-playbook ibm.mas_devops.run_role
```

## Extracted Directory Structure

After successful execution, the role will extract the backup archive to the restore directory with the following structure:

```text
/restore/mas/
├── backup-20260117-191500-catalog/
├── backup-20260117-191500-certmanager/
├── backup-20260117-191500-sls/
├── backup-20260117-191500-mongoce/
├── backup-20260117-191500-app-<appid>/
├── backup-20260117-191500-db2u-<appid>/
└── backup-20260117-191500-suite/
```

The exact directories present will depend on which components were included in the original backup.

## Related Roles

- `upload_backup_archive` - Creates and uploads MAS backup archives to S3 or Artifactory
- `mongodb` - MongoDB backup and restore operations
- `db2` - Db2 backup and restore operations

## License

EPL-2.0
