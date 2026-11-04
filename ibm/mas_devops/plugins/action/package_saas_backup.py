#!/usr/bin/env python3
"""Package a collected MAS SaaS backup into one tar.gz with metadata.json and SHA256SUMS.

The staging directory is walked once, every regular file is hashed, and then:

* ``metadata.json`` is written into the staging directory. It carries the caller supplied
  metadata plus the list of every collected file (path, size, sha256).
* ``SHA256SUMS`` is written into the staging directory. It covers every file in the
  package including ``metadata.json``. It cannot list itself.
* The staging directory is written to a single ``.tar.gz`` whose top level directory is the
  staging directory name.
* The archive is read back and every member is compared with the checksums so that the
  metadata and checksums are proven to describe the final packaged contents.
* ``<archive>.sha256`` is written next to the archive (outside of it) so the archive itself can
  be verified without checksumming a file from inside itself.

Nothing is printed from file contents. Symlinks are rejected so that the archive can never
pull in files from outside of the staging directory.
"""

import hashlib
import json
import os
import tarfile

from ansible.errors import AnsibleError
from ansible.plugins.action import ActionBase

METADATA_FILE = "metadata.json"
CHECKSUM_FILE = "SHA256SUMS"
DIR_MODE = 0o700
FILE_MODE = 0o600
CHUNK_SIZE = 1024 * 1024
PRIVATE_KEY_MARKER = b"PRIVATE KEY-----"


def sha256Stream(stream, detectPrivateKey: bool = False):
    """Calculate the SHA-256 digest of a binary stream.

    Args:
        stream (BinaryIO): Readable binary stream.
        detectPrivateKey (bool, optional): Also detect a plaintext PEM private key marker. Defaults to False.

    Returns:
        str: Hex digest of the stream contents when detectPrivateKey is False.
        tuple: (hex digest, bool marker found) when detectPrivateKey is True.
    """
    digest = hashlib.sha256()
    found = False
    tail = b""
    for chunk in iter(lambda: stream.read(CHUNK_SIZE), b""):
        digest.update(chunk)
        if detectPrivateKey and not found:
            found = PRIVATE_KEY_MARKER in tail + chunk
            tail = chunk[-len(PRIVATE_KEY_MARKER) :]
    return (digest.hexdigest(), found) if detectPrivateKey else digest.hexdigest()


def sha256File(path: str) -> str:
    """Calculate the SHA-256 digest of a file.

    Args:
        path (str): Path of the file.

    Returns:
        str: Hex digest of the file contents.
    """
    with open(path, "rb") as f:
        return sha256Stream(f)


def collectFiles(root: str) -> list:
    """List every regular file below a directory with its size and SHA-256.

    Args:
        root (str): Directory to walk.

    Returns:
        list: Sorted list of dicts with ``path`` (posix, relative to root), ``size``, ``sha256`` and
            ``plaintext_private_key`` (True when a PEM private key marker is present; zip contents are not inspected).

    Raises:
        AnsibleError: If a symlink or a non-regular file is found.
    """
    entries = []
    for current, dirNames, fileNames in os.walk(root, followlinks=False):
        for name in dirNames + fileNames:
            full = os.path.join(current, name)
            if os.path.islink(full):
                raise AnsibleError(f"Refusing to package symlink '{os.path.relpath(full, root)}': symlinks could pull in files from outside the backup")
        for name in fileNames:
            full = os.path.join(current, name)
            if not os.path.isfile(full):
                raise AnsibleError(f"Refusing to package non-regular file '{os.path.relpath(full, root)}'")
            with open(full, "rb") as f:
                digest, hasKey = sha256Stream(f, detectPrivateKey=True)
            entries.append(
                {
                    "path": os.path.relpath(full, root).replace(os.sep, "/"),
                    "size": os.path.getsize(full),
                    "sha256": digest,
                    "plaintext_private_key": hasKey,
                }
            )
    return sorted(entries, key=lambda e: e["path"])


def restrictPermissions(root: str) -> None:
    """Make every directory owner-only (0700) and every file owner read/write (0600).

    Args:
        root (str): Directory to restrict.
    """
    os.chmod(root, DIR_MODE)
    for current, dirNames, fileNames in os.walk(root, followlinks=False):
        for name in dirNames:
            os.chmod(os.path.join(current, name), DIR_MODE)
        for name in fileNames:
            os.chmod(os.path.join(current, name), FILE_MODE)


def writePrivateFile(path: str, content: str) -> None:
    """Write a text file with owner-only permissions, failing if it already exists.

    Args:
        path (str): File to create.
        content (str): Text content.
    """
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, FILE_MODE)
    with os.fdopen(fd, "w") as f:
        f.write(content)


def normalizeTarInfo(info: tarfile.TarInfo) -> tarfile.TarInfo:
    """Remove local user and group identity from an archive member.

    Args:
        info (tarfile.TarInfo): Member being added.

    Returns:
        tarfile.TarInfo: The same member with ownership cleared.
    """
    info.uid = info.gid = 0
    info.uname = info.gname = ""
    return info


def buildArchive(root: str, archivePath: str) -> None:
    """Write the directory to a new owner-only tar.gz whose top level entry is the directory name.

    Args:
        root (str): Directory to archive.
        archivePath (str): Archive file to create. Must not exist.
    """
    fd = os.open(archivePath, os.O_WRONLY | os.O_CREAT | os.O_EXCL, FILE_MODE)
    with os.fdopen(fd, "wb") as raw:
        with tarfile.open(fileobj=raw, mode="w:gz") as tar:
            tar.add(root, arcname=os.path.basename(root), filter=normalizeTarInfo)


