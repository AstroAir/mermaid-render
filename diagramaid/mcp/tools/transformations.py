"""
Transformation MCP tools for diagramaid.

This module provides style and structure transformation tools.
"""

import logging
from typing import Any

from .base import (
    ErrorCategory,
    create_error_response,
    create_success_response,
    measure_performance,
)
from .helpers import (
    _add_comments,
    _change_diagram_direction,
    _detect_diagram_type,
    _extract_nodes,
    _wrap_in_subgraph,
)

logger = logging.getLogger(__name__)


@measure_performance
def transform_diagram_style(
    diagram_code: str,
    style_preset: str = "modern",
    color_scheme: str | None = None,
    node_style: str | None = None,
    edge_style: str | None = None,
) -> dict[str, Any]:
    """
    Transform diagram styling using presets or custom styles.

    This tool applies styling transformations to a Mermaid diagram,
    including color schemes, node shapes, and edge styles.

    Args:
        diagram_code: Mermaid diagram code to transform
        style_preset: Style preset (modern, classic, minimal, colorful)
        color_scheme: Custom color scheme (primary, secondary colors)
        node_style: Custom node styling
        edge_style: Custom edge styling

    Returns:
        Dictionary containing styled diagram code and metadata

    Example:
        >>> result = transform_diagram_style(
        ...     "flowchart TD\\n    A --> B",
        ...     style_preset="modern"
        ... )
        >>> print(result["data"]["styled_code"])
    """
    try:
        import datetime

        valid_presets = ["modern", "classic", "minimal", "colorful", "dark", "blueprint"]
        if style_preset not in valid_presets:
            return create_error_response(
                ValueError(f"Invalid style preset: {style_preset}"),
                ErrorCategory.VALIDATION,
                context={"valid_presets": valid_presets},
                suggestions=[f"Use one of: {', '.join(valid_presets)}"],
            )

        # Style definitions
        style_definitions = {
            "modern": {
                "node_fill": "#e1f5fe",
                "node_stroke": "#01579b",
                "edge_stroke": "#0288d1",
                "text_color": "#01579b",
            },
            "classic": {
                "node_fill": "#fff3e0",
                "node_stroke": "#e65100",
                "edge_stroke": "#ff6d00",
                "text_color": "#bf360c",
            },
            "minimal": {
                "node_fill": "#fafafa",
                "node_stroke": "#424242",
                "edge_stroke": "#757575",
                "text_color": "#212121",
            },
            "colorful": {
                "node_fill": "#e8f5e9",
                "node_stroke": "#2e7d32",
                "edge_stroke": "#43a047",
                "text_color": "#1b5e20",
            },
            "dark": {
                "node_fill": "#263238",
                "node_stroke": "#78909c",
                "edge_stroke": "#90a4ae",
                "text_color": "#eceff1",
            },
            "blueprint": {
                "node_fill": "#e3f2fd",
                "node_stroke": "#1565c0",
                "edge_stroke": "#1976d2",
                "text_color": "#0d47a1",
            },
        }

        preset_style = style_definitions.get(style_preset, style_definitions["modern"])

        # Apply custom overrides
        if color_scheme:
            # Parse color scheme if provided (format: "primary:#color,secondary:#color")
            try:
                color_parts = color_scheme.split(",")
                for part in color_parts:
                    if ":" in part:
                        key, value = part.strip().split(":", 1)
                        key = key.strip().lower()
                        value = value.strip()
                        if key == "primary" or key == "node_fill":
                            preset_style["node_fill"] = value
                        elif key == "secondary" or key == "node_stroke":
                            preset_style["node_stroke"] = value
                        elif key == "text" or key == "text_color":
                            preset_style["text_color"] = value
                        elif key == "edge" or key == "edge_stroke":
                            preset_style["edge_stroke"] = value
            except Exception as parse_error:
                logger.warning(f"Could not parse color scheme: {parse_error}")

        # Extract nodes to apply styles
        nodes = _extract_nodes(diagram_code)

        # Build styled diagram
        styled_code = diagram_code

        # Add style definitions at the end
        style_lines = []
        for node in nodes:
            node_id = node.get("id", "")
            if node_id:
                style_lines.append(
                    f"    style {node_id} fill:{preset_style['node_fill']},stroke:{preset_style['node_stroke']},color:{preset_style['text_color']}"
                )

        if style_lines:
            styled_code = styled_code.rstrip() + "\n" + "\n".join(style_lines)

        # Enhanced metadata
        metadata = {
            "transform_timestamp": datetime.datetime.now().isoformat(),
            "style_preset": style_preset,
            "styles_applied": len(style_lines),
            "diagram_type": _detect_diagram_type(diagram_code),
        }

        return create_success_response(
            data={
                "styled_code": styled_code,
                "original_code": diagram_code,
                "style_preset": style_preset,
                "styles_applied": style_lines,
            },
            metadata=metadata,
        )

    except Exception as e:
        logger.error(f"Error transforming diagram style: {e}")
        return create_error_response(
            e,
            ErrorCategory.SYSTEM,
            suggestions=[
                "Check diagram syntax",
                "Verify style preset is valid",
            ],
        )


