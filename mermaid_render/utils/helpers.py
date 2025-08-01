"""
Helper utilities for the Mermaid Render library.

This module provides various helper functions for common operations including
format detection, theme management, diagram analysis, and validation utilities.
These functions are designed to simplify common tasks and provide convenient
shortcuts for frequently used operations.

The helpers are organized into several categories:
- Format and theme utilities
- Diagram analysis and statistics
- Validation helpers
- File and path utilities
- Content detection and parsing

All functions are designed to be standalone and can be used independently
without requiring complex setup or configuration.
"""

import re
from pathlib import Path
from typing import List, Optional


def get_supported_formats() -> List[str]:
    """
    Get list of supported output formats.

    Returns a list of formats that the renderer can output to. This is useful
    for validation, UI generation, or informational purposes.

    Returns:
        List of supported format names (e.g., ["svg", "png", "pdf"])

    Example:
        >>> formats = get_supported_formats()
        >>> print(f"Supported formats: {', '.join(formats)}")
        Supported formats: svg, png, pdf

        >>> # Check if a format is supported
        >>> if "svg" in get_supported_formats():
        ...     print("SVG export is available")

        >>> # Generate format options for UI
        >>> format_options = [{"value": fmt, "label": fmt.upper()}
        ...                  for fmt in get_supported_formats()]
    """
    return ["svg", "png", "pdf"]


def get_available_themes() -> List[str]:
    """
    Get list of available themes.

    Returns:
        List of available theme names

    Example:
        >>> themes = get_available_themes()
        >>> print(f"Available themes: {', '.join(themes)}")
    """
    from ..config import ThemeManager

    theme_manager = ThemeManager()
    return theme_manager.get_available_themes()


def detect_diagram_type(mermaid_code: str) -> Optional[str]:
    """
    Detect the type of Mermaid diagram from code.

    Args:
        mermaid_code: Raw Mermaid diagram syntax

    Returns:
        Detected diagram type or None if unknown

    Example:
        >>> diagram_type = detect_diagram_type('''
        ... flowchart TD
        ...     A --> B
        ... ''')
        >>> print(f"Diagram type: {diagram_type}")  # "flowchart"
    """
    if not mermaid_code or not mermaid_code.strip():
        return None

    first_line = mermaid_code.strip().split("\n")[0].strip()

    # Diagram type patterns
    patterns = {
        "flowchart": r"^flowchart\s+(TD|TB|BT|RL|LR)",
        "sequenceDiagram": r"^sequenceDiagram",
        "classDiagram": r"^classDiagram",
        "stateDiagram": r"^stateDiagram(-v2)?",
        "erDiagram": r"^erDiagram",
        "journey": r"^journey",
        "gantt": r"^gantt",
        "pie": r"^pie",
        "gitgraph": r"^gitgraph",
        "mindmap": r"^mindmap",
    }

    for diagram_type, pattern in patterns.items():
        if re.match(pattern, first_line):
            return diagram_type

    return None


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file system usage.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename safe for file systems

    Example:
        >>> safe_name = sanitize_filename("My Diagram: Version 2.0")
        >>> print(safe_name)  # "My_Diagram_Version_2_0"
    """
    # Replace invalid characters with underscores
    sanitized = re.sub(r'[<>:"/\\|?*]', "_", filename)

    # Replace spaces with underscores
    sanitized = re.sub(r"\s+", "_", sanitized)

    # Remove leading/trailing underscores and dots
    sanitized = sanitized.strip("_.")

    # Ensure it's not empty
    if not sanitized:
        sanitized = "diagram"

    # Limit length
    if len(sanitized) > 100:
        sanitized = sanitized[:100]

    return sanitized


def ensure_directory(path: Path) -> Path:
    """
    Ensure directory exists, creating it if necessary.

    Args:
        path: Directory path

    Returns:
        The directory path

    Example:
        >>> output_dir = ensure_directory(Path("output/diagrams"))
        >>> # Directory is now guaranteed to exist
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string

    Example:
        >>> size_str = format_file_size(1024 * 1024)
        >>> print(size_str)  # "1.0 MB"
    """
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)

    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1

    return f"{size:.1f} {size_names[i]}"


def get_file_info(file_path: Path) -> dict:
    """
    Get information about a file.

    Args:
        file_path: Path to file

    Returns:
        Dictionary with file information

    Example:
        >>> info = get_file_info(Path("diagram.svg"))
        >>> print(f"Size: {info['size_formatted']}")
    """
    if not file_path.exists():
        return {"exists": False}

    stat = file_path.stat()

    return {
        "exists": True,
        "size_bytes": stat.st_size,
        "size_formatted": format_file_size(stat.st_size),
        "modified": stat.st_mtime,
        "is_file": file_path.is_file(),
        "is_dir": file_path.is_dir(),
        "extension": file_path.suffix.lower(),
        "name": file_path.name,
        "stem": file_path.stem,
    }


def validate_format(format: str) -> bool:
    """
    Validate if a format is supported.

    Args:
        format: Format name to validate

    Returns:
        True if format is supported

    Example:
        >>> if validate_format("svg"):
        ...     print("SVG is supported")
    """
    return format.lower() in get_supported_formats()


def validate_theme(theme: str) -> bool:
    """
    Validate if a theme is available.

    Args:
        theme: Theme name to validate

    Returns:
        True if theme is available

    Example:
        >>> if validate_theme("dark"):
        ...     renderer.set_theme("dark")
    """
    return theme in get_available_themes()


def get_diagram_stats(mermaid_code: str) -> dict:
    """
    Get statistics about a Mermaid diagram.

    Args:
        mermaid_code: Raw Mermaid diagram syntax

    Returns:
        Dictionary with diagram statistics

    Example:
        >>> stats = get_diagram_stats(my_diagram_code)
        >>> print(f"Lines: {stats['line_count']}")
    """
    lines = mermaid_code.strip().split("\n")
    non_empty_lines = [line for line in lines if line.strip()]

    return {
        "line_count": len(lines),
        "non_empty_lines": len(non_empty_lines),
        "character_count": len(mermaid_code),
        "diagram_type": detect_diagram_type(mermaid_code),
        "has_title": "title" in mermaid_code.lower(),
        "estimated_complexity": _estimate_complexity(mermaid_code),
    }


def _estimate_complexity(mermaid_code: str) -> str:
    """
    Estimate diagram complexity based on content.

    Args:
        mermaid_code: Raw Mermaid diagram syntax

    Returns:
        Complexity level (low, medium, high)
    """
    lines = len([line for line in mermaid_code.split("\n") if line.strip()])

    # Count connections/relationships
    connection_patterns = [
        "-->",
        "---",
        "-.-",
        "-.->",
        "==>",
        "===",
        "->",
        "->>",
        "-->>",
    ]
    connections = sum(mermaid_code.count(pattern) for pattern in connection_patterns)

    # Simple heuristic
    if lines <= 10 and connections <= 5:
        return "low"
    elif lines <= 25 and connections <= 15:
        return "medium"
    else:
        return "high"
