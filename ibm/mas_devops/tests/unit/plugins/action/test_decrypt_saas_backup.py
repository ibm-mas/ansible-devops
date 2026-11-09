"""Unit tests for the decrypt_saas_backup action plugin.

Real encrypted archives are produced with ``encryptArchive`` and the OpenSSL subprocess boundary is replaced by a fake, so these
tests need neither an ML-KEM capable OpenSSL nor a cluster.
"""

import hashlib
import io
import json
import os
import stat
import subprocess
import sys
import tarfile

import pytest
from ansible.errors import AnsibleError

import decrypt_saas_backup

ActionModule = decrypt_saas_backup.ActionModule

# The same module object the plugin uses (registered under its collection path by conftest.py)
enc = sys.modules["ansible_collections.ibm.mas_devops.plugins.module_utils.saas_backup_encryption"]

TS = "20261109T152831Z"
TOP = f"saas-backup-acc-reg-cl-{TS}"
SUITE_DIR = f"openshift/inst01/backup-{TS}-suite"
MANAGE_DIR = f"openshift/inst01/backup-{TS}-app-manage"


def keyId(content):
    """Return the id embedded in a fake key file ("id=<name>")."""
    return content.split("id=")[1].split()[0]


class FakeOpenSsl:
    """Minimal fake of the OpenSSL CLI. The shared secret depends on the key id, so a different private key cannot decapsulate."""

    def __init__(self):
        self.calls = []

    def __call__(self, opensslPath, args):
        self.calls.append(list(args))

        def result(rc=0, out="", err=""):
            return subprocess.CompletedProcess([opensslPath] + args, rc, out, err)

        if args == ["version"]:
            return result(out="OpenSSL fake\n")
        if args == ["list", "-kem-algorithms"]:
            return result(out="  ML-KEM-768 @ default\n")
        if args == ["pkeyutl", "-help"]:
            return result(err=" -encap\n -decap\n")
        if args[0] == "pkey":
            return result(out="ML-KEM-768 Public-Key:\n") if "id=" in open(args[args.index("-in") + 1]).read() else result(rc=1, err="bad key")
        if args[:2] == ["pkeyutl", "-encap"]:
            ident = keyId(open(args[args.index("-inkey") + 1]).read())
            kem = os.urandom(enc.KEM_CIPHERTEXT_SIZE)
            open(args[args.index("-out") + 1], "wb").write(kem)
            open(args[args.index("-secret") + 1], "wb").write(hashlib.sha256(ident.encode() + kem).digest())
            return result()
        if args[:2] == ["pkeyutl", "-decap"]:
            ident = keyId(open(args[args.index("-inkey") + 1]).read())
            kem = open(args[args.index("-in") + 1], "rb").read()
            open(args[args.index("-secret") + 1], "wb").write(hashlib.sha256(ident.encode() + kem).digest())
            return result()
        return result(rc=1, err="unexpected")


def sha(data):
    """SHA-256 hex digest of bytes."""
    return hashlib.sha256(data).hexdigest()


BASE_FILES = {
    f"{SUITE_DIR}/resources/projects/p.yaml": b"kind: Project\n",
    f"{MANAGE_DIR}/resources/manageapps/m.yaml": b"kind: ManageApp\n",
    "saas-envs/gitops/acc/reg/cl/inst01/params.yaml": b"a: 1\n",
}


def baseMetadata(files):
    """Build metadata.json content consistent with the given files."""
    return {
        "backup_type": "saas-named-resources",
        "created_utc": TS,
        "account": "acc",
        "region": "reg",
        "cluster": "cl",
        "cluster_api_server": "https://api.cl.example.com:6443",
        "instances": ["inst01"],
        "instance_details": [
            {
                "instance_id": "inst01",
                "workspace_id": "main",
                "applications_backed_up": ["core", "manage"],
                "versions": {"suite_reconciled": "9.2.9"},
                "openshift": {"suite": {"backup_path": SUITE_DIR}, "manage": {"backup_path": MANAGE_DIR}},
            }
        ],
        "repositories": {},
        "scope": {"restore_included": False},
        "warnings": ["w1"],
        "package": {
            "archive_top_level_directory": TOP,
            "files": [{"path": p, "size": len(b), "sha256": sha(b)} for p, b in sorted(files.items())],
        },
    }


