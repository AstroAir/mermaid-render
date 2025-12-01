"""
Template resources for MCP.

This module provides template-related resource implementations.
"""

import json

from .base import Context, ResourceError, logger


async def get_templates_resource(ctx: Context) -> str:
    """
    Get all available templates resource.

    Args:
        ctx: MCP context

    Returns:
        JSON string containing templates data
    """
    try:
        try:
            from ...templates import TemplateManager

            template_manager = TemplateManager()
            templates = template_manager.list_templates()

            templates_data = {
                "templates": [
                    {
                        "id": template.id,
                        "name": template.name,
                        "description": template.description,
                        "diagram_type": template.diagram_type,
                        "author": template.author,
                        "tags": template.tags,
                        "created_at": (
                            template.created_at.isoformat()
                            if template.created_at
                            else None
                        ),
                        "parameters": template.parameters,
                    }
                    for template in templates
                ],
                "total_count": len(templates),
                "builtin_count": len(
                    [t for t in templates if t.author == "diagramaid"]
                ),
                "custom_count": len(
                    [t for t in templates if t.author != "diagramaid"]
                ),
            }

        except ImportError:
            templates_data = {
                "templates": [],
                "total_count": 0,
                "builtin_count": 0,
                "custom_count": 0,
                "error": "Template functionality not available. Install with: pip install diagramaid[templates]",
            }

        return json.dumps(templates_data, indent=2)

    except Exception as e:
        logger.error(f"Error getting templates resource: {e}")
        raise ResourceError(f"Failed to get templates: {e}")


async def get_template_details(ctx: Context, template_name: str) -> str:
    """
    Get details for a specific template.

    Args:
        ctx: MCP context
        template_name: Name of the template

    Returns:
        JSON string containing template details
    """
    try:
        try:
            from ...templates import TemplateManager

            template_manager = TemplateManager()
            template = template_manager.get_template_by_name(template_name)

            if not template:
                raise ResourceError(f"Template '{template_name}' not found")

            template_data = {
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "diagram_type": template.diagram_type,
                "template_content": template.template_content,
                "parameters": template.parameters,
                "metadata": template.metadata,
                "author": template.author,
                "tags": template.tags,
                "created_at": (
                    template.created_at.isoformat() if template.created_at else None
                ),
                "updated_at": (
                    template.updated_at.isoformat() if template.updated_at else None
                ),
                "usage_examples": (
                    template.metadata.get("examples", []) if template.metadata else []
                ),
            }

        except ImportError:
            raise ResourceError(
                "Template functionality not available. Install with: pip install diagramaid[templates]"
            )

        return json.dumps(template_data, indent=2)

    except Exception as e:
        logger.error(f"Error getting template details for {template_name}: {e}")
        raise ResourceError(f"Failed to get template details: {e}")
