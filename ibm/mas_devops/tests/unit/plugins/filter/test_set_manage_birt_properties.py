"""
Unit tests for setManageBirtProperties filter.
"""

from filters import setManageBirtProperties


class TestSetManageBirtProperties:
    """Test suite for the setManageBirtProperties filter function."""

    def test_adds_report_bundle_when_missing(self):
        """A report bundle is appended when no report bundle exists."""
        data = [
            {"bundleType": "all", "name": "d--sb0"},
        ]
        result = setManageBirtProperties(data, "https://rpt.manage.example.com", "rpt")
        assert len(result) == 2
        rpt_bundles = [sb for sb in result if sb["bundleType"] == "report"]
        assert len(rpt_bundles) == 1
        assert rpt_bundles[0]["name"] == "rpt"
        assert rpt_bundles[0]["routeSubDomain"] == "rpt"
        assert rpt_bundles[0]["replica"] == 1

    def test_does_not_duplicate_report_bundle(self):
        """An existing report bundle is not duplicated."""
        data = [
            {"bundleType": "all", "name": "d--sb0"},
            {"bundleType": "report", "name": "rpt"},
        ]
        result = setManageBirtProperties(data, "https://rpt.manage.example.com", "rpt")
        rpt_bundles = [sb for sb in result if sb["bundleType"] == "report"]
        assert len(rpt_bundles) == 1

    def test_properties_use_newline_separator(self):
        """Bundle level properties are newline-separated, not space-separated."""
        data = [
            {"bundleType": "all", "name": "d--sb0"},
        ]
        result = setManageBirtProperties(data, "https://rpt.manage.example.com", "rpt")
        for sb in result:
            assert "mxe.report.birt.viewerurl=https://rpt.manage.example.com" in sb["bundleLevelProperties"]
            assert "\nmxe.report.birt.disablequeuemanager=" in sb["bundleLevelProperties"]

    def test_disablequeuemanager_per_bundle_type(self):
        """disablequeuemanager is 0 for report bundles and 1 for other bundles."""
        data = [
            {"bundleType": "all", "name": "d--sb0"},
        ]
        result = setManageBirtProperties(data, "https://rpt.manage.example.com", "rpt")
        for sb in result:
            expected = 0 if sb["bundleType"] == "report" else 1
            assert f"mxe.report.birt.disablequeuemanager={expected}" in sb["bundleLevelProperties"]

    def test_appends_to_existing_properties(self):
        """Properties are appended to existing bundleLevelProperties with a newline."""
        data = [
            {"bundleType": "all", "name": "d--sb0", "bundleLevelProperties": "mxe.some.prop=1"},
        ]
        result = setManageBirtProperties(data, "https://rpt.manage.example.com", "rpt")
        existing = [sb for sb in result if sb["name"] == "d--sb0"]
        assert len(existing) == 1
        assert existing[0]["bundleLevelProperties"].startswith("mxe.some.prop=1\n")

    def test_idempotent(self):
        """Applying the filter twice does not duplicate the properties."""
        data = [
            {"bundleType": "all", "name": "d--sb0"},
        ]
        once = setManageBirtProperties(data, "https://rpt.manage.example.com", "rpt")
        twice = setManageBirtProperties(once, "https://rpt.manage.example.com", "rpt")
        for sb in twice:
            assert sb["bundleLevelProperties"].count("mxe.report.birt.viewerurl=") == 1
            assert sb["bundleLevelProperties"].count("mxe.report.birt.disablequeuemanager=") == 1
