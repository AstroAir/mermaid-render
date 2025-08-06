"""Entity-Relationship diagram model for the Mermaid Render library."""

from typing import Dict, List, Optional

from ..core import MermaidDiagram


class ERDiagram(MermaidDiagram):
    """Entity-Relationship diagram model."""

    def __init__(self, title: Optional[str] = None) -> None:
        super().__init__(title)
        self.entities: Dict[str, Dict[str, str]] = {}
        self.relationships: List[tuple] = []

    def get_diagram_type(self) -> str:
        return "erDiagram"

    def add_entity(
        self, name: str, attributes: Optional[Dict[str, str]] = None
    ) -> None:
        """Add an entity with attributes."""
        self.entities[name] = attributes or {}

    def add_relationship(self, entity1: str, entity2: str, relationship: str) -> None:
        """Add a relationship between entities."""
        self.relationships.append((entity1, entity2, relationship))

    def _generate_mermaid(self) -> str:
        """Generate Mermaid syntax for the ER diagram."""
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
