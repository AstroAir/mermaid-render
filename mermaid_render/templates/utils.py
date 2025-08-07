"""
Utility functions for the template system.

This module provides convenience functions for working with templates,
including generation, validation, and management utilities.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, cast

from ..exceptions import TemplateError as MermaidTemplateError
from .schema import validate_template_parameters
from .template_manager import Template, TemplateManager


def generate_from_template(
    template_name: str,
    parameters: Dict[str, Any],
    template_manager: Optional[TemplateManager] = None,
    validate_params: bool = True,
) -> str:
    """
    Generate diagram from template - convenience function.

    Args:
        template_name: Name or ID of template to use
        parameters: Template parameters
        template_manager: Optional template manager instance
        validate_params: Whether to validate parameters

    Returns:
        Generated Mermaid diagram code

    Raises:
        MermaidTemplateError: If generation fails

    Example:
        >>> diagram_code = generate_from_template("software_architecture", {
        ...     "title": "My System",
        ...     "services": [{"id": "api", "name": "API Service"}],
        ...     "databases": [{"id": "db", "name": "Database"}],
        ...     "connections": [{"from": "api", "to": "db", "label": "queries"}]
        ... })
    """
    if template_manager is None:
        template_manager = TemplateManager()

    return template_manager.generate(template_name, parameters, validate_params)


def list_available_templates(
    template_manager: Optional[TemplateManager] = None,
    diagram_type: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    List available templates with metadata.

    Args:
        template_manager: Optional template manager instance
        diagram_type: Filter by diagram type
        tags: Filter by tags

    Returns:
        List of template information dictionaries

    Example:
        >>> templates = list_available_templates(diagram_type="flowchart")
        >>> for template in templates:
        ...     print(f"{template['name']}: {template['description']}")
    """
    if template_manager is None:
        template_manager = TemplateManager()

    templates = template_manager.list_templates(diagram_type=diagram_type, tags=tags)

    return [
        {
            "id": template.id,
            "name": template.name,
            "description": template.description,
            "diagram_type": template.diagram_type,
            "tags": template.tags,
            "author": template.author,
            "version": template.version,
            "created_at": template.created_at.isoformat(),
            "parameter_count": len(template.parameters.get("required", [])),
        }
        for template in templates
    ]


def get_template_info(
    template_name: str,
    template_manager: Optional[TemplateManager] = None,
) -> Optional[Dict[str, Any]]:
    """
    Get detailed information about a template.

    Args:
        template_name: Name or ID of template
        template_manager: Optional template manager instance

    Returns:
        Template information dictionary or None if not found

    Example:
        >>> info = get_template_info("software_architecture")
        >>> print(f"Parameters: {info['parameters']}")
    """
    if template_manager is None:
        template_manager = TemplateManager()

    template = template_manager.get_template(template_name)
    if not template:
        template = template_manager.get_template_by_name(template_name)

    if not template:
        return None

    return {
        "id": template.id,
        "name": template.name,
        "description": template.description,
        "diagram_type": template.diagram_type,
        "parameters": template.parameters,
        "metadata": template.metadata,
        "tags": template.tags,
        "author": template.author,
        "version": template.version,
        "created_at": template.created_at.isoformat(),
        "updated_at": template.updated_at.isoformat(),
        "template_content": template.template_content,
    }


def validate_template_params_by_name(
    template_name: str,
    parameters: Dict[str, Any],
    template_manager: Optional[TemplateManager] = None,
) -> List[str]:
    """
    Validate parameters against template schema.

    Args:
        template_name: Name or ID of template
        parameters: Parameters to validate
        template_manager: Optional template manager instance

    Returns:
        List of validation errors (empty if valid)

    Example:
        >>> errors = validate_template_parameters("software_architecture", {
        ...     "title": "My System"
        ...     # Missing required parameters
        ... })
        >>> if errors:
        ...     print("Validation errors:", errors)
    """
    if template_manager is None:
        template_manager = TemplateManager()

    template = template_manager.get_template(template_name)
    if not template:
        template = template_manager.get_template_by_name(template_name)

    if not template:
        return [f"Template not found: {template_name}"]

    from .schema import validate_template_parameters as validate_params

    return validate_params(template.parameters, parameters)


def export_template(
    template_name: str,
    output_path: Union[str, Path],
    template_manager: Optional[TemplateManager] = None,
) -> bool:
    """
    Export template to file.

    Args:
        template_name: Name or ID of template to export
        output_path: Output file path
        template_manager: Optional template manager instance

    Returns:
        True if export successful

    Example:
        >>> success = export_template("my_template", "exported_template.json")
    """
    if template_manager is None:
        template_manager = TemplateManager()

    try:
        template_manager.export_template(template_name, Path(output_path))
        return True
    except MermaidTemplateError:
        return False


def import_template(
    template_file: Union[str, Path],
    template_manager: Optional[TemplateManager] = None,
) -> Optional[str]:
    """
    Import template from file.

    Args:
        template_file: Path to template file
        template_manager: Optional template manager instance

    Returns:
        Template ID if import successful, None otherwise

    Example:
        >>> template_id = import_template("my_template.json")
        >>> if template_id:
        ...     print(f"Imported template: {template_id}")
    """
    if template_manager is None:
        template_manager = TemplateManager()

    try:
        template = template_manager.import_template(Path(template_file))
        return template.id
    except (MermaidTemplateError, FileNotFoundError, json.JSONDecodeError):
        return None