def verifyArchive(archivePath: str, topName: str, expected: dict) -> None:
    """Read the archive back and compare every member with the expected checksums.

    Args:
        archivePath (str): Archive to verify.
        topName (str): Expected top level directory name inside the archive.
        expected (dict): Mapping of relative file path to SHA-256 for every file that must be present,
            excluding the SHA256SUMS file itself which is only required to exist.

    Raises:
        AnsibleError: If a member is missing, unexpected, or has different contents.
    """
    seen = set()
    with tarfile.open(archivePath, mode="r:gz") as tar:
        for member in tar:
            if member.isdir():
                continue
            if not member.isreg():
                raise AnsibleError(f"Archive verification failed: unexpected non-regular member '{member.name}'")
            prefix = topName + "/"
            if not member.name.startswith(prefix):
                raise AnsibleError(f"Archive verification failed: member '{member.name}' is outside '{topName}/'")
            relPath = member.name[len(prefix) :]
            seen.add(relPath)
            if relPath == CHECKSUM_FILE:
                continue
            if relPath not in expected:
                raise AnsibleError(f"Archive verification failed: '{relPath}' is not covered by {CHECKSUM_FILE}")
            if sha256Stream(tar.extractfile(member)) != expected[relPath]:
                raise AnsibleError(f"Archive verification failed: checksum mismatch for '{relPath}'")
    missing = (set(expected) | {CHECKSUM_FILE}) - seen
    if missing:
        raise AnsibleError(f"Archive verification failed: missing from archive: {sorted(missing)}")


class ActionModule(ActionBase):
    """Package a staging directory into one tar.gz with metadata.json and SHA256SUMS.

    Usage Example
    -------------
    tasks:
      - name: Package backup
        ibm.mas_devops.package_saas_backup:
          staging_dir: /out/.work/saas-backup-aws-dev-us-east-2-fvtsaas-20260101T000000Z
          archive_path: /out/saas-backup-aws-dev-us-east-2-fvtsaas-20260101T000000Z.tar.gz
          metadata: {region: us-east-2, cluster: fvtsaas, instances: [fvtsaas]}
    """

    def run(self, tmp=None, task_vars=None):
        super(ActionModule, self).run(tmp, task_vars)

        stagingDir = self._task.args.get("staging_dir")
        archivePath = self._task.args.get("archive_path")
        metadata = self._task.args.get("metadata")

        if not stagingDir or not os.path.isdir(stagingDir) or os.path.islink(stagingDir):
            raise AnsibleError(f"staging_dir '{stagingDir}' must be an existing directory")
        if not archivePath or not str(archivePath).endswith(".tar.gz"):
            raise AnsibleError("archive_path must be provided and end with .tar.gz")
        if not isinstance(metadata, dict):
            raise AnsibleError("metadata must be provided as a dictionary")

        stagingDir = os.path.realpath(stagingDir)
        archivePath = os.path.abspath(archivePath)
        topName = os.path.basename(stagingDir)

        if os.path.commonpath([stagingDir, archivePath]) == stagingDir:
            raise AnsibleError("archive_path must not be inside staging_dir")
        if os.path.exists(archivePath):
            raise AnsibleError(f"Archive '{archivePath}' already exists; refusing to overwrite")
        if not os.path.isdir(os.path.dirname(archivePath)):
            raise AnsibleError(f"Directory for archive_path '{os.path.dirname(archivePath)}' does not exist")
        for reserved in (METADATA_FILE, CHECKSUM_FILE):
            if os.path.lexists(os.path.join(stagingDir, reserved)):
                raise AnsibleError(f"staging_dir already contains reserved file '{reserved}'")

        try:
            entries = collectFiles(stagingDir)
            if not entries:
                raise AnsibleError("staging_dir contains no files; nothing to package")

            fullMetadata = dict(metadata)
            fullMetadata["package"] = {
                "archive_top_level_directory": topName,
                "checksum_algorithm": "sha256",
                "checksums_file": CHECKSUM_FILE,
                "checksums_note": (
                    f"{CHECKSUM_FILE} covers every file below, plus {METADATA_FILE}; it does not list itself. "
                    "The archive checksum is in the sidecar <archive>.sha256"
                ),
                "file_count": len(entries),
                "plaintext_private_key_files": [e["path"] for e in entries if e["plaintext_private_key"]],
                "files": entries,
            }
            metadataPath = os.path.join(stagingDir, METADATA_FILE)
            writePrivateFile(metadataPath, json.dumps(fullMetadata, indent=2, default=str) + "\n")

            checksums = {e["path"]: e["sha256"] for e in entries}
            checksums[METADATA_FILE] = sha256File(metadataPath)
            writePrivateFile(
                os.path.join(stagingDir, CHECKSUM_FILE),
                "".join(f"{digest}  {path}\n" for path, digest in sorted(checksums.items())),
            )

            restrictPermissions(stagingDir)
            buildArchive(stagingDir, archivePath)
            verifyArchive(archivePath, topName, checksums)

            archiveSha256 = sha256File(archivePath)
            writePrivateFile(archivePath + ".sha256", f"{archiveSha256}  {os.path.basename(archivePath)}\n")
        except OSError as e:
            raise AnsibleError(f"Failed to package backup: {type(e).__name__}: {e.strerror or e}")

        return dict(
            changed=True,
            failed=False,
            msg=f"Packaged {len(entries) + 2} files into {archivePath}",
            archive_path=archivePath,
            archive_sha256=archiveSha256,
            archive_checksum_file=archivePath + ".sha256",
            archive_size=os.path.getsize(archivePath),
            archive_top_level_directory=topName,
            file_count=len(entries) + 2,
        )
