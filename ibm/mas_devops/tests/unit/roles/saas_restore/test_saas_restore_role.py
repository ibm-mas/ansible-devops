"""Tests for the saas_restore role and the br_saas_restore playbook.

Static tests parse the task files. Behavioural tests run the real playbook with ``ansible-playbook`` on localhost against a
fake ``openssl`` (no ML-KEM needed) and a stub ``oc`` that records every invocation, proving when the cluster is, and is not,
contacted. No real cluster is used and the OpenShift restore roles are never reached by these tests.
"""

import hashlib
import io
import json
import os
import shutil
import stat
import subprocess
import sys
import tarfile
from pathlib import Path
from typing import Any, Dict, List

import pytest
import yaml

_COLLECTION = Path(__file__).resolve().parents[3].parent
ROLE = _COLLECTION / "roles" / "saas_restore"
PLAYBOOK = _COLLECTION / "playbooks" / "br_saas_restore.yml"
MODULE_UTILS = _COLLECTION / "plugins" / "module_utils"

TS = "20261109T152831Z"
TOP = f"saas-backup-acc-reg-cl-{TS}"
SERVER = "https://api.cl.example.com:6443"
SUITE_DIR = f"openshift/inst01/backup-{TS}-suite"
MANAGE_DIR = f"openshift/inst01/backup-{TS}-app-manage"

FAKE_OPENSSL = """#!{python}
import hashlib, os, sys

args = sys.argv[1:]


def keyId(path):
    return open(path).read().split("id=")[1].split()[0]


if args == ["version"]:
    print("OpenSSL fake")
elif args == ["list", "-kem-algorithms"]:
    print("  ML-KEM-768 @ default")
elif args == ["pkeyutl", "-help"]:
    sys.stderr.write(" -encap\\n -decap\\n")
elif args[0] == "pkey":
    if "id=" not in open(args[args.index("-in") + 1]).read():
        sys.exit(1)
    print("ML-KEM-768 Public-Key:")
elif args[:2] == ["pkeyutl", "-encap"]:
    ident = keyId(args[args.index("-inkey") + 1])
    kem = os.urandom(1088)
    open(args[args.index("-out") + 1], "wb").write(kem)
    open(args[args.index("-secret") + 1], "wb").write(hashlib.sha256(ident.encode() + kem).digest())
elif args[:2] == ["pkeyutl", "-decap"]:
    ident = keyId(args[args.index("-inkey") + 1])
    kem = open(args[args.index("-in") + 1], "rb").read()
    open(args[args.index("-secret") + 1], "wb").write(hashlib.sha256(ident.encode() + kem).digest())
else:
    sys.exit(1)
"""

STUB_OC = """#!/bin/sh
echo "$@" >> "$OC_STUB_LOG"
if [ "$1" = "whoami" ] && [ "$2" = "--show-server" ]; then echo "$OC_STUB_SERVER"; exit 0; fi
if [ "$1" = "whoami" ]; then echo "kube:admin"; exit 0; fi
exit 1
"""


def loadYaml(path: Path) -> Any:
    """Load a YAML file."""
    with open(path) as f:
        return yaml.safe_load(f)


