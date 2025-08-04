"""Interactive templates for quick diagram creation."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class InteractiveTemplate:
    """Template for interactive diagram creation."""

    id: str
    name: str
    description: str
    diagram_type: str
    elements: List[Dict[str, Any]]
    connections: List[Dict[str, Any]]
    metadata: Dict[str, Any]


class TemplateLibrary:
    """Library of interactive templates."""

    def __init__(self):
        self.templates = self._load_default_templates()

    def get_template(self, template_id: str) -> Optional[InteractiveTemplate]:
        return self.templates.get(template_id)

    def list_templates(self) -> List[InteractiveTemplate]:
        return list(self.templates.values())

    def _load_default_templates(self) -> Dict[str, InteractiveTemplate]:
        return {
            "simple_flow": InteractiveTemplate(
                id="simple_flow",
                name="Simple Flow",
                description="Basic flowchart template",
                diagram_type="flowchart",
                elements=[
                    {
                        "id": "start",
                        "type": "node",
                        "label": "Start",
                        "position": {"x": 100, "y": 50},
                    },
                    {
                        "id": "process",
                        "type": "node",
                        "label": "Process",
                        "position": {"x": 100, "y": 150},
                    },
                    {
                        "id": "end",
                        "type": "node",
                        "label": "End",
                        "position": {"x": 100, "y": 250},
                    },
                ],
                connections=[
                    {"source_id": "start", "target_id": "process"},
                    {"source_id": "process", "target_id": "end"},
                ],
                metadata={"category": "basic"},
            )
        }
