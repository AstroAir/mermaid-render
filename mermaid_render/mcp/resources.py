"""
MCP resources implementation for mermaid-render.

This module provides MCP (Model Context Protocol) resource implementations
that expose mermaid-render data and configurations through the MCP protocol.
"""

import json
import logging
from typing import Any, Dict, List, Optional

try:
    from fastmcp import FastMCP, Context
    from fastmcp.resources import ResourceError
    _FASTMCP_AVAILABLE = True
except ImportError:
    # Allow importing for testing without FastMCP
    FastMCP = None
    Context = None
    ResourceError = Exception
    _FASTMCP_AVAILABLE = False

logger = logging.getLogger(__name__)


def register_all_resources(mcp) -> None:
    """
    Register all MCP resources with the FastMCP server.
    
    Args:
        mcp: FastMCP server instance
    """
    if not _FASTMCP_AVAILABLE:
        raise ImportError(
            "FastMCP is required for MCP server functionality. "
            "Install it with: pip install fastmcp"
        )
    
    # Theme resources
    mcp.resource(
        uri="mermaid://themes",
        name="Available Themes",
        description="List of all available Mermaid themes with descriptions",
        mimeType="application/json"
    )(get_themes_resource)
    
    mcp.resource(
        uri="mermaid://themes/{theme_name}",
        name="Theme Details",
        description="Detailed information about a specific theme",
        mimeType="application/json"
    )(get_theme_details)
    
    # Template resources
    mcp.resource(
        uri="mermaid://templates",
        name="Available Templates",
        description="List of all available diagram templates",
        mimeType="application/json"
    )(get_templates_resource)
    
    mcp.resource(
        uri="mermaid://templates/{template_name}",
        name="Template Details",
        description="Detailed information about a specific template",
        mimeType="application/json"
    )(get_template_details)
    
    # Configuration resources
    mcp.resource(
        uri="mermaid://config/schema",
        name="Configuration Schema",
        description="JSON schema for mermaid-render configuration",
        mimeType="application/json"
    )(get_config_schema)
    
    mcp.resource(
        uri="mermaid://config/defaults",
        name="Default Configuration",
        description="Default configuration values",
        mimeType="application/json"
    )(get_default_config)
    
    # Documentation resources
    mcp.resource(
        uri="mermaid://docs/diagram-types",
        name="Diagram Types",
        description="Documentation for all supported diagram types",
        mimeType="application/json"
    )(get_diagram_types_docs)
    
    mcp.resource(
        uri="mermaid://examples/{diagram_type}",
        name="Diagram Examples",
        description="Example diagrams for each type",
        mimeType="application/json"
    )(get_diagram_examples)
    
    logger.info("Registered all MCP resources")