def flatten(tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return every task including those nested in block/rescue/always."""
    result = []
    for task in tasks:
        result.append(task)
        for key in ("block", "rescue", "always"):
            if key in task:
                result.extend(flatten(task[key]))
    return result


def taskFile(name: str) -> List[Dict[str, Any]]:
    """Return all tasks of a role task file."""
    return flatten(loadYaml(ROLE / "tasks" / name))


def findTask(tasks: List[Dict[str, Any]], fragment: str) -> Dict[str, Any]:
    """Return the single task whose name contains the fragment."""
    matches = [t for t in tasks if fragment in str(t.get("name", ""))]
    assert len(matches) == 1, f"expected one task matching '{fragment}', found {len(matches)}"
    return matches[0]


# --- static tests ------------------------------------------------------------------------------------------------


def test_playbook_runs_role_on_localhost_and_fails_fast():
    """GIVEN br_saas_restore WHEN parsed THEN it targets localhost with any_errors_fatal and only runs the saas_restore role."""
    play = loadYaml(PLAYBOOK)[0]
    assert play["hosts"] == "localhost" and play["any_errors_fatal"] is True
    assert play["roles"] == ["ibm.mas_devops.saas_restore"]


def test_defaults_follow_conventions_and_default_to_decrypt_only():
    """GIVEN the role defaults THEN every variable reads its SAAS_RESTORE_* environment variable and the mode defaults to decrypt_only."""
    defaults = loadYaml(ROLE / "defaults" / "main.yml")
    expected = {
        "saas_restore_mode": "SAAS_RESTORE_MODE",
        "saas_restore_encrypted_archive_path": "SAAS_RESTORE_ENCRYPTED_ARCHIVE_PATH",
        "saas_restore_private_key_path": "SAAS_RESTORE_PRIVATE_KEY_PATH",
        "saas_restore_output_dir": "SAAS_RESTORE_OUTPUT_DIR",
        "saas_restore_cluster": "SAAS_RESTORE_CLUSTER",
        "saas_restore_instances": "SAAS_RESTORE_INSTANCES",
        "saas_restore_skip_cluster_url_check": "SAAS_RESTORE_SKIP_CLUSTER_URL_CHECK",
    }
    for variable, env in expected.items():
        assert f"lookup('env', '{env}')" in defaults[variable]
    assert "default('decrypt_only', true)" in defaults["saas_restore_mode"]
    assert "default('false', true)" in defaults["saas_restore_skip_cluster_url_check"]


def test_main_flow_decrypts_and_validates_before_any_restore():
    """Test the ordering that makes the restore conditional on validation.

    GIVEN main.yml
    WHEN the block is inspected
    THEN decrypt, the assertion and the report precede the restore include, which only runs in full_restore mode.
    """
    block = next(t for t in loadYaml(ROLE / "tasks" / "main.yml") if "block" in t)
    names = [t["name"] for t in block["block"]]
    decrypt = findTask(block["block"], "Verify the checksum, decrypt")
    restore = findTask(block["block"], "Restore the OpenShift resources")

    assert (
        names.index(decrypt["name"]) < names.index(findTask(block["block"], "Assert that every integrity check passed")["name"]) < names.index(restore["name"])
    )
    assert restore["when"] == "saas_restore_mode == 'full_restore'"
    assert restore["ansible.builtin.include_tasks"].endswith("tasks/restore.yml")
    assert decrypt["ibm.mas_devops.decrypt_saas_backup"]["extract"] == "{{ saas_restore_mode == 'full_restore' }}"
    assert "ibm.mas_devops.decrypt_saas_backup" in decrypt and "failed_when" not in decrypt and "ignore_errors" not in decrypt


def test_decrypt_only_path_has_no_cluster_interaction():
    """Test that decrypt-only cannot modify the cluster.

    GIVEN main.yml and validate_inputs.yml
    WHEN every task outside the restore include is inspected
    THEN none uses oc, kubernetes.core or the restore roles, so decrypt_only never contacts OpenShift.
    """
    for name in ("main.yml", "validate_inputs.yml"):
        for task in taskFile(name):
            serialized = yaml.dump(task)
            assert "kubernetes.core" not in serialized and "include_role" not in serialized and "restore_resource" not in serialized
            command = task.get("ansible.builtin.command", {})
            assert "oc" not in command.get("argv", []) if isinstance(command, dict) else True


def test_all_cluster_access_is_in_restore_tasks_and_reuses_existing_roles():
    """GIVEN restore.yml and restore_instance.yml THEN restoration is delegated to suite_restore and suite_app_restore only."""
    restoreTasks = taskFile("restore.yml") + taskFile("restore_instance.yml")
    roles = [t["ansible.builtin.include_role"]["name"] for t in restoreTasks if "ansible.builtin.include_role" in t]
    assert roles == ["ibm.mas_devops.suite_restore", "ibm.mas_devops.suite_app_restore"]
    assert not any("kubernetes.core" in yaml.dump(t) or "restore_resource" in yaml.dump(t) for t in restoreTasks)
    manage = findTask(restoreTasks, "Restore Manage resources")
    assert manage["ansible.builtin.include_role"]["name"] == "ibm.mas_devops.suite_app_restore"
    assert manage["vars"]["mas_app_restore_include_pvc"] is False
    assert manage["vars"]["mas_app_id"] == "manage"


def test_cluster_identity_is_checked_before_restoring():
    """GIVEN restore.yml THEN oc login and the cluster URL are verified before the first instance is restored."""
    tasks = loadYaml(ROLE / "tasks" / "restore.yml")
    names = [t["name"] for t in tasks]
    assert (
        names.index("Check oc is logged in")
        < names.index("Fail if the logged in cluster is not the cluster the backup was taken from")
        < names.index("Restore instance")
    )
    check = findTask(tasks, "Fail if the logged in cluster is not")
    assert check["when"] == "not (saas_restore_skip_cluster_url_check | bool)"


def test_work_directory_is_always_removed_and_encrypted_backup_never_deleted():
    """Test cleanup and non-destruction.

    GIVEN main.yml
    WHEN the always section and all deletion tasks are inspected
    THEN the plaintext work directory is removed even on failure, and nothing can delete the encrypted backup or the key.
    """
    block = next(t for t in loadYaml(ROLE / "tasks" / "main.yml") if "block" in t)
    cleanup = findTask(block["always"], "Remove the decrypted plaintext work directory")
    assert cleanup["ibm.mas_devops.decrypt_saas_backup"]["state"] == "absent"
    assert "rescue" not in block

    for name in ("main.yml", "restore.yml", "restore_instance.yml", "validate_inputs.yml"):
        for task in taskFile(name):
            if task.get("ansible.builtin.file", {}).get("state") == "absent":
                raise AssertionError(f"unexpected file deletion task in {name}: {task['name']}")


def test_private_key_content_is_never_read_or_printed():
    """GIVEN all role files THEN the private key is only passed by path: never slurped, looked up, copied or printed."""
    text = "\n".join(p.read_text() for p in ROLE.rglob("*.yml"))
    assert "slurp" not in text and "lookup('file'" not in text and "ansible.builtin.copy" not in text
    for task in flatten(loadYaml(ROLE / "tasks" / "main.yml")):
        if "ansible.builtin.debug" in task:
            assert "private_key" not in yaml.dump(task["ansible.builtin.debug"])
    stats = [t for t in taskFile("main.yml") if "ansible.builtin.stat" in t]
    assert all("get_checksum" not in t["ansible.builtin.stat"] for t in stats)


# --- behavioural tests: the real playbook against a fake openssl and a stub oc -----------------------------------

ansiblePlaybook = shutil.which("ansible-playbook", path=os.path.dirname(sys.executable)) or shutil.which("ansible-playbook")
pytestmark_behaviour = pytest.mark.skipif(ansiblePlaybook is None, reason="ansible-playbook is not available")


def sha(data):
    """SHA-256 hex digest of bytes."""
    return hashlib.sha256(data).hexdigest()


def buildArchive(path):
    """Write a valid SaaS backup tar.gz."""
    files = {
        f"{SUITE_DIR}/resources/projects/p.yaml": b"kind: Project\n",
        f"{MANAGE_DIR}/resources/manageapps/m.yaml": b"kind: ManageApp\n",
    }
    meta = {
        "backup_type": "saas-named-resources",
        "created_utc": TS,
        "account": "acc",
        "region": "reg",
        "cluster": "cl",
        "cluster_api_server": SERVER,
        "instances": ["inst01"],
        "instance_details": [
            {
                "instance_id": "inst01",
                "workspace_id": "main",
                "applications_backed_up": ["core", "manage"],
                "openshift": {"suite": {"backup_path": SUITE_DIR}, "manage": {"backup_path": MANAGE_DIR}},
            }
        ],
        "warnings": [],
        "package": {
            "archive_top_level_directory": TOP,
            "files": [{"path": p, "size": len(b), "sha256": sha(b)} for p, b in sorted(files.items())],
        },
    }
    metaBytes = json.dumps(meta).encode()
    sums = {p: sha(b) for p, b in files.items()}
    sums["metadata.json"] = sha(metaBytes)
    members = {f"{TOP}/{p}": b for p, b in files.items()}
    members[f"{TOP}/metadata.json"] = metaBytes
    members[f"{TOP}/SHA256SUMS"] = "".join(f"{d}  {p}\n" for p, d in sorted(sums.items())).encode()
    with tarfile.open(path, "w:gz") as tar:
        for name, data in members.items():
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    """Create a workspace with the fake openssl, the stub oc, keys, an encrypted backup and a collections path."""
    binDir = tmp_path / "bin"
    binDir.mkdir()
    for name, content in (("openssl", FAKE_OPENSSL.format(python=sys.executable)), ("oc", STUB_OC)):
        (binDir / name).write_text(content)
        (binDir / name).chmod(stat.S_IRWXU)
    collections = tmp_path / "collections" / "ansible_collections" / "ibm"
    collections.mkdir(parents=True)
    (collections / "mas_devops").symlink_to(_COLLECTION)
    keys = tmp_path / "keys"
    keys.mkdir()
    (keys / "public.pem").write_text("-----BEGIN PUBLIC KEY-----\nid=alpha\n-----END PUBLIC KEY-----\n")
    (keys / "private.pem").write_text("-----BEGIN PRIVATE KEY-----\nid=alpha\n-----END PRIVATE KEY-----\n")
    (keys / "other.pem").write_text("-----BEGIN PRIVATE KEY-----\nid=beta\n-----END PRIVATE KEY-----\n")
    for name in ("src", "backup", "out"):
        (tmp_path / name).mkdir()

    monkeypatch.setenv("PATH", f"{binDir}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.syspath_prepend(str(MODULE_UTILS))
    import saas_backup_encryption as enc

    plain = tmp_path / "src" / f"{TOP}.tar.gz"
    buildArchive(plain)
    encPath = str(tmp_path / "backup" / f"{TOP}.tar.gz.enc")
    enc.encryptArchive(str(plain), str(keys / "public.pem"), encPath)
    return {"root": tmp_path, "enc": encPath, "keys": keys, "log": tmp_path / "oc.log", "encModule": enc}


def runPlaybook(sandbox, **env):
    """Run br_saas_restore.yml and return the completed process (output merged)."""
    root = sandbox["root"]
    variables = {
        "SAAS_RESTORE_ENCRYPTED_ARCHIVE_PATH": sandbox["enc"],
        "SAAS_RESTORE_PRIVATE_KEY_PATH": str(sandbox["keys"] / "private.pem"),
        "SAAS_RESTORE_OUTPUT_DIR": str(root / "out"),
    }
    variables.update(env)
    fullEnv = dict(os.environ)
    fullEnv.update(
        {
            "ANSIBLE_COLLECTIONS_PATH": str(root / "collections"),
            "ANSIBLE_NOCOLOR": "1",
            "ANSIBLE_LOCAL_TEMP": str(root / "ansible-tmp"),
            "ANSIBLE_HOME": str(root / "ansible-home"),
            "OC_STUB_LOG": str(sandbox["log"]),
            "OC_STUB_SERVER": SERVER,
            "PYTHONPATH": "",
        }
    )
    fullEnv.update(variables)
    return subprocess.run([ansiblePlaybook, str(PLAYBOOK)], env=fullEnv, capture_output=True, text=True, cwd=str(root), timeout=240)


def ocCalls(sandbox):
    """Return every recorded oc invocation."""
    return sandbox["log"].read_text().splitlines() if sandbox["log"].exists() else []


def snapshot(encPath):
    """Return the bytes of the encrypted archive and its sidecar."""
    return open(encPath, "rb").read(), open(encPath + ".sha256", "rb").read()


@pytestmark_behaviour
def test_decrypt_only_succeeds_without_contacting_the_cluster(sandbox):
    """Test mode A end to end.

    GIVEN a valid encrypted backup and no mode setting
    WHEN the playbook runs
    THEN it verifies, decrypts and reports the backup, never invokes oc, and leaves no plaintext and the backup untouched.
    """
    before = snapshot(sandbox["enc"])
    result = runPlaybook(sandbox)
    output = result.stdout + result.stderr

    assert result.returncode == 0, output
    assert "AES-256-GCM authentication: verified" in output
    assert "SHA256SUMS manifest: 3 files verified" in output
    assert "Instances: inst01" in output and "Account/region/cluster: acc/reg/cl" in output
    assert "Decrypt-only: OpenShift was not contacted and nothing was restored." in output
    assert ocCalls(sandbox) == []
    assert os.listdir(sandbox["root"] / "out") == []
    assert snapshot(sandbox["enc"]) == before
    assert "PRIVATE KEY" not in output and "id=alpha" not in output


@pytestmark_behaviour
def test_decrypt_only_with_wrong_key_stops_and_never_contacts_the_cluster(sandbox):
    """GIVEN the wrong private key WHEN the playbook runs in decrypt_only mode THEN it fails, oc is never called and no plaintext remains."""
    result = runPlaybook(sandbox, SAAS_RESTORE_PRIVATE_KEY_PATH=str(sandbox["keys"] / "other.pem"))

    assert result.returncode != 0 and "Authentication failed" in result.stdout + result.stderr
    assert ocCalls(sandbox) == [] and os.listdir(sandbox["root"] / "out") == []


@pytestmark_behaviour
def test_full_restore_refuses_after_checksum_failure(sandbox):
    """Test that a failed validation stops a full restore.

    GIVEN an encrypted backup that no longer matches its sidecar
    WHEN a full restore runs
    THEN it fails before decryption, oc is never called and no restore role runs.
    """
    raw = bytearray(open(sandbox["enc"], "rb").read())
    raw[-20] ^= 0xFF
    open(sandbox["enc"], "wb").write(raw)
    result = runPlaybook(sandbox, SAAS_RESTORE_MODE="full_restore", SAAS_RESTORE_CLUSTER="cl", SAAS_RESTORE_INSTANCES="inst01")
    output = result.stdout + result.stderr

    assert result.returncode != 0 and "checksum mismatch" in output
    assert ocCalls(sandbox) == [] and "Restore Suite" not in output and os.listdir(sandbox["root"] / "out") == []


@pytestmark_behaviour
def test_full_restore_refuses_after_authentication_failure(sandbox):
    """GIVEN the wrong private key WHEN a full restore runs THEN it fails, oc is never called and no restore role runs."""
    result = runPlaybook(
        sandbox,
        SAAS_RESTORE_MODE="full_restore",
        SAAS_RESTORE_CLUSTER="cl",
        SAAS_RESTORE_INSTANCES="inst01",
        SAAS_RESTORE_PRIVATE_KEY_PATH=str(sandbox["keys"] / "other.pem"),
    )
    assert result.returncode != 0 and "Authentication failed" in result.stdout + result.stderr
    assert ocCalls(sandbox) == [] and "Restore Suite" not in result.stdout and os.listdir(sandbox["root"] / "out") == []


@pytestmark_behaviour
@pytest.mark.parametrize(
    "selection",
    [{"SAAS_RESTORE_CLUSTER": "other"}, {"SAAS_RESTORE_INSTANCES": "inst99"}],
    ids=["wrong-cluster", "unknown-instance"],
)
def test_full_restore_refuses_when_selection_does_not_match_the_backup(sandbox, selection):
    """GIVEN a valid backup but a cluster or instance that is not in it WHEN a full restore runs THEN nothing is restored and oc is never called."""
    env = {"SAAS_RESTORE_MODE": "full_restore", "SAAS_RESTORE_CLUSTER": "cl", "SAAS_RESTORE_INSTANCES": "inst01"}
    env.update(selection)
    result = runPlaybook(sandbox, **env)

    assert result.returncode != 0 and "does not match the request" in result.stdout + result.stderr
    assert ocCalls(sandbox) == [] and os.listdir(sandbox["root"] / "out") == []


@pytestmark_behaviour
def test_full_restore_refuses_on_cluster_url_mismatch_before_restoring(sandbox):
    """Test the final gate before any restore.

    GIVEN a valid backup but an oc session on another cluster
    WHEN a full restore runs
    THEN only the read-only oc whoami calls happen, no restore role runs and the plaintext is removed.
    """
    result = runPlaybook(
        sandbox,
        SAAS_RESTORE_MODE="full_restore",
        SAAS_RESTORE_CLUSTER="cl",
        SAAS_RESTORE_INSTANCES="inst01",
        OC_STUB_SERVER="https://api.other.example.com:6443",
    )
    output = result.stdout + result.stderr

    assert result.returncode != 0 and "Nothing was restored" in output and "Restore Suite" not in output
    assert ocCalls(sandbox) == ["whoami", "whoami --show-server"]
    assert os.listdir(sandbox["root"] / "out") == []


@pytestmark_behaviour
def test_full_restore_refuses_when_oc_is_not_logged_in(sandbox):
    """GIVEN no oc login WHEN a full restore runs THEN it stops before restoring and removes the plaintext."""
    (sandbox["root"] / "bin" / "oc").write_text('#!/bin/sh\necho "$@" >> "$OC_STUB_LOG"\nexit 1\n')
    result = runPlaybook(sandbox, SAAS_RESTORE_MODE="full_restore", SAAS_RESTORE_CLUSTER="cl", SAAS_RESTORE_INSTANCES="inst01")

    assert result.returncode != 0 and "Log in to the cl cluster" in result.stdout + result.stderr
    assert ocCalls(sandbox) == ["whoami"] and os.listdir(sandbox["root"] / "out") == []


@pytestmark_behaviour
@pytest.mark.parametrize(
    "env,message",
    [
        ({"SAAS_RESTORE_MODE": "restore_everything"}, "must be 'decrypt_only'"),
        ({"SAAS_RESTORE_MODE": "full_restore"}, "requires SAAS_RESTORE_CLUSTER and SAAS_RESTORE_INSTANCES"),
        ({"SAAS_RESTORE_ENCRYPTED_ARCHIVE_PATH": "/tmp/backup.tar.gz"}, "must be an absolute path ending in .tar.gz.enc"),
    ],
)
def test_invalid_inputs_are_rejected_before_anything_runs(sandbox, env, message):
    """GIVEN invalid inputs THEN the playbook fails at validation, before decryption, and never contacts the cluster."""
    result = runPlaybook(sandbox, **env)
    output = " ".join((result.stdout + result.stderr).split())

    assert result.returncode != 0 and message in output
    assert ocCalls(sandbox) == [] and os.listdir(sandbox["root"] / "out") == []
