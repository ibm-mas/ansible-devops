"""
Unit tests for backup_resource action plugin.
"""

import pytest
from unittest.mock import Mock, patch
from ansible.errors import AnsibleError

import backup_resource

ActionModule = backup_resource.ActionModule


class TestBackupResource:
    """Test cases for backup_resource action plugin."""

    @pytest.fixture
    def action_module(self, action_module_base):
        """Create ActionModule instance."""
        module = ActionModule(**action_module_base)
        return module

    def test_missing_backup_resources_raises_error(self, action_module):
        """Test that missing backup_resources raises AnsibleError."""
        action_module._task.args = {
            "backup_path": "/tmp/backup",
        }
        with pytest.raises(AnsibleError, match="backup_resources argument must be provided as a list"):
            with patch("backup_resource.get_api_client", return_value=Mock()):
                action_module.run()

    def test_missing_backup_path_raises_error(self, action_module):
        """Test that missing backup_path raises AnsibleError."""
        action_module._task.args = {
            "backup_resources": [{"namespace": "mas-inst1-core", "resources": []}],
        }
        with pytest.raises(AnsibleError, match="backup_path argument was not provided"):
            with patch("backup_resource.get_api_client", return_value=Mock()):
                action_module.run()

    def test_missing_api_version_raises_error(self, action_module):
        """Test that missing api_version in resource definition raises AnsibleError."""
        action_module._task.args = {
            "backup_path": "/tmp/backup",
            "backup_resources": [
                {
                    "namespace": "mas-inst1-core",
                    "resources": [{"kind": "Suite", "name": "inst1"}],
                }
            ],
        }
        with pytest.raises(AnsibleError, match="api_version is required"):
            with patch("backup_resource.get_api_client", return_value=Mock()):
                action_module.run()

    def test_strict_named_only_rejects_unnamed_resource(self, action_module):
        """Test that strict_named_only fails when resource name is missing."""
        action_module._task.args = {
            "backup_path": "/tmp/backup",
            "strict_named_only": True,
            "backup_resources": [
                {
                    "namespace": "mas-inst1-core",
                    "resources": [
                        {
                            "kind": "Suite",
                            "api_version": "core.mas.ibm.com/v1",
                        }
                    ],
                }
            ],
        }
        with patch("backup_resource.get_api_client", return_value=Mock()):
            result = action_module.run()

        assert result["failed"] is True
        assert result["success"] is False
        assert result["failed_count"] == 1
        assert len(result["failed_resources"]) == 1
        assert result["failed_resources"][0]["name"] == "unnamed"
        assert result["failed_resources"][0]["kind"] == "Suite"

    def test_strict_named_only_succeeds_with_named_resource(self, action_module):
        """Test that strict_named_only succeeds when all resources have names."""
        action_module._task.args = {
            "backup_path": "/tmp/backup",
            "strict_named_only": True,
            "auto_discover_secrets": False,
            "backup_resources": [
                {
                    "namespace": "mas-inst1-core",
                    "resources": [
                        {
                            "kind": "Suite",
                            "api_version": "core.mas.ibm.com/v1",
                            "name": "inst1",
                        }
                    ],
                }
            ],
        }
        mock_backup = Mock(return_value=(1, 0, 0, set()))
        with patch("backup_resource.get_api_client", return_value=Mock()), patch("backup_resource.backupResources", mock_backup):
            result = action_module.run()

        assert result["failed"] is False
        assert result["success"] is True
        assert result["backed_up_count"] == 1
        mock_backup.assert_called_once()
        _, kwargs = mock_backup.call_args
        assert kwargs["strict_named_only"] is True
        assert kwargs["name"] == "inst1"

    def test_auto_discover_secrets_enabled_non_strict(self, action_module):
        """Test that auto-discovered secrets are backed up in non-strict mode."""
        action_module._task.args = {
            "backup_path": "/tmp/backup",
            "strict_named_only": False,
            "auto_discover_secrets": True,
            "backup_resources": [
                {
                    "namespace": "mas-inst1-core",
                    "resources": [
                        {
                            "kind": "MongoCfg",
                            "api_version": "config.mas.ibm.com/v1",
                            "name": "inst1-mongo-system",
                        }
                    ],
                }
            ],
        }

        # First call backs up MongoCfg and discovers secret 'mongo-admin-secret'
        # Second call backs up the discovered secret
        def mock_backup_fn(*args, **kwargs):
            kind = args[1]
            if kind == "MongoCfg":
                return (1, 0, 0, {"mongo-admin-secret"})
            elif kind == "Secret":
                return (1, 0, 0, set())
            return (0, 0, 0, set())

        with patch("backup_resource.get_api_client", return_value=Mock()), patch("backup_resource.backupResources", side_effect=mock_backup_fn) as mock_backup:
            result = action_module.run()

        assert result["failed"] is False
        assert result["success"] is True
        assert result["backed_up_count"] == 2
        assert result["discovered_secrets_count"] == 1
        assert "mongo-admin-secret" in result["discovered_secrets"]
        assert mock_backup.call_count == 2

    def test_strict_named_only_forces_secret_discovery_off(self, action_module):
        """Strict mode must never auto-discover Secrets, even if auto_discover_secrets=True is requested."""
        action_module._task.args = {
            "backup_path": "/tmp/backup",
            "strict_named_only": True,
            "auto_discover_secrets": True,
            "backup_resources": [
                {
                    "namespace": "cert-manager",
                    "resources": [{"kind": "Certificate", "api_version": "cert-manager.io/v1", "name": "inst1-cert-internal-ca"}],
                }
            ],
        }
        # Even if the library reports a CA key-pair secretName, it must not be fetched
        mock_backup = Mock(return_value=(1, 0, 0, {"inst1-cert-internal-ca"}))
        with patch("backup_resource.get_api_client", return_value=Mock()), patch("backup_resource.backupResources", mock_backup):
            result = action_module.run()

        assert mock_backup.call_count == 1
        _, kwargs = mock_backup.call_args
        assert kwargs["strict_named_only"] is True
        assert kwargs["auto_discover_secrets"] is False
        assert result["backed_up_count"] == 1

    def test_auto_discover_secrets_disabled(self, action_module):
        """Test that auto-discovered secrets are not backed up when auto_discover_secrets=False."""
        action_module._task.args = {
            "backup_path": "/tmp/backup",
            "strict_named_only": True,
            "auto_discover_secrets": False,
            "backup_resources": [
                {
                    "namespace": "mas-inst1-core",
                    "resources": [
                        {
                            "kind": "MongoCfg",
                            "api_version": "config.mas.ibm.com/v1",
                            "name": "inst1-mongo-system",
                        }
                    ],
                }
            ],
        }

        mock_backup = Mock(return_value=(1, 0, 0, set()))
        with patch("backup_resource.get_api_client", return_value=Mock()), patch("backup_resource.backupResources", mock_backup):
            result = action_module.run()

        assert result["failed"] is False
        assert result["success"] is True
        assert result["backed_up_count"] == 1
        assert mock_backup.call_count == 1

    def test_secret_deduplication_prevents_duplicate_backup(self, action_module):
        """Test that explicitly listed Secrets are not backed up again when auto-discovered."""
        action_module._task.args = {
            "backup_path": "/tmp/backup",
            "strict_named_only": True,
            "auto_discover_secrets": True,
            "backup_resources": [
                {
                    "namespace": "mas-inst1-core",
                    "resources": [
                        {
                            "kind": "Secret",
                            "api_version": "v1",
                            "name": "mongo-admin-secret",
                        },
                        {
                            "kind": "MongoCfg",
                            "api_version": "config.mas.ibm.com/v1",
                            "name": "inst1-mongo-system",
                        },
                    ],
                }
            ],
        }

        # First call backs up Secret explicitly (returns 1, 0, 0, set())
        # Second call backs up MongoCfg and discovers 'mongo-admin-secret' (returns 1, 0, 0, {'mongo-admin-secret'})
        # The auto-discovery step should SKIP backing up 'mongo-admin-secret' again because it was explicitly listed.
        def mock_backup_fn(*args, **kwargs):
            kind = args[1]
            if kind == "Secret":
                return (1, 0, 0, set())
            elif kind == "MongoCfg":
                return (1, 0, 0, {"mongo-admin-secret"})
            return (0, 0, 0, set())

        with patch("backup_resource.get_api_client", return_value=Mock()), patch("backup_resource.backupResources", side_effect=mock_backup_fn) as mock_backup:
            result = action_module.run()

        assert result["failed"] is False
        assert result["success"] is True
        # Total backed up should be 2 (Secret once + MongoCfg once), NOT 3
        assert result["backed_up_count"] == 2
        assert result["discovered_secrets_count"] == 1
        assert "mongo-admin-secret" in result["discovered_secrets"]
        # Exactly 2 calls: 1 for explicit Secret, 1 for MongoCfg, 0 extra for discovered Secret
        assert mock_backup.call_count == 2

    def test_backward_compatibility_with_older_mas_devops(self, action_module):
        """Test that older mas-devops signatures without new kwargs do not fail with TypeError."""
        action_module._task.args = {
            "backup_path": "/tmp/backup",
            "strict_named_only": False,
            "auto_discover_secrets": True,
            "backup_resources": [
                {
                    "namespace": "mas-inst1-core",
                    "resources": [
                        {
                            "kind": "Suite",
                            "api_version": "core.mas.ibm.com/v1",
                            "name": "inst1",
                        }
                    ],
                }
            ],
        }

        # Simulate older mas-devops backupResources function that rejects strict_named_only / auto_discover_secrets kwargs
        def older_backup_resources(dynClient, kind, api_version, backup_path, namespace=None, name=None, labels=None):
            return (1, 0, 0, set())

        with patch("backup_resource.get_api_client", return_value=Mock()), patch("backup_resource.backupResources", side_effect=older_backup_resources):
            result = action_module.run()

        assert result["failed"] is False
        assert result["success"] is True
        assert result["backed_up_count"] == 1

    def test_strict_fails_clearly_when_library_lacks_strict_support(self, action_module):
        """Strict mode must raise, never silently fall back to broad GET behavior, on an incompatible mas-devops."""
        action_module._task.args = {
            "backup_path": "/tmp/backup",
            "strict_named_only": True,
            "backup_resources": [{"namespace": "mas-inst1-core", "resources": [{"kind": "Suite", "api_version": "core.mas.ibm.com/v1", "name": "inst1"}]}],
        }
        calls = []

        def older_backup_resources(dynClient, kind, api_version, backup_path, namespace=None, name=None, labels=None):
            calls.append((kind, name))
            return (1, 0, 0, set())

        with patch("backup_resource.get_api_client", return_value=Mock()), patch("backup_resource.backupResources", new=older_backup_resources):
            with pytest.raises(AnsibleError, match="Strict named-only backup requires a mas-devops release"):
                action_module.run()
        assert calls == []

    def test_missing_named_resource_is_reported(self, action_module):
        """Named resources that do not exist are listed in not_found_resources and do not fail the backup."""
        action_module._task.args = {
            "backup_path": "/tmp/backup",
            "strict_named_only": True,
            "backup_resources": [
                {
                    "namespace": "mas-inst1-manage",
                    "resources": [
                        {"kind": "ConfigMap", "api_version": "v1", "name": "maximo-config"},
                        {"kind": "ConfigMap", "api_version": "v1", "name": "absent-cm"},
                    ],
                }
            ],
        }

        def fake(dynClient, kind, api_version, backup_path, namespace=None, name=None, labels=None, **kwargs):
            return (0, 1, 0, set()) if name == "absent-cm" else (1, 0, 0, set())

        with patch("backup_resource.get_api_client", return_value=Mock()), patch("backup_resource.backupResources", side_effect=fake):
            result = action_module.run()

        assert result["failed"] is False
        assert result["backed_up_count"] == 1
        assert result["not_found_count"] == 1
        assert result["not_found_resources"] == [
            {"scope": "mas-inst1-manage", "kind": "ConfigMap", "name": "absent-cm", "api_version": "v1", "required": False}
        ]

    def test_missing_required_resource_fails_backup(self, action_module):
        """A required resource (e.g. ManageWorkspace, encryption Secrets) that is missing fails the backup."""
        action_module._task.args = {
            "backup_path": "/tmp/backup",
            "strict_named_only": True,
            "backup_resources": [
                {
                    "namespace": "mas-inst1-manage",
                    "resources": [{"kind": "Secret", "api_version": "v1", "name": "masdev-manage-encryption-secret", "required": True}],
                }
            ],
        }
        with patch("backup_resource.get_api_client", return_value=Mock()), patch("backup_resource.backupResources", return_value=(0, 1, 0, set())):
            result = action_module.run()

        assert result["failed"] is True
        assert result["failed_count"] == 1
        assert result["not_found_resources"][0]["required"] is True
        assert "required resource not found" in result["failed_resources"][0]["description"]


