"""
Extended MCP resources for diagramaid.

This module provides additional resources for syntax references,
best practices, capabilities, and other documentation.
"""

import json

from .base import Context, ResourceError, logger


async def get_syntax_reference(ctx: Context, diagram_type: str) -> str:
    """
    Get syntax reference for a specific diagram type.

    Args:
        ctx: MCP context
        diagram_type: Type of diagram (flowchart, sequence, class, etc.)

    Returns:
        JSON string containing syntax reference
    """
    try:
        syntax_references = {
            "flowchart": {
                "name": "Flowchart",
                "declaration": ["flowchart TD", "flowchart LR", "flowchart TB", "flowchart BT", "flowchart RL", "graph TD"],
                "directions": {
                    "TD": "Top to Down",
                    "TB": "Top to Bottom (same as TD)",
                    "BT": "Bottom to Top",
                    "LR": "Left to Right",
                    "RL": "Right to Left",
                },
                "node_shapes": {
                    "A[text]": "Rectangle",
                    "A(text)": "Rounded rectangle",
                    "A([text])": "Stadium-shaped",
                    "A[[text]]": "Subroutine",
                    "A[(text)]": "Cylindrical (database)",
                    "A((text))": "Circle",
                    "A>text]": "Asymmetric",
                    "A{text}": "Rhombus (decision)",
                    "A{{text}}": "Hexagon",
                    "A[/text/]": "Parallelogram",
                    "A[\\text\\]": "Parallelogram alt",
                    "A[/text\\]": "Trapezoid",
                    "A[\\text/]": "Trapezoid alt",
                },
                "link_types": {
                    "-->": "Arrow",
                    "---": "Open link",
                    "-.->": "Dotted arrow",
                    "==>": "Thick arrow",
                    "--o": "Circle end",
                    "--x": "Cross end",
                    "<-->": "Multi-directional",
                },
                "link_labels": {
                    "A-->|text|B": "Arrow with text",
                    "A-- text -->B": "Alternative syntax",
                },
                "subgraphs": {
                    "syntax": "subgraph title\\n    content\\nend",
                    "with_id": "subgraph id[title]\\n    content\\nend",
                    "direction": "subgraph id\\n    direction TB\\n    content\\nend",
                },
                "styling": {
                    "node_style": "style A fill:#f9f,stroke:#333,stroke-width:4px",
                    "class_def": "classDef className fill:#f9f,stroke:#333",
                    "class_apply": "class A,B className",
                },
                "examples": [
                    "flowchart TD\\n    A[Start] --> B{Decision}\\n    B -->|Yes| C[OK]\\n    B -->|No| D[End]",
                ],
            },
            "sequence": {
                "name": "Sequence Diagram",
                "declaration": ["sequenceDiagram"],
                "participants": {
                    "participant": "participant A",
                    "actor": "actor A",
                    "with_alias": "participant A as Alice",
                },
                "messages": {
                    "->": "Solid line without arrow",
                    "-->": "Dotted line without arrow",
                    "->>": "Solid line with arrow",
                    "-->>": "Dotted line with arrow",
                    "-x": "Solid line with cross",
                    "--x": "Dotted line with cross",
                    "-)": "Solid line with open arrow (async)",
                    "--)": "Dotted line with open arrow (async)",
                },
                "activation": {
                    "activate": "activate A",
                    "deactivate": "deactivate A",
                    "shorthand": "A->>+B: message (activate B)",
                    "shorthand_deactivate": "B-->>-A: response (deactivate B)",
                },
                "notes": {
                    "right_of": "Note right of A: text",
                    "left_of": "Note left of A: text",
                    "over": "Note over A: text",
                    "over_multiple": "Note over A,B: text",
                },
                "loops": {
                    "loop": "loop description\\n    content\\nend",
                    "alt": "alt description\\n    content\\nelse other\\n    content\\nend",
                    "opt": "opt description\\n    content\\nend",
                    "par": "par description\\n    content\\nand other\\n    content\\nend",
                    "critical": "critical description\\n    content\\noption other\\n    content\\nend",
                    "break": "break description\\n    content\\nend",
                },
                "examples": [
                    "sequenceDiagram\\n    participant A\\n    participant B\\n    A->>B: Hello\\n    B-->>A: Hi!",
                ],
            },
            "class": {
                "name": "Class Diagram",
                "declaration": ["classDiagram"],
                "class_definition": {
                    "basic": "class ClassName",
                    "with_members": "class ClassName {\\n    +attribute\\n    +method()\\n}",
                    "generic": "class ClassName~T~",
                },
                "visibility": {
                    "+": "Public",
                    "-": "Private",
                    "#": "Protected",
                    "~": "Package/Internal",
                },
                "relationships": {
                    "<|--": "Inheritance",
                    "*--": "Composition",
                    "o--": "Aggregation",
                    "-->": "Association",
                    "--": "Link (solid)",
                    "..>": "Dependency",
                    "..|>": "Realization",
                    "..": "Link (dashed)",
                },
                "cardinality": {
                    "1": "Only 1",
                    "0..1": "Zero or One",
                    "1..*": "One or more",
                    "*": "Many",
                    "n": "n (where n>1)",
                    "0..n": "Zero to n",
                    "1..n": "One to n",
                },
                "annotations": {
                    "<<interface>>": "Interface",
                    "<<abstract>>": "Abstract class",
                    "<<service>>": "Service",
                    "<<enumeration>>": "Enumeration",
                },
                "examples": [
                    "classDiagram\\n    class Animal {\\n        +name: string\\n        +makeSound()\\n    }\\n    class Dog\\n    Animal <|-- Dog",
                ],
            },
            "state": {
                "name": "State Diagram",
                "declaration": ["stateDiagram-v2", "stateDiagram"],
                "states": {
                    "simple": "state_name",
                    "with_description": "state \"Description\" as state_name",
                    "initial": "[*]",
                    "final": "[*]",
                },
                "transitions": {
                    "basic": "s1 --> s2",
                    "with_label": "s1 --> s2 : event",
                },
                "composite_states": {
                    "syntax": "state CompositeState {\\n    [*] --> inner1\\n    inner1 --> inner2\\n}",
                },
                "choice": {
                    "syntax": "state choice <<choice>>\\ns1 --> choice\\nchoice --> s2 : if condition\\nchoice --> s3 : else",
                },
                "fork_join": {
                    "fork": "state fork <<fork>>",
                    "join": "state join <<join>>",
                },
                "notes": {
                    "syntax": "note right of state_name\\n    note text\\nend note",
                },
                "examples": [
                    "stateDiagram-v2\\n    [*] --> Idle\\n    Idle --> Processing : start\\n    Processing --> Done : complete\\n    Done --> [*]",
                ],
            },
            "er": {
                "name": "Entity Relationship Diagram",
                "declaration": ["erDiagram"],
                "entities": {
                    "basic": "ENTITY_NAME",
                    "with_attributes": "ENTITY_NAME {\\n    type attribute_name\\n}",
                },
                "attribute_types": ["string", "int", "float", "date", "datetime", "boolean"],
                "attribute_keys": {
                    "PK": "Primary Key",
                    "FK": "Foreign Key",
                    "UK": "Unique Key",
                },
                "relationships": {
                    "||--||": "One to one",
                    "||--o{": "One to many",
                    "}o--||": "Many to one",
                    "}o--o{": "Many to many",
                    "||--o|": "One to zero or one",
                    "|o--o{": "Zero or one to many",
                },
                "relationship_labels": {
                    "syntax": "ENTITY1 ||--o{ ENTITY2 : \"relationship_name\"",
                },
                "examples": [
                    "erDiagram\\n    CUSTOMER ||--o{ ORDER : places\\n    ORDER ||--|{ LINE-ITEM : contains",
                ],
            },
            "gantt": {
                "name": "Gantt Chart",
                "declaration": ["gantt"],
                "configuration": {
                    "title": "title Chart Title",
                    "dateFormat": "dateFormat YYYY-MM-DD",
                    "axisFormat": "axisFormat %Y-%m-%d",
                    "excludes": "excludes weekends",
                },
                "sections": {
                    "syntax": "section Section Name",
                },
                "tasks": {
                    "basic": "Task name : task_id, start_date, duration",
                    "after": "Task name : task_id, after prev_task, duration",
                    "active": "Task name : active, task_id, start_date, duration",
                    "done": "Task name : done, task_id, start_date, duration",
                    "crit": "Task name : crit, task_id, start_date, duration",
                    "milestone": "Milestone : milestone, m1, start_date, 0d",
                },
                "duration_formats": ["1d", "1w", "1h", "2024-01-15"],
                "examples": [
                    "gantt\\n    title Project\\n    dateFormat YYYY-MM-DD\\n    section Phase 1\\n    Task 1 : a1, 2024-01-01, 5d\\n    Task 2 : a2, after a1, 3d",
                ],
            },
            "pie": {
                "name": "Pie Chart",
                "declaration": ["pie"],
                "configuration": {
                    "title": "pie title Chart Title",
                    "showData": "pie showData",
                },
                "data": {
                    "syntax": "\"Label\" : value",
                },
                "examples": [
                    "pie title Distribution\\n    \"A\" : 42\\n    \"B\" : 30\\n    \"C\" : 28",
                ],
            },
            "mindmap": {
                "name": "Mind Map",
                "declaration": ["mindmap"],
                "root": {
                    "default": "root((Central Topic))",
                    "square": "root[Central Topic]",
                    "rounded": "root(Central Topic)",
                },
                "branches": {
                    "syntax": "Use indentation for hierarchy",
                    "shapes": {
                        "default": "Branch text",
                        "square": "[Branch text]",
                        "rounded": "(Branch text)",
                        "circle": "((Branch text))",
                        "cloud": ")Branch text(",
                        "hexagon": "{{Branch text}}",
                    },
                },
                "icons": {
                    "syntax": "::icon(fa fa-icon-name)",
                },
                "examples": [
                    "mindmap\\n  root((Topic))\\n    Branch 1\\n      Sub 1\\n    Branch 2",
                ],
            },
            "timeline": {
                "name": "Timeline",
                "declaration": ["timeline"],
                "configuration": {
                    "title": "title Timeline Title",
                },
                "events": {
                    "basic": "period : event",
                    "with_description": "period : event\\n         : description",
                },
                "sections": {
                    "syntax": "section Section Name",
                },
                "examples": [
                    "timeline\\n    title History\\n    2020 : Event 1\\n    2021 : Event 2\\n         : Details",
                ],
            },
            "gitgraph": {
                "name": "Git Graph",
                "declaration": ["gitgraph"],
                "commands": {
                    "commit": "commit",
                    "commit_with_id": "commit id: \"message\"",
                    "commit_with_tag": "commit tag: \"v1.0\"",
                    "branch": "branch branch_name",
                    "checkout": "checkout branch_name",
                    "merge": "merge branch_name",
                    "cherry_pick": "cherry-pick id: \"commit_id\"",
                },
                "configuration": {
                    "theme": "%%{init: { 'theme': 'base' }}%%",
                },
                "examples": [
                    "gitgraph\\n    commit\\n    branch develop\\n    checkout develop\\n    commit\\n    checkout main\\n    merge develop",
                ],
            },
        }

        if diagram_type not in syntax_references:
            raise ResourceError(f"Syntax reference for '{diagram_type}' not found")

        return json.dumps(syntax_references[diagram_type], indent=2)

    except Exception as e:
        logger.error(f"Error getting syntax reference for {diagram_type}: {e}")
        raise ResourceError(f"Failed to get syntax reference: {e}")


