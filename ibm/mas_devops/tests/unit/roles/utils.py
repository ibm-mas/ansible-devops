"""
Utilities for role unit tests.

Provides helpers for running Ansible task files as subprocesses against a
FakeKubernetesServer, following the same pattern used in the watcher
integration tests.
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

from mocks.fake_k8s_server import FakeKubernetesServer

# Root of the ibm/mas_devops collection — two levels up from tests/unit/roles/
_ROLES_ROOT = Path(__file__).parent.parent.parent.parent / "roles"

_ANSIBLE_PLAYBOOK = str(Path(sys.executable).parent / "ansible-playbook")


def run_task(task_file: str, fake_k8s: FakeKubernetesServer, variables: dict = None) -> subprocess.CompletedProcess:
    """Run an Ansible task file against a fake Kubernetes server.

    Wraps the task file in a minimal localhost playbook and executes it as a
    subprocess with KUBECONFIG set to the fake server's kubeconfig.

    Args:
        task_file (str): Absolute path to the task YAML file to run
        kubeconfig_path (str): Path to the kubeconfig pointing at the fake server
        variables (dict, optional): Extra variables passed to the playbook. Defaults to None.

    Returns:
        subprocess.CompletedProcess: The completed process result. Check
            returncode == 0 for success; stdout and stderr contain Ansible output.
    """
    vars_lines = ""
    if variables:
        vars_lines = "  vars:\n" + "".join(f"    {k}: \"{v}\"\n" for k, v in variables.items())

    playbook_content = (
        f"- hosts: localhost\n"
        f"  gather_facts: false\n"
        f"  connection: local\n"
        f"  tasks:\n"
        f"    - ansible.builtin.include_tasks:\n"
        f"        file: \"{task_file}\"\n"
        + vars_lines
    )

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
            timeout=60,
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
