#!/usr/bin/env python3
"""Post-quantum encryption of SaaS backup archives (ML-KEM-768 + HKDF-SHA256 + AES-256-GCM).

Encrypted file format (``.tar.gz.enc``)::

    MAGIC (8 bytes, ``SAASPQC1``)
    header length (4 bytes, big endian)
    header (canonical JSON: version, kem, kdf, cipher, salt, nonce, kem_ciphertext)
    AES-256-GCM ciphertext (same length as the plaintext archive)
    GCM authentication tag (16 bytes)

The ML-KEM-768 encapsulation is performed by the OpenSSL command line (``openssl pkeyutl -encap`` / ``-decap``), the
shared secret is expanded with HKDF-SHA256 and the archive is encrypted in 1 MiB chunks with AES-256-GCM. The exact
header bytes are authenticated as AES-GCM additional authenticated data, so any change to the header or to the payload
fails authentication. Decrypted data is written to a private temporary file and only published once authentication
has succeeded. Existing files are never overwritten.

Only the public key is needed to encrypt. The private key is only used by decryptArchive.
"""

import base64
import binascii
import hashlib
import json
import os
import re
import secrets
import shutil
import struct
import subprocess
import tempfile
from typing import Any, BinaryIO, Dict, List, Optional, Tuple

try:
    from cryptography.exceptions import InvalidTag
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF

    CRYPTOGRAPHY_IMPORT_ERROR: Optional[BaseException] = None
except ImportError as importError:  # pragma: no cover - exercised by patching CRYPTOGRAPHY_IMPORT_ERROR in tests
    CRYPTOGRAPHY_IMPORT_ERROR = importError

    class InvalidTag(Exception):  # type: ignore[no-redef]
        """Placeholder used only when the cryptography package is missing."""


MAGIC = b"SAASPQC1"
FORMAT_VERSION = 1
KEM_ALGORITHM = "ML-KEM-768"
KDF_ALGORITHM = "HKDF-SHA256"
CIPHER_ALGORITHM = "AES-256-GCM"
HKDF_INFO = b"saas-backup-encryption-v1"
SALT_SIZE = 16
NONCE_SIZE = 12
TAG_SIZE = 16
KEY_SIZE = 32
SHARED_SECRET_SIZE = 32
KEM_CIPHERTEXT_SIZE = 1088
LENGTH_PREFIX_SIZE = 4
MAX_HEADER_SIZE = 16 * 1024
MAX_KEY_FILE_SIZE = 64 * 1024
CHUNK_SIZE = 1024 * 1024
DIR_MODE = 0o700
FILE_MODE = 0o600
OPENSSL_TIMEOUT_SECONDS = 120
DEFAULT_OPENSSL = "openssl"
HEADER_FIELDS = frozenset({"version", "kem", "kdf", "cipher", "salt", "nonce", "kem_ciphertext"})
MLKEM768_PATTERN = re.compile(r"(?<![A-Za-z0-9])(ML-KEM-768|MLKEM768)(?![A-Za-z0-9])")


class SaasBackupEncryptionError(Exception):
    """Base class for every error raised by this module."""


class MissingDependencyError(SaasBackupEncryptionError):
    """A required Python package is not installed."""


class UnsupportedOpenSslError(SaasBackupEncryptionError):
    """OpenSSL is missing or does not support ML-KEM-768 encapsulation."""


class InvalidKeyError(SaasBackupEncryptionError):
    """A key file is missing, unreadable, of the wrong type or not an ML-KEM-768 key."""


class UnsafePathError(SaasBackupEncryptionError):
    """An input or output path is unsafe or an output would overwrite an existing file."""


class ArchiveFormatError(SaasBackupEncryptionError):
    """The encrypted file is malformed, truncated or uses an unsupported format."""


class AuthenticationError(SaasBackupEncryptionError):
    """AES-GCM authentication failed: wrong private key, or the header or payload was modified."""


def requireCryptography() -> None:
    """Fail clearly when the cryptography package is not installed.

    Raises:
        MissingDependencyError: If the cryptography package could not be imported.
    """
    if CRYPTOGRAPHY_IMPORT_ERROR is not None:
        raise MissingDependencyError(
            f"The Python package 'cryptography' (>= 42.0.0) is required for backup encryption but could not be imported "
            f"({CRYPTOGRAPHY_IMPORT_ERROR}). Install it with: pip install -r ibm/mas_devops/requirements.txt"
        )


