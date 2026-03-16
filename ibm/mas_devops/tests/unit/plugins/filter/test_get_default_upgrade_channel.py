"""
Unit tests for get_default_upgrade_channel filter.
"""
import pytest

from filters import get_default_upgrade_channel


class TestGetDefaultUpgradeChannel:
    """Test suite for get_default_upgrade_channel filter."""

    def test_valid_current_channel_with_list_returns_first_element(self):
        """Test that valid current channel with list paths returns first element."""
        # Arrange
        paths = {'a': ['b', 'c']}

        # Act
        result = get_default_upgrade_channel('a', paths)

        # Assert
        assert result == 'b'

    def test_string_target_channel_returns_string(self):
        """Test that string target channel is returned as-is."""
        # Arrange
        paths = {'a': 'b'}

        # Act
        result = get_default_upgrade_channel('a', paths)

        # Assert
        assert result == 'b'

    def test_invalid_current_channel_raises_key_error(self):
        """Test that invalid current channel raises KeyError."""
        # Arrange
        paths = {'a': ['b', 'c']}

        # Act & Assert
        with pytest.raises(KeyError):
            get_default_upgrade_channel('b', paths)

    def test_invalid_paths_type_returns_none(self):
        """Test that invalid paths type returns None."""
        # Arrange
        paths = {'a': 1}

        # Act
        result = get_default_upgrade_channel('a', paths)

        # Assert
        assert result is None

    def test_empty_list_paths_raises_index_error(self):
        """Test that empty list in paths raises IndexError."""
        # Arrange
        paths = {'a': []}

        # Act & Assert
        # Empty list will try to access [0] which will raise IndexError
        with pytest.raises(IndexError):
            get_default_upgrade_channel('a', paths)

    def test_multiple_upgrade_paths_returns_first(self):
        """Test that multiple upgrade paths returns the first one."""
        # Arrange
        paths = {'v8.11': ['v8.12', 'v9.0', 'v9.1']}

        # Act
        result = get_default_upgrade_channel('v8.11', paths)

        # Assert
        assert result == 'v8.12'

    def test_single_string_path(self):
        """Test single string path is returned correctly."""
        # Arrange
        paths = {'v8.11': 'v8.12'}

        # Act
        result = get_default_upgrade_channel('v8.11', paths)

        # Assert
        assert result == 'v8.12'

    def test_dict_type_paths_returns_none(self):
        """Test that dict type in paths returns None."""
        # Arrange
        paths = {'a': {'b': 'c'}}

        # Act
        result = get_default_upgrade_channel('a', paths)

        # Assert
        assert result is None

    def test_none_type_paths_returns_none(self):
        """Test that None type in paths returns None."""
        # Arrange
        paths = {'a': None}

        # Act
        result = get_default_upgrade_channel('a', paths)

        # Assert
        assert result is None

# Made with Bob