def buildMembers(metadataEdit=None, postEdit=None, noManifest=False):
    """Build the archive members (name -> bytes, or ("symlink", target)) of a valid backup, with optional damage."""
    files = dict(BASE_FILES)
    meta = baseMetadata(files)
    if metadataEdit:
        metadataEdit(meta)
    metaBytes = json.dumps(meta).encode()
    sums = {p: sha(b) for p, b in files.items()}
    sums["metadata.json"] = sha(metaBytes)
    members = {f"{TOP}/{p}": b for p, b in files.items()}
    members[f"{TOP}/metadata.json"] = metaBytes
    if not noManifest:
        members[f"{TOP}/SHA256SUMS"] = "".join(f"{d}  {p}\n" for p, d in sorted(sums.items())).encode()
    if postEdit:
        postEdit(members)
    return members


def writeTarGz(path, members):
    """Write members to a .tar.gz."""
    with tarfile.open(path, "w:gz") as tar:
        for name, data in members.items():
            info = tarfile.TarInfo(name)
            if isinstance(data, tuple):
                info.type = tarfile.SYMTYPE
                info.linkname = data[1]
                tar.addfile(info)
            else:
                info.size = len(data)
                tar.addfile(info, io.BytesIO(data))


def rewriteSidecar(encPath):
    """Rewrite the .sha256 sidecar so that it matches the current file content."""
    with open(encPath + ".sha256", "w") as f:
        f.write(f"{enc.sha256File(encPath)}  {os.path.basename(encPath)}\n")