def create_template_from_diagram(
    diagram_code: str,
    template_name: str,
    parameters: Dict[str, Any],
    description: str = "",
    diagram_type: Optional[str] = None,
    template_manager: Optional[TemplateManager] = None,
) -> Optional[str]:
    """
    Create a template from existing diagram code.

    Args:
        diagram_code: Existing Mermaid diagram code
        template_name: Name for the new template
        parameters: Parameter definitions
        description: Template description
        diagram_type: Diagram type (auto-detected if not provided)
        template_manager: Optional template manager instance

    Returns:
        Template ID if creation successful, None otherwise

    Example:
        >>> template_id = create_template_from_diagram(
        ...     "flowchart TD\\n    A[{{title}}] --> B[End]",
        ...     "simple_flow",
        ...     {"required": ["title"], "properties": {"title": {"type": "string"}}},
        ...     "Simple flowchart template"
        ... )
    """
    if template_manager is None:
        template_manager = TemplateManager()

    # Auto-detect diagram type if not provided
    if diagram_type is None:
        from ..utils.helpers import detect_diagram_type

        diagram_type = detect_diagram_type(diagram_code)
        if not diagram_type:
            return None

    try:
        template = template_manager.create_template(
            name=template_name,
            diagram_type=diagram_type,
            template_content=diagram_code,
            parameters=parameters,
            description=description,
        )
        return template.id
    except MermaidTemplateError:
        return None


def get_template_examples(
    template_name: str,
    template_manager: Optional[TemplateManager] = None,
) -> List[Dict[str, Any]]:
    """
    Get example parameter sets for a template.

    Args:
        template_name: Name or ID of template
        template_manager: Optional template manager instance

    Returns:
        List of example parameter dictionaries

    Example:
        >>> examples = get_template_examples("software_architecture")
        >>> for example in examples:
        ...     print(f"Example: {example['name']}")
        ...     diagram = generate_from_template("software_architecture", example['parameters'])
    """
    if template_manager is None:
        template_manager = TemplateManager()

    template = template_manager.get_template(template_name)
    if not template:
        template = template_manager.get_template_by_name(template_name)

    if not template:
        return []

    # Extract examples from parameter definitions
    examples = []

    # Check if template has predefined examples in metadata
    if "examples" in template.metadata:
        examples.extend(template.metadata["examples"])

    # Generate basic example from parameter schema
    if not examples:
        basic_example = _generate_basic_example(template.parameters)
        if basic_example:
            examples.append(
                {
                    "name": "Basic Example",
                    "description": "Minimal parameter set",
                    "parameters": basic_example,
                }
            )

    return examples


def _generate_basic_example(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a basic example from parameter schema."""
    example: Dict[str, Any] = {}

    required_params = parameters.get("required", [])
    properties = parameters.get("properties", {})

    for param_name in required_params:
        if param_name in properties:
            param_def = properties[param_name]
            param_type = param_def.get("type", "string")

            # Generate example values based on type
            if param_type == "string":
                example[param_name] = f"Example {param_name}"
            elif param_type == "integer":
                example[param_name] = 1
            elif param_type == "float":
                example[param_name] = 1.0
            elif param_type == "boolean":
                example[param_name] = True
            elif param_type == "list":
                example[param_name] = ["item1", "item2"]
            elif param_type == "dict":
                example[param_name] = {"key": "value"}

    return example


def search_templates(
    query: str,
    template_manager: Optional[TemplateManager] = None,
    search_fields: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Search templates by query string.

    Args:
        query: Search query
        template_manager: Optional template manager instance
        search_fields: Fields to search in (name, description, tags)

    Returns:
        List of matching template information

    Example:
        >>> results = search_templates("architecture")
        >>> for result in results:
        ...     print(f"Found: {result['name']}")
    """
    if template_manager is None:
        template_manager = TemplateManager()

    if search_fields is None:
        search_fields = ["name", "description", "tags"]

    query_lower = query.lower()
    all_templates = template_manager.list_templates()
    matching_templates = []

    for template in all_templates:
        match = False

        if "name" in search_fields and query_lower in template.name.lower():
            match = True

        if (
            "description" in search_fields
            and query_lower in template.description.lower()
        ):
            match = True

        if "tags" in search_fields and template.tags:
            for tag in template.tags:
                if query_lower in tag.lower():
                    match = True
                    break

        if match:
            matching_templates.append(
                {
                    "id": template.id,
                    "name": template.name,
                    "description": template.description,
                    "diagram_type": template.diagram_type,
                    "tags": template.tags,
                    "relevance_score": _calculate_relevance(
                        template, query_lower, search_fields
                    ),
                }
            )

    # Sort by relevance score
    matching_templates.sort(key=lambda x: cast(float, x["relevance_score"]), reverse=True)

    return matching_templates


def _calculate_relevance(
    template: Template, query: str, search_fields: List[str]
) -> float:
    """Calculate relevance score for search results."""
    score = 0.0

    if "name" in search_fields:
        if query in template.name.lower():
            score += 3.0  # Name matches are most important
        elif any(word in template.name.lower() for word in query.split()):
            score += 1.5

    if "description" in search_fields:
        if query in template.description.lower():
            score += 2.0
        elif any(word in template.description.lower() for word in query.split()):
            score += 1.0

    if "tags" in search_fields and template.tags:
        for tag in template.tags:
            if query in tag.lower():
                score += 2.5
            elif any(word in tag.lower() for word in query.split()):
                score += 1.2

    return score
