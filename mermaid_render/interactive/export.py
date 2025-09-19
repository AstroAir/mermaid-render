"""Export functionality for interactive diagrams."""

import json
import tempfile
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, Union

from ..core import MermaidRenderer
from .builder import DiagramBuilder


class ExportFormat(Enum):
    """Supported export formats."""

    SVG = "svg"
    PNG = "png"
    PDF = "pdf"
    MERMAID = "mermaid"
    JSON = "json"


class ExportManager:
    """Manages diagram export functionality."""

    def __init__(self, renderer: Optional[MermaidRenderer] = None) -> None:
        """
        Initialize export manager.

        Args:
            renderer: MermaidRenderer instance for rendering diagrams
        """
        self.renderer = renderer or MermaidRenderer()
        self.supported_formats = list(ExportFormat)

    def export_diagram(
        self,
        diagram_data: Union[Dict[str, Any], DiagramBuilder],
        format: ExportFormat,
        filename: Optional[str] = None
    ) -> Union[str, bytes]:
        """
        Export diagram in specified format.

        Args:
            diagram_data: Diagram data dictionary or DiagramBuilder instance
            format: Export format
            filename: Optional filename for file-based exports

        Returns:
            Exported content as string or bytes
        """
        if isinstance(diagram_data, DiagramBuilder):
            builder = diagram_data
        else:
            # Create builder from data
            builder = self._create_builder_from_data(diagram_data)

        if format == ExportFormat.MERMAID:
            return self._export_mermaid_code(builder)
        elif format == ExportFormat.JSON:
            return self._export_json(builder)
        elif format in [ExportFormat.SVG, ExportFormat.PNG, ExportFormat.PDF]:
            return self._export_rendered_format(builder, format, filename)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def export_to_file(
        self,
        diagram_data: Union[Dict[str, Any], DiagramBuilder],
        filepath: Union[str, Path],
        format: Optional[ExportFormat] = None
    ) -> None:
        """
        Export diagram to file.

        Args:
            diagram_data: Diagram data dictionary or DiagramBuilder instance
            filepath: Output file path
            format: Export format (auto-detected from file extension if not provided)
        """
        filepath = Path(filepath)

        if format is None:
            # Auto-detect format from file extension
            extension = filepath.suffix.lower().lstrip('.')
            format_map = {
                'svg': ExportFormat.SVG,
                'png': ExportFormat.PNG,
                'pdf': ExportFormat.PDF,
                'mmd': ExportFormat.MERMAID,
                'json': ExportFormat.JSON
            }
            format = format_map.get(extension, ExportFormat.SVG)

        content = self.export_diagram(diagram_data, format)

        # Write to file
        if format in [ExportFormat.PNG, ExportFormat.PDF]:
            # Binary content
            if isinstance(content, bytes):
                filepath.write_bytes(content)
            else:
                raise TypeError(f"Expected bytes for {format} format, got {type(content)}")
        else:
            # Text content
            if isinstance(content, str):
                filepath.write_text(content, encoding='utf-8')
            else:
                raise TypeError(f"Expected str for {format} format, got {type(content)}")

    def _create_builder_from_data(self, diagram_data: Dict[str, Any]) -> DiagramBuilder:
        """Create DiagramBuilder from data dictionary."""
        from .builder import DiagramType

        builder = DiagramBuilder()

        # Set diagram type if specified
        if 'diagram_type' in diagram_data:
            builder.diagram_type = DiagramType(diagram_data['diagram_type'])

        # Load from dictionary
        builder.from_dict(diagram_data)

        return builder

    def _export_mermaid_code(self, builder: DiagramBuilder) -> str:
        """Export as Mermaid code."""
        return builder.generate_mermaid_code()

    def _export_json(self, builder: DiagramBuilder) -> str:
        """Export as JSON."""
        return json.dumps(builder.to_dict(), indent=2)

    def _export_rendered_format(
        self,
        builder: DiagramBuilder,
        format: ExportFormat,
        filename: Optional[str] = None
    ) -> Union[str, bytes]:
        """Export using MermaidRenderer for SVG/PNG/PDF formats."""
        # Generate Mermaid code
        mermaid_code = builder.generate_mermaid_code()

        # Render using core renderer
        try:
            if format == ExportFormat.SVG:
                return self.renderer.render_raw(mermaid_code, format="svg")
            elif format == ExportFormat.PNG:
                return self.renderer.render_raw(mermaid_code, format="png")
            elif format == ExportFormat.PDF:
                return self.renderer.render_raw(mermaid_code, format="pdf")
            else:
                raise ValueError(f"Unsupported rendered format: {format}")

        except Exception as e:
            # Fallback to basic SVG if rendering fails
            if format == ExportFormat.SVG:
                return self._generate_fallback_svg(builder)
            else:
                raise RuntimeError(f"Failed to render diagram: {e}") from e

    def _generate_fallback_svg(self, builder: DiagramBuilder) -> str:
        """Generate basic SVG fallback when rendering fails."""
        svg_parts = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600" viewBox="0 0 800 600">',
            '<style>',
            '.node { fill: #f9f9f9; stroke: #333; stroke-width: 2; }',
            '.text { font-family: Arial, sans-serif; font-size: 14px; text-anchor: middle; }',
            '.connection { stroke: #333; stroke-width: 2; fill: none; marker-end: url(#arrowhead); }',
            '</style>',
            '<defs>',
            '<marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">',
            '<polygon points="0 0, 10 3.5, 0 7" fill="#333" />',
            '</marker>',
            '</defs>'
        ]

        # Add elements
        for element in builder.elements.values():
            x, y = element.position.x, element.position.y
            width, height = element.size.width, element.size.height

            # Add shape based on type
            shape = element.properties.get('shape', 'rectangle')
            if shape == 'circle':
                cx, cy = x + width/2, y + height/2
                rx, ry = width/2, height/2
                svg_parts.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" class="node" />')
            else:
                svg_parts.append(f'<rect x="{x}" y="{y}" width="{width}" height="{height}" class="node" />')

            # Add text
            text_x, text_y = x + width/2, y + height/2
            svg_parts.append(f'<text x="{text_x}" y="{text_y}" class="text">{element.label}</text>')

        # Add connections
        for connection in builder.connections.values():
            source = builder.elements.get(connection.source_id)
            target = builder.elements.get(connection.target_id)

            if source and target:
                x1 = source.position.x + source.size.width/2
                y1 = source.position.y + source.size.height/2
                x2 = target.position.x + target.size.width/2
                y2 = target.position.y + target.size.height/2

                svg_parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="connection" />')

                # Add label if present
                if connection.label:
                    label_x = (x1 + x2) / 2
                    label_y = (y1 + y2) / 2
                    svg_parts.append(f'<text x="{label_x}" y="{label_y}" class="text">{connection.label}</text>')

        svg_parts.append('</svg>')
        return '\n'.join(svg_parts)

    def get_supported_formats(self) -> list[ExportFormat]:
        """Get list of supported export formats."""
        return self.supported_formats.copy()

    def validate_format(self, format: Union[str, ExportFormat]) -> ExportFormat:
        """
        Validate and normalize export format.

        Args:
            format: Format as string or ExportFormat enum

        Returns:
            Validated ExportFormat

        Raises:
            ValueError: If format is not supported
        """
        if isinstance(format, str):
            try:
                format = ExportFormat(format.lower())
            except ValueError:
                raise ValueError(f"Unsupported format: {format}")

        if format not in self.supported_formats:
            raise ValueError(f"Format {format} is not supported")

        return format
