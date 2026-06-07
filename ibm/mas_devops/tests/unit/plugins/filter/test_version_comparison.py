"""
Unit tests for version comparison filters (strip_build_number and compare_versions_ignore_build).

These tests validate the version comparison logic used in suite_upgrade role to handle:
- Custom channel suffixes (e.g., -dev, -test1, -pre.maint90xdev)
- Build number suffixes (e.g., -28084)
- Feature channel format differences (+ vs -)
"""
import pytest

from filters import strip_build_number, compare_versions_ignore_build


class TestStripBuildNumber:
    """Tests for strip_build_number filter function."""

    def test_no_build_number(self):
        """Version without build number should remain unchanged."""
        assert strip_build_number("9.0.27") == "9.0.27"

    def test_with_build_number(self):
        """Build number suffix should be stripped."""
        assert strip_build_number("9.0.27-28084") == "9.0.27"

    def test_custom_suffix_no_build(self):
        """Custom text suffix should be preserved."""
        assert strip_build_number("9.0.27-dev") == "9.0.27-dev"
        assert strip_build_number("9.0.27-test1") == "9.0.27-test1"

    def test_custom_suffix_with_build(self):
        """Custom suffix preserved, build number stripped."""
        assert strip_build_number("9.0.27-dev-28084") == "9.0.27-dev"
        assert strip_build_number("9.1.0-test1-12345") == "9.1.0-test1"

    def test_complex_custom_suffix_no_build(self):
        """Complex custom suffix should be preserved."""
        assert strip_build_number("9.0.27-pre.maint90xdev") == "9.0.27-pre.maint90xdev"

    def test_complex_custom_suffix_with_build(self):
        """Complex custom suffix preserved, build number stripped."""
        assert strip_build_number("9.0.27-pre.maint90xdev-28084") == "9.0.27-pre.maint90xdev"

    def test_feature_channel_no_build(self):
        """Feature channel version should be preserved."""
        assert strip_build_number("9.1.0-pre.stable") == "9.1.0-pre.stable"

    def test_feature_channel_with_build(self):
        """Feature channel version preserved, build stripped."""
        assert strip_build_number("9.1.0-pre.stable-8193") == "9.1.0-pre.stable"
        assert strip_build_number("9.1.0-pre.stable-8193-28084") == "9.1.0-pre.stable-8193"

    def test_multiple_hyphens(self):
        """Only trailing numeric suffix should be stripped."""
        assert strip_build_number("9.2.0-feature-dev-28084") == "9.2.0-feature-dev"
        assert strip_build_number("9.2.0-feature-dev") == "9.2.0-feature-dev"


class TestCompareVersionsIgnoreBuild:
    """Tests for compare_versions_ignore_build filter function."""

    # GA Channel Tests (is_feature_channel=False)
    
    def test_ga_exact_match(self):
        """Exact version match should return True."""
        assert compare_versions_ignore_build("9.0.27", "9.0.27", False)

    def test_ga_with_build_number(self):
        """Version with build number should match base version."""
        assert compare_versions_ignore_build("9.0.27", "9.0.27-28084", False)

    def test_ga_different_versions(self):
        """Different versions should not match."""
        assert not compare_versions_ignore_build("9.0.27", "9.0.28", False)

    def test_ga_custom_suffix_exact(self):
        """Custom suffix exact match should return True."""
        assert compare_versions_ignore_build("9.0.27-dev", "9.0.27-dev", False)

    def test_ga_custom_suffix_with_build(self):
        """Custom suffix with build number should match."""
        assert compare_versions_ignore_build("9.0.27-dev", "9.0.27-dev-28084", False)

    def test_ga_custom_suffix_mismatch(self):
        """Different custom suffixes should not match."""
        assert not compare_versions_ignore_build("9.0.27-dev", "9.0.27-test1", False)

    def test_ga_complex_suffix_exact(self):
        """Complex custom suffix exact match should return True."""
        assert compare_versions_ignore_build(
            "9.0.27-pre.maint90xdev",
            "9.0.27-pre.maint90xdev",
            False
        )

    def test_ga_complex_suffix_with_build(self):
        """Complex custom suffix with build number should match (original issue)."""
        assert compare_versions_ignore_build(
            "9.0.27-pre.maint90xdev",
            "9.0.27-pre.maint90xdev-28084",
            False
        )

    def test_ga_multiple_custom_suffixes(self):
        """Multiple custom suffixes with build should match."""
        assert compare_versions_ignore_build(
            "9.2.0-feature-dev",
            "9.2.0-feature-dev-28084",
            False
        )

    # Feature Channel Tests (is_feature_channel=True)
    
    def test_feature_plus_vs_hyphen(self):
        """Feature channel + vs - difference should be handled."""
        assert compare_versions_ignore_build(
            "9.1.0-pre.stable+8193",
            "9.1.0-pre.stable-8193",
            True
        )

    def test_feature_plus_vs_hyphen_with_build(self):
        """Feature channel + vs - with build number should match."""
        assert compare_versions_ignore_build(
            "9.1.0-pre.stable+8193",
            "9.1.0-pre.stable-8193-28084",
            True
        )

    def test_feature_exact_match(self):
        """Feature channel exact match should return True."""
        assert compare_versions_ignore_build(
            "9.1.0-pre.stable-8193",
            "9.1.0-pre.stable-8193",
            True
        )

    def test_feature_with_build(self):
        """Feature channel with build number should match."""
        assert compare_versions_ignore_build(
            "9.1.0-pre.stable-8193",
            "9.1.0-pre.stable-8193-28084",
            True
        )

    def test_feature_custom_suffix_plus_vs_hyphen(self):
        """Feature channel with custom suffix + vs - should match."""
        assert compare_versions_ignore_build(
            "9.2.0-feature-dev+1234",
            "9.2.0-feature-dev-1234",
            True
        )

    def test_feature_custom_suffix_with_build(self):
        """Feature channel with custom suffix and build should match."""
        assert compare_versions_ignore_build(
            "9.2.0-feature-dev+1234",
            "9.2.0-feature-dev-1234-28084",
            True
        )

    def test_feature_different_versions(self):
        """Feature channel different versions should not match."""
        assert not compare_versions_ignore_build(
            "9.1.0-pre.stable+8193",
            "9.1.0-pre.stable-8194",
            True
        )

    # Edge Cases
    
    def test_empty_strings(self):
        """Empty strings should match."""
        assert compare_versions_ignore_build("", "", False)

    def test_only_build_number(self):
        """Version that is only a build number."""
        assert compare_versions_ignore_build("28084", "28084", False)
        assert not compare_versions_ignore_build("28084", "28085", False)

    def test_no_hyphen(self):
        """Versions without hyphens should work."""
        assert compare_versions_ignore_build("9.0.27", "9.0.27", False)
        assert not compare_versions_ignore_build("9.0.27", "9.0.28", False)


