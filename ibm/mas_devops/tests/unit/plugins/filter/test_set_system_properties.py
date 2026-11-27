"""
Unit tests for setSystemProperties filter.
"""

from filters import _setSystemProperties as setSystemProperties


class TestSetSystemProperties:
    """Test suite for the setSystemProperties filter function."""

    def test_properties_use_newline_separator(self):
        """Bundle level properties are newline-separated, not space-separated."""
        data = [
            {"bundleType": "all", "name": "d--sb0"},
        ]
        result = setSystemProperties(
            data,
            "https://main.manage.example.com/meaweb",
            "https://main.manage.example.com/maxrest/oslc",
            "https://main.manage.example.com/maximo/oslc",
            "https://main.manage.example.com/maxrest",
        )
        for sb in result:
            props = sb["bundleLevelProperties"]
            assert "mxe.int.webappurl=https://main.manage.example.com/meaweb" in props
            assert "\nmxe.oslc.restwebappurl=" in props
            assert "\nmxe.oslc.webappurl=" in props
            assert "\nmxe.rest.webappurl=" in props

    def test_appends_to_existing_properties(self):
        """Properties are appended to existing bundleLevelProperties with a newline."""
        data = [
            {"bundleType": "all", "name": "d--sb0", "bundleLevelProperties": "mxe.some.prop=1"},
        ]
        result = setSystemProperties(data, "a", "b", "c", "d")
        assert result[0]["bundleLevelProperties"].startswith("mxe.some.prop=1\n")

    def test_idempotent(self):
        """Applying the filter twice does not duplicate the properties."""
        data = [
            {"bundleType": "all", "name": "d--sb0"},
        ]
        once = setSystemProperties(data, "a", "b", "c", "d")
        twice = setSystemProperties(once, "a", "b", "c", "d")
        for sb in twice:
            assert sb["bundleLevelProperties"].count("mxe.int.webappurl=") == 1
            assert sb["bundleLevelProperties"].count("mxe.rest.webappurl=") == 1

    def test_all_bundles_updated(self):
        """Every bundle in the list receives the properties."""
        data = [
            {"bundleType": "all", "name": "d--sb0"},
            {"bundleType": "report", "name": "rpt"},
        ]
        result = setSystemProperties(data, "a", "b", "c", "d")
        assert len(result) == 2
        for sb in result:
            assert "mxe.int.webappurl=" in sb["bundleLevelProperties"]
