"""
Core MCP tools for mermaid-render.

This module provides core rendering and validation tools.
"""

import base64
import logging
from typing import Any

from ...core import MermaidConfig, MermaidRenderer
from ...exceptions import ValidationError
from ...validators import MermaidValidator
from .base import (
    ErrorCategory,
    create_error_response,
    create_success_response,
    measure_performance,
)
from .helpers import (
    _calculate_complexity_score,
    _calculate_quality_score,
    _detect_diagram_type,
)
from .params import RenderDiagramParams, ValidateDiagramParams

logger = logging.getLogger(__name__)


@measure_performance
def render_diagram(
    diagram_code: str,
    output_format: str = "svg",
    theme: str | None = None,
    width: int | None = None,
    height: int | None = None,
    background_color: str | None = None,
    scale: float | None = None,
) -> dict[str, Any]:
    """
    Render a Mermaid diagram to the specified format.

    This tool provides comprehensive diagram rendering with support for multiple
    output formats, themes, and customization options. It includes automatic
    validation, error handling, and detailed metadata in responses.

    Args:
        diagram_code: Mermaid diagram code to render
        output_format: Output format (svg, png, pdf)
        theme: Theme name (default, dark, forest, neutral, base)
        width: Output width in pixels (100-4096)
        height: Output height in pixels (100-4096)
        background_color: Background color (hex format or named color)
        scale: Scale factor for output (0.1-10.0)

    Returns:
        Dictionary containing rendered diagram data and comprehensive metadata

    Example:
        >>> result = render_diagram(
        ...     "flowchart TD\\n    A[Start] --> B[End]",
        ...     output_format="svg",
        ...     theme="dark"
        ... )
        >>> print(result["success"])  # True
        >>> print(result["data"])     # SVG content
    """
    try:
        # Validate parameters with enhanced validation
        params = RenderDiagramParams(
            diagram_code=diagram_code,
            output_format=output_format,
            theme=theme,
            width=width,
            height=height,
            background_color=background_color,
            scale=scale,
        )

        # Create configuration
        config = MermaidConfig()

        # Prepare rendering options
        options: dict[str, Any] = {}
        if params.width:
            options["width"] = params.width
        if params.height:
            options["height"] = params.height
        if params.background_color:
            options["background_color"] = params.background_color
        if params.scale:
            options["scale"] = params.scale

        # Create renderer with theme
        renderer = MermaidRenderer(config=config, theme=params.theme)

        # Render diagram
        result = renderer.render_raw(
            params.diagram_code, params.output_format.value, **options
        )

        # Convert result to string if it's bytes (for consistent handling)
        if isinstance(result, bytes):
            # For binary formats, we'll encode as base64 for JSON serialization
            data = base64.b64encode(result).decode("utf-8")
            is_binary = True
        else:
            data = result
            is_binary = False

        # Enhanced metadata
        metadata = {
            "theme": params.theme.value if params.theme else "default",
            "width": params.width,
            "height": params.height,
            "background_color": params.background_color,
            "scale": params.scale,
            "size_bytes": len(result) if isinstance(result, (str, bytes)) else 0,
            "diagram_type": _detect_diagram_type(params.diagram_code),
            "line_count": len(params.diagram_code.splitlines()),
            "character_count": len(params.diagram_code),
            "encoding": "base64" if is_binary else "utf-8",
        }

        return create_success_response(
            data={
                "format": params.output_format.value,
                "content": data,
                "is_binary": is_binary,
            },
            metadata=metadata,
        )

    except ValidationError as e:
        logger.error(f"Validation error in render_diagram: {e}")
        return create_error_response(
            e,
            ErrorCategory.VALIDATION,
            context={"diagram_code_length": len(diagram_code) if diagram_code else 0},
            suggestions=[
                "Check diagram syntax",
                "Verify parameter values are within valid ranges",
            ],
        )
    except Exception as e:
        logger.error(f"Error rendering diagram: {e}")
        return create_error_response(
            e,
            ErrorCategory.RENDERING,
            context={
                "output_format": output_format,
                "theme": theme,
                "diagram_type": (
                    _detect_diagram_type(diagram_code) if diagram_code else None
                ),
            },
        )