def sha256File(path: str) -> str:
    """Calculate the SHA-256 digest of a file in 1 MiB chunks.

    Args:
        path (str): Path of the file.

    Returns:
        str: Hex digest of the file contents.
    """
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def writeSha256Sidecar(path: str) -> str:
    """Write ``<path>.sha256`` (``sha256sum`` format, mode 0600) next to a file, refusing to overwrite.

    Args:
        path (str): File to checksum.

    Returns:
        str: Hex SHA-256 digest of the file.

    Raises:
        UnsafePathError: If the sidecar file already exists.
    """
    digest = sha256File(path)
    try:
        fd = os.open(path + ".sha256", os.O_WRONLY | os.O_CREAT | os.O_EXCL, FILE_MODE)
    except FileExistsError:
        raise UnsafePathError(f"Checksum file '{path}.sha256' already exists; refusing to overwrite")
    with os.fdopen(fd, "w") as f:
        f.write(f"{digest}  {os.path.basename(path)}\n")
    return digest


def summarize(text: Optional[str]) -> str:
    """Reduce tool output to one short line for an error message.

    Args:
        text (str, optional): Raw stderr or stdout of a subprocess.

    Returns:
        str: First non-empty line, truncated to 200 characters.
    """
    for line in (text or "").splitlines():
        if line.strip():
            return line.strip()[:200]
    return "no output"


def runOpenSsl(opensslPath: str, args: List[str]) -> "subprocess.CompletedProcess[str]":
    """Run the OpenSSL command line. This is the only place the OpenSSL subprocess is started.

    Args:
        opensslPath (str): OpenSSL executable name or path.
        args (list): Arguments after the executable.

    Returns:
        subprocess.CompletedProcess: Completed process with text stdout and stderr (return code is not checked).

    Raises:
        UnsupportedOpenSslError: If OpenSSL cannot be started or times out.
    """
    try:
        return subprocess.run(
            [opensslPath] + args,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=OPENSSL_TIMEOUT_SECONDS,
            check=False,
        )
    except FileNotFoundError:
        raise UnsupportedOpenSslError(f"OpenSSL executable '{opensslPath}' was not found. OpenSSL 3.5 or later with ML-KEM-768 support is required")
    except subprocess.TimeoutExpired:
        raise UnsupportedOpenSslError(f"OpenSSL did not finish within {OPENSSL_TIMEOUT_SECONDS} seconds (is the key passphrase protected?)")


def checkMlKem768Support(opensslPath: str = DEFAULT_OPENSSL, needEncap: bool = True) -> None:
    """Verify that OpenSSL supports ML-KEM-768 and the ``pkeyutl`` encapsulation operations.

    Args:
        opensslPath (str, optional): OpenSSL executable. Defaults to "openssl".
        needEncap (bool, optional): Check ``-encap`` (True) or ``-decap`` (False) support. Defaults to True.

    Raises:
        UnsupportedOpenSslError: If OpenSSL is missing or lacks ML-KEM-768 or the encapsulation operation.
    """
    version = summarize(runOpenSsl(opensslPath, ["version"]).stdout)
    hint = f"Found '{version}'. OpenSSL 3.5 or later with ML-KEM-768 support is required for backup encryption"
    kems = runOpenSsl(opensslPath, ["list", "-kem-algorithms"])
    if kems.returncode != 0 or not MLKEM768_PATTERN.search(kems.stdout or ""):
        raise UnsupportedOpenSslError(f"OpenSSL does not provide the ML-KEM-768 algorithm. {hint}")
    operation = "-encap" if needEncap else "-decap"
    helpResult = runOpenSsl(opensslPath, ["pkeyutl", "-help"])
    if operation not in (helpResult.stdout or "") + (helpResult.stderr or ""):
        raise UnsupportedOpenSslError(f"'openssl pkeyutl' does not support {operation}. {hint}")


