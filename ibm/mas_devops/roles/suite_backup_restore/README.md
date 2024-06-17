Suite Backup and Restore
===============================================================================

Backup and resotre the k8s resources in MAS Core namespace.


Role Variables - Backup and Restore
-----------------------------------------------------------------------------------------------------------------
### masbr_action
Required. Types of backup/restore job.  
Supported values: `backup`, `restore`

- Environment Variable: `MASBR_ACTION`
- Default Value: None

### mas_instance_id
Required. Defines the instance id that was used for the MAS backup/restore

- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### masbr_confirm_cluster
Optional. Whether to confirm the currently connected cluster before perform the backup/restore job.

- Environment Variable: `MASBR_CONFIRM_CLUSTER`
- Default Value: `false`

### masbr_copy_timeout_sec
Optional. Sets the waiting time in seconds for copying backup files between cluster and specified storage locaiton.

- Environment Variable: `MASBR_COPY_TIMEOUT_SEC`
- Default Value: `3600`

### masbr_storage_type
Required. Types of storage location for saving backup files.  
Supported storage locations: `local`, `cloud`

- Environment Variable: `MASBR_STORAGE_TYPE`
- Default Value: None

### masbr_storage_local_folder
Required only if `masbr_storage_type` is `local`. The folder name in local storage system.

- Environment Variable: `MASBR_STORAGE_LOCAL_FOLDER`
- Default Value: None

### masbr_storage_cloud_rclone_file
Required only if `masbr_storage_type` is `cloud`. The rclone configuration file path.

- Environment Variable: `MASBR_STORAGE_CLOUD_RCLONE_FILE`
- Default Value: None

### masbr_storage_cloud_rclone_name
Required only if `masbr_storage_type` is `cloud`. The rclone configuration name.

- Environment Variable: `MASBR_STORAGE_CLOUD_RCLONE_NAME`
- Default Value: None

### masbr_storage_cloud_bucket
Required only if `masbr_storage_type` is `cloud`. The bucket name used for saving backup files.

- Environment Variable: `MASBR_STORAGE_CLOUD_BUCKET`
- Default Value: None

### masbr_backup_schedule
Optional. Cron expression for scheduled backup.  
https://en.wikipedia.org/wiki/Cron

- Environment Variable: `MASBR_BACKUP_SCHEDULE`
- Default Value: None

### masbr_backup_timezone
Optional. Time zone for scheduled backup.  
https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

- Environment Variable: `MASBR_BACKUP_TIMEZONE`
- Default Value: None

### masbr_restore_from_version
Required only if `masbr_action` is `restore`. The version of the backup to be restored from.

- Environment Variable: `MASBR_RESTORE_FROM_VERSION`
- Default Value: None

### masbr_slack_enabled
Optional. Whether to enable sending backup/resore progress notifications via Slack messages.

- Environment Variable: `MASBR_SLACK_ENABLED`
- Default Value: `false`

### masbr_slack_level
Required only if `masbr_slack_enabled` is `true`. Supported notification levels:   
`info`: send notifications when job in the phase `InProgress`, `Completed`, `Failed`, `PartiallyFailed`    
`failure`: sent notifications only when job in the phase `Failed`, `PartiallyFailed`

- Environment Variable: `MASBR_SLACK_LEVEL`
- Default Value: `info`

### masbr_slack_token
Required only if `masbr_slack_enabled` is `true`. Slack integration token, this authenticates you to the slack service.  

- Environment Variable: `MASBR_SLACK_TOKEN`
- Default Value: None

### masbr_slack_channel
Required only if `masbr_slack_enabled` is `true`. Slack channel to send the message to.

- Environment Variable: `MASBR_SLACK_CHANNEL`
- Default Value: None


License
-------------------------------------------------------------------------------

EPL-2.0
