"""
Core classes for the Mermaid Render library.

This module contains the main classes that form the foundation of the library:
- MermaidRenderer: Main rendering engine
- MermaidDiagram: Base class for all diagram types
- MermaidTheme: Theme configuration
- MermaidConfig: Global configuration management
"""

import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    import mermaid as md  # type: ignore[import-untyped]  # noqa: F401
    _MERMAID_AVAILABLE = True
except ImportError:
    md = None
    _MERMAID_AVAILABLE = False

from .exceptions import (
    ConfigurationError,
    RenderingError,
    UnsupportedFormatError,
    ValidationError,
)
from .renderers import PDFRenderer, PNGRenderer, SVGRenderer


class MermaidConfig:
    """
    Configuration management for Mermaid rendering.

    This class handles global settings, server configuration, and rendering options
    for the Mermaid Render library. It provides a centralized way to manage all
    configuration aspects including timeouts, caching, validation, and server URLs.

    The configuration follows a hierarchical approach where values can be set from:
    1. Default values (lowest priority)
    2. Environment variables
    3. Configuration files
    4. Runtime parameters (highest priority)

    Attributes:
        _config (Dict[str, Any]): Internal configuration dictionary

    Example:
        >>> # Basic configuration
        >>> config = MermaidConfig()
        >>>
        >>> # Configuration with custom values
        >>> config = MermaidConfig(
        ...     timeout=60,
        ...     default_theme="dark",
        ...     validate_syntax=True,
        ...     cache_enabled=True
        ... )
        >>>
        >>> # Access configuration values
        >>> timeout = config.get("timeout")
        >>> config.set("server_url", "https://custom-server.com")
    """

    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize configuration with default values.

        Creates a new configuration instance with sensible defaults that can be
        overridden by the provided keyword arguments. Environment variables are
        automatically loaded if they exist.

        Args:
            **kwargs: Configuration options to override defaults. Common options include:
                - timeout (int): Request timeout in seconds (default: 30)
                - retries (int): Number of retry attempts (default: 3)
                - default_theme (str): Default theme name (default: "default")
                - default_format (str): Default output format (default: "svg")
                - validate_syntax (bool): Enable syntax validation (default: True)
                - cache_enabled (bool): Enable caching (default: True)
                - cache_dir (Path): Cache directory path
                - server_url (str): Mermaid rendering server URL

        Example:
            >>> # Default configuration
            >>> config = MermaidConfig()
            >>>
            >>> # Custom configuration
            >>> config = MermaidConfig(
            ...     timeout=45,
            ...     default_theme="forest",
            ...     cache_enabled=False
            ... )
        """
        self._config: Dict[str, Any] = {
            "server_url": os.getenv("MERMAID_INK_SERVER", "https://mermaid.ink"),
            "timeout": 30,
            "retries": 3,
            "default_theme": "default",
            "default_format": "svg",
            "validate_syntax": True,
            "cache_enabled": True,
            "cache_dir": Path.home() / ".mermaid_render_cache",
        }
        self._config.update(kwargs)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.

        Args:
            key: Configuration key to retrieve
            default: Default value to return if key is not found

        Returns:
            Configuration value or default if key doesn't exist

        Example:
            >>> config = MermaidConfig()
            >>> timeout = config.get("timeout", 30)
            >>> theme = config.get("default_theme")
        """
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value.

        Args:
            key: Configuration key to set
            value: Value to assign to the key

        Example:
            >>> config = MermaidConfig()
            >>> config.set("timeout", 60)
            >>> config.set("default_theme", "dark")
        """
        self._config[key] = value

    def update(self, config: Dict[str, Any]) -> None:
        """
        Update multiple configuration values at once.

        Args:
            config: Dictionary of configuration key-value pairs to update

        Example:
            >>> config = MermaidConfig()
            >>> config.update({
            ...     "timeout": 45,
            ...     "default_theme": "forest",
            ...     "cache_enabled": False
            ... })
        """
        self._config.update(config)

    def to_dict(self) -> Dict[str, Any]:
        """
        Return configuration as dictionary.

        Returns:
            Copy of the internal configuration dictionary

        Example:
            >>> config = MermaidConfig()
            >>> config_dict = config.to_dict()
            >>> print(f"Current timeout: {config_dict['timeout']}")
        """
        return self._config.copy()


class MermaidTheme:
    """
    Theme configuration for Mermaid diagrams.

    This class manages color schemes, fonts, and styling options for Mermaid diagrams.
    It supports both built-in themes and custom theme configurations, allowing for
    comprehensive visual customization of rendered diagrams.

    Built-in themes include:
    - default: Standard Mermaid theme
    - dark: Dark mode theme with light text on dark backgrounds
    - forest: Green-based theme with natural colors
    - neutral: Neutral color palette
    - base: Minimal base theme

    Custom themes can be created by providing theme configuration parameters
    such as colors, fonts, and other styling options.

    Attributes:
        BUILT_IN_THEMES (Dict[str, Dict]): Available built-in theme configurations
        name (str): Theme name
        _config (Dict[str, Any]): Theme configuration dictionary

    Example:
        >>> # Use built-in theme
        >>> theme = MermaidTheme("dark")
        >>>
        >>> # Create custom theme
        >>> custom_theme = MermaidTheme("custom",
        ...     primaryColor="#ff6b6b",
        ...     primaryTextColor="#ffffff",
        ...     lineColor="#4ecdc4",
        ...     backgroundColor="#2c3e50"
        ... )
        >>>
        >>> # Apply theme to renderer
        >>> renderer = MermaidRenderer()
        >>> renderer.set_theme(theme)
    """

    BUILT_IN_THEMES = {
        "default": {},
        "dark": {"theme": "dark"},
        "forest": {"theme": "forest"},
        "neutral": {"theme": "neutral"},
        "base": {"theme": "base"},
    }

    def __init__(self, name: str = "default", **custom_config: Any) -> None:
        """
        Initialize theme configuration.

        Args:
            name: Built-in theme name or "custom" for custom themes. Available
                built-in themes: "default", "dark", "forest", "neutral", "base"
            **custom_config: Custom theme configuration options. Common options include:
                - primaryColor (str): Primary color for diagram elements
                - primaryTextColor (str): Text color for primary elements
                - lineColor (str): Color for lines and borders
                - backgroundColor (str): Background color
                - secondaryColor (str): Secondary color for accents
                - tertiaryColor (str): Tertiary color for additional elements

        Raises:
            ConfigurationError: If the specified theme name is not recognized

        Example:
            >>> # Built-in theme
            >>> dark_theme = MermaidTheme("dark")
            >>>
            >>> # Custom theme with specific colors
            >>> corporate_theme = MermaidTheme("custom",
            ...     primaryColor="#2c3e50",
            ...     primaryTextColor="#ffffff",
            ...     lineColor="#34495e",
            ...     backgroundColor="#ecf0f1"
            ... )
        """
        self.name = name
        self._config: Dict[str, Any] = {}

        if name in self.BUILT_IN_THEMES:
            self._config = self.BUILT_IN_THEMES[name].copy()
        elif name == "custom":
            self._config = {}
        else:
            raise ConfigurationError(f"Unknown theme: {name}")

        self._config.update(custom_config)

    def to_dict(self) -> Dict[str, Any]:
        """
        Return theme configuration as dictionary.

        Returns:
            Copy of the theme configuration dictionary

        Example:
            >>> theme = MermaidTheme("dark")
            >>> config = theme.to_dict()
            >>> print(f"Theme config: {config}")
        """
        return self._config.copy()

    def apply_to_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply theme settings to a configuration dictionary.

        This method merges the theme configuration with an existing configuration
        dictionary, with theme settings taking precedence.

        Args:
            config: Base configuration dictionary to apply theme to

        Returns:
            New configuration dictionary with theme settings applied

        Example:
            >>> theme = MermaidTheme("dark")
            >>> base_config = {"timeout": 30}
            >>> themed_config = theme.apply_to_config(base_config)
        """
        result = config.copy()
        result.update(self._config)
        return result


