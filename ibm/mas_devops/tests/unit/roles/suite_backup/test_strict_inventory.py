"""
Static tests for the strict_named_only resource inventories in the
suite_backup and suite_app_backup roles (MASCORE-20277).

The role task files are parsed and rendered with Jinja2 (no cluster or Ansible run
required) for the staging targets fvtsaas / fvtsaas2 with workspace 'masdev'. The tests
assert that every strict resource list contains only explicitly named resources, matches
the exact POC-confirmed inventory, propagates the workspace ID, applies the CA key-pair
opt-in policy, and lists CRDs by exact object name.
"""

from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

import jinja2
import pytest
import yaml

_ROLES_ROOT = Path(__file__).resolve().parents[3].parent / "roles"
_COMMON_TASKS = Path(__file__).resolve().parents[3].parent / "common_tasks"

SUITE_BACKUP_TASKS = _ROLES_ROOT / "suite_backup" / "tasks" / "main.yml"
SUITE_BACKUP_DEFAULTS = _ROLES_ROOT / "suite_backup" / "defaults" / "main.yml"
MANAGE_BACKUP_TASKS = _ROLES_ROOT / "suite_app_backup" / "tasks" / "manage" / "backup-namespace.yml"
MANAGE_BACKUP_DEFAULTS = _ROLES_ROOT / "suite_app_backup" / "defaults" / "main.yml"
ENV_SNAPSHOT_TASKS = _COMMON_TASKS / "backup_env_snapshot.yml"

STRICT_WHEN = "strict_named_only | bool"
STAGING_INSTANCES = ["fvtsaas", "fvtsaas2"]
WORKSPACE = "masdev"


def loadYaml(path: Path) -> Any:
    """Load a YAML file."""
    with open(path) as f:
        return yaml.safe_load(f)


def loadTasks(path: Path) -> List[Dict[str, Any]]:
    """Load a task file and return its list of tasks."""
    return loadYaml(path)


def isStrictOnly(task: Dict[str, Any]) -> bool:
    """Return True if a task only runs when strict_named_only is enabled."""
    when = task.get("when")
    conditions = when if isinstance(when, list) else [when]
    return STRICT_WHEN in conditions


def strictResourceLists(path: Path) -> Dict[str, List[Dict[str, Any]]]:
    """Return resource lists (task name -> list) defined by strict-only set_fact tasks."""
    lists = {}
    for task in loadTasks(path):
        if not isStrictOnly(task) or "set_fact" not in task:
            continue
        for value in task["set_fact"].values():
            if isinstance(value, list):
                lists[task["name"]] = value
    return lists


def render(value: Any, ctx: Dict[str, Any]) -> Any:
    """Recursively render Jinja2 templates in a loaded YAML structure."""
    env = jinja2.Environment(undefined=jinja2.StrictUndefined)
    if isinstance(value, str):
        return env.from_string(value).render(**ctx)
    if isinstance(value, list):
        return [render(v, ctx) for v in value]
    if isinstance(value, dict):
        return {k: render(v, ctx) for k, v in value.items()}
    return value


def ctxFor(instance: str) -> Dict[str, Any]:
    """Template context for a staging instance."""
    return {
        "mas_instance_id": instance,
        "mas_workspace_id": WORKSPACE,
        "mas_core_namespace": f"mas-{instance}-core",
        "mas_app_namespace": f"mas-{instance}-manage",
        "manage_workspace_cr_name": f"{instance}-{WORKSPACE}",
        "manage_encryptionsecret_name": f"{WORKSPACE}-manage-encryption-secret",
    }


def renderedStrict(path: Path, taskNameFragment: str, instance: str) -> List[Dict[str, Any]]:
    """Render the strict list whose task name contains taskNameFragment."""
    for name, resources in strictResourceLists(path).items():
        if taskNameFragment in name:
            return render(resources, ctxFor(instance))
    raise AssertionError(f"no strict list matching '{taskNameFragment}'")


def keys(resources: List[Dict[str, Any]]) -> set:
    """Return a set of (kind, name) tuples."""
    return {(r["kind"], r["name"]) for r in resources}


