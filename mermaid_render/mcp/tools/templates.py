"""
Template management MCP tools for mermaid-render.

This module provides template creation and management tools.
"""

import logging
from typing import Any

try:
    from fastmcp import Context

    _FASTMCP_AVAILABLE = True
except ImportError:
    Context = None
    _FASTMCP_AVAILABLE = False

from .base import (
    ErrorCategory,
    create_error_response,
    create_success_response,
    measure_performance,
)
from .helpers import (
    _assess_template_complexity,
    _extract_parameter_schema,
    _generate_template_usage_example,
    _generate_template_usage_instructions,
)
from .params import CreateFromTemplateParams, TemplateManagementParams

logger = logging.getLogger(__name__)


def create_from_template(
    template_name: str,
    parameters: dict[str, Any],
    validate_params: bool = True,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """
    Create a Mermaid diagram from a template with provided data.

    Args:
        template_name: Name of the template to use
        parameters: Template parameters
        validate_params: Validate template parameters
        ctx: MCP context (optional)

    Returns:
        Dictionary containing generated diagram from template
    """
    try:
        # Validate parameters
        params = CreateFromTemplateParams(
            template_name=template_name,
            parameters=parameters,
            validate_params=validate_params,
        )

        # Check if templates module is available
        try:
            from ...templates import TemplateManager
        except ImportError:
            return {
                "success": False,
                "error": "Template functionality not available. Install with: pip install mermaid-render[templates]",
                "error_type": "ImportError",
                "request_id": ctx.request_id if ctx else None,
            }

        # Create template manager and generate diagram
        template_manager = TemplateManager()
        diagram_code = template_manager.generate(
            params.template_name,
            params.parameters,
            validate_params=params.validate_params,
        )

        # Get template info for metadata
        template = template_manager.get_template_by_name(params.template_name)

        return {
            "success": True,
            "diagram_code": diagram_code,
            "template_name": params.template_name,
            "parameters_used": params.parameters,
            "template_info": {
                "id": template.id if template else None,
                "description": template.description if template else None,
                "diagram_type": template.diagram_type if template else None,
                "author": template.author if template else None,
                "tags": template.tags if template else [],
            },
            "request_id": ctx.request_id if ctx else None,
        }

    except Exception as e:
        logger.error(f"Error creating diagram from template: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "request_id": ctx.request_id if ctx else None,
        }


@measure_performance
def list_available_templates(
    template_name: str | None = None,
    category: str | None = None,
    include_builtin: bool = True,
    include_custom: bool = True,
) -> dict[str, Any]:
    """
    List all available diagram templates with filtering and categorization.

    This tool provides comprehensive information about all available templates,
    including built-in and custom templates, with filtering capabilities and
    detailed metadata about each template.

    Args:
        template_name: Filter by specific template name
        category: Filter by template category
        include_builtin: Include built-in templates in results
        include_custom: Include custom templates in results

    Returns:
        Dictionary containing template list and metadata

    Example:
        >>> result = list_available_templates()
        >>> print(result["data"]["templates"])  # List of all templates
        >>> result = list_available_templates(category="flowchart")
        >>> print(result["data"]["filtered_count"])  # Number of flowchart templates
    """
    try:
        # Validate parameters
        params = TemplateManagementParams(
            template_name=template_name,
            category=category,
            include_builtin=include_builtin,
            include_custom=include_custom,
        )

        # Check if templates module is available
        try:
            from ...templates import TemplateManager
        except ImportError:
            return create_error_response(
                ImportError("Template functionality not available"),
                ErrorCategory.TEMPLATE,
                suggestions=[
                    "Install template support with: pip install mermaid-render[templates]"
                ],
            )

        # Get templates
        template_manager = TemplateManager()
        all_templates = []

        # Get built-in templates
        if params.include_builtin:
            try:
                from ...templates.library import BuiltInTemplates

                builtin_lib = BuiltInTemplates()
                builtin_templates = builtin_lib.get_all_templates()
                for template in builtin_templates:
                    template["source"] = "builtin"
                    all_templates.append(template)
            except Exception as e:
                logger.warning(f"Could not load built-in templates: {e}")

        # Get custom templates
        if params.include_custom:
            try:
                custom_templates = template_manager.list_templates()
                for template in custom_templates:  # type: ignore[assignment]
                    if hasattr(template, "to_dict"):
                        template_dict = template.to_dict()
                        template_dict["source"] = "custom"
                        all_templates.append(template_dict)
                    elif isinstance(template, dict):
                        template_dict = template.copy()
                        template_dict["source"] = "custom"
                        all_templates.append(template_dict)
                    else:
                        # Skip non-dict, non-template objects
                        pass
            except Exception as e:
                logger.warning(f"Could not load custom templates: {e}")

        # Apply filters
        filtered_templates = all_templates

        if params.template_name:
            filtered_templates = [
                t
                for t in filtered_templates
                if params.template_name.lower() in t.get("name", "").lower()
            ]

        if params.category:
            filtered_templates = [
                t
                for t in filtered_templates
                if t.get("diagram_type") == params.category
            ]

        # Enhanced metadata
        metadata = {
            "total_templates": len(all_templates),
            "filtered_count": len(filtered_templates),
            "builtin_count": len(
                [t for t in all_templates if t.get("source") == "builtin"]
            ),
            "custom_count": len(
                [t for t in all_templates if t.get("source") == "custom"]
            ),
            "categories": list(
                {t.get("diagram_type", "unknown") for t in all_templates}
            ),
            "filters_applied": {
                "template_name": params.template_name,
                "category": params.category,
                "include_builtin": params.include_builtin,
                "include_custom": params.include_custom,
            },
        }

        return create_success_response(
            data={
                "templates": filtered_templates,
                "summary": {
                    "total": len(filtered_templates),
                    "by_category": {
                        cat: len(
                            [
                                t
                                for t in filtered_templates
                                if t.get("diagram_type") == cat
                            ]
                        )
                        for cat in {
                            t.get("diagram_type", "unknown") for t in filtered_templates
                        }
                    },
                    "by_source": {
                        src: len(
                            [t for t in filtered_templates if t.get("source") == src]
                        )
                        for src in {
                            t.get("source", "unknown") for t in filtered_templates
                        }
                    },
                },
            },
            metadata=metadata,
        )

    except Exception as e:
        logger.error(f"Error listing templates: {e}")
        return create_error_response(
            e,
            ErrorCategory.TEMPLATE,
            suggestions=[
                "Check template system is properly configured",
                "Verify template directories are accessible",
            ],
        )


@measure_performance
def get_template_details(
    template_name: str,
) -> dict[str, Any]:
    """
    Get detailed information about a specific template.

    This tool provides comprehensive information about a template including
    its parameters, schema, examples, and usage instructions.

    Args:
        template_name: Name or ID of the template

    Returns:
        Dictionary containing detailed template information

    Example:
        >>> result = get_template_details("software_architecture")
        >>> print(result["data"]["parameters"])  # Template parameters
        >>> print(result["data"]["examples"])    # Usage examples
    """
    try:
        # Check if templates module is available
        try:
            from ...templates import TemplateManager
        except ImportError:
            return create_error_response(
                ImportError("Template functionality not available"),
                ErrorCategory.TEMPLATE,
                suggestions=[
                    "Install template support with: pip install mermaid-render[templates]"
                ],
            )

        # Get template details
        template_manager = TemplateManager()
        template = template_manager.get_template_by_name(template_name)

        if not template:
            # Try by ID
            template = template_manager.get_template(template_name)

        if not template:
            return create_error_response(
                ValueError(f"Template '{template_name}' not found"),
                ErrorCategory.TEMPLATE,
                context={"requested_template": template_name},
                suggestions=[
                    "Check template name spelling",
                    "Use list_available_templates to see available templates",
                ],
            )

        # Get template examples if available
        examples = []
        try:
            from ...templates.utils import get_template_examples

            examples = get_template_examples(template_name, template_manager)
        except Exception as e:
            logger.warning(f"Could not load template examples: {e}")

        # Prepare detailed template information
        template_data = {
            "id": template.id,
            "name": template.name,
            "description": template.description,
            "diagram_type": template.diagram_type,
            "parameters": template.parameters,
            "template_content": template.template_content,
            "metadata": template.metadata,
            "version": template.version,
            "author": template.author,
            "tags": template.tags or [],
            "created_at": (
                template.created_at.isoformat() if template.created_at else None
            ),
            "updated_at": (
                template.updated_at.isoformat() if template.updated_at else None
            ),
            "examples": examples,
            "usage_instructions": _generate_template_usage_instructions(template),
            "parameter_schema": _extract_parameter_schema(template.parameters),
        }

        # Enhanced metadata
        import datetime

        metadata = {
            "template_source": (
                "custom"
                if hasattr(template, "id") and template.id.startswith("custom")
                else "builtin"
            ),
            "parameter_count": len(template.parameters),
            "example_count": len(examples),
            "complexity_level": _assess_template_complexity(template),
            "last_accessed": datetime.datetime.now().isoformat(),
        }

        return create_success_response(data=template_data, metadata=metadata)

    except Exception as e:
        logger.error(f"Error getting template details: {e}")
        return create_error_response(
            e, ErrorCategory.TEMPLATE, context={"template_name": template_name}
        )


@measure_performance
def create_custom_template(
    name: str,
    diagram_type: str,
    template_content: str,
    parameters: dict[str, Any],
    description: str = "",
    author: str | None = None,
    tags: list[str] | None = None,
) -> dict[str, Any]:
    """
    Create a new custom template with validation.

    This tool allows creation of custom diagram templates with comprehensive
    validation and automatic parameter schema generation.

    Args:
        name: Template name
        diagram_type: Type of diagram (flowchart, sequence, etc.)
        template_content: Jinja2 template content
        parameters: Parameter definitions
        description: Template description
        author: Template author
        tags: Template tags for categorization

    Returns:
        Dictionary containing created template information

    Example:
        >>> result = create_custom_template(
        ...     "my_flowchart",
        ...     "flowchart",
        ...     "flowchart TD\\n    {{start}} --> {{end}}",
        ...     {"start": {"type": "string"}, "end": {"type": "string"}},
        ...     "Simple flowchart template"
        ... )
        >>> print(result["data"]["template_id"])  # New template ID
    """
    try:
        # Check if templates module is available
        try:
            from ...templates import TemplateManager
        except ImportError:
            return create_error_response(
                ImportError("Template functionality not available"),
                ErrorCategory.TEMPLATE,
                suggestions=[
                    "Install template support with: pip install mermaid-render[templates]"
                ],
            )

        # Validate template content
        if not template_content.strip():
            return create_error_response(
                ValueError("Template content cannot be empty"),
                ErrorCategory.VALIDATION,
                suggestions=[
                    "Provide valid Jinja2 template content with Mermaid syntax"
                ],
            )

        # Create template
        template_manager = TemplateManager()
        template = template_manager.create_template(
            name=name,
            diagram_type=diagram_type,
            template_content=template_content,
            parameters=parameters,
            description=description,
            author=author,
            tags=tags or [],
        )

        # Prepare response data
        template_data = {
            "template_id": template.id,
            "name": template.name,
            "diagram_type": template.diagram_type,
            "description": template.description,
            "parameters": template.parameters,
            "author": template.author,
            "tags": template.tags,
            "created_at": template.created_at.isoformat(),
            "validation_status": "passed",
            "usage_example": _generate_template_usage_example(template),
        }

        # Enhanced metadata
        metadata = {
            "creation_timestamp": template.created_at.isoformat(),
            "parameter_count": len(parameters),
            "template_size_bytes": len(template_content),
            "complexity_score": _assess_template_complexity(template),
            "validation_passed": True,
        }

        return create_success_response(data=template_data, metadata=metadata)

    except Exception as e:
        logger.error(f"Error creating custom template: {e}")
        return create_error_response(
            e,
            ErrorCategory.TEMPLATE,
            context={
                "template_name": name,
                "diagram_type": diagram_type,
                "content_length": len(template_content) if template_content else 0,
            },
            suggestions=[
                "Check template syntax",
                "Verify parameter definitions",
                "Ensure diagram type is valid",
            ],
        )
