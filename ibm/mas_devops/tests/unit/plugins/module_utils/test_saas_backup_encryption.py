"""Unit tests for the saas_backup_encryption module utils.

The OpenSSL subprocess boundary is replaced by FakeOpenSsl (see conftest.py), so these tests do not depend on the
host OpenSSL version. Real ML-KEM-768 integration tests at the end run only when OpenSSL supports it.
"""

import base64
import hashlib
import json
import os
import shutil
import stat
import struct
import subprocess

import pytest

import saas_backup_encryption as enc


def sha256Bytes(data: bytes) -> str:
    """Return the SHA-256 hex digest of bytes."""
    return hashlib.sha256(data).hexdigest()


def readAll(path):
    """Read a whole file."""
    with open(path, "rb") as f:
        return f.read()


def headerSpan(data: bytes):
    """Return (start, end) offsets of the header JSON inside an encrypted file."""
    length = struct.unpack(">I", data[8:12])[0]
    return 12, 12 + length


def rewriteHeader(path, mutate):
    """Rewrite the header JSON of an encrypted file (keeping a valid length prefix)."""
    data = readAll(path)
    start, end = headerSpan(data)
    header = json.loads(data[start:end])
    mutate(header)
    newHeader = json.dumps(header, sort_keys=True, separators=(",", ":")).encode()
    with open(path, "wb") as f:
        f.write(data[:8] + struct.pack(">I", len(newHeader)) + newHeader + data[end:])


def leftovers(directory):
    """List hidden temporary files left in a directory."""
    return [n for n in os.listdir(directory) if n.startswith(".saas-pqc-")]


@pytest.fixture
def encrypted(fakeOpenSsl, keys, archive, tmp_path):
    """Encrypt the archive and return the result."""
    return enc.encryptArchive(archive, keys["public"], str(tmp_path / "backup.tar.gz.enc"))


