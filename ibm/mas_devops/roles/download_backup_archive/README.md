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
- Optional cleanup of temporary files after extraction
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

### Required Variables

#### mas_instance_id
Instance ID of the MAS instance. This is used to identify the backup directories.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

#### mas_restore_dir
Directory where the backup archive will be downloaded and extracted. This is the parent directory where all component backup directories will be restored.

- **Required**
- Environment Variable: `MAS_RESTORE_DIR`
- Default Value: None

### Backup Archive Variables

#### backup_version
Version identifier for the backup to download. This must match the version used when the backup was created. When downloading multiple archives, this is used as the default version for all components unless specific component versions are provided.

- **Required**
- Environment Variable: `BACKUP_VERSION`
- Default Value: None

#### backup_archive_names
List of archive names to download. Can be provided as a comma-separated string or as a list. If not provided, the role will auto-generate archive names based on component versions.

Examples:
- String format: `"archive1.tar.gz,archive2.tar.gz,archive3.tar.gz"`
- List format: `["archive1.tar.gz", "archive2.tar.gz", "archive3.tar.gz"]`

- **Optional**
- Environment Variable: `BACKUP_ARCHIVE_NAMES`
- Default Value: Auto-generated from component versions

#### Component-Specific Backup Versions

These variables allow you to specify different backup versions for each component. If not provided, they default to the value of `backup_version`. These are used to auto-generate archive names when `backup_archive_names` is not provided.

- `ibm_catalogs_backup_version` - Environment Variable: `IBM_CATALOGS_BACKUP_VERSION`
- `certmanager_backup_version` - Environment Variable: `CERTMANAGER_BACKUP_VERSION`
- `mongodb_backup_version` - Environment Variable: `MONGODB_BACKUP_VERSION`
- `sls_backup_version` - Environment Variable: `SLS_BACKUP_VERSION`
- `db2_backup_version` - Environment Variable: `DB2_BACKUP_VERSION`
- `suite_backup_version` - Environment Variable: `SUITE_BACKUP_VERSION`
- `manage_backup_version` - Environment Variable: `MANAGE_BACKUP_VERSION`

All are **Optional** and default to `backup_version`.

### S3 Download Variables

Provide these variables to download the backup archive from AWS S3 or S3-compatible storage. If S3 credentials are provided, S3 download takes precedence over Artifactory.

#### aws_access_key_id
AWS access key ID for authentication.

- **Required for S3 download**
- Environment Variable: `S3_ACCESS_KEY_ID`
- Default Value: None

#### aws_secret_access_key
AWS secret access key for authentication.

- **Required for S3 download**
- Environment Variable: `S3_SECRET_ACCESS_KEY`
- Default Value: None

#### s3_bucket_name
Name of the S3 bucket where the archive is stored.

- **Required for S3 download**
- Environment Variable: `S3_BUCKET_NAME`
- Default Value: None

#### s3_region
AWS region where the S3 bucket is located.

- **Optional**
- Environment Variable: `S3_REGION`
- Default Value: `us-east-1`

#### s3_endpoint_url
Custom S3 endpoint URL for S3-compatible storage services (e.g., MinIO, Wasabi, IBM Cloud Object Storage).

- **Optional**
- Environment Variable: `S3_ENDPOINT_URL`
- Default Value: None (uses AWS S3 endpoints)

### Artifactory Download Variables

Provide these variables to download the backup archive from Artifactory. Artifactory download is used only if S3 credentials are not provided.

#### artifactory_username
Artifactory username for authentication.

- **Required for Artifactory download**
- Environment Variable: `ARTIFACTORY_USERNAME`
- Default Value: None

#### artifactory_token
Artifactory API token for authentication.

- **Required for Artifactory download**
- Environment Variable: `ARTIFACTORY_TOKEN`
- Default Value: None

#### artifactory_url
Base URL of the Artifactory server (e.g., `https://artifactory.example.com/artifactory`).

- **Required for Artifactory download**
- Environment Variable: `ARTIFACTORY_URL`
- Default Value: None

#### artifactory_repository
Name of the Artifactory repository where the archive is stored.

- **Required for Artifactory download**
- Environment Variable: `ARTIFACTORY_REPOSITORY`
- Default Value: None

### General Configuration

#### backup_temp_dir
Temporary directory where the archive will be downloaded before extraction. The directory is created if it doesn't exist and can be cleaned up after extraction.

- **Optional**
- Environment Variable: None
- Default Value: `<mas_restore_dir>/mas-restore-<backup_version>`

#### download_timeout
Maximum time in seconds to wait for the download to complete. Useful for large archives or slow network connections.

- **Optional**
- Environment Variable: `DOWNLOAD_TIMEOUT_SECS`
- Default Value: `3600` (1 hour)

#### extract_archive
Whether to automatically extract the downloaded archive. Set to `false` if you only want to download the archive without extracting it.

- **Optional**
- Environment Variable: `EXTRACT_ARCHIVE`
- Default Value: `true`

#### cleanup_archive
Whether to remove the archive file and temporary directory after successful extraction. Set to `false` to keep the downloaded archive. 

- **Optional**
- Environment Variable: `CLEANUP_ARCHIVE`
- Default Value: `true`

#### include_sls_archive
Whether to download SLS archive (`-sls.tar.gz`) from S3 or Artifactory.

**Important:** When set to `false`, the role will automatically skip downloading sls archive from S3 or Artifactory. This prevents unnecessary downloads when SLS component restore is not needed.

- **Optional**
- Environment Variable: `INCLUDE_SLS_ARCHIVE`
- Default Value: `true`

#### include_manage_app_archive
Whether to download Manage app archive (`-app-manage.tar.gz`) from S3 or Artifactory.

**Important:** When set to `false`, the role will automatically skip downloading manage-app archive from S3 or Artifactory. This prevents unnecessary downloads when manage component restore is not needed.

- **Optional**
- Environment Variable: `INCLUDE_MANAGE_APP_ARCHIVE`
- Default Value: `true`

#### include_manage_db_archive
Whether to download Manage DB2 archive (`-db2u-manage.tar.gz`) from S3 or Artifactory.

**Important:** When set to `false`, the role will automatically skip downloading manage-db2 archive (`-db2u-manage.tar.gz`) from S3 or Artifactory. This prevents unnecessary downloads when manage component restore is not needed.

- **Optional**
- Environment Variable: `INCLUDE_MANAGE_DB_ARCHIVE`
- Default Value: `true`

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
    db2_backup_version: "20260115-100000"
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
export MANAGE_ARCHIVES=false
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

```
/restore/mas/
├── backup-20260117-191500-catalog/
├── backup-20260117-191500-certmanager/
├── backup-20260117-191500-sls/
├── backup-20260117-191500-mongoce/
├── backup-20260117-191500-db2u/
└── backup-20260117-191500-suite/
```

The exact directories present will depend on which components were included in the original backup.

## Related Roles

- `upload_backup_archive` - Creates and uploads MAS backup archives to S3 or Artifactory
- `mongodb` - MongoDB backup and restore operations
- `db2` - Db2 backup and restore operations

## License
EPL-2.0