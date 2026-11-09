#!/usr/bin/env python3
"""Decrypt, verify and optionally unpack an encrypted MAS SaaS backup (``.tar.gz.enc``).

Runs on the Ansible controller. It is the counterpart of ``ibm.mas_devops.encrypt_saas_backup`` and performs, in order:

1. Verification of the encrypted file against its ``<archive>.sha256`` sidecar.
2. Decryption with ``decryptArchive`` from ``module_utils/saas_backup_encryption.py`` (ML-KEM-768 decapsulation, HKDF-SHA256,
   AES-256-GCM). That function strictly validates the header, authenticates header and payload and never overwrites a file.
3. Inspection of the decrypted ``.tar.gz``: only regular files and directories below one top level directory are accepted,
   every member is hashed and compared with the archive's ``SHA256SUMS`` manifest, and ``metadata.json`` is cross-checked
   against the manifest.
4. Only when ``extract`` is true and everything above succeeded: extraction of the validated archive.

All plaintext is written below a private (0700) work directory. Without ``extract`` the work directory is removed (files are
zero-filled first) before the plugin returns. With ``extract`` it is returned in ``work_dir`` and must be removed by calling the
plugin again with ``state: absent``. On any failure the work directory is removed immediately. The encrypted archive, its
sidecar and the private key are never modified, copied or deleted, and no key material is ever returned or logged.
"""

import gzip
import hashlib
import json
import os
import re
import stat
import tarfile
import tempfile
import zlib
from typing import Any, Dict, List, Optional

from ansible.errors import AnsibleError
from ansible.module_utils.parsing.convert_bool import boolean
from ansible.plugins.action import ActionBase

from ansible_collections.ibm.mas_devops.plugins.module_utils.saas_backup_encryption import (
    CHUNK_SIZE,
    DIR_MODE,
    FILE_MODE,
    SaasBackupEncryptionError,
    decryptArchive,
    removeSecureTempDir,
    sha256File,
)

ENCRYPTED_SUFFIX = ".tar.gz.enc"
WORK_PREFIX = "saas-restore-"
EXTRACT_DIR = "extracted"
MANIFEST_FILE = "SHA256SUMS"
METADATA_FILE = "metadata.json"
MAX_MEMBERS = 500000
MAX_SMALL_FILE_SIZE = 64 * 1024 * 1024
SIDECAR_MAX_SIZE = 4096
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
SIDECAR_PATTERN = re.compile(r"^([0-9a-fA-F]{64})(\s+\*?\S.*)?$")
MANIFEST_LINE_PATTERN = re.compile(r"^([0-9a-f]{64})  (.+)$")
TIMESTAMP_PATTERN = re.compile(r"^\d{8}T\d{6}Z$")
NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
INSTANCE_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9-]*$")


class RestoreValidationError(Exception):
    """Base class for validation failures raised by this plugin."""


class ChecksumError(RestoreValidationError):
    """The encrypted archive checksum sidecar is missing, malformed or does not match."""


class ArchiveContentError(RestoreValidationError):
    """The decrypted archive is not a valid, internally consistent SaaS backup."""


def readSidecarDigest(encryptedPath: str) -> str:
    """Read the expected SHA-256 digest from ``<encryptedPath>.sha256``.

    Args:
        encryptedPath (str): Encrypted archive path.

    Returns:
        str: Lower case hex digest.

    Raises:
        ChecksumError: If the sidecar is missing, not a regular file, too large or malformed.
    """
    sidecar = encryptedPath + ".sha256"
    if not os.path.isfile(sidecar):
        raise ChecksumError(f"Checksum sidecar '{sidecar}' is missing; refusing to decrypt an archive that cannot be verified")
    if os.path.getsize(sidecar) > SIDECAR_MAX_SIZE:
        raise ChecksumError(f"Checksum sidecar '{sidecar}' is unexpectedly large")
    with open(sidecar, "r", encoding="utf-8", errors="replace") as f:
        lines = f.read().strip().splitlines()
    match = SIDECAR_PATTERN.match(lines[0]) if len(lines) == 1 else None
    if not match:
        raise ChecksumError(f"Checksum sidecar '{sidecar}' is malformed; expected one 'sha256sum' line")
    return match.group(1).lower()


