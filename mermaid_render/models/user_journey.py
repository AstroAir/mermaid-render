"""User Journey diagram model for the Mermaid Render library."""

from typing import List, Optional

from ..core import MermaidDiagram


class UserJourneyDiagram(MermaidDiagram):
    """User Journey diagram model.

    Allows defining sections and tasks with actors and satisfaction scores,
    and renders Mermaid journey syntax.
    """

    def __init__(self, title: Optional[str] = None) -> None:
        """Initialize an empty user journey diagram.

        Args:
            title: Optional diagram title.
        """
        super().__init__(title)
        self.sections: List[tuple] = []
        self.tasks: List[tuple] = []

    def get_diagram_type(self) -> str:
        """Return the Mermaid diagram type identifier."""
        return "journey"

    def add_section(self, title: str) -> None:
        """Add a section to the journey.

        Args:
            title: Section title displayed in the diagram.
        """
        self.sections.append(("section", title))

    def add_task(self, task: str, actors: List[str], score: int) -> None:
        """Add a task with actors and satisfaction score.

        Args:
            task: Task description.
            actors: Ordered list of actor names.
            score: Satisfaction score (typically 1–5).
        """
        self.tasks.append((task, actors, score))

    def _generate_mermaid(self) -> str:
        """Generate Mermaid syntax for the user journey.

        Returns:
            Mermaid journey diagram text including sections and tasks.
        """
        lines = ["journey"]

        if self.title:
            lines.append(f"    title {self.title}")

        for _section_type, title in self.sections:
            lines.append(f"    section {title}")

        for task, actors, score in self.tasks:
            actors_str = " : ".join(actors)
            lines.append(f"        {task}: {score}: {actors_str}")

        return "\n".join(lines)