class FakeResource(dict):
    """Minimal stand-in for a kubernetes dynamic resource."""

    def to_dict(self):
        return dict(self)


def _fakeDynClient(store):
    """Dynamic client whose get(name=, namespace=) serves objects from store[(kind, namespace, name)]."""
    from kubernetes.dynamic.exceptions import NotFoundError

    def resourcesGet(api_version=None, kind=None):
        api = Mock()

        def get(name=None, namespace=None, **kwargs):
            if name is None:
                raise AssertionError(f"unnamed GET issued for {kind} (strict mode must never list)")
            try:
                return FakeResource(store[(kind, namespace, name)])
            except KeyError:
                raise NotFoundError(Mock(status=404, reason="NotFound", data="{}", getheader=lambda *a: None))

        api.get.side_effect = get
        return api

    client = Mock()
    client.resources.get.side_effect = resourcesGet
    return client


class TestBackupCoverageEndToEnd:
    """Real backupResources() against a fake cluster: CRs, Secrets, ConfigMaps, CRDs, plus missing + collision handling."""

    @pytest.fixture
    def action_module(self, action_module_base):
        return ActionModule(**action_module_base)

    def _obj(self, kind, ns, name, **extra):
        meta = {"name": name}
        if ns:
            meta["namespace"] = ns
        return {"kind": kind, "metadata": meta, **extra}

    def test_strict_backup_covers_cr_secret_configmap_crd_and_reports_missing(self, action_module, tmp_path):
        core, manage = "mas-fvtsaas-core", "mas-fvtsaas-manage"
        store = {
            ("Suite", core, "fvtsaas"): self._obj("Suite", core, "fvtsaas", spec={"settings": {"secretName": "should-not-be-discovered"}}),
            ("Workspace", core, "fvtsaas-masdev"): self._obj("Workspace", core, "fvtsaas-masdev", spec={}),
            ("Secret", core, "fvtsaas-keys-jwt"): self._obj("Secret", core, "fvtsaas-keys-jwt", data={"k": "v"}),
            ("ConfigMap", core, "fvtsaas-nps"): self._obj("ConfigMap", core, "fvtsaas-nps", data={"a": "b"}),
            ("CustomResourceDefinition", None, "suites.core.mas.ibm.com"): self._obj("CustomResourceDefinition", None, "suites.core.mas.ibm.com", spec={}),
            ("Secret", manage, "masdev-manage-encryption-secret"): self._obj("Secret", manage, "masdev-manage-encryption-secret", data={"k": "v"}),
            ("ManageWorkspace", manage, "fvtsaas-masdev"): self._obj("ManageWorkspace", manage, "fvtsaas-masdev", spec={}),
        }
        action_module._task.args = {
            "backup_path": str(tmp_path),
            "strict_named_only": True,
            "auto_discover_secrets": True,
            "backup_resources": [
                {
                    "namespace": core,
                    "resources": [
                        {"kind": "Suite", "api_version": "core.mas.ibm.com/v1", "name": "fvtsaas"},
                        {"kind": "Workspace", "api_version": "core.mas.ibm.com/v1", "name": "fvtsaas-masdev"},
                        {"kind": "Secret", "api_version": "v1", "name": "fvtsaas-keys-jwt"},
                        {"kind": "ConfigMap", "api_version": "v1", "name": "fvtsaas-nps"},
                        {"kind": "ConfigMap", "api_version": "v1", "name": "fvtsaas-catalog-items"},
                    ],
                },
                {
                    "namespace": manage,
                    "resources": [
                        {"kind": "ManageWorkspace", "api_version": "apps.mas.ibm.com/v1", "name": "fvtsaas-masdev", "required": True},
                        {"kind": "Secret", "api_version": "v1", "name": "masdev-manage-encryption-secret", "required": True},
                    ],
                },
                {"resources": [{"kind": "CustomResourceDefinition", "api_version": "apiextensions.k8s.io/v1", "name": "suites.core.mas.ibm.com"}]},
            ],
        }
        with patch("backup_resource.get_api_client", return_value=_fakeDynClient(store)):
            result = action_module.run()

        assert result["failed"] is False, result
        assert result["backed_up_count"] == 7
        assert result["not_found_count"] == 1
        assert result["discovered_secrets"] == []  # strict path performs no Secret discovery
        res = tmp_path / "resources"
        for rel in (
            "suites/fvtsaas.yaml",
            "workspaces/fvtsaas-masdev.yaml",
            "secrets/fvtsaas-keys-jwt.yaml",
            "secrets/masdev-manage-encryption-secret.yaml",
            "configmaps/fvtsaas-nps.yaml",
            "manageworkspaces/fvtsaas-masdev.yaml",
            "customresourcedefinitions/suites.core.mas.ibm.com.yaml",
        ):
            assert (res / rel).exists(), rel
        assert not (res / "secrets" / "should-not-be-discovered.yaml").exists()
        assert [(r["kind"], r["name"]) for r in result["not_found_resources"]] == [("ConfigMap", "fvtsaas-catalog-items")]

    def test_same_named_secret_in_two_namespaces_is_not_silently_overwritten(self, action_module, tmp_path):
        store = {
            ("Secret", "ns-a", "dup"): self._obj("Secret", "ns-a", "dup", data={"v": "A"}),
            ("Secret", "ns-b", "dup"): self._obj("Secret", "ns-b", "dup", data={"v": "B"}),
        }
        action_module._task.args = {
            "backup_path": str(tmp_path),
            "strict_named_only": True,
            "backup_resources": [
                {"namespace": "ns-a", "resources": [{"kind": "Secret", "api_version": "v1", "name": "dup"}]},
                {"namespace": "ns-b", "resources": [{"kind": "Secret", "api_version": "v1", "name": "dup"}]},
            ],
        }
        with patch("backup_resource.get_api_client", return_value=_fakeDynClient(store)):
            result = action_module.run()

        assert result["failed"] is True
        assert result["backed_up_count"] == 1
        assert result["failed_count"] == 1
        saved = (tmp_path / "resources" / "secrets" / "dup.yaml").read_text()
        assert "ns-a" in saved and "ns-b" not in saved
