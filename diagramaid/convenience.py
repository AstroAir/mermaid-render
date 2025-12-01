"""
Convenience functions for the Mermaid Render library.

This module provides high-level convenience functions that wrap the core
functionality for common use cases. These functions are designed to be
simple to use and require minimal configuration.
"""

from pathlib import Path
from typing import Any

from .core import MermaidConfig, MermaidRenderer


def quick_render(
    diagram_code: str,
    output_path: str | Path | None = None,
    format: str = "svg",
    theme: str | None = None,
    config: dict[str, Any] | None = None,
    use_plugin_system: bool = True,
) -> str | bytes:
    """
    Quick utility function to render Mermaid diagram code.

    This is a convenience function that provides a simple interface for rendering
    Mermaid diagrams without needing to create renderer instances. It handles
    validation, rendering, and optional file output in a single call.

    Args:
        diagram_code (str): Raw Mermaid diagram syntax. Must be valid Mermaid code
            following the official Mermaid syntax specification.
        output_path (Optional[Union[str, Path]], optional): Path to save the rendered
            diagram. If provided, the diagram will be saved to this file. The file
            extension is ignored - format is determined by the format parameter.
            Defaults to None (no file output).
        format (str, optional): Output format for the rendered diagram. Supported
            formats are:
            - "svg": Scalable Vector Graphics (default, best for web)
            - "png": Portable Network Graphics (good for documents)
            - "pdf": Portable Document Format (best for printing)
            Defaults to "svg".
        theme (Optional[str], optional): Theme name to apply to the diagram.
            Available built-in themes include:
            - "default": Standard Mermaid theme
            - "dark": Dark theme with light text
            - "forest": Green-based theme
            - "neutral": Neutral colors
            - "base": Minimal styling
            Defaults to None (uses default theme).
        config (Optional[Dict[str, Any]], optional): Additional configuration options
            to pass to the renderer. Can include timeout, validation settings, etc.
            Defaults to None.

    Returns:
        Union[str, bytes]: Rendered diagram content. Returns str for SVG format,
        bytes for PNG and PDF formats.

    Raises:
        ValidationError: If the diagram code contains syntax errors or is invalid
            according to Mermaid specifications.
        RenderingError: If the rendering process fails due to network issues,
            server errors, or other rendering problems.
        UnsupportedFormatError: If the specified format is not supported by the
            current installation or configuration.
        FileNotFoundError: If output_path directory doesn't exist.
        PermissionError: If unable to write to the specified output_path.

    Examples:
        Basic SVG rendering:
        >>> svg_content = quick_render('''
        ... flowchart TD
        ...     A[Start] --> B[Process]
        ...     B --> C[End]
        ... ''')
        >>> print(type(svg_content))
        <class 'str'>

        Render with theme and save to file:
        >>> quick_render('''
        ... sequenceDiagram
        ...     Alice->>Bob: Hello Bob!
        ...     Bob-->>Alice: Hello Alice!
        ... ''', output_path="sequence.png", format="png", theme="dark")

        Render with custom configuration:
        >>> config = {"timeout": 60, "validate_syntax": True}
        >>> pdf_content = quick_render('''
        ... classDiagram
        ...     Animal <|-- Duck
        ...     Animal <|-- Fish
        ... ''', format="pdf", config=config)

        Error handling:
        >>> try:
        ...     result = quick_render("invalid mermaid syntax")
        ... except ValidationError as e:
        ...     print(f"Invalid diagram: {e}")
    """
    from .exceptions import ValidationError
    from .validators import MermaidValidator

    # Validate the diagram code
    validator = MermaidValidator()
    validation_result = validator.validate(diagram_code)
    if not validation_result.is_valid:
        raise ValidationError(f"Invalid diagram code: {validation_result.errors}")

    # Create renderer with optional theme and config
    renderer_config = MermaidConfig()
    if config:
        renderer_config.update(config)

    renderer = MermaidRenderer(config=renderer_config, use_plugin_system=use_plugin_system)

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
    output_path: str | Path,
    format: str | None = None,
    theme: str | None = None,
    config: dict[str, Any] | None = None,
    use_plugin_system: bool = True,
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
            path_obj = Path(output_path)
            format = path_obj.suffix.lstrip(".").lower()
            if format not in ["svg", "png", "pdf"]:
                format = "svg"

        quick_render(
            diagram_code=diagram_code,
            format=format,
            theme=theme,
            config=config,
            output_path=output_path,
            use_plugin_system=use_plugin_system,
        )
        return True
    except Exception:
        return False


# Backward compatibility alias
render = quick_render
