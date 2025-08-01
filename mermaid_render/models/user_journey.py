"""User Journey diagram model for the Mermaid Render library."""

from typing import List, Optional

from ..core import MermaidDiagram


class UserJourneyDiagram(MermaidDiagram):
    """User Journey diagram model."""

    def __init__(self, title: Optional[str] = None) -> None:
        super().__init__(title)
        self.sections: List[tuple] = []
        self.tasks: List[tuple] = []

    def get_diagram_type(self) -> str:
        return "journey"

    def add_section(self, title: str) -> None:
        """Add a section to the journey."""
        self.sections.append(("section", title))

    def add_task(self, task: str, actors: List[str], score: int) -> None:
        """Add a task with actors and satisfaction score."""
        self.tasks.append((task, actors, score))

    def to_mermaid(self) -> str:
        """Generate Mermaid syntax for the user journey."""
        lines = ["journey"]

        if self.title:
            lines.append(f"    title {self.title}")

        for section_type, title in self.sections:
            lines.append(f"    section {title}")

        for task, actors, score in self.tasks:
            actors_str = " : ".join(actors)
            lines.append(f"        {task}: {score}: {actors_str}")

        return "\n".join(lines)
