"""
Built-in and community template libraries for Mermaid diagrams.

This module provides access to pre-built templates for common diagram
patterns and use cases, as well as community-contributed templates.
"""

from datetime import datetime
from typing import Any, Dict, List


class BuiltInTemplates:
    """
    Built-in template library with common diagram patterns.

    Provides pre-built templates for frequently used diagram types
    and patterns to accelerate diagram creation.
    """

    def __init__(self):
        self._templates = self._load_builtin_templates()

    def get_all_templates(self) -> List[Dict[str, Any]]:
        """Get all built-in templates."""
        return list(self._templates.values())

    def get_template(self, name: str) -> Dict[str, Any]:
        """Get specific template by name."""
        return self._templates.get(name)

    def list_template_names(self) -> List[str]:
        """Get list of all template names."""
        return list(self._templates.keys())

    def _load_builtin_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load built-in template definitions."""
        now = datetime.now().isoformat()

        templates = {
            "software_architecture": {
                "id": "builtin_software_architecture",
                "name": "Software Architecture",
                "description": "Multi-tier software architecture diagram with services and databases",
                "diagram_type": "flowchart",
                "template_content": """flowchart TD
    %% {{ title }}
    {% for service in services %}
    {{ service.id }}[{{ service.name }}]
    {% endfor %}
    
    {% for db in databases %}
    {{ db.id }}[({{ db.name }})]
    {% endfor %}
    
    {% for connection in connections %}
    {{ connection.from }} --> {{ connection.to }}{% if connection.label %} : {{ connection.label }}{% endif %}
    {% endfor %}
    
    %% Styling
    {% for service in services %}
    classDef service fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    class {{ service.id }} service
    {% endfor %}
    
    {% for db in databases %}
    classDef database fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    class {{ db.id }} database
    {% endfor %}""",
                "parameters": {
                    "required": ["title", "services", "databases", "connections"],
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Architecture diagram title",
                        },
                        "services": {
                            "type": "list",
                            "description": "List of services",
                            "validation": {"min_items": 1, "item_type": "dict"},
                        },
                        "databases": {
                            "type": "list",
                            "description": "List of databases",
                            "validation": {"item_type": "dict"},
                        },
                        "connections": {
                            "type": "list",
                            "description": "Service connections",
                            "validation": {"min_items": 1, "item_type": "dict"},
                        },
                    },
                },
                "metadata": {
                    "category": "architecture",
                    "complexity": "medium",
                    "use_cases": ["system design", "documentation", "planning"],
                },
                "created_at": now,
                "updated_at": now,
                "version": "1.0.0",
                "author": "Mermaid Render Team",
                "tags": ["architecture", "software", "services", "database"],
            },
            "user_journey": {
                "id": "builtin_user_journey",
                "name": "User Journey Map",
                "description": "User journey mapping with touchpoints and emotions",
                "diagram_type": "journey",
                "template_content": """journey
    title {{ title }}
    
    {% for section in sections %}
    section {{ section.name }}
        {% for step in section.steps %}
        {{ step.name }}: {{ step.score }}: {{ step.actors|join(', ') }}
        {% endfor %}
    {% endfor %}""",
                "parameters": {
                    "required": ["title", "sections"],
                    "properties": {
                        "title": {"type": "string", "description": "Journey title"},
                        "sections": {
                            "type": "list",
                            "description": "Journey sections",
                            "validation": {"min_items": 1, "item_type": "dict"},
                        },
                    },
                },
                "metadata": {
                    "category": "ux",
                    "complexity": "simple",
                    "use_cases": [
                        "user experience",
                        "customer journey",
                        "service design",
                    ],
                },
                "created_at": now,
                "updated_at": now,
                "version": "1.0.0",
                "author": "Mermaid Render Team",
                "tags": ["ux", "journey", "customer", "experience"],
            },
            "api_sequence": {
                "id": "builtin_api_sequence",
                "name": "API Interaction Sequence",
                "description": "API call sequence diagram with authentication and error handling",
                "diagram_type": "sequence",
                "template_content": """sequenceDiagram
    title {{ title }}
    
    {% for participant in participants %}
    participant {{ participant.id }} as {{ participant.name }}
    {% endfor %}
    
    {% for interaction in interactions %}
    {% if interaction.type == "call" %}
    {{ interaction.from }}->>{{ interaction.to }}: {{ interaction.message }}
    {% elif interaction.type == "return" %}
    {{ interaction.from }}-->>{{ interaction.to }}: {{ interaction.message }}
    {% elif interaction.type == "note" %}
    Note over {{ interaction.participant }}: {{ interaction.message }}
    {% elif interaction.type == "activate" %}
    activate {{ interaction.participant }}
    {% elif interaction.type == "deactivate" %}
    deactivate {{ interaction.participant }}
    {% endif %}
    {% endfor %}""",
                "parameters": {
                    "required": ["title", "participants", "interactions"],
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Sequence diagram title",
                        },
                        "participants": {
                            "type": "list",
                            "description": "Sequence participants",
                            "validation": {"min_items": 2, "item_type": "dict"},
                        },
                        "interactions": {
                            "type": "list",
                            "description": "Sequence interactions",
                            "validation": {"min_items": 1, "item_type": "dict"},
                        },
                    },
                },
                "metadata": {
                    "category": "api",
                    "complexity": "medium",
                    "use_cases": [
                        "api documentation",
                        "system integration",
                        "debugging",
                    ],
                },
                "created_at": now,
                "updated_at": now,
                "version": "1.0.0",
                "author": "Mermaid Render Team",
                "tags": ["api", "sequence", "integration", "documentation"],
            },
            "class_hierarchy": {
                "id": "builtin_class_hierarchy",
                "name": "Class Hierarchy",
                "description": "Object-oriented class hierarchy with inheritance and relationships",
                "diagram_type": "class",
                "template_content": """classDiagram
    %% {{ title }}
    
    {% for class in classes %}
    class {{ class.name }} {
        {% for attribute in class.attributes %}
        {{ attribute.visibility }}{{ attribute.name }}: {{ attribute.type }}
        {% endfor %}
        {% for method in class.methods %}
        {{ method.visibility }}{{ method.name }}({{ method.parameters|join(', ') }}){% if method.return_type %}: {{ method.return_type }}{% endif %}
        {% endfor %}
    }
    {% if class.abstract %}
    <<abstract>> {{ class.name }}
    {% endif %}
    {% if class.interface %}
    <<interface>> {{ class.name }}
    {% endif %}
    {% endfor %}
    
    {% for relationship in relationships %}
    {{ relationship.from }} {{ relationship.type }} {{ relationship.to }}{% if relationship.label %} : {{ relationship.label }}{% endif %}
    {% endfor %}""",
                "parameters": {
                    "required": ["title", "classes"],
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Class diagram title",
                        },
                        "classes": {
                            "type": "list",
                            "description": "Class definitions",
                            "validation": {"min_items": 1, "item_type": "dict"},
                        },
                        "relationships": {
                            "type": "list",
                            "description": "Class relationships",
                            "validation": {"item_type": "dict"},
                        },
                    },
                },
                "metadata": {
                    "category": "oop",
                    "complexity": "high",
                    "use_cases": ["software design", "documentation", "modeling"],
                },
                "created_at": now,
                "updated_at": now,
                "version": "1.0.0",
                "author": "Mermaid Render Team",
                "tags": ["class", "oop", "inheritance", "uml"],
            },
            "process_flow": {
                "id": "builtin_process_flow",
                "name": "Business Process Flow",
                "description": "Business process flowchart with decision points and parallel processes",
                "diagram_type": "flowchart",
                "template_content": """flowchart TD
    %% {{ title }}
    
    Start([{{ start_label }}])
    {% for step in steps %}
    {% if step.type == "process" %}
    {{ step.id }}[{{ step.label }}]
    {% elif step.type == "decision" %}
    {{ step.id }}{{{ step.label }}}
    {% elif step.type == "subprocess" %}
    {{ step.id }}[[{{ step.label }}]]
    {% elif step.type == "data" %}
    {{ step.id }}[/{{ step.label }}/]
    {% elif step.type == "document" %}
    {{ step.id }}[{{ step.label }}]
    {% endif %}
    {% endfor %}
    End([{{ end_label }}])
    
    %% Connections
    Start --> {{ first_step }}
    {% for connection in connections %}
    {{ connection.from }} -->{% if connection.condition %}|{{ connection.condition }}|{% endif %} {{ connection.to }}
    {% endfor %}
    {{ last_step }} --> End
    
    %% Styling
    classDef startEnd fill:#c8e6c9,stroke:#2e7d32,stroke-width:3px
    classDef process fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef decision fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    
    class Start,End startEnd
    {% for step in steps %}
    {% if step.type == "process" %}
    class {{ step.id }} process
    {% elif step.type == "decision" %}
    class {{ step.id }} decision
    {% endif %}
    {% endfor %}""",
                "parameters": {
                    "required": [
                        "title",
                        "start_label",
                        "end_label",
                        "steps",
                        "connections",
                        "first_step",
                        "last_step",
                    ],
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Process flow title",
                        },
                        "start_label": {
                            "type": "string",
                            "description": "Start node label",
                        },
                        "end_label": {
                            "type": "string",
                            "description": "End node label",
                        },
                        "first_step": {
                            "type": "string",
                            "description": "First step ID",
                        },
                        "last_step": {"type": "string", "description": "Last step ID"},
                        "steps": {
                            "type": "list",
                            "description": "Process steps",
                            "validation": {"min_items": 1, "item_type": "dict"},
                        },
                        "connections": {
                            "type": "list",
                            "description": "Step connections",
                            "validation": {"min_items": 1, "item_type": "dict"},
                        },
                    },
                },
                "metadata": {
                    "category": "business",
                    "complexity": "medium",
                    "use_cases": [
                        "process documentation",
                        "workflow design",
                        "business analysis",
                    ],
                },
                "created_at": now,
                "updated_at": now,
                "version": "1.0.0",
                "author": "Mermaid Render Team",
                "tags": ["process", "workflow", "business", "flowchart"],
            },
        }

        return templates


class CommunityTemplates:
    """
    Community-contributed template library.

    Provides access to templates shared by the community,
    with optional online synchronization.
    """

    def __init__(self, enable_online: bool = False):
        """
        Initialize community templates.

        Args:
            enable_online: Whether to fetch templates from online repository
        """
        self.enable_online = enable_online
        self._templates = {}

        if enable_online:
            self._load_online_templates()

    def get_all_templates(self) -> List[Dict[str, Any]]:
        """Get all community templates."""
        return list(self._templates.values())

    def get_template(self, name: str) -> Dict[str, Any]:
        """Get specific template by name."""
        return self._templates.get(name)

    def list_template_names(self) -> List[str]:
        """Get list of all template names."""
        return list(self._templates.keys())

    def submit_template(self, template_data: Dict[str, Any]) -> bool:
        """
        Submit a template to the community library.

        Args:
            template_data: Template data to submit

        Returns:
            True if submission successful
        """
        # In a real implementation, this would submit to an online repository
        # For now, just add to local collection
        template_name = template_data.get("name")
        if template_name:
            self._templates[template_name] = template_data
            return True
        return False

    def _load_online_templates(self) -> None:
        """Load templates from online community repository."""
        # In a real implementation, this would fetch from a remote API
        # For now, return empty - this is a placeholder for future functionality
        pass
