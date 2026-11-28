"""Guard against template delimiters ({{ }}) inside Ansible conditional expressions.

ansible-core >= 2.19 (required by this collection, see meta/runtime.yml) evaluates `when`,
`until`, `failed_when`, `changed_when` and `assert.that` conditionals as native Jinja
expressions. Template delimiters inside an expression are a hard syntax error at task
runtime — "Syntax error in expression. Template delimiters are not supported in
expressions" — a class of bug that neither ansible-lint nor `ansible-playbook
--syntax-check` catches, because it only manifests when the conditional is evaluated.

Introduced in the suite_app_config_manage imagestitching action (ibm-mas/ansible-devops#2540,
reported from an fvtcpd run); this test scans every task and playbook file in the collection
so any reintroduction fails fast in CI instead of in a pipeline.
"""

from pathlib import Path

import pytest
import yaml

# Root of the ibm/mas_devops collection — three levels up from tests/unit/roles/
_COLLECTION_ROOT = Path(__file__).resolve().parents[3]

# Conditional fields that ansible-core parses as Jinja expressions; `retries`, `delay`
# and friends are plain template fields where {{ }} is legal and must NOT be flagged
_CONDITIONAL_FIELDS = ("when", "until", "failed_when", "changed_when")

# Sections whose entries are themselves task lists: block sections within task files,
# and the play sections of standalone playbooks
_TASK_LIST_SECTIONS = ("block", "rescue", "always", "tasks", "pre_tasks", "post_tasks", "handlers")

_TASK_FILE_SUFFIXES = (".yml", ".yaml")


def _task_files():
    """Return every task/playbook YAML file in the collection.

    Covers role task/handler files recursively, shared common_tasks, and the top-level
    dev-*.yml playbooks. Only descends into tasks/ and handlers/ within each role so
    defaults/vars/meta templates (where {{ }} is legal) are not scanned.
    """
    files = sorted((_COLLECTION_ROOT / "common_tasks").glob("*.yml"))
    files += sorted(p for p in _COLLECTION_ROOT.glob("*.yml") if p.is_file())
    for role_dir in sorted((_COLLECTION_ROOT / "roles").iterdir()):
        if not role_dir.is_dir():
            continue
        for sub in ("tasks", "handlers"):
            subdir = role_dir / sub
            if subdir.is_dir():
                files += sorted(p for p in subdir.rglob("*") if p.is_file() and p.suffix in _TASK_FILE_SUFFIXES)
    return [p for p in files if p.suffix in _TASK_FILE_SUFFIXES]


def _iter_task_dicts(entries):
    """Recursively yield task dicts from a document, play section, or block section."""
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        yield entry
        for section in _TASK_LIST_SECTIONS:
            subtasks = entry.get(section)
            if isinstance(subtasks, list):
                yield from _iter_task_dicts(subtasks)


def _conditional_strings(task: dict):
    """Yield (field, value) for every conditional expression string in a task dict."""
    for field in _CONDITIONAL_FIELDS:
        value = task.get(field)
        if isinstance(value, str):
            yield field, value
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, str):
                    yield field, item

    assert_value = task.get("assert")
    if isinstance(assert_value, dict):
        that = assert_value.get("that")
        if isinstance(that, str):
            yield "assert.that", that
        elif isinstance(that, list):
            for item in that:
                if isinstance(item, str):
                    yield "assert.that", item


def _find_violations(path: Path) -> list[str]:
    """Return a readable violation for every conditional containing template delimiters."""
    violations = []
    try:
        parsed = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        # Malformed YAML is out of scope here; ansible syntax checks cover it
        return violations

    if not isinstance(parsed, list):
        return violations

    for task in _iter_task_dicts(parsed):
        name = task.get("name", "<unnamed task>")
        for field, value in _conditional_strings(task):
            if "{{" in value:
                violations.append(f"{path.relative_to(_COLLECTION_ROOT)}: task '{name}' has {{{{ in {field}: {value.strip()}")
    return violations


@pytest.mark.parametrize(
    "task_file",
    _task_files(),
    ids=lambda p: str(p.relative_to(_COLLECTION_ROOT)),
)
def test_no_template_delimiters_in_conditionals(task_file: Path):
    """Test that no conditional expression contains template delimiters.

    GIVEN a task or playbook file in the collection
    WHEN its when/until/failed_when/changed_when/assert.that expressions are scanned
    THEN none of them contains {{ }}, which ansible-core >= 2.19 rejects as a syntax
    error when the conditional is evaluated at task runtime.
    """
    violations = _find_violations(task_file)
    assert not violations, "Template delimiters are not supported in expressions:\n" + "\n".join(violations)