def readKeyFile(path: str, label: str) -> str:
    """Read a small PEM key file after checking that it is a regular file.

    Args:
        path (str): Key file path.
        label (str): "public key" or "private key", used in messages.

    Returns:
        str: File content. Never include it in a message.

    Raises:
        InvalidKeyError: If the file is missing, not a regular file, too large or unreadable.
    """
    if not path or not os.path.isfile(path):
        raise InvalidKeyError(f"The {label} file '{path}' does not exist or is not a regular file")
    if os.path.getsize(path) > MAX_KEY_FILE_SIZE:
        raise InvalidKeyError(f"The {label} file '{path}' is unexpectedly large and was rejected")
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError as e:
        raise InvalidKeyError(f"The {label} file '{path}' cannot be read: {e.strerror or e}")


def validateKeyFile(path: str, opensslPath: str, isPublic: bool) -> None:
    """Check that a file is an unencrypted ML-KEM-768 public or private key.

    Args:
        path (str): Key file path.
        opensslPath (str): OpenSSL executable.
        isPublic (bool): True for a public key, False for a private key.

    Raises:
        InvalidKeyError: If the file is missing, of the wrong type or not ML-KEM-768.
    """
    label = "public key" if isPublic else "private key"
    content = readKeyFile(path, label)
    if isPublic and "PRIVATE KEY" in content:
        raise InvalidKeyError(f"'{path}' contains a private key. Backup encryption must be given the ML-KEM-768 public key only")
    if not isPublic and "PRIVATE KEY" not in content:
        raise InvalidKeyError(f"'{path}' does not contain a PEM private key")
    args = ["pkey"] + (["-pubin"] if isPublic else []) + ["-in", path, "-noout", "-text_pub"]
    result = runOpenSsl(opensslPath, args)
    if result.returncode != 0:
        raise InvalidKeyError(f"OpenSSL could not read the {label} '{path}': {summarize(result.stderr)}")
    if not (result.stdout or "").lstrip().startswith(KEM_ALGORITHM):
        raise InvalidKeyError(f"The {label} '{path}' is not an {KEM_ALGORITHM} key")


def createSecureTempDir() -> str:
    """Create a private (0700) temporary directory.

    Returns:
        str: Path of the new directory.
    """
    path = tempfile.mkdtemp(prefix="saas-pqc-")
    os.chmod(path, DIR_MODE)
    return path


def removeSecureTempDir(path: Optional[str]) -> None:
    """Zero-fill the files in a temporary directory, then remove the directory. Never raises.

    Args:
        path (str, optional): Directory created by createSecureTempDir.
    """
    if not path:
        return
    for current, _, fileNames in os.walk(path):
        for name in fileNames:
            full = os.path.join(current, name)
            try:
                size = os.path.getsize(full)
                with open(full, "r+b") as f:
                    f.write(b"\0" * size)
                    f.flush()
                    os.fsync(f.fileno())
            except OSError:
                pass
    shutil.rmtree(path, ignore_errors=True)


def createPrivateFile(path: str) -> None:
    """Create an empty file with mode 0600, failing if it exists.

    Args:
        path (str): File to create.
    """
    os.close(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, FILE_MODE))


def encapsulate(publicKeyPath: str, workDir: str, opensslPath: str) -> Tuple[bytes, bytes]:
    """Perform ML-KEM-768 encapsulation with the public key.

    Args:
        publicKeyPath (str): ML-KEM-768 public key.
        workDir (str): Private temporary directory that receives the shared secret file.
        opensslPath (str): OpenSSL executable.

    Returns:
        tuple: (KEM ciphertext, shared secret).

    Raises:
        SaasBackupEncryptionError: If OpenSSL fails or returns unexpected sizes.
    """
    kemFile = os.path.join(workDir, "kem.bin")
    secretFile = os.path.join(workDir, "secret.bin")
    createPrivateFile(secretFile)
    result = runOpenSsl(opensslPath, ["pkeyutl", "-encap", "-pubin", "-inkey", publicKeyPath, "-out", kemFile, "-secret", secretFile])
    if result.returncode != 0:
        raise UnsupportedOpenSslError(f"ML-KEM-768 encapsulation failed: {summarize(result.stderr)}")
    with open(kemFile, "rb") as f:
        kemCiphertext = f.read()
    with open(secretFile, "rb") as f:
        sharedSecret = f.read()
    if len(kemCiphertext) != KEM_CIPHERTEXT_SIZE or len(sharedSecret) != SHARED_SECRET_SIZE:
        raise UnsupportedOpenSslError("ML-KEM-768 encapsulation returned unexpected output sizes")
    return kemCiphertext, sharedSecret


