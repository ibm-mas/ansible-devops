"""Static tests for the saas_backup role and br_saas_backup playbook (MASCORE-20277).

The task files are parsed as YAML (no cluster, git or Ansible run). They assert the safety properties of
the local SaaS backup: the reused backup roles are called once per instance in strict named-only mode with an
explicit workspace ID, nothing is auto-discovered, failures are never swallowed, secrets are not echoed, and the
archive is produced by the packaging plugin after all collection steps.
"""

import ast
from pathlib import Path
from typing import Any, Dict, List

import jinja2
import pytest
import yaml

_COLLECTION = Path(__file__).resolve().parents[3].parent
ROLE = _COLLECTION / "roles" / "saas_backup"
PLAYBOOK = _COLLECTION / "playbooks" / "br_saas_backup.yml"


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


def test_playbook_runs_role_on_localhost_and_fails_fast():
    """Test the local entry point.

    GIVEN the br_saas_backup playbook
    WHEN it is parsed
    THEN it targets localhost with any_errors_fatal and only runs the saas_backup role.
    """
    play = loadYaml(PLAYBOOK)[0]

    assert play["hosts"] == "localhost"
    assert play["any_errors_fatal"] is True
    assert play["roles"] == ["ibm.mas_devops.saas_backup"]


@pytest.mark.parametrize(
    "fragment,role,extra",
    [
        ("Back up Suite (core) resources", "ibm.mas_devops.suite_backup", {"include_ca_keys": False}),
        ("Back up Manage resources", "ibm.mas_devops.suite_app_backup", {"mas_app_id": "manage", "mas_app_backup_include_pvc": False}),
    ],
)
def test_reused_roles_run_strict_with_explicit_ids(fragment, role, extra):
    """Test the arguments passed to the reused backup roles.

    GIVEN backup_instance.yml
    WHEN the Suite and Manage role invocations are inspected
    THEN each is strict named-only, has no secret auto-discovery, and receives explicit instance, workspace and directory values.
    """
    task = findTask(taskFile("backup_instance.yml"), fragment)
    variables = task["vars"]

    assert task["ansible.builtin.include_role"]["name"] == role
    assert variables["strict_named_only"] is True
    assert variables["auto_discover_secrets"] is False
    assert variables["mas_instance_id"] == "{{ _sb_inst }}"
    assert variables["mas_workspace_id"] == "{{ _si_workspace_id }}"
    assert variables["mas_backup_dir"].startswith("{{ _sb_staging }}/openshift/")
    assert variables["env_snapshot_saas_envs_dir"] == "" and variables["env_snapshot_gitops_envs_dir"] == ""
    for key, value in extra.items():
        assert variables[key] == value


def test_instances_are_backed_up_one_at_a_time_through_a_loop():
    """Test per-instance execution.

    GIVEN main.yml
    WHEN the instance task is inspected
    THEN backup_instance.yml is included once per entry of the validated instance list.
    """
    task = findTask(taskFile("main.yml"), "Back up instance")

    assert task["ansible.builtin.include_tasks"].endswith("backup_instance.yml")
    assert task["loop"] == "{{ _sb_instances }}"
    assert task["vars"]["_sb_inst"] == "{{ inst }}"


def test_workspace_id_is_never_guessed():
    """Test workspace resolution.

    GIVEN backup_instance.yml
    WHEN the workspace tasks are inspected
    THEN the ID comes only from the explicit override or saas-envs, has no other default, and is validated.
    """
    tasks = taskFile("backup_instance.yml")
    resolve = findTask(tasks, "Resolve workspace ID")["ansible.builtin.set_fact"]["_si_workspace_id"]
    validate = findTask(tasks, "cannot be resolved")["ansible.builtin.assert"]["that"]

    assert resolve == "{{ _sb_ws_overrides[_sb_inst] | default(_si_instance_params.mas_workspaces.id | default('', true), true) }}"
    assert any("match('^[a-z][a-z0-9]{2,11}$')" in c for c in validate)
    assert any("mas_instance.id" in c for c in validate)


# Informational reads that only populate the "versions" block of metadata.json. A failure is recorded there as "unavailable".
VERSION_ONLY_REGISTERS = {"_si_core_sub", "_si_manage_cr"}
# Results that are summarised into a secret-free fact first (so loop items never echo secret values); the fact is what is checked.
CHECKED_VIA_SUMMARY = {"_sb_aws_fetch": "_sb_aws_status"}


