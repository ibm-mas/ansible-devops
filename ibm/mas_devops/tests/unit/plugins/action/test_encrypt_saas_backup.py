"""Unit tests for the encrypt_saas_backup action plugin.

The OpenSSL subprocess boundary is mocked, so these tests do not require an ML-KEM capable OpenSSL.
"""

import hashlib
import os
import stat
import subprocess
import sys

import pytest
from ansible.errors import AnsibleError

import encrypt_saas_backup

ActionModule = encrypt_saas_backup.ActionModule

# The same module object the plugin uses (registered under its collection path by conftest.py)
enc = sys.modules["ansible_collections.ibm.mas_devops.plugins.module_utils.saas_backup_encryption"]


class FakeOpenSsl:
    """Minimal fake of the OpenSSL CLI (ML-KEM-768 encap/decap only)."""

    def __init__(self, supportsMlKem=True):
        self.supportsMlKem = supportsMlKem

    def __call__(self, opensslPath, args):
        def result(rc=0, out="", err=""):
            return subprocess.CompletedProcess([opensslPath] + args, rc, out, err)

        if args == ["version"]:
            return result(out="OpenSSL fake\n")
        if args == ["list", "-kem-algorithms"]:
            return result(out="  ML-KEM-768 @ default\n" if self.supportsMlKem else "  X25519\n")
        if args == ["pkeyutl", "-help"]:
            return result(err=" -encap\n -decap\n")
        if args[0] == "pkey":
            return result(out="ML-KEM-768 Public-Key:\n")
        if args[:2] == ["pkeyutl", "-encap"]:
            kem = os.urandom(enc.KEM_CIPHERTEXT_SIZE)
            open(args[args.index("-out") + 1], "wb").write(kem)
            open(args[args.index("-secret") + 1], "wb").write(hashlib.sha256(kem).digest())
            return result()
        if args[:2] == ["pkeyutl", "-decap"]:
            kem = open(args[args.index("-in") + 1], "rb").read()
            open(args[args.index("-secret") + 1], "wb").write(hashlib.sha256(kem).digest())
            return result()
        return result(rc=1, err="unexpected")