@measure_performance
def validate_diagram(diagram_code: str) -> dict[str, Any]:
    """
    Validate Mermaid diagram syntax and structure.

    This tool provides comprehensive validation of Mermaid diagram code,
    including syntax checking, structure analysis, and detailed error reporting
    with line-by-line feedback and improvement suggestions.

    Args:
        diagram_code: Mermaid diagram code to validate

    Returns:
        Dictionary containing detailed validation results and metadata

    Example:
        >>> result = validate_diagram("flowchart TD\\n    A[Start] --> B[End]")
        >>> print(result["data"]["valid"])  # True
        >>> print(result["data"]["diagram_type"])  # "flowchart"
    """
    try:
        # Validate parameters with enhanced validation
        params = ValidateDiagramParams(diagram_code=diagram_code)

        # Validate syntax using MermaidValidator
        validator = MermaidValidator()
        result = validator.validate(params.diagram_code)

        # Enhanced validation data
        validation_data = {
            "valid": result.is_valid,
            "errors": result.errors,
            "warnings": result.warnings,
            "line_errors": result.line_errors,
            "diagram_type": _detect_diagram_type(params.diagram_code),
            "complexity_score": _calculate_complexity_score(params.diagram_code),
            "quality_score": _calculate_quality_score(result, params.diagram_code),
        }

        # Enhanced metadata
        import datetime

        metadata = {
            "line_count": len(params.diagram_code.splitlines()),
            "character_count": len(params.diagram_code),
            "word_count": len(params.diagram_code.split()),
            "error_count": len(result.errors),
            "warning_count": len(result.warnings),
            "validation_timestamp": datetime.datetime.now().isoformat(),
        }

        # Add suggestions for improvement if there are issues
        suggestions = []
        if not result.is_valid:
            suggestions.extend(
                [
                    "Check syntax against Mermaid documentation",
                    "Verify diagram type declaration",
                    "Ensure proper node and edge syntax",
                ]
            )
        if result.warnings:
            suggestions.append("Review warnings for potential improvements")

        return create_success_response(data=validation_data, metadata=metadata)

    except ValidationError as e:
        logger.error(f"Validation error in validate_diagram: {e}")
        return create_error_response(
            e,
            ErrorCategory.VALIDATION,
            context={"diagram_code_length": len(diagram_code) if diagram_code else 0},
            suggestions=[
                "Ensure diagram code is not empty",
                "Check for valid UTF-8 encoding",
            ],
        )
    except Exception as e:
        logger.error(f"Error validating diagram: {e}")
        return create_error_response(
            e,
            ErrorCategory.SYSTEM,
            context={
                "diagram_type": (
                    _detect_diagram_type(diagram_code) if diagram_code else None
                )
            },
        )


@measure_performance
def list_themes() -> dict[str, Any]:
    """
    List all available Mermaid themes with detailed information.

    This tool provides comprehensive information about all available themes,
    including built-in themes and any custom themes that have been configured.
    Each theme includes description, color palette information, and usage examples.

    Returns:
        Dictionary containing detailed theme information and metadata

    Example:
        >>> result = list_themes()
        >>> print(result["data"]["themes"]["dark"]["description"])
        >>> print(result["data"]["default_theme"])  # "default"
    """
    try:
        # Enhanced theme information with more details
        themes = {
            "default": {
                "name": "Default",
                "description": "Default theme with light background and standard colors",
                "background": "light",
                "primary_color": "#0066cc",
                "suitable_for": ["presentations", "documentation", "general use"],
                "contrast": "high",
            },
            "dark": {
                "name": "Dark",
                "description": "Dark theme with dark background for low-light environments",
                "background": "dark",
                "primary_color": "#66b3ff",
                "suitable_for": ["night work", "dark interfaces", "reduced eye strain"],
                "contrast": "high",
            },
            "forest": {
                "name": "Forest",
                "description": "Forest theme with green color palette for nature-inspired designs",
                "background": "light",
                "primary_color": "#228B22",
                "suitable_for": [
                    "environmental topics",
                    "organic processes",
                    "natural systems",
                ],
                "contrast": "medium",
            },
            "base": {
                "name": "Base",
                "description": "Minimal base theme with clean, simple styling",
                "background": "light",
                "primary_color": "#333333",
                "suitable_for": [
                    "minimalist designs",
                    "technical documentation",
                    "clean layouts",
                ],
                "contrast": "medium",
            },
            "neutral": {
                "name": "Neutral",
                "description": "Neutral theme with gray color palette for professional appearance",
                "background": "light",
                "primary_color": "#666666",
                "suitable_for": [
                    "business documents",
                    "professional presentations",
                    "formal reports",
                ],
                "contrast": "medium",
            },
        }

        # Try to get custom themes from theme manager if available
        custom_themes = {}
        try:
            from ...config import ThemeManager

            theme_manager = ThemeManager()
            available_themes = theme_manager.get_available_themes()

            for theme_name in available_themes:
                if theme_name not in themes:  # Custom theme
                    try:
                        theme_config = theme_manager.get_theme(theme_name)
                        custom_themes[theme_name] = {
                            "name": theme_name.title(),
                            "description": f"Custom theme: {theme_name}",
                            "background": "unknown",
                            "primary_color": theme_config.get(
                                "primaryColor", "#000000"
                            ),
                            "suitable_for": ["custom use cases"],
                            "contrast": "unknown",
                            "custom": True,
                        }
                    except Exception:
                        pass  # Skip themes that can't be loaded
        except ImportError:
            pass  # Theme manager not available

        # Combine built-in and custom themes
        all_themes = {**themes, **custom_themes}

        # Enhanced metadata
        metadata = {
            "total_themes": len(all_themes),
            "builtin_themes": len(themes),
            "custom_themes": len(custom_themes),
            "default_theme": "default",
            "theme_categories": {
                "light_background": [
                    name
                    for name, info in all_themes.items()
                    if info.get("background") == "light"
                ],
                "dark_background": [
                    name
                    for name, info in all_themes.items()
                    if info.get("background") == "dark"
                ],
                "custom": [
                    name
                    for name, info in all_themes.items()
                    if info.get("custom", False)
                ],
            },
        }

        return create_success_response(
            data={
                "themes": all_themes,
                "default_theme": "default",
                "recommendations": {
                    "presentations": ["default", "neutral"],
                    "dark_mode": ["dark"],
                    "nature_topics": ["forest"],
                    "minimal_design": ["base"],
                    "professional": ["neutral", "base"],
                },
            },
            metadata=metadata,
        )

    except Exception as e:
        logger.error(f"Error listing themes: {e}")
        return create_error_response(
            e,
            ErrorCategory.CONFIGURATION,
            suggestions=[
                "Check theme configuration",
                "Verify theme manager is properly initialized",
            ],
        )
