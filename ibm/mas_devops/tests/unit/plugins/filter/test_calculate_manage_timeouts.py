"""
Unit tests for calculate_manage_timeouts filter.
"""

from manage_timeouts import calculateManageTimeouts


class TestCalculateManageTimeouts:
    """Test suite for the calculateManageTimeouts filter function."""

    def test_foundation_mode_with_none(self):
        """Test foundation mode when components is None."""
        result = calculateManageTimeouts(None)
        assert result == {"delay": 240, "retries": 60}

    def test_foundation_mode_with_empty_dict(self):
        """Test foundation mode when components is an empty dict."""
        result = calculateManageTimeouts({})
        assert result == {"delay": 240, "retries": 60}

    def test_base_mode(self):
        """Test base mode"""
        components = {"base": {"version": "latest"}}
        result = calculateManageTimeouts(components)
        assert result == {"delay": 240, "retries": 60}

    def test_health_mode(self):
        """Test health mode"""
        components = {"base": {"version": "latest"}, "health": {"version": "latest"}}
        result = calculateManageTimeouts(components)
        assert result == {"delay": 360, "retries": 60}

    def test_unknown_mode(self):
        """Test unknown mode"""
        components = {
            "base": {"version": "latest"},
            "health": {"version": "8.8.0"},
            "civil": {"version": "8.7.0"},
        }
        result = calculateManageTimeouts(components)
        assert result == {"delay": 360, "retries": 180}

    def test_return_type_is_dict(self):
        """Test that the return type is always a dictionary."""
        assert isinstance(calculateManageTimeouts(None), dict)
        assert isinstance(calculateManageTimeouts({}), dict)
        assert isinstance(
            calculateManageTimeouts({"base": {"version": "latest"}}), dict
        )

    def test_return_keys_are_present(self):
        """Test that both 'delay' and 'retries' keys are present in the result."""
        result = calculateManageTimeouts(None)
        assert "delay" in result
        assert "retries" in result

    def test_return_values_are_integers(self):
        """Test that delay and retries values are integers."""
        result = calculateManageTimeouts(None)
        assert isinstance(result["delay"], int)
        assert isinstance(result["retries"], int)

        result = calculateManageTimeouts({"base": {"version": "latest"}})
        assert isinstance(result["delay"], int)
        assert isinstance(result["retries"], int)


# Made with Bob