# ---------------------------------------------------------------------------
# 1. strict named-only behaviour of the inventories
# ---------------------------------------------------------------------------
def test_suite_backup_has_strict_core_and_config_lists():
    lists = strictResourceLists(SUITE_BACKUP_TASKS)
    assert len(lists) == 2
    assert any("config resources" in name for name in lists)
    assert any("core namespace resources" in name for name in lists)


def test_manage_backup_has_strict_list():
    assert len(strictResourceLists(MANAGE_BACKUP_TASKS)) == 1


def test_strict_lists_contain_only_named_resources():
    for path in (SUITE_BACKUP_TASKS, MANAGE_BACKUP_TASKS):
        for taskName, resources in strictResourceLists(path).items():
            for resource in resources:
                assert resource.get("name"), f"{taskName}: {resource['kind']} has no name"
                assert resource.get("api_version"), f"{taskName}: {resource['kind']} has no api_version"
                assert "labels" not in resource, f"{taskName}: {resource['kind']} uses a label query"


def test_strict_lists_have_no_duplicates():
    for instance in STAGING_INSTANCES:
        for path, fragment in ((SUITE_BACKUP_TASKS, "core namespace"), (SUITE_BACKUP_TASKS, "config resources"), (MANAGE_BACKUP_TASKS, "Manage namespace")):
            resources = renderedStrict(path, fragment, instance)
            counts = Counter((r["kind"], r["name"]) for r in resources)
            duplicates = [key for key, count in counts.items() if count > 1]
            assert not duplicates, f"{instance} {fragment}: duplicate entries {duplicates}"


def test_strict_append_tasks_set_explicit_names():
    """Tasks that append to a list in strict mode must embed a name."""
    appendTasks = [
        t
        for t in loadTasks(SUITE_BACKUP_TASKS)
        if isStrictOnly(t) and "set_fact" in t and any(isinstance(v, str) and "+ [" in v and "'kind'" in v for v in t["set_fact"].values())
    ]
    assert len(appendTasks) == 3  # BasCfg, SlsCfg, SLS credentials Secret
    for task in appendTasks:
        value = next(iter(task["set_fact"].values()))
        assert "'name':" in value, f"{task['name']} appends a resource without a name"


def test_always_on_backup_lists_are_named():
    """ClusterIssuer/Issuer/Certificate entries are named in every mode."""
    for task in loadTasks(SUITE_BACKUP_TASKS):
        if task.get("name") == "Set fact: mas suite backup resources":
            for group in task["set_fact"]["suite_backup_resources"]:
                if isinstance(group["resources"], list):
                    for resource in group["resources"]:
                        assert resource.get("name"), f"{resource['kind']} has no name"


def test_backup_tasks_pass_strict_flags_to_plugin():
    for path in (SUITE_BACKUP_TASKS, MANAGE_BACKUP_TASKS):
        calls = [t for t in loadTasks(path) if "ibm.mas_devops.backup_resource" in t]
        assert len(calls) == 1
        args = calls[0]["ibm.mas_devops.backup_resource"]
        assert args["strict_named_only"] == "{{ strict_named_only | bool }}"
        assert args["auto_discover_secrets"] == "{{ auto_discover_secrets | bool }}"


# ---------------------------------------------------------------------------
# 2. exact Suite / Manage inventory (POC MASCORE-20742 + live-cluster verified names)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("instance", STAGING_INSTANCES)
def test_exact_suite_core_inventory(instance):
    resources = renderedStrict(SUITE_BACKUP_TASKS, "core namespace", instance)
    expected = {
        ("Project", f"mas-{instance}-core"),
        ("Subscription", "ibm-mas-operator"),
        ("OperatorGroup", "ibm-mas-operator-group"),
        ("Secret", f"{instance}-credentials-superuser"),
        ("Secret", f"{instance}-keys-jwt"),
        ("Secret", f"{instance}-keys-ltpa"),
        ("Secret", "ibm-entitlement"),
        ("Secret", f"{instance}-password-policy"),
        ("Secret", f"{instance}-cert-public"),
        ("Secret", f"{instance}-admindashboard-cert-internal"),
        ("ConfigMap", f"{instance}-catalog-items"),
        ("ConfigMap", f"{instance}-catalog-settings"),
        ("ConfigMap", f"{instance}-nps"),
        ("ConfigMap", f"{instance}-settings-applications"),
        ("ConfigMap", f"{instance}-suite-reconcile"),
        ("ConfigMap", f"{instance}-supported-applications"),
        ("Suite", instance),
        ("Workspace", f"{instance}-{WORKSPACE}"),
        ("GenericAddon", f"{instance}-addons-production-database-access"),
    }
    assert keys(resources) == expected


