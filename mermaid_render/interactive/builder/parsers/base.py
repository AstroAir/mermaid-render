"""
Base parser for the interactive diagram builder.

This module provides the abstract base class for Mermaid code parsers.
"""

from abc import ABC, abstractmethod

from ...models import DiagramConnection, DiagramElement


class DiagramParser(ABC):
    """
    Abstract base class for Mermaid code parsers.

    Subclasses implement specific diagram type parsing.
    """

    @abstractmethod
    def parse(
        self, lines: list[str]
    ) -> tuple[dict[str, DiagramElement], dict[str, DiagramConnection]]:
        """
        Parse Mermaid code lines into elements and connections.

        Args:
            lines: Lines of Mermaid code (excluding diagram declaration)

        Returns:
            Tuple of (elements dict, connections dict)
        """
        pass

    def _skip_line(self, line: str) -> bool:
        """Check if line should be skipped (empty or comment)."""
        line = line.strip()
        return not line or line.startswith("%")