def verifyEncryptedChecksum(encryptedPath: str) -> str:
    """Verify the encrypted archive against its checksum sidecar.

    Args:
        encryptedPath (str): Encrypted archive path.

    Returns:
        str: The verified SHA-256 digest of the encrypted archive.

    Raises:
        ChecksumError: If the sidecar is invalid or the digest does not match.
    """
    expected = readSidecarDigest(encryptedPath)
    actual = sha256File(encryptedPath)
    if actual != expected:
        raise ChecksumError(f"Encrypted archive checksum mismatch: sidecar says {expected}, the file is {actual}. The archive is corrupted or was modified")
    return actual


def splitMemberName(name: str) -> List[str]:
    """Split a tar member name into safe path components.

    Args:
        name (str): Member name from the archive.

    Returns:
        list: Path components.

    Raises:
        ArchiveContentError: If the name is absolute, empty, contains backslashes, NUL, ``.`` or ``..`` components.
    """
    if not name or name.startswith("/") or "\\" in name or "\0" in name:
        raise ArchiveContentError(f"Unsafe archive member name {name!r}")
    parts = name.rstrip("/").split("/")
    if any(part in ("", ".", "..") for part in parts):
        raise ArchiveContentError(f"Unsafe archive member name {name!r}")
    return parts


def inspectArchive(archivePath: str) -> Dict[str, Any]:
    """Hash every member of the decrypted archive and check its structure.

    Only directories and regular files below exactly one top level directory are accepted. Symlinks, hard links, devices,
    absolute paths, ``..`` components and duplicate members are rejected.

    Args:
        archivePath (str): Decrypted ``.tar.gz``.

    Returns:
        dict: ``top`` (top level directory), ``hashes`` (relative path to SHA-256), ``manifest`` and ``metadata`` (raw bytes).

    Raises:
        ArchiveContentError: If the archive is not a gzip compressed tar file or has an unsafe or unexpected structure.
    """
    top: Optional[str] = None
    hashes: Dict[str, str] = {}
    small: Dict[str, bytes] = {}
    try:
        with tarfile.open(archivePath, mode="r:gz") as tar:
            for count, member in enumerate(tar, start=1):
                if count > MAX_MEMBERS:
                    raise ArchiveContentError(f"The archive has more than {MAX_MEMBERS} members")
                parts = splitMemberName(member.name)
                if top is None:
                    top = parts[0]
                elif parts[0] != top:
                    raise ArchiveContentError(f"The archive has more than one top level entry ('{top}' and '{parts[0]}')")
                if member.isdir():
                    continue
                if not member.isreg():
                    raise ArchiveContentError(f"Unexpected non-regular archive member {member.name!r}")
                if len(parts) == 1:
                    raise ArchiveContentError(f"Unexpected file {member.name!r} at the top level of the archive")
                relPath = "/".join(parts[1:])
                if relPath in hashes:
                    raise ArchiveContentError(f"Duplicate archive member '{relPath}'")
                keep = relPath in (MANIFEST_FILE, METADATA_FILE)
                if keep and member.size > MAX_SMALL_FILE_SIZE:
                    raise ArchiveContentError(f"'{relPath}' is unexpectedly large")
                digest = hashlib.sha256()
                data = bytearray()
                stream = tar.extractfile(member)
                for chunk in iter(lambda: stream.read(CHUNK_SIZE), b""):
                    digest.update(chunk)
                    if keep:
                        data.extend(chunk)
                hashes[relPath] = digest.hexdigest()
                if keep:
                    small[relPath] = bytes(data)
    except (tarfile.TarError, EOFError, zlib.error, gzip.BadGzipFile) as e:
        raise ArchiveContentError(f"The decrypted data is not a valid .tar.gz archive ({type(e).__name__})")
    if top is None or not hashes:
        raise ArchiveContentError("The decrypted archive is empty")
    for required in (MANIFEST_FILE, METADATA_FILE):
        if required not in small:
            raise ArchiveContentError(f"The archive does not contain {required}")
    return {"top": top, "hashes": hashes, "manifest": small[MANIFEST_FILE], "metadata": small[METADATA_FILE]}