def test_no_task_swallows_a_failure_without_a_matching_fail():
    """Test that failures are not ignored.

    GIVEN every role task
    WHEN ignore_errors and failed_when: false are searched
    THEN ignore_errors is never used, and each failed_when: false is followed by a task that fails on the registered result,
         except the two version-only reads.
    """
    for name in ("main.yml", "backup_instance.yml", "prepare_repo.yml", "aws_secrets.yml"):
        tasks = taskFile(name)
        assert not any(t.get("ignore_errors") for t in tasks), name
        for index, task in enumerate(tasks):
            if task.get("failed_when") is False:
                registered = task["register"]
                if registered in VERSION_ONLY_REGISTERS:
                    continue
                next_index = index + 1
                following = tasks[next_index:]
                registered = CHECKED_VIA_SUMMARY.get(registered, registered)
                assert any(
                    registered in str(t) for t in following if "ansible.builtin.fail" in t or "ansible.builtin.assert" in t or "failed_when" in t
                ), f"{name}: '{task['name']}' ignores failure of {registered} but nothing checks it"


def test_secret_bearing_tasks_use_no_log():
    """Test that credential and secret handling tasks hide their output.

    GIVEN the repository clone, git remote read and AWS secret tasks
    WHEN they are inspected
    THEN they use no_log, and no task loops over registered AWS results in clear.
    """
    clone = findTask(taskFile("prepare_repo.yml"), "clone {{")
    remote = findTask(taskFile("prepare_repo.yml"), "read commit, branch and origin")
    fetch = findTask(taskFile("aws_secrets.yml"), "fetch secret values")
    write = findTask(taskFile("aws_secrets.yml"), "write secret values")
    summarise = findTask(taskFile("aws_secrets.yml"), "summarise fetch results")

    for task in (clone, remote, fetch, write, summarise):
        assert task["no_log"] is True, task["name"]
    for task in taskFile("aws_secrets.yml"):
        if "ansible.builtin.fail" in task:
            assert "_sb_aws_fetch" not in str(task.get("loop")), task["name"]


def test_packaging_is_the_last_collection_step_and_cleanup_follows_success():
    """Test ordering.

    GIVEN main.yml
    WHEN the block order is inspected
    THEN packaging happens after the instance and AWS collection, optional encryption and verification follow it inside the block,
         the rescue removes the work directory and fails the play,
         and the work directory is only removed after the block succeeds.
    """
    main = loadYaml(ROLE / "tasks" / "main.yml")
    block = next(t for t in main if "block" in t)
    names = [t["name"] for t in block["block"]]
    package = next(t for t in block["block"] if "ibm.mas_devops.package_saas_backup" in t)

    assert names.index("Back up instance") < names.index("Collect explicitly listed AWS secrets") < names.index(package["name"])
    encrypt = next(t for t in block["block"] if "ibm.mas_devops.encrypt_saas_backup" in t)
    assert names.index(encrypt["name"]) == names.index(package["name"]) + 1
    assert encrypt["when"] == "saas_backup_encryption_enabled | bool"
    assert encrypt["register"] == "_sb_encryption"
    assert [list(t)[1] for t in block["rescue"]] == ["ansible.builtin.file", "ansible.builtin.fail"]
    assert main.index(block) < next(i for i, t in enumerate(main) if t.get("name") == "Remove the work directory")
    assert package["ibm.mas_devops.package_saas_backup"]["metadata"]["scope"]["auto_discover_secrets"] is False
    assert package["ibm.mas_devops.package_saas_backup"]["metadata"]["scope"]["ca_private_keys_exported"] is False


def test_defaults_are_safe():
    """Test the defaults.

    GIVEN the role defaults
    WHEN the opt-out flags are evaluated from an empty environment
    THEN every opt-out defaults to false, AWS collection is empty, and no input has an invented default.
    """
    defaults = loadYaml(ROLE / "defaults" / "main.yml")

    for name in (
        "saas_backup_allow_missing_gitops_envs",
        "saas_backup_allow_dirty_checkout",
        "saas_backup_skip_cluster_url_check",
        "saas_backup_include_manual_certs",
    ):
        assert "default('false', true) | bool" in defaults[name], name
    for name in ("saas_backup_account", "saas_backup_region", "saas_backup_cluster", "saas_backup_instances", "saas_backup_aws_secret_ids"):
        assert "default(" not in defaults[name], name


