"""Unit tests for variable precedence in the suite_app_config and suite_app_install roles.

Regression tests for ibm-mas/ansible-devops#519. Environment variable lookups in a role's
vars/ files override values set by the user (include_vars has higher precedence than play
vars), so they must live in defaults/ instead. These tests load the real defaults and vars
files in the same precedence order the roles use and check what a user ends up with.
"""

import json
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

import pytest
import yaml
from utils import _ANSIBLE_PLAYBOOK, _ROLES_ROOT, _collections_tmp

CONFIG_ROLE = _ROLES_ROOT / "suite_app_config"
INSTALL_ROLE = _ROLES_ROOT / "suite_app_install"
ENV_LOOKUP = re.compile(r"lookup\(\s*['\"]env['\"]")

# Environment variables that could leak in from the developer's shell and skew results
CLEARED_ENV_PREFIXES = ("MAS_APP_", "MAS_APPWS_", "PREDICT_")


def _resolve(
    role: Path,
    varsFile: Path,
    names: list,
    playVars: Optional[Dict[str, Any]] = None,
    env: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Resolve variables the way a role does when it loads a vars file.

    Builds a temporary role whose defaults/main.yml is a copy of the real role's defaults
    and whose tasks load the real vars file with include_vars, then runs it from a play
    carrying the user's play vars.

    Args:
        role (Path): The real role directory providing defaults/main.yml
        varsFile (Path): The real vars file loaded with include_vars
        names (list): Names of the variables to resolve and return
        playVars (dict, optional): Variables set by the user at play level. Defaults to None.
        env (dict, optional): Environment variables set for the run. Defaults to None.

    Returns:
        dict: Resolved variable values keyed by name

    Raises:
        AssertionError: If the playbook run fails
    """
    with tempfile.TemporaryDirectory(prefix="vars_precedence_") as tmp:
        tmpPath = Path(tmp)
        roleDir = tmpPath / "roles" / "varstest"
        (roleDir / "defaults").mkdir(parents=True)
        (roleDir / "tasks").mkdir()
        (roleDir / "defaults" / "main.yml").write_text((role / "defaults" / "main.yml").read_text())

        outFile = tmpPath / "out.json"
        report = "{" + ", ".join(f"'{name}': {name}" for name in names) + "}"
        tasks = [
            {"ansible.builtin.include_vars": str(varsFile)},
            {
                "ansible.builtin.copy": {
                    "dest": str(outFile),
                    "content": "{{ " + report + " | to_json }}",
                }
            },
        ]
        (roleDir / "tasks" / "main.yml").write_text(yaml.dump(tasks))

        play = {
            "hosts": "localhost",
            "gather_facts": False,
            "connection": "local",
            "vars": {"mas_instance_id": "test", "mas_workspace_id": "main", **(playVars or {})},
            "roles": ["varstest"],
        }
        playbook = tmpPath / "play.yml"
        playbook.write_text(yaml.dump([play]))

        runEnv = {k: v for k, v in os.environ.items() if not k.startswith(CLEARED_ENV_PREFIXES)}
        runEnv.update(
            {
                "ANSIBLE_ROLES_PATH": str(tmpPath / "roles"),
                "ANSIBLE_COLLECTIONS_PATH": str(_collections_tmp),
                "ANSIBLE_DEPRECATION_WARNINGS": "False",
                "ANSIBLE_LOCALHOST_WARNING": "False",
                **(env or {}),
            }
        )
        result = subprocess.run(
            [_ANSIBLE_PLAYBOOK, "-i", "localhost,", str(playbook)],
            capture_output=True,
            text=True,
            env=runEnv,
            timeout=120,
        )
        assert result.returncode == 0, f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        return json.loads(outFile.read_text())


def _configVars(app: str, names: list, playVars=None, env=None) -> Dict[str, Any]:
    """Resolve suite_app_config variables for an application."""
    return _resolve(CONFIG_ROLE, CONFIG_ROLE / "vars" / f"{app}.yml", names, playVars, env)


class TestNoEnvLookupsInVarsFiles:
    """Vars files must not contain environment variable lookups."""

    @pytest.mark.parametrize("role", [CONFIG_ROLE, INSTALL_ROLE], ids=lambda r: r.name)
    def test_vars_files_have_no_env_lookups(self, role):
        """Test no top-level vars file performs an environment variable lookup.

        GIVEN the vars/ files of a role
        WHEN they are scanned for lookup('env', ...)
        THEN none are found, because they would override user-supplied variables.
        """
        offenders = [
            f"{f.relative_to(_ROLES_ROOT)}:{n}"
            for f in sorted((role / "vars").glob("*.yml"))
            for n, line in enumerate(f.read_text().splitlines(), 1)
            if ENV_LOOKUP.search(line)
        ]
        assert offenders == []


class TestManageSettingsPrecedence:
    """Tests for Manage settings that moved from vars/manage.yml to defaults/main.yml."""

    def test_defaults_apply(self):
        """Test defaults are used when nothing is set."""
        result = _configVars("manage", ["mas_app_settings_aio_flag", "mas_app_settings_server_bundles_size"])
        assert result == {"mas_app_settings_aio_flag": True, "mas_app_settings_server_bundles_size": "dev"}

    def test_env_var_applies(self):
        """Test the documented environment variable still sets the value."""
        result = _configVars("manage", ["mas_app_settings_aio_flag"], env={"MAS_APP_SETTINGS_AIO_FLAG": "false"})
        assert result["mas_app_settings_aio_flag"] is False

    def test_play_var_overrides_default(self):
        """Test a play var overrides the default (ansible-devops#519).

        GIVEN the user sets mas_app_settings_aio_flag in their play vars
        WHEN the Manage vars file is loaded with include_vars
        THEN the user's value is used rather than being replaced by an environment lookup.
        """
        result = _configVars("manage", ["mas_app_settings_aio_flag"], playVars={"mas_app_settings_aio_flag": False})
        assert result["mas_app_settings_aio_flag"] is False

    def test_play_var_beats_env_var(self):
        """Test a play var takes precedence over the environment variable."""
        result = _configVars(
            "manage",
            ["mas_app_settings_server_bundles_size"],
            playVars={"mas_app_settings_server_bundles_size": "small"},
            env={"MAS_APP_SETTINGS_SERVER_BUNDLES_SIZE": "jms"},
        )
        assert result["mas_app_settings_server_bundles_size"] == "small"


class TestConfigTimeouts:
    """Tests for mas_app_cfg_delay and mas_app_cfg_retries."""

    @pytest.mark.parametrize(
        "app, delay, retries",
        [
            ("manage", 240, 60),
            ("facilities", 360, 180),
            ("iot", 180, 30),
            ("monitor", 120, 30),
            ("predict", 120, 30),
            ("optimizer", 120, 30),
            ("visualinspection", 120, 30),
            ("assist", 120, 30),
        ],
    )
    def test_per_app_fallbacks(self, app, delay, retries):
        """Test each application falls back to its own timeouts."""
        result = _configVars(app, ["mas_app_cfg_delay", "mas_app_cfg_retries"])
        assert (int(result["mas_app_cfg_delay"]), int(result["mas_app_cfg_retries"])) == (delay, retries)

    def test_env_var_overrides_fallback(self):
        """Test MAS_APP_CFG_DELAY and MAS_APP_CFG_RETRIES override the per-app fallback."""
        result = _configVars(
            "facilities",
            ["mas_app_cfg_delay", "mas_app_cfg_retries"],
            env={"MAS_APP_CFG_DELAY": "5", "MAS_APP_CFG_RETRIES": "6"},
        )
        assert (int(result["mas_app_cfg_delay"]), int(result["mas_app_cfg_retries"])) == (5, 6)

    @pytest.mark.parametrize("app", ["manage", "iot"])
    def test_play_var_overrides_fallback(self, app):
        """Test play vars override both the fallback and the environment variable."""
        result = _configVars(
            app,
            ["mas_app_cfg_delay", "mas_app_cfg_retries"],
            playVars={"mas_app_cfg_delay": 7, "mas_app_cfg_retries": 8},
            env={"MAS_APP_CFG_DELAY": "5", "MAS_APP_CFG_RETRIES": "6"},
        )
        assert (int(result["mas_app_cfg_delay"]), int(result["mas_app_cfg_retries"])) == (7, 8)


class TestPredictDeploymentSize:
    """Tests for mas_app_settings_predict_deployment_size in suite_app_install."""

    @staticmethod
    def _size(playVars=None, env=None) -> str:
        """Resolve the Predict deployment size."""
        name = "mas_app_settings_predict_deployment_size"
        return _resolve(INSTALL_ROLE, INSTALL_ROLE / "vars" / "predict.yml", [name], playVars, env)[name]

    def test_default(self):
        """Test the default size is small."""
        assert self._size() == "small"

    def test_legacy_env_var(self):
        """Test the legacy PREDICT_DEPLOYMENT_SIZE environment variable still works."""
        assert self._size(env={"PREDICT_DEPLOYMENT_SIZE": "medium"}) == "medium"

    def test_new_env_var(self):
        """Test the MAS_APP_SETTINGS_PREDICT_DEPLOYMENT_SIZE environment variable works."""
        assert self._size(env={"MAS_APP_SETTINGS_PREDICT_DEPLOYMENT_SIZE": "large"}) == "large"

    def test_new_env_var_beats_legacy(self):
        """Test the new environment variable takes precedence over the legacy one."""
        env = {"MAS_APP_SETTINGS_PREDICT_DEPLOYMENT_SIZE": "large", "PREDICT_DEPLOYMENT_SIZE": "medium"}
        assert self._size(env=env) == "large"

    def test_play_var_overrides_env_vars(self):
        """Test a play var overrides both environment variables (ansible-devops#519)."""
        env = {"MAS_APP_SETTINGS_PREDICT_DEPLOYMENT_SIZE": "large", "PREDICT_DEPLOYMENT_SIZE": "medium"}
        assert self._size(playVars={"mas_app_settings_predict_deployment_size": "developer"}, env=env) == "developer"
