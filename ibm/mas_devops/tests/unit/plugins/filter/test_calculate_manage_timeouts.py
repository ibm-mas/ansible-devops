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
        assert result["delay"] * result["retries"] == 14400  # 4 hours in seconds

    def test_foundation_mode_with_empty_dict(self):
        """Test foundation mode when components is an empty dict."""
        result = calculateManageTimeouts({})
        assert result == {"delay": 240, "retries": 60}

    def test_full_mode_with_single_component(self):
        """Test full mode with a single component."""
        components = {"base": {"version": "latest"}}
        result = calculateManageTimeouts(components)
        assert result == {"delay": 360, "retries": 180}
        assert result["delay"] * result["retries"] == 64800  # 18 hours in seconds

    def test_full_mode_with_multiple_components(self):
        """Test full mode with multiple components."""
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
