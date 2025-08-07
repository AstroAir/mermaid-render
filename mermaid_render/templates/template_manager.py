"""
Template management system for Mermaid diagrams.

This module provides the core template management functionality including
template storage, validation, generation, and lifecycle management.
"""

import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from jinja2 import BaseLoader, Environment, TemplateError

from ..exceptions import TemplateError as MermaidTemplateError
from ..exceptions import ValidationError
from .schema import validate_template


@dataclass
class Template:
    """
    Represents a Mermaid diagram template.

    A template contains the template definition, metadata, and generation logic
    for creating parameterized Mermaid diagrams.
    """

    id: str
    name: str
    description: str
    diagram_type: str
    template_content: str
    parameters: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    version: str = "1.0.0"
    author: Optional[str] = None
    tags: Optional[List[str]] = None

    def __post_init__(self) -> None:
        if self.tags is None:
            self.tags = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary for serialization."""
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Template":
        """Create template from dictionary."""
        data = data.copy()
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        return cls(**data)

    def validate(self) -> bool:
        """Validate template structure and content."""
        try:
            # Validate template schema
            validate_template(self.to_dict())

            # Validate Jinja2 template syntax
            env = Environment(loader=BaseLoader())
            env.from_string(self.template_content)

            return True
        except (TemplateError, ValidationError):
            return False


class TemplateManager:
    """
    Manages Mermaid diagram templates including storage, validation, and generation.

    Provides functionality for:
    - Creating and managing custom templates
    - Loading built-in and community templates
    - Generating diagrams from templates with parameters
    - Template validation and schema checking
    - Template sharing and export/import
    """

    def __init__(
        self,
        templates_dir: Optional[Path] = None,
        auto_load_builtin: bool = True,
        auto_load_community: bool = False,
    ):
        """
        Initialize template manager.

        Args:
            templates_dir: Directory for storing custom templates
            auto_load_builtin: Whether to automatically load built-in templates
            auto_load_community: Whether to automatically load community templates
        """
        self.templates_dir = templates_dir or Path.home() / ".mermaid_render_templates"
        self.templates_dir.mkdir(parents=True, exist_ok=True)

        self._templates: Dict[str, Template] = {}
        self._jinja_env = Environment(
            loader=BaseLoader(),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True,
        )

        if auto_load_builtin:
            self._load_builtin_templates()

        if auto_load_community:
            self._load_community_templates()

        # Load custom templates from directory
        self._load_custom_templates()

    def create_template(
        self,
        name: str,
        diagram_type: str,
        template_content: str,
        parameters: Dict[str, Any],
        description: str = "",
        author: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Template:
        """
        Create a new template.

        Args:
            name: Template name
            diagram_type: Type of diagram (flowchart, sequence, etc.)
            template_content: Jinja2 template content
            parameters: Parameter definitions
            description: Template description
            author: Template author
            tags: Template tags for categorization
            metadata: Additional metadata

        Returns:
            Created template

        Raises:
            MermaidTemplateError: If template creation fails
        """
        template_id = str(uuid.uuid4())
        now = datetime.now()

        template = Template(
            id=template_id,
            name=name,
            description=description,
            diagram_type=diagram_type,
            template_content=template_content,
            parameters=parameters,
            metadata=metadata or {},
            created_at=now,
            updated_at=now,
            author=author,
            tags=tags or [],
        )

        # Validate template
        if not template.validate():
            raise MermaidTemplateError(f"Invalid template: {name}")

        self._templates[template_id] = template
        self._save_template(template)

        return template

    def get_template(self, template_id: str) -> Optional[Template]:
        """Get template by ID."""
        return self._templates.get(template_id)

    def get_template_by_name(self, name: str) -> Optional[Template]:
        """Get template by name."""
        for template in self._templates.values():
            if template.name == name:
                return template
        return None

    def list_templates(
        self,
        diagram_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        author: Optional[str] = None,
    ) -> List[Template]:
        """
        List templates with optional filtering.

        Args:
            diagram_type: Filter by diagram type
            tags: Filter by tags (any match)
            author: Filter by author

        Returns:
            List of matching templates
        """
        templates = list(self._templates.values())

        if diagram_type:
            templates = [t for t in templates if t.diagram_type == diagram_type]

        if tags:
            templates = [t for t in templates if t.tags and any(tag in t.tags for tag in tags)]

        if author:
            templates = [t for t in templates if t.author == author]

        return sorted(templates, key=lambda t: t.name)

    def generate(
        self,
        template_id: str,
        parameters: Dict[str, Any],
        validate_params: bool = True,
    ) -> str:
        """
        Generate Mermaid diagram from template.

        Args:
            template_id: Template ID or name
            parameters: Template parameters
            validate_params: Whether to validate parameters

        Returns:
            Generated Mermaid diagram code

        Raises:
            MermaidTemplateError: If generation fails
        """
        # Get template by ID or name
        template = self.get_template(template_id)
        if not template:
            template = self.get_template_by_name(template_id)

        if not template:
            raise MermaidTemplateError(f"Template not found: {template_id}")

        # Validate parameters if requested
        if validate_params:
            self._validate_parameters(template, parameters)

        try:
            # Render template with parameters
            jinja_template = self._jinja_env.from_string(template.template_content)
            diagram_code = jinja_template.render(**parameters)

            return diagram_code.strip()

        except TemplateError as e:
            raise MermaidTemplateError(f"Template rendering failed: {str(e)}") from e

    def delete_template(self, template_id: str) -> bool:
        """Delete a template."""
        if template_id in self._templates:
            # template = self._templates[template_id]  # TODO: Use for logging/validation
            del self._templates[template_id]

            # Remove file if it exists
            template_file = self.templates_dir / f"{template_id}.json"
            if template_file.exists():
                template_file.unlink()

            return True
        return False

    def export_template(self, template_id: str, output_path: Path) -> None:
        """Export template to file."""
        template = self.get_template(template_id)
        if not template:
            raise MermaidTemplateError(f"Template not found: {template_id}")

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(template.to_dict(), f, indent=2)

    def import_template(self, template_file: Path) -> Template:
        """Import template from file."""
        with open(template_file, encoding="utf-8") as f:
            template_data = json.load(f)

        template = Template.from_dict(template_data)

        # Generate new ID to avoid conflicts
        template.id = str(uuid.uuid4())
        template.updated_at = datetime.now()

        self._templates[template.id] = template
        self._save_template(template)

        return template

    def _validate_parameters(
        self, template: Template, parameters: Dict[str, Any]
    ) -> None:
        """Validate parameters against template schema."""
        # This is a simplified validation - in a full implementation,
        # you'd use jsonschema or similar for comprehensive validation
        required_params = template.parameters.get("required", [])

        for param in required_params:
            if param not in parameters:
                raise MermaidTemplateError(f"Missing required parameter: {param}")

    def _save_template(self, template: Template) -> None:
        """Save template to file."""
        template_file = self.templates_dir / f"{template.id}.json"
        with open(template_file, "w", encoding="utf-8") as f:
            json.dump(template.to_dict(), f, indent=2)

    def _load_custom_templates(self) -> None:
        """Load custom templates from templates directory."""
        for template_file in self.templates_dir.glob("*.json"):
            try:
                with open(template_file, encoding="utf-8") as f:
                    template_data = json.load(f)

                template = Template.from_dict(template_data)
                self._templates[template.id] = template

            except (json.JSONDecodeError, KeyError, ValueError):
                # Skip invalid template files
                continue

    def _load_builtin_templates(self) -> None:
        """Load built-in templates."""
        from .library import BuiltInTemplates

        builtin = BuiltInTemplates()
        for template_data in builtin.get_all_templates():
            template = Template.from_dict(template_data)
            self._templates[template.id] = template

    def _load_community_templates(self) -> None:
        """Load community templates."""
        from .library import CommunityTemplates

        try:
            community = CommunityTemplates()
            for template_data in community.get_all_templates():
                template = Template.from_dict(template_data)
                self._templates[template.id] = template
        except Exception:
            # Community templates are optional - don't fail if unavailable
            pass