def decapsulate(privateKeyPath: str, kemCiphertext: bytes, workDir: str, opensslPath: str) -> bytes:
    """Perform ML-KEM-768 decapsulation with the private key.

    Args:
        privateKeyPath (str): ML-KEM-768 private key.
        kemCiphertext (bytes): KEM ciphertext from the encrypted file header.
        workDir (str): Private temporary directory that receives the shared secret file.
        opensslPath (str): OpenSSL executable.

    Returns:
        bytes: Shared secret.

    Raises:
        SaasBackupEncryptionError: If OpenSSL fails or returns an unexpected size.
    """
    kemFile = os.path.join(workDir, "kem.bin")
    secretFile = os.path.join(workDir, "secret.bin")
    fd = os.open(kemFile, os.O_WRONLY | os.O_CREAT | os.O_EXCL, FILE_MODE)
    with os.fdopen(fd, "wb") as f:
        f.write(kemCiphertext)
    createPrivateFile(secretFile)
    result = runOpenSsl(opensslPath, ["pkeyutl", "-decap", "-inkey", privateKeyPath, "-in", kemFile, "-secret", secretFile])
    if result.returncode != 0:
        raise InvalidKeyError(f"ML-KEM-768 decapsulation failed: {summarize(result.stderr)}")
    with open(secretFile, "rb") as f:
        sharedSecret = f.read()
    if len(sharedSecret) != SHARED_SECRET_SIZE:
        raise InvalidKeyError("ML-KEM-768 decapsulation returned an unexpected shared secret size")
    return sharedSecret


def deriveKey(sharedSecret: bytes, salt: bytes) -> bytes:
    """Derive the AES-256 key from the ML-KEM shared secret with HKDF-SHA256.

    Args:
        sharedSecret (bytes): ML-KEM-768 shared secret.
        salt (bytes): Random per-file salt.

    Returns:
        bytes: 32 byte AES key.
    """
    return HKDF(algorithm=hashes.SHA256(), length=KEY_SIZE, salt=salt, info=HKDF_INFO).derive(sharedSecret)


def buildHeader(salt: bytes, nonce: bytes, kemCiphertext: bytes) -> bytes:
    """Serialize the header deterministically (sorted keys, compact separators, UTF-8).

    Args:
        salt (bytes): HKDF salt.
        nonce (bytes): AES-GCM nonce.
        kemCiphertext (bytes): ML-KEM-768 encapsulation ciphertext.

    Returns:
        bytes: Header bytes, used both as the file header and as the GCM additional authenticated data.
    """
    header = {
        "version": FORMAT_VERSION,
        "kem": KEM_ALGORITHM,
        "kdf": KDF_ALGORITHM,
        "cipher": CIPHER_ALGORITHM,
        "salt": base64.b64encode(salt).decode("ascii"),
        "nonce": base64.b64encode(nonce).decode("ascii"),
        "kem_ciphertext": base64.b64encode(kemCiphertext).decode("ascii"),
    }
    return json.dumps(header, sort_keys=True, separators=(",", ":")).encode("utf-8")


