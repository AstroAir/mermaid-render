"""Interactive templates for quick diagram creation."""

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .builder import DiagramBuilder
from .models import DiagramType, ElementType, Position, Size


@dataclass
class InteractiveTemplate:
    """Template for interactive diagram creation."""

    id: str
    name: str
    description: str
    diagram_type: str
    elements: list[dict[str, Any]]
    connections: list[dict[str, Any]]
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Convert template to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "InteractiveTemplate":
        """Create template from dictionary."""
        return cls(**data)

    def to_builder(self) -> DiagramBuilder:
        """Convert template to DiagramBuilder instance."""
        # Create builder with appropriate diagram type
        diagram_type = DiagramType(self.diagram_type)
        builder = DiagramBuilder(diagram_type)

        # Set metadata
        builder.metadata.update(self.metadata)
        builder.metadata["title"] = self.name
        builder.metadata["description"] = self.description

        # Add elements
        for element_data in self.elements:
            element_type = ElementType(element_data.get("element_type", "node"))
            position = Position.from_dict(element_data["position"])
            size = Size.from_dict(
                element_data.get("size", {"width": 120, "height": 60})
            )

            builder.add_element(
                element_type=element_type,
                label=element_data["label"],
                position=position,
                size=size,
                properties=element_data.get("properties", {}),
                style=element_data.get("style", {}),
            )

        # Add connections
        for connection_data in self.connections:
            builder.add_connection(
                source_id=connection_data["source_id"],
                target_id=connection_data["target_id"],
                label=connection_data.get("label", ""),
                connection_type=connection_data.get("connection_type", "default"),
                style=connection_data.get("style", {}),
                properties=connection_data.get("properties", {}),
            )

        return builder