def parseManifest(raw: bytes) -> Dict[str, str]:
    """Parse the ``SHA256SUMS`` manifest strictly.

    Args:
        raw (bytes): Manifest content.

    Returns:
        dict: Relative path to SHA-256.

    Raises:
        ArchiveContentError: If a line is malformed, a path is unsafe or duplicated, or the manifest is empty.
    """
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise ArchiveContentError(f"{MANIFEST_FILE} is not valid UTF-8")
    manifest: Dict[str, str] = {}
    for line in text.splitlines():
        match = MANIFEST_LINE_PATTERN.match(line)
        if not match:
            raise ArchiveContentError(f"{MANIFEST_FILE} contains a malformed line")
        digest, path = match.groups()
        splitMemberName(path)
        if path == MANIFEST_FILE or path in manifest:
            raise ArchiveContentError(f"{MANIFEST_FILE} lists '{path}' more than once or lists itself")
        manifest[path] = digest
    if not manifest:
        raise ArchiveContentError(f"{MANIFEST_FILE} is empty")
    return manifest


def verifyManifest(manifest: Dict[str, str], hashes: Dict[str, str]) -> None:
    """Compare the manifest with the hashes of the archive members.

    Args:
        manifest (dict): Parsed ``SHA256SUMS``.
        hashes (dict): Actual SHA-256 of every archive file.

    Raises:
        ArchiveContentError: If a listed file is missing or differs, or the archive has files the manifest does not cover.
    """
    missing = sorted(set(manifest) - set(hashes))
    if missing:
        raise ArchiveContentError(f"Files listed in {MANIFEST_FILE} are missing from the archive: {missing[:10]}")
    unlisted = sorted(set(hashes) - set(manifest) - {MANIFEST_FILE})
    if unlisted:
        raise ArchiveContentError(f"Archive files are not covered by {MANIFEST_FILE}: {unlisted[:10]}")
    mismatched = sorted(path for path, digest in manifest.items() if hashes[path] != digest)
    if mismatched:
        raise ArchiveContentError(f"Checksum mismatch against {MANIFEST_FILE} for: {mismatched[:10]}")
    if METADATA_FILE not in manifest:
        raise ArchiveContentError(f"{METADATA_FILE} is not covered by {MANIFEST_FILE}")


def requireString(container: Dict[str, Any], key: str, pattern: "re.Pattern[str]", label: str) -> str:
    """Return a string field after validating it against a pattern.

    Args:
        container (dict): Dictionary holding the field.
        key (str): Field name.
        pattern (re.Pattern): Accepted format.
        label (str): Description used in messages.

    Returns:
        str: The validated value.

    Raises:
        ArchiveContentError: If the field is missing, not a string or has an unexpected format.
    """
    value = container.get(key)
    if not isinstance(value, str) or not pattern.match(value):
        raise ArchiveContentError(f"{METADATA_FILE}: {label} is missing or invalid")
    return value