class TestEncryptSaasBackup:
    """Test cases for encrypt_saas_backup."""

    @pytest.fixture
    def action_module(self, action_module_base):
        """Create ActionModule instance."""
        return ActionModule(**action_module_base)

    @pytest.fixture(autouse=True)
    def fakeOpenSsl(self, monkeypatch):
        """Mock the OpenSSL boundary for every test."""
        fake = FakeOpenSsl()
        monkeypatch.setattr(enc, "runOpenSsl", fake)
        return fake

    @pytest.fixture
    def files(self, tmp_path):
        """Create a fake archive and a fake public key."""
        archive = tmp_path / "saas-backup-test.tar.gz"
        archive.write_bytes(os.urandom(1024 * 1024 + 123))
        pub = tmp_path / "public.pem"
        pub.write_text("-----BEGIN PUBLIC KEY-----\nid=x\n-----END PUBLIC KEY-----\n")
        return archive, pub

    def run(self, module, archive, pub, output=None):
        """Run the plugin with the given arguments."""
        module._task.args = {
            "archive_path": str(archive),
            "public_key_path": str(pub),
            "output_path": str(output if output is not None else str(archive) + ".enc"),
        }
        return module.run()

    def test_encrypts_and_returns_ansible_result(self, action_module, files):
        """Test a valid run.

        GIVEN an archive and a public key
        WHEN the plugin runs
        THEN a .tar.gz.enc and sidecar exist and every documented result field is returned.
        """
        archive, pub = files
        result = self.run(action_module, archive, pub)
        enc_path = str(archive) + ".enc"
        assert result["changed"] is True and result["failed"] is False
        assert result["encrypted_archive_path"] == enc_path and enc_path.endswith(".tar.gz.enc")
        assert result["encrypted_archive_size"] == os.path.getsize(enc_path)
        assert result["encrypted_archive_sha256"] == hashlib.sha256(open(enc_path, "rb").read()).hexdigest()
        assert result["encrypted_archive_checksum_file"] == enc_path + ".sha256"
        assert os.path.isfile(enc_path + ".sha256")
        assert result["encryption_algorithm"] == "AES-256-GCM"
        assert result["key_encapsulation_algorithm"] == "ML-KEM-768"
        assert result["key_derivation_algorithm"] == "HKDF-SHA256"
        assert os.path.exists(archive)
        assert stat.S_IMODE(os.stat(enc_path).st_mode) == 0o600

    def test_result_never_contains_key_material(self, action_module, files):
        """GIVEN a run THEN the returned result does not contain the key file content."""
        archive, pub = files
        assert "BEGIN PUBLIC KEY" not in repr(self.run(action_module, archive, pub))

    @pytest.mark.parametrize("missing", ["archive_path", "public_key_path", "output_path"])
    def test_missing_arguments_rejected(self, action_module, files, missing):
        """GIVEN a missing required argument THEN AnsibleError is raised."""
        archive, pub = files
        action_module._task.args = {"archive_path": str(archive), "public_key_path": str(pub), "output_path": str(archive) + ".enc"}
        del action_module._task.args[missing]
        with pytest.raises(AnsibleError):
            action_module.run()

    def test_missing_archive_rejected(self, action_module, files, tmp_path):
        """GIVEN a missing archive THEN AnsibleError names it."""
        _, pub = files
        with pytest.raises(AnsibleError, match="does-not-exist"):
            self.run(action_module, tmp_path / "does-not-exist.tar.gz", pub)

    def test_missing_public_key_gives_useful_error(self, action_module, files, tmp_path):
        """GIVEN a missing public key THEN AnsibleError names the file and no output exists."""
        archive, _ = files
        with pytest.raises(AnsibleError, match="no-key.pem"):
            self.run(action_module, archive, tmp_path / "no-key.pem")
        assert not os.path.exists(str(archive) + ".enc")

    def test_output_must_end_with_tar_gz_enc(self, action_module, files):
        """GIVEN an output path with another extension THEN AnsibleError is raised."""
        archive, pub = files
        with pytest.raises(AnsibleError, match=r"\.tar\.gz\.enc"):
            self.run(action_module, archive, pub, output=str(archive) + ".bin")

    def test_existing_output_is_not_overwritten(self, action_module, files):
        """GIVEN an existing encrypted output THEN AnsibleError is raised and the file is unchanged."""
        archive, pub = files
        out = str(archive) + ".enc"
        open(out, "wb").write(b"keep")
        with pytest.raises(AnsibleError, match="refusing to overwrite"):
            self.run(action_module, archive, pub)
        assert open(out, "rb").read() == b"keep"

    def test_unsupported_openssl_gives_useful_error(self, action_module, files, fakeOpenSsl):
        """GIVEN an OpenSSL without ML-KEM-768 THEN AnsibleError explains the requirement and nothing is written."""
        archive, pub = files
        fakeOpenSsl.supportsMlKem = False
        with pytest.raises(AnsibleError, match="ML-KEM-768.*OpenSSL 3.5"):
            self.run(action_module, archive, pub)
        assert not os.path.exists(str(archive) + ".enc")

    def test_missing_cryptography_gives_clear_diagnostic(self, action_module, files, monkeypatch):
        """GIVEN no cryptography package THEN AnsibleError says how to install it."""
        archive, pub = files
        monkeypatch.setattr(enc, "CRYPTOGRAPHY_IMPORT_ERROR", ImportError("No module named 'cryptography'"))
        with pytest.raises(AnsibleError, match="cryptography.*pip install"):
            self.run(action_module, archive, pub)

    def test_output_decrypts_with_matching_key(self, action_module, files, tmp_path):
        """GIVEN a plugin-produced file THEN decryptArchive restores identical bytes."""
        archive, pub = files
        result = self.run(action_module, archive, pub)
        priv = tmp_path / "private.pem"
        priv.write_text("-----BEGIN PRIVATE KEY-----\nid=x\n-----END PRIVATE KEY-----\n")
        restored = enc.decryptArchive(result["encrypted_archive_path"], str(priv), str(tmp_path / "restored.tar.gz"))
        assert open(restored["path"], "rb").read() == open(archive, "rb").read()
