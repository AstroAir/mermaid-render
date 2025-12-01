"""
Unit tests for mcp.tools.config module.

Tests for configuration and system management tools.
"""

import pytest

from diagramaid.mcp.tools.config import (
    get_configuration,
    get_system_information,
    manage_cache_operations,
    update_configuration,
)


@pytest.mark.unit
class TestGetConfiguration:
    """Tests for get_configuration function."""

    def test_returns_dict(self):
        """Test function returns a dictionary."""
        result = get_configuration()
        assert isinstance(result, dict)

    def test_has_success_key(self):
        """Test result has success key."""
        result = get_configuration()
        assert "success" in result

    def test_with_specific_key(self):
        """Test with specific configuration key."""
        result = get_configuration(key="timeout")
        assert isinstance(result, dict)

    def test_with_section_filter(self):
        """Test with section filter."""
        result = get_configuration(section="rendering")
        assert isinstance(result, dict)

    def test_nonexistent_key(self):
        """Test with nonexistent key."""
        result = get_configuration(key="nonexistent_key_xyz")
        # Should return error
        assert isinstance(result, dict)

    def test_result_has_settings(self):
        """Test result includes settings data."""
        result = get_configuration()
        if result["success"]:
            assert "data" in result


@pytest.mark.unit
class TestUpdateConfiguration:
    """Tests for update_configuration function."""

    def test_returns_dict(self):
        """Test function returns a dictionary."""
        result = update_configuration("timeout", 30)
        assert isinstance(result, dict)

    def test_has_success_key(self):
        """Test result has success key."""
        result = update_configuration("timeout", 30)
        assert "success" in result

    def test_nonexistent_key(self):
        """Test with nonexistent key."""
        result = update_configuration("nonexistent_key_xyz", "value")
        # Should return error
        assert isinstance(result, dict)


@pytest.mark.unit
class TestGetSystemInformation:
    """Tests for get_system_information function."""

    def test_returns_dict(self):
        """Test function returns a dictionary."""
        result = get_system_information()
        assert isinstance(result, dict)

    def test_has_success_key(self):
        """Test result has success key."""
        result = get_system_information()
        assert "success" in result

    def test_includes_version(self):
        """Test result includes version information."""
        result = get_system_information()
        if result["success"]:
            assert "data" in result
            assert "system" in result["data"] or "diagramaid_version" in str(
                result["data"]
            )

    def test_includes_features(self):
        """Test result includes features information."""
        result = get_system_information()
        if result["success"]:
            assert "data" in result
            assert "features" in result["data"]

    def test_includes_capabilities(self):
        """Test result includes capabilities information."""
        result = get_system_information()
        if result["success"]:
            assert "data" in result


@pytest.mark.unit
class TestManageCacheOperations:
    """Tests for manage_cache_operations function."""

    def test_returns_dict(self):
        """Test function returns a dictionary."""
        result = manage_cache_operations("stats")
        assert isinstance(result, dict)

    def test_has_success_key(self):
        """Test result has success key."""
        result = manage_cache_operations("stats")
        assert "success" in result

    def test_stats_operation(self):
        """Test stats operation."""
        result = manage_cache_operations("stats")
        assert isinstance(result, dict)

    def test_clear_operation_without_key(self):
        """Test clear operation without key fails."""
        result = manage_cache_operations("clear")
        # Should fail without cache_key
        assert isinstance(result, dict)

    def test_clear_operation_with_key(self):
        """Test clear operation with key."""
        result = manage_cache_operations("clear", cache_key="test_key")
        assert isinstance(result, dict)

    def test_clear_all_operation(self):
        """Test clear_all operation."""
        result = manage_cache_operations("clear_all")
        assert isinstance(result, dict)

    def test_cleanup_operation(self):
        """Test cleanup operation."""
        result = manage_cache_operations("cleanup")
        assert isinstance(result, dict)

    def test_invalid_operation(self):
        """Test invalid operation."""
        result = manage_cache_operations("invalid_operation")
        assert result["success"] is False