async def get_best_practices(ctx: Context) -> str:
    """
    Get best practices for creating Mermaid diagrams.

    Args:
        ctx: MCP context

    Returns:
        JSON string containing best practices
    """
    try:
        best_practices = {
            "general": {
                "title": "General Best Practices",
                "practices": [
                    {
                        "name": "Keep it Simple",
                        "description": "Start with simple diagrams and add complexity as needed",
                        "tips": [
                            "Limit nodes to 15-20 per diagram",
                            "Break complex diagrams into multiple views",
                            "Use subgraphs to organize related elements",
                        ],
                    },
                    {
                        "name": "Use Clear Labels",
                        "description": "Labels should be descriptive but concise",
                        "tips": [
                            "Use action verbs for process steps",
                            "Avoid abbreviations unless well-known",
                            "Keep labels under 30 characters",
                        ],
                    },
                    {
                        "name": "Consistent Styling",
                        "description": "Apply consistent styles throughout the diagram",
                        "tips": [
                            "Use the same shapes for similar elements",
                            "Apply consistent color schemes",
                            "Use classDef for reusable styles",
                        ],
                    },
                    {
                        "name": "Logical Flow",
                        "description": "Arrange elements in a logical reading order",
                        "tips": [
                            "Use TD for hierarchical data",
                            "Use LR for process flows",
                            "Minimize crossing lines",
                        ],
                    },
                ],
            },
            "flowchart": {
                "title": "Flowchart Best Practices",
                "practices": [
                    {
                        "name": "Shape Conventions",
                        "description": "Use standard shapes for their intended purposes",
                        "tips": [
                            "Rectangles for processes/actions",
                            "Diamonds for decisions",
                            "Rounded rectangles for start/end",
                            "Parallelograms for input/output",
                        ],
                    },
                    {
                        "name": "Decision Points",
                        "description": "Make decision points clear and complete",
                        "tips": [
                            "Label all branches (Yes/No, True/False)",
                            "Ensure all paths lead somewhere",
                            "Avoid more than 3 branches from one decision",
                        ],
                    },
                ],
            },
            "sequence": {
                "title": "Sequence Diagram Best Practices",
                "practices": [
                    {
                        "name": "Participant Order",
                        "description": "Order participants logically",
                        "tips": [
                            "Place initiator on the left",
                            "Group related participants",
                            "Minimize message crossings",
                        ],
                    },
                    {
                        "name": "Message Clarity",
                        "description": "Make messages clear and actionable",
                        "tips": [
                            "Use verb phrases for messages",
                            "Show return values explicitly",
                            "Use activation boxes for long operations",
                        ],
                    },
                ],
            },
            "class": {
                "title": "Class Diagram Best Practices",
                "practices": [
                    {
                        "name": "Abstraction Level",
                        "description": "Choose appropriate level of detail",
                        "tips": [
                            "Show only relevant attributes/methods",
                            "Use visibility modifiers consistently",
                            "Group related classes together",
                        ],
                    },
                    {
                        "name": "Relationships",
                        "description": "Use correct relationship types",
                        "tips": [
                            "Inheritance for 'is-a' relationships",
                            "Composition for 'has-a' (strong)",
                            "Aggregation for 'has-a' (weak)",
                            "Association for 'uses'",
                        ],
                    },
                ],
            },
            "accessibility": {
                "title": "Accessibility Best Practices",
                "practices": [
                    {
                        "name": "Color Contrast",
                        "description": "Ensure sufficient color contrast",
                        "tips": [
                            "Don't rely solely on color to convey meaning",
                            "Use patterns or labels in addition to colors",
                            "Test with color blindness simulators",
                        ],
                    },
                    {
                        "name": "Text Alternatives",
                        "description": "Provide text descriptions",
                        "tips": [
                            "Add alt text when embedding diagrams",
                            "Include a text summary of the diagram",
                            "Use descriptive titles",
                        ],
                    },
                ],
            },
            "performance": {
                "title": "Performance Best Practices",
                "practices": [
                    {
                        "name": "Diagram Size",
                        "description": "Keep diagrams reasonably sized",
                        "tips": [
                            "Limit to 50 nodes maximum",
                            "Split large diagrams into multiple views",
                            "Use SVG format for scalability",
                        ],
                    },
                    {
                        "name": "Rendering Optimization",
                        "description": "Optimize for faster rendering",
                        "tips": [
                            "Avoid complex styling when not needed",
                            "Use simple shapes over custom ones",
                            "Cache rendered diagrams when possible",
                        ],
                    },
                ],
            },
        }

        return json.dumps(best_practices, indent=2)

    except Exception as e:
        logger.error(f"Error getting best practices: {e}")
        raise ResourceError(f"Failed to get best practices: {e}")


