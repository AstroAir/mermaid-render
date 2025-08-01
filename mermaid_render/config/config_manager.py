"""
Configuration management for the Mermaid Render library.

This module provides comprehensive configuration management with support for
environment variables, configuration files, and runtime configuration.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from ..exceptions import ConfigurationError


class ConfigManager:
    """
    Comprehensive configuration manager for Mermaid Render.

    Manages configuration from multiple sources with proper precedence:
    1. Runtime configuration (highest priority)
    2. Environment variables
    3. Configuration files
    4. Default values (lowest priority)
    """

    # Default configuration values
    DEFAULT_CONFIG = {
        "server_url": "https://mermaid.ink",
        "timeout": 30.0,
        "retries": 3,
        "default_theme": "default",
        "default_format": "svg",
        "validate_syntax": True,
        "cache_enabled": True,
        "cache_dir": "~/.mermaid_render_cache",
        "max_cache_size": 100,  # MB
        "cache_ttl": 3600,  # seconds
        "default_width": 800,
        "default_height": 600,
        "max_width": 4000,
        "max_height": 4000,
        "use_local_rendering": True,
        "log_level": "INFO",
        "custom_themes_dir": "~/.mermaid_render_themes",
    }

    # Environment variable mappings
    ENV_MAPPINGS = {
        "MERMAID_INK_SERVER": "server_url",
        "MERMAID_TIMEOUT": "timeout",
        "MERMAID_RETRIES": "retries",
        "MERMAID_DEFAULT_THEME": "default_theme",
        "MERMAID_DEFAULT_FORMAT": "default_format",
        "MERMAID_VALIDATE_SYNTAX": "validate_syntax",
        "MERMAID_CACHE_ENABLED": "cache_enabled",
        "MERMAID_CACHE_DIR": "cache_dir",
        "MERMAID_MAX_CACHE_SIZE": "max_cache_size",
        "MERMAID_CACHE_TTL": "cache_ttl",
        "MERMAID_DEFAULT_WIDTH": "default_width",
        "MERMAID_DEFAULT_HEIGHT": "default_height",
        "MERMAID_USE_LOCAL": "use_local_rendering",
        "MERMAID_LOG_LEVEL": "log_level",
        "MERMAID_THEMES_DIR": "custom_themes_dir",
    }

    def __init__(
        self,
        config_file: Optional[Path] = None,
        load_env: bool = True,
        **runtime_config: Any,
    ) -> None:
        """
        Initialize configuration manager.

        Args:
            config_file: Optional configuration file path
            load_env: Whether to load environment variables
            **runtime_config: Runtime configuration overrides
        """
        self._config: Dict[str, Any] = {}
        self._runtime_config: Dict[str, Any] = {}

        # Load configuration in order of precedence
        self._load_defaults()

        if config_file:
            self._load_config_file(config_file)

        if load_env:
            self._load_environment()

        if runtime_config:
            self._runtime_config.update(runtime_config)

        # Validate and process configuration
        self._process_config()

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value
        """
        # Check runtime config first
        if key in self._runtime_config:
            return self._runtime_config[key]

        # Then check main config
        return self._config.get(key, default)

    def set(self, key: str, value: Any, runtime: bool = True) -> None:
        """
        Set configuration value.

        Args:
            key: Configuration key
            value: Configuration value
            runtime: Whether to set as runtime config (higher priority)
        """
        if runtime:
            self._runtime_config[key] = value
        else:
            self._config[key] = value

        # Re-process configuration if needed
        if key in ["cache_dir", "custom_themes_dir"]:
            self._process_paths()

    def update(self, config: Dict[str, Any], runtime: bool = True) -> None:
        """
        Update multiple configuration values.

        Args:
            config: Configuration dictionary
            runtime: Whether to update runtime config
        """
        if runtime:
            self._runtime_config.update(config)
        else:
            self._config.update(config)

        self._process_config()

    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values with proper precedence."""
        result = self._config.copy()
        result.update(self._runtime_config)
        return result

    def reset_to_defaults(self) -> None:
        """Reset configuration to default values."""
        self._config.clear()
        self._runtime_config.clear()
        self._load_defaults()
        self._process_config()

    def save_to_file(self, config_file: Path) -> None:
        """
        Save current configuration to file.

        Args:
            config_file: Output configuration file path
        """
        config = self.get_all()

        # Convert Path objects to strings for JSON serialization
        serializable_config = {}
        for key, value in config.items():
            if isinstance(value, Path):
                serializable_config[key] = str(value)
            else:
                serializable_config[key] = value

        config_file.parent.mkdir(parents=True, exist_ok=True)

        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(serializable_config, f, indent=2)

    def validate_config(self) -> None:
        """
        Validate current configuration.

        Raises:
            ConfigurationError: If configuration is invalid
        """
        config = self.get_all()

        # Validate timeout
        timeout = config.get("timeout")
        if not isinstance(timeout, (int, float)) or timeout <= 0:
            raise ConfigurationError("timeout must be a positive number")

        # Validate retries
        retries = config.get("retries")
        if not isinstance(retries, int) or retries < 0:
            raise ConfigurationError("retries must be a non-negative integer")

        # Validate dimensions
        width = config.get("default_width")
        height = config.get("default_height")
        max_width = config.get("max_width")
        max_height = config.get("max_height")

        if not isinstance(width, int) or width <= 0:
            raise ConfigurationError("default_width must be a positive integer")

        if not isinstance(height, int) or height <= 0:
            raise ConfigurationError("default_height must be a positive integer")

        if width > max_width or height > max_height:
            raise ConfigurationError("Default dimensions exceed maximum allowed")

        # Validate cache settings
        cache_size = config.get("max_cache_size")
        if not isinstance(cache_size, (int, float)) or cache_size <= 0:
            raise ConfigurationError("max_cache_size must be a positive number")

        cache_ttl = config.get("cache_ttl")
        if not isinstance(cache_ttl, (int, float)) or cache_ttl <= 0:
            raise ConfigurationError("cache_ttl must be a positive number")

    def _load_defaults(self) -> None:
        """Load default configuration values."""
        self._config = self.DEFAULT_CONFIG.copy()

    def _load_config_file(self, config_file: Path) -> None:
        """
        Load configuration from file.

        Args:
            config_file: Configuration file path
        """
        if not config_file.exists():
            return

        try:
            with open(config_file, encoding="utf-8") as f:
                file_config = json.load(f)

            self._config.update(file_config)

        except (OSError, json.JSONDecodeError) as e:
            raise ConfigurationError(f"Failed to load config file {config_file}: {e}")

    def _load_environment(self) -> None:
        """Load configuration from environment variables."""
        for env_var, config_key in self.ENV_MAPPINGS.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                # Convert string values to appropriate types
                converted_value = self._convert_env_value(env_value, config_key)
                self._config[config_key] = converted_value

    def _convert_env_value(self, value: str, key: str) -> Any:
        """
        Convert environment variable string to appropriate type.

        Args:
            value: Environment variable value
            key: Configuration key

        Returns:
            Converted value
        """
        # Boolean values
        if key in ["validate_syntax", "cache_enabled", "use_local_rendering"]:
            return value.lower() in ("true", "1", "yes", "on")

        # Numeric values
        if key in ["timeout", "cache_ttl"]:
            return float(value)

        if key in ["retries", "max_cache_size", "default_width", "default_height"]:
            return int(value)

        # String values (default)
        return value

    def _process_config(self) -> None:
        """Process and validate configuration after loading."""
        self._process_paths()
        self.validate_config()

    def _process_paths(self) -> None:
        """Process path configuration values."""
        config = self.get_all()

        # Expand user paths
        for key in ["cache_dir", "custom_themes_dir"]:
            if key in config:
                path_value = config[key]
                if isinstance(path_value, str):
                    expanded_path = Path(path_value).expanduser().resolve()
                    if key in self._runtime_config:
                        self._runtime_config[key] = expanded_path
                    else:
                        self._config[key] = expanded_path