def rejectDuplicateKeys(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
    """JSON object hook that rejects duplicate keys.

    Args:
        pairs (list): Key/value pairs of a JSON object.

    Returns:
        dict: The object.

    Raises:
        ArchiveFormatError: If a key occurs more than once.
    """
    result: Dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ArchiveFormatError(f"Invalid header: duplicate field '{key}'")
        result[key] = value
    return result


def decodeBase64Field(header: Dict[str, Any], name: str, expectedSize: int) -> bytes:
    """Strictly decode a Base64 header field and check its decoded size.

    Args:
        header (dict): Parsed header.
        name (str): Field name.
        expectedSize (int): Required decoded length in bytes.

    Returns:
        bytes: Decoded value.

    Raises:
        ArchiveFormatError: If the value is not a string, not valid Base64 or has the wrong length.
    """
    value = header[name]
    if not isinstance(value, str):
        raise ArchiveFormatError(f"Invalid header: '{name}' must be a Base64 string")
    try:
        decoded = base64.b64decode(value.encode("ascii"), validate=True)
    except (binascii.Error, ValueError, UnicodeEncodeError):
        raise ArchiveFormatError(f"Invalid header: '{name}' is not valid Base64")
    if len(decoded) != expectedSize:
        raise ArchiveFormatError(f"Invalid header: '{name}' must be {expectedSize} bytes but is {len(decoded)}")
    return decoded


def readHeader(stream: BinaryIO) -> Tuple[bytes, Dict[str, bytes], int]:
    """Read and strictly validate the magic bytes and the header of an encrypted file.

    Args:
        stream (BinaryIO): Encrypted file positioned at offset 0.

    Returns:
        tuple: (exact header bytes, dict with salt, nonce and kem_ciphertext as bytes, offset where the payload starts).

    Raises:
        ArchiveFormatError: If the file is not a supported, well-formed encrypted backup.
    """
    if stream.read(len(MAGIC)) != MAGIC:
        raise ArchiveFormatError("Not a SaaS backup encrypted file: invalid magic bytes")
    rawLength = stream.read(LENGTH_PREFIX_SIZE)
    if len(rawLength) != LENGTH_PREFIX_SIZE:
        raise ArchiveFormatError("Encrypted file is truncated: incomplete header length")
    headerLength = struct.unpack(">I", rawLength)[0]
    if headerLength == 0 or headerLength > MAX_HEADER_SIZE:
        raise ArchiveFormatError(f"Invalid header length {headerLength} (maximum {MAX_HEADER_SIZE})")
    headerBytes = stream.read(headerLength)
    if len(headerBytes) != headerLength:
        raise ArchiveFormatError("Encrypted file is truncated: incomplete header")
    try:
        header = json.loads(headerBytes.decode("utf-8"), object_pairs_hook=rejectDuplicateKeys)
    except (UnicodeDecodeError, ValueError) as e:
        if isinstance(e, ArchiveFormatError):
            raise
        raise ArchiveFormatError("Invalid header: not valid UTF-8 JSON")
    if not isinstance(header, dict) or set(header) != HEADER_FIELDS:
        raise ArchiveFormatError("Invalid header: unexpected structure or fields")
    if type(header["version"]) is not int or header["version"] != FORMAT_VERSION:
        raise ArchiveFormatError(f"Unsupported encrypted file format version '{header['version']}'")
    for name, expected in (("kem", KEM_ALGORITHM), ("kdf", KDF_ALGORITHM), ("cipher", CIPHER_ALGORITHM)):
        if header[name] != expected:
            raise ArchiveFormatError(f"Unsupported {name} algorithm; only {expected} is supported")
    fields = {
        "salt": decodeBase64Field(header, "salt", SALT_SIZE),
        "nonce": decodeBase64Field(header, "nonce", NONCE_SIZE),
        "kem_ciphertext": decodeBase64Field(header, "kem_ciphertext", KEM_CIPHERTEXT_SIZE),
    }
    return headerBytes, fields, stream.tell()


def checkInputFile(path: str, label: str) -> str:
    """Check that an input is an existing regular file and return its absolute path.

    Args:
        path (str): Input path.
        label (str): Description used in messages.

    Returns:
        str: Absolute path.

    Raises:
        UnsafePathError: If the path is not a regular file.
    """
    if not path or not os.path.isfile(path):
        raise UnsafePathError(f"{label} '{path}' does not exist or is not a regular file")
    return os.path.abspath(path)


def checkOutputPath(outputPath: str, inputPath: str) -> str:
    """Check that an output path is safe to create and return its absolute path.

    Args:
        outputPath (str): Requested output file.
        inputPath (str): Input file that must not be the same file.

    Returns:
        str: Absolute output path.

    Raises:
        UnsafePathError: If the output exists (including a dangling symlink), is the input, or has no existing parent directory.
    """
    if not outputPath:
        raise UnsafePathError("An output path is required")
    outputPath = os.path.abspath(outputPath)
    if os.path.lexists(outputPath):
        raise UnsafePathError(f"Output '{outputPath}' already exists; refusing to overwrite")
    if os.path.realpath(outputPath) == os.path.realpath(inputPath):
        raise UnsafePathError("Input and output must be different files")
    parent = os.path.dirname(outputPath)
    if not os.path.isdir(parent):
        raise UnsafePathError(f"Directory '{parent}' for the output does not exist")
    return outputPath


def publishFile(tempPath: str, finalPath: str) -> None:
    """Move a finished temporary file to its final name without ever replacing an existing file.

    A hard link is created (fails atomically if the name exists) and the temporary name is removed. When the
    filesystem does not support hard links, the final name is first reserved with O_EXCL and then replaced atomically.

    Args:
        tempPath (str): Completed temporary file.
        finalPath (str): Final path, which must not exist.

    Raises:
        UnsafePathError: If the final path already exists.
    """
    try:
        os.link(tempPath, finalPath)
    except FileExistsError:
        raise UnsafePathError(f"Output '{finalPath}' already exists; refusing to overwrite")
    except OSError:
        try:
            createPrivateFile(finalPath)
        except FileExistsError:
            raise UnsafePathError(f"Output '{finalPath}' already exists; refusing to overwrite")
        try:
            os.replace(tempPath, finalPath)
        except OSError:
            os.unlink(finalPath)
            raise
        return
    os.unlink(tempPath)


def removeQuietly(path: Optional[str]) -> None:
    """Remove a file if it exists. Never raises.

    Args:
        path (str, optional): File to remove.
    """
    if path:
        try:
            os.unlink(path)
        except OSError:
            pass


def encryptArchive(inputPath: str, publicKeyPath: str, outputPath: str, opensslPath: str = DEFAULT_OPENSSL) -> Dict[str, Any]:
    """Encrypt a file with ML-KEM-768 + HKDF-SHA256 + AES-256-GCM and write ``<output>.sha256``.

    The archive is streamed in 1 MiB chunks. The output is written to a private temporary file next to the
    destination, then published without overwriting. The input file is not modified or deleted.

    Args:
        inputPath (str): Archive to encrypt.
        publicKeyPath (str): ML-KEM-768 public key (PEM).
        outputPath (str): Encrypted file to create. Must not exist.
        opensslPath (str, optional): OpenSSL executable. Defaults to "openssl".

    Returns:
        dict: ``path``, ``size``, ``sha256``, ``checksum_file``, ``cipher``, ``kem`` and ``kdf``.

    Raises:
        SaasBackupEncryptionError: For missing dependencies, unsupported OpenSSL, invalid keys, unsafe paths or I/O errors.
    """
    requireCryptography()
    inputPath = checkInputFile(inputPath, "Input archive")
    outputPath = checkOutputPath(outputPath, inputPath)
    if os.path.lexists(outputPath + ".sha256"):
        raise UnsafePathError(f"Checksum file '{outputPath}.sha256' already exists; refusing to overwrite")
    checkMlKem768Support(opensslPath, needEncap=True)
    validateKeyFile(publicKeyPath, opensslPath, isPublic=True)

    workDir = None
    tempOutput = None
    try:
        workDir = createSecureTempDir()
        kemCiphertext, sharedSecret = encapsulate(publicKeyPath, workDir, opensslPath)
        salt = secrets.token_bytes(SALT_SIZE)
        nonce = secrets.token_bytes(NONCE_SIZE)
        key = deriveKey(sharedSecret, salt)
        headerBytes = buildHeader(salt, nonce, kemCiphertext)
        encryptor = Cipher(algorithms.AES(key), modes.GCM(nonce)).encryptor()
        encryptor.authenticate_additional_data(headerBytes)

        digest = hashlib.sha256()
        fd, tempOutput = tempfile.mkstemp(prefix=".saas-pqc-", suffix=".tmp", dir=os.path.dirname(outputPath))
        with os.fdopen(fd, "wb") as dst, open(inputPath, "rb") as src:
            os.fchmod(dst.fileno(), FILE_MODE)
            prefix = MAGIC + struct.pack(">I", len(headerBytes)) + headerBytes
            dst.write(prefix)
            digest.update(prefix)
            for chunk in iter(lambda: src.read(CHUNK_SIZE), b""):
                encrypted = encryptor.update(chunk)
                dst.write(encrypted)
                digest.update(encrypted)
            tail = encryptor.finalize() + encryptor.tag
            dst.write(tail)
            digest.update(tail)
            dst.flush()
            os.fsync(dst.fileno())

        publishFile(tempOutput, outputPath)
        tempOutput = None
        sha256 = writeSha256Sidecar(outputPath)
        if sha256 != digest.hexdigest():
            removeQuietly(outputPath)
            removeQuietly(outputPath + ".sha256")
            raise SaasBackupEncryptionError("The encrypted file changed on disk while it was being written; it was removed")
    except OSError as e:
        raise SaasBackupEncryptionError(f"Failed to encrypt '{inputPath}': {type(e).__name__}: {e.strerror or e}")
    finally:
        removeQuietly(tempOutput)
        removeSecureTempDir(workDir)

    return {
        "path": outputPath,
        "size": os.path.getsize(outputPath),
        "sha256": sha256,
        "checksum_file": outputPath + ".sha256",
        "cipher": CIPHER_ALGORITHM,
        "kem": KEM_ALGORITHM,
        "kdf": KDF_ALGORITHM,
    }


def decryptArchive(inputPath: str, privateKeyPath: str, outputPath: str, opensslPath: str = DEFAULT_OPENSSL) -> Dict[str, Any]:
    """Decrypt a file produced by encryptArchive.

    The header is validated and authenticated as AES-GCM additional authenticated data. The plaintext is written to a
    private temporary file in the destination directory and is only published after the GCM tag has been verified.
    On any failure the temporary file is removed and nothing is published. An existing output is never overwritten.

    Args:
        inputPath (str): Encrypted file (``.tar.gz.enc``).
        privateKeyPath (str): ML-KEM-768 private key (PEM, unencrypted).
        outputPath (str): Decrypted file to create. Must not exist.
        opensslPath (str, optional): OpenSSL executable. Defaults to "openssl".

    Returns:
        dict: ``path``, ``size`` and ``sha256`` of the decrypted file.

    Raises:
        ArchiveFormatError: If the file is malformed, truncated or unsupported.
        AuthenticationError: If the private key is wrong or the header or payload was modified.
        SaasBackupEncryptionError: For other dependency, OpenSSL, key, path or I/O errors.
    """
    requireCryptography()
    inputPath = checkInputFile(inputPath, "Encrypted archive")
    outputPath = checkOutputPath(outputPath, inputPath)

    workDir = None
    tempOutput = None
    try:
        with open(inputPath, "rb") as src:
            headerBytes, fields, payloadStart = readHeader(src)
            ciphertextLength = os.fstat(src.fileno()).st_size - payloadStart - TAG_SIZE
            if ciphertextLength < 0:
                raise ArchiveFormatError("Encrypted file is truncated: the authentication tag is missing")
            src.seek(-TAG_SIZE, os.SEEK_END)
            tag = src.read(TAG_SIZE)

            checkMlKem768Support(opensslPath, needEncap=False)
            validateKeyFile(privateKeyPath, opensslPath, isPublic=False)
            workDir = createSecureTempDir()
            sharedSecret = decapsulate(privateKeyPath, fields["kem_ciphertext"], workDir, opensslPath)
            key = deriveKey(sharedSecret, fields["salt"])
            decryptor = Cipher(algorithms.AES(key), modes.GCM(fields["nonce"], tag)).decryptor()
            decryptor.authenticate_additional_data(headerBytes)

            fd, tempOutput = tempfile.mkstemp(prefix=".saas-pqc-", suffix=".tmp", dir=os.path.dirname(outputPath))
            with os.fdopen(fd, "wb") as dst:
                os.fchmod(dst.fileno(), FILE_MODE)
                src.seek(payloadStart)
                remaining = ciphertextLength
                while remaining:
                    chunk = src.read(min(CHUNK_SIZE, remaining))
                    if not chunk:
                        raise ArchiveFormatError("Encrypted file is truncated: the ciphertext is incomplete")
                    dst.write(decryptor.update(chunk))
                    remaining -= len(chunk)
                try:
                    dst.write(decryptor.finalize())
                except InvalidTag:
                    raise AuthenticationError(
                        "Authentication failed: the private key is wrong, or the header or encrypted payload has been modified. No output was written"
                    )
                dst.flush()
                os.fsync(dst.fileno())

        publishFile(tempOutput, outputPath)
        tempOutput = None
    except OSError as e:
        raise SaasBackupEncryptionError(f"Failed to decrypt '{inputPath}': {type(e).__name__}: {e.strerror or e}")
    finally:
        removeQuietly(tempOutput)
        removeSecureTempDir(workDir)

    return {"path": outputPath, "size": os.path.getsize(outputPath), "sha256": sha256File(outputPath)}