async def get_themes_resource(ctx: Context) -> str:
    """
    Get all available themes resource.
    
    Args:
        ctx: MCP context
        
    Returns:
        JSON string containing themes data
    """
    try:
        # Get themes from theme manager
        themes_data = {
            "themes": {
                "default": {
                    "name": "default",
                    "description": "Default theme with light background",
                    "colors": {
                        "primary": "#0066cc",
                        "secondary": "#ffffff",
                        "background": "#ffffff"
                    }
                },
                "dark": {
                    "name": "dark",
                    "description": "Dark theme with dark background",
                    "colors": {
                        "primary": "#58a6ff",
                        "secondary": "#f0f6fc",
                        "background": "#0d1117"
                    }
                },
                "forest": {
                    "name": "forest",
                    "description": "Forest theme with green colors",
                    "colors": {
                        "primary": "#1f7a1f",
                        "secondary": "#ffffff",
                        "background": "#f0fff0"
                    }
                },
                "neutral": {
                    "name": "neutral",
                    "description": "Neutral theme with gray colors",
                    "colors": {
                        "primary": "#666666",
                        "secondary": "#ffffff",
                        "background": "#f8f9fa"
                    }
                },
                "base": {
                    "name": "base",
                    "description": "Base theme with minimal styling",
                    "colors": {
                        "primary": "#000000",
                        "secondary": "#ffffff",
                        "background": "#ffffff"
                    }
                }
            },
            "default_theme": "default",
            "total_count": 5,
            "custom_themes_supported": True
        }
        
        return json.dumps(themes_data, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting themes resource: {e}")
        raise ResourceError(f"Failed to get themes: {e}")


async def get_theme_details(ctx: Context, theme_name: str) -> str:
    """
    Get details for a specific theme.
    
    Args:
        ctx: MCP context
        theme_name: Name of the theme
        
    Returns:
        JSON string containing theme details
    """
    try:
        # Theme details mapping
        theme_details = {
            "default": {
                "name": "default",
                "description": "Default theme with light background and blue accents",
                "colors": {
                    "primary": "#0066cc",
                    "secondary": "#ffffff",
                    "background": "#ffffff",
                    "text": "#000000",
                    "border": "#cccccc"
                },
                "usage": "Best for general purpose diagrams and documentation",
                "compatibility": "All diagram types"
            },
            "dark": {
                "name": "dark",
                "description": "Dark theme optimized for dark mode interfaces",
                "colors": {
                    "primary": "#58a6ff",
                    "secondary": "#f0f6fc",
                    "background": "#0d1117",
                    "text": "#f0f6fc",
                    "border": "#30363d"
                },
                "usage": "Ideal for dark mode applications and presentations",
                "compatibility": "All diagram types"
            },
            "forest": {
                "name": "forest",
                "description": "Nature-inspired theme with green color palette",
                "colors": {
                    "primary": "#1f7a1f",
                    "secondary": "#ffffff",
                    "background": "#f0fff0",
                    "text": "#000000",
                    "border": "#90ee90"
                },
                "usage": "Great for environmental, growth, or nature-related diagrams",
                "compatibility": "All diagram types"
            },
            "neutral": {
                "name": "neutral",
                "description": "Professional neutral theme with gray tones",
                "colors": {
                    "primary": "#666666",
                    "secondary": "#ffffff",
                    "background": "#f8f9fa",
                    "text": "#000000",
                    "border": "#dee2e6"
                },
                "usage": "Perfect for business and professional documentation",
                "compatibility": "All diagram types"
            },
            "base": {
                "name": "base",
                "description": "Minimal base theme with basic styling",
                "colors": {
                    "primary": "#000000",
                    "secondary": "#ffffff",
                    "background": "#ffffff",
                    "text": "#000000",
                    "border": "#000000"
                },
                "usage": "Minimal styling for custom theme development",
                "compatibility": "All diagram types"
            }
        }
        
        if theme_name not in theme_details:
            raise ResourceError(f"Theme '{theme_name}' not found")
        
        return json.dumps(theme_details[theme_name], indent=2)
        
    except Exception as e:
        logger.error(f"Error getting theme details for {theme_name}: {e}")
        raise ResourceError(f"Failed to get theme details: {e}")


async def get_templates_resource(ctx: Context) -> str:
    """
    Get all available templates resource.
    
    Args:
        ctx: MCP context
        
    Returns:
        JSON string containing templates data
    """
    try:
        # Check if templates module is available
        try:
            from ..templates import TemplateManager
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
                        "created_at": template.created_at.isoformat() if template.created_at else None,
                        "parameters": template.parameters
                    }
                    for template in templates
                ],
                "total_count": len(templates),
                "builtin_count": len([t for t in templates if t.author == "mermaid-render"]),
                "custom_count": len([t for t in templates if t.author != "mermaid-render"])
            }
            
        except ImportError:
            templates_data = {
                "templates": [],
                "total_count": 0,
                "builtin_count": 0,
                "custom_count": 0,
                "error": "Template functionality not available. Install with: pip install mermaid-render[templates]"
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
        # Check if templates module is available
        try:
            from ..templates import TemplateManager
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
                "created_at": template.created_at.isoformat() if template.created_at else None,
                "updated_at": template.updated_at.isoformat() if template.updated_at else None,
                "usage_examples": template.metadata.get("examples", []) if template.metadata else []
            }

        except ImportError:
            raise ResourceError("Template functionality not available. Install with: pip install mermaid-render[templates]")

        return json.dumps(template_data, indent=2)

    except Exception as e:
        logger.error(f"Error getting template details for {template_name}: {e}")
        raise ResourceError(f"Failed to get template details: {e}")


