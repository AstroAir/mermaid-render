"""
Built-in and community template libraries for Mermaid diagrams.

This module provides access to pre-built templates for common diagram
patterns and use cases, as well as community-contributed templates.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)

class BuiltInTemplates:
    """
    Built-in template library with common diagram patterns.

    Provides pre-built templates for frequently used diagram types
    and patterns to accelerate diagram creation.
    """

    def __init__(self) -> None:
        self._templates = self._load_builtin_templates()

    def get_all_templates(self) -> list[dict[str, Any]]:
        """Get all built-in templates."""
        return list(self._templates.values())

    def get_template(self, name: str) -> dict[str, Any] | None:
        """Get specific template by name."""
        return self._templates.get(name)

    def list_template_names(self) -> list[str]:
        """Get list of all template names."""
        return list(self._templates.keys())

    def _load_builtin_templates(self) -> dict[str, dict[str, Any]]:
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
        self._templates: dict[str, dict[str, Any]] = {}

        if enable_online:
            self._load_online_templates()

    def get_all_templates(self) -> list[dict[str, Any]]:
        """Get all community templates."""
        return list(self._templates.values())

    def get_template(self, name: str) -> dict[str, Any] | None:
        """Get specific template by name."""
        return self._templates.get(name)

    def list_template_names(self) -> list[str]:
        """Get list of all template names."""
        return list(self._templates.keys())

    def submit_template(self, template_data: dict[str, Any]) -> bool:
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
        """
        Load templates from online community repository.

        Fetches templates from the configured community repository URL.
        Falls back to cached templates if network is unavailable.
        """
        # Default community repository URL (can be configured)
        repository_url = self._get_repository_url()
        cache_file = self._get_cache_file()

        try:
            # Try to fetch from online repository
            templates = self._fetch_online_templates(repository_url)

            if templates:
                # Update local templates
                for template in templates:
                    template_name = template.get("name")
                    if template_name:
                        # Add metadata
                        template["source"] = "community"
                        template["fetched_at"] = datetime.now().isoformat()
                        self._templates[template_name] = template

                # Cache the templates for offline use
                self._cache_templates(templates, cache_file)

                logger.info(
                    f"Loaded {len(templates)} templates from community repository"
                )

        except (URLError, TimeoutError, json.JSONDecodeError) as e:
            logger.warning(f"Failed to fetch online templates: {e}")
            # Try to load from cache
            self._load_cached_templates(cache_file)

    def _get_repository_url(self) -> str:
        """
        Get the community repository URL.

        Returns:
            Repository URL string
        """
        # Default URL - can be overridden via environment variable or config
        import os

        return os.environ.get(
            "MERMAID_COMMUNITY_TEMPLATES_URL",
            "https://raw.githubusercontent.com/mermaid-js/mermaid/develop/packages/mermaid/src/docs/syntax/examples.json",
        )

    def _get_cache_file(self) -> Path:
        """
        Get the cache file path for offline templates.

        Returns:
            Path to cache file
        """
        cache_dir = Path.home() / ".mermaid_render_cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir / "community_templates.json"

    def _fetch_online_templates(self, url: str) -> list[dict[str, Any]]:
        """
        Fetch templates from online repository.

        Args:
            url: Repository URL

        Returns:
            List of template dictionaries
        """
        request = Request(
            url,
            headers={
                "User-Agent": "mermaid-render/1.0.0",
                "Accept": "application/json",
            },
        )

        with urlopen(request, timeout=10) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))

                # Handle different response formats
                if isinstance(data, list):
                    return self._normalize_templates(data)
                elif isinstance(data, dict):
                    # If it's a dict with templates key
                    if "templates" in data:
                        return self._normalize_templates(data["templates"])
                    # If it's a dict of templates by name
                    return self._normalize_templates(list(data.values()))

        return []

    def _normalize_templates(self, raw_templates: list[Any]) -> list[dict[str, Any]]:
        """
        Normalize templates to consistent format.

        Args:
            raw_templates: Raw template data from various sources

        Returns:
            List of normalized template dictionaries
        """
        normalized = []

        for item in raw_templates:
            if not isinstance(item, dict):
                continue

            template = {
                "id": item.get("id", f"community_{len(normalized)}"),
                "name": item.get("name", item.get("title", f"Template {len(normalized)}")),
                "description": item.get("description", ""),
                "diagram_type": item.get("diagram_type", item.get("type", "flowchart")),
                "template_content": item.get(
                    "template_content", item.get("content", item.get("code", ""))
                ),
                "parameters": item.get("parameters", {}),
                "tags": item.get("tags", []),
                "author": item.get("author", "Community"),
                "version": item.get("version", "1.0.0"),
            }

            # Only include templates with actual content
            if template["template_content"]:
                normalized.append(template)

        return normalized

    def _cache_templates(
        self, templates: list[dict[str, Any]], cache_file: Path
    ) -> None:
        """
        Cache templates to local file for offline use.

        Args:
            templates: Templates to cache
            cache_file: Path to cache file
        """
        try:
            cache_data = {
                "cached_at": datetime.now().isoformat(),
                "templates": templates,
            }
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, indent=2)
            logger.debug(f"Cached {len(templates)} templates to {cache_file}")
        except OSError as e:
            logger.warning(f"Failed to cache templates: {e}")

    def _load_cached_templates(self, cache_file: Path) -> None:
        """
        Load templates from local cache.

        Args:
            cache_file: Path to cache file
        """
        if not cache_file.exists():
            logger.debug("No cached templates found")
            return

        try:
            with open(cache_file, encoding="utf-8") as f:
                cache_data = json.load(f)

            templates = cache_data.get("templates", [])
            for template in templates:
                template_name = template.get("name")
                if template_name:
                    template["source"] = "cache"
                    self._templates[template_name] = template

            logger.info(f"Loaded {len(templates)} templates from cache")

        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Failed to load cached templates: {e}")

    def refresh_templates(self) -> int:
        """
        Force refresh templates from online repository.

        Returns:
            Number of templates loaded
        """
        self._templates.clear()
        self._load_online_templates()
        return len(self._templates)

    def search_templates(
        self,
        query: str | None = None,
        diagram_type: str | None = None,
        tags: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Search community templates.

        Args:
            query: Search query string
            diagram_type: Filter by diagram type
            tags: Filter by tags

        Returns:
            List of matching templates
        """
        results = []

        for template in self._templates.values():
            # Filter by diagram type
            if diagram_type and template.get("diagram_type") != diagram_type:
                continue

            # Filter by tags
            if tags:
                template_tags = template.get("tags", [])
                if not any(tag in template_tags for tag in tags):
                    continue

            # Filter by query
            if query:
                query_lower = query.lower()
                name = template.get("name", "").lower()
                description = template.get("description", "").lower()
                if query_lower not in name and query_lower not in description:
                    continue

            results.append(template)

        return results
