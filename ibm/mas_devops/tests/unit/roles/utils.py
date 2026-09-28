"""
Utilities for role unit tests.

Provides helpers for running Ansible task files as subprocesses against a
FakeKubernetesServer, following the same pattern used in the watcher
integration tests.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from mocks.fake_k8s_server import FakeKubernetesServer

# Root of the ibm/mas_devops collection — two levels up from tests/unit/roles/
_ROLES_ROOT = Path(__file__).parent.parent.parent.parent / "roles"

_ANSIBLE_PLAYBOOK = str(Path(sys.executable).parent / "ansible-playbook")


def _coerce_variable(value: Any) -> Any:
    """Coerce a variable value for embedding in a playbook vars block.

    JSON strings that represent dicts or lists are parsed back to native Python
    so they are emitted as proper YAML structures (not quoted strings) and
    Ansible receives them as the correct types.

    Args:
        value: The variable value to coerce

    Returns:
        The coerced value — a parsed dict/list if the input was a JSON string,
        otherwise the original value unchanged
    """
    if isinstance(value, str):
        stripped = value.strip()
        if stripped.startswith(("{", "[")):
            try:
                return json.loads(stripped)
            except json.JSONDecodeError:
                pass
    return value


def run_task(
    task_file: str,
    fake_k8s: FakeKubernetesServer,
    variables: Optional[Dict[str, Any]] = None,
    timeout: int = 60,
) -> subprocess.CompletedProcess:
    """Run an Ansible task file against a fake Kubernetes server.

    Wraps the task file in a minimal localhost playbook and executes it as a
    subprocess with KUBECONFIG set to the fake server's kubeconfig. Variables
    are serialised as proper YAML so complex types (dicts, lists) are passed
    correctly to Ansible.

    Args:
        task_file (str): Absolute path to the task YAML file to run
        fake_k8s (FakeKubernetesServer): Running fake server; provides kubeconfig_path
        variables (dict, optional): Extra variables passed to the playbook. Dict and
            list values, or JSON strings representing them, are embedded as structured
            YAML rather than quoted strings. Defaults to None.
        timeout (int, optional): Subprocess timeout in seconds. Defaults to 60.

    Returns:
        subprocess.CompletedProcess: The completed process result. Check
            returncode == 0 for success; stdout and stderr contain Ansible output.
    """
    # Derive role_path from task_file if under roles/
    vars_dict: Dict[str, Any] = {}
    try:
        task_path_obj = Path(task_file).resolve()
        if "roles" in task_path_obj.parts:
            roles_idx = task_path_obj.parts.index("roles")
            role_dir = Path(*task_path_obj.parts[: roles_idx + 2])
            vars_dict["role_path"] = str(role_dir)
    except Exception:
        pass

    playbook: Dict[str, Any] = {
        "hosts": "localhost",
        "gather_facts": False,
        "connection": "local",
        "tasks": [
            {"ansible.builtin.include_tasks": {"file": task_file}},
        ],
    }

    if variables:
        vars_dict.update({k: _coerce_variable(v) for k, v in variables.items()})

    if vars_dict:
        playbook["vars"] = vars_dict

    playbook_content = yaml.dump([playbook], default_flow_style=False, allow_unicode=True)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        f.write(playbook_content)
        playbook_path = f.name

    try:
        env = {
            **os.environ,
            "KUBECONFIG": fake_k8s.kubeconfig_path,
            "ANSIBLE_DEPRECATION_WARNINGS": "False",
            "ANSIBLE_LOCALHOST_WARNING": "False",
        }
        return subprocess.run(
            [_ANSIBLE_PLAYBOOK, "-i", "localhost ansible_connection=local,", playbook_path],
            capture_output=True,
            text=True,
            env=env,
            timeout=timeout,
        )
    finally:
        os.unlink(playbook_path)


def task_path(role: str, *relative_parts: str) -> str:
    """Resolve the absolute path to a task file within a role.

    Args:
        role (str): Role directory name (e.g. "aiservice_upgrade")
        *relative_parts (str): Path components below the role's tasks/ directory
            (e.g. "tenant", "delete_truststore_operator.yaml")

    Returns:
        str: Absolute path to the task file
    """
    return str(_ROLES_ROOT / role / "tasks" / Path(*relative_parts))
