new_db2
===============================================================================

This role provides backup and restore capabilities for DB2 databases in two deployment scenarios:
1. **In-cluster DB2**: DB2 running as a Db2uCluster in OpenShift/Kubernetes
2. **RDS DB2**: DB2 running as a managed service (e.g., AWS RDS, IBM Cloud Databases)

The role is based on the existing `db2` role but extends it to support both deployment types with a unified interface.

## Features

- **Dual Deployment Support**: Works with both in-cluster DB2 and RDS DB2
- **Full and Incremental Backups**: Supports both full and incremental backup strategies
- **Automated Restore**: Handles database restore with rollforward recovery
- **Keystore Management**: Manages DB2 encryption keystores for secure backups
- **Storage Flexibility**: Supports local and S3 storage backends
  - Local filesystem storage
  - AWS S3
  - S3-compatible storage (MinIO, IBM Cloud Object Storage, etc.)
- **Job Status Tracking**: Integrates with MAS backup/restore framework for status tracking
- **Automatic AWS CLI Installation**: Installs AWS CLI if not present for S3 operations

## Role Variables

### Common Variables

#### db2_action
Action to perform: `backup` or `restore`

- **Required**
- Environment Variable: `DB2_ACTION`
- Default: `backup`

#### db2_type
Type of DB2 deployment: `incluster` or `rds`

- **Required**
- Environment Variable: `DB2_TYPE`
- Default: `incluster`

#### db2_namespace
Namespace where DB2 is deployed (for in-cluster DB2)

- Optional
- Environment Variable: `DB2_NAMESPACE`
- Default: `db2u`

#### db2_instance_name
Name of the DB2 instance

- **Required**
- Environment Variable: `DB2_INSTANCE_NAME`
- Default: None

#### db2_dbname
Name of the database within the instance

- Optional
- Environment Variable: `DB2_DBNAME`
- Default: `BLUDB`

#### db2_jdbc_username
DB2 username for authentication

- Optional
- Environment Variable: `DB2_JDBC_USERNAME`
- Default: `db2inst1`

### In-Cluster DB2 Variables

These variables are used when `db2_type` is set to `incluster`.

#### db2_incluster_pod_label_selector
Label selector to find the DB2 pod

- Optional
- Environment Variable: `DB2_INCLUSTER_POD_LABEL_SELECTOR`
- Default: `type=engine`

#### db2_incluster_container_name
Name of the DB2 container in the pod

- Optional
- Environment Variable: `DB2_INCLUSTER_CONTAINER_NAME`
- Default: `db2u`

#### db2_incluster_keystore_folder
Path to the DB2 keystore folder in the pod

- Optional
- Environment Variable: `DB2_INCLUSTER_KEYSTORE_FOLDER`
- Default: `/mnt/blumeta0/db2/keystore`

#### db2_incluster_pvc_name
Name of the PVC used for backup storage

- Optional
- Environment Variable: `DB2_INCLUSTER_PVC_NAME`
- Default: `c-<instance_name>-backup`

#### db2_incluster_pvc_mount_path
Mount path of the backup PVC

- Optional
- Environment Variable: `DB2_INCLUSTER_PVC_MOUNT_PATH`
- Default: `/mnt/backup`

### RDS DB2 Variables

These variables are used when `db2_type` is set to `rds`.

#### db2_rds_host
Hostname or IP address of the RDS DB2 instance

- **Required** (when db2_type=rds)
- Environment Variable: `DB2_RDS_HOST`
- Default: None

#### db2_rds_port
Port number for RDS DB2 connection

- Optional
- Environment Variable: `DB2_RDS_PORT`
- Default: `50000`

#### db2_rds_username
Username for RDS DB2 authentication

- **Required** (when db2_type=rds)
- Environment Variable: `DB2_RDS_USERNAME`
- Default: None

#### db2_rds_password
Password for RDS DB2 authentication

- **Required** (when db2_type=rds)
- Environment Variable: `DB2_RDS_PASSWORD`
- Default: None

#### db2_rds_ssl_enabled
Enable SSL/TLS for RDS DB2 connection

- Optional
- Environment Variable: `DB2_RDS_SSL_ENABLED`
- Default: `true`

#### db2_rds_cert_path
Path to SSL certificate for RDS DB2 connection

- Optional
- Environment Variable: `DB2_RDS_CERT_PATH`
- Default: None