class TestEncrypt:
    """Encryption behaviour."""

    def test_creates_encrypted_file_and_sidecar(self, encrypted, archive):
        """GIVEN a valid archive and key WHEN encrypted THEN a .tar.gz.enc and checksum sidecar exist and the original is retained."""
        assert encrypted["path"].endswith(".tar.gz.enc")
        assert readAll(encrypted["path"]).startswith(enc.MAGIC)
        assert encrypted["size"] == os.path.getsize(archive) + len(enc.MAGIC) + 4 + headerSpan(readAll(encrypted["path"]))[1] - 12 + enc.TAG_SIZE
        assert os.path.exists(archive)
        assert readAll(encrypted["checksum_file"]).decode() == f"{sha256Bytes(readAll(encrypted['path']))}  backup.tar.gz.enc\n"
        assert encrypted["sha256"] == sha256Bytes(readAll(encrypted["path"]))
        assert (encrypted["cipher"], encrypted["kem"], encrypted["kdf"]) == ("AES-256-GCM", "ML-KEM-768", "HKDF-SHA256")

    def test_ciphertext_does_not_contain_plaintext(self, encrypted, archive):
        """GIVEN an encrypted archive THEN the plaintext does not appear in it."""
        assert readAll(archive)[1000:1064] not in readAll(encrypted["path"])

    def test_output_permissions_are_restrictive(self, encrypted):
        """GIVEN an encryption WHEN finished THEN the output and sidecar are 0600."""
        for path in (encrypted["path"], encrypted["checksum_file"]):
            assert stat.S_IMODE(os.stat(path).st_mode) == 0o600

    def test_header_is_canonical_and_complete(self, encrypted):
        """GIVEN an encrypted file THEN the header holds exactly the documented fields with correct sizes."""
        data = readAll(encrypted["path"])
        start, end = headerSpan(data)
        header = json.loads(data[start:end])
        assert set(header) == enc.HEADER_FIELDS
        assert data[start:end] == json.dumps(header, sort_keys=True, separators=(",", ":")).encode()
        assert len(base64.b64decode(header["kem_ciphertext"])) == enc.KEM_CIPHERTEXT_SIZE

    def test_each_encryption_uses_fresh_salt_nonce_and_kem(self, fakeOpenSsl, keys, archive, tmp_path):
        """GIVEN the same input encrypted twice THEN salt, nonce and KEM ciphertext differ."""
        a = enc.encryptArchive(archive, keys["public"], str(tmp_path / "a.tar.gz.enc"))
        b = enc.encryptArchive(archive, keys["public"], str(tmp_path / "b.tar.gz.enc"))
        da, db = readAll(a["path"]), readAll(b["path"])
        ha, hb = json.loads(da[slice(*headerSpan(da))]), json.loads(db[slice(*headerSpan(db))])
        assert all(ha[f] != hb[f] for f in ("salt", "nonce", "kem_ciphertext"))

    def test_streams_in_chunks(self, fakeOpenSsl, keys, archive, tmp_path, monkeypatch):
        """GIVEN a multi-MiB archive THEN it is read in chunks of at most 1 MiB, never whole."""
        sizes = []
        realOpen = open

        class Spy:
            def __init__(self, f):
                self.f = f

            def read(self, n=-1):
                sizes.append(n)
                return self.f.read(n)

            def __getattr__(self, name):
                return getattr(self.f, name)

            def __enter__(self):
                return self

            def __exit__(self, *a):
                self.f.close()

        def spyOpen(path, mode="r", *a, **k):
            f = realOpen(path, mode, *a, **k)
            return Spy(f) if path == archive and "b" in mode else f

        monkeypatch.setattr("builtins.open", spyOpen)
        enc.encryptArchive(archive, keys["public"], str(tmp_path / "s.tar.gz.enc"))
        assert sizes and all(0 < n <= enc.CHUNK_SIZE for n in sizes)

    def test_existing_encrypted_output_not_overwritten(self, fakeOpenSsl, keys, archive, tmp_path):
        """GIVEN an existing encrypted output WHEN encrypting to it THEN it fails and the file is untouched."""
        out = tmp_path / "backup.tar.gz.enc"
        out.write_bytes(b"precious")
        with pytest.raises(enc.UnsafePathError, match="refusing to overwrite"):
            enc.encryptArchive(archive, keys["public"], str(out))
        assert out.read_bytes() == b"precious"
        assert leftovers(tmp_path) == []

    def test_dangling_symlink_output_refused(self, fakeOpenSsl, keys, archive, tmp_path):
        """GIVEN a dangling symlink at the output path THEN it is refused rather than followed."""
        out = tmp_path / "backup.tar.gz.enc"
        os.symlink(str(tmp_path / "nowhere"), str(out))
        with pytest.raises(enc.UnsafePathError):
            enc.encryptArchive(archive, keys["public"], str(out))

    def test_existing_checksum_sidecar_refused_before_work(self, fakeOpenSsl, keys, archive, tmp_path):
        """GIVEN an existing .sha256 sidecar THEN encryption is refused and no encrypted file is created."""
        (tmp_path / "backup.tar.gz.enc.sha256").write_text("x")
        with pytest.raises(enc.UnsafePathError):
            enc.encryptArchive(archive, keys["public"], str(tmp_path / "backup.tar.gz.enc"))
        assert not (tmp_path / "backup.tar.gz.enc").exists()

    def test_input_equal_output_refused(self, fakeOpenSsl, keys, archive):
        """GIVEN input and output are the same file THEN it is refused."""
        with pytest.raises(enc.UnsafePathError):
            enc.encryptArchive(archive, keys["public"], archive)

    def test_missing_output_directory_refused(self, fakeOpenSsl, keys, archive, tmp_path):
        """GIVEN an output in a missing directory THEN it is refused."""
        with pytest.raises(enc.UnsafePathError, match="does not exist"):
            enc.encryptArchive(archive, keys["public"], str(tmp_path / "nope" / "x.tar.gz.enc"))

    def test_missing_input_refused(self, fakeOpenSsl, keys, tmp_path):
        """GIVEN a missing archive THEN it is refused."""
        with pytest.raises(enc.UnsafePathError, match="does not exist"):
            enc.encryptArchive(str(tmp_path / "missing.tar.gz"), keys["public"], str(tmp_path / "x.tar.gz.enc"))

    def test_missing_public_key_gives_useful_error(self, fakeOpenSsl, archive, tmp_path):
        """GIVEN a missing public key THEN the error names the file."""
        missing = str(tmp_path / "no-such-public.pem")
        with pytest.raises(enc.InvalidKeyError, match="no-such-public.pem"):
            enc.encryptArchive(archive, missing, str(tmp_path / "x.tar.gz.enc"))
        assert not (tmp_path / "x.tar.gz.enc").exists()

    def test_private_key_rejected_as_public_key(self, fakeOpenSsl, keys, archive, tmp_path):
        """GIVEN a private key passed as the public key THEN it is refused without echoing its content."""
        with pytest.raises(enc.InvalidKeyError, match="public key only") as info:
            enc.encryptArchive(archive, keys["private"], str(tmp_path / "x.tar.gz.enc"))
        assert "id=alpha" not in str(info.value)

    def test_garbage_public_key_rejected(self, fakeOpenSsl, archive, tmp_path):
        """GIVEN a file that OpenSSL cannot parse THEN the error is clear."""
        bad = tmp_path / "bad.pem"
        bad.write_text("not a key")
        with pytest.raises(enc.InvalidKeyError, match="could not read"):
            enc.encryptArchive(archive, str(bad), str(tmp_path / "x.tar.gz.enc"))

    def test_non_mlkem_public_key_rejected(self, fakeOpenSsl, keys, archive, tmp_path, monkeypatch):
        """GIVEN a key of another algorithm THEN it is rejected."""
        original = fakeOpenSsl

        def other(path, args):
            res = original(path, args)
            if args[0] == "pkey":
                res.stdout = "RSA Public-Key: (2048 bit)\n"
            return res

        monkeypatch.setattr(enc, "runOpenSsl", other)
        with pytest.raises(enc.InvalidKeyError, match="not an ML-KEM-768 key"):
            enc.encryptArchive(archive, keys["public"], str(tmp_path / "x.tar.gz.enc"))

    def test_openssl_without_mlkem768_gives_useful_error(self, fakeOpenSsl, keys, archive, tmp_path):
        """GIVEN an OpenSSL without ML-KEM-768 THEN a clear UnsupportedOpenSslError names the requirement and nothing is written."""
        fakeOpenSsl.supportsMlKem = False
        with pytest.raises(enc.UnsupportedOpenSslError, match="ML-KEM-768.*OpenSSL 3.5"):
            enc.encryptArchive(archive, keys["public"], str(tmp_path / "x.tar.gz.enc"))
        assert os.listdir(tmp_path / "keys") and not (tmp_path / "x.tar.gz.enc").exists()

    def test_openssl_without_encap_gives_useful_error(self, fakeOpenSsl, keys, archive, tmp_path):
        """GIVEN an OpenSSL whose pkeyutl lacks -encap THEN a clear error is raised."""
        fakeOpenSsl.supportsEncap = False
        with pytest.raises(enc.UnsupportedOpenSslError, match="does not support -encap"):
            enc.encryptArchive(archive, keys["public"], str(tmp_path / "x.tar.gz.enc"))

    def test_openssl_executable_missing(self, keys, archive, tmp_path):
        """GIVEN no OpenSSL executable THEN a clear error is raised."""
        with pytest.raises(enc.UnsupportedOpenSslError, match="was not found"):
            enc.encryptArchive(archive, keys["public"], str(tmp_path / "x.tar.gz.enc"), opensslPath="/nonexistent/openssl")

    def test_missing_cryptography_gives_clear_diagnostic(self, keys, archive, tmp_path, monkeypatch):
        """GIVEN the cryptography package is not importable THEN a MissingDependencyError explains how to install it."""
        monkeypatch.setattr(enc, "CRYPTOGRAPHY_IMPORT_ERROR", ImportError("No module named 'cryptography'"))
        with pytest.raises(enc.MissingDependencyError, match="cryptography.*pip install"):
            enc.encryptArchive(archive, keys["public"], str(tmp_path / "x.tar.gz.enc"))
        with pytest.raises(enc.MissingDependencyError):
            enc.decryptArchive(archive, keys["private"], str(tmp_path / "x.tar.gz"))

    def test_temp_files_removed_on_failure(self, fakeOpenSsl, keys, archive, tmp_path, monkeypatch):
        """GIVEN a failure mid-encryption THEN no temporary file or secret directory is left behind."""
        monkeypatch.setattr(enc, "publishFile", lambda *a: (_ for _ in ()).throw(OSError(28, "No space left on device")))
        before = set(os.listdir("/tmp")) if os.path.isdir("/tmp") else set()
        with pytest.raises(enc.SaasBackupEncryptionError, match="No space"):
            enc.encryptArchive(archive, keys["public"], str(tmp_path / "x.tar.gz.enc"))
        assert leftovers(tmp_path) == []
        assert not (tmp_path / "x.tar.gz.enc").exists()
        assert all(not os.path.exists(p) for p in fakeOpenSsl.secretFiles)
        assert {n for n in os.listdir("/tmp") if n.startswith("saas-pqc-")} <= {n for n in before if n.startswith("saas-pqc-")}

    def test_shared_secret_files_are_private_and_removed(self, fakeOpenSsl, keys, archive, tmp_path, monkeypatch):
        """GIVEN encryption THEN the shared secret lives in a 0700 directory and is gone afterwards."""
        modes = []
        realRun = fakeOpenSsl

        def spy(path, args):
            if args[:2] == ["pkeyutl", "-encap"]:
                secretPath = args[args.index("-secret") + 1]
                modes.append((stat.S_IMODE(os.stat(secretPath).st_mode), stat.S_IMODE(os.stat(os.path.dirname(secretPath)).st_mode)))
            return realRun(path, args)

        monkeypatch.setattr(enc, "runOpenSsl", spy)
        enc.encryptArchive(archive, keys["public"], str(tmp_path / "x.tar.gz.enc"))
        assert modes == [(0o600, 0o700)]
        assert all(not os.path.exists(p) for p in fakeOpenSsl.secretFiles)
        assert all(not os.path.exists(os.path.dirname(p)) for p in fakeOpenSsl.secretFiles)

    def test_publish_falls_back_without_hardlinks(self, fakeOpenSsl, keys, archive, tmp_path, monkeypatch):
        """GIVEN a filesystem without hard links THEN publication still works and never overwrites."""
        monkeypatch.setattr(os, "link", lambda *a: (_ for _ in ()).throw(OSError(1, "Operation not permitted")))
        result = enc.encryptArchive(archive, keys["public"], str(tmp_path / "x.tar.gz.enc"))
        assert os.path.exists(result["path"]) and leftovers(tmp_path) == []


