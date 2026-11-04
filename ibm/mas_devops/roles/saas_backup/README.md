SaaS Backup
===============================================================================

Overview
-------------------------------------------------------------------------------
Backs up one SaaS cluster (`<account>/<region>/<cluster>`) and one or more MAS instances on it into a **single `.tar.gz`**
that also contains `metadata.json` and `SHA256SUMS`. It runs locally (`ansible-playbook`), needs no Tekton and never uploads,
restores or modifies anything on the cluster or in the repositories.

What is collected:

- **SaaS ENVS** instance folder `gitops/<account>/<region>/<cluster>/<instance>/` from the saas-envs repository
- **GitOps ENVS** instance folder from the gitops-envs repository (`<account>/<region>/<cluster>/<instance>` or `<account>/<cluster>/<instance>`)
- **OpenShift named resources** for Suite (core) and, when saas-envs `mas-apps-params.yaml` declares `manage`, Manage. This reuses the
  existing [suite_backup](suite_backup.md) and [suite_app_backup](suite_app_backup.md) roles in `strict_named_only` mode, once per
  instance, with the instance ID and workspace ID of that instance. There is no auto-discovery of secrets, CA private keys are not exported
  and persistent volume data is not backed up.
- **AWS Secrets Manager secrets**, only the exact secret IDs listed in `SAAS_BACKUP_AWS_SECRET_IDS` (optional, empty by default)

!!! warning

    This role has only been exercised against stubbed `oc`/Kubernetes modules and local git repositories. It has not been validated against a real cluster, a
    staging pipeline or real AWS Secrets Manager.

    The list of AWS secrets that are *required* for a SaaS backup is not defined in the repositories, so none are collected unless you list them. Nothing is inferred.

Command
-------------------------------------------------------------------------------
```bash
export SAAS_BACKUP_ACCOUNT=aws-dev
export SAAS_BACKUP_REGION=us-east-2
export SAAS_BACKUP_CLUSTER=fvtsaas
export SAAS_BACKUP_INSTANCES=fvtsaas,fvtsaas2
export SAAS_BACKUP_OUTPUT_DIR=/var/backups/mas
export SAAS_ENVS_REPO_URL=git@github.ibm.com:<org>/saas-envs.git
export SAAS_ENVS_BRANCH=master
export GITOPS_ENVS_REPO_URL=git@github.ibm.com:<org>/gitops-envs.git
export GITOPS_ENVS_BRANCH=master
oc login ...        # the cluster must be the one named in saas-envs cluster-params.yaml (cluster.url)
ansible-playbook ibm.mas_devops.br_saas_backup
```

Use `SAAS_ENVS_CHECKOUT=/path/to/saas-envs` / `GITOPS_ENVS_CHECKOUT=/path/to/gitops-envs` instead of the URL and branch variables to use an existing checkout.

Prerequisites
-------------------------------------------------------------------------------
- `oc` logged in to the cluster with read access to the `mas-<instance>-core` and `mas-<instance>-manage` namespaces and the CRDs
- `git` and access to both repositories (credentials are never logged or stored; credentials embedded in a URL are redacted in `metadata.json`)
- The Ansible collection `kubernetes.core` and its Python client
- `aws` CLI with credentials in the environment, only when `SAAS_BACKUP_AWS_SECRET_IDS` is set
- `tar` is not required to create the archive; it is used below to inspect it

Role Variables
-------------------------------------------------------------------------------
### Selection

| Variable (environment variable) | Required | Description |
| --- | --- | --- |
| `saas_backup_account` (`SAAS_BACKUP_ACCOUNT`) | yes | Account folder, e.g. `aws-dev` |
| `saas_backup_region` (`SAAS_BACKUP_REGION`) | yes | Region folder, e.g. `us-east-2` |
| `saas_backup_cluster` (`SAAS_BACKUP_CLUSTER`) | yes | Cluster ID, e.g. `fvtsaas` |
| `saas_backup_instances` (`SAAS_BACKUP_INSTANCES`) | yes | Comma separated instance IDs; each runs the OpenShift backup once |
| `saas_backup_workspace_ids` (`SAAS_BACKUP_WORKSPACE_IDS`) | no | `instance=workspace,instance2=workspace2`. Overrides the saas-envs value |
| `saas_backup_output_dir` (`SAAS_BACKUP_OUTPUT_DIR`) | yes | Absolute path; receives the archive and its `.sha256` sidecar |

The workspace ID of an instance is `SAAS_BACKUP_WORKSPACE_IDS`, otherwise `mas_workspaces.id` in the instance's saas-envs `mas-instance-params.yaml`.
It is never guessed. The run fails if it is not a valid ID, if `mas_instance.id` in that file differs from the instance, or if the `Suite` /
`Workspace` custom resources do not exist in `mas-<instance>-core`.

### Repositories
Provide exactly one of the URL or the checkout for each repository. A URL requires its branch and is cloned (depth 1) into a temporary directory at backup time.

