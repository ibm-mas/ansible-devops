#!/usr/bin/env python3
"""Encrypt a packaged MAS SaaS backup archive with ML-KEM-768 and AES-256-GCM.

Runs on the Ansible controller (the same host that produced the archive). It encrypts the ``.tar.gz`` written by
``ibm.mas_devops.package_saas_backup`` into ``<archive>.tar.gz.enc`` and writes ``<archive>.tar.gz.enc.sha256`` next to it.
The original archive is not modified or deleted. Only the ML-KEM-768 public key is needed; the private key is never
used or required by this plugin.

The cryptography lives in ``module_utils/saas_backup_encryption.py``, which also provides decryption for the
future restore workflow. Requires the ``cryptography`` Python package and OpenSSL 3.5+ with ML-KEM-768 on the controller.
"""

import os

from ansible.errors import AnsibleError
from ansible.plugins.action import ActionBase

from ansible_collections.ibm.mas_devops.plugins.module_utils.saas_backup_encryption import (
    SaasBackupEncryptionError,
    encryptArchive,
)

ENCRYPTED_SUFFIX = ".tar.gz.enc"


class ActionModule(ActionBase):
    """Encrypt a SaaS backup archive with a persistent ML-KEM-768 public key.

    Usage Example
    -------------
    tasks:
      - name: Encrypt backup
        ibm.mas_devops.encrypt_saas_backup:
          archive_path: /out/saas-backup-aws-dev-us-east-2-fvtsaas-20260101T000000Z.tar.gz
          public_key_path: /etc/mas/mlkem-public.pem
          output_path: /out/saas-backup-aws-dev-us-east-2-fvtsaas-20260101T000000Z.tar.gz.enc
    """

    def run(self, tmp=None, task_vars=None):
        super(ActionModule, self).run(tmp, task_vars)

        archivePath = self._task.args.get("archive_path")
        publicKeyPath = self._task.args.get("public_key_path")
        outputPath = self._task.args.get("output_path")

        if not archivePath or not os.path.isfile(archivePath):
            raise AnsibleError(f"archive_path '{archivePath}' must be an existing file")
        if not publicKeyPath:
            raise AnsibleError("public_key_path must be provided (SAAS_BACKUP_ENCRYPTION_PUBLIC_KEY_PATH)")
        if not os.path.isfile(publicKeyPath):
            raise AnsibleError(f"public_key_path '{publicKeyPath}' does not exist or is not a file")
        if not outputPath or not str(outputPath).endswith(ENCRYPTED_SUFFIX):
            raise AnsibleError(f"output_path must be provided and end with {ENCRYPTED_SUFFIX}")

        try:
            result = encryptArchive(archivePath, publicKeyPath, outputPath)
        except SaasBackupEncryptionError as e:
            raise AnsibleError(f"Backup encryption failed: {e}")

        return dict(
            changed=True,
            failed=False,
            msg=f"Encrypted {archivePath} to {result['path']}",
            encrypted_archive_path=result["path"],
            encrypted_archive_size=result["size"],
            encrypted_archive_sha256=result["sha256"],
            encrypted_archive_checksum_file=result["checksum_file"],
            encryption_algorithm=result["cipher"],
            key_encapsulation_algorithm=result["kem"],
            key_derivation_algorithm=result["kdf"],
        )