@pytest.mark.parametrize("instance", STAGING_INSTANCES)
def test_exact_suite_config_inventory(instance):
    resources = renderedStrict(SUITE_BACKUP_TASKS, "config resources", instance)
    assert keys(resources) == {
        ("MongoCfg", f"{instance}-mongo-system"),
        ("JdbcCfg", f"{instance}-jdbc-wsapp-{WORKSPACE}-manage"),
    }


@pytest.mark.parametrize("instance", STAGING_INSTANCES)
def test_exact_manage_inventory(instance):
    resources = renderedStrict(MANAGE_BACKUP_TASKS, "Manage namespace", instance)
    names = keys(resources)
    expectedCore = {
        ("Project", f"mas-{instance}-manage"),
        ("Subscription", "ibm-mas-manage"),
        ("OperatorGroup", f"mas-{instance}-manage-operator-group"),
        ("ManageApp", instance),
        ("ManageWorkspace", f"{instance}-{WORKSPACE}"),
        ("Secret", f"{WORKSPACE}-manage-encryption-secret"),
        ("Secret", f"{WORKSPACE}-manage-encryption-secret-operator"),
        ("Secret", f"{instance}-keys-ltpa"),
        ("Secret", f"{instance}-{WORKSPACE}-jdbccfg-workspace-application-binding"),
        ("Secret", "ibm-entitlement"),
        ("ConfigMap", "maximo-config"),
        ("ConfigMap", f"{instance}-manage-install-placeholder"),
        ("ConfigMap", f"{instance}-manage-{WORKSPACE}-config-placeholder"),
        ("ConfigMap", f"{instance}-{WORKSPACE}-truststore-tsmcfg"),
        ("ConfigMap", f"pre-jreporter-app-install-manage-{instance}-synctime"),
    }
    assert expectedCore <= names
    assert names - expectedCore  # remaining POC secrets / configmaps are listed too


def test_wrong_legacy_names_are_gone_from_strict_lists():
    """Subscription / OperatorGroup / encryption-secret fallback names that were wrong are corrected."""
    for instance in STAGING_INSTANCES:
        suite = keys(renderedStrict(SUITE_BACKUP_TASKS, "core namespace", instance))
        manage = keys(renderedStrict(MANAGE_BACKUP_TASKS, "Manage namespace", instance))
        assert ("Subscription", "ibm-mas") not in suite
        assert ("OperatorGroup", "operatorgroup") not in suite | manage
    text = MANAGE_BACKUP_TASKS.read_text()
    assert "-manage-encryptionsecret" not in text
    assert "-manage-encryption-secret'" in text


def test_non_strict_olm_names_are_also_corrected():
    suiteText = SUITE_BACKUP_TASKS.read_text()
    assert "name: ibm-mas-operator" in suiteText
    assert "name: ibm-mas-operator-group" in suiteText
    assert "name: operatorgroup" not in suiteText


def test_cluster_scoped_and_cert_manager_resources_are_named():
    for task in loadTasks(SUITE_BACKUP_TASKS):
        if task.get("name") == "Set fact: mas suite backup resources":
            groups = task["set_fact"]["suite_backup_resources"]
            certManager = [g for g in groups if g.get("namespace") == "{{ cert_manager_cluster_resource_namespace }}"][0]
            names = {(r["kind"], r["name"]) for r in certManager["resources"]}
            assert names == {
                ("Issuer", "mas-{{ mas_instance_id }}-core-internal-ca-issuer"),
                ("Issuer", "mas-{{ mas_instance_id }}-core-public-ca-issuer"),
                ("Certificate", "{{ mas_instance_id }}-cert-internal-ca"),
                ("Certificate", "{{ mas_instance_id }}-cert-public-ca"),
            }
            return
    raise AssertionError("suite backup resources task not found")