def summarizeMetadata(rawMetadata: bytes, top: str, manifest: Dict[str, str], hashes: Dict[str, str]) -> Dict[str, Any]:
    """Validate ``metadata.json`` against the archive and build a summary for reporting and restoration.

    Args:
        rawMetadata (bytes): Content of ``metadata.json``.
        top (str): Top level directory of the archive.
        manifest (dict): Verified manifest.
        hashes (dict): Actual SHA-256 of every archive file.

    Returns:
        dict: Backup type, timestamp, account, region, cluster, API server, instances, per instance details, repositories,
            scope and warnings.

    Raises:
        ArchiveContentError: If the metadata is malformed or inconsistent with the archive.
    """
    try:
        metadata = json.loads(rawMetadata.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        raise ArchiveContentError(f"{METADATA_FILE} is not valid JSON")
    if not isinstance(metadata, dict):
        raise ArchiveContentError(f"{METADATA_FILE} is not a JSON object")

    createdUtc = requireString(metadata, "created_utc", TIMESTAMP_PATTERN, "created_utc")
    cluster = requireString(metadata, "cluster", NAME_PATTERN, "cluster")
    instances = metadata.get("instances")
    if not isinstance(instances, list) or not instances or not all(isinstance(i, str) and INSTANCE_PATTERN.match(i) for i in instances):
        raise ArchiveContentError(f"{METADATA_FILE}: instances is missing or invalid")
    if len(set(instances)) != len(instances):
        raise ArchiveContentError(f"{METADATA_FILE}: instances contains duplicates")

    package = metadata.get("package")
    if not isinstance(package, dict) or package.get("archive_top_level_directory") != top:
        raise ArchiveContentError(f"{METADATA_FILE} does not describe this archive (top level directory differs)")
    files = package.get("files")
    if not isinstance(files, list) or not all(isinstance(f, dict) for f in files):
        raise ArchiveContentError(f"{METADATA_FILE}: package.files is missing or invalid")
    described = {f.get("path"): f.get("sha256") for f in files}
    expected = {path: digest for path, digest in manifest.items() if path != METADATA_FILE}
    if described != expected:
        raise ArchiveContentError(f"{METADATA_FILE} package.files does not match {MANIFEST_FILE}")

    details = []
    for entry in metadata.get("instance_details") or []:
        instanceId = entry.get("instance_id") if isinstance(entry, dict) else None
        if instanceId not in instances:
            raise ArchiveContentError(f"{METADATA_FILE}: instance_details references an unknown instance")
        openshift = entry.get("openshift") if isinstance(entry.get("openshift"), dict) else {}
        paths = {}
        for app, suffix in (("suite", "suite"), ("manage", "app-manage")):
            section = openshift.get(app)
            if section is None:
                continue
            backupPath = section.get("backup_path") if isinstance(section, dict) else None
            if backupPath != f"openshift/{instanceId}/backup-{createdUtc}-{suffix}":
                raise ArchiveContentError(f"{METADATA_FILE}: unexpected {app} backup path for instance '{instanceId}'")
            if not any(path.startswith(backupPath + "/resources/") for path in hashes):
                raise ArchiveContentError(f"The archive contains no {app} resources for instance '{instanceId}'")
            paths[app] = backupPath
        if "suite" not in paths:
            raise ArchiveContentError(f"{METADATA_FILE}: instance '{instanceId}' has no Suite backup")
        details.append(
            {
                "instance_id": instanceId,
                "workspace_id": entry.get("workspace_id"),
                "applications_backed_up": list(entry.get("applications_backed_up") or []),
                "suite_backup_path": paths["suite"],
                "manage_backup_path": paths.get("manage"),
                "versions": entry.get("versions") or {},
            }
        )
    if sorted(d["instance_id"] for d in details) != sorted(instances):
        raise ArchiveContentError(f"{METADATA_FILE}: instance_details does not cover every instance")

    return {
        "backup_type": metadata.get("backup_type"),
        "created_utc": createdUtc,
        "account": metadata.get("account"),
        "region": metadata.get("region"),
        "cluster": cluster,
        "cluster_api_server": metadata.get("cluster_api_server"),
        "instances": instances,
        "instance_details": details,
        "repositories": metadata.get("repositories") or {},
        "scope": metadata.get("scope") or {},
        "warnings": metadata.get("warnings") or [],
    }


def summarizeContents(top: str, hashes: Dict[str, str]) -> Dict[str, Any]:
    """Count the archive files per top level section (saas-envs, gitops-envs, openshift, ...).

    Args:
        top (str): Top level directory of the archive.
        hashes (dict): Relative path to SHA-256 for every archive file.

    Returns:
        dict: Top level directory, file count and files per section.
    """
    sections: Dict[str, int] = {}
    for path in hashes:
        section = path.split("/")[0] if "/" in path else "(root)"
        sections[section] = sections.get(section, 0) + 1
    return {"top_level_directory": top, "file_count": len(hashes), "files_by_section": dict(sorted(sections.items()))}


def extractArchive(archivePath: str, destination: str, top: str) -> str:
    """Extract a validated archive, creating only directories (0700) and regular files (0600), never overwriting.

    Args:
        archivePath (str): Validated decrypted ``.tar.gz``.
        destination (str): Directory to create inside the private work directory. Must not exist.
        top (str): Top level directory of the archive.

    Returns:
        str: Path of the extracted top level directory.

    Raises:
        ArchiveContentError: If a member would be written outside the destination.
    """
    os.mkdir(destination, DIR_MODE)
    root = os.path.realpath(destination)
    with tarfile.open(archivePath, mode="r:gz") as tar:
        for member in tar:
            target = os.path.join(root, *splitMemberName(member.name))
            if os.path.commonpath([root, os.path.realpath(target)]) != root:
                raise ArchiveContentError(f"Archive member {member.name!r} would be extracted outside the work directory")
            if member.isdir():
                os.makedirs(target, exist_ok=True)
                os.chmod(target, DIR_MODE)
                continue
            parent = os.path.dirname(target)
            if not os.path.isdir(parent):
                os.makedirs(parent)
                os.chmod(parent, DIR_MODE)
            fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, FILE_MODE)
            with os.fdopen(fd, "wb") as dst:
                stream = tar.extractfile(member)
                for chunk in iter(lambda: stream.read(CHUNK_SIZE), b""):
                    dst.write(chunk)
    return os.path.join(root, top)


