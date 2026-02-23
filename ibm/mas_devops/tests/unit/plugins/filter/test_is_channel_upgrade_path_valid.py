"""
Unit tests for is_channel_upgrade_path_valid filter.
"""
import pytest

from filters import is_channel_upgrade_path_valid


class TestIsChannelUpgradePathValid:
    """Test suite for is_channel_upgrade_path_valid filter."""

    def test_blank_target_channel_returns_true(self):
        """Test that blank target channel is considered valid."""
        # Arrange
        paths = {'a': ['b', 'c']}

        # Act
        result = is_channel_upgrade_path_valid('a', '', paths)

        # Assert
        assert result is True

    def test_invalid_target_channel_returns_false(self):
        """Test that invalid target channel returns False."""
        # Arrange
        paths = {'a': ['b', 'c']}

        # Act
        result = is_channel_upgrade_path_valid('a', 'd', paths)

        # Assert
        assert result is False

    def test_valid_target_channel_returns_true(self):
        """Test that valid target channel returns True."""
        # Arrange
        paths = {'a': ['b', 'c']}

        # Act
        result = is_channel_upgrade_path_valid('a', 'c', paths)

        # Assert
        assert result is True

    def test_invalid_current_channel_returns_false(self):
        """Test that invalid current channel returns False."""
        # Arrange
        paths = {'a': ['b', 'c']}

        # Act
        result = is_channel_upgrade_path_valid('d', 'c', paths)

        # Assert
        assert result is False

    def test_string_target_channel_returns_true(self):
        """Test that string target channel (not list) is handled correctly."""
        # Arrange
        paths = {'a': 'b'}

        # Act
        result = is_channel_upgrade_path_valid('a', 'b', paths)

        # Assert
        assert result is True

    def test_invalid_paths_type_returns_false(self):
        """Test that invalid paths type returns False."""
        # Arrange
        paths = {'a': 1}

        # Act
        result = is_channel_upgrade_path_valid('a', 'b', paths)

        # Assert
        assert result is False

    def test_string_target_channel_mismatch_returns_false(self):
        """Test that mismatched string target channel returns False."""
        # Arrange
        paths = {'a': 'b'}

        # Act
        result = is_channel_upgrade_path_valid('a', 'c', paths)

        # Assert
        assert result is False

    def test_empty_target_with_list_paths_returns_true(self):
        """Test that empty target with list paths returns True."""
        # Arrange
        paths = {'v8.11': ['v8.12', 'v9.0']}

        # Act
        result = is_channel_upgrade_path_valid('v8.11', '', paths)

        # Assert
        assert result is True

    def test_multiple_valid_targets_first_option(self):
        """Test upgrade to first option in multiple valid targets."""
        # Arrange
        paths = {'v8.11': ['v8.12', 'v9.0']}

        # Act
        result = is_channel_upgrade_path_valid('v8.11', 'v8.12', paths)

        # Assert
        assert result is True

    def test_multiple_valid_targets_second_option(self):
        """Test upgrade to second option in multiple valid targets."""
        # Arrange
        paths = {'v8.11': ['v8.12', 'v9.0']}

        # Act
        result = is_channel_upgrade_path_valid('v8.11', 'v9.0', paths)

        # Assert
        assert result is True

# Made with Bob
