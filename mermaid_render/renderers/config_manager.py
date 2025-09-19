"""
Configuration management for the plugin-based rendering system.

This module provides enhanced configuration management with schema validation,
environment variable support, and renderer-specific configuration handling.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import jsonschema  # type: ignore[import-untyped]


class RendererConfigManager:
    """
    Configuration manager for renderer-specific settings.

    This class handles configuration loading, validation, and management
    for individual renderers in the plugin-based system. It supports
    configuration files, environment variables, and runtime overrides.
    """

    def __init__(
        self,
        config_dir: Optional[Union[str, Path]] = None,
        env_prefix: str = "MERMAID_RENDER",
    ) -> None:
        """
        Initialize the configuration manager.

        Args:
            config_dir: Directory for configuration files
            env_prefix: Prefix for environment variables
        """
        self.logger = logging.getLogger(__name__)
        self.config_dir = Path(
            config_dir) if config_dir else Path.home() / ".mermaid_render"
        self.env_prefix = env_prefix

        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Loaded configurations
        self._configs: Dict[str, Dict[str, Any]] = {}
        self._schemas: Dict[str, Dict[str, Any]] = {}

    def load_renderer_config(
        self,
        renderer_name: str,
        schema: Optional[Dict[str, Any]] = None,
        defaults: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Load configuration for a specific renderer.

        Args:
            renderer_name: Name of the renderer
            schema: JSON schema for validation
            defaults: Default configuration values

        Returns:
            Merged configuration dictionary
        """
        # Start with defaults
        config = defaults.copy() if defaults else {}

        # Load from configuration file
        config_file = self.config_dir / f"{renderer_name}.json"
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    file_config = json.load(f)
                config.update(file_config)
                self.logger.debug(f"Loaded config from {config_file}")
            except Exception as e:
                self.logger.warning(f"Failed to load config from {config_file}: {e}")

        # Override with environment variables
        env_config = self._load_env_config(renderer_name)
        config.update(env_config)

        # Validate against schema if provided
        if schema:
            self._schemas[renderer_name] = schema
            validation_errors = self._validate_config(config, schema)
            if validation_errors:
                self.logger.warning(
                    f"Configuration validation errors for {renderer_name}: {validation_errors}"
                )

        # Cache the configuration
        self._configs[renderer_name] = config

        return config

    def save_renderer_config(
        self,
        renderer_name: str,
        config: Dict[str, Any],
        validate: bool = True,
    ) -> bool:
        """
        Save configuration for a specific renderer.

        Args:
            renderer_name: Name of the renderer
            config: Configuration to save
            validate: Whether to validate before saving

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Validate if schema is available
            if validate and renderer_name in self._schemas:
                validation_errors = self._validate_config(
                    config, self._schemas[renderer_name])
                if validation_errors:
                    self.logger.error(
                        f"Cannot save invalid config for {renderer_name}: {validation_errors}"
                    )
                    return False

            # Save to file
            config_file = self.config_dir / f"{renderer_name}.json"
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)

            # Update cached config
            self._configs[renderer_name] = config.copy()

            self.logger.info(
                f"Saved configuration for {renderer_name} to {config_file}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to save config for {renderer_name}: {e}")
            return False

    def get_renderer_config(
        self,
        renderer_name: str,
        key: Optional[str] = None,
        default: Any = None,
    ) -> Any:
        """
        Get configuration value for a renderer.

        Args:
            renderer_name: Name of the renderer
            key: Specific configuration key (returns full config if None)
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        if renderer_name not in self._configs:
            return default if key else {}

        config = self._configs[renderer_name]

        if key is None:
            return config

        return config.get(key, default)

    def set_renderer_config(
        self,
        renderer_name: str,
        key: str,
        value: Any,
        save: bool = False,
    ) -> bool:
        """
        Set configuration value for a renderer.

        Args:
            renderer_name: Name of the renderer
            key: Configuration key
            value: Configuration value
            save: Whether to save to file immediately

        Returns:
            True if set successfully, False otherwise
        """
        try:
            # Initialize config if not exists
            if renderer_name not in self._configs:
                self._configs[renderer_name] = {}

            # Set the value
            self._configs[renderer_name][key] = value

            # Save if requested
            if save:
                return self.save_renderer_config(renderer_name, self._configs[renderer_name])

            return True

        except Exception as e:
            self.logger.error(f"Failed to set config {key} for {renderer_name}: {e}")
            return False

    def _load_env_config(self, renderer_name: str) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        config = {}
        prefix = f"{self.env_prefix}_{renderer_name.upper()}_"

        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix):].lower()

                # Try to parse as JSON first, then as string
                try:
                    config[config_key] = json.loads(value)
                except json.JSONDecodeError:
                    config[config_key] = value

        if config:
            self.logger.debug(
                f"Loaded environment config for {renderer_name}: {list(config.keys())}")

        return config

    def _validate_config(
        self,
        config: Dict[str, Any],
        schema: Dict[str, Any],
    ) -> List[str]:
        """Validate configuration against JSON schema."""
        try:
            jsonschema.validate(config, schema)
            return []
        except jsonschema.ValidationError as e:
            return [str(e)]
        except Exception as e:
            return [f"Schema validation error: {e}"]

    def get_all_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get all loaded renderer configurations."""
        return self._configs.copy()

    def clear_config(self, renderer_name: str) -> bool:
        """
        Clear configuration for a renderer.

        Args:
            renderer_name: Name of the renderer

        Returns:
            True if cleared successfully
        """
        try:
            if renderer_name in self._configs:
                del self._configs[renderer_name]

            # Remove config file if it exists
            config_file = self.config_dir / f"{renderer_name}.json"
            if config_file.exists():
                config_file.unlink()

            self.logger.info(f"Cleared configuration for {renderer_name}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to clear config for {renderer_name}: {e}")
            return False

    def export_configs(self, output_path: Union[str, Path]) -> bool:
        """
        Export all configurations to a file.

        Args:
            output_path: Path to export file

        Returns:
            True if exported successfully
        """
        try:
            export_data = {
                "version": "1.0",
                "configs": self._configs,
                "schemas": self._schemas,
            }

            with open(output_path, 'w') as f:
                json.dump(export_data, f, indent=2)

            self.logger.info(f"Exported configurations to {output_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to export configurations: {e}")
            return False

    def import_configs(self, input_path: Union[str, Path]) -> bool:
        """
        Import configurations from a file.

        Args:
            input_path: Path to import file

        Returns:
            True if imported successfully
        """
        try:
            with open(input_path, 'r') as f:
                import_data = json.load(f)

            if "configs" in import_data:
                self._configs.update(import_data["configs"])

            if "schemas" in import_data:
                self._schemas.update(import_data["schemas"])

            self.logger.info(f"Imported configurations from {input_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to import configurations: {e}")
            return False


# Global config manager instance
_global_config_manager: Optional[RendererConfigManager] = None


def get_global_config_manager() -> RendererConfigManager:
    """Get the global renderer configuration manager instance."""
    global _global_config_manager
    if _global_config_manager is None:
        _global_config_manager = RendererConfigManager()
    return _global_config_manager
