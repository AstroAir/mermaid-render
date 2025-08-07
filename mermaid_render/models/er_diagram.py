"""Entity-Relationship diagram model for the Mermaid Render library.

Provides a simple interface to define entities, their attributes, and relationships,
and to emit Mermaid-compatible ER diagram syntax.
"""

from typing import Dict, List, Optional

from ..core import MermaidDiagram


class ERDiagram(MermaidDiagram):
    """Entity-Relationship diagram model.

    Stores entities (with attribute name/type pairs) and relationships between entities,
    and renders them to Mermaid ER diagram syntax.
    """

    def __init__(self, title: Optional[str] = None) -> None:
        """Initialize an empty ER diagram.

        Args:
            title: Optional diagram title.
        """
        super().__init__(title)
        self.entities: Dict[str, Dict[str, str]] = {}
        self.relationships: List[tuple] = []

    def get_diagram_type(self) -> str:
        """Return the Mermaid diagram type identifier."""
        return "erDiagram"

    def add_entity(
        self, name: str, attributes: Optional[Dict[str, str]] = None
    ) -> None:
        """Add or replace an entity with optional attributes.

        Args:
            name: Entity name.
            attributes: Mapping of attribute name to type (e.g., {"id": "INT"}).
        """
        self.entities[name] = attributes or {}

    def add_relationship(self, entity1: str, entity2: str, relationship: str) -> None:
        """Add a relationship between two entities.

        Args:
            entity1: Left entity name.
            entity2: Right entity name.
            relationship: Mermaid ER relationship operator (e.g., "||--o{").
        """
        self.relationships.append((entity1, entity2, relationship))

    def _generate_mermaid(self) -> str:
        """Generate Mermaid syntax for the ER diagram.

        Returns:
            Mermaid ER diagram text including entities, attributes, and relationships.
        """
        lines = ["erDiagram"]

        if self.title:
            lines.append(f"    title: {self.title}")

        # Add entities with attributes
        for entity, attributes in self.entities.items():
            lines.append(f"    {entity} {{")
            for attr_name, attr_type in attributes.items():
                lines.append(f"        {attr_type} {attr_name}")
            lines.append("    }")

        # Add relationships
        for entity1, entity2, relationship in self.relationships:
            lines.append(f"    {entity1} {relationship} {entity2}")

        return "\n".join(lines)
