"""Static tests for the saas_backup role and br_saas_backup playbook (MASCORE-20277).

The task files are parsed as YAML (no cluster, git or Ansible run). They assert the safety properties of
the local SaaS backup: the reused backup roles are called once per instance in strict named-only mode with an
explicit workspace ID, nothing is auto-discovered, failures are never swallowed, secrets are not echoed, and the
archive is produced by the packaging plugin after all collection steps.
"""

from pathlib import Path
from typing import Any, Dict, List

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
                following = tasks[index + 1 :]
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
    THEN packaging happens after the instance and AWS collection, the rescue removes the work directory and fails the play,
         and the work directory is only removed after the block succeeds.
    """
    main = loadYaml(ROLE / "tasks" / "main.yml")
    block = next(t for t in main if "block" in t)
    names = [t["name"] for t in block["block"]]
    package = next(t for t in block["block"] if "ibm.mas_devops.package_saas_backup" in t)

    assert names.index("Back up instance") < names.index("Collect explicitly listed AWS secrets") < names.index(package["name"])
    assert names.index(package["name"]) == len(names) - 1
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
