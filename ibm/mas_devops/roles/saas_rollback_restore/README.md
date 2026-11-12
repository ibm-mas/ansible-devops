SaaS Upgrade Rollback: Restore
===============================================================================

Overview
-------------------------------------------------------------------------------
Returns one SaaS cluster and one or more of its MAS instances to the state held in a **backup set** taken before an upgrade
(a change of `channel` in `mas-instance-params.yaml` and of the catalog `version` in `cluster-params.yaml`). It is **destructive**: it drops and
restores the Manage and Facilities databases, overwrites Mongo collections, replaces Secrets, ConfigMaps and custom resources, and reinstalls
operators at the versions recorded in the backup.

The design, the order and the reasons are in `saas-tekton/docs/upgrade-rollback/03-restore-process.md`. This role implements that document.
The backup set is written by the backup runbook (`02-backup-process.md`); the Kubernetes part of it comes from the
[saas_backup](saas_backup.md) role and the Db2 part from the `ssp-mas-sre-automation` playbooks and the Mongo part from the [mongodb](mongodb.md) role and the `br_mongodb` playbook (branch `mascore-20279`).

!!! warning

    This role has **not been run against a cluster**. It was syntax-checked and exercised in a dry run against a stub `oc` and a fixture backup set only.
    It runs in **dry-run mode by default**: it reads the cluster, prints the plan and writes nothing to the cluster, Git or S3.
    See [Testing status](#testing-status).

Two approaches (choose with `SAAS_ROLLBACK_APPROACH`):

| | `git-first` (default) | `cluster-first` |
| --- | --- | --- |
| Who restores the MAS custom resources | ArgoCD from the reverted Git, then a drift pass for what Git does not own | This role, from the backup, in dependency order |
| Git revert | Early | Late, after the cluster is correct |
| Hooks and jobs run again | Yes | No, until the final resume |

Both support a manual Git revert (a person merges a pull request) and an automated one (`SAAS_ROLLBACK_GIT_REVERT_MODE=automated`, the role pushes only the recorded lever values).

Command
-------------------------------------------------------------------------------
```bash
export SAAS_ROLLBACK_BACKUP_DIR=/work/backups/upg-noble10-20261104-101500   # the backup set (contains manifest.json)
export SAAS_ROLLBACK_CLUSTER=noble10
export SAAS_ROLLBACK_INSTANCES=test20414
export SAAS_ROLLBACK_ARGO_ROOT_APP=root.fyre-noble10-dev
export SAAS_ROLLBACK_APPROACH=git-first
export SAAS_ROLLBACK_GIT_REVERT_MODE=manual
export SAAS_ROLLBACK_SSP_DIR=/work/ssp-mas-sre-automation                   # branch mascore-20278-db2-backup-restore
export SAAS_ROLLBACK_DB2_CLOUD=aws
oc login ...                                                                 # the cluster named in the backup (record/run.json)

# 1. Dry run (default): reads, checks, prints the plan
ansible-playbook ibm.mas_devops.br_saas_rollback_restore

# 2. Live run
export SAAS_ROLLBACK_DRY_RUN=false
export SAAS_ROLLBACK_CHANGE_TICKET=CHG0012345
export SAAS_ROLLBACK_APPROVED_BY=jdoe
export SAAS_ROLLBACK_CONFIRM=upg-noble10-20261104-101500                     # must equal manifest.backupId
export SAAS_ROLLBACK_PRE_ROLLBACK_BACKUP_DONE=true                           # or SAAS_ROLLBACK_SKIP_PRE_ROLLBACK_BACKUP=true
ansible-playbook ibm.mas_devops.br_saas_rollback_restore
```

Prerequisites
-------------------------------------------------------------------------------
- `oc` logged in to the cluster that was backed up, as a cluster admin. The server must equal `record/run.json` `ocServer` (override: `SAAS_ROLLBACK_SKIP_CLUSTER_URL_CHECK=true`)
- On the machine that runs the playbook: `python3` with `PyYAML`, `jq`, `yq` (mikefarah v4), `git`, `aws`, `curl`, `ansible-playbook`; the collection `kubernetes.core` and its Python client
- A **backup set** that passes `SHA256SUMS` (see the layout below)
- A checkout of `ssp-mas-sre-automation` on branch `mascore-20278-db2-backup-restore` (`SAAS_ROLLBACK_SSP_DIR`) and the credentials its playbooks need (`SAAS_ROLLBACK_SSP_VARS_FILE`)
- **Mongo Community:** the `br_mongodb` playbook and `mongodb` role. **Mongo Atlas:** the `atlas` provider (`backup.yml`, `restore.yml`). Both are on branch `mascore-20279` of `ansible-devops`. This branch is **not merged** into `mascore-20277`, so the collection that runs this role must contain both, or the Mongo phase fails at run time
- **Mongo Atlas** also needs the collection `amazon.aws`, the `aws` CLI (the `verify` phase reads `mongo-backup.txt` from S3) and the Atlas API keys
- For DocumentDB and the IBM Cloud logical restore: `mongorestore` on the machine and `SAAS_ROLLBACK_MONGO_*`. The `mascore-20279` branch has no DocumentDB restore
- The Db2 backup images and keystore copy still in S3 (checked in the `verify` phase)
- A **pre-rollback backup** of the post-upgrade databases, or an explicit decision to skip it (see the live-run gate below)
- The recorded operator CSVs must still be served by the catalog (checked in the `catalog` phase). Nothing in this role can recreate a CSV that the catalog no longer has

Backup set layout (read by this role)
-------------------------------------------------------------------------------
```
<SAAS_ROLLBACK_BACKUP_DIR>/
  manifest.json            backupId, cluster, git.configRepo{url,branch,path,sha}, instances[]{id,workspace,db{mongo,manage,facilities},quiesce}
  SHA256SUMS
  raw/                     <ns>__secrets.json, <ns>__configmaps.json, cr__<crd>.json, all__<kind>.json, cluster__<kind>.json, crds.json, _missing.txt
  record/                  subscriptions.json, catalog-image.txt, run.json, manage-mode.txt, fac-podtemplates.json, db2-cronjobs.json,
                           db2u-cr.json, *-status.json, export-index.tsv
  argocd/                  applications-summary.json, appset-generators.json
  config-repo/             copy of the lever files at the backup commit
  roles/backup-<id>-mongoce/data/   mongodump-<id>.tar.gz, mongodb-info.yaml
  roles/backup-<id>-app-{manage,facilities}/data/   <pvc>.tar.gz
  external/                aws-secretsmanager/, cis/
```

Phases
-------------------------------------------------------------------------------
Phases run in this order. Use `SAAS_ROLLBACK_START_AT`, `SAAS_ROLLBACK_STOP_AFTER` and `SAAS_ROLLBACK_SKIP_PHASES` to select. An unknown name fails the run.

`git-first`: `verify`, `freeze`, `snapshot`, `stop`, `objects`, `mongo`, `db2`, `pv`, `git_revert`, `catalog`, `crs`, `operators`, `sync_core`, `start`, `sync_apps`, `drift`, `external`, `verify_post`, `resume`

`cluster-first`: `verify`, `freeze`, `snapshot`, `stop`, `objects`, `certs`, `mongo`, `db2`, `pv`, `catalog`, `crs`, `operators`, `reconcile`, `start`, `git_revert`, `prove`, `external`, `verify_post`, `resume`

| Phase | What it does | Changes state |
| --- | --- | --- |
| `verify` | Checks `SHA256SUMS`, cluster and instances against the manifest, `oc` server, missing named objects, Db2 images in S3 | no |
| `freeze` | Terminates running syncs and sets `syncPolicy.automated` to null on the root, every ApplicationSet template and every Application; gate holds for `FREEZE_HOLD_SECONDS` | ArgoCD |
| `snapshot` | Exports the post-upgrade state to `restore/<run id>/before/` (the way back) | no (local files) |
| `stop` | Manage mode `down`, Facilities replicas 0, Db2 CronJobs suspended, MAS operators and Core, SLS, Manage and Facilities workloads to 0; waits for no running pods. Never touches the Db2u or Mongo operators or pods | yes (downtime starts) |
| `objects` | Namespaces, Secrets, ConfigMaps from `raw/` (`git-first`: only objects ArgoCD does not track). Critical Secrets must equal the backup | yes |
| `certs` | cert-manager `ClusterIssuer`, `Issuer`, `Certificate` (`cluster-first` only); no Certificate may be re-issued | yes |
| `mongo` | Per instance: Mongo CE through `br_mongodb` (`MONGODB_ACTION=restore-database`), Atlas through the `mongodb` role (`restore`, collection restore job, `OVERWRITE_EXISTING`), DocumentDB and IBM Cloud logical dump through `mongorestore`, IBM Cloud new service by repoint; DRO objects | yes |
| `db2` | Per instance: pre-checks, `mas_db_restore_only.yaml` (wrapper of `mas_db_restore` `restore_database.yaml`), gates, CronJobs back | yes |
| `pv` | Manage JMS store and Facilities `userfiles` and `log` from the archives | yes |
| `git_revert` | Compares the lever files with the backup; manual: stops with the diff or accepts a merged `SAAS_ROLLBACK_GIT_ROLLBACK_SHA`; automated: writes only the recorded values with `yq`, guards the diff, commits and pushes. Hard-refreshes the root | Git (automated) |
| `catalog` | Pins the CatalogSource to the recorded image or digest, waits `READY`, checks every recorded CSV is in the PackageManifest | yes |
| `crs` | Puts back the custom resource specs in dependency order while the operators are still the new CSV at 0 replicas (Manage `mode: down`, Facilities replicas 0) | yes |
| `operators` | CRD gate, then per Subscription in order: delete Subscription and CSV, create it at the recorded CSV with manual approval, approve only that InstallPlan, wait `Succeeded`, set the recorded approval | yes |
| `sync_core` | `git-first`: scale back up, sync SLS, Db2u, config charts, Suite and Workspace Applications wave by wave (no prune), wait Ready | yes |
| `reconcile` | `cluster-first`: scale back up, wait SLS, Suite, Workspace, ManageApp, FacilitiesApp Ready, put Secrets and ConfigMaps back again | yes |
| `start` | Manage `mode` from the record, Facilities replicas from the record, wait Ready | yes (downtime ends) |
| `sync_apps` | `git-first`: sync Manage, Facilities, app config, add-on and postsync Applications (waves 300 and up) | yes |
| `drift` | `git-first`: exports the live state, diffs it with `raw/`, puts back what differs, diffs again | yes |
| `prove` | `cluster-first`: every Application Synced and Healthy; lists objects that exist now but not in the backup | no |
| `external` | Compares AWS Secrets Manager versions (opt-in) and prints the manual items | Secrets Manager (opt-in) |
| `verify_post` | X1 to X18 of the design: operators, catalog, Secrets and CR specs, critical Secrets, certificates, Ready, versions, `/maximo/ping`, Db2 CronJobs, Facilities replicas, Manage mode, ArgoCD, Git | no |
| `resume` | Re-applies the recorded sync policies bottom-up with prune off, checks everything is Synced, then re-applies with prune as recorded | ArgoCD |

Failure and re-run
-------------------------------------------------------------------------------
- Every phase can be repeated. A failure prints the state (`report_state.yml`) and stops. Re-run with the **same** `SAAS_ROLLBACK_RUN_ID` and `SAAS_ROLLBACK_START_AT=<failed phase>`. The run id is printed at the start (`rb-<cluster>-<timestamp>`); records are in `<backup dir>/restore/<run id>/` (`before/`, `after/`, `record/`).
- **On failure the role does not resume ArgoCD, start Manage or scale anything.** Once the `mongo`, `db2` or `pv` phase has started, resuming ArgoCD onto a half-restored cluster would re-apply the upgrade. Resume only through the `resume` phase, after `verify_post` passes.
- `stop` keeps the first replica record in `before/replicas-*.json` on a re-run, so the values restored later are the ones from before the stop.
- A dry run writes its working files under `/tmp/<run id>-work` and `/tmp/<run id>-git`, not in the backup set.

Role Variables
-------------------------------------------------------------------------------
All inputs are environment variables read in `defaults/main.yml`. The playbook can therefore be started from a Tekton task with one `env:` block.

### Backup set and scope

| Variable (environment variable) | Required | Description |
| --- | --- | --- |
| `saas_rollback_backup_dir` (`SAAS_ROLLBACK_BACKUP_DIR`) | yes | Absolute path of the backup set (contains `manifest.json`) |
| `saas_rollback_cluster` (`SAAS_ROLLBACK_CLUSTER`) | yes | Cluster id; must equal `manifest.cluster` |
| `saas_rollback_instances` (`SAAS_ROLLBACK_INSTANCES`) | yes | Comma-separated instance ids; all must be in `manifest.instances` |
| `saas_rollback_argo_root_app` (`SAAS_ROLLBACK_ARGO_ROOT_APP`) | yes | Root Application, e.g. `root.fyre-noble10-dev` |
| `saas_rollback_workspace_ids` (`SAAS_ROLLBACK_WORKSPACE_IDS`) | no | `inst=workspace,...`; default is the manifest value, then `main` |
| `saas_rollback_account` / `saas_rollback_region` (`SAAS_ROLLBACK_ACCOUNT`, `SAAS_ROLLBACK_REGION`) | no | Shown in the run summary only |

### Run control

| Variable (environment variable) | Required | Description |
| --- | --- | --- |
| `saas_rollback_dry_run` (`SAAS_ROLLBACK_DRY_RUN`) | no | Default `true`. Set `false` for a live run |
| `saas_rollback_approach` (`SAAS_ROLLBACK_APPROACH`) | no | `git-first` (default) or `cluster-first` |
| `saas_rollback_git_revert_mode` (`SAAS_ROLLBACK_GIT_REVERT_MODE`) | no | `manual` (default) or `automated` |
| `saas_rollback_run_id` (`SAAS_ROLLBACK_RUN_ID`) | no | Reuse the value of the failed run when re-running |
| `saas_rollback_start_at` / `saas_rollback_stop_after` / `saas_rollback_skip_phases` (`SAAS_ROLLBACK_START_AT`, `_STOP_AFTER`, `_SKIP_PHASES`) | no | Phase selection |
| `saas_rollback_timeout` (`SAAS_ROLLBACK_TIMEOUT`) | no | Seconds for each long wait. Default `3600` |
| `saas_rollback_freeze_hold_seconds` (`SAAS_ROLLBACK_FREEZE_HOLD_SECONDS`) | no | Default `120` |
| `saas_rollback_argo_ns` (`SAAS_ROLLBACK_ARGO_NS`) | no | Default `openshift-gitops` |

### Live-run gate (all required when `SAAS_ROLLBACK_DRY_RUN=false`)

| Variable (environment variable) | Description |
| --- | --- |
| `saas_rollback_change_ticket` (`SAAS_ROLLBACK_CHANGE_TICKET`) | Change record |
| `saas_rollback_approved_by` (`SAAS_ROLLBACK_APPROVED_BY`) | Approver |
| `saas_rollback_confirm` (`SAAS_ROLLBACK_CONFIRM`) | Must equal `manifest.backupId` |
| `saas_rollback_pre_rollback_backup_done` (`SAAS_ROLLBACK_PRE_ROLLBACK_BACKUP_DONE`) | `true` once the post-upgrade databases are backed up. Or: |
| `saas_rollback_skip_pre_rollback_backup` (`SAAS_ROLLBACK_SKIP_PRE_ROLLBACK_BACKUP`) | `true` accepts that the post-upgrade databases are lost (requester decision) |

### Git revert of the upgrade levers

| Variable (environment variable) | Required | Description |
| --- | --- | --- |
| `saas_rollback_env_type` (`SAAS_ROLLBACK_ENV_TYPE`) | no | `aws-saas` (default; `cluster-params.yaml`, `<inst>/mas-instance-params.yaml`, `<inst>/mas-apps-params.yaml`) or `gitops-envs` (`ibm-operator-catalog.yaml`, `<inst>/*.yaml`) |
| `saas_rollback_levers_json` (`SAAS_ROLLBACK_LEVERS_JSON`) | no | JSON list that replaces the built-in lever definition |
| `saas_rollback_git_repo_url` / `_branch` / `_path` (`SAAS_ROLLBACK_GIT_REPO_URL`, `_GIT_BRANCH`, `_GIT_PATH`) | no | Default to `manifest.git.configRepo` |
| `saas_rollback_git_user` / `saas_rollback_git_token` (`SAAS_ROLLBACK_GIT_USER`, `SAAS_ROLLBACK_GIT_TOKEN`) | automated mode, private repo | HTTPS credentials, passed through `GIT_ASKPASS`, never printed |
| `saas_rollback_git_author_name` / `_email` (`SAAS_ROLLBACK_GIT_AUTHOR_NAME`, `_EMAIL`) | no | Commit author in automated mode |
| `saas_rollback_git_rollback_sha` (`SAAS_ROLLBACK_GIT_ROLLBACK_SHA`) | manual mode, re-run | SHA of the merged rollback pull request; the root Application revision must equal it |

### Catalog and operators

| Variable (environment variable) | Description |
| --- | --- |
| `saas_rollback_catalog_source_name` / `_ns` (`SAAS_ROLLBACK_CATALOG_SOURCE_NAME`, `_NS`) | Default `ibm-operator-catalog` in `openshift-marketplace` |
| `saas_rollback_catalog_pin_digest` (`SAAS_ROLLBACK_CATALOG_PIN_DIGEST`) | Default `true`: pin `<image>@sha256:<digest>` from `record/catalog-image.txt` |
| `saas_rollback_operator_exclude_ns_regex` (`SAAS_ROLLBACK_OPERATOR_EXCLUDE_NS_REGEX`) | Subscriptions in these namespaces are never reinstalled. Default: `openshift-*` and `cert-manager-operator` |
| `saas_rollback_ca_namespace` (`SAAS_ROLLBACK_CA_NAMESPACE`) | Namespace of the internal CA Secret. Default `cert-manager` |

### Mongo

The variant comes from the manifest, `instances[].db.mongo.variant`: `community`, `atlas`, `documentdb` or `ibm-cloud`.

| Manifest field | Variant | Used for |
| --- | --- | --- |
| `backupId`, `dumpPath` | community | `MONGODB_BACKUP_VERSION` for `br_mongodb`; the dump under `roles/backup-<id>-mongoce/data/` |
| `catalogBuildId` | atlas | `catalog_build_id`: the key of `releases/<id>/mongo/mongo-backup.txt` in S3 |
| `projectId`, `clusterName` | atlas | `atlas_project_id`, `atlas_cluster_name` (or the `SAAS_ROLLBACK_ATLAS_*` variables) |
| `snapshotId`, `slsDatabase` | atlas | Compared with `mongo-backup.txt` in the `verify` phase |

| Variable (environment variable) | Description |
| --- | --- |
| `saas_rollback_atlas_project_id` / `_cluster_name` (`SAAS_ROLLBACK_ATLAS_PROJECT_ID`, `_CLUSTER_NAME`) | Atlas only; used when the manifest has no value |
| `saas_rollback_atlas_public_key` / `_private_key` (`SAAS_ROLLBACK_ATLAS_PUBLIC_KEY`, `_PRIVATE_KEY`) | Atlas API keys. Written to a mode-0600 extra-vars file that is removed afterwards. Or use the next row |
| `saas_rollback_atlas_account_id` / `_aws_region` (`SAAS_ROLLBACK_ATLAS_ACCOUNT_ID`, `_AWS_REGION`) | The `mongodb` role reads `<account>/mongodb-atlas` from AWS Secrets Manager |
| `saas_rollback_atlas_info_bucket` / `_info_region` (`SAAS_ROLLBACK_ATLAS_INFO_BUCKET`, `_INFO_REGION`) | Where `mongo-backup.txt` is read in the `verify` phase. Defaults `mref-backflow-test-bucket`, `eu-central-1`: the values hardcoded in the `mongodb` role |
| `saas_rollback_mongo_namespace` / `_instance_name` (`SAAS_ROLLBACK_MONGO_NAMESPACE`, `_INSTANCE_NAME`) | In-cluster Mongo CE. Defaults `mongoce`, `mas-mongo-ce` |
| `saas_rollback_mongo_host` / `_port` / `_user` / `_password` / `_tls_ca_file` / `_retry_writes` (`SAAS_ROLLBACK_MONGO_*`) | DocumentDB and IBM Cloud logical restore (`mongorestore`). DocumentDB needs TLS and `retryWrites=false` (default) |
| `saas_rollback_ibm_mongo_method` (`SAAS_ROLLBACK_IBM_MONGO_METHOD`) | `logical-dump` (default) or `new-service` |
| `saas_rollback_ibm_mongo_restored_service_name` (`SAAS_ROLLBACK_IBM_MONGO_RESTORED_SERVICE_NAME`) | `new-service` only |
| `saas_rollback_ibm_mongo_repoint_done` (`SAAS_ROLLBACK_IBM_MONGO_REPOINT_DONE`) | `new-service` only: `true` after MongoCfg, the Mongo Secrets and AWS Secrets Manager point at the new service |

### Databases and PV data

| Variable (environment variable) | Required | Description |
| --- | --- | --- |
| `saas_rollback_ssp_dir` (`SAAS_ROLLBACK_SSP_DIR`) | yes for Db2 | Checkout of `ssp-mas-sre-automation`, branch `mascore-20278-db2-backup-restore` |
| `saas_rollback_db2_cloud` (`SAAS_ROLLBACK_DB2_CLOUD`) | yes for Db2 | `ibm`, `aws`, `fyre` or `mcsp_aws` (RDS) |
| `saas_rollback_ssp_vars_file` (`SAAS_ROLLBACK_SSP_VARS_FILE`) | no | Vars file with the credentials the ssp playbooks read |
| `saas_rollback_db2_s3_endpoint` (`SAAS_ROLLBACK_DB2_S3_ENDPOINT`) | no | Default `https://s3.amazonaws.com` |
| `saas_rollback_helper_pod_image` (`SAAS_ROLLBACK_HELPER_POD_IMAGE`) | no | Image of the helper pod for the PV restore (needs `sh` and `tar`) |

### External systems

| Variable (environment variable) | Description |
| --- | --- |
| `saas_rollback_check_secrets_manager` (`SAAS_ROLLBACK_CHECK_SECRETS_MANAGER`) | Compare AWS Secrets Manager version ids with `external/aws-secretsmanager/` |
| `saas_rollback_restore_secrets_manager` (`SAAS_ROLLBACK_RESTORE_SECRETS_MANAGER`) | Move `AWSCURRENT` back to the saved version. A write to a shared service: get approval |
| `saas_rollback_aws_region` (`SAAS_ROLLBACK_AWS_REGION`) | Defaults to `AWS_DEFAULT_REGION` |

### Checks that can be switched off (all default `false`; each is a recorded decision)

| Variable (environment variable) | Switches off |
| --- | --- |
| `SAAS_ROLLBACK_SKIP_SHA_CHECK` | `SHA256SUMS` verification |
| `SAAS_ROLLBACK_SKIP_CLUSTER_URL_CHECK` | `oc` server equals `record/run.json` |
| `SAAS_ROLLBACK_SKIP_S3_CHECK` | Db2 image and keystore checks in S3 |
| `SAAS_ROLLBACK_ALLOW_MISSING_NAMED` | Failure on objects missing at backup time |
| `SAAS_ROLLBACK_ALLOW_CRD_GATE_FAILURE` | Failure when the upgrade changed CRD storage versions (a rollback may not be safe) |
| `SAAS_ROLLBACK_ALLOW_KEYSTORE_MISMATCH` | Db2 keystore in the pod equals the S3 copy |
| `SAAS_ROLLBACK_ALLOW_OUTOFSYNC` | Applications must be Synced and Healthy before prune and in `verify_post` |
| `SAAS_ROLLBACK_ALLOW_DRIFT` | Remaining differences after the drift pass and in `verify_post` X3 |
| `SAAS_ROLLBACK_FAIL_ON_LEFTOVERS` | When `true`, custom resources that exist now but not in the backup fail the run |
| `SAAS_ROLLBACK_SKIP_MANAGE_PING` | `/maximo/ping` check (X8) |

Example: Tekton task environment
-------------------------------------------------------------------------------
```yaml
env:
  - { name: SAAS_ROLLBACK_BACKUP_DIR,       value: $(params.backup-dir) }
  - { name: SAAS_ROLLBACK_CLUSTER,          value: $(params.cluster) }
  - { name: SAAS_ROLLBACK_INSTANCES,        value: $(params.instances) }
  - { name: SAAS_ROLLBACK_ARGO_ROOT_APP,    value: $(params.argo-root-app) }
  - { name: SAAS_ROLLBACK_APPROACH,         value: $(params.approach) }
  - { name: SAAS_ROLLBACK_GIT_REVERT_MODE,  value: $(params.git-revert-mode) }
  - { name: SAAS_ROLLBACK_DRY_RUN,          value: $(params.dry-run) }
  - { name: SAAS_ROLLBACK_CHANGE_TICKET,    value: $(params.change-ticket) }
  - { name: SAAS_ROLLBACK_APPROVED_BY,      value: $(params.approved-by) }
  - { name: SAAS_ROLLBACK_CONFIRM,          value: $(params.confirm) }
  - { name: SAAS_ROLLBACK_RUN_ID,           value: $(params.run-id) }
  - { name: SAAS_ROLLBACK_START_AT,         value: $(params.start-at) }
  - { name: SAAS_ROLLBACK_GIT_USER,         valueFrom: { secretKeyRef: { name: rollback-git, key: user } } }
  - { name: SAAS_ROLLBACK_GIT_TOKEN,        valueFrom: { secretKeyRef: { name: rollback-git, key: token } } }
```

Scope and limitations
-------------------------------------------------------------------------------
- One cluster and the instances named in `SAAS_ROLLBACK_INSTANCES`. A restore to another cluster or instance is out of scope.
- Manage and Facilities, plus Core, SLS, DRO and Mongo. CP4D and its services are out of scope and their Applications are not synced.
- The recovery point is the backup. Data written after it is not kept (the pre-rollback backup is the only copy).
- Db2 engine version changes in the same window are not supported; the role fails if the Db2 CR version differs from the record.
- ArgoCD namespaces and AppProjects are not touched; the user maps them.
- Downtime runs from `stop` to `start`; plan a maintenance window.
- The operator return relies on OLM behaviour: the old operator starts the moment its CSV succeeds, so all data and specs are restored first. There is no switch that installs a CSV but keeps it stopped.
- `strict_named_only` backups need a `mas-devops` release that supports it; check the backup set before relying on `_missing.txt`.
- Manage attachment buckets, CIS DNS and edge certificates are reported, not restored.
- No encryption of the backup set; keep it on controlled storage.
- Mongo Atlas: the S3 bucket and region of `mongo-backup.txt` are hardcoded in the `mongodb` role, and its snapshot retention default is 7 days. Atlas restores collections of the instance (`OVERWRITE_EXISTING`, `indexStrategy: ALL`); the Atlas restore job is the only recovery, with no local dump to fall back on. `mongo-backup.txt` is keyed by `catalog_build_id`: a second backup with the same build id overwrites it.
- Application names `<app>.<cluster>.<instance>` and the sync waves were taken from `gitops/root-applications`; confirm them on the first AWS run.

Testing status
-------------------------------------------------------------------------------
Not run against a cluster. What was exercised, with a stub `oc` that answers only `oc whoami`:

- `ansible-playbook --syntax-check`
- Dry runs through all phases of both approaches (cluster-specific phases skipped where the stub has no data)
- `git_revert` in manual and automated mode against a local bare repository, including the `yq` write and the diff guard
- `rr_helper.py`: `levers`, `diff-index`, `catalog-pin`, `ops-diff` argument parsing, `-h` of every sub-command
- `verify` with a stub `aws`: valid Atlas `mongo-backup.txt`, expired snapshot (fails), file of another instance (fails); the Atlas input check fails when the API keys are missing; the `mongo` phase passes in dry run for the `atlas` manifest variant

Not exercised: every call that needs a real cluster, Db2, Mongo, S3 or ArgoCD, including the live `br_mongodb` and Atlas runs, the extra-vars file being read by the `mongodb` role, and the parsing of a real `mongo-backup.txt`; operator reinstall (`op-return`); the Db2 wrapper (`files/mas_db_restore_only.yaml`); PV restore; the CRD gate on real CRDs.
Run the dry run on a non-production cluster first, then each phase alone with `SAAS_ROLLBACK_START_AT` and `SAAS_ROLLBACK_STOP_AFTER`.