def test_manual_certs_are_excluded_unless_requested():
    """Test private key handling for the saas-envs snapshot.

    GIVEN backup_instance.yml
    WHEN the manual-certs removal task is inspected
    THEN it removes the folder unless SAAS_BACKUP_INCLUDE_MANUAL_CERTS is true.
    """
    task = findTask(taskFile("backup_instance.yml"), "Remove manual-certs")

    assert task["ansible.builtin.file"]["state"] == "absent"
    assert task["ansible.builtin.file"]["path"].endswith("/manual-certs")
    assert task["when"] == "not (saas_backup_include_manual_certs | bool)"


def test_aws_secrets_only_read_explicit_ids_and_check_cluster_provider():
    """Test AWS collection scope.

    GIVEN aws_secrets.yml
    WHEN the fetch task and preconditions are inspected
    THEN only the explicit ID list is looped, no list-secrets discovery is used, and avp_type must be aws.
    """
    tasks = taskFile("aws_secrets.yml")
    fetch = findTask(tasks, "fetch secret values")
    argv = fetch["ansible.builtin.command"]["argv"]
    asserted = findTask(tasks, "does not use AWS Secrets Manager")["ansible.builtin.assert"]["that"]

    assert fetch["loop"] == "{{ _sb_aws_secret_ids }}"
    assert argv[:3] == ["aws", "secretsmanager", "get-secret-value"]
    assert "list-secrets" not in yaml.dump(tasks)
    assert any("avp_type" in c and "'aws'" in c for c in asserted)


def test_encryption_is_opt_in_and_never_needs_the_private_key():
    """Test the encryption defaults and wiring.

    GIVEN the role defaults and main.yml
    WHEN the encryption variables and task are inspected
    THEN encryption defaults to false, only a public key is configured, and the output defaults to the archive plus .enc.
    """
    defaults = loadYaml(ROLE / "defaults" / "main.yml")
    main = loadYaml(ROLE / "tasks" / "main.yml")
    block = next(t for t in main if "block" in t)
    encrypt = next(t for t in block["block"] if "ibm.mas_devops.encrypt_saas_backup" in t)
    args = encrypt["ibm.mas_devops.encrypt_saas_backup"]

    assert "SAAS_BACKUP_ENCRYPTION_ENABLED" in defaults["saas_backup_encryption_enabled"]
    assert "default('false', true) | bool" in defaults["saas_backup_encryption_enabled"]
    assert "SAAS_BACKUP_ENCRYPTION_PUBLIC_KEY_PATH" in defaults["saas_backup_encryption_public_key_path"]
    assert not [k for k in defaults if "private" in k]
    assert set(args) == {"archive_path", "public_key_path", "output_path"}
    assert args["archive_path"] == "{{ _sb_package.archive_path }}"
    assert "_sb_package.archive_path ~ '.enc'" in args["output_path"]
    assert "private" not in yaml.dump(encrypt).lower()


