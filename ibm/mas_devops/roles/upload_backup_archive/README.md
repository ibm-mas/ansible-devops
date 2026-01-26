upload_backup_archive
===============================================================================

This role creates a tar.gz archive of MAS backup directories and uploads it to either AWS S3 or Artifactory.

Role Variables
-------------------------------------------------------------------------------

### Required Variables

- `mas_backup_dir`: Directory containing the backup folders
- `backup_version`: Version identifier for the backup (used to identify backup directories)

### S3 Upload Variables (Optional)

Provide these variables to upload to AWS S3:

- `aws_access_key_id`: AWS access key ID
- `aws_secret_access_key`: AWS secret access key
- `s3_bucket_name`: S3 bucket name where the archive will be uploaded
- `s3_region`: AWS region (default: `us-east-1`)
- `s3_endpoint_url`: Custom S3 endpoint URL (optional, for S3-compatible storage)

### Artifactory Upload Variables (Optional)

Provide these variables to upload to Artifactory:

- `artifactory_username`: Artifactory username
- `artifactory_token`: Artifactory API token
- `artifactory_url`: Artifactory base URL (e.g., `https://artifactory.example.com/artifactory`)
- `artifactory_repository`: Artifactory repository name where the archive will be uploaded

### Optional Variables

- `backup_archive_name`: Name of the tar.gz archive file (default: `mas-backup-{{ backup_version }}.tar.gz`)
- `backup_temp_dir`: Temporary directory for creating the archive (default: `/tmp/mas-backup-{{ backup_version }}`)
- `upload_timeout`: Upload timeout in seconds (default: `3600`)

Backup Directories
-------------------------------------------------------------------------------

The role will archive the following directories from `mas_backup_dir`:

- `backup-{{ backup_version }}_catalog`
- `backup-{{ backup_version }}_certmanager`
- `backup-{{ backup_version }}_sls`
- `backup-{{ backup_version }}_mongoce`
- `backup-{{ backup_version }}_db2u`
- `backup-{{ backup_version }}_suite`

Only directories that exist will be included in the archive. The role will fail if no backup directories are found.

Upload Behavior
-------------------------------------------------------------------------------

- If S3 credentials are provided, the archive will be uploaded to S3
- If Artifactory credentials are provided and S3 credentials are not, the archive will be uploaded to Artifactory
- If both S3 and Artifactory credentials are provided, S3 takes precedence
- If neither S3 nor Artifactory credentials are provided, the role will fail

Example Playbook - S3 Upload
-------------------------------------------------------------------------------

```yaml
- hosts: localhost
  vars:
    mas_backup_dir: /backup/mas
    backup_version: "8.11.0"
    aws_access_key_id: "{{ lookup('env', 'AWS_ACCESS_KEY_ID') }}"
    aws_secret_access_key: "{{ lookup('env', 'AWS_SECRET_ACCESS_KEY') }}"
    s3_bucket_name: my-mas-backups
    s3_region: us-west-2
  roles:
    - ibm.mas_devops.upload_backup_archive
```

Example Playbook - Artifactory Upload
-------------------------------------------------------------------------------

```yaml
- hosts: localhost
  vars:
    mas_backup_dir: /backup/mas
    backup_version: "8.11.0"
    artifactory_username: "{{ lookup('env', 'ARTIFACTORY_USERNAME') }}"
    artifactory_token: "{{ lookup('env', 'ARTIFACTORY_TOKEN') }}"
    artifactory_url: https://artifactory.example.com/artifactory
    artifactory_repository: mas-backups
  roles:
    - ibm.mas_devops.upload_backup_archive
```

Example Playbook - S3-Compatible Storage
-------------------------------------------------------------------------------

```yaml
- hosts: localhost
  vars:
    mas_backup_dir: /backup/mas
    backup_version: "8.11.0"
    aws_access_key_id: "{{ lookup('env', 'S3_ACCESS_KEY') }}"
    aws_secret_access_key: "{{ lookup('env', 'S3_SECRET_KEY') }}"
    s3_bucket_name: mas-backups
    s3_region: us-east-1
    s3_endpoint_url: https://s3.example.com
  roles:
    - ibm.mas_devops.upload_backup_archive
```

Dependencies
-------------------------------------------------------------------------------

### For S3 Upload
- `amazon.aws` collection (for `s3_object` module)
- AWS CLI or boto3 Python library

### For Artifactory Upload
- `curl` command-line tool

License
-------------------------------------------------------------------------------

EPL-2.0