class TestDecrypt:
    """Decryption behaviour."""

    def test_round_trip_restores_original_bytes(self, encrypted, keys, archive, tmp_path):
        """GIVEN an encrypted archive WHEN decrypted with the matching private key THEN bytes and SHA-256 are identical."""
        result = enc.decryptArchive(encrypted["path"], keys["private"], str(tmp_path / "restored.tar.gz"))
        assert readAll(result["path"]) == readAll(archive)
        assert result["sha256"] == sha256Bytes(readAll(archive)) == enc.sha256File(archive)
        assert stat.S_IMODE(os.stat(result["path"]).st_mode) == 0o600
        assert leftovers(tmp_path) == []

    def test_empty_archive_round_trip(self, fakeOpenSsl, keys, tmp_path):
        """GIVEN an empty input THEN it round-trips."""
        empty = tmp_path / "empty.tar.gz"
        empty.write_bytes(b"")
        e = enc.encryptArchive(str(empty), keys["public"], str(tmp_path / "empty.tar.gz.enc"))
        d = enc.decryptArchive(e["path"], keys["private"], str(tmp_path / "empty-restored.tar.gz"))
        assert d["size"] == 0

    def test_wrong_private_key_fails_and_publishes_nothing(self, encrypted, keys, tmp_path):
        """GIVEN a different private key THEN authentication fails and no output or temp file remains."""
        out = tmp_path / "restored.tar.gz"
        with pytest.raises(enc.AuthenticationError, match="private key is wrong"):
            enc.decryptArchive(encrypted["path"], keys["other"], str(out))
        assert not out.exists() and leftovers(tmp_path) == []

    def test_modified_payload_fails_authentication(self, encrypted, keys, tmp_path):
        """GIVEN one flipped payload bit THEN authentication fails and no plaintext is published."""
        data = bytearray(readAll(encrypted["path"]))
        data[headerSpan(bytes(data))[1] + 5000] ^= 0x01
        open(encrypted["path"], "wb").write(bytes(data))
        out = tmp_path / "restored.tar.gz"
        with pytest.raises(enc.AuthenticationError):
            enc.decryptArchive(encrypted["path"], keys["private"], str(out))
        assert not out.exists() and leftovers(tmp_path) == []

    def test_modified_tag_fails_authentication(self, encrypted, keys, tmp_path):
        """GIVEN a flipped tag bit THEN authentication fails."""
        data = bytearray(readAll(encrypted["path"]))
        data[-1] ^= 0x01
        open(encrypted["path"], "wb").write(bytes(data))
        with pytest.raises(enc.AuthenticationError):
            enc.decryptArchive(encrypted["path"], keys["private"], str(tmp_path / "r.tar.gz"))

    def test_modified_header_fails_authentication(self, encrypted, keys, tmp_path):
        """GIVEN a header that is still valid but differs in bytes (reordered JSON) THEN authentication fails.

        Reordering keeps every field value intact, so only the AAD binding can detect the change.
        """
        data = readAll(encrypted["path"])
        start, end = headerSpan(data)
        header = json.loads(data[start:end])
        reordered = json.dumps(header, sort_keys=False, indent=None).encode()  # different bytes, same content
        assert reordered != data[start:end]
        open(encrypted["path"], "wb").write(data[:8] + struct.pack(">I", len(reordered)) + reordered + data[end:])
        out = tmp_path / "r.tar.gz"
        with pytest.raises(enc.AuthenticationError):
            enc.decryptArchive(encrypted["path"], keys["private"], str(out))
        assert not out.exists()

    def test_modified_salt_fails_authentication(self, encrypted, keys, tmp_path):
        """GIVEN a different (valid) salt THEN decryption cannot succeed."""
        rewriteHeader(encrypted["path"], lambda h: h.__setitem__("salt", base64.b64encode(b"\x01" * 16).decode()))
        with pytest.raises(enc.AuthenticationError):
            enc.decryptArchive(encrypted["path"], keys["private"], str(tmp_path / "r.tar.gz"))

    def test_header_is_bound_as_additional_data(self, encrypted, keys, tmp_path, monkeypatch):
        """GIVEN decryption THEN the exact header bytes are passed to authenticate_additional_data (not just parsed)."""
        data = readAll(encrypted["path"])
        calls = []
        realBuild = enc.deriveKey

        class Recorder:
            def __init__(self, inner):
                self.inner = inner

            def authenticate_additional_data(self, aad):
                calls.append(aad)
                return self.inner.authenticate_additional_data(aad)

            def __getattr__(self, name):
                return getattr(self.inner, name)

        realCipher = enc.Cipher

        class CipherSpy:
            def __init__(self, *a, **k):
                self.c = realCipher(*a, **k)

            def decryptor(self):
                return Recorder(self.c.decryptor())

        monkeypatch.setattr(enc, "Cipher", CipherSpy)
        enc.decryptArchive(encrypted["path"], keys["private"], str(tmp_path / "r.tar.gz"))
        assert calls == [data[slice(*headerSpan(data))]]
        assert realBuild is enc.deriveKey

    def test_existing_decrypted_output_not_overwritten(self, encrypted, keys, tmp_path):
        """GIVEN an existing destination THEN decryption refuses and leaves it untouched."""
        out = tmp_path / "restored.tar.gz"
        out.write_bytes(b"keep me")
        with pytest.raises(enc.UnsafePathError, match="refusing to overwrite"):
            enc.decryptArchive(encrypted["path"], keys["private"], str(out))
        assert out.read_bytes() == b"keep me"

    def test_destination_created_concurrently_is_not_overwritten(self, encrypted, keys, tmp_path, monkeypatch):
        """GIVEN the destination appears after the pre-check THEN publication still refuses to replace it."""
        out = tmp_path / "restored.tar.gz"
        realPublish = enc.publishFile

        def racing(tempPath, finalPath):
            out.write_bytes(b"race winner")
            return realPublish(tempPath, finalPath)

        monkeypatch.setattr(enc, "publishFile", racing)
        with pytest.raises(enc.UnsafePathError):
            enc.decryptArchive(encrypted["path"], keys["private"], str(out))
        assert out.read_bytes() == b"race winner" and leftovers(tmp_path) == []

    def test_missing_private_key_gives_useful_error(self, encrypted, tmp_path):
        """GIVEN a missing private key THEN the error names the file."""
        with pytest.raises(enc.InvalidKeyError, match="no-private.pem"):
            enc.decryptArchive(encrypted["path"], str(tmp_path / "no-private.pem"), str(tmp_path / "r.tar.gz"))

    def test_public_key_rejected_as_private_key(self, encrypted, keys, tmp_path):
        """GIVEN a public key passed for decryption THEN it is rejected."""
        with pytest.raises(enc.InvalidKeyError, match="PEM private key"):
            enc.decryptArchive(encrypted["path"], keys["public"], str(tmp_path / "r.tar.gz"))

    def test_decrypt_unsupported_openssl(self, encrypted, keys, fakeOpenSsl, tmp_path):
        """GIVEN an OpenSSL without ML-KEM-768 THEN decryption fails clearly."""
        fakeOpenSsl.supportsMlKem = False
        with pytest.raises(enc.UnsupportedOpenSslError):
            enc.decryptArchive(encrypted["path"], keys["private"], str(tmp_path / "r.tar.gz"))
        assert leftovers(tmp_path) == []