async def get_capabilities(ctx: Context) -> str:
    """
    Get server capabilities and features.

    Args:
        ctx: MCP context

    Returns:
        JSON string containing server capabilities
    """
    try:
        capabilities = {
            "server": {
                "name": "diagramaid",
                "version": "1.0.0",
                "protocol": "MCP",
                "transports": ["stdio", "sse", "websocket"],
            },
            "diagram_types": {
                "supported": [
                    "flowchart",
                    "sequence",
                    "class",
                    "state",
                    "er",
                    "gantt",
                    "pie",
                    "journey",
                    "gitgraph",
                    "mindmap",
                    "timeline",
                    "quadrant",
                    "requirement",
                    "c4",
                ],
                "experimental": ["zenuml", "sankey"],
            },
            "output_formats": {
                "supported": ["svg", "png", "pdf"],
                "default": "svg",
                "features": {
                    "svg": ["scalable", "editable", "small_size"],
                    "png": ["raster", "universal_support"],
                    "pdf": ["print_ready", "vector"],
                },
            },
            "themes": {
                "builtin": ["default", "dark", "forest", "neutral", "base"],
                "custom_support": True,
            },
            "tools": {
                "core": [
                    "render_diagram",
                    "validate_diagram",
                    "list_themes",
                ],
                "ai_powered": [
                    "generate_diagram_from_text",
                    "optimize_diagram",
                    "analyze_diagram",
                    "get_diagram_suggestions",
                ],
                "templates": [
                    "create_from_template",
                    "list_available_templates",
                    "get_template_details",
                    "create_custom_template",
                ],
                "extended": [
                    "convert_diagram_format",
                    "merge_diagrams",
                    "extract_diagram_elements",
                    "compare_diagrams",
                    "export_to_markdown",
                    "transform_diagram_style",
                    "generate_diagram_variants",
                ],
                "management": [
                    "get_configuration",
                    "update_configuration",
                    "get_system_information",
                    "save_diagram_to_file",
                    "batch_render_diagrams",
                    "manage_cache_operations",
                ],
            },
            "prompts": {
                "generation": [
                    "generate_flowchart",
                    "generate_sequence",
                    "generate_class_diagram",
                    "generate_er_diagram",
                    "generate_state_diagram",
                    "generate_gantt_chart",
                    "generate_mindmap",
                    "generate_timeline",
                    "generate_pie_chart",
                    "generate_git_graph",
                    "generate_c4_diagram",
                ],
                "analysis": [
                    "analyze_diagram_quality",
                    "suggest_improvements",
                ],
                "optimization": [
                    "optimize_layout",
                    "simplify_diagram",
                    "refactor_diagram",
                ],
                "documentation": [
                    "explain_diagram",
                    "create_diagram_documentation",
                    "document_architecture",
                ],
                "transformation": [
                    "translate_diagram",
                    "convert_to_diagram",
                ],
            },
            "resources": {
                "themes": ["mermaid://themes", "mermaid://themes/{theme_name}"],
                "templates": ["mermaid://templates", "mermaid://templates/{template_name}"],
                "config": ["mermaid://config/schema", "mermaid://config/defaults"],
                "docs": ["mermaid://docs/diagram-types", "mermaid://examples/{diagram_type}"],
                "extended": [
                    "mermaid://syntax/{diagram_type}",
                    "mermaid://best-practices",
                    "mermaid://capabilities",
                    "mermaid://changelog",
                ],
            },
            "features": {
                "ai_support": {
                    "available": True,
                    "providers": ["openai", "anthropic"],
                    "requires_api_key": True,
                },
                "caching": {
                    "available": True,
                    "backends": ["memory", "disk", "redis"],
                },
                "batch_processing": {
                    "available": True,
                    "max_diagrams": 50,
                    "parallel_support": True,
                },
                "validation": {
                    "syntax_check": True,
                    "structure_analysis": True,
                    "quality_scoring": True,
                },
            },
            "limits": {
                "max_diagram_size": "50KB",
                "max_nodes": 500,
                "max_batch_size": 50,
                "timeout_seconds": 30,
            },
        }

        return json.dumps(capabilities, indent=2)

    except Exception as e:
        logger.error(f"Error getting capabilities: {e}")
        raise ResourceError(f"Failed to get capabilities: {e}")