class TestVersionComparisonIntegration:
    """Integration tests simulating real upgrade scenarios."""

    def test_standard_ga_upgrade(self):
        """Standard GA channel upgrade scenario."""
        # Reconciled: 9.0.27, Expected: 9.0.27
        assert compare_versions_ignore_build("9.0.27", "9.0.27", False)
        
        # Reconciled: 9.0.27, Expected: 9.0.27-28084 (with build)
        assert compare_versions_ignore_build("9.0.27", "9.0.27-28084", False)

    def test_custom_dev_channel_upgrade(self):
        """Custom development channel upgrade scenario."""
        # Reconciled: 9.0.27-dev, Expected: 9.0.27-dev
        assert compare_versions_ignore_build("9.0.27-dev", "9.0.27-dev", False)
        
        # Reconciled: 9.0.27-dev, Expected: 9.0.27-dev-28084 (with build)
        assert compare_versions_ignore_build("9.0.27-dev", "9.0.27-dev-28084", False)

    def test_complex_custom_channel_upgrade(self):
        """Complex custom channel upgrade scenario (original issue)."""
        # Reconciled: 9.0.27-pre.maint90xdev, Expected: 9.0.27-pre.maint90xdev-28084
        assert compare_versions_ignore_build(
            "9.0.27-pre.maint90xdev",
            "9.0.27-pre.maint90xdev-28084",
            False
        )

    def test_feature_channel_upgrade(self):
        """Feature channel upgrade scenario."""
        # Reconciled: 9.1.0-pre.stable+8193, Expected: 9.1.0-pre.stable-8193
        assert compare_versions_ignore_build(
            "9.1.0-pre.stable+8193",
            "9.1.0-pre.stable-8193",
            True
        )
        
        # Reconciled: 9.1.0-pre.stable+8193, Expected: 9.1.0-pre.stable-8193-28084
        assert compare_versions_ignore_build(
            "9.1.0-pre.stable+8193",
            "9.1.0-pre.stable-8193-28084",
            True
        )

    def test_feature_with_custom_suffix_upgrade(self):
        """Feature channel with custom suffix upgrade scenario."""
        # Reconciled: 9.2.0-feature-dev+1234, Expected: 9.2.0-feature-dev-1234-28084
        assert compare_versions_ignore_build(
            "9.2.0-feature-dev+1234",
            "9.2.0-feature-dev-1234-28084",
            True
        )

    def test_cross_suffix_upgrade_should_fail(self):
        """Upgrading between different custom suffixes should fail."""
        # 9.0.x-dev should not match 9.0.x-test1
        assert not compare_versions_ignore_build("9.0.27-dev", "9.0.27-test1", False)
        
        # 9.1.x-dev should not match 9.1.x-stable
        assert not compare_versions_ignore_build("9.1.0-dev", "9.1.0-stable", False)

    def test_version_mismatch_should_fail(self):
        """Different base versions should not match."""
        assert not compare_versions_ignore_build("9.0.27", "9.0.28", False)
        assert not compare_versions_ignore_build("9.0.27-dev", "9.0.28-dev", False)
        assert not compare_versions_ignore_build(
            "9.0.27-pre.maint90xdev",
            "9.0.28-pre.maint90xdev",
            False
        )

# Made with Bob
