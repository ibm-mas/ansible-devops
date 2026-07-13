"""
Unit tests for is_channel_upgrade_path_valid filter.
"""
import pytest

from filters import is_operator_upgraded_by_version


class TestIsOperatorUpgradedByVersion:

    def test_all_versions_match(self):
       version = "9.2.0-pre.stable+16576"
       assert is_operator_upgraded_by_version(version, version, version)

    def test_subscription_version_has_hyphen(self):
        version_plus = "9.2.0-pre.stable+16576"
        version_hyphen = version_plus.replace('+', '-')
        assert is_operator_upgraded_by_version(version_plus, version_plus, version_hyphen)
    
    def test_opcon_version_has_build_number(self):
        version_simple = "9.2.0-pre.1450"
        version_build = version_simple + "-5075"
        assert is_operator_upgraded_by_version(version_simple, version_build, version_build)
    
    def test_no_versions_match(self):
       assert not is_operator_upgraded_by_version('a', 'b', 'c')
