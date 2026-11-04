"""Unit tests for the package_saas_backup action plugin."""

import hashlib
import json
import os
import stat
import tarfile

import pytest
from ansible.errors import AnsibleError

import package_saas_backup

ActionModule = package_saas_backup.ActionModule

PEM_KEY = b"-----BEGIN RSA PRIVATE KEY-----\nabc\n-----END RSA PRIVATE KEY-----\n"


def sha256Bytes(data: bytes) -> str:
    """Return the SHA-256 hex digest of bytes."""
    return hashlib.sha256(data).hexdigest()


class TestPackageSaasBackup:
    """Test cases for package_saas_backup."""

    @pytest.fixture
    def action_module(self, action_module_base):
        """Create ActionModule instance."""
        return ActionModule(**action_module_base)

    @pytest.fixture
    def staging(self, tmp_path):
        """Create a staging directory with a few files and a separate output directory."""
        stagingDir = tmp_path / "work" / "saas-backup-test"
        (stagingDir / "openshift" / "inst1").mkdir(parents=True)
        (stagingDir / "openshift" / "inst1" / "suite.yaml").write_text("kind: Suite\n")
        (stagingDir / "saas-envs").mkdir()
        (stagingDir / "saas-envs" / "params.yaml").write_text("a: 1\n")
        (tmp_path / "out").mkdir()
        return stagingDir

    def run(self, module, staging, tmp_path, metadata=None, archiveName="backup.tar.gz"):
        """Run the plugin with default arguments."""
        module._task.args = {
            "staging_dir": str(staging),
            "archive_path": str(tmp_path / "out" / archiveName),
            "metadata": metadata if metadata is not None else {"region": "us-east-2", "instances": ["inst1"]},
        }
        return module.run()

    def test_creates_single_archive_with_metadata_and_checksums(self, action_module, staging, tmp_path):
        """Test that one archive containing metadata.json and SHA256SUMS is produced.

        GIVEN a staging directory with collected files
        WHEN the plugin runs
        THEN one tar.gz exists whose top level directory contains the files, metadata.json and SHA256SUMS.
        """
        result = self.run(action_module, staging, tmp_path)

        assert result["failed"] is False
        assert result["file_count"] == 4
        with tarfile.open(result["archive_path"], "r:gz") as tar:
            names = sorted(m.name for m in tar.getmembers() if m.isreg())
        assert names == [
            "saas-backup-test/SHA256SUMS",
            "saas-backup-test/metadata.json",
            "saas-backup-test/openshift/inst1/suite.yaml",
            "saas-backup-test/saas-envs/params.yaml",
        ]
        assert [p.name for p in (tmp_path / "out").iterdir() if p.is_file()].count("backup.tar.gz") == 1

    def test_checksums_describe_final_archive_contents(self, action_module, staging, tmp_path):
        """Test that SHA256SUMS and metadata.json match the archived bytes.

        GIVEN a successful run
        WHEN the archive is read back
        THEN every SHA256SUMS line matches the member, metadata lists the same hashes and SHA256SUMS does not list itself.
        """
        result = self.run(action_module, staging, tmp_path)

        with tarfile.open(result["archive_path"], "r:gz") as tar:
            sums = tar.extractfile("saas-backup-test/SHA256SUMS").read().decode()
            metadata = json.loads(tar.extractfile("saas-backup-test/metadata.json").read())
            listed = {line.split("  ", 1)[1]: line.split("  ", 1)[0] for line in sums.splitlines()}
            assert "SHA256SUMS" not in listed
            assert set(listed) == {"metadata.json", "openshift/inst1/suite.yaml", "saas-envs/params.yaml"}
            for path, digest in listed.items():
                assert sha256Bytes(tar.extractfile(f"saas-backup-test/{path}").read()) == digest
        metaFiles = {f["path"]: f["sha256"] for f in metadata["package"]["files"]}
        assert metaFiles == {p: d for p, d in listed.items() if p != "metadata.json"}
        assert metadata["region"] == "us-east-2"
        assert metadata["package"]["file_count"] == 2

    def test_archive_checksum_is_written_outside_the_archive(self, action_module, staging, tmp_path):
        """Test that the archive checksum is a sidecar and matches the archive.

        GIVEN a successful run
        WHEN the sidecar is read
        THEN it holds the SHA-256 of the archive file and is not inside the archive.
        """
        result = self.run(action_module, staging, tmp_path)

        sidecar = (tmp_path / "out" / "backup.tar.gz.sha256").read_text()
        archiveBytes = (tmp_path / "out" / "backup.tar.gz").read_bytes()
        assert sidecar == f"{sha256Bytes(archiveBytes)}  backup.tar.gz\n"
        assert result["archive_sha256"] == sha256Bytes(archiveBytes)
        with tarfile.open(result["archive_path"], "r:gz") as tar:
            assert not any(m.name.endswith(".sha256") for m in tar.getmembers())

    def test_files_and_archive_are_owner_only(self, action_module, staging, tmp_path):
        """Test restrictive permissions on the archive and its members.

        GIVEN a successful run
        WHEN permissions are inspected
        THEN the archive and sidecar are 0600 and no member grants group or other access.
        """
        result = self.run(action_module, staging, tmp_path)

        assert stat.S_IMODE(os.stat(result["archive_path"]).st_mode) == 0o600
        assert stat.S_IMODE(os.stat(result["archive_checksum_file"]).st_mode) == 0o600
        with tarfile.open(result["archive_path"], "r:gz") as tar:
            for member in tar.getmembers():
                assert member.mode & 0o077 == 0, member.name
                assert member.uid == 0 and member.uname == ""

    def test_plaintext_private_keys_are_flagged_in_metadata(self, action_module, staging, tmp_path):
        """Test that files containing a PEM private key are reported.

        GIVEN a staged file containing a PEM private key
        WHEN the plugin runs
        THEN metadata.json lists it under plaintext_private_key_files and no other file.
        """
        (staging / "saas-envs" / "tls.key").write_bytes(PEM_KEY)
        result = self.run(action_module, staging, tmp_path)

        with tarfile.open(result["archive_path"], "r:gz") as tar:
            metadata = json.loads(tar.extractfile("saas-backup-test/metadata.json").read())
        assert metadata["package"]["plaintext_private_key_files"] == ["saas-envs/tls.key"]

    def test_symlink_is_rejected(self, action_module, staging, tmp_path):
        """Test that symlinks are never packaged.

        GIVEN a staging directory with a symlink to a file outside it
        WHEN the plugin runs
        THEN it fails and no archive is left behind.
        """
        outside = tmp_path / "secret.txt"
        outside.write_text("secret")
        os.symlink(outside, staging / "link.txt")

        with pytest.raises(AnsibleError, match="symlink"):
            self.run(action_module, staging, tmp_path)

        assert not (tmp_path / "out" / "backup.tar.gz").exists()

    def test_existing_archive_is_not_overwritten(self, action_module, staging, tmp_path):
        """Test that an existing archive is refused.

        GIVEN an archive path that already exists
        WHEN the plugin runs
        THEN it fails and leaves the existing file unchanged.
        """
        existing = tmp_path / "out" / "backup.tar.gz"
        existing.write_text("keep")

        with pytest.raises(AnsibleError, match="already exists"):
            self.run(action_module, staging, tmp_path)

        assert existing.read_text() == "keep"

    @pytest.mark.parametrize("reserved", ["metadata.json", "SHA256SUMS"])
    def test_reserved_files_in_staging_are_rejected(self, action_module, staging, tmp_path, reserved):
        """Test that staged files cannot masquerade as the manifest or checksums.

        GIVEN a staging directory that already has a reserved file
        WHEN the plugin runs
        THEN it fails.
        """
        (staging / reserved).write_text("fake")

        with pytest.raises(AnsibleError, match="reserved file"):
            self.run(action_module, staging, tmp_path)

    def test_empty_staging_is_rejected(self, action_module, tmp_path):
        """Test that nothing is packaged when no files were collected.

        GIVEN an empty staging directory
        WHEN the plugin runs
        THEN it fails instead of producing an empty backup.
        """
        emptyDir = tmp_path / "empty"
        emptyDir.mkdir()
        (tmp_path / "out").mkdir()

        with pytest.raises(AnsibleError, match="nothing to package"):
            self.run(action_module, emptyDir, tmp_path)

    def test_archive_path_inside_staging_is_rejected(self, action_module, staging):
        """Test that the archive cannot be written inside the directory being archived.

        GIVEN an archive path below staging_dir
        WHEN the plugin runs
        THEN it fails.
        """
        action_module._task.args = {"staging_dir": str(staging), "archive_path": str(staging / "x.tar.gz"), "metadata": {}}

        with pytest.raises(AnsibleError, match="must not be inside"):
            action_module.run()

    def test_invalid_arguments_are_rejected(self, action_module, staging, tmp_path):
        """Test argument validation.

        GIVEN a missing staging dir, a non tar.gz name, or non dictionary metadata
        WHEN the plugin runs
        THEN each case fails with a clear error.
        """
        archive = str(tmp_path / "x.tar.gz")
        cases = [
            ({"staging_dir": str(tmp_path / "missing"), "archive_path": archive, "metadata": {}}, "existing directory"),
            ({"staging_dir": str(staging), "archive_path": str(tmp_path / "x.zip"), "metadata": {}}, r"\.tar\.gz"),
            ({"staging_dir": str(staging), "archive_path": archive, "metadata": "text"}, "dictionary"),
        ]
        for args, message in cases:
            action_module._task.args = args
            with pytest.raises(AnsibleError, match=message):
                action_module.run()
