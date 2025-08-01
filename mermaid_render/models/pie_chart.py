"""Pie chart diagram model for the Mermaid Render library."""

from typing import Dict, Optional

from ..core import MermaidDiagram


class PieChartDiagram(MermaidDiagram):
    """Pie chart diagram model for data visualization."""

    def __init__(self, title: Optional[str] = None, show_data: bool = True) -> None:
        super().__init__(title)
        self.show_data = show_data
        self.data: Dict[str, float] = {}

    def get_diagram_type(self) -> str:
        return "pie"

    def add_slice(self, label: str, value: float) -> None:
        """Add a slice to the pie chart."""
        self.data[label] = value

    def to_mermaid(self) -> str:
        """Generate Mermaid syntax for the pie chart."""
        lines = ["pie"]

        if self.title:
            lines.append(f"    title {self.title}")

        if self.show_data:
            lines.append("    showData")

        for label, value in self.data.items():
            lines.append(f'    "{label}" : {value}')

        return "\n".join(lines)
