"""
Export utilities for the Mermaid Render library.

This module provides convenient functions for exporting diagrams to various formats.
"""

from pathlib import Path
from typing import Any

from ..core import MermaidDiagram, MermaidRenderer
from ..exceptions import UnsupportedFormatError


def export_to_file(
    diagram: MermaidDiagram | str,
    output_path: str | Path,
    format: str | None = None,
    theme: str | None = None,
    config: dict[str, Any] | None = None,
    renderer: MermaidRenderer | None = None,
    **options: Any,
) -> None:
    """
    Export a Mermaid diagram to file.

    This is a convenience function that handles the complete export process
    including format detection, rendering, and file writing.

    Args:
        diagram: MermaidDiagram object or raw Mermaid syntax
        output_path: Output file path
        format: Output format (auto-detected from extension if not provided)
        theme: Optional theme name
        config: Optional configuration dictionary
        renderer: Optional custom renderer instance
        **options: Additional rendering options

    Raises:
        UnsupportedFormatError: If format is not supported
        RenderingError: If rendering fails

    Example:
        >>> from mermaid_render import FlowchartDiagram, export_to_file
        >>>
        >>> # Create a diagram
        >>> flowchart = FlowchartDiagram()
        >>> flowchart.add_node("A", "Start")
        >>> flowchart.add_node("B", "End")
        >>> flowchart.add_edge("A", "B")
        >>>
        >>> # Export to various formats
        >>> export_to_file(flowchart, "diagram.svg")
        >>> export_to_file(flowchart, "diagram.png", theme="dark")
        >>> export_to_file(flowchart, "diagram.pdf", config={"width": 1200})
    """
    output_path = Path(output_path)

    # Auto-detect format from file extension if not provided
    if format is None:
        format = _detect_format_from_extension(output_path)

    # Create renderer if not provided
    if renderer is None:
        from ..core import MermaidConfig

        renderer_config = MermaidConfig()
        if config:
            renderer_config.update(config)
        renderer = MermaidRenderer(config=renderer_config)

    # Set theme if provided
    if theme:
        renderer.set_theme(theme)

    # Render and save
    renderer.save(diagram, output_path, format, **options)


def export_multiple_formats(
    diagram: MermaidDiagram | str,
    base_path: str | Path,
    formats: list[str],
    theme: str | None = None,
    config: dict[str, Any] | None = None,
    **options: Any,
) -> dict[str, Path]:
    """
    Export a diagram to multiple formats simultaneously.

    This function is useful when you need the same diagram in multiple formats
    for different use cases (e.g., SVG for web, PNG for presentations, PDF for print).
    It efficiently renders the diagram once and converts to all requested formats.

    Args:
        diagram: MermaidDiagram object or raw Mermaid syntax string to export
        base_path: Base path for output files (without extension). The format
            extension will be automatically appended for each output file
        formats: List of formats to export to. Must be supported formats
            (svg, png, pdf). Example: ["svg", "png", "pdf"]
        theme: Optional theme name to apply to all exports. Available themes:
            "default", "dark", "forest", "neutral", "base"
        config: Optional configuration dictionary with rendering settings
        **options: Additional rendering options passed to the renderer

    Returns:
        Dictionary mapping format names to their corresponding output file paths.
        Useful for tracking which files were created.

    Raises:
        UnsupportedFormatError: If any of the requested formats is not supported
        RenderingError: If rendering fails for any format

    Example:
        >>> from mermaid_render import FlowchartDiagram, export_multiple_formats
        >>>
        >>> # Create a diagram
        >>> diagram = FlowchartDiagram()
        >>> diagram.add_node("A", "Start")
        >>> diagram.add_node("B", "End")
        >>> diagram.add_edge("A", "B")
        >>>
        >>> # Export to multiple formats
        >>> output_files = export_multiple_formats(
        ...     diagram,
        ...     "my_diagram",  # Will create my_diagram.svg, my_diagram.png, etc.
        ...     ["svg", "png", "pdf"],
        ...     theme="dark"
        ... )
        >>>
        >>> # Check what files were created
        >>> for format, path in output_files.items():
        ...     print(f"{format}: {path}")
        svg: my_diagram.svg
        png: my_diagram.png
        pdf: my_diagram.pdf

        >>> paths = export_multiple_formats(
        ...     diagram,
        ...     "my_diagram",
        ...     ["svg", "png", "pdf"]
        ... )
        >>> # Returns: {"svg": Path("my_diagram.svg"), ...}
    """
    base_path = Path(base_path)
    output_paths = {}

    # Create renderer
    from ..core import MermaidConfig, MermaidRenderer

    renderer_config = MermaidConfig()
    if config:
        renderer_config.update(config)
    renderer = MermaidRenderer(config=renderer_config)

    if theme:
        renderer.set_theme(theme)

    # Export to each format
    for fmt in formats:
        output_path = base_path.with_suffix(f".{fmt}")
        renderer.save(diagram, output_path, fmt, **options)
        output_paths[fmt] = output_path

    return output_paths