def createWorkDir(parentDir: Optional[str]) -> str:
    """Create the private (0700) work directory that receives all plaintext.

    Args:
        parentDir (str, optional): Existing directory that will contain the work directory. None uses the system temporary directory.

    Returns:
        str: Path of the new directory.
    """
    path = tempfile.mkdtemp(prefix=WORK_PREFIX, dir=parentDir or None)
    os.chmod(path, DIR_MODE)
    return path


def decryptAndVerify(encryptedPath: str, privateKeyPath: str, parentDir: Optional[str], extract: bool) -> Dict[str, Any]:
    """Verify, decrypt and validate an encrypted backup and optionally extract it.

    Args:
        encryptedPath (str): Encrypted archive (``.tar.gz.enc``) with its ``.sha256`` sidecar next to it.
        privateKeyPath (str): ML-KEM-768 private key (PEM).
        parentDir (str, optional): Existing absolute directory that will contain the private work directory.
        extract (bool): Extract the validated archive and keep the work directory.

    Returns:
        dict: Verification results, backup summary, ``work_dir`` and ``extract_root`` (empty unless extract is true).

    Raises:
        RestoreValidationError: If a checksum or content validation fails.
        SaasBackupEncryptionError: If decryption or authentication fails.
        OSError: For other I/O errors.
    """
    encryptedSha256 = verifyEncryptedChecksum(encryptedPath)
    workDir = createWorkDir(parentDir)
    keepWorkDir = False
    try:
        decryptedPath = os.path.join(workDir, os.path.basename(encryptedPath)[: -len(".enc")])
        decrypted = decryptArchive(encryptedPath, privateKeyPath, decryptedPath)
        inspection = inspectArchive(decryptedPath)
        manifest = parseManifest(inspection["manifest"])
        verifyManifest(manifest, inspection["hashes"])
        summary = summarizeMetadata(inspection["metadata"], inspection["top"], manifest, inspection["hashes"])
        extractRoot = ""
        if extract:
            extractRoot = extractArchive(decryptedPath, os.path.join(workDir, EXTRACT_DIR), inspection["top"])
            keepWorkDir = True
        return {
            "encrypted_archive_sha256": encryptedSha256,
            "decrypted_archive_size": decrypted["size"],
            "decrypted_archive_sha256": decrypted["sha256"],
            "manifest_file_count": len(manifest),
            "backup_metadata": summary,
            "contents": summarizeContents(inspection["top"], inspection["hashes"]),
            "work_dir": workDir if keepWorkDir else "",
            "extract_root": extractRoot,
        }
    finally:
        if not keepWorkDir:
            removeSecureTempDir(workDir)