async def get_changelog(ctx: Context) -> str:
    """
    Get version changelog.

    Args:
        ctx: MCP context

    Returns:
        JSON string containing changelog
    """
    try:
        changelog = {
            "current_version": "1.0.0",
            "releases": [
                {
                    "version": "1.0.0",
                    "date": "2024-01-01",
                    "changes": {
                        "added": [
                            "Full MCP server implementation",
                            "19 core tools for diagram operations",
                            "9 built-in prompts for diagram generation",
                            "8 resource endpoints for documentation",
                            "Extended tools for advanced operations",
                            "Extended prompts for all diagram types",
                            "Multi-transport support (stdio, SSE, WebSocket)",
                            "AI-powered diagram generation and analysis",
                            "Template system with custom templates",
                            "Batch processing support",
                            "Cache management",
                        ],
                        "improved": [
                            "Error handling with detailed messages",
                            "Performance metrics for all operations",
                            "Validation with quality scoring",
                        ],
                        "fixed": [],
                    },
                },
            ],
            "upcoming": {
                "version": "1.1.0",
                "planned_features": [
                    "Additional diagram type support",
                    "Enhanced AI capabilities",
                    "Plugin system for custom renderers",
                    "Real-time collaboration features",
                ],
            },
        }

        return json.dumps(changelog, indent=2)

    except Exception as e:
        logger.error(f"Error getting changelog: {e}")
        raise ResourceError(f"Failed to get changelog: {e}")