def batch_export(
    diagrams: dict[str, MermaidDiagram | str],
    output_dir: str | Path,
    format: str = "svg",
    theme: str | None = None,
    config: dict[str, Any] | None = None,
    **options: Any,
) -> dict[str, Path]:
    """
    Export multiple diagrams to files in batch.

    This function is useful for processing multiple diagrams at once, such as
    generating documentation with multiple diagram types or creating a gallery
    of diagrams. All diagrams will be exported to the same format and directory.

    Args:
        diagrams: Dictionary mapping diagram names to diagram objects or raw
            Mermaid syntax strings. The keys will be used as filenames
        output_dir: Output directory where all diagrams will be saved. Will be
            created if it does not exist
        format: Output format for all diagrams. Must be a supported format
            (svg, png, pdf). Default is "svg"
        theme: Optional theme name to apply to all diagrams. Available themes:
            "default", "dark", "forest", "neutral", "base"
        config: Optional configuration dictionary with rendering settings
        **options: Additional rendering options passed to the renderer

    Returns:
        Dictionary mapping original diagram names to their output file paths.
        Useful for tracking which files were created and their locations.

    Raises:
        UnsupportedFormatError: If the specified format is not supported
        RenderingError: If rendering fails for any diagram

    Example:
        >>> from mermaid_render import FlowchartDiagram, SequenceDiagram, batch_export
        >>>
        >>> # Create multiple diagrams
        >>> flowchart = FlowchartDiagram()
        >>> flowchart.add_node("A", "Start")
        >>>
        >>> sequence = SequenceDiagram()
        >>> sequence.add_participant("user", "User")
        >>>
        >>> # Batch export
        >>> diagrams = {
        ...     "user_flow": flowchart,
        ...     "api_sequence": sequence,
        ...     "raw_diagram": "graph TD; A-->B"
        ... }
        >>>
        >>> output_paths = batch_export(
        ...     diagrams,
        ...     "documentation/diagrams/",
        ...     format="png",
        ...     theme="forest"
        ... )
        >>>
        >>> # Check results
        >>> for name, path in output_paths.items():
        ...     print(f"{name} -> {path}")
        user_flow -> documentation/diagrams/user_flow.png
        api_sequence -> documentation/diagrams/api_sequence.png
        raw_diagram -> documentation/diagrams/raw_diagram.png
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_paths = {}

    # Create renderer
    from ..core import MermaidConfig, MermaidRenderer

    renderer_config = MermaidConfig()
    if config:
        renderer_config.update(config)
    renderer = MermaidRenderer(config=renderer_config)

    if theme:
        renderer.set_theme(theme)

    # Export each diagram
    for name, diagram in diagrams.items():
        # Sanitize filename
        safe_name = _sanitize_filename(name)
        output_path = output_dir / f"{safe_name}.{format}"

        renderer.save(diagram, output_path, format, **options)
        output_paths[name] = output_path

    return output_paths


def _detect_format_from_extension(file_path: Path) -> str:
    """
    Detect output format from file extension.

    Args:
        file_path: File path to analyze

    Returns:
        Detected format

    Raises:
        UnsupportedFormatError: If extension is not recognized
    """
    extension = file_path.suffix.lower().lstrip(".")

    if not extension:
        raise UnsupportedFormatError(
            "No file extension provided and format not specified"
        )

    # Map extensions to formats
    extension_map = {
        "svg": "svg",
        "png": "png",
        "pdf": "pdf",
        "jpg": "png",  # Treat as PNG for now
        "jpeg": "png",
    }

    if extension not in extension_map:
        supported = list(extension_map.keys())
        raise UnsupportedFormatError(
            f"Unsupported file extension: .{extension}",
            requested_format=extension,
            supported_formats=supported,
        )

    return extension_map[extension]


def _sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file system usage.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    import re

    # Replace invalid characters with underscores
    sanitized = re.sub(r'[<>:"/\\|?*]', "_", filename)

    # Remove leading/trailing whitespace and dots
    sanitized = sanitized.strip(" .")

    # Ensure it's not empty
    if not sanitized:
        sanitized = "diagram"

    return sanitized