### Backup Variables

#### masbr_backup_type
Type of backup: `full` or `incr` (incremental)

- Optional
- Environment Variable: `MASBR_BACKUP_TYPE`
- Default: `full`

#### masbr_backup_from_version
For incremental backups, the full backup version to base on (timestamp format: YYYYMMDDHHMMSS)

- Optional
- Environment Variable: `MASBR_BACKUP_FROM_VERSION`
- Default: None (will use latest full backup)

#### masbr_storage_type
Type of storage backend for backups: `local` or `s3`

- Optional
- Environment Variable: `MASBR_STORAGE_TYPE`
- Default: `local`

#### masbr_storage_local_folder
Local folder path to store backup files (used as staging area for S3 uploads)

- **Required**
- Environment Variable: `MASBR_STORAGE_LOCAL_FOLDER`
- Default: None

#### masbr_storage_s3_bucket
S3 bucket name for storing backups

- **Required** (when masbr_storage_type=s3)
- Environment Variable: `MASBR_STORAGE_S3_BUCKET`
- Default: None

#### masbr_storage_s3_access_key
AWS access key ID for S3 authentication

- **Required** (when masbr_storage_type=s3)
- Environment Variable: `MASBR_STORAGE_S3_ACCESS_KEY`
- Default: None

#### masbr_storage_s3_secret_key
AWS secret access key for S3 authentication

- **Required** (when masbr_storage_type=s3)
- Environment Variable: `MASBR_STORAGE_S3_SECRET_KEY`
- Default: None

#### masbr_storage_s3_region
AWS region for S3 bucket

- Optional
- Environment Variable: `MASBR_STORAGE_S3_REGION`
- Default: `us-east-1`

#### masbr_storage_s3_endpoint
Custom S3 endpoint URL (for S3-compatible storage like MinIO, IBM Cloud Object Storage)

- Optional
- Environment Variable: `MASBR_STORAGE_S3_ENDPOINT`
- Default: None (uses AWS S3)

#### masbr_backup_schedule
Cron expression for scheduled backups

- Optional
- Environment Variable: `MASBR_BACKUP_SCHEDULE`
- Default: None (on-demand backup)

### Restore Variables

#### masbr_restore_from_version
Backup version to restore from (timestamp format: YYYYMMDDHHMMSS)

- **Required** (when db2_action=restore)
- Environment Variable: `MASBR_RESTORE_FROM_VERSION`
- Default: None

### Job Configuration Variables

#### masbr_confirm_cluster
Confirm cluster before running backup/restore

- Optional
- Environment Variable: `MASBR_CONFIRM_CLUSTER`
- Default: `false`

#### masbr_copy_timeout_sec
Timeout for file transfer operations (in seconds)

- Optional
- Environment Variable: `MASBR_COPY_TIMEOUT_SEC`
- Default: `43200` (12 hours)

#### masbr_job_timezone
Timezone for scheduled backup jobs

- Optional
- Environment Variable: `MASBR_JOB_TIMEZONE`
- Default: None (UTC)

#### masbr_allow_multi_jobs
Allow multiple backup/restore jobs to run simultaneously

- Optional
- Environment Variable: `MASBR_ALLOW_MULTI_JOBS`
- Default: `false`

## Example Playbooks

### Backup In-Cluster DB2

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    db2_action: backup
    db2_type: incluster
    db2_instance_name: db2u-manage
    db2_namespace: db2u
    db2_dbname: BLUDB
    masbr_storage_local_folder: /tmp/db2-backups
    masbr_backup_type: full
  roles:
    - ibm.mas_devops.new_db2
```

### Backup RDS DB2

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    db2_action: backup
    db2_type: rds
    db2_instance_name: my-rds-db2
    db2_dbname: BLUDB
    db2_rds_host: my-db2.abc123.us-east-1.rds.amazonaws.com
    db2_rds_port: 50000
    db2_rds_username: db2admin
    db2_rds_password: "{{ vault_db2_password }}"
    db2_rds_ssl_enabled: true
    db2_rds_cert_path: /path/to/rds-cert.pem
    masbr_storage_local_folder: /tmp/db2-backups
    masbr_backup_type: full
  roles:
    - ibm.mas_devops.new_db2
```