async def get_config_schema(ctx: Context) -> str:
    """
    Get configuration schema resource.

    Args:
        ctx: MCP context

    Returns:
        JSON string containing configuration schema
    """
    try:
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Mermaid Render Configuration",
            "type": "object",
            "properties": {
                "server_url": {
                    "type": "string",
                    "description": "Mermaid.ink server URL",
                    "default": "https://mermaid.ink"
                },
                "timeout": {
                    "type": "number",
                    "description": "Request timeout in seconds",
                    "default": 30.0,
                    "minimum": 1,
                    "maximum": 300
                },
                "retries": {
                    "type": "integer",
                    "description": "Number of retry attempts",
                    "default": 3,
                    "minimum": 0,
                    "maximum": 10
                },
                "default_theme": {
                    "type": "string",
                    "description": "Default theme name",
                    "default": "default",
                    "enum": ["default", "dark", "forest", "neutral", "base"]
                },
                "default_format": {
                    "type": "string",
                    "description": "Default output format",
                    "default": "svg",
                    "enum": ["svg", "png", "pdf"]
                },
                "validate_syntax": {
                    "type": "boolean",
                    "description": "Enable syntax validation",
                    "default": True
                },
                "cache_enabled": {
                    "type": "boolean",
                    "description": "Enable caching",
                    "default": True
                },
                "cache_dir": {
                    "type": "string",
                    "description": "Cache directory path",
                    "default": "~/.mermaid_render_cache"
                },
                "max_cache_size": {
                    "type": "integer",
                    "description": "Maximum cache size in MB",
                    "default": 100,
                    "minimum": 1,
                    "maximum": 10000
                },
                "cache_ttl": {
                    "type": "integer",
                    "description": "Cache TTL in seconds",
                    "default": 3600,
                    "minimum": 60,
                    "maximum": 86400
                },
                "default_width": {
                    "type": "integer",
                    "description": "Default output width in pixels",
                    "default": 800,
                    "minimum": 100,
                    "maximum": 4000
                },
                "default_height": {
                    "type": "integer",
                    "description": "Default output height in pixels",
                    "default": 600,
                    "minimum": 100,
                    "maximum": 4000
                },
                "use_local_rendering": {
                    "type": "boolean",
                    "description": "Use local rendering when available",
                    "default": True
                },
                "log_level": {
                    "type": "string",
                    "description": "Logging level",
                    "default": "INFO",
                    "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
                }
            }
        }

        return json.dumps(schema, indent=2)

    except Exception as e:
        logger.error(f"Error getting config schema: {e}")
        raise ResourceError(f"Failed to get config schema: {e}")


async def get_default_config(ctx: Context) -> str:
    """
    Get default configuration resource.

    Args:
        ctx: MCP context

    Returns:
        JSON string containing default configuration
    """
    try:
        from ..core import MermaidConfig

        config = MermaidConfig()
        default_config = config.to_dict()

        return json.dumps(default_config, indent=2)

    except Exception as e:
        logger.error(f"Error getting default config: {e}")
        raise ResourceError(f"Failed to get default config: {e}")


