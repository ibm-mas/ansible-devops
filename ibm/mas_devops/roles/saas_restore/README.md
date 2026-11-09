SaaS Restore
===============================================================================

Overview
-------------------------------------------------------------------------------
Verifies, decrypts and (optionally) restores an **encrypted SaaS backup** (`<archive>.tar.gz.enc`) produced by [saas_backup](saas_backup.md) with
`SAAS_BACKUP_ENCRYPTION_ENABLED=true`. It runs locally (`ansible-playbook ibm.mas_devops.br_saas_restore`) and has two modes selected by
`SAAS_RESTORE_MODE`:

| Mode | What it does | Touches OpenShift |
| --- | --- | --- |
| `decrypt_only` (default) | Verifies the checksum, decrypts, authenticates, verifies the internal `SHA256SUMS`, reports metadata, then removes the plaintext | **Never** (`oc` is not invoked) |
| `full_restore` | Everything in `decrypt_only`, then extracts the archive and restores the OpenShift resources with the existing `suite_restore` and `suite_app_restore` roles | Yes, after every integrity check passed |

Pipeline (both modes, stops at the first failure):

1. SHA-256 of the `.tar.gz.enc` is compared with its strict `.sha256` sidecar
2. ML-KEM-768 decapsulation (OpenSSL `pkeyutl -decap`), HKDF-SHA256 and AES-256-GCM decryption into a private `0700` work directory. The plaintext is only
   published after every GCM tag (header included, as additional data) has verified, so a wrong key, tampered header or payload, or truncated file is rejected
3. The tar is inspected without extraction (no absolute, `..`, link or device members) and `SHA256SUMS` is checked against every file, including `metadata.json`
4. `metadata.json` is cross-checked with the manifest and the requested cluster and instances
5. The report is printed (cluster, API server, creation time, instances, applications, OpenShift/ENVS/AWS content counts, warnings)
6. `full_restore` only: restore. Always: the work directory is zero-filled and removed. The encrypted backup is never deleted or modified

Prerequisites
-------------------------------------------------------------------------------
- Ansible controller with `cryptography>=42` (see `requirements.txt`)
- **OpenSSL 3.5 or later** with ML-KEM-768 and `pkeyutl -decap` support (checked at run time). `openssl` on `PATH` must be that build
- The ML-KEM-768 **private key** (unencrypted PEM) matching the public key used for the backup, readable only by you (`chmod 600`). Only its path is used:
  the content is never loaded into Ansible variables, logged, copied or placed in the work directory
- `full_restore` additionally: `oc` logged in to the target cluster, and the prerequisites of [suite_restore](suite_restore.md) and
  [suite_app_restore](suite_app_restore.md)

Usage
-------------------------------------------------------------------------------
### Decrypt only (safe, no cluster)

```bash
export SAAS_RESTORE_ENCRYPTED_ARCHIVE_PATH=/var/backups/mas/saas-backup-aws-dev-us-east-2-fvtsaas-20260101T000000Z.tar.gz.enc
export SAAS_RESTORE_PRIVATE_KEY_PATH=/secure/mlkem-private.pem
export SAAS_RESTORE_OUTPUT_DIR=/var/tmp/mas-restore   # optional, must exist
ansible-playbook ibm.mas_devops.br_saas_restore
```

Optionally set `SAAS_RESTORE_CLUSTER` and/or `SAAS_RESTORE_INSTANCES` to assert that the backup is the one you expect.

### Full restore

```bash
export SAAS_RESTORE_MODE=full_restore
export SAAS_RESTORE_CLUSTER=fvtsaas
export SAAS_RESTORE_INSTANCES=fvtsaas
oc login ...
ansible-playbook ibm.mas_devops.br_saas_restore
```

Run `decrypt_only` first and read the report. `full_restore` requires `SAAS_RESTORE_CLUSTER` and `SAAS_RESTORE_INSTANCES`, every instance must exist in the
backup, and `oc whoami --show-server` must equal the `cluster_api_server` recorded in the backup (unless `SAAS_RESTORE_SKIP_CLUSTER_URL_CHECK=true`).
For each instance, `suite_restore` and then (when the backup holds Manage) `suite_app_restore` (`manage`, PVC data excluded) are run from
`<extract>/openshift/<instance>/backup-<created_utc>-{suite,app-manage}`.