### Incremental Backup

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    db2_action: backup
    db2_type: incluster
    db2_instance_name: db2u-manage
    masbr_storage_local_folder: /tmp/db2-backups
    masbr_backup_type: incr
    masbr_backup_from_version: 20240621021316  # Base full backup
  roles:
    - ibm.mas_devops.new_db2
```

### Restore In-Cluster DB2

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    db2_action: restore
    db2_type: incluster
    db2_instance_name: db2u-manage
    db2_namespace: db2u
    db2_dbname: BLUDB
    masbr_storage_local_folder: /tmp/db2-backups
    masbr_restore_from_version: 20240621021316
  roles:
    - ibm.mas_devops.new_db2
```

### Restore RDS DB2

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    db2_action: restore
    db2_type: rds
    db2_instance_name: my-rds-db2
    db2_dbname: BLUDB
    db2_rds_host: my-db2.abc123.us-east-1.rds.amazonaws.com
    db2_rds_port: 50000
    db2_rds_username: db2admin
    db2_rds_password: "{{ vault_db2_password }}"
    db2_rds_ssl_enabled: true
    masbr_storage_local_folder: /tmp/db2-backups
    masbr_restore_from_version: 20240621021316
  roles:
    - ibm.mas_devops.new_db2
```

### Backup In-Cluster DB2 to S3

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    db2_action: backup
    db2_type: incluster
    db2_instance_name: db2u-manage
    db2_namespace: db2u
    db2_dbname: BLUDB
    masbr_storage_type: s3
    masbr_storage_local_folder: /tmp/db2-backups  # Staging area
    masbr_storage_s3_bucket: my-db2-backups
    masbr_storage_s3_access_key: "{{ vault_aws_access_key }}"
    masbr_storage_s3_secret_key: "{{ vault_aws_secret_key }}"
    masbr_storage_s3_region: us-east-1
    masbr_backup_type: full
  roles:
    - ibm.mas_devops.new_db2
```

### Backup RDS DB2 to S3

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    db2_action: backup
    db2_type: rds
    db2_instance_name: my-rds-db2
    db2_dbname: BLUDB
    db2_rds_host: my-db2.abc123.us-east-1.rds.amazonaws.com
    db2_rds_port: 50000
    db2_rds_username: db2admin
    db2_rds_password: "{{ vault_db2_password }}"
    db2_rds_ssl_enabled: true
    masbr_storage_type: s3
    masbr_storage_local_folder: /tmp/db2-backups  # Staging area
    masbr_storage_s3_bucket: my-db2-backups
    masbr_storage_s3_access_key: "{{ vault_aws_access_key }}"
    masbr_storage_s3_secret_key: "{{ vault_aws_secret_key }}"
    masbr_storage_s3_region: us-east-1
    masbr_backup_type: full
  roles:
    - ibm.mas_devops.new_db2
```

### Restore In-Cluster DB2 from S3

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    db2_action: restore
    db2_type: incluster
    db2_instance_name: db2u-manage
    db2_namespace: db2u
    db2_dbname: BLUDB
    masbr_storage_type: s3
    masbr_storage_local_folder: /tmp/db2-backups  # Staging area
    masbr_storage_s3_bucket: my-db2-backups
    masbr_storage_s3_access_key: "{{ vault_aws_access_key }}"
    masbr_storage_s3_secret_key: "{{ vault_aws_secret_key }}"
    masbr_storage_s3_region: us-east-1
    masbr_restore_from_version: 20240621021316
  roles:
    - ibm.mas_devops.new_db2
```

### Restore RDS DB2 from S3

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    db2_action: restore
    db2_type: rds
    db2_instance_name: my-rds-db2
    db2_dbname: BLUDB
    db2_rds_host: my-db2.abc123.us-east-1.rds.amazonaws.com
    db2_rds_port: 50000
    db2_rds_username: db2admin
    db2_rds_password: "{{ vault_db2_password }}"
    db2_rds_ssl_enabled: true
    masbr_storage_type: s3
    masbr_storage_local_folder: /tmp/db2-backups  # Staging area
    masbr_storage_s3_bucket: my-db2-backups
    masbr_storage_s3_access_key: "{{ vault_aws_access_key }}"
    masbr_storage_s3_secret_key: "{{ vault_aws_secret_key }}"
    masbr_storage_s3_region: us-east-1
    masbr_restore_from_version: 20240621021316
  roles:
    - ibm.mas_devops.new_db2
