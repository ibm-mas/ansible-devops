# upload_backup_archive
Creates a compressed archive of MAS backup directories and uploads it to AWS S3 or Artifactory.

This role automates the process of packaging MAS backup directories into a single tar.gz archive and uploading it to a remote storage location. It supports multiple backup components (catalog, cert-manager, SLS, MongoDB, Db2, and MAS Suite) and allows for component-specific backup versions. The role intelligently detects which backup directories exist and only archives those that are present.

Key features:
- Creates compressed tar.gz archives of MAS backup directories
- Supports uploading to AWS S3 or S3-compatible storage
- Supports uploading to Artifactory repositories
- Handles component-specific backup versions
- Automatic cleanup of temporary files
- Configurable upload timeouts for large archives

## Prerequisites

### For S3 Upload
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) or boto3 Python library must be installed
- `amazon.aws` Ansible collection must be installed
- AWS credentials with S3 write permissions
- S3 bucket must exist and be accessible

### For Artifactory Upload
- `curl` command-line tool must be installed
- Artifactory API token with upload permissions
- Artifactory repository must exist and be accessible

## Role Variables

### Required Variables

#### mas_backup_dir
Directory containing the MAS backup folders. This is the parent directory where all component backup directories are located.

- **Required**
- Environment Variable: `MAS_BACKUP_DIR`
- Default Value: None

#### backup_version
Version identifier for the backup. This is used as the default version for all component backups unless component-specific versions are provided.

- **Required**
- Environment Variable: `BACKUP_VERSION`
- Default Value: None

### Component-Specific Backup Versions

These variables allow you to specify different backup versions for individual components. If not provided, they default to the value of `backup_version`.

#### ibm_catalogs_backup_version
Backup version for the catalog component.

- **Optional**
- Environment Variable: `IBM_CATALOGS_BACKUP_VERSION`
- Default Value: Value of `backup_version`

#### certmanager_backup_version
Backup version for the cert-manager component.

- **Optional**
- Environment Variable: `CERTMANAGER_BACKUP_VERSION`
- Default Value: Value of `backup_version`

#### mongodb_backup_version
Backup version for the MongoDB component.

- **Optional**
- Environment Variable: `MONGODB_BACKUP_VERSION`
- Default Value: Value of `backup_version`

#### sls_backup_version
Backup version for the SLS (Suite License Service) component.

- **Optional**
- Environment Variable: `SLS_BACKUP_VERSION`
- Default Value: Value of `backup_version`

#### db2_backup_version
Backup version for the Db2 component.

- **Optional**
- Environment Variable: `DB2_BACKUP_VERSION`
- Default Value: Value of `backup_version`

#### suite_backup_version
Backup version for the MAS Suite component.

- **Optional**
- Environment Variable: `SUITE_BACKUP_VERSION`
- Default Value: Value of `backup_version`

### S3 Upload Variables

Provide these variables to upload the backup archive to AWS S3 or S3-compatible storage. If S3 credentials are provided, S3 upload takes precedence over Artifactory.

#### aws_access_key_id
AWS access key ID for authentication.

- **Required for S3 upload**
- Environment Variable: `S3_ACCESS_KEY_ID`
- Default Value: None

#### aws_secret_access_key
AWS secret access key for authentication.

- **Required for S3 upload**
- Environment Variable: `S3_SECRET_ACCESS_KEY`
- Default Value: None

#### s3_bucket_name
Name of the S3 bucket where the archive will be uploaded.

- **Required for S3 upload**
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

### Artifactory Upload Variables

Provide these variables to upload the backup archive to Artifactory. Artifactory upload is used only if S3 credentials are not provided.

#### artifactory_username
Artifactory username for authentication.

- **Required for Artifactory upload**
- Environment Variable: `ARTIFACTORY_USERNAME`
- Default Value: None

#### artifactory_token
Artifactory API token for authentication.

- **Required for Artifactory upload**
- Environment Variable: `ARTIFACTORY_TOKEN`
- Default Value: None

#### artifactory_url
Base URL of the Artifactory server (e.g., `https://artifactory.example.com/artifactory`).

- **Required for Artifactory upload**
- Environment Variable: `ARTIFACTORY_URL`
- Default Value: None

