# suite_app_config_manage

This role provides post-installation configuration actions for the Maximo Manage application. It consolidates the former `suite_manage_*_config` roles into a single role, with the `suite_app_config_manage_actions` parameter selecting which actions to run — either one at a time or several together as part of the initial configuration of a Manage workspace.

!!! important "Prerequisites"
    - Manage application must be installed and its workspace ready before running any action
    - Actions that execute SQL against the Manage database (`bim`, `logging` with `mas_manage_logging_is_prod`) require the Db2 Warehouse instance to be available and are not supported with an external (JDBC) database

## Actions

| Action | Former role | Description |
| ------ | ----------- | ----------- |
| `attachments` | `suite_manage_attachments_config` | Configure where Manage stores attachment files: PVC file storage, IBM Cloud Object Storage or AWS S3 (CR-based configuration only) |
| `bim` | `suite_manage_bim_config` | Configure BIM (Building Information Models) support: create the BIM folders on the mounted PVC and set the `bim.*` system properties |
| `birt` | `suite_manage_birt_report_config` | Configure the BIRT report server bundle for Manage |
| `custfiles` | `suite_manage_customer_files_config` | Provision the IBM COS / AWS S3 buckets (main, recovery, backup) used to store Manage customer files, and import the storage certificates |
| `eventstreams` | `configure_manage_eventstreams` | Configure Manage to use IBM Cloud Event Streams: import the Event Streams certificates, set the `mxe.*` system properties and insert the Kafka message hub provider, queues and cron task definitions |
| `imagestitching` | `suite_manage_imagestitching_config` | Configure persistent storage for Manage image stitching files (Civil component) |
| `import-certs` | `suite_manage_import_certs_config` | Import certificates into the ManageWorkspace CR so they are added to the Manage truststore |
| `dbc-scripts` | `suite_manage_load_dbc_scripts` | Load DBC (database configuration) scripts into the Manage database via the maxinst pod |
| `logging` | `suite_manage_logging_config` | Configure the COS/S3 destination for Manage server log uploads and (optionally) lock down the Admin Center on production databases |
| `pvc` | `suite_manage_pvc_config` | Add custom persistent volumes to the ManageWorkspace CR |

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`suite_app_config_manage_actions`](#suite_app_config_manage_actions) | Yes | None |
| [`mas_instance_id`](#mas_instance_id) | Yes | None |
| [`mas_workspace_id`](#mas_workspace_id) | Yes | None |
| [`mas_app_id`](#mas_app_id) | No | `manage` |
| [`mas_manual_route_mgmt`](#mas_manual_route_mgmt) | No | `false` |
| [`mas_manage_attachments_provider`](#mas_manage_attachments_provider) | No | `filestorage` |
| [`mas_manage_custfiles_provider`](#mas_manage_custfiles_provider) | Conditional | Legacy `COS_TYPE` |
| [`mas_manage_logging_provider`](#mas_manage_logging_provider) | Conditional | Legacy `COS_TYPE` |
| [`mas_manage_birt_report_bundle_name`](#mas_manage_birt_report_bundle_name) | No | `rpt` |
| [`mas_manage_eventstreams_name`](#mas_manage_eventstreams_name) | Conditional | None |
| [`mas_manage_imagestitching_pvc_name`](#mas_manage_imagestitching_pvc_name) | No | `manage-imagestitching` |
| [`manage_certificates`](#manage_certificates) | Conditional | None |
| [`mas_manage_dbc_script_path_local`](#mas_manage_dbc_script_path_local) | Conditional | None |
| [`mas_manage_custom_persistent_volumes`](#mas_manage_custom_persistent_volumes) | Conditional | None |
| [`db2_instance_name`](#db2_instance_name) | Conditional | None |

Most action-specific variables are only required when the corresponding action is selected; the condition is noted in each entry.

### Actions and MAS Targeting

#### suite_app_config_manage_actions

The actions to run, either as a list or as a comma-separated string — any combination of `attachments`, `bim`, `birt`, `custfiles`, `eventstreams`, `imagestitching`, `import-certs`, `dbc-scripts`, `logging`, and `pvc`.

- **Required**
- Environment Variable: `SUITE_APP_CONFIG_MANAGE_ACTIONS`
- Default: None

Each action corresponds to one of the former `suite_manage_*_config` roles. Running multiple actions in one invocation is more efficient than invoking the role several times, for example `attachments,bim` configures both attachment storage and BIM support in a single run.

#### mas_instance_id

MAS instance identifier — identifies which MAS instance contains the Manage application to configure.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

#### mas_workspace_id

MAS workspace identifier — identifies the workspace containing the Manage application to configure.

- **Required**
- Environment Variable: `MAS_WORKSPACE_ID`
- Default: None

#### mas_app_id

Application identifier — set to `health` when configuring a Health stand-alone application (supported by the `attachments`, `bim` and `dbc-scripts` actions).

- **Optional**
- Environment Variable: `MAS_APP_ID`
- Default: `manage`

#### mas_manual_route_mgmt

Set to `true` when the MAS instance uses manual route management (`manualRouteMgmt`, always the case when Service Mesh is in use) — used by the `attachments` action.

- **Optional**
- Environment Variable: `MAS_MANUAL_ROUTE_MGMT`
- Default: `false`

With manual route management the MAS operator does not create Routes, so the `attachments` action cannot look up the application Route. When `true`, the action reads the application host from the `routeref-<instance>-<app>-<workspace>` ConfigMap in the application namespace instead, and fails if that ConfigMap does not exist.

### Storage Providers

#### mas_manage_attachments_provider

Attachment storage provider (action: `attachments`) — `filestorage`, `ibm`, or `aws`.

- **Optional**
- Environment Variable: `MAS_MANAGE_ATTACHMENTS_PROVIDER`
- Default: `filestorage`

Only the CR-based configuration is supported: the former `db` configuration mode (raw SQL against the Manage database) has been removed, and setting `mas_manage_attachment_configuration_mode` to `db` fails with a migration message. The variable is retained so that playbooks setting it to `cr` continue to work.

#### mas_manage_custfiles_provider

Customer files storage provider (action: `custfiles`) — `ibm` or `aws`.

- **Required** for the action
- Environment Variable: `MAS_MANAGE_CUSTFILES_PROVIDER` (falls back to the legacy `COS_TYPE`)
- Default: Value of the legacy `COS_TYPE` environment variable (`None` if unset)

#### mas_manage_logging_provider

Manage log upload storage provider (action: `logging`) — `ibm` or `aws`.

- **Required** for the action
- Environment Variable: `MAS_MANAGE_LOGGING_PROVIDER` (falls back to the legacy `COS_TYPE`)
- Default: Value of the legacy `COS_TYPE` environment variable (`None` if unset)

Related settings: `mas_manage_logging_is_prod` (`false`; enables the Admin Center lockdown on production databases), `mas_manage_logging_secret_name` (`s3secretkey`), and `mas_manage_logging_force` (`false`; reconfigure logging even when a destination is already set).

### Action-Specific Settings

#### mas_manage_birt_report_bundle_name

Name used for the report server bundle when one is not already configured (action: `birt`).

- **Optional**
- Environment Variable: `MANAGE_REPORT_BUNDLE_SERVER_NAME`
- Default: `rpt`

#### mas_manage_eventstreams_name

The IBM Cloud Event Streams instance name (action: `eventstreams`) — identifies the Event Streams service instance whose Kafka brokers Manage is configured to use.

- **Required** for the action
- Environment Variable: `EVENTSTREAMS_NAME`
- Default: None

Related settings: `mas_manage_eventstreams_location` (`us-east`), `ibmcloud_apikey`, `ibmcloud_resourcegroup` (`Default`), `db2wh_dbname` (`BLUDB`), `cpd_meta_namespace` (the CP4D namespace hosting the Manage Db2 Warehouse), and `mas_manage_eventstreams_manage_url_subdomain` (`main`; the former role hardcoded this value, override when the Manage UI route uses a different workspace subdomain).

!!! warning
    This action inserts a dummy Kafka password during configuration (not the actual one); the real password must be configured manually via the Manage administration dashboard afterwards.

#### mas_manage_imagestitching_pvc_name

Name of the PVC used for image stitching files (action: `imagestitching`).

- **Optional**
- Environment Variable: `IMAGESTITCHING_PVCNAME`
- Default: `manage-imagestitching`

Related settings: `mas_manage_imagestitching_storage_class` (defaults to the cluster RWX storage class), `mas_manage_imagestitching_storage_size` (`20Gi`), `mas_manage_imagestitching_storage_mode` (`ReadWriteMany`), and `mas_manage_imagestitching_mount_path` (`imagestitching`).

#### manage_certificates

List of PEM certificate strings to import into the Manage truststore (action: `import-certs`). Requires `manage_certificates_alias_prefix`.

- **Required** for the action (or provide `manage_certificates_file_path_local`)
- Environment Variable: None (passed as variable; `manage_certificates_file_path_local` uses `MANAGE_CERTIFICATES_FILE_PATH_LOCAL`)
- Default: None

When invoked from `suite_app_config` for the AI Service integration, these variables are set automatically.

#### mas_manage_dbc_script_path_local

Local folder containing the `.dbc` scripts to load (action: `dbc-scripts`).

- **Required** for the action
- Environment Variable: `DBC_SCRIPT_PATH_LOCAL`
- Default: None

!!! warning
    This action is not idempotent by nature — running it again re-applies the scripts.

#### mas_manage_custom_persistent_volumes

Custom persistent volume definitions as a YAML list string (action: `pvc`). Each entry requires `pvcName`, `mountPath` and `size`; `storageClassName` defaults to the cluster RWX storage class.

- **Required** for the action (or provide `mas_manage_custom_persistent_volumes_file`)
- Environment Variable: `MAS_MANAGE_CUSTOM_PERSISTENT_VOLUMES`
- Default: None

The former discrete single-PVC variables (`MAS_APP_SETTINGS_CUSTOM_PVC_NAME`, `MAS_APP_SETTINGS_CUSTOM_MOUNT_PATH`, etc.) are replaced by the list format — express the former SRE default as a list entry with `pvcName: <instance>-<workspace>-cust-files-pvc` and `mountPath: /MeaGlobalDirs`.

### Database Access

#### db2_instance_name

Db2 Warehouse instance name, used by the actions that execute SQL against the Manage database (`bim`, `logging` with `mas_manage_logging_is_prod`).

- **Required** for those actions
- Environment Variable: `DB2_INSTANCE_NAME`
- Default: None

Not available when an external (JDBC) database is used; those actions fail with a clear message in that case. To find the instance name, go to the Db2 namespace and look for pods with `label=engine`. Describe the pod and find the `app` label value - that's your instance name.

## Example Playbooks

### Configure attachments and BIM together

The following sample can be used to deploy Manage and configure attachment storage and BIM support as part of the same workflow:

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_app_id: manage
    mas_app_channel: 8.4.x
    mas_instance_id: masinst1
    mas_workspace_id: masdev
    db2_instance_name: db2w-manage
    mas_app_settings_persistent_volumes_flag: true
    mas_manage_attachments_provider: filestorage
    mas_app_settings_bim_mount_path: /bim
  roles:
    - ibm.mas_devops.db2
    - ibm.mas_devops.suite_db2_setup_for_manage
    - ibm.mas_devops.suite_config
    - ibm.mas_devops.suite_app_install
    - ibm.mas_devops.suite_app_config
    - role: ibm.mas_devops.suite_app_config_manage
      vars:
        suite_app_config_manage_actions:
          - attachments
          - bim
```

### Import certificates from a file

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_workspace_id: masdev
    manage_certificates_file_path_local: /path/to/certs.yml
  roles:
    - role: ibm.mas_devops.suite_app_config_manage
      vars:
        suite_app_config_manage_actions: [import-certs]
```

### Add custom persistent volumes

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_workspace_id: masdev
    mas_manage_custom_persistent_volumes: |
      persistentVolumes:
        - mountPath: /MeaGlobalDirs
          pvcName: masinst1-masdev-cust-files-pvc
          size: 100Gi
  roles:
    - role: ibm.mas_devops.suite_app_config_manage
      vars:
        suite_app_config_manage_actions: [pvc]
```

## License

EPL-2.0
