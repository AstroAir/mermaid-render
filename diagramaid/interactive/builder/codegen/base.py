"""
Base code generator for the interactive diagram builder.

This module provides the abstract base class for Mermaid code generators.
"""

from abc import ABC, abstractmethod
from typing import Any

from ...models import DiagramConnection, DiagramElement


class CodeGenerator(ABC):
    """
    Abstract base class for Mermaid code generators.

    Subclasses implement specific diagram type code generation.
    """

    @abstractmethod
    def generate(
        self,
        elements: dict[str, DiagramElement],
        connections: dict[str, DiagramConnection],
        metadata: dict[str, Any],
    ) -> str:
        """
        Generate Mermaid code for the diagram.

        Args:
            elements: Dictionary of diagram elements
            connections: Dictionary of diagram connections
            metadata: Diagram metadata

        Returns:
            Generated Mermaid code
        """
        pass

    def _add_title_comment(self, lines: list[str], metadata: dict[str, Any]) -> None:
        """Add title as comment if present in metadata."""
        if metadata.get("title"):
            lines.append(f"    %% {metadata['title']}")
            lines.append("")

    def _add_description_comment(
        self, lines: list[str], metadata: dict[str, Any]
    ) -> None:
        """Add description as comment if present in metadata."""
        if metadata.get("description"):
            lines.append(f"    %% {metadata['description']}")
            lines.append("")