class TemplateLibrary:
    """Library of interactive templates."""

    def __init__(self, template_dir: str | Path | None = None) -> None:
        """
        Initialize template library.

        Args:
            template_dir: Directory containing template files (optional)
        """
        self.template_dir = Path(template_dir) if template_dir else None
        self.templates: dict[str, InteractiveTemplate] = {}
        self._load_templates()

    def get_template(self, template_id: str) -> InteractiveTemplate | None:
        """Get template by ID."""
        return self.templates.get(template_id)

    def list_templates(self, category: str | None = None) -> list[InteractiveTemplate]:
        """
        List all templates, optionally filtered by category.

        Args:
            category: Optional category filter

        Returns:
            List of templates
        """
        templates = list(self.templates.values())

        if category:
            templates = [t for t in templates if t.metadata.get("category") == category]

        return sorted(templates, key=lambda t: t.name)

    def get_categories(self) -> list[str]:
        """Get list of all template categories."""
        categories = set()
        for template in self.templates.values():
            category = template.metadata.get("category")
            if category:
                categories.add(category)
        return sorted(categories)

    def add_template(self, template: InteractiveTemplate) -> None:
        """Add a template to the library."""
        self.templates[template.id] = template

    def remove_template(self, template_id: str) -> bool:
        """
        Remove a template from the library.

        Args:
            template_id: ID of template to remove

        Returns:
            True if template was removed, False if not found
        """
        if template_id in self.templates:
            del self.templates[template_id]
            return True
        return False

    def save_template(
        self, template: InteractiveTemplate, filepath: str | Path | None = None
    ) -> None:
        """
        Save template to file.

        Args:
            template: Template to save
            filepath: Optional file path (defaults to template_dir/template_id.json)
        """
        if filepath is None:
            if self.template_dir is None:
                raise ValueError(
                    "No template directory configured and no filepath provided"
                )
            filepath = self.template_dir / f"{template.id}.json"

        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(template.to_dict(), f, indent=2)

    def load_template_from_file(self, filepath: str | Path) -> InteractiveTemplate:
        """
        Load template from file.

        Args:
            filepath: Path to template file

        Returns:
            Loaded template
        """
        filepath = Path(filepath)

        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)

        return InteractiveTemplate.from_dict(data)

    def _load_templates(self) -> None:
        """Load templates from default set and template directory."""
        # Load default templates
        self.templates.update(self._load_default_templates())

        # Load templates from directory if specified
        if self.template_dir and self.template_dir.exists():
            self._load_templates_from_directory()

    def _load_templates_from_directory(self) -> None:
        """Load templates from the template directory."""
        if not self.template_dir:
            return

        for template_file in self.template_dir.glob("*.json"):
            try:
                template = self.load_template_from_file(template_file)
                self.templates[template.id] = template
            except Exception as e:
                print(f"Warning: Failed to load template from {template_file}: {e}")

    def _load_default_templates(self) -> dict[str, InteractiveTemplate]:
        """Load default built-in templates."""
        return {
            "simple_flow": InteractiveTemplate(
                id="simple_flow",
                name="Simple Flow",
                description="Basic flowchart template",
                diagram_type="flowchart",
                elements=[
                    {
                        "id": "start",
                        "element_type": "node",
                        "label": "Start",
                        "position": {"x": 100, "y": 50},
                        "size": {"width": 120, "height": 60},
                        "properties": {"shape": "circle"},
                        "style": {},
                    },
                    {
                        "id": "process",
                        "element_type": "node",
                        "label": "Process",
                        "position": {"x": 100, "y": 150},
                        "size": {"width": 120, "height": 60},
                        "properties": {"shape": "rectangle"},
                        "style": {},
                    },
                    {
                        "id": "end",
                        "element_type": "node",
                        "label": "End",
                        "position": {"x": 100, "y": 250},
                        "size": {"width": 120, "height": 60},
                        "properties": {"shape": "circle"},
                        "style": {},
                    },
                ],
                connections=[
                    {
                        "source_id": "start",
                        "target_id": "process",
                        "label": "",
                        "connection_type": "default",
                        "style": {},
                        "properties": {},
                    },
                    {
                        "source_id": "process",
                        "target_id": "end",
                        "label": "",
                        "connection_type": "default",
                        "style": {},
                        "properties": {},
                    },
                ],
                metadata={"category": "basic", "tags": ["flowchart", "simple"]},
            ),
            "decision_flow": InteractiveTemplate(
                id="decision_flow",
                name="Decision Flow",
                description="Flowchart with decision points",
                diagram_type="flowchart",
                elements=[
                    {
                        "id": "start",
                        "element_type": "node",
                        "label": "Start",
                        "position": {"x": 200, "y": 50},
                        "size": {"width": 120, "height": 60},
                        "properties": {"shape": "circle"},
                        "style": {},
                    },
                    {
                        "id": "decision",
                        "element_type": "node",
                        "label": "Decision?",
                        "position": {"x": 200, "y": 150},
                        "size": {"width": 120, "height": 60},
                        "properties": {"shape": "diamond"},
                        "style": {},
                    },
                    {
                        "id": "yes_path",
                        "element_type": "node",
                        "label": "Yes Path",
                        "position": {"x": 100, "y": 250},
                        "size": {"width": 120, "height": 60},
                        "properties": {"shape": "rectangle"},
                        "style": {},
                    },
                    {
                        "id": "no_path",
                        "element_type": "node",
                        "label": "No Path",
                        "position": {"x": 300, "y": 250},
                        "size": {"width": 120, "height": 60},
                        "properties": {"shape": "rectangle"},
                        "style": {},
                    },
                    {
                        "id": "end",
                        "element_type": "node",
                        "label": "End",
                        "position": {"x": 200, "y": 350},
                        "size": {"width": 120, "height": 60},
                        "properties": {"shape": "circle"},
                        "style": {},
                    },
                ],
                connections=[
                    {
                        "source_id": "start",
                        "target_id": "decision",
                        "label": "",
                        "connection_type": "default",
                        "style": {},
                        "properties": {},
                    },
                    {
                        "source_id": "decision",
                        "target_id": "yes_path",
                        "label": "Yes",
                        "connection_type": "default",
                        "style": {},
                        "properties": {},
                    },
                    {
                        "source_id": "decision",
                        "target_id": "no_path",
                        "label": "No",
                        "connection_type": "default",
                        "style": {},
                        "properties": {},
                    },
                    {
                        "source_id": "yes_path",
                        "target_id": "end",
                        "label": "",
                        "connection_type": "default",
                        "style": {},
                        "properties": {},
                    },
                    {
                        "source_id": "no_path",
                        "target_id": "end",
                        "label": "",
                        "connection_type": "default",
                        "style": {},
                        "properties": {},
                    },
                ],
                metadata={"category": "basic", "tags": ["flowchart", "decision"]},
            ),
            "sequence_basic": InteractiveTemplate(
                id="sequence_basic",
                name="Basic Sequence",
                description="Simple sequence diagram template",
                diagram_type="sequence",
                elements=[
                    {
                        "id": "alice",
                        "element_type": "node",
                        "label": "Alice",
                        "position": {"x": 100, "y": 50},
                        "size": {"width": 120, "height": 60},
                        "properties": {"type": "participant"},
                        "style": {},
                    },
                    {
                        "id": "bob",
                        "element_type": "node",
                        "label": "Bob",
                        "position": {"x": 300, "y": 50},
                        "size": {"width": 120, "height": 60},
                        "properties": {"type": "participant"},
                        "style": {},
                    },
                ],
                connections=[
                    {
                        "source_id": "alice",
                        "target_id": "bob",
                        "label": "Hello Bob",
                        "connection_type": "sync",
                        "style": {},
                        "properties": {},
                    },
                    {
                        "source_id": "bob",
                        "target_id": "alice",
                        "label": "Hello Alice",
                        "connection_type": "return",
                        "style": {},
                        "properties": {},
                    },
                ],
                metadata={"category": "sequence", "tags": ["sequence", "basic"]},
            ),
        }
