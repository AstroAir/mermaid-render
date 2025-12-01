"""
Plugin-based MermaidRenderer with advanced architecture.

This module provides a plugin-based version of MermaidRenderer that uses
the new plugin-based rendering system while maintaining backward compatibility.
"""

import logging
import time
from pathlib import Path
from typing import Any

from .core import MermaidConfig, MermaidDiagram, MermaidTheme
from .exceptions import ConfigurationError, RenderingError
from .renderers import (
    RendererCapability,
    RendererManager,
    get_global_registry,
)


class PluginMermaidRenderer:
    """
    Plugin-based MermaidRenderer with advanced architecture.

    This class provides an improved rendering interface that uses the new
    plugin-based renderer system. It maintains backward compatibility with
    the original MermaidRenderer while adding new capabilities like
    renderer selection, fallback handling, and improved error reporting.

    Key improvements:
    - Plugin-based renderer architecture
    - Automatic fallback between renderers
    - Improved error handling and reporting
    - Renderer-specific configuration
    - Performance monitoring
    - Health status checking
    """

    def __init__(
        self,
        config: MermaidConfig | None = None,
        theme: str | MermaidTheme | None = None,
        preferred_renderer: str | None = None,
        fallback_enabled: bool = True,
        renderer_config: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize the plugin-based renderer.

        Args:
            config: Optional configuration object
            theme: Optional theme name or MermaidTheme object
            preferred_renderer: Preferred renderer name
            fallback_enabled: Whether to enable fallback rendering
            renderer_config: Renderer-specific configuration
        """
        self.config = config or MermaidConfig()
        self._theme: MermaidTheme | None = None
        self.preferred_renderer = preferred_renderer
        self.fallback_enabled = fallback_enabled
        self.renderer_config = renderer_config or {}

        # Initialize renderer manager
        self.renderer_manager = RendererManager(
            default_fallback_enabled=fallback_enabled,
            max_fallback_attempts=self.config.get("max_fallback_attempts", 3),
            fallback_timeout=self.config.get("fallback_timeout", 30.0),
        )

        # Set up logging
        self.logger = logging.getLogger(__name__)

        # Set theme if provided
        if theme:
            self.set_theme(theme)

    @property
    def SUPPORTED_FORMATS(self) -> list[str]:
        """Get list of supported formats from available renderers."""
        return list(self.renderer_manager.get_available_formats())

    def set_theme(self, theme: str | MermaidTheme) -> None:
        """
        Set the rendering theme.

        Args:
            theme: Theme name or MermaidTheme object
        """
        if isinstance(theme, str):
            self._theme = MermaidTheme(theme)
        elif isinstance(theme, MermaidTheme):
            self._theme = theme
        else:
            raise ConfigurationError(f"Invalid theme type: {type(theme)}")

    def get_theme(self) -> MermaidTheme | None:
        """Get current theme."""
        return self._theme

    def render(
        self,
        diagram: MermaidDiagram | str,
        format: str = "svg",
        renderer: str | None = None,
        fallback: bool | None = None,
        **options: Any,
    ) -> str | bytes:
        """
        Render a diagram using the plugin-based system.

        Args:
            diagram: MermaidDiagram object or raw Mermaid syntax
            format: Output format
            renderer: Specific renderer to use (overrides preferred)
            fallback: Whether to enable fallback (overrides default)
            **options: Additional rendering options

        Returns:
            Rendered diagram content
        """
        # Get Mermaid code
        if isinstance(diagram, MermaidDiagram):
            mermaid_code = diagram.to_mermaid()

            # Validate if enabled
            if self.config.get("validate_syntax", True):
                if not diagram.validate():
                    raise RenderingError("Invalid diagram syntax")
        else:
            mermaid_code = diagram

            # Skip strict validation for now to avoid compatibility issues
            # The renderer-level validation will handle basic checks
            pass

        # Prepare theme
        theme_name = None
        if self._theme:
            theme_name = self._theme.name if self._theme.name != "custom" else None
            # For custom themes, pass the config directly
            if self._theme.name == "custom":
                options.update(self._theme.to_dict())

        # Determine renderer to use
        target_renderer = renderer or self.preferred_renderer

        # Determine fallback setting
        use_fallback = fallback if fallback is not None else self.fallback_enabled

        # Render using the manager
        result = self.renderer_manager.render(
            mermaid_code=mermaid_code,
            format=format,
            theme=theme_name,
            config=self.renderer_config,
            preferred_renderer=target_renderer,
            fallback_enabled=use_fallback,
            **options,
        )

        if not result.success:
            raise RenderingError(result.error or "Rendering failed")

        return result.content

    def save(
        self,
        diagram: MermaidDiagram | str,
        output_path: str | Path,
        format: str | None = None,
        renderer: str | None = None,
        **options: Any,
    ) -> dict[str, Any]:
        """
        Render and save diagram to file.

        Args:
            diagram: Diagram to render
            output_path: Output file path
            format: Output format (inferred from extension if not provided)
            renderer: Specific renderer to use
            **options: Additional rendering options

        Returns:
            Dictionary with save operation metadata
        """
        output_path = Path(output_path)

        # Infer format from extension if not provided
        if format is None:
            format = output_path.suffix.lstrip(".").lower()
            if not format:
                format = self.config.get("default_format", "svg")

        # Ensure format is not None for type safety
        if format is None:
            format = "svg"

        # Render the diagram
        start_time = time.time()
        content = self.render(diagram, format, renderer, **options)

        # Create output directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write to file
        mode = "w" if format == "svg" else "wb"
        with open(output_path, mode) as f:
            if format == "svg":
                f.write(content)
            else:
                if isinstance(content, str):
                    f.write(content.encode())
                else:
                    f.write(content)

        save_time = time.time() - start_time

        return {
            "output_path": str(output_path),
            "format": format,
            "size_bytes": output_path.stat().st_size,
            "save_time": save_time,
            "renderer_used": renderer or self.preferred_renderer or "auto",
        }

    def get_available_renderers(
        self,
        format: str | None = None,
        capabilities: set[RendererCapability] | None = None,
    ) -> list[str]:
        """
        Get list of available renderers.

        Args:
            format: Filter by format support
            capabilities: Filter by required capabilities

        Returns:
            List of available renderer names
        """
        registry = get_global_registry()
        return registry.list_renderers(
            format_filter=format,
            capability_filter=capabilities,
            available_only=True,
        )

    def get_renderer_status(self) -> dict[str, Any]:
        """
        Get status of all renderers.

        Returns:
            Dictionary with renderer status information
        """
        registry = get_global_registry()
        status: dict[str, Any] = {}
        for name in registry.list_renderers():
            info = registry.get_renderer_info(name)
            if info:
                status[name] = {
                    "available": True,  # If it's in the registry, it's available
                    "formats": list(info.supported_formats),
                    "priority": (
                        info.priority.value
                        if hasattr(info.priority, "value")
                        else info.priority
                    ),
                }
        return status

    def get_performance_stats(self) -> dict[str, Any]:
        """
        Get performance statistics.

        Returns:
            Dictionary with performance statistics
        """
        # Return basic stats since RendererManager doesn't track performance
        return {
            "active_renderers": len(self.renderer_manager._active_renderers),
            "available_formats": list(self.renderer_manager.get_available_formats()),
        }

    def test_renderer(self, renderer_name: str) -> dict[str, Any]:
        """
        Test a specific renderer with a simple diagram.

        Args:
            renderer_name: Name of renderer to test

        Returns:
            Test results dictionary
        """
        test_diagram = "graph TD\n    A --> B"

        try:
            result = self.renderer_manager.render(
                mermaid_code=test_diagram,
                format="svg",
                preferred_renderer=renderer_name,
                fallback_enabled=False,
            )

            return {
                "renderer": renderer_name,
                "success": result.success,
                "render_time": result.render_time,
                "content_size": len(result.content),
                "error": result.error,
            }

        except Exception as e:
            return {
                "renderer": renderer_name,
                "success": False,
                "render_time": 0.0,
                "content_size": 0,
                "error": str(e),
            }

    def benchmark_renderers(
        self,
        test_diagrams: list[str] | None = None,
        formats: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Benchmark all available renderers.

        Args:
            test_diagrams: List of test diagrams (uses defaults if not provided)
            formats: List of formats to test (uses common formats if not provided)

        Returns:
            Benchmark results dictionary
        """
        if test_diagrams is None:
            test_diagrams = [
                "graph TD\n    A --> B",
                "sequenceDiagram\n    A->>B: Hello",
                "classDiagram\n    class A\n    A : +method()",
            ]

        if formats is None:
            formats = ["svg", "png"]

        results = {}

        for renderer_name in self.get_available_renderers():
            renderer_results = []

            for diagram in test_diagrams:
                for fmt in formats:
                    try:
                        result = self.renderer_manager.render(
                            mermaid_code=diagram,
                            format=fmt,
                            preferred_renderer=renderer_name,
                            fallback_enabled=False,
                        )

                        renderer_results.append(
                            {
                                "diagram_type": diagram.split("\n")[0],
                                "format": fmt,
                                "success": result.success,
                                "render_time": result.render_time,
                                "content_size": len(result.content),
                            }
                        )

                    except Exception as e:
                        renderer_results.append(
                            {
                                "diagram_type": diagram.split("\n")[0],
                                "format": fmt,
                                "success": False,
                                "render_time": 0.0,
                                "content_size": 0,
                                "error": str(e),
                            }
                        )

            results[renderer_name] = renderer_results

        return results

    def cleanup(self) -> None:
        """Clean up renderer resources."""
        self.renderer_manager.cleanup()

    def __enter__(self) -> "PluginMermaidRenderer":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.cleanup()