class TestFormatValidation:
    """Strict validation of the encrypted file format."""

    def decryptBytes(self, data, keys, tmp_path, name="bad.tar.gz.enc"):
        """Write data as an encrypted file and try to decrypt it."""
        path = tmp_path / name
        path.write_bytes(data)
        out = tmp_path / "out.tar.gz"
        try:
            enc.decryptArchive(str(path), keys["private"], str(out))
        finally:
            assert not out.exists()
            assert leftovers(tmp_path) == []

    def test_invalid_magic_rejected(self, encrypted, keys, tmp_path):
        """GIVEN wrong magic bytes THEN the file is rejected."""
        data = b"NOTMAGIC" + readAll(encrypted["path"])[8:]
        with pytest.raises(enc.ArchiveFormatError, match="invalid magic"):
            self.decryptBytes(data, keys, tmp_path)

    @pytest.mark.parametrize("length", [0, enc.MAX_HEADER_SIZE + 1, 0xFFFFFFFF])
    def test_invalid_header_length_rejected(self, encrypted, keys, tmp_path, length):
        """GIVEN a zero or oversized header length THEN the file is rejected."""
        data = readAll(encrypted["path"])
        data = data[:8] + struct.pack(">I", length) + data[12:]
        with pytest.raises(enc.ArchiveFormatError, match="Invalid header length"):
            self.decryptBytes(data, keys, tmp_path)

    def test_header_length_beyond_file_rejected(self, encrypted, keys, tmp_path):
        """GIVEN a header length larger than the file THEN it is reported as truncated."""
        data = readAll(encrypted["path"])[:20]
        with pytest.raises(enc.ArchiveFormatError, match="truncated"):
            self.decryptBytes(data, keys, tmp_path)

    def test_truncated_length_prefix_rejected(self, keys, tmp_path):
        """GIVEN a file that ends inside the length prefix THEN it is rejected."""
        with pytest.raises(enc.ArchiveFormatError, match="truncated"):
            self.decryptBytes(enc.MAGIC + b"\x00\x00", keys, tmp_path)

    @pytest.mark.parametrize("field", ["salt", "nonce", "kem_ciphertext"])
    def test_invalid_base64_rejected(self, encrypted, keys, tmp_path, field):
        """GIVEN invalid Base64 in a header field THEN the file is rejected."""
        rewriteHeader(encrypted["path"], lambda h: h.__setitem__(field, "!!!not-base64!!!"))
        with pytest.raises(enc.ArchiveFormatError, match=f"'{field}' is not valid Base64"):
            self.decryptBytes(readAll(encrypted["path"]), keys, tmp_path)

    def test_non_string_base64_rejected(self, encrypted, keys, tmp_path):
        """GIVEN a numeric Base64 field THEN the file is rejected."""
        rewriteHeader(encrypted["path"], lambda h: h.__setitem__("salt", 5))
        with pytest.raises(enc.ArchiveFormatError, match="must be a Base64 string"):
            self.decryptBytes(readAll(encrypted["path"]), keys, tmp_path)

    @pytest.mark.parametrize("field,size", [("salt", 15), ("nonce", 13), ("kem_ciphertext", 1087)])
    def test_wrong_field_lengths_rejected(self, encrypted, keys, tmp_path, field, size):
        """GIVEN a salt, nonce or KEM ciphertext of the wrong length THEN the file is rejected."""
        rewriteHeader(encrypted["path"], lambda h: h.__setitem__(field, base64.b64encode(b"a" * size).decode()))
        with pytest.raises(enc.ArchiveFormatError, match=f"'{field}' must be"):
            self.decryptBytes(readAll(encrypted["path"]), keys, tmp_path)

    @pytest.mark.parametrize(
        "field,value", [("version", 2), ("version", True), ("version", "1"), ("kem", "ML-KEM-512"), ("kdf", "HKDF-SHA1"), ("cipher", "AES-128-GCM")]
    )
    def test_unsupported_versions_and_algorithms_rejected(self, encrypted, keys, tmp_path, field, value):
        """GIVEN an unsupported version or algorithm identifier THEN the file is rejected."""
        rewriteHeader(encrypted["path"], lambda h: h.__setitem__(field, value))
        with pytest.raises(enc.ArchiveFormatError, match="Unsupported"):
            self.decryptBytes(readAll(encrypted["path"]), keys, tmp_path)

    def test_extra_and_missing_fields_rejected(self, encrypted, keys, tmp_path):
        """GIVEN extra or missing header fields THEN the file is rejected."""
        rewriteHeader(encrypted["path"], lambda h: h.__setitem__("extra", 1))
        with pytest.raises(enc.ArchiveFormatError, match="unexpected structure"):
            self.decryptBytes(readAll(encrypted["path"]), keys, tmp_path)
        rewriteHeader(encrypted["path"], lambda h: (h.pop("extra"), h.pop("nonce")))
        with pytest.raises(enc.ArchiveFormatError, match="unexpected structure"):
            self.decryptBytes(readAll(encrypted["path"]), keys, tmp_path)

    def test_non_json_header_rejected(self, encrypted, keys, tmp_path):
        """GIVEN a header that is not JSON THEN the file is rejected."""
        junk = b"\xff\xfe not json"
        data = enc.MAGIC + struct.pack(">I", len(junk)) + junk + b"\0" * 64
        with pytest.raises(enc.ArchiveFormatError, match="not valid UTF-8 JSON"):
            self.decryptBytes(data, keys, tmp_path)

    def test_json_array_header_rejected(self, keys, tmp_path):
        """GIVEN a JSON array as header THEN the file is rejected."""
        junk = b"[1,2]"
        with pytest.raises(enc.ArchiveFormatError, match="unexpected structure"):
            self.decryptBytes(enc.MAGIC + struct.pack(">I", len(junk)) + junk + b"\0" * 64, keys, tmp_path)

    def test_duplicate_header_keys_rejected(self, encrypted, keys, tmp_path):
        """GIVEN a header with a duplicated field THEN the file is rejected."""
        data = readAll(encrypted["path"])
        start, end = headerSpan(data)
        header = data[start:end].decode()
        dup = header[:-1] + ',"version":1}'
        newHeader = dup.encode()
        data = data[:8] + struct.pack(">I", len(newHeader)) + newHeader + data[end:]
        with pytest.raises(enc.ArchiveFormatError, match="duplicate field"):
            self.decryptBytes(data, keys, tmp_path)

    def test_missing_tag_rejected(self, encrypted, keys, tmp_path):
        """GIVEN a file that ends right after the header THEN the missing tag is reported."""
        data = readAll(encrypted["path"])
        end = headerSpan(data)[1]
        with pytest.raises(enc.ArchiveFormatError, match="tag is missing"):
            self.decryptBytes(data[: end + 3], keys, tmp_path)

    @pytest.mark.parametrize("cut", [1, 16, 17, 1024, 1024 * 1024])
    def test_truncated_archive_rejected(self, encrypted, keys, tmp_path, cut):
        """GIVEN a truncated encrypted file THEN it is rejected and nothing is published."""
        data = readAll(encrypted["path"])[:-cut]
        with pytest.raises((enc.ArchiveFormatError, enc.AuthenticationError)):
            self.decryptBytes(data, keys, tmp_path)

    def test_appended_data_rejected(self, encrypted, keys, tmp_path):
        """GIVEN data appended after the tag THEN authentication fails."""
        with pytest.raises(enc.AuthenticationError):
            self.decryptBytes(readAll(encrypted["path"]) + b"x", keys, tmp_path)

    def test_empty_file_rejected(self, keys, tmp_path):
        """GIVEN an empty file THEN it is rejected."""
        with pytest.raises(enc.ArchiveFormatError):
            self.decryptBytes(b"", keys, tmp_path)