# ---------------------------------------------------------------------------
# 3. workspace ID propagation
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("instance", STAGING_INSTANCES)
def test_workspace_id_propagates_into_suite_and_manage_names(instance):
    suite = keys(renderedStrict(SUITE_BACKUP_TASKS, "core namespace", instance))
    config = keys(renderedStrict(SUITE_BACKUP_TASKS, "config resources", instance))
    manage = keys(renderedStrict(MANAGE_BACKUP_TASKS, "Manage namespace", instance))
    assert ("Workspace", f"{instance}-masdev") in suite
    assert ("JdbcCfg", f"{instance}-jdbc-wsapp-masdev-manage") in config
    assert ("ManageWorkspace", f"{instance}-masdev") in manage
    assert ("Secret", f"{instance}-masdev-jdbccfg-workspace-application-binding") in manage
    assert ("Secret", "masdev-default-bundleproperty") in manage


def test_workspace_id_is_required_in_strict_mode():
    tasks = {t["name"]: t for t in loadTasks(SUITE_BACKUP_TASKS)}
    task = tasks["Strict named-only: workspace ID is required"]
    assert isStrictOnly(task)
    assert 'mas_workspace_id != ""' in task["assert"]["that"]


def test_no_hardcoded_workspace_id_in_task_files():
    for path in (SUITE_BACKUP_TASKS, MANAGE_BACKUP_TASKS, SUITE_BACKUP_DEFAULTS):
        assert "masdev" not in path.read_text(), f"{path.name} hard-codes the workspace"


# ---------------------------------------------------------------------------
# 4. CRDs: explicit, exact object names only (never CR kinds)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "path, var",
    [(SUITE_BACKUP_DEFAULTS, "suite_backup_crds"), (MANAGE_BACKUP_DEFAULTS, "manage_backup_crds")],
)
def test_crd_lists_are_exact_crd_object_names(path, var):
    crds = loadYaml(path)[var]
    assert crds
    for crd in crds:
        assert crd["kind"] == "CustomResourceDefinition"
        assert crd["api_version"] == "apiextensions.k8s.io/v1"
        # CRD object names are <plural>.<group>, never a CR kind such as 'Suite'
        plural, _, group = crd["name"].partition(".")
        assert group and plural == plural.lower() and plural.endswith("s"), crd["name"]


def test_exact_crd_inventory():
    suite = {c["name"] for c in loadYaml(SUITE_BACKUP_DEFAULTS)["suite_backup_crds"]}
    manage = {c["name"] for c in loadYaml(MANAGE_BACKUP_DEFAULTS)["manage_backup_crds"]}
    assert suite == {
        "suites.core.mas.ibm.com",
        "workspaces.core.mas.ibm.com",
        "bascfgs.config.mas.ibm.com",
        "genericaddons.addons.mas.ibm.com",
        "jdbccfgs.config.mas.ibm.com",
        "mongocfgs.config.mas.ibm.com",
        "slscfgs.config.mas.ibm.com",
    }
    assert manage == {
        "manageapps.apps.mas.ibm.com",
        "manageworkspaces.apps.mas.ibm.com",
        "manageserverbundles.apps.mas.ibm.com",
        "managedeployments.apps.mas.ibm.com",
        "truststores.truststore-mgr.ibm.com",
    }


def test_crds_are_added_only_in_strict_mode_to_backup_resources():
    for path, var in ((SUITE_BACKUP_TASKS, "suite_backup_crds"), (MANAGE_BACKUP_TASKS, "manage_backup_crds")):
        tasks = [t for t in loadTasks(path) if "set_fact" in t and any(var in str(v) for v in t["set_fact"].values())]
        assert len(tasks) == 1
        assert isStrictOnly(tasks[0])


# ---------------------------------------------------------------------------
# 5. CA key-pair Secrets: documented POC opt-in policy
# ---------------------------------------------------------------------------
def test_ca_keypair_secrets_not_exported_by_default():
    assert loadYaml(SUITE_BACKUP_DEFAULTS)["include_ca_keys"] == "{{ lookup('env', 'INCLUDE_CA_KEYS') | default('false', true) | bool }}"
    for instance in STAGING_INSTANCES:
        for path, fragment in ((SUITE_BACKUP_TASKS, "core namespace"), (MANAGE_BACKUP_TASKS, "Manage namespace")):
            for resource in renderedStrict(path, fragment, instance):
                assert not resource["name"].endswith(("-cert-internal-ca", "-cert-public-ca")) or resource["kind"] != "Secret"