def removeWorkDir(workDir: Optional[str]) -> Dict[str, Any]:
    """Securely remove a work directory created by this plugin.

    Only an absolute, non-symlink directory owned by the current user, named ``saas-restore-*`` and not accessible to
    group or others is removed, so the plugin cannot be pointed at arbitrary paths.

    Args:
        workDir (str, optional): Work directory returned by a previous run.

    Returns:
        dict: Ansible result with ``changed`` set when a directory was removed.

    Raises:
        AnsibleError: If the path is not a work directory created by this plugin or cannot be removed completely.
    """
    if not workDir or not os.path.isabs(workDir):
        raise AnsibleError("work_dir must be the absolute path returned by a previous decrypt_saas_backup run")
    if not os.path.lexists(workDir):
        return dict(changed=False, failed=False, msg=f"Work directory '{workDir}' is already absent")
    info = os.lstat(workDir)
    if not stat.S_ISDIR(info.st_mode) or not os.path.basename(workDir).startswith(WORK_PREFIX):
        raise AnsibleError(f"Refusing to remove '{workDir}': it is not a {WORK_PREFIX}* work directory")
    if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) & 0o077:
        raise AnsibleError(f"Refusing to remove '{workDir}': it is not private to the current user")
    removeSecureTempDir(workDir)
    if os.path.lexists(workDir):
        raise AnsibleError(f"Work directory '{workDir}' could not be removed completely")
    return dict(changed=True, failed=False, msg=f"Removed work directory '{workDir}'")


class ActionModule(ActionBase):
    """Decrypt and verify an encrypted SaaS backup, optionally unpacking it for restoration.

    Usage Example
    -------------
    tasks:
      - name: Decrypt, verify and inspect
        ibm.mas_devops.decrypt_saas_backup:
          encrypted_archive_path: /out/saas-backup-aws-dev-us-east-2-fvtsaas-20260101T000000Z.tar.gz.enc
          private_key_path: /secure/mlkem-private.pem
          extract: false

      - name: Remove the extracted plaintext
        ibm.mas_devops.decrypt_saas_backup:
          state: absent
          work_dir: "{{ result.work_dir }}"
    """

    def run(self, tmp=None, task_vars=None):
        super(ActionModule, self).run(tmp, task_vars)
        args = self._task.args
        state = args.get("state", "present")

        if state == "absent":
            return removeWorkDir(args.get("work_dir"))
        if state != "present":
            raise AnsibleError("state must be 'present' or 'absent'")

        encryptedPath = args.get("encrypted_archive_path")
        privateKeyPath = args.get("private_key_path")
        outputDir = args.get("output_dir") or None
        if not encryptedPath or not str(encryptedPath).endswith(ENCRYPTED_SUFFIX):
            raise AnsibleError(f"encrypted_archive_path must be provided and end with {ENCRYPTED_SUFFIX}")
        if not os.path.isfile(encryptedPath):
            raise AnsibleError(f"encrypted_archive_path '{encryptedPath}' does not exist or is not a file")
        if not privateKeyPath or not os.path.isfile(privateKeyPath):
            raise AnsibleError("private_key_path must be provided and be an existing file (SAAS_RESTORE_PRIVATE_KEY_PATH)")
        if outputDir is not None and (not os.path.isabs(outputDir) or not os.path.isdir(outputDir)):
            raise AnsibleError(f"output_dir '{outputDir}' must be an existing absolute directory")
        extract = boolean(args.get("extract", False))

        try:
            result = decryptAndVerify(os.path.abspath(encryptedPath), privateKeyPath, outputDir, extract)
        except (SaasBackupEncryptionError, RestoreValidationError) as e:
            raise AnsibleError(f"Backup decryption failed: {e}")
        except OSError as e:
            raise AnsibleError(f"Backup decryption failed: {type(e).__name__}: {e.strerror or e}")

        return dict(
            changed=extract,
            failed=False,
            msg=f"Decrypted and verified {encryptedPath}",
            integrity_verified=True,
            authentication_verified=True,
            **result,
        )