async def get_diagram_types_docs(ctx: Context) -> str:
    """
    Get diagram types documentation resource.

    Args:
        ctx: MCP context

    Returns:
        JSON string containing diagram types documentation
    """
    try:
        diagram_types = {
            "flowchart": {
                "name": "Flowchart",
                "description": "Flowcharts show the flow of a process or algorithm",
                "syntax": "flowchart TD\n    A[Start] --> B{Decision}\n    B -->|Yes| C[Process]\n    B -->|No| D[End]",
                "keywords": ["flowchart", "graph"],
                "directions": ["TD", "TB", "BT", "RL", "LR"],
                "node_types": ["rectangle", "rounded", "circle", "rhombus", "hexagon", "parallelogram"],
                "use_cases": ["Process flows", "Decision trees", "Algorithms", "Workflows"]
            },
            "sequence": {
                "name": "Sequence Diagram",
                "description": "Sequence diagrams show interactions between participants over time",
                "syntax": "sequenceDiagram\n    participant A\n    participant B\n    A->>B: Message\n    B-->>A: Response",
                "keywords": ["sequenceDiagram"],
                "elements": ["participant", "actor", "note", "loop", "alt", "opt"],
                "arrow_types": ["->", "->>", "-->>", "-x", "--x"],
                "use_cases": ["API interactions", "System communications", "User flows", "Protocol diagrams"]
            },
            "class": {
                "name": "Class Diagram",
                "description": "Class diagrams show the structure of classes and their relationships",
                "syntax": "classDiagram\n    class Animal {\n        +name: string\n        +makeSound()\n    }\n    Animal <|-- Dog",
                "keywords": ["classDiagram"],
                "relationships": ["inheritance", "composition", "aggregation", "association"],
                "visibility": ["public (+)", "private (-)", "protected (#)", "package (~)"],
                "use_cases": ["Object-oriented design", "Database schemas", "System architecture", "Code documentation"]
            },
            "state": {
                "name": "State Diagram",
                "description": "State diagrams show the states of a system and transitions between them",
                "syntax": "stateDiagram-v2\n    [*] --> Still\n    Still --> [*]\n    Still --> Moving\n    Moving --> Still",
                "keywords": ["stateDiagram", "stateDiagram-v2"],
                "elements": ["state", "transition", "choice", "fork", "join"],
                "use_cases": ["State machines", "Workflow states", "System behavior", "Protocol states"]
            },
            "er": {
                "name": "Entity Relationship Diagram",
                "description": "ER diagrams show relationships between entities in a database",
                "syntax": "erDiagram\n    CUSTOMER {\n        string name\n        string email\n    }\n    ORDER {\n        int id\n        date created\n    }\n    CUSTOMER ||--o{ ORDER : places",
                "keywords": ["erDiagram"],
                "relationships": ["one-to-one", "one-to-many", "many-to-many"],
                "cardinality": ["||--||", "||--o{", "}o--||", "}o--o{"],
                "use_cases": ["Database design", "Data modeling", "System architecture", "Documentation"]
            },
            "journey": {
                "name": "User Journey",
                "description": "User journey diagrams show user experiences and touchpoints",
                "syntax": "journey\n    title My working day\n    section Go to work\n      Make tea: 5: Me\n      Go upstairs: 3: Me",
                "keywords": ["journey"],
                "elements": ["title", "section", "task"],
                "use_cases": ["User experience design", "Customer journey mapping", "Process improvement", "Service design"]
            },
            "gantt": {
                "name": "Gantt Chart",
                "description": "Gantt charts show project schedules and task dependencies",
                "syntax": "gantt\n    title Project Timeline\n    dateFormat YYYY-MM-DD\n    section Planning\n    Task 1: 2023-01-01, 30d",
                "keywords": ["gantt"],
                "elements": ["title", "dateFormat", "section", "task"],
                "use_cases": ["Project management", "Timeline planning", "Resource allocation", "Progress tracking"]
            },
            "pie": {
                "name": "Pie Chart",
                "description": "Pie charts show proportional data as slices of a circle",
                "syntax": "pie title Survey Results\n    \"Option A\" : 42\n    \"Option B\" : 30\n    \"Option C\" : 28",
                "keywords": ["pie"],
                "elements": ["title", "data"],
                "use_cases": ["Data visualization", "Survey results", "Market share", "Budget allocation"]
            },
            "gitgraph": {
                "name": "Git Graph",
                "description": "Git graphs show branching and merging in version control",
                "syntax": "gitgraph\n    commit\n    branch develop\n    checkout develop\n    commit\n    checkout main\n    merge develop",
                "keywords": ["gitgraph"],
                "elements": ["commit", "branch", "checkout", "merge"],
                "use_cases": ["Version control visualization", "Release planning", "Development workflows", "Code review"]
            },
            "mindmap": {
                "name": "Mind Map",
                "description": "Mind maps show hierarchical information radiating from a central topic",
                "syntax": "mindmap\n  root((Central Topic))\n    Branch 1\n      Sub-branch 1\n      Sub-branch 2\n    Branch 2",
                "keywords": ["mindmap"],
                "elements": ["root", "branch", "sub-branch"],
                "use_cases": ["Brainstorming", "Knowledge organization", "Planning", "Learning"]
            }
        }

        return json.dumps(diagram_types, indent=2)

    except Exception as e:
        logger.error(f"Error getting diagram types docs: {e}")
        raise ResourceError(f"Failed to get diagram types docs: {e}")