async def get_shortcuts_reference(ctx: Context) -> str:
    """
    Get quick reference for common diagram patterns.

    Args:
        ctx: MCP context

    Returns:
        JSON string containing shortcuts reference
    """
    try:
        shortcuts = {
            "quick_start": {
                "flowchart": "flowchart TD\\n    A[Start] --> B[End]",
                "sequence": "sequenceDiagram\\n    A->>B: Message",
                "class": "classDiagram\\n    class A",
                "state": "stateDiagram-v2\\n    [*] --> A",
                "er": "erDiagram\\n    A ||--o{ B : has",
                "gantt": "gantt\\n    Task : a1, 2024-01-01, 1d",
                "pie": "pie\\n    \"A\" : 50",
                "mindmap": "mindmap\\n    root((Topic))",
                "timeline": "timeline\\n    2024 : Event",
                "gitgraph": "gitgraph\\n    commit",
            },
            "common_patterns": {
                "decision_tree": """flowchart TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Action 1]
    B -->|No| D[Action 2]
    C --> E[End]
    D --> E""",
                "api_call": """sequenceDiagram
    Client->>+Server: Request
    Server-->>-Client: Response""",
                "inheritance": """classDiagram
    class Parent
    class Child
    Parent <|-- Child""",
                "state_machine": """stateDiagram-v2
    [*] --> Idle
    Idle --> Active : start
    Active --> Idle : stop
    Active --> [*] : finish""",
                "one_to_many": """erDiagram
    PARENT ||--o{ CHILD : has""",
            },
            "styling_shortcuts": {
                "colored_node": "style A fill:#f9f,stroke:#333",
                "class_definition": "classDef highlight fill:#ff0",
                "apply_class": "class A,B highlight",
                "link_style": "linkStyle 0 stroke:#ff0,stroke-width:2px",
            },
        }

        return json.dumps(shortcuts, indent=2)

    except Exception as e:
        logger.error(f"Error getting shortcuts reference: {e}")
        raise ResourceError(f"Failed to get shortcuts reference: {e}")
