SaaS Backup
===============================================================================

Overview
-------------------------------------------------------------------------------
Backs up one SaaS cluster (`<account>/<region>/<cluster>`) and one or more MAS instances on it into a **single `.tar.gz`**
that also contains `metadata.json` and `SHA256SUMS`. It runs locally (`ansible-playbook`), needs no Tekton and never uploads,
restores or modifies anything on the cluster or in the repositories.

What is collected:

- **SaaS ENVS cluster-level files**, the files directly inside `gitops/<account>/<region>/<cluster>/` in the saas-envs repository (for example
  `cluster-params.yaml` and CA certificate `.pem` files). Copied once per archive, not recursively.
- **GitOps ENVS cluster-level files**, the files directly inside `<account>/<cluster>/` in the gitops-envs repository (for example the `ibm-dro.yaml` and
  `ibm-operator-catalog.yaml` application files). Copied once per archive, not recursively, and only when a GitOps ENVS repository is supplied.
- **SaaS ENVS** folders of the **selected instances only** `gitops/<account>/<region>/<cluster>/<instance>/` from the saas-envs repository
- **GitOps ENVS** folders of the **selected instances only** from the gitops-envs repository (`<account>/<region>/<cluster>/<instance>` or `<account>/<cluster>/<instance>`)
- **OpenShift named resources** for Suite (core) and, when saas-envs `mas-apps-params.yaml` declares `manage`, Manage. This reuses the
  existing [suite_backup](suite_backup.md) and [suite_app_backup](suite_app_backup.md) roles in `strict_named_only` mode, once per
  instance, with the instance ID and workspace ID of that instance. There is no auto-discovery of secrets, CA private keys are not exported
  and persistent volume data is not backed up.
- **AWS Secrets Manager secrets**, only the exact secret IDs listed in `SAAS_BACKUP_AWS_SECRET_IDS` (optional, empty by default)

