"""
Unit tests for configuration and theme management.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from mermaid_render.config import ConfigManager, ThemeManager
from mermaid_render.exceptions import ConfigurationError, ThemeError


class TestConfigManager:
    """Test ConfigManager class."""

    def test_init_default(self) -> None:
        """Test config manager initialization with defaults."""
        config = ConfigManager(load_env=False)

        assert config.get("server_url") == "https://mermaid.ink"
        assert config.get("timeout") == 30.0
        assert config.get("default_theme") == "default"
        assert config.get("validate_syntax") is True

    def test_init_with_runtime_config(self) -> None:
        """Test initialization with runtime configuration."""
        config = ConfigManager(
            load_env=False, timeout=60.0, custom_setting="test_value"
        )

        assert config.get("timeout") == 60.0
        assert config.get("custom_setting") == "test_value"

    def test_get_with_default(self) -> None:
        """Test getting configuration with default value."""
        config = ConfigManager(load_env=False)

        assert config.get("nonexistent_key", "default_value") == "default_value"
        assert config.get("timeout", 999) == 30.0  # Should return actual value

    def test_set_runtime_config(self) -> None:
        """Test setting runtime configuration."""
        config = ConfigManager(load_env=False)

        config.set("timeout", 45.0, runtime=True)
        config.set("new_setting", "test", runtime=True)

        assert config.get("timeout") == 45.0
        assert config.get("new_setting") == "test"

    def test_set_persistent_config(self) -> None:
        """Test setting persistent configuration."""
        config = ConfigManager(load_env=False)

        config.set("timeout", 45.0, runtime=False)

        assert config.get("timeout") == 45.0

    def test_update_runtime_config(self) -> None:
        """Test updating multiple runtime configuration values."""
        config = ConfigManager(load_env=False)

        updates = {"timeout": 60.0, "retries": 5, "custom_setting": "test_value"}
        config.update(updates, runtime=True)

        assert config.get("timeout") == 60.0
        assert config.get("retries") == 5
        assert config.get("custom_setting") == "test_value"

    def test_update_persistent_config(self) -> None:
        """Test updating persistent configuration."""
        config = ConfigManager(load_env=False)

        updates = {"timeout": 60.0, "retries": 5}
        config.update(updates, runtime=False)

        assert config.get("timeout") == 60.0
        assert config.get("retries") == 5

    def test_get_all(self) -> None:
        """Test getting all configuration values."""
        config = ConfigManager(load_env=False)
        config.set("custom_setting", "test_value")

        all_config = config.get_all()

        assert "server_url" in all_config
        assert "timeout" in all_config
        assert "custom_setting" in all_config
        assert all_config["custom_setting"] == "test_value"

    def test_reset_to_defaults(self) -> None:
        """Test resetting configuration to defaults."""
        config = ConfigManager(load_env=False)
        config.set("timeout", 60.0)
        config.set("custom_setting", "test")

        config.reset_to_defaults()

        assert config.get("timeout") == 30.0  # Back to default
        assert config.get("custom_setting") is None  # Custom setting removed

    def test_runtime_config_precedence(self) -> None:
        """Test that runtime config takes precedence over persistent config."""
        config = ConfigManager(load_env=False)

        config.set("timeout", 45.0, runtime=False)  # Persistent
        config.set("timeout", 60.0, runtime=True)  # Runtime (higher priority)

        assert config.get("timeout") == 60.0

    @patch.dict("os.environ", {"MERMAID_TIMEOUT": "45.0", "MERMAID_RETRIES": "5"})
    def test_load_environment_variables(self) -> None:
        """Test loading configuration from environment variables."""
        config = ConfigManager(load_env=True)

        assert config.get("timeout") == 45.0
        assert config.get("retries") == 5

    def test_load_config_file(self) -> None:
        """Test loading configuration from file."""
        config_data = {"timeout": 45.0, "retries": 5, "custom_setting": "from_file"}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_file = Path(f.name)

        try:
            config = ConfigManager(config_file=config_file, load_env=False)

            assert config.get("timeout") == 45.0
            assert config.get("retries") == 5
            assert config.get("custom_setting") == "from_file"
        finally:
            config_file.unlink()

    def test_load_invalid_config_file(self) -> None:
        """Test loading invalid configuration file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("invalid json content")
            config_file = Path(f.name)

        try:
            with pytest.raises(ConfigurationError, match="Failed to load config file"):
                ConfigManager(config_file=config_file, load_env=False)
        finally:
            config_file.unlink()

    def test_validate_config_valid(self) -> None:
        """Test configuration validation with valid config."""
        config = ConfigManager(load_env=False)

        # Should not raise any exception
        config.validate_config()

    def test_validate_config_invalid_timeout(self) -> None:
        """Test configuration validation with invalid timeout."""
        config = ConfigManager(load_env=False)
        config.set("timeout", -1)

        with pytest.raises(
            ConfigurationError, match="timeout must be a positive number"
        ):
            config.validate_config()

    def test_validate_config_invalid_retries(self) -> None:
        """Test configuration validation with invalid retries."""
        config = ConfigManager(load_env=False)
        config.set("retries", -1)

        with pytest.raises(
            ConfigurationError, match="retries must be a non-negative integer"
        ):
            config.validate_config()

    def test_validate_config_invalid_cache_size(self) -> None:
        """Test configuration validation with invalid cache size."""
        config = ConfigManager(load_env=False)
        config.set("max_cache_size", -1)

        with pytest.raises(
            ConfigurationError, match="max_cache_size must be a positive number"
        ):
            config.validate_config()

    def test_save_config_file(self) -> None:
        """Test saving configuration to file."""
        config = ConfigManager(load_env=False)
        config.set("timeout", 45.0)
        config.set("custom_setting", "test_value")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            config_file = Path(f.name)

        try:
            config.save_to_file(config_file)

            # Verify file was created and contains correct data
            assert config_file.exists()

            with open(config_file) as f:
                saved_config = json.load(f)

            assert saved_config["timeout"] == 45.0
            assert saved_config["custom_setting"] == "test_value"
        finally:
            if config_file.exists():
                config_file.unlink()