class MermaidDiagram(ABC):
    """
    Abstract base class for all Mermaid diagram types.

    This class provides the foundation for all diagram types in the Mermaid Render
    library. It defines the common interface and functionality that all diagram
    types must implement, including validation, configuration management, and
    Mermaid syntax generation.

    All concrete diagram classes (FlowchartDiagram, SequenceDiagram, etc.) inherit
    from this base class and must implement the abstract methods to define their
    specific diagram type and syntax generation logic.

    Attributes:
        title (Optional[str]): Optional diagram title
        _elements (List[str]): Internal list of diagram elements
        _config (Dict[str, Any]): Diagram-specific configuration

    Example:
        This is an abstract class and cannot be instantiated directly.
        Use concrete implementations like:

        >>> from mermaid_render import FlowchartDiagram
        >>> diagram = FlowchartDiagram(title="My Process Flow")
        >>> diagram.add_node("A", "Start")
        >>> mermaid_code = diagram.to_mermaid()
    """

    def __init__(self, title: Optional[str] = None) -> None:
        """
        Initialize diagram with optional title.

        Args:
            title: Optional diagram title that will be displayed above the diagram

        Example:
            >>> # This is called by concrete diagram classes
            >>> diagram = FlowchartDiagram(title="User Registration Process")
        """
        self.title = title
        self._elements: List[str] = []
        self._config: Dict[str, Any] = {}
        self._cached_mermaid: Optional[str] = None
        self._is_disposed: bool = False

    @abstractmethod
    def get_diagram_type(self) -> str:
        """
        Return the Mermaid diagram type identifier.

        This method must be implemented by all concrete diagram classes to return
        the specific diagram type identifier used in Mermaid syntax (e.g., "flowchart",
        "sequenceDiagram", "classDiagram").

        Returns:
            String identifier for the diagram type

        Example:
            >>> class FlowchartDiagram(MermaidDiagram):
            ...     def get_diagram_type(self) -> str:
            ...         return "flowchart"
        """
        pass

    def to_mermaid(self) -> str:
        """
        Generate Mermaid syntax for this diagram.

        This method generates the complete Mermaid syntax string for the diagram,
        including the diagram type declaration and all diagram elements. It uses
        caching to improve performance for repeated calls.

        Returns:
            Complete Mermaid syntax string for the diagram

        Raises:
            RuntimeError: If the diagram has been disposed

        Example:
            >>> diagram = FlowchartDiagram()
            >>> diagram.add_node("A", "Start")
            >>> mermaid_code = diagram.to_mermaid()
            >>> print(mermaid_code)
            flowchart TD
                A[Start]
        """
        self._check_disposed()

        # Use cached version if available
        if self._cached_mermaid is not None:
            return self._cached_mermaid

        # Generate new Mermaid syntax
        self._cached_mermaid = self._generate_mermaid()
        return self._cached_mermaid

    @abstractmethod
    def _generate_mermaid(self) -> str:
        """
        Generate Mermaid syntax for this diagram (internal implementation).

        This method must be implemented by all concrete diagram classes to generate
        the complete Mermaid syntax string for the diagram, including the diagram
        type declaration and all diagram elements.

        Returns:
            Complete Mermaid syntax string for the diagram

        Note:
            This is the internal implementation that concrete classes should override.
            External code should call to_mermaid() instead.
        """
        pass

    def add_config(self, key: str, value: Any) -> None:
        """
        Add configuration option to the diagram.

        Args:
            key: Configuration key
            value: Configuration value

        Example:
            >>> diagram = FlowchartDiagram()
            >>> diagram.add_config("direction", "LR")
            >>> diagram.add_config("theme", "dark")
        """
        self._check_disposed()
        self._config[key] = value
        # Clear cache since configuration changed
        self.clear_cache()

    def get_config(self) -> Dict[str, Any]:
        """
        Get diagram configuration.

        Returns:
            Copy of the diagram configuration dictionary

        Example:
            >>> diagram = FlowchartDiagram()
            >>> diagram.add_config("direction", "TD")
            >>> config = diagram.get_config()
            >>> print(f"Direction: {config.get('direction')}")
        """
        return self._config.copy()

    def validate(self) -> bool:
        """
        Validate the diagram syntax.

        Uses the built-in validator to check if the generated Mermaid syntax
        is valid and can be rendered successfully.

        Returns:
            True if diagram is valid, False otherwise

        Example:
            >>> diagram = FlowchartDiagram()
            >>> diagram.add_node("A", "Start")
            >>> if diagram.validate():
            ...     print("Diagram is valid!")
            ... else:
            ...     print("Diagram has validation errors")
        """
        from .validators import MermaidValidator

        validator = MermaidValidator()
        result = validator.validate(self.to_mermaid())
        return result.is_valid

    def clear_cache(self) -> None:
        """
        Clear any cached diagram data.

        This method clears internal caches to free up memory. It's useful
        for long-running applications or when processing many diagrams.

        Example:
            >>> diagram = FlowchartDiagram()
            >>> # ... build diagram ...
            >>> diagram.clear_cache()  # Free cached data
        """
        self._cached_mermaid = None

    def dispose(self) -> None:
        """
        Dispose of diagram resources and mark as disposed.

        This method cleans up all internal resources and marks the diagram
        as disposed. After calling this method, the diagram should not be used.

        Example:
            >>> diagram = FlowchartDiagram()
            >>> # ... use diagram ...
            >>> diagram.dispose()  # Clean up resources
        """
        if self._is_disposed:
            return

        # Clear all data structures
        self._elements.clear()
        self._config.clear()
        self._cached_mermaid = None
        self.title = None

        # Mark as disposed
        self._is_disposed = True

    def __del__(self) -> None:
        """
        Destructor to ensure proper cleanup.

        Automatically called when the diagram object is garbage collected.
        Ensures that resources are properly cleaned up even if dispose()
        wasn't called explicitly.
        """
        try:
            self.dispose()
        except Exception:
            # Ignore errors during cleanup to avoid issues during shutdown
            pass

    def _check_disposed(self) -> None:
        """
        Check if diagram has been disposed and raise error if so.

        Raises:
            RuntimeError: If the diagram has been disposed
        """
        if self._is_disposed:
            raise RuntimeError("Cannot use diagram after it has been disposed")

    def __str__(self) -> str:
        """
        Return Mermaid syntax representation.

        Returns:
            Complete Mermaid syntax string for the diagram

        Example:
            >>> diagram = FlowchartDiagram()
            >>> diagram.add_node("A", "Start")
            >>> print(str(diagram))  # Same as diagram.to_mermaid()
        """
        return self.to_mermaid()