def test_post_encryption_verification_validates_existence_non_empty_and_checksum_match():
    """Test post-encryption verification tasks before plaintext removal.

    GIVEN main.yml
    WHEN the post-encryption verification tasks are inspected
    THEN stat and slurp tasks verify the encrypted archive and sidecar exist, size is > 0, and checksums match before cleanup.
    """
    main = loadYaml(ROLE / "tasks" / "main.yml")
    block = next(t for t in main if "block" in t)
    tasks = block["block"]

    stat_enc = findTask(tasks, "Stat the encrypted archive for post-encryption verification")
    stat_sidecar = findTask(tasks, "Stat the encrypted archive checksum sidecar")
    read_sidecar = findTask(tasks, "Read the encrypted archive checksum sidecar")
    verify = findTask(tasks, "Verify encrypted archive and checksum sidecar before removing plaintext")

    assert stat_enc["ansible.builtin.stat"]["path"] == "{{ _sb_encryption.encrypted_archive_path }}"
    assert stat_enc["ansible.builtin.stat"]["get_checksum"] is True
    assert stat_enc["when"] == "saas_backup_encryption_enabled | bool"

    assert stat_sidecar["ansible.builtin.stat"]["path"] == "{{ _sb_encryption.encrypted_archive_checksum_file }}"
    assert stat_sidecar["when"] == "saas_backup_encryption_enabled | bool"

    assert read_sidecar["ansible.builtin.slurp"]["src"] == "{{ _sb_encryption.encrypted_archive_checksum_file }}"

    asserted = verify["ansible.builtin.assert"]["that"]
    assert any("not (_sb_encryption.failed" in c for c in asserted)
    assert any("_sb_enc_stat.stat.exists" in c for c in asserted)
    assert any("_sb_enc_stat.stat.isreg" in c for c in asserted)
    assert any("_sb_enc_stat.stat.size" in c and "> 0" in c for c in asserted)
    assert any("_sb_enc_sidecar_stat.stat.exists" in c for c in asserted)
    assert any("_sb_enc_sidecar_stat.stat.isreg" in c for c in asserted)
    assert any("_sb_enc_stat.stat.checksum" in c and "_sb_encryption.encrypted_archive_sha256" in c for c in asserted)
    assert any("_sb_enc_sidecar_raw.content" in c and "_sb_encryption.encrypted_archive_sha256" in c for c in asserted)


def test_successful_encryption_removes_exact_plaintext_archive_and_sidecar():
    """Test plaintext cleanup upon successful encryption.

    GIVEN main.yml
    WHEN the plaintext cleanup task is inspected
    THEN it runs only after verification and deletes exactly the plaintext archive and sidecar.
    """
    main = loadYaml(ROLE / "tasks" / "main.yml")
    block = next(t for t in main if "block" in t)
    tasks = block["block"]
    names = [t["name"] for t in tasks]

    verify_idx = names.index("Verify encrypted archive and checksum sidecar before removing plaintext")
    cleanup = findTask(tasks, "Remove the plaintext backup archive and checksum")
    cleanup_idx = names.index(cleanup["name"])

    assert cleanup_idx > verify_idx
    assert cleanup["when"] == "saas_backup_encryption_enabled | bool"
    assert cleanup["ansible.builtin.file"]["state"] == "absent"
    assert cleanup["loop"] == ["{{ _sb_package.archive_path }}", "{{ _sb_package.archive_checksum_file }}"]


def test_cleanup_is_restricted_to_exact_current_backup_paths_without_wildcards():
    """Test that cleanup never uses wildcards and targets only current backup paths.

    GIVEN main.yml
    WHEN all file deletion tasks are inspected
    THEN no task uses wildcards in deletion paths, and only exact paths are targeted.
    """
    tasks = taskFile("main.yml")
    deletion_tasks = [t for t in tasks if t.get("ansible.builtin.file", {}).get("state") == "absent"]

    for task in deletion_tasks:
        file_args = task["ansible.builtin.file"]
        path = str(file_args.get("path", ""))
        loop = str(task.get("loop", ""))
        assert "*" not in path and "?" not in path
        assert "*" not in loop and "?" not in loop


def test_encrypted_archive_and_sidecar_are_never_deleted():
    """Test that encrypted output files are never targeted for deletion.

    GIVEN main.yml
    WHEN all file deletion tasks and loops are inspected
    THEN none of them reference _sb_encryption or .tar.gz.enc paths with state: absent.
    """
    tasks = taskFile("main.yml")
    deletion_tasks = [t for t in tasks if t.get("ansible.builtin.file", {}).get("state") == "absent"]

    for task in deletion_tasks:
        serialized = yaml.dump(task)
        assert "_sb_encryption" not in serialized
        assert ".enc" not in serialized


def test_encryption_and_verification_failure_preserves_plaintext_archive():
    """Test error handling when encryption or verification fails.

    GIVEN main.yml
    WHEN the rescue block is inspected
    THEN only the temporary work directory is removed, and plaintext archive paths are never removed in rescue.
    """
    main = loadYaml(ROLE / "tasks" / "main.yml")
    block = next(t for t in main if "block" in t)
    rescue_tasks = block["rescue"]

    deleted_paths = [t["ansible.builtin.file"]["path"] for t in rescue_tasks if t.get("ansible.builtin.file", {}).get("state") == "absent"]
    assert deleted_paths == ["{{ _sb_work_dir }}"]
    fail_task = next(t for t in rescue_tasks if "ansible.builtin.fail" in t)
    assert "_sb_archive ~ ' was retained)'" in fail_task["ansible.builtin.fail"]["msg"]