Variables
-------------------------------------------------------------------------------

| Variable | Environment variable | Default | Description |
| --- | --- | --- | --- |
| `saas_restore_mode` | `SAAS_RESTORE_MODE` | `decrypt_only` | `decrypt_only` or `full_restore` |
| `saas_restore_encrypted_archive_path` | `SAAS_RESTORE_ENCRYPTED_ARCHIVE_PATH` | | **Required.** Absolute path ending in `.tar.gz.enc`; the `.sha256` sidecar must be next to it |
| `saas_restore_private_key_path` | `SAAS_RESTORE_PRIVATE_KEY_PATH` | | **Required.** Absolute path of the ML-KEM-768 private key (PEM) |
| `saas_restore_output_dir` | `SAAS_RESTORE_OUTPUT_DIR` | system temp dir | Existing absolute directory in which the private work directory is created |
| `saas_restore_cluster` | `SAAS_RESTORE_CLUSTER` | | Expected cluster ID. Required for `full_restore` |
| `saas_restore_instances` | `SAAS_RESTORE_INSTANCES` | | Comma separated instance IDs. Required for `full_restore`; must be in the backup |
| `saas_restore_skip_cluster_url_check` | `SAAS_RESTORE_SKIP_CLUSTER_URL_CHECK` | `false` | `full_restore` only: skip the API URL comparison |

Security and recovery
-------------------------------------------------------------------------------
- The private key is the only way to read the backup. Store it (and an offline copy) separately from the backups; losing it makes every backup encrypted
  with the matching public key unrecoverable. Never place it in the backup directory, a repository or CI logs
- Decrypted data exists only in the `0700` work directory (files `0600`), is never written next to the backup, and is zero-filled and removed in an `always`
  section even on failure. If the controller is killed mid-run, remove any leftover `saas-restore-*` directory in the output directory manually
- Nothing is overwritten: decryption and extraction refuse existing paths. The encrypted archive and its sidecar are never deleted
- `full_restore` does nothing on the cluster unless the checksum, authentication, manifest, metadata, cluster and instance checks all passed
- A failed integrity check means the file is corrupt or has been tampered with: do not restore from it, retrieve another copy of the backup
- Run `full_restore` first against a non-production cluster to confirm the result

Scope and limitations
-------------------------------------------------------------------------------
- Only the **OpenShift resources** are restored, by reusing `suite_restore` and `suite_app_restore`. No restore logic is added here
- The saas-envs and gitops-envs folders and the AWS Secrets Manager secrets stored in the archive are **not restored**: no restore procedure exists for them.
  They are verified and listed in the report and remain available in the decrypted archive (use `decrypt_only` to inspect them)
- PVC data is not part of the backup and is not restored
- `suite_restore` settings (for example `MAS_DOMAIN`, `SLS_URL`, `BAS_URL`, and the SLS/DRO from-backup switches) keep their own defaults and environment
  variables; review [suite_restore](suite_restore.md) before a real restore. A SaaS backup is `strict_named_only`, so it holds fewer resource kinds than a
  full `suite_backup`
- `full_restore` has **not** been validated against a live OpenShift cluster. Do not rely on it for disaster recovery until it has been tested

Testing status
-------------------------------------------------------------------------------
### Tested
- `decrypt_only` was run successfully against an actual encrypted Noble8 backup produced by [saas_backup](saas_backup.md). The recap was
  `ok=14 changed=0 failed=0 skipped=3`. The encrypted archive checksum, ML-KEM decapsulation, AES-256-GCM authentication and all 114 internal
  `SHA256SUMS` entries were verified, and the decrypted archive contained 115 files.
- The integrity checks and failure behaviour are covered by unit and playbook-level tests with a mocked OpenSSL.

### Not tested
- `full_restore` against a live OpenShift cluster has **not** been tested.

License
-------------------------------------------------------------------------------
EPL-2.0