class TestThemeManager:
    """Test ThemeManager class."""

    def test_init_default(self) -> None:
        """Test theme manager initialization."""
        theme_manager = ThemeManager()

        assert theme_manager.custom_themes_dir is None
        assert len(theme_manager._custom_themes) == 0

    def test_init_with_custom_dir(self) -> None:
        """Test initialization with custom themes directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_dir = Path(temp_dir)
            theme_manager = ThemeManager(custom_themes_dir=custom_dir)

            assert theme_manager.custom_themes_dir == custom_dir

    def test_get_built_in_theme(self) -> None:
        """Test getting built-in theme."""
        theme_manager = ThemeManager()

        default_theme = theme_manager.get_theme("default")

        assert default_theme["theme"] == "default"
        assert "primaryColor" in default_theme
        assert "primaryTextColor" in default_theme

    def test_get_all_built_in_themes(self) -> None:
        """Test getting all built-in themes."""
        theme_manager = ThemeManager()

        built_in = theme_manager.get_built_in_themes()

        assert "default" in built_in
        assert "dark" in built_in
        assert "forest" in built_in
        assert "neutral" in built_in
        assert "base" in built_in

    def test_get_nonexistent_theme(self) -> None:
        """Test getting nonexistent theme."""
        theme_manager = ThemeManager()

        with pytest.raises(ThemeError, match="Theme 'nonexistent' not found"):
            theme_manager.get_theme("nonexistent")

    def test_get_available_themes(self) -> None:
        """Test getting list of available themes."""
        theme_manager = ThemeManager()

        available = theme_manager.get_available_themes()

        assert "default" in available
        assert "dark" in available
        assert isinstance(available, list)
        assert len(available) >= 5  # At least the built-in themes

    def test_add_custom_theme(self) -> None:
        """Test adding custom theme."""
        theme_manager = ThemeManager()

        custom_theme = {
            "theme": "custom",
            "primaryColor": "#ff0000",
            "primaryTextColor": "#ffffff",
            "lineColor": "#000000",
        }

        theme_manager.add_custom_theme("my_theme", custom_theme, save_to_file=False)

        assert "my_theme" in theme_manager.get_available_themes()
        retrieved = theme_manager.get_theme("my_theme")
        assert retrieved["primaryColor"] == "#ff0000"

    def test_add_custom_theme_override_builtin(self) -> None:
        """Test adding custom theme with built-in name should fail."""
        theme_manager = ThemeManager()

        custom_theme = {"theme": "custom", "primaryColor": "#ff0000"}

        with pytest.raises(ThemeError, match="Cannot override built-in theme"):
            theme_manager.add_custom_theme("default", custom_theme)

    def test_add_custom_theme_invalid_config(self) -> None:
        """Test adding custom theme with invalid configuration."""
        theme_manager = ThemeManager()

        invalid_theme: dict = {
            # Missing required "theme" field
        }

        with pytest.raises(ThemeError, match="Missing required theme field"):
            theme_manager.add_custom_theme("invalid_theme", invalid_theme)

    def test_remove_custom_theme(self) -> None:
        """Test removing custom theme."""
        theme_manager = ThemeManager()

        custom_theme = {
            "theme": "custom",
            "primaryColor": "#ff0000",
            "primaryTextColor": "#ffffff",
            "lineColor": "#000000",
        }

        theme_manager.add_custom_theme("my_theme", custom_theme, save_to_file=False)
        assert "my_theme" in theme_manager.get_available_themes()

        theme_manager.remove_custom_theme("my_theme")
        assert "my_theme" not in theme_manager.get_available_themes()

    def test_remove_nonexistent_custom_theme(self) -> None:
        """Test removing nonexistent custom theme."""
        theme_manager = ThemeManager()

        with pytest.raises(ThemeError, match="Custom theme 'nonexistent' not found"):
            theme_manager.remove_custom_theme("nonexistent")

    def test_remove_builtin_theme(self) -> None:
        """Test removing built-in theme should fail."""
        theme_manager = ThemeManager()

        with pytest.raises(ThemeError, match="Cannot remove built-in theme"):
            theme_manager.remove_custom_theme("default")

    def test_create_theme_variant(self) -> None:
        """Test creating theme variant."""
        theme_manager = ThemeManager()

        modifications = {"primaryColor": "#00ff00", "secondaryColor": "#0000ff"}

        theme_manager.create_theme_variant(
            "default", "my_variant", modifications, save_to_file=False
        )

        variant = theme_manager.get_theme("my_variant")
        assert variant["primaryColor"] == "#00ff00"
        assert variant["secondaryColor"] == "#0000ff"
        # Should inherit other properties from default theme
        assert "primaryTextColor" in variant

    def test_validate_theme_config_valid(self) -> None:
        """Test theme configuration validation with valid config."""
        theme_manager = ThemeManager()

        valid_theme = {
            "theme": "custom",
            "primaryColor": "#ff0000",
            "primaryTextColor": "#ffffff",
            "lineColor": "#000000",
        }

        # Should not raise any exception
        theme_manager._validate_theme_config(valid_theme)

    def test_validate_theme_config_missing_required(self) -> None:
        """Test theme validation with missing required fields."""
        theme_manager = ThemeManager()

        invalid_theme: dict = {
            # Missing required "theme" field
        }

        with pytest.raises(ThemeError, match="Missing required theme field"):
            theme_manager._validate_theme_config(invalid_theme)

    def test_validate_theme_config_invalid_color(self) -> None:
        """Test theme validation with invalid color format."""
        theme_manager = ThemeManager()

        invalid_theme = {
            "theme": "custom",
            "primaryColor": "not_a_color",
        }

        with pytest.raises(ThemeError, match="Invalid color value"):
            theme_manager._validate_theme_config(invalid_theme)

    def test_save_theme_to_file(self) -> None:
        """Test saving theme to file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_dir = Path(temp_dir)
            theme_manager = ThemeManager(custom_themes_dir=custom_dir)

            custom_theme = {
                "theme": "custom",
                "primaryColor": "#ff0000",
                "primaryTextColor": "#ffffff",
                "lineColor": "#000000",
            }

            theme_manager.add_custom_theme("my_theme", custom_theme, save_to_file=True)

            theme_file = custom_dir / "my_theme.json"
            assert theme_file.exists()

            with open(theme_file) as f:
                saved_theme = json.load(f)

            assert saved_theme["primaryColor"] == "#ff0000"

    def test_load_custom_themes_from_directory(self) -> None:
        """Test loading custom themes from directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_dir = Path(temp_dir)

            # Create a theme file
            theme_data = {
                "theme": "loaded",
                "primaryColor": "#00ff00",
                "primaryTextColor": "#000000",
                "lineColor": "#333333",
            }

            theme_file = custom_dir / "loaded_theme.json"
            with open(theme_file, "w") as f:
                json.dump(theme_data, f)

            # Create theme manager - should load the theme
            theme_manager = ThemeManager(custom_themes_dir=custom_dir)

            assert "loaded_theme" in theme_manager.get_available_themes()
            loaded = theme_manager.get_theme("loaded_theme")
            assert loaded["primaryColor"] == "#00ff00"

    def test_load_invalid_theme_file(self) -> None:
        """Test loading invalid theme file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_dir = Path(temp_dir)

            # Create invalid theme file
            invalid_file = custom_dir / "invalid.json"
            with open(invalid_file, "w") as f:
                f.write("invalid json")

            # Should not crash, just skip the invalid file
            theme_manager = ThemeManager(custom_themes_dir=custom_dir)
            assert "invalid" not in theme_manager.get_available_themes()

    def test_export_theme(self) -> None:
        """Test exporting theme to file."""
        theme_manager = ThemeManager()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            export_file = Path(f.name)

        try:
            theme_manager.export_theme("default", export_file)

            assert export_file.exists()

            with open(export_file) as f:
                exported_theme = json.load(f)

            assert exported_theme["theme"] == "default"
            assert "primaryColor" in exported_theme
        finally:
            if export_file.exists():
                export_file.unlink()

    def test_export_nonexistent_theme(self) -> None:
        """Test exporting nonexistent theme."""
        theme_manager = ThemeManager()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            export_file = Path(f.name)

        try:
            with pytest.raises(ThemeError, match="Theme 'nonexistent' not found"):
                theme_manager.export_theme("nonexistent", export_file)
        finally:
            if export_file.exists():
                export_file.unlink()

    def test_import_theme(self) -> None:
        """Test importing theme from file."""
        theme_manager = ThemeManager()

        theme_data = {
            "theme": "imported",
            "primaryColor": "#ff00ff",
            "primaryTextColor": "#ffffff",
            "lineColor": "#000000",
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(theme_data, f)
            import_file = Path(f.name)

        try:
            imported_name = theme_manager.import_theme(import_file)

            assert imported_name in theme_manager.get_available_themes()
            imported = theme_manager.get_theme(imported_name)
            assert imported["primaryColor"] == "#ff00ff"
        finally:
            import_file.unlink()

    def test_import_theme_with_custom_name(self) -> None:
        """Test importing theme with custom name."""
        theme_manager = ThemeManager()

        theme_data = {
            "theme": "imported",
            "primaryColor": "#ff00ff",
            "primaryTextColor": "#ffffff",
            "lineColor": "#000000",
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(theme_data, f)
            import_file = Path(f.name)

        try:
            imported_name = theme_manager.import_theme(import_file, "custom_name")

            assert imported_name == "custom_name"
            assert "custom_name" in theme_manager.get_available_themes()
        finally:
            import_file.unlink()

    def test_get_theme_returns_copy(self) -> None:
        """Test that get_theme returns a copy, not reference."""
        theme_manager = ThemeManager()

        theme1 = theme_manager.get_theme("default")
        theme2 = theme_manager.get_theme("default")

        # Modify one copy
        theme1["primaryColor"] = "#modified"

        # Other copy should be unchanged
        assert theme2["primaryColor"] != "#modified"

    def test_is_theme_available(self) -> None:
        """Test checking if theme is available."""
        theme_manager = ThemeManager()

        # Built-in theme should be available
        assert theme_manager.is_theme_available("default") is True

        # Non-existent theme should not be available
        assert theme_manager.is_theme_available("nonexistent") is False

        # Add custom theme and check availability
        custom_theme = {
            "theme": "custom",
            "primaryColor": "#ff0000",
            "primaryTextColor": "#ffffff",
            "lineColor": "#000000",
        }

        theme_manager.add_custom_theme("my_theme", custom_theme, save_to_file=False)
        assert theme_manager.is_theme_available("my_theme") is True