#### artifactory_repository
Name of the Artifactory repository where the archive will be uploaded.

- **Required for Artifactory upload**
- Environment Variable: `ARTIFACTORY_REPOSITORY`
- Default Value: None

### General Configuration

#### backup_archive_name
Name of the tar.gz archive file that will be created and uploaded.

- **Optional**
- Environment Variable: None
- Default Value: `mas-backup-{{ backup_version }}.tar.gz`

#### backup_temp_dir
Temporary directory where the archive will be created before upload. The directory is created if it doesn't exist and cleaned up after upload.

- **Optional**
- Environment Variable: None
- Default Value: `/tmp/mas-backup-{{ backup_version }}`

#### upload_timeout
Maximum time in seconds to wait for the upload to complete. Useful for large archives or slow network connections.

- **Optional**
- Environment Variable: None
- Default Value: `3600` (1 hour)

## Example Playbook

### S3 Upload
After installing the Ansible Collection you can include this role in your own custom playbooks.

```yaml
- hosts: localhost
  vars:
    mas_backup_dir: /backup/mas
    backup_version: "260117-191500"
    aws_access_key_id: "{{ lookup('env', 'AWS_ACCESS_KEY_ID') }}"
    aws_secret_access_key: "{{ lookup('env', 'AWS_SECRET_ACCESS_KEY') }}"
    s3_bucket_name: my-mas-backups
    s3_region: us-west-2
  roles:
    - ibm.mas_devops.upload_backup_archive
```

### Artifactory Upload

```yaml
- hosts: localhost
  vars:
    mas_backup_dir: /backup/mas
    backup_version: "260117-191500"
    artifactory_username: "{{ lookup('env', 'ARTIFACTORY_USERNAME') }}"
    artifactory_token: "{{ lookup('env', 'ARTIFACTORY_TOKEN') }}"
    artifactory_url: https://artifactory.example.com/artifactory
    artifactory_repository: mas-backups
  roles:
    - ibm.mas_devops.upload_backup_archive
```

### S3-Compatible Storage (IBMcloud, MinIO, Wasabi, etc.)

```yaml
- hosts: localhost
  vars:
    mas_backup_dir: /backup/mas
    backup_version: "260117-191500"
    aws_access_key_id: "{{ lookup('env', 'S3_ACCESS_KEY') }}"
    aws_secret_access_key: "{{ lookup('env', 'S3_SECRET_KEY') }}"
    s3_bucket_name: mas-backups
    s3_region: us-east-1
    s3_endpoint_url: https://s3.example.com
  roles:
    - ibm.mas_devops.upload_backup_archive
```

### Component-Specific Backup Versions

```yaml
- hosts: localhost
  vars:
    mas_backup_dir: /backup/mas
    backup_version: "260117-191500"
    # Override specific component versions
    mongodb_backup_version: "260116-120000"
    db2_backup_version: "260115-180000"
    aws_access_key_id: "{{ lookup('env', 'AWS_ACCESS_KEY_ID') }}"
    aws_secret_access_key: "{{ lookup('env', 'AWS_SECRET_ACCESS_KEY') }}"
    s3_bucket_name: my-mas-backups
  roles:
    - ibm.mas_devops.upload_backup_archive
```

## Run Role Playbook
After installing the Ansible Collection you can easily run the role standalone using the `run_role` playbook provided.

### S3 Upload

```bash
export MAS_BACKUP_DIR=/backup/mas
export BACKUP_VERSION=260117-191500
export S3_ACCESS_KEY_ID=your_access_key
export S3_SECRET_ACCESS_KEY=your_secret_key
export S3_BUCKET_NAME=my-mas-backups
export S3_REGION=us-west-2
ROLE_NAME=upload_backup_archive ansible-playbook ibm.mas_devops.run_role
```

### Artifactory Upload

```bash
export MAS_BACKUP_DIR=/backup/mas
export BACKUP_VERSION=260117-191500
export ARTIFACTORY_USERNAME=your_username
export ARTIFACTORY_TOKEN=your_token
export ARTIFACTORY_URL=https://artifactory.example.com/artifactory
export ARTIFACTORY_REPOSITORY=mas-backups
ROLE_NAME=upload_backup_archive ansible-playbook ibm.mas_devops.run_role
```

## License
EPL-2.0