"""Gantt diagram model for the Mermaid Render library."""

from typing import List, Optional

from ..core import MermaidDiagram


class GanttDiagram(MermaidDiagram):
    """Gantt diagram model for project timelines.

    Stores sections and tasks and renders them to Mermaid Gantt syntax.
    """

    def __init__(
        self, title: Optional[str] = None, date_format: str = "%Y-%m-%d"
    ) -> None:
        """Initialize an empty Gantt diagram.

        Args:
            title: Optional diagram title.
            date_format: Mermaid dateFormat string (e.g., '%Y-%m-%d').
        """
        super().__init__(title)
        self.date_format = date_format
        self.sections: List[str] = []
        self.tasks: List[tuple] = []

    def get_diagram_type(self) -> str:
        """Return the Mermaid diagram type identifier."""
        return "gantt"

    def add_section(self, title: str) -> None:
        """Add a section to group tasks.

        Args:
            title: Section title shown in the diagram.
        """
        self.sections.append(title)

    def add_task(
        self,
        name: str,
        start_date: Optional[str] = None,
        duration: Optional[str] = None,
        status: str = "active",
    ) -> None:
        """Add a task to the Gantt chart.

        Args:
            name: Task name.
            start_date: Optional start date matching date_format.
            duration: Optional duration (e.g., '3d', '2w').
            status: Mermaid task status/marker (e.g., 'active', 'done', 'crit').
        """
        self.tasks.append((name, start_date, duration, status))

    def _generate_mermaid(self) -> str:
        """Generate Mermaid syntax for the Gantt diagram.

        Returns:
            Mermaid Gantt diagram text including sections and tasks.
        """
        lines = ["gantt"]

        if self.title:
            lines.append(f"    title {self.title}")

        lines.append(f"    dateFormat {self.date_format}")

        for section in self.sections:
            lines.append(f"    section {section}")

        for name, start_date, duration, status in self.tasks:
            task_line = f"        {name} :{status},"
            if start_date:
                task_line += f" {start_date},"
            if duration:
                task_line += f" {duration}"
            lines.append(task_line)

        return "\n".join(lines)