!!! warning

    The list of AWS secrets that are *required* for a SaaS backup is not defined in the repositories, so none are collected unless you list them. Nothing is inferred.

    See [Testing status](#testing-status) for what has and has not been validated.

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
- Only when `SAAS_BACKUP_ENCRYPTION_ENABLED=true`: on the machine running `ansible-playbook`, the Python package `cryptography` (>= 42.0.0, see `requirements.txt`) and
  **OpenSSL 3.5 or later with ML-KEM-768 support** (`openssl list -kem-algorithms` must list `ML-KEM-768` and `openssl pkeyutl -help` must list `-encap`). The run fails with a clear error otherwise

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

### Encryption (optional)

| Variable (environment variable) | Default | Description |
| --- | --- | --- |
| `saas_backup_encryption_enabled` (`SAAS_BACKUP_ENCRYPTION_ENABLED`) | `false` | Encrypt the finished archive to `<archive>.tar.gz.enc` |
| `saas_backup_encryption_public_key_path` (`SAAS_BACKUP_ENCRYPTION_PUBLIC_KEY_PATH`) | | Required when enabled. Absolute path of the persistent ML-KEM-768 **public** key (PEM) |
| `saas_backup_encryption_output_path` (`SAAS_BACKUP_ENCRYPTION_OUTPUT_PATH`) | archive path + `.enc` | Optional absolute path ending in `.tar.gz.enc` |

Encryption runs on the Ansible controller inside the same block as packaging, immediately after it, so a failure fails the backup. It uses ML-KEM-768
(OpenSSL `pkeyutl -encap`), HKDF-SHA256 and AES-256-GCM in 1 MiB chunks; the whole header is authenticated as GCM additional data. `<archive>.tar.gz.enc` and
`<archive>.tar.gz.enc.sha256` are created with mode 0600 and never overwrite existing files.
After encryption succeeds, the encrypted archive and its checksum sidecar are verified (non-empty, existing, matching SHA-256 checksum). Once verified, the
original plaintext `.tar.gz` archive and its `.sha256` sidecar are **automatically removed** to ensure encryption at rest. If encryption or post-encryption
verification fails, the plaintext archive and sidecar are preserved on disk for recovery/debugging, and the playbook fails.
The backup needs only the public key; the private key is never read, copied into the archive or required. Generate one persistent key pair once and keep the
private key outside the backup host, for example:

```bash
openssl genpkey -algorithm ML-KEM-768 -out mlkem-private.pem
openssl pkey -in mlkem-private.pem -pubout -out mlkem-public.pem
```

Decryption, verification and restoration are provided by the [saas_restore](saas_restore.md) role (`br_saas_restore` playbook), which uses `decryptArchive`
from `plugins/module_utils/saas_backup_encryption.py`.

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
With encryption enabled, `<archive>.tar.gz.enc` and `<archive>.tar.gz.enc.sha256` are written next to it, and upon successful verification the plaintext `.tar.gz` and `.tar.gz.sha256` are removed.
The run refuses to overwrite an existing archive. On any failure the work directory is removed and no archive is left.

```
saas-backup-<account>-<region>-<cluster>-<timestamp>/
  metadata.json
  SHA256SUMS
  saas-envs/gitops/<account>/<region>/<cluster>/<cluster-level files>      (once)
  saas-envs/gitops/<account>/<region>/<cluster>/<instance>/...             (selected instances only)
  gitops-envs/<account>/<cluster>/<cluster-level files>                    (once, when GitOps ENVS is supplied)
  gitops-envs/<path in the repository>/...                                 (selected instances only)
  openshift/<instance>/backup-<timestamp>-suite/...
  openshift/<instance>/backup-<timestamp>-app-manage/...
  aws-secrets/NN-<secret id>.secret          (only when requested)
```

Unselected instance folders in the cluster directories are never copied. The cluster-level file names are listed in `metadata.json` under `cluster_level_files`.
Cluster-level files are copied as they are, so a private key placed directly in a cluster folder would be included (and flagged in `metadata.json`).
This is not a guarantee that every License Services (SLS) dependency, secret or certificate is backed up; only the files and named resources described above are collected.

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

Testing status
-------------------------------------------------------------------------------
### Tested
- Unit and static tests with stubbed `oc`/Kubernetes modules and local git repositories.
- An actual backup of the Noble8 cluster with encryption enabled completed successfully. The playbook recap was `ok=124 changed=13 failed=0`.
  The encrypted archive was generated and verified, and the plaintext archive and its sidecar were removed after successful encryption.
- An actual `decrypt_only` restore of that Noble8 encrypted backup (see [saas_restore](saas_restore.md)) completed successfully with recap
  `ok=14 changed=0 failed=0 skipped=3`. The encrypted archive checksum, ML-KEM decapsulation, AES-256-GCM authentication and all 114 internal
  `SHA256SUMS` entries were verified. The decrypted archive contained 115 files.

### Not tested
- `full_restore` against a live OpenShift cluster has **not** been tested, so restoring a SaaS backup onto a cluster is not validated.
- The Noble8 results above do not cover other clusters, other environments, or backups taken without encryption.
- Collecting AWS Secrets Manager secrets (`SAAS_BACKUP_AWS_SECRET_IDS`) against real AWS Secrets Manager is not covered by the verified results listed above.

Known limitations
-------------------------------------------------------------------------------
- Only core and Manage are backed up. Other applications declared in saas-envs (for example Facilities) are listed in `metadata.json` as not backed up.
- This role does not restore (see [saas_restore](saas_restore.md)), does not upload, and does not back up persistent volume data or CA private keys.
- Operator/product versions are best effort: if the core `Subscription` or `ManageApp` cannot be read the version is recorded as `unavailable` and the backup continues. Every other read is required.
- The required AWS secret list is not defined; the gitops-envs folder layout is not uniform across environments, so both `<account>/<region>/<cluster>/<instance>`
  and `<account>/<cluster>/<instance>` are tried and an ambiguous match fails.
- The Tekton/CLI backup path does not set `MAS_WORKSPACE_ID` for the Suite backup task; this role passes it explicitly.

License
-------------------------------------------------------------------------------
EPL-2.0
