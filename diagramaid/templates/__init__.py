"""
Template system for the Mermaid Render library.

This package provides a comprehensive template system for creating reusable
diagram templates with parameterized generation, template management,
and community template sharing.

Features:
- Pre-built templates for common diagram patterns
- Parameterized template generation
- Template validation and schema checking
- Template library management
- Custom template creation and sharing
- Integration with data sources (JSON, CSV, databases)

Example:
    >>> from diagramaid.templates import TemplateManager, generate_from_template
    >>>
    >>> # Use a built-in template
    >>> manager = TemplateManager()
    >>> diagram = manager.generate("software_architecture", {
    ...     "services": ["API", "Database", "Cache"],
    ...     "connections": [("API", "Database"), ("API", "Cache")]
    ... })
    >>>
    >>> # Create custom template
    >>> template = manager.create_template("my_template", {
    ...     "type": "flowchart",
    ...     "parameters": {"title": "string", "nodes": "list"},
    ...     "template": "flowchart TD\\n    {{title}}\\n    {% for node in nodes %}{{node}}{% endfor %}"
    ... })
"""

from .data_sources import (
    APIDataSource,
    CSVDataSource,
    DatabaseDataSource,
    JSONDataSource,
)
from .generators import (
    ArchitectureGenerator,
    ClassDiagramGenerator,
    FlowchartGenerator,
    ProcessFlowGenerator,
    SequenceGenerator,
)
from .library import BuiltInTemplates, CommunityTemplates
from .schema import (
    ParameterSchema,
    TemplateSchema,
    validate_template,
    validate_template_parameters,
)
from .template_manager import Template, TemplateManager

# Convenience functions
from .utils import (
    export_template,
    generate_from_template,
    get_template_info,
    import_template,
    list_available_templates,
)

__all__ = [
    # Core classes
    "TemplateManager",
    "Template",
    "TemplateSchema",
    "ParameterSchema",
    # Generators
    "FlowchartGenerator",
    "SequenceGenerator",
    "ClassDiagramGenerator",
    "ArchitectureGenerator",
    "ProcessFlowGenerator",
    # Template libraries
    "BuiltInTemplates",
    "CommunityTemplates",
    # Data sources
    "JSONDataSource",
    "CSVDataSource",
    "DatabaseDataSource",
    "APIDataSource",
    # Utilities
    "generate_from_template",
    "list_available_templates",
    "get_template_info",
    "validate_template_parameters",
    "validate_template",
    "export_template",
    "import_template",
]