```

### Using S3-Compatible Storage (MinIO, IBM COS)

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    db2_action: backup
    db2_type: incluster
    db2_instance_name: db2u-manage
    db2_namespace: db2u
    db2_dbname: BLUDB
    masbr_storage_type: s3
    masbr_storage_local_folder: /tmp/db2-backups
    masbr_storage_s3_bucket: my-db2-backups
    masbr_storage_s3_access_key: "{{ vault_s3_access_key }}"
    masbr_storage_s3_secret_key: "{{ vault_s3_secret_key }}"
    masbr_storage_s3_region: us-east-1
    masbr_storage_s3_endpoint: https://s3.us-east.cloud-object-storage.appdomain.cloud  # IBM COS
    # masbr_storage_s3_endpoint: https://minio.example.com:9000  # MinIO
    masbr_backup_type: full
  roles:
    - ibm.mas_devops.new_db2
```

## Architecture

### In-Cluster DB2 Backup Flow

1. Validates DB2 cluster is running and accessible
2. Connects to DB2 pod using `oc exec`
3. Executes DB2 backup command with compression
4. Extracts and backs up keystore files
5. Creates tar.gz archive of backup files
6. Copies backup to specified storage location
7. Updates job status and cleans up temporary files

### RDS DB2 Backup Flow

1. Validates RDS DB2 connection parameters
2. Catalogs RDS DB2 node and database
3. Connects to RDS DB2 using DB2 client
4. Executes DB2 backup command
5. Saves SSL certificate and metadata
6. Creates tar.gz archive of backup files
7. Uncatalogs database and cleans up

### In-Cluster DB2 Restore Flow

1. Validates DB2 cluster is running
2. Copies backup files from storage to pod
3. Extracts backup and validates keystore files
4. Adds master key to target keystore
5. Deactivates DB2 (disables HA, stops database)
6. Executes DB2 restore command
7. Performs rollforward recovery
8. Reactivates DB2 (enables HA, starts database)
9. Cleans up temporary files

### RDS DB2 Restore Flow

1. Validates RDS DB2 connection parameters
2. Extracts backup files locally
3. Reads backup metadata
4. Catalogs RDS DB2 node and database
5. Configures SSL if enabled
6. Quiesces database
7. Executes DB2 restore command
8. Unquiesces database
9. Verifies connectivity
10. Uncatalogs and cleans up

## Differences from Original db2 Role

1. **Dual Deployment Support**: Supports both in-cluster and RDS DB2
2. **Simplified Configuration**: Uses `db2_type` to route to appropriate implementation
3. **RDS-Specific Features**: Handles RDS cataloging, SSL, and metadata
4. **Unified Interface**: Same variables and playbook structure for both types
5. **Enhanced Documentation**: Clear examples for both deployment scenarios

## Prerequisites

### For In-Cluster DB2
- OpenShift/Kubernetes cluster with DB2 operator installed
- DB2uCluster custom resource deployed
- `oc` CLI configured and authenticated
- Sufficient storage for backup PVC

### For RDS DB2
- DB2 client tools installed on the Ansible controller
- Network connectivity to RDS DB2 instance
- Valid DB2 credentials with backup/restore privileges
- SSL certificate (if SSL is enabled)

## Limitations

- RDS DB2 restore requires database downtime (quiesce operation)
- Incremental backups are only supported for in-cluster DB2
- RDS DB2 backups are performed from the Ansible controller (not in-pod)
- Large databases may require significant storage and time for backup/restore

## Troubleshooting

### In-Cluster DB2 Issues

**Pod not found**: Check that the pod label selector matches your DB2 deployment
```bash
oc get pods -n db2u -l type=engine
```

**PVC not accessible**: Verify the PVC name and mount path
```bash
oc get pvc -n db2u
```

**Keystore errors**: Ensure the keystore folder path is correct for your DB2 version

### RDS DB2 Issues

**Connection failed**: Verify network connectivity and security groups
```bash
db2 catalog tcpip node testnode remote <host> server <port>
db2 catalog database <dbname> at node testnode
db2 connect to <dbname> user <username>
```

**SSL errors**: Verify the SSL certificate path and format

**Catalog errors**: Clean up existing catalog entries
```bash
db2 uncatalog database <dbname>
db2 uncatalog node <nodename>
```

## License

EPL-2.0