class MermaidRenderer:
    """
    Main rendering engine for Mermaid diagrams.

    This class is the primary interface for rendering Mermaid diagrams to various
    output formats. It handles the complete rendering pipeline including validation,
    theme application, format conversion, and output management.

    The renderer supports multiple output formats (SVG, PNG, PDF) and provides
    comprehensive configuration options for customizing the rendering process.
    It can work with both diagram objects and raw Mermaid syntax strings.

    Key features:
    - Multiple output formats (SVG, PNG, PDF)
    - Theme support (built-in and custom themes)
    - Syntax validation
    - Caching support
    - Error handling and recovery
    - Batch processing capabilities

    Attributes:
        SUPPORTED_FORMATS (List[str]): List of supported output formats
        config (MermaidConfig): Configuration object
        _theme (Optional[MermaidTheme]): Current theme

    Example:
        >>> from mermaid_render import MermaidRenderer, FlowchartDiagram
        >>>
        >>> # Basic usage
        >>> renderer = MermaidRenderer()
        >>> diagram = FlowchartDiagram()
        >>> diagram.add_node("A", "Start")
        >>> svg_content = renderer.render(diagram, format="svg")
        >>>
        >>> # With custom configuration and theme
        >>> config = MermaidConfig(timeout=60, validate_syntax=True)
        >>> renderer = MermaidRenderer(config=config, theme="dark")
        >>> renderer.save(diagram, "output.png", format="png")
    """

    SUPPORTED_FORMATS = ["svg", "png", "pdf"]

    def __init__(
        self,
        config: Optional[MermaidConfig] = None,
        theme: Optional[Union[str, MermaidTheme]] = None,
    ) -> None:
        """
        Initialize the renderer.

        Args:
            config: Optional configuration object. If not provided, default
                configuration will be used
            theme: Optional theme name (string) or MermaidTheme object. Available
                built-in themes: "default", "dark", "forest", "neutral", "base"

        Example:
            >>> # Default renderer
            >>> renderer = MermaidRenderer()
            >>>
            >>> # With custom config
            >>> config = MermaidConfig(timeout=45, cache_enabled=True)
            >>> renderer = MermaidRenderer(config=config)
            >>>
            >>> # With theme
            >>> renderer = MermaidRenderer(theme="dark")
            >>>
            >>> # With both config and theme
            >>> renderer = MermaidRenderer(config=config, theme="forest")
        """
        self.config = config or MermaidConfig()
        self._theme: Optional[MermaidTheme] = None

        # Initialize format-specific renderers
        self._svg_renderer = SVGRenderer()
        self._png_renderer = PNGRenderer(
            server_url=self.config.get("server_url", "https://mermaid.ink"),
            timeout=self.config.get("timeout", 30.0),
        )
        self._pdf_renderer = PDFRenderer()

        if theme:
            self.set_theme(theme)

    def set_theme(self, theme: Union[str, MermaidTheme]) -> None:
        """
        Set the rendering theme.

        Args:
            theme: Theme name (string) or MermaidTheme object. For string themes,
                must be one of the built-in themes: "default", "dark", "forest",
                "neutral", "base"

        Raises:
            ConfigurationError: If theme type is invalid or theme name is not recognized

        Example:
            >>> renderer = MermaidRenderer()
            >>>
            >>> # Set built-in theme
            >>> renderer.set_theme("dark")
            >>>
            >>> # Set custom theme object
            >>> custom_theme = MermaidTheme("custom", primaryColor="#ff6b6b")
            >>> renderer.set_theme(custom_theme)
        """
        if isinstance(theme, str):
            self._theme = MermaidTheme(theme)
        elif isinstance(theme, MermaidTheme):
            self._theme = theme
        else:
            raise ConfigurationError(f"Invalid theme type: {type(theme)}")

    def get_theme(self) -> Optional[MermaidTheme]:
        """
        Get current theme.

        Returns:
            Current MermaidTheme object or None if no theme is set

        Example:
            >>> renderer = MermaidRenderer(theme="dark")
            >>> current_theme = renderer.get_theme()
            >>> if current_theme:
            ...     print(f"Current theme: {current_theme.name}")
        """
        return self._theme

    def render(
        self,
        diagram: Union[MermaidDiagram, str],
        format: str = "svg",
        **options: Any,
    ) -> Union[str, bytes]:
        """
        Render a diagram to the specified format.

        Args:
            diagram: MermaidDiagram object or raw Mermaid syntax
            format: Output format (svg, png, pdf)
            **options: Additional rendering options

        Returns:
            Rendered diagram content

        Raises:
            UnsupportedFormatError: If format is not supported
            RenderingError: If rendering fails
            ValidationError: If diagram is invalid
        """
        if format not in self.SUPPORTED_FORMATS:
            raise UnsupportedFormatError(f"Unsupported format: {format}")

        # Get Mermaid syntax
        if isinstance(diagram, MermaidDiagram):
            mermaid_code = diagram.to_mermaid()

            # Validate if enabled
            if self.config.get("validate_syntax", True):
                if not diagram.validate():
                    raise ValidationError("Invalid diagram syntax")
        else:
            mermaid_code = diagram

            # Validate raw syntax if enabled
            if self.config.get("validate_syntax", True):
                from .validators import MermaidValidator

                validator = MermaidValidator()
                result = validator.validate(mermaid_code)
                if not result.is_valid:
                    raise ValidationError(f"Invalid syntax: {result.errors}")

        return self.render_raw(mermaid_code, format, **options)

    def render_raw(
        self, mermaid_code: str, format: str = "svg", **options: Any
    ) -> Union[str, bytes]:
        """
        Render raw Mermaid code to specified format.

        Args:
            mermaid_code: Raw Mermaid diagram syntax
            format: Output format
            **options: Additional rendering options

        Returns:
            Rendered content (str for SVG, bytes for PNG/PDF)
        """
        try:
            # Prepare theme configuration
            theme_name = None
            if self._theme:
                theme_name = self._theme.name if self._theme.name != "custom" else None
                # For custom themes, pass the config directly
                if self._theme.name == "custom":
                    options.update(self._theme.to_dict())

            if format == "svg":
                # Use SVG renderer
                return self._svg_renderer.render(
                    mermaid_code, theme=theme_name, config=options
                )
            elif format == "png":
                # Use PNG renderer
                return self._png_renderer.render(
                    mermaid_code,
                    theme=theme_name,
                    config=options,
                    width=options.get("width"),
                    height=options.get("height"),
                )
            elif format == "pdf":
                # Use PDF renderer - first get SVG, then convert
                # Disable validation for PDF conversion to avoid XML parsing issues
                svg_content = self._svg_renderer.render(
                    mermaid_code,
                    theme=theme_name,
                    config=options,
                    validate=False,
                    sanitize=False,
                )
                # PDF renderer expects SVG content, not mermaid code
                return self._pdf_renderer.render_from_svg(svg_content)
            else:
                raise UnsupportedFormatError(f"Unsupported format: {format}")

        except Exception as e:
            raise RenderingError(f"Failed to render diagram: {str(e)}") from e

    def save(
        self,
        diagram: Union[MermaidDiagram, str],
        output_path: Union[str, Path],
        format: Optional[str] = None,
        **options: Any,
    ) -> None:
        """
        Render and save diagram to file.

        Args:
            diagram: Diagram to render
            output_path: Output file path
            format: Output format (inferred from extension if not provided)
            **options: Additional rendering options
        """
        output_path = Path(output_path)

        # Infer format from extension if not provided
        if format is None:
            format = output_path.suffix.lstrip(".").lower()
            if not format:
                format = self.config.get("default_format", "svg")

        # Ensure format is not None at this point
        assert format is not None, "Format should not be None after inference"

        # Render the diagram
        content = self.render(diagram, format, **options)

        # Create output directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write to file
        mode = "w" if format == "svg" else "wb"
        with open(output_path, mode) as f:
            if format == "svg":
                f.write(content)
            else:
                # For binary formats, content should be bytes
                if isinstance(content, str):
                    f.write(content.encode())
                else:
                    f.write(content)