| Variable | Description |
| --- | --- |
| `SAAS_ENVS_REPO_URL`, `SAAS_ENVS_BRANCH` / `SAAS_ENVS_CHECKOUT` | SaaS ENVS repository (required) |
| `GITOPS_ENVS_REPO_URL`, `GITOPS_ENVS_BRANCH` / `GITOPS_ENVS_CHECKOUT` | GitOps ENVS repository (required unless `SAAS_BACKUP_ALLOW_MISSING_GITOPS_ENVS=true`) |

For an existing checkout the commit SHA and branch are read from it, and the run fails when the snapshotted folder has uncommitted changes.

### Explicit opt-outs (all default `false`, all recorded in `metadata.json` `warnings`)

| Variable | Effect |
| --- | --- |
| `SAAS_BACKUP_ALLOW_MISSING_GITOPS_ENVS` | Allow no GitOps ENVS repository, or an instance without a folder in it |
| `SAAS_BACKUP_ALLOW_DIRTY_CHECKOUT` | Allow uncommitted changes in an existing checkout |
| `SAAS_BACKUP_SKIP_CLUSTER_URL_CHECK` | Skip the comparison of `oc whoami --show-server` with `cluster.url` in saas-envs `cluster-params.yaml` |
| `SAAS_BACKUP_INCLUDE_MANUAL_CERTS` | Include the saas-envs `manual-certs` folders. They hold TLS **private keys in plaintext**, so they are excluded by default. No backup encryption has been approved |

### AWS secrets
`SAAS_BACKUP_AWS_SECRET_IDS` is a comma separated list of full secret names/ARNs. Each is read with `aws secretsmanager get-secret-value` in the region
declared by `secrets.avp_aws_secret_region` in saas-envs `cluster-params.yaml` (the cluster must declare `secrets.avp_type: aws`). Values are written to
`aws-secrets/` with mode 0600 and never printed (`no_log`). The AWS credentials used to run the CLI are never stored. Any unreadable or empty secret fails the run.

Output
-------------------------------------------------------------------------------
`<output_dir>/saas-backup-<account>-<region>-<cluster>-<UTC timestamp>.tar.gz` plus `<archive>.sha256` (the archive checksum, kept outside the archive), both mode 0600.
The run refuses to overwrite an existing archive. On any failure the work directory is removed and no archive is left.

```
saas-backup-<account>-<region>-<cluster>-<timestamp>/
  metadata.json
  SHA256SUMS
  saas-envs/gitops/<account>/<region>/<cluster>/<instance>/...
  gitops-envs/<path in the repository>/...
  openshift/<instance>/backup-<timestamp>-suite/...
  openshift/<instance>/backup-<timestamp>-app-manage/...
  aws-secrets/NN-<secret id>.secret          (only when requested)
```

`metadata.json` records account, region, cluster, API server, instances, timestamp, the repository URL/name/branch/commit SHA (and whether it was cloned or an
existing checkout), per instance the workspace ID and its source, namespaces, Suite/Manage reconciled versions and operator CSV where available,
resources backed up and named resources that were not found, the AWS secret IDs and region (never values), scope, warnings, and the size, SHA-256 and
whether it contains a plaintext private key for every file. `SHA256SUMS` covers every file including `metadata.json` and does not list itself. The plugin reads the
finished archive back and compares every member with these checksums before reporting success.

### Inspect and verify
```bash
tar -tzf saas-backup-*.tar.gz                                          # list contents
tar -xzOf saas-backup-*.tar.gz '*/metadata.json' | python3 -m json.tool   # read the manifest
shasum -a 256 -c saas-backup-*.tar.gz.sha256                           # verify the archive (sha256sum -c on Linux)
mkdir x && tar -xzf saas-backup-*.tar.gz -C x && (cd x/* && shasum -a 256 -c SHA256SUMS)   # verify the contents
```

Failure behaviour
-------------------------------------------------------------------------------
The run stops with a clear message for: missing/invalid inputs, `oc` missing or not logged in, the logged in cluster not matching saas-envs, a repository
that cannot be cloned or read, a missing saas-envs (or gitops-envs) instance folder, an unresolved instance/workspace ID, a missing `Suite`/`Workspace`,
namespaces that cannot be read, any failed or missing required OpenShift resource (from the reused roles), and any AWS secret that cannot be read.

Known limitations
-------------------------------------------------------------------------------
- Only core and Manage are backed up. Other applications declared in saas-envs (for example Facilities) are listed in `metadata.json` as not backed up.
- No restore, no upload, no persistent volume data and no CA private keys.
- Operator/product versions are best effort: if the core `Subscription` or `ManageApp` cannot be read the version is recorded as `unavailable` and the backup continues. Every other read is required.
- The required AWS secret list is not defined; the gitops-envs folder layout is not uniform across environments, so both `<account>/<region>/<cluster>/<instance>`
  and `<account>/<cluster>/<instance>` are tried and an ambiguous match fails.
- The Tekton/CLI backup path does not set `MAS_WORKSPACE_ID` for the Suite backup task; this role passes it explicitly.

License
-------------------------------------------------------------------------------
EPL-2.0
