"""Export functionality for interactive diagrams."""

from enum import Enum
from typing import Any, Dict


class ExportFormat(Enum):
    """Supported export formats."""

    SVG = "svg"
    PNG = "png"
    PDF = "pdf"
    MERMAID = "mermaid"
    JSON = "json"


class ExportManager:
    """Manages diagram export functionality."""

    def __init__(self) -> None:
        self.supported_formats = list(ExportFormat)

    def export_diagram(self, diagram_data: Dict[str, Any], format: ExportFormat) -> str:
        """Export diagram in specified format."""
        if format == ExportFormat.MERMAID:
            return self._export_mermaid_code(diagram_data)
        elif format == ExportFormat.JSON:
            return self._export_json(diagram_data)
        else:
            # For other formats, would integrate with renderer
            return f"Export to {format.value} not implemented"

    def _export_mermaid_code(self, _diagram_data: Dict[str, Any]) -> str:
        """Export as Mermaid code."""
        # This would use the builder's generate_mermaid_code method
        return "flowchart TD\n    A --> B"

    def _export_json(self, diagram_data: Dict[str, Any]) -> str:
        """Export as JSON."""
        import json

        return json.dumps(diagram_data, indent=2)