def test_ca_keypair_opt_in_is_blocked_without_approved_encryption():
    tasks = {t["name"]: t for t in loadTasks(SUITE_BACKUP_TASKS)}
    task = tasks["CA key-pair Secrets: opt-in is blocked until backup encryption is approved"]
    assert "fail" in task
    assert task["when"] == "include_ca_keys | bool"
    assert "DR_ENCRYPT_CMD" in task["fail"]["msg"]


def test_no_task_adds_ca_secrets_to_inventory():
    text = SUITE_BACKUP_TASKS.read_text()
    assert 'kind: Secret\n            api_version: v1\n            name: "{{ mas_instance_id }}-cert-internal-ca"' not in text
    assert "'name': mas_instance_id + '-cert-internal-ca'" not in text


# ---------------------------------------------------------------------------
# 6. environment snapshots
# ---------------------------------------------------------------------------
def test_env_snapshot_is_invoked_from_both_backup_roles():
    for path, backupPathVar in ((SUITE_BACKUP_TASKS, "suite_backup_path"), (MANAGE_BACKUP_TASKS, "manage_backup_path")):
        calls = [t for t in loadTasks(path) if "include_tasks" in t and "backup_env_snapshot.yml" in t["include_tasks"]]
        assert len(calls) == 1
        assert calls[0]["vars"]["env_snapshot_backup_path"] == "{{ " + backupPathVar + " }}"


def test_env_snapshot_sources_are_explicit_inputs_not_discovered():
    for defaults in (SUITE_BACKUP_DEFAULTS, MANAGE_BACKUP_DEFAULTS):
        data = loadYaml(defaults)
        assert data["env_snapshot_saas_envs_dir"] == "{{ lookup('env', 'SAAS_ENVS_INSTANCE_DIR') }}"
        assert data["env_snapshot_gitops_envs_dir"] == "{{ lookup('env', 'GITOPS_ENVS_INSTANCE_DIR') }}"
    text = ENV_SNAPSHOT_TASKS.read_text()
    assert "find:" not in text and "with_fileglob" not in text and "lookup('fileglob'" not in text


def test_env_snapshot_records_missing_gitops_envs_instead_of_inventing_a_source():
    text = ENV_SNAPSHOT_TASKS.read_text()
    assert "no_matching_folder" in text
    assert "nothing was captured" in text
    tasks = {t["name"]: t for t in loadTasks(ENV_SNAPSHOT_TASKS)}
    copyTask = tasks["Environment snapshot: copy gitops-envs instance folder"]
    assert copyTask["when"] == '_env_snapshot_gitops_dir != ""'
    # missing folder that WAS provided is an error, not a silent skip
    assert "fail" in tasks["Environment snapshot: fail if gitops-envs folder was provided but does not exist"]


def test_env_snapshot_is_owner_only():
    tasks = {t["name"]: t for t in loadTasks(ENV_SNAPSHOT_TASKS)}
    assert tasks["Environment snapshot: create destination directory"]["file"]["mode"] == "0700"
    assert tasks["Environment snapshot: copy saas-envs instance folder"]["copy"]["mode"] == "u=rwX,go="


# ---------------------------------------------------------------------------
# 7. missing-resource reporting surfaced by the roles
# ---------------------------------------------------------------------------
def test_roles_report_not_found_named_resources():
    for path, var in ((SUITE_BACKUP_TASKS, "backup_result"), (MANAGE_BACKUP_TASKS, "manage_backup_result")):
        display = [t for t in loadTasks(path) if t.get("name") in ("Display backup results", "Display Manage backup results")][0]
        assert any(f"{var}.not_found_resources" in line for line in display["debug"]["msg"])


def test_manage_required_resources_marked():
    required = {(r["kind"], r["name"]) for r in renderedStrict(MANAGE_BACKUP_TASKS, "Manage namespace", "fvtsaas") if r.get("required")}
    assert required == {
        ("ManageWorkspace", f"fvtsaas-{WORKSPACE}"),
        ("Secret", f"{WORKSPACE}-manage-encryption-secret"),
        ("Secret", f"{WORKSPACE}-manage-encryption-secret-operator"),
    }