@measure_performance
def generate_diagram_variants(
    diagram_code: str,
    variant_count: int = 3,
    variation_type: str = "layout",
) -> dict[str, Any]:
    """
    Generate multiple variants of a diagram with different layouts or styles.

    This tool creates variations of a diagram by changing its layout direction,
    styling, or structure while preserving the core content.

    Args:
        diagram_code: Mermaid diagram code to vary
        variant_count: Number of variants to generate (1-5)
        variation_type: Type of variation (layout, style, structure)

    Returns:
        Dictionary containing diagram variants and metadata

    Example:
        >>> result = generate_diagram_variants(
        ...     "flowchart TD\\n    A --> B",
        ...     variant_count=3,
        ...     variation_type="layout"
        ... )
        >>> print(result["data"]["variants"])
    """
    try:
        import datetime

        if variant_count < 1 or variant_count > 5:
            return create_error_response(
                ValueError("variant_count must be between 1 and 5"),
                ErrorCategory.VALIDATION,
                suggestions=["Provide a variant_count between 1 and 5"],
            )

        valid_types = ["layout", "style", "structure"]
        if variation_type not in valid_types:
            return create_error_response(
                ValueError(f"Invalid variation type: {variation_type}"),
                ErrorCategory.VALIDATION,
                context={"valid_types": valid_types},
                suggestions=[f"Use one of: {', '.join(valid_types)}"],
            )

        variants = []
        diagram_type = _detect_diagram_type(diagram_code)

        if variation_type == "layout":
            # Generate layout variants
            directions = ["TD", "LR", "BT", "RL", "TB"]
            for i in range(min(variant_count, len(directions))):
                direction = directions[i]
                variant_code = _change_diagram_direction(diagram_code, direction)
                variants.append(
                    {
                        "variant_id": f"layout_{i+1}",
                        "description": f"Layout direction: {direction}",
                        "code": variant_code,
                        "changes": [f"Changed direction to {direction}"],
                    }
                )

        elif variation_type == "style":
            # Generate style variants
            presets = ["modern", "classic", "minimal", "colorful", "dark"]
            for i in range(min(variant_count, len(presets))):
                preset = presets[i]
                style_result = transform_diagram_style(diagram_code, style_preset=preset)
                if style_result.get("success"):
                    variants.append(
                        {
                            "variant_id": f"style_{i+1}",
                            "description": f"Style preset: {preset}",
                            "code": style_result["data"]["styled_code"],
                            "changes": [f"Applied {preset} style preset"],
                        }
                    )

        elif variation_type == "structure":
            # Generate structural variants
            # Variant 1: Original
            variants.append(
                {
                    "variant_id": "structure_1",
                    "description": "Original structure",
                    "code": diagram_code,
                    "changes": ["No changes"],
                }
            )

            # Variant 2: With subgraph wrapper
            if variant_count >= 2 and diagram_type == "flowchart":
                wrapped_code = _wrap_in_subgraph(diagram_code, "Main Process")
                variants.append(
                    {
                        "variant_id": "structure_2",
                        "description": "Wrapped in subgraph",
                        "code": wrapped_code,
                        "changes": ["Wrapped content in subgraph"],
                    }
                )

            # Variant 3: With comments
            if variant_count >= 3:
                commented_code = _add_comments(diagram_code)
                variants.append(
                    {
                        "variant_id": "structure_3",
                        "description": "With comments",
                        "code": commented_code,
                        "changes": ["Added descriptive comments"],
                    }
                )

        # Enhanced metadata
        metadata = {
            "generation_timestamp": datetime.datetime.now().isoformat(),
            "original_type": diagram_type,
            "variation_type": variation_type,
            "variants_generated": len(variants),
            "requested_count": variant_count,
        }

        return create_success_response(
            data={
                "variants": variants,
                "original_code": diagram_code,
                "variation_type": variation_type,
            },
            metadata=metadata,
        )

    except Exception as e:
        logger.error(f"Error generating diagram variants: {e}")
        return create_error_response(
            e,
            ErrorCategory.SYSTEM,
            suggestions=[
                "Check diagram syntax",
                "Verify variation type is valid",
            ],
        )