def test_summary_reports_encrypted_archive_and_plaintext_cleanup_confirmation():
    """Test summary reporting when encryption is enabled.

    GIVEN main.yml
    WHEN the final debug summary task is inspected
    THEN it reports encrypted archive path, size, sha256, and confirms plaintext cleanup when encryption is enabled.
    """
    task = findTask(taskFile("main.yml"), "Backup complete")
    msg = task["ansible.builtin.debug"]["msg"]

    assert "_sb_encryption.encrypted_archive_path" in msg
    assert "_sb_encryption.encrypted_archive_size" in msg
    assert "_sb_encryption.encrypted_archive_sha256" in msg
    assert "Plaintext cleanup:" in msg


def test_original_plaintext_sha256_is_preserved_before_cleanup_as_digest_only():
    """Test the plaintext digest is captured before the plaintext files are removed.

    GIVEN main.yml
    WHEN the digest-preservation task and the cleanup task are inspected
    THEN the digest is stored as a fact from the packaging result before cleanup, and no file copy is made.
    """
    block = next(t for t in loadYaml(ROLE / "tasks" / "main.yml") if "block" in t)
    tasks = block["block"]
    names = [t["name"] for t in tasks]

    preserve = findTask(tasks, "Preserve the original plaintext archive SHA-256")
    cleanup = findTask(tasks, "Remove the plaintext backup archive and checksum")

    assert names.index(preserve["name"]) < names.index(cleanup["name"])
    assert preserve["ansible.builtin.set_fact"] == {"_sb_plaintext_sha256": "{{ _sb_package.archive_sha256 }}"}
    assert preserve["when"] == "saas_backup_encryption_enabled | bool"
    assert not any(k in preserve for k in ("ansible.builtin.copy", "ansible.builtin.file"))


def test_summary_reports_original_sha256_after_plaintext_cleanup():
    """Test the rendered final summary after the plaintext files no longer exist.

    GIVEN the "Backup complete" message template and facts as they exist after plaintext cleanup
    WHEN the template is rendered
    THEN it contains the original plaintext SHA-256, encrypted path, size, SHA-256 and the cleanup status.
    """
    msg = findTask(taskFile("main.yml"), "Backup complete")["ansible.builtin.debug"]["msg"]
    plain_sha = "a" * 64
    enc_sha = "b" * 64
    variables = {
        "saas_backup_account": "acc",
        "saas_backup_region": "reg",
        "saas_backup_cluster": "cl",
        "saas_backup_encryption_enabled": True,
        "_sb_instances": ["inst01"],
        "_sb_warnings": [],
        "_sb_plaintext_sha256": plain_sha,
        "_sb_package": {
            "archive_path": "/out/x.tar.gz",
            "archive_checksum_file": "/out/x.tar.gz.sha256",
            "archive_sha256": plain_sha,
        },
        "_sb_encryption": {
            "encrypted_archive_path": "/out/x.tar.gz.enc",
            "encrypted_archive_size": 1234,
            "encrypted_archive_sha256": enc_sha,
            "encrypted_archive_checksum_file": "/out/x.tar.gz.enc.sha256",
            "key_encapsulation_algorithm": "ML-KEM-768",
            "key_derivation_algorithm": "HKDF-SHA256",
            "encryption_algorithm": "AES-256-GCM",
        },
    }
    env = jinja2.Environment(undefined=jinja2.StrictUndefined)
    env.filters["bool"] = bool
    lines = ast.literal_eval(env.from_string(msg).render(**variables))
    text = "\n".join(str(line) for line in lines)

    assert f"Original plaintext archive SHA-256: {plain_sha}" in text
    assert "Encrypted archive: /out/x.tar.gz.enc" in text
    assert "Encrypted archive size: 1234 bytes" in text
    assert f"Encrypted archive SHA-256: {enc_sha}" in text
    assert "Plaintext cleanup: plaintext archive /out/x.tar.gz and sidecar removed" in text