class TestDecryptSaasBackup:
    """Test cases for decrypt_saas_backup."""

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
    def env(self, tmp_path):
        """Create keys and the source, backup and output directories."""
        for name in ("src", "backup", "out", "keys"):
            (tmp_path / name).mkdir()
        keys = tmp_path / "keys"
        (keys / "public.pem").write_text("-----BEGIN PUBLIC KEY-----\nid=alpha\n-----END PUBLIC KEY-----\n")
        (keys / "private.pem").write_text("-----BEGIN PRIVATE KEY-----\nid=alpha\n-----END PRIVATE KEY-----\n")
        (keys / "other.pem").write_text("-----BEGIN PRIVATE KEY-----\nid=beta\n-----END PRIVATE KEY-----\n")
        return {
            "root": tmp_path,
            "public": str(keys / "public.pem"),
            "private": str(keys / "private.pem"),
            "other": str(keys / "other.pem"),
            "out": str(tmp_path / "out"),
        }

    @pytest.fixture
    def makeEncrypted(self, env):
        """Return a factory that encrypts a package built from members (or arbitrary bytes) into backup/."""

        def make(members=None, rawBytes=None):
            plain = env["root"] / "src" / f"{TOP}.tar.gz"
            if rawBytes is not None:
                plain.write_bytes(rawBytes)
            else:
                writeTarGz(str(plain), members if members is not None else buildMembers())
            encPath = str(env["root"] / "backup" / f"{TOP}.tar.gz.enc")
            enc.encryptArchive(str(plain), env["public"], encPath)
            return encPath

        return make

    def run(self, module, env, encPath, **overrides):
        """Run the plugin."""
        args = {"encrypted_archive_path": encPath, "private_key_path": env["private"], "output_dir": env["out"]}
        args.update(overrides)
        module._task.args = args
        return module.run()

    @staticmethod
    def runAbsent(module, workDir):
        """Run the plugin with state=absent."""
        module._task.args = {"state": "absent", "work_dir": workDir}
        return module.run()

    @staticmethod
    def snapshot(encPath):
        """Return the bytes of the encrypted archive and its sidecar."""
        return open(encPath, "rb").read(), open(encPath + ".sha256", "rb").read()

    # --- success -------------------------------------------------------------------------------------------------

    def test_successful_decrypt_only(self, action_module, env, makeEncrypted):
        """Test a valid decrypt-only run.

        GIVEN a valid encrypted backup and its private key
        WHEN the plugin runs without extract
        THEN integrity and authentication are reported verified, the metadata is summarised, and no plaintext remains.
        """
        encPath = makeEncrypted()
        before = self.snapshot(encPath)
        result = self.run(action_module, env, encPath)

        assert result["failed"] is False and result["changed"] is False
        assert result["integrity_verified"] is True and result["authentication_verified"] is True
        assert result["encrypted_archive_sha256"] == enc.sha256File(encPath)
        assert result["manifest_file_count"] == 4
        summary = result["backup_metadata"]
        assert summary["cluster"] == "cl" and summary["instances"] == ["inst01"] and summary["created_utc"] == TS
        assert summary["cluster_api_server"] == "https://api.cl.example.com:6443"
        detail = summary["instance_details"][0]
        assert detail["suite_backup_path"] == SUITE_DIR and detail["manage_backup_path"] == MANAGE_DIR
        assert result["contents"]["files_by_section"] == {"(root)": 2, "openshift": 2, "saas-envs": 1}
        assert result["work_dir"] == "" and result["extract_root"] == ""
        assert self.snapshot(encPath) == before
        assert os.listdir(env["out"]) == []

    def test_result_never_contains_key_material(self, action_module, env, makeEncrypted):
        """GIVEN a run THEN neither the private key content nor the key itself appear in the result."""
        text = repr(self.run(action_module, env, makeEncrypted()))
        assert "PRIVATE KEY" not in text and "id=alpha" not in text

    def test_extract_keeps_private_work_dir_until_removed(self, action_module, env, makeEncrypted):
        """Test extraction for a full restore.

        GIVEN extract=true
        WHEN the plugin runs and later runs with state=absent
        THEN the validated archive is extracted into a 0700 work dir which is then removed on request.
        """
        encPath = makeEncrypted()
        result = self.run(action_module, env, encPath, extract=True)
        workDir = result["work_dir"]
        suiteFile = os.path.join(result["extract_root"], SUITE_DIR, "resources", "projects", "p.yaml")

        assert result["changed"] is True
        assert os.path.dirname(workDir) == env["out"] and os.path.basename(workDir).startswith("saas-restore-")
        assert stat.S_IMODE(os.stat(workDir).st_mode) == 0o700
        assert result["extract_root"] == os.path.join(workDir, "extracted", TOP)
        assert open(suiteFile, "rb").read() == b"kind: Project\n"
        assert stat.S_IMODE(os.stat(suiteFile).st_mode) == 0o600

        removed = self.runAbsent(action_module, workDir)
        assert removed["changed"] is True and not os.path.exists(workDir)
        assert os.listdir(env["out"]) == []

    # --- cryptographic failures ----------------------------------------------------------------------------------

    def test_wrong_private_key_is_rejected(self, action_module, env, makeEncrypted):
        """GIVEN a private key that does not match THEN decryption fails authentication, nothing is published and nothing is left behind."""
        encPath = makeEncrypted()
        before = self.snapshot(encPath)
        with pytest.raises(AnsibleError, match="Authentication failed"):
            self.run(action_module, env, encPath, private_key_path=env["other"])
        assert os.listdir(env["out"]) == [] and self.snapshot(encPath) == before

    def test_public_key_is_rejected_as_private_key(self, action_module, env, makeEncrypted):
        """GIVEN the public key as private key THEN the run fails."""
        with pytest.raises(AnsibleError, match="private key"):
            self.run(action_module, env, makeEncrypted(), private_key_path=env["public"])

    def test_tampered_payload_is_rejected(self, action_module, env, makeEncrypted):
        """GIVEN a modified ciphertext byte (with a matching sidecar) THEN AES-GCM authentication fails."""
        encPath = makeEncrypted()
        raw = bytearray(open(encPath, "rb").read())
        raw[-enc.TAG_SIZE - 5] ^= 0xFF
        open(encPath, "wb").write(raw)
        rewriteSidecar(encPath)
        with pytest.raises(AnsibleError, match="Authentication failed"):
            self.run(action_module, env, encPath)
        assert os.listdir(env["out"]) == []

    def test_tampered_tag_is_rejected(self, action_module, env, makeEncrypted):
        """GIVEN a modified authentication tag (with a matching sidecar) THEN AES-GCM authentication fails."""
        encPath = makeEncrypted()
        raw = bytearray(open(encPath, "rb").read())
        raw[-1] ^= 0x01
        open(encPath, "wb").write(raw)
        rewriteSidecar(encPath)
        with pytest.raises(AnsibleError, match="Authentication failed"):
            self.run(action_module, env, encPath)

    def test_tampered_header_is_rejected(self, action_module, env, makeEncrypted):
        """GIVEN a modified header (with a matching sidecar) THEN decryption fails and nothing is published."""
        encPath = makeEncrypted()
        raw = bytearray(open(encPath, "rb").read())
        raw[len(enc.MAGIC) + enc.LENGTH_PREFIX_SIZE + 5] ^= 0x01
        open(encPath, "wb").write(raw)
        rewriteSidecar(encPath)
        with pytest.raises(AnsibleError, match="Backup decryption failed"):
            self.run(action_module, env, encPath)
        assert os.listdir(env["out"]) == []

    # --- checksum failures ---------------------------------------------------------------------------------------

    def test_sidecar_mismatch_is_rejected_before_decryption(self, action_module, env, makeEncrypted, fakeOpenSsl):
        """GIVEN a modified archive but an unchanged sidecar THEN the run fails on the checksum without touching OpenSSL."""
        encPath = makeEncrypted()
        raw = bytearray(open(encPath, "rb").read())
        raw[-20] ^= 0xFF
        open(encPath, "wb").write(raw)
        fakeOpenSsl.calls.clear()
        with pytest.raises(AnsibleError, match="checksum mismatch"):
            self.run(action_module, env, encPath)
        assert fakeOpenSsl.calls == [] and os.listdir(env["out"]) == []

    def test_missing_sidecar_is_rejected(self, action_module, env, makeEncrypted):
        """GIVEN no sidecar THEN the run refuses to decrypt."""
        encPath = makeEncrypted()
        os.unlink(encPath + ".sha256")
        with pytest.raises(AnsibleError, match="sidecar.*missing"):
            self.run(action_module, env, encPath)

    @pytest.mark.parametrize("content", ["", "not-a-digest  file\n", "abc\n", "a" * 63 + "\n", ("a" * 64 + "\n") * 2])
    def test_malformed_sidecar_is_rejected(self, action_module, env, makeEncrypted, content):
        """GIVEN a malformed sidecar THEN the run fails."""
        encPath = makeEncrypted()
        open(encPath + ".sha256", "w").write(content)
        with pytest.raises(AnsibleError, match="malformed"):
            self.run(action_module, env, encPath)

    # --- format failures -----------------------------------------------------------------------------------------

    def test_invalid_archive_format_is_rejected(self, action_module, env, makeEncrypted):
        """GIVEN a file that is not a SaaS backup encrypted file (correct sidecar) THEN the magic bytes are rejected."""
        encPath = makeEncrypted()
        open(encPath, "wb").write(b"NOTSAAS!" + os.urandom(2048))
        rewriteSidecar(encPath)
        with pytest.raises(AnsibleError, match="invalid magic bytes"):
            self.run(action_module, env, encPath)
        assert os.listdir(env["out"]) == []

    @pytest.mark.parametrize("cut", [0, 5, 10, 100, 1000, "half"])
    def test_truncated_encrypted_archive_is_rejected(self, action_module, env, makeEncrypted, cut):
        """GIVEN a truncated encrypted archive (with a matching sidecar) THEN the run fails and nothing is published."""
        encPath = makeEncrypted()
        raw = open(encPath, "rb").read()
        open(encPath, "wb").write(raw[: len(raw) // 2 if cut == "half" else cut])
        rewriteSidecar(encPath)
        with pytest.raises(AnsibleError, match="Backup decryption failed"):
            self.run(action_module, env, encPath)
        assert os.listdir(env["out"]) == []

    def test_decrypted_data_that_is_not_a_tar_gz_is_rejected(self, action_module, env, makeEncrypted):
        """GIVEN valid encryption of data that is not a tar.gz THEN the content validation rejects it."""
        with pytest.raises(AnsibleError, match="not a valid .tar.gz"):
            self.run(action_module, env, makeEncrypted(rawBytes=b"plain text, not an archive" * 100))
        assert os.listdir(env["out"]) == []

    # --- manifest and structure failures -------------------------------------------------------------------------

    @staticmethod
    def tamperFile(members):
        members[f"{TOP}/{SUITE_DIR}/resources/projects/p.yaml"] = b"kind: Evil\n"

    @staticmethod
    def addUnlisted(members):
        members[f"{TOP}/extra.txt"] = b"unlisted"

    @staticmethod
    def dropListed(members):
        del members[f"{TOP}/saas-envs/gitops/acc/reg/cl/inst01/params.yaml"]

    @staticmethod
    def tamperMetadata(members):
        members[f"{TOP}/metadata.json"] = members[f"{TOP}/metadata.json"].replace(b"inst01", b"inst02")

    @staticmethod
    def addSymlink(members):
        members[f"{TOP}/link"] = ("symlink", "/etc/passwd")

    @staticmethod
    def addTraversal(members):
        members[f"{TOP}/../escape.txt"] = b"x"

    @staticmethod
    def addSecondTop(members):
        members["other-top/file.txt"] = b"x"

    @pytest.mark.parametrize(
        "postEdit,noManifest,message",
        [
            ("tamperFile", False, "Checksum mismatch against SHA256SUMS"),
            ("addUnlisted", False, "not covered by SHA256SUMS"),
            ("dropListed", False, "missing from the archive"),
            ("tamperMetadata", False, "Checksum mismatch against SHA256SUMS"),
            ("addSymlink", False, "non-regular"),
            ("addTraversal", False, "Unsafe archive member"),
            ("addSecondTop", False, "more than one top level"),
            (None, True, "does not contain SHA256SUMS"),
        ],
    )
    def test_manifest_and_structure_failures_are_rejected(self, action_module, env, makeEncrypted, postEdit, noManifest, message):
        """GIVEN an authentic encrypted archive whose contents are inconsistent THEN the SHA256SUMS validation rejects it."""
        edit = getattr(self, postEdit) if postEdit else None
        encPath = makeEncrypted(buildMembers(postEdit=edit, noManifest=noManifest))
        with pytest.raises(AnsibleError, match=message):
            self.run(action_module, env, encPath, extract=True)
        assert os.listdir(env["out"]) == []

    @pytest.mark.parametrize(
        "edit,message",
        [
            (lambda m: m.update(instances=["inst01", "inst02"]), "does not cover every instance"),
            (lambda m: m.update(instance_details=[]), "does not cover every instance"),
            (lambda m: m["package"].update(archive_top_level_directory="other"), "does not describe this archive"),
            (lambda m: m["package"].update(files=[]), "does not match SHA256SUMS"),
            (lambda m: m.update(created_utc="yesterday"), "created_utc"),
            (lambda m: m.update(cluster="bad cluster!"), "cluster"),
            (lambda m: m["instance_details"][0]["openshift"]["suite"].update(backup_path="../../etc"), "unexpected suite backup path"),
            (lambda m: m["instance_details"][0]["openshift"].pop("suite"), "no Suite backup"),
        ],
    )
    def test_inconsistent_metadata_is_rejected(self, action_module, env, makeEncrypted, edit, message):
        """GIVEN a self-consistent manifest but inconsistent metadata.json THEN the run fails and nothing is extracted."""
        encPath = makeEncrypted(buildMembers(metadataEdit=edit))
        with pytest.raises(AnsibleError, match=message):
            self.run(action_module, env, encPath, extract=True)
        assert os.listdir(env["out"]) == []

    # --- overwrite prevention and cleanup ------------------------------------------------------------------------

    def test_existing_output_file_is_not_overwritten(self, action_module, env, makeEncrypted, monkeypatch):
        """GIVEN a decrypted output path that already exists THEN the run refuses and the existing file is untouched."""
        encPath = makeEncrypted()
        seen = {}
        originalCreate = decrypt_saas_backup.createWorkDir
        originalRemove = decrypt_saas_backup.removeSecureTempDir

        def createWithPlantedOutput(parent):
            workDir = originalCreate(parent)
            seen["path"] = os.path.join(workDir, os.path.basename(encPath)[: -len(".enc")])
            open(seen["path"], "wb").write(b"keep me")
            return workDir

        def removeSpy(path):
            seen["content_at_cleanup"] = open(seen["path"], "rb").read()
            originalRemove(path)

        monkeypatch.setattr(decrypt_saas_backup, "createWorkDir", createWithPlantedOutput)
        monkeypatch.setattr(decrypt_saas_backup, "removeSecureTempDir", removeSpy)

        with pytest.raises(AnsibleError, match="refusing to overwrite"):
            self.run(action_module, env, encPath)
        assert seen["content_at_cleanup"] == b"keep me"
        assert os.listdir(env["out"]) == []

    def test_no_temporary_files_remain_after_success_or_failure(self, action_module, env, makeEncrypted, monkeypatch):
        """Test temporary file cleanup.

        GIVEN runs that succeed, fail authentication and fail content validation
        WHEN each run ends
        THEN the output directory is empty and every OpenSSL shared secret file is gone.
        """
        secrets = []
        fake = enc.runOpenSsl

        def spy(opensslPath, args):
            if "-secret" in args:
                secrets.append(args[args.index("-secret") + 1])
            return fake(opensslPath, args)

        monkeypatch.setattr(enc, "runOpenSsl", spy)
        good = makeEncrypted()
        self.run(action_module, env, good)
        with pytest.raises(AnsibleError):
            self.run(action_module, env, good, private_key_path=env["other"])
        os.unlink(good)
        os.unlink(good + ".sha256")
        bad = makeEncrypted(buildMembers(postEdit=self.tamperFile))
        with pytest.raises(AnsibleError):
            self.run(action_module, env, bad, extract=True)

        assert os.listdir(env["out"]) == []
        assert secrets and not any(os.path.exists(path) for path in secrets)

    def test_failed_validation_after_decryption_zero_fills_and_removes_plaintext(self, action_module, env, makeEncrypted, monkeypatch):
        """GIVEN a failure after the plaintext was written THEN the plaintext is zero-filled and removed."""
        removed = []
        original = decrypt_saas_backup.removeSecureTempDir

        def spy(path):
            removed.append(sorted(os.listdir(path)))
            original(path)

        monkeypatch.setattr(decrypt_saas_backup, "removeSecureTempDir", spy)
        with pytest.raises(AnsibleError):
            self.run(action_module, env, makeEncrypted(buildMembers(postEdit=self.tamperFile)))
        assert removed == [[f"{TOP}.tar.gz"]]
        assert os.listdir(env["out"]) == []

    # --- argument validation and work directory removal ---------------------------------------------------------

    @pytest.mark.parametrize("missing", ["encrypted_archive_path", "private_key_path"])
    def test_missing_arguments_rejected(self, action_module, env, makeEncrypted, missing):
        """GIVEN a missing required argument THEN AnsibleError is raised."""
        args = {"encrypted_archive_path": makeEncrypted(), "private_key_path": env["private"]}
        del args[missing]
        action_module._task.args = args
        with pytest.raises(AnsibleError):
            action_module.run()

    def test_archive_must_end_with_tar_gz_enc(self, action_module, env):
        """GIVEN another extension THEN AnsibleError is raised."""
        path = env["root"] / "backup" / "x.bin"
        path.write_bytes(b"x")
        with pytest.raises(AnsibleError, match=r"\.tar\.gz\.enc"):
            self.run(action_module, env, str(path))

    def test_missing_private_key_file_rejected(self, action_module, env, makeEncrypted):
        """GIVEN a missing private key file THEN AnsibleError is raised."""
        with pytest.raises(AnsibleError, match="private_key_path"):
            self.run(action_module, env, makeEncrypted(), private_key_path=str(env["root"] / "none.pem"))

    def test_output_dir_must_exist(self, action_module, env, makeEncrypted):
        """GIVEN a missing output directory THEN AnsibleError is raised."""
        with pytest.raises(AnsibleError, match="output_dir"):
            self.run(action_module, env, makeEncrypted(), output_dir=str(env["root"] / "missing"))

    def test_unsupported_openssl_gives_useful_error(self, action_module, env, makeEncrypted, monkeypatch):
        """GIVEN an OpenSSL without ML-KEM-768 THEN AnsibleError explains the requirement and nothing is left behind."""
        encPath = makeEncrypted()
        monkeypatch.setattr(enc, "runOpenSsl", lambda path, args: subprocess.CompletedProcess([path] + args, 0, "  X25519\n", ""))
        with pytest.raises(AnsibleError, match="ML-KEM-768.*OpenSSL 3.5"):
            self.run(action_module, env, encPath)
        assert os.listdir(env["out"]) == []

    def test_state_absent_refuses_unsafe_paths(self, action_module, tmp_path):
        """GIVEN paths that were not created by this plugin THEN state=absent refuses to remove them."""
        other = tmp_path / "important"
        other.mkdir(mode=0o700)
        loose = tmp_path / "saas-restore-loose"
        loose.mkdir(mode=0o755)
        link = tmp_path / "saas-restore-link"
        link.symlink_to(other)

        cases = ((str(other), "not a saas-restore-"), (str(loose), "not private"), (str(link), "not a saas-restore-"), ("relative", "absolute"))
        for path, message in cases:
            with pytest.raises(AnsibleError, match=message):
                self.runAbsent(action_module, path)
        assert other.exists() and loose.exists()

    def test_state_absent_is_idempotent(self, action_module, tmp_path):
        """GIVEN an already removed work directory THEN state=absent reports no change."""
        assert self.runAbsent(action_module, str(tmp_path / "saas-restore-gone"))["changed"] is False

    def test_invalid_state_rejected(self, action_module):
        """GIVEN an unknown state THEN AnsibleError is raised."""
        action_module._task.args = {"state": "other"}
        with pytest.raises(AnsibleError, match="state must be"):
            action_module.run()
