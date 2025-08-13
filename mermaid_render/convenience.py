"""
Convenience functions for the Mermaid Render library.

This module provides high-level convenience functions that wrap the core
functionality for common use cases. These functions are designed to be
simple to use and require minimal configuration.
"""

from pathlib import Path
from typing import Any, Dict, Optional, Union

from .core import MermaidConfig, MermaidRenderer


def quick_render(
    diagram_code: str,
    format: str = "svg",
    theme: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None,
    output_path: Optional[Union[str, Path]] = None,
) -> str:
    """
    Quick rendering function for simple use cases.

    This function provides a simple interface for rendering Mermaid diagrams
    without needing to create renderer instances or manage configuration.

    Args:
        diagram_code: Raw Mermaid diagram syntax
        format: Output format ("svg", "png", "pdf")
        theme: Theme name to apply
        config: Optional configuration overrides
        output_path: Optional path to save the rendered diagram

    Returns:
        Rendered diagram content as string

    Example:
        >>> # Simple rendering
        >>> svg_content = quick_render('''
        ... flowchart TD
        ...     A[Start] --> B[Process]
        ...     B --> C[End]
        ... ''')
        >>>
        >>> # With custom theme and format
        >>> png_content = quick_render(
        ...     diagram_code,
        ...     format="png",
        ...     theme="dark"
        ... )
        >>>
        >>> # Save to file
        >>> quick_render(
        ...     diagram_code,
        ...     format="svg",
        ...     output_path="my_diagram.svg"
        ... )
    """
    # Create renderer with configuration
    renderer_config = MermaidConfig()
    if config:
        renderer_config.update(config)

    renderer = MermaidRenderer(config=renderer_config)

    if theme:
        renderer.set_theme(theme)

    # Render the diagram
    content = renderer.render_raw(diagram_code, format=format)

    # Save to file if path provided
    if output_path:
        with open(output_path, "w" if format == "svg" else "wb") as f:
            if format == "svg":
                f.write(content)
            else:
                f.write(content.encode() if isinstance(content, str) else content)

    return content


def render_to_file(
    diagram_code: str,
    output_path: Union[str, Path],
    format: Optional[str] = None,
    theme: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None,
) -> bool:
    """
    Render diagram directly to file.

    Args:
        diagram_code: Raw Mermaid diagram syntax
        output_path: Path to save the rendered diagram
        format: Output format (auto-detected from file extension if not provided)
        theme: Theme name to apply
        config: Optional configuration overrides

    Returns:
        True if successful, False otherwise

    Example:
        >>> # Auto-detect format from extension
        >>> render_to_file(diagram_code, "output.png")
        >>>
        >>> # Explicit format
        >>> render_to_file(diagram_code, "output.svg", format="svg", theme="dark")
    """
    try:
        # Auto-detect format from file extension if not provided
        if format is None:
            output_path = Path(output_path)
            format = output_path.suffix.lstrip('.').lower()
            if format not in ["svg", "png", "pdf"]:
                format = "svg"

        quick_render(
            diagram_code=diagram_code,
            format=format,
            theme=theme,
            config=config,
            output_path=output_path,
        )
        return True
    except Exception:
        return False


# Backward compatibility alias
render = quick_render
