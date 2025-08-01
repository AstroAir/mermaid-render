"""
Theme management for the Mermaid Render library.

This module provides comprehensive theme management with built-in themes,
custom theme support, and theme validation.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..exceptions import ThemeError


class ThemeManager:
    """
    Comprehensive theme management for Mermaid diagrams.

    The ThemeManager provides a centralized system for managing both built-in and
    custom themes for Mermaid diagrams. It handles theme loading, validation,
    storage, and retrieval, making it easy to apply consistent styling across
    all diagrams in an application.

    Key features:
    - Built-in theme collection with popular color schemes
    - Custom theme support with JSON-based storage
    - Theme validation and error handling
    - Dynamic theme loading and caching
    - Theme inheritance and composition
    - Export/import capabilities for theme sharing

    Built-in themes include:
    - default: Standard Mermaid theme with light colors
    - dark: Dark mode theme with light text on dark backgrounds
    - forest: Green-based nature theme
    - neutral: Minimal neutral color palette
    - base: Clean base theme for customization

    Attributes:
        BUILT_IN_THEMES (Dict[str, Dict]): Collection of built-in theme configurations
        custom_themes_dir (Optional[Path]): Directory for custom theme files
        _custom_themes (Dict[str, Dict]): Loaded custom theme configurations

    Example:
        >>> from mermaid_render.config import ThemeManager
        >>>
        >>> # Basic usage
        >>> theme_manager = ThemeManager()
        >>> dark_theme = theme_manager.get_theme("dark")
        >>>
        >>> # With custom themes directory
        >>> theme_manager = ThemeManager(custom_themes_dir=Path("./themes"))
        >>>
        >>> # Add custom theme
        >>> corporate_theme = {
        ...     "primaryColor": "#2c3e50",
        ...     "primaryTextColor": "#ffffff",
        ...     "lineColor": "#34495e"
        ... }
        >>> theme_manager.add_custom_theme("corporate", corporate_theme)
        >>>
        >>> # List all available themes
        >>> themes = theme_manager.get_available_themes()
        >>> print(f"Available themes: {', '.join(themes)}")
    """

    # Built-in themes with their configurations
    BUILT_IN_THEMES = {
        "default": {
            "theme": "default",
            "primaryColor": "#fff2cc",
            "primaryTextColor": "#333",
            "primaryBorderColor": "#d6b656",
            "lineColor": "#333333",
            "secondaryColor": "#eeeeee",
            "tertiaryColor": "#fff2cc",
        },
        "dark": {
            "theme": "dark",
            "primaryColor": "#1f2020",
            "primaryTextColor": "#fff",
            "primaryBorderColor": "#81B1DB",
            "lineColor": "#81B1DB",
            "secondaryColor": "#2e2f2f",
            "tertiaryColor": "#1f2020",
        },
        "forest": {
            "theme": "forest",
            "primaryColor": "#cde498",
            "primaryTextColor": "#333",
            "primaryBorderColor": "#13540a",
            "lineColor": "#333333",
            "secondaryColor": "#cdffb2",
            "tertiaryColor": "#cde498",
        },
        "neutral": {
            "theme": "neutral",
            "primaryColor": "#eee",
            "primaryTextColor": "#333",
            "primaryBorderColor": "#cccccc",
            "lineColor": "#333333",
            "secondaryColor": "#efefef",
            "tertiaryColor": "#eee",
        },
        "base": {
            "theme": "base",
            "primaryColor": "#ffffff",
            "primaryTextColor": "#333",
            "primaryBorderColor": "#cccccc",
            "lineColor": "#666666",
            "secondaryColor": "#f9f9f9",
            "tertiaryColor": "#ffffff",
        },
    }

    def __init__(self, custom_themes_dir: Optional[Path] = None) -> None:
        """
        Initialize theme manager.

        Sets up the theme manager with optional custom themes directory.
        If a custom themes directory is provided, it will be scanned for
        JSON theme files and loaded automatically.

        Args:
            custom_themes_dir: Optional directory path containing custom theme
                JSON files. Each file should contain a theme configuration
                dictionary. Files should be named with .json extension.

        Example:
            >>> # Basic initialization
            >>> theme_manager = ThemeManager()
            >>>
            >>> # With custom themes directory
            >>> theme_manager = ThemeManager(Path("./my_themes"))
            >>>
            >>> # Custom themes directory structure:
            >>> # my_themes/
            >>> #   ├── corporate.json
            >>> #   ├── brand.json
            >>> #   └── presentation.json
        """
        self.custom_themes_dir = custom_themes_dir
        self._custom_themes: Dict[str, Dict[str, Any]] = {}
        self._load_custom_themes()

    def get_theme(self, theme_name: str) -> Dict[str, Any]:
        """
        Get theme configuration by name.

        Args:
            theme_name: Name of the theme

        Returns:
            Theme configuration dictionary

        Raises:
            ThemeError: If theme does not exist
        """
        if theme_name in self.BUILT_IN_THEMES:
            return self.BUILT_IN_THEMES[theme_name].copy()
        elif theme_name in self._custom_themes:
            return self._custom_themes[theme_name].copy()
        else:
            available = self.get_available_themes()
            raise ThemeError(
                f"Theme '{theme_name}' not found",
                theme_name=theme_name,
                available_themes=available,
            )

    def get_available_themes(self) -> List[str]:
        """Get list of all available theme names."""
        built_in = list(self.BUILT_IN_THEMES.keys())
        custom = list(self._custom_themes.keys())
        return sorted(built_in + custom)

    def get_built_in_themes(self) -> List[str]:
        """Get list of built-in theme names."""
        return list(self.BUILT_IN_THEMES.keys())

    def get_custom_themes(self) -> List[str]:
        """Get list of custom theme names."""
        return list(self._custom_themes.keys())

    def is_theme_available(self, theme_name: str) -> bool:
        """Check if a theme is available."""
        return theme_name in self.BUILT_IN_THEMES or theme_name in self._custom_themes

    def add_custom_theme(
        self,
        theme_name: str,
        theme_config: Dict[str, Any],
        save_to_file: bool = True,
    ) -> None:
        """
        Add a custom theme.

        Args:
            theme_name: Name for the new theme
            theme_config: Theme configuration dictionary
            save_to_file: Whether to save theme to file

        Raises:
            ThemeError: If theme name conflicts or config is invalid
        """
        if theme_name in self.BUILT_IN_THEMES:
            raise ThemeError(f"Cannot override built-in theme: {theme_name}")

        # Validate theme configuration
        self._validate_theme_config(theme_config)

        # Add to custom themes
        self._custom_themes[theme_name] = theme_config.copy()

        # Save to file if requested and directory is set
        if save_to_file and self.custom_themes_dir:
            self._save_theme_to_file(theme_name, theme_config)

    def remove_custom_theme(self, theme_name: str, delete_file: bool = True) -> None:
        """
        Remove a custom theme.

        Args:
            theme_name: Name of theme to remove
            delete_file: Whether to delete theme file

        Raises:
            ThemeError: If theme doesn't exist or is built-in
        """
        if theme_name in self.BUILT_IN_THEMES:
            raise ThemeError(f"Cannot remove built-in theme: {theme_name}")

        if theme_name not in self._custom_themes:
            raise ThemeError(f"Custom theme '{theme_name}' not found")

        # Remove from memory
        del self._custom_themes[theme_name]

        # Delete file if requested
        if delete_file and self.custom_themes_dir:
            theme_file = self.custom_themes_dir / f"{theme_name}.json"
            if theme_file.exists():
                theme_file.unlink()

    def create_theme_variant(
        self,
        base_theme: str,
        variant_name: str,
        modifications: Dict[str, Any],
        save_to_file: bool = True,
    ) -> None:
        """
        Create a theme variant based on an existing theme.

        Args:
            base_theme: Name of base theme
            variant_name: Name for the variant
            modifications: Modifications to apply to base theme
            save_to_file: Whether to save variant to file
        """
        base_config = self.get_theme(base_theme)
        variant_config = base_config.copy()
        variant_config.update(modifications)

        self.add_custom_theme(variant_name, variant_config, save_to_file)

    def _validate_theme_config(self, config: Dict[str, Any]) -> None:
        """
        Validate theme configuration.

        Args:
            config: Theme configuration to validate

        Raises:
            ThemeError: If configuration is invalid
        """
        required_fields = ["theme"]
        optional_fields = [
            "primaryColor",
            "primaryTextColor",
            "primaryBorderColor",
            "lineColor",
            "secondaryColor",
            "tertiaryColor",
            "background",
            "mainBkg",
            "secondBkg",
            "tertiaryBkg",
        ]

        # Check for required fields
        for field in required_fields:
            if field not in config:
                raise ThemeError(f"Missing required theme field: {field}")

        # Validate color values (basic validation)
        color_fields = [
            f for f in config.keys() if "color" in f.lower() or "bkg" in f.lower()
        ]
        for field in color_fields:
            value = config[field]
            if isinstance(value, str) and not self._is_valid_color(value):
                raise ThemeError(f"Invalid color value for {field}: {value}")

    def _is_valid_color(self, color: str) -> bool:
        """
        Basic color validation.

        Args:
            color: Color string to validate

        Returns:
            True if color appears valid
        """
        # Basic validation for hex colors and named colors
        if color.startswith("#"):
            return len(color) in [4, 7] and all(
                c in "0123456789abcdefABCDEF" for c in color[1:]
            )

        # Allow common named colors
        named_colors = {
            "red",
            "green",
            "blue",
            "yellow",
            "orange",
            "purple",
            "pink",
            "black",
            "white",
            "gray",
            "grey",
            "brown",
            "cyan",
            "magenta",
            "transparent",
            "inherit",
            "initial",
            "unset",
        }
        return color.lower() in named_colors

    def _load_custom_themes(self) -> None:
        """Load custom themes from files."""
        if not self.custom_themes_dir or not self.custom_themes_dir.exists():
            return

        for theme_file in self.custom_themes_dir.glob("*.json"):
            try:
                with open(theme_file, encoding="utf-8") as f:
                    theme_config = json.load(f)

                theme_name = theme_file.stem
                self._validate_theme_config(theme_config)
                self._custom_themes[theme_name] = theme_config

            except (json.JSONDecodeError, ThemeError) as e:
                # Log error but continue loading other themes
                print(f"Warning: Failed to load theme from {theme_file}: {e}")

    def _save_theme_to_file(
        self, theme_name: str, theme_config: Dict[str, Any]
    ) -> None:
        """Save theme configuration to file."""
        if not self.custom_themes_dir:
            return

        self.custom_themes_dir.mkdir(parents=True, exist_ok=True)
        theme_file = self.custom_themes_dir / f"{theme_name}.json"

        with open(theme_file, "w", encoding="utf-8") as f:
            json.dump(theme_config, f, indent=2)

    def export_theme(self, theme_name: str, output_path: Path) -> None:
        """
        Export theme configuration to file.

        Args:
            theme_name: Name of theme to export
            output_path: Output file path
        """
        theme_config = self.get_theme(theme_name)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(theme_config, f, indent=2)

    def import_theme(self, theme_file: Path, theme_name: Optional[str] = None) -> str:
        """
        Import theme from file.

        Args:
            theme_file: Path to theme file
            theme_name: Optional name for imported theme (defaults to filename)

        Returns:
            Name of imported theme
        """
        with open(theme_file, encoding="utf-8") as f:
            theme_config = json.load(f)

        name = theme_name or theme_file.stem
        self.add_custom_theme(name, theme_config, save_to_file=False)

        return name