async def get_diagram_examples(ctx: Context, diagram_type: str) -> str:
    """
    Get examples for a specific diagram type.

    Args:
        ctx: MCP context
        diagram_type: Type of diagram

    Returns:
        JSON string containing diagram examples
    """
    try:
        examples = {
            "flowchart": [
                {
                    "title": "Simple Process Flow",
                    "description": "Basic flowchart showing a simple process",
                    "code": "flowchart TD\n    A[Start] --> B{Is it working?}\n    B -->|Yes| C[Great!]\n    B -->|No| D[Fix it]\n    D --> B\n    C --> E[End]"
                },
                {
                    "title": "Decision Tree",
                    "description": "Flowchart representing a decision-making process",
                    "code": "flowchart LR\n    A[Problem] --> B{Can we solve it?}\n    B -->|Yes| C[Solve it]\n    B -->|No| D{Can we learn from it?}\n    D -->|Yes| E[Learn from it]\n    D -->|No| F[Let it go]\n    C --> G[Success]\n    E --> G\n    F --> G"
                }
            ],
            "sequence": [
                {
                    "title": "API Authentication",
                    "description": "Sequence diagram showing API authentication flow",
                    "code": "sequenceDiagram\n    participant C as Client\n    participant A as Auth Server\n    participant R as Resource Server\n    \n    C->>A: Login Request\n    A-->>C: Access Token\n    C->>R: API Request + Token\n    R->>A: Validate Token\n    A-->>R: Token Valid\n    R-->>C: API Response"
                }
            ],
            "class": [
                {
                    "title": "Animal Hierarchy",
                    "description": "Class diagram showing inheritance",
                    "code": "classDiagram\n    class Animal {\n        +String name\n        +int age\n        +makeSound()\n        +move()\n    }\n    \n    class Dog {\n        +String breed\n        +bark()\n    }\n    \n    class Cat {\n        +boolean indoor\n        +meow()\n    }\n    \n    Animal <|-- Dog\n    Animal <|-- Cat"
                }
            ]
        }

        if diagram_type not in examples:
            raise ResourceError(f"No examples found for diagram type '{diagram_type}'")

        return json.dumps({
            "diagram_type": diagram_type,
            "examples": examples[diagram_type]
        }, indent=2)

    except Exception as e:
        logger.error(f"Error getting diagram examples for {diagram_type}: {e}")
        raise ResourceError(f"Failed to get diagram examples: {e}")