def realMlKemAvailable() -> bool:
    """Return True when the host OpenSSL can really do ML-KEM-768 encapsulation."""
    if shutil.which("openssl") is None:
        return False
    try:
        enc.checkMlKem768Support("openssl", needEncap=True)
        return True
    except enc.SaasBackupEncryptionError:
        return False


@pytest.mark.skipif(not realMlKemAvailable(), reason="host OpenSSL has no ML-KEM-768 / pkeyutl -encap support (OpenSSL 3.5+ required)")
class TestRealOpenSsl:
    """End to end tests against the real OpenSSL ML-KEM-768 implementation."""

    @pytest.fixture
    def realKeys(self, tmp_path):
        """Generate throw-away ML-KEM-768 key pairs (never reused or committed)."""
        out = {}
        for name in ("a", "b"):
            priv, pub = tmp_path / f"{name}-priv.pem", tmp_path / f"{name}-pub.pem"
            subprocess.run(["openssl", "genpkey", "-algorithm", "ML-KEM-768", "-out", str(priv)], check=True, capture_output=True)
            subprocess.run(["openssl", "pkey", "-in", str(priv), "-pubout", "-out", str(pub)], check=True, capture_output=True)
            out[name] = (str(priv), str(pub))
        return out

    def test_real_round_trip_and_tamper_detection(self, realKeys, archive, tmp_path):
        """GIVEN real keys THEN a round trip restores identical bytes, a wrong key and tampering are rejected."""
        e = enc.encryptArchive(archive, realKeys["a"][1], str(tmp_path / "r.tar.gz.enc"))
        d = enc.decryptArchive(e["path"], realKeys["a"][0], str(tmp_path / "r.tar.gz"))
        assert readAll(d["path"]) == readAll(archive)
        with pytest.raises(enc.AuthenticationError):
            enc.decryptArchive(e["path"], realKeys["b"][0], str(tmp_path / "wrong.tar.gz"))
        data = bytearray(readAll(e["path"]))
        data[-40] ^= 1
        open(e["path"], "wb").write(bytes(data))
        with pytest.raises(enc.AuthenticationError):
            enc.decryptArchive(e["path"], realKeys["a"][0], str(tmp_path / "tampered.tar.gz"))
        assert not (tmp_path / "wrong.tar.gz").exists() and not (tmp_path / "tampered.tar.gz").exists()
