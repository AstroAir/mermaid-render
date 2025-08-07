"""Pie chart diagram model for the Mermaid Render library."""

from typing import Dict, Optional

from ..core import MermaidDiagram


class PieChartDiagram(MermaidDiagram):
    """Pie chart diagram model for data visualization.

    Supports adding labeled numeric slices and rendering Mermaid pie syntax.
    """

    def __init__(self, title: Optional[str] = None, show_data: bool = True) -> None:
        """Initialize an empty pie chart.

        Args:
            title: Optional chart title.
            show_data: Whether to display numeric values on the chart.
        """
        super().__init__(title)
        self.show_data = show_data
        self.data: Dict[str, float] = {}

    def get_diagram_type(self) -> str:
        """Return the Mermaid diagram type identifier."""
        return "pie"

    def add_slice(self, label: str, value: float) -> None:
        """Add a slice to the pie chart.

        Args:
            label: Display label for the slice.
            value: Numeric value determining the slice size.
        """
        self.data[label] = value

    def _generate_mermaid(self) -> str:
        """Generate Mermaid syntax for the pie chart.

        Returns:
            Mermaid pie diagram text with title, showData flag, and slices.
        """
        lines = ["pie"]

        if self.title:
            lines.append(f"    title {self.title}")

        if self.show_data:
            lines.append("    showData")

        for label, value in self.data.items():
            lines.append(f'    "{label}" : {value}')

        return "\n".join(lines)
