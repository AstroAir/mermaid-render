"""
Helper functions for MCP tools.

This module provides shared helper functions used across multiple tool modules.
"""

import re
from collections.abc import Callable
from typing import Any


def _detect_diagram_type(diagram_code: str) -> str | None:
    """
    Detect the type of Mermaid diagram from the code.

    Args:
        diagram_code: Mermaid diagram code

    Returns:
        Detected diagram type or None
    """
    code_lower = diagram_code.lower().strip()

    if code_lower.startswith("graph"):
        return "flowchart"
    elif code_lower.startswith("flowchart"):
        return "flowchart"
    elif code_lower.startswith("sequencediagram"):
        return "sequence"
    elif code_lower.startswith("classdiagram"):
        return "class"
    elif code_lower.startswith("statediagram"):
        return "state"
    elif code_lower.startswith("erdiagram"):
        return "er"
    elif code_lower.startswith("gantt"):
        return "gantt"
    elif code_lower.startswith("pie"):
        return "pie"
    elif code_lower.startswith("journey"):
        return "user_journey"
    elif code_lower.startswith("gitgraph"):
        return "git_graph"
    elif code_lower.startswith("mindmap"):
        return "mindmap"
    elif code_lower.startswith("timeline"):
        return "timeline"

    return None


def _calculate_complexity_score(diagram_code: str) -> float:
    """
    Calculate a complexity score for the diagram.

    Args:
        diagram_code: Mermaid diagram code

    Returns:
        Complexity score from 0.0 to 10.0
    """
    lines = diagram_code.splitlines()
    non_empty_lines = [line.strip() for line in lines if line.strip()]

    # Basic metrics
    line_count = len(non_empty_lines)
    arrow_count = sum(
        line.count("-->") + line.count("->") + line.count("->>")
        for line in non_empty_lines
    )
    node_count = sum(
        1 for line in non_empty_lines if "[" in line or "(" in line or "{" in line
    )

    # Calculate complexity based on various factors
    complexity = 0.0
    complexity += min(line_count * 0.1, 3.0)  # Line count contribution (max 3.0)
    complexity += min(arrow_count * 0.2, 3.0)  # Connection complexity (max 3.0)
    complexity += min(node_count * 0.15, 2.0)  # Node complexity (max 2.0)

    # Additional complexity factors
    if "subgraph" in diagram_code.lower():
        complexity += 1.0
    if any(
        keyword in diagram_code.lower() for keyword in ["note", "class", "interface"]
    ):
        complexity += 0.5

    return min(complexity, 10.0)


def _calculate_quality_score(validation_result: Any, diagram_code: str) -> float:
    """
    Calculate a quality score for the diagram.

    Args:
        validation_result: Validation result object
        diagram_code: Mermaid diagram code

    Returns:
        Quality score from 0.0 to 10.0
    """
    if not validation_result.is_valid:
        return 0.0

    score = 10.0

    # Deduct for warnings
    score -= len(validation_result.warnings) * 0.5

    # Check for good practices
    lines = diagram_code.splitlines()
    non_empty_lines = [line.strip() for line in lines if line.strip()]

    # Deduct for very short or very long lines (readability)
    for line in non_empty_lines:
        if len(line) > 100:
            score -= 0.1
        elif len(line) < 5 and "-->" not in line:
            score -= 0.1

    # Bonus for good structure
    if any(line.strip().startswith("%%") for line in lines):  # Has comments
        score += 0.5

    return max(score, 0.0)


def _get_config_description(key: str) -> str:
    """Get description for a configuration key."""
    descriptions = {
        "server_url": "URL for the Mermaid rendering server",
        "timeout": "Timeout in seconds for rendering operations",
        "retries": "Number of retry attempts for failed operations",
        "default_theme": "Default theme to use for diagrams",
        "default_format": "Default output format for rendered diagrams",
        "validate_syntax": "Whether to validate diagram syntax before rendering",
        "cache_enabled": "Whether to enable caching for improved performance",
        "cache_dir": "Directory path for storing cached files",
        "use_plugin_system": "Whether to use the plugin-based rendering system",
        "fallback_enabled": "Whether to enable fallback rendering methods",
        "max_fallback_attempts": "Maximum number of fallback attempts",
    }
    return descriptions.get(key, f"Configuration setting: {key}")


def _get_section_keys(section: str) -> list[str]:
    """Get configuration keys for a specific section."""
    sections = {
        "rendering": [
            "server_url",
            "timeout",
            "retries",
            "default_format",
            "use_plugin_system",
        ],
        "themes": ["default_theme"],
        "cache": ["cache_enabled", "cache_dir"],
        "validation": ["validate_syntax"],
        "fallback": ["fallback_enabled", "max_fallback_attempts"],
    }
    return sections.get(section, [])


def _validate_config_value(key: str, value: Any) -> bool:
    """Validate a configuration value for a specific key."""
    validations: dict[str, Callable[[Any], bool]] = {
        "timeout": lambda v: isinstance(v, (int, float)) and v > 0,
        "retries": lambda v: isinstance(v, int) and v >= 0,
        "default_theme": lambda v: isinstance(v, str)
        and v in ["default", "dark", "forest", "neutral", "base"],
        "default_format": lambda v: isinstance(v, str) and v in ["svg", "png", "pdf"],
        "validate_syntax": lambda v: isinstance(v, bool),
        "cache_enabled": lambda v: isinstance(v, bool),
        "use_plugin_system": lambda v: isinstance(v, bool),
        "fallback_enabled": lambda v: isinstance(v, bool),
        "max_fallback_attempts": lambda v: isinstance(v, int) and v >= 0,
        "server_url": lambda v: isinstance(v, str)
        and v.startswith(("http://", "https://")),
    }

    validator = validations.get(key)
    if validator:
        return validator(value)

    # Default validation - just check it's not None
    return value is not None


def _get_diagram_example(diagram_type: str) -> str:
    """Get example code for a specific diagram type."""
    examples = {
        "flowchart": """flowchart TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Process]
    B -->|No| D[Skip]
    C --> E[End]
    D --> E""",
        "sequence": """sequenceDiagram
    participant A as Alice
    participant B as Bob
    A->>B: Hello Bob!
    B-->>A: Hello Alice!
    A->>B: How are you?
    B-->>A: I'm good, thanks!""",
        "class": """classDiagram
    class Animal {
        +String name
        +int age
        +makeSound()
    }
    class Dog {
        +String breed
        +bark()
    }
    Animal <|-- Dog""",
        "state": """stateDiagram-v2
    [*] --> Idle
    Idle --> Processing : start
    Processing --> Success : complete
    Processing --> Error : fail
    Success --> [*]
    Error --> Idle : retry""",
        "er": """erDiagram
    CUSTOMER {
        int customer_id PK
        string name
        string email
    }
    ORDER {
        int order_id PK
        int customer_id FK
        date order_date
    }
    CUSTOMER ||--o{ ORDER : places""",
        "journey": """journey
    title User Shopping Journey
    section Discovery
        Visit website: 5: User
        Browse products: 4: User
    section Purchase
        Add to cart: 3: User
        Checkout: 2: User
        Payment: 1: User""",
        "gantt": """gantt
    title Project Timeline
    dateFormat YYYY-MM-DD
    section Planning
        Requirements: 2024-01-01, 5d
        Design: 2024-01-06, 3d
    section Development
        Coding: 2024-01-09, 10d
        Testing: 2024-01-19, 5d""",
        "pie": """pie title Sample Data
    "Category A" : 42.5
    "Category B" : 30.0
    "Category C" : 17.5
    "Category D" : 10.0""",
        "gitgraph": """gitgraph
    commit
    branch develop
    checkout develop
    commit
    commit
    checkout main
    merge develop
    commit""",
        "mindmap": """mindmap
  root((Project))
    Planning
      Requirements
      Timeline
    Development
      Frontend
      Backend
    Testing
      Unit Tests
      Integration""",
        "timeline": """timeline
    title History of Programming
    1940s : ENIAC
         : First Computer
    1950s : FORTRAN
         : First High-level Language
    1970s : C Language
         : System Programming""",
    }

    return examples.get(diagram_type, f"# Example for {diagram_type} not available")


def _get_diagram_best_practices(diagram_type: str) -> list[str]:
    """Get best practices for a specific diagram type."""
    practices = {
        "flowchart": [
            "Use clear, descriptive labels for nodes",
            "Keep the flow direction consistent (top-down or left-right)",
            "Use appropriate shapes: rectangles for processes, diamonds for decisions",
            "Ensure all decision paths are clearly labeled",
            "Group related processes using subgraphs when appropriate",
        ],
        "sequence": [
            "Define all participants at the beginning",
            "Use consistent arrow types for different message types",
            "Add activation boxes for long-running operations",
            "Include notes for complex interactions",
            "Keep message labels concise but descriptive",
        ],
        "class": [
            "Show only relevant attributes and methods",
            "Use proper visibility indicators (+, -, #)",
            "Group related classes together",
            "Use inheritance and composition relationships appropriately",
            "Keep class names and method names clear and consistent",
        ],
        "state": [
            "Use clear state names that describe the system condition",
            "Label transitions with triggering events",
            "Include guard conditions when necessary",
            "Use composite states for complex state hierarchies",
            "Ensure all states have clear entry and exit paths",
        ],
    }

    return practices.get(
        diagram_type,
        [
            "Use clear and descriptive labels",
            "Keep the diagram simple and focused",
            "Follow Mermaid syntax guidelines",
            "Test the diagram for readability",
        ],
    )


def _get_syntax_guide(diagram_type: str) -> dict[str, str]:
    """Get syntax guide for a specific diagram type."""
    guides = {
        "flowchart": {
            "start": "flowchart TD (top-down) or flowchart LR (left-right)",
            "nodes": "[text] for rectangles, {text} for diamonds, ((text)) for circles",
            "connections": "--> for arrows, --- for lines, -.-> for dotted arrows",
            "labels": "A-->|label|B for labeled connections",
            "subgraphs": "subgraph title ... end for grouping",
        },
        "sequence": {
            "start": "sequenceDiagram",
            "participants": "participant A as Alice",
            "messages": "A->>B for sync calls, A-->>B for responses",
            "activation": "activate A ... deactivate A",
            "notes": "note over A: Note text",
        },
        "class": {
            "start": "classDiagram",
            "classes": "class ClassName { attributes methods }",
            "relationships": "<|-- inheritance, *-- composition, o-- aggregation",
            "visibility": "+ public, - private, # protected",
            "types": ": type after attribute/method names",
        },
    }

    return guides.get(
        diagram_type, {"info": "Syntax guide not available for this diagram type"}
    )


def _get_common_patterns(diagram_type: str) -> list[dict[str, str]]:
    """Get common patterns for a specific diagram type."""
    patterns = {
        "flowchart": [
            {
                "name": "Decision Tree",
                "description": "Branching logic with yes/no decisions",
            },
            {
                "name": "Process Flow",
                "description": "Sequential steps with start and end points",
            },
            {
                "name": "Parallel Processing",
                "description": "Multiple paths that converge later",
            },
        ],
        "sequence": [
            {
                "name": "Request-Response",
                "description": "Simple client-server interaction",
            },
            {
                "name": "Authentication Flow",
                "description": "Login process with validation",
            },
            {
                "name": "Error Handling",
                "description": "Exception and error response patterns",
            },
        ],
        "class": [
            {
                "name": "Inheritance Hierarchy",
                "description": "Parent-child class relationships",
            },
            {
                "name": "Composition Pattern",
                "description": "Classes containing other classes",
            },
            {
                "name": "Interface Implementation",
                "description": "Classes implementing interfaces",
            },
        ],
    }

    return patterns.get(diagram_type, [])


def _get_quick_reference_guide() -> dict[str, str]:
    """Get quick reference guide for all diagram types."""
    return {
        "flowchart": "flowchart TD; A[Start] --> B{Decision} --> C[End]",
        "sequence": "sequenceDiagram; A->>B: Message; B-->>A: Response",
        "class": "classDiagram; class A { +method() }; A <|-- B",
        "state": "stateDiagram-v2; [*] --> A; A --> B; B --> [*]",
        "er": "erDiagram; A { id int }; A ||--o{ B : has",
        "journey": "journey; title: Journey; section: Step; Task: 5: Actor",
        "gantt": "gantt; title: Project; Task: 2024-01-01, 5d",
        "pie": "pie title: Data; 'A': 50; 'B': 30; 'C': 20",
        "gitgraph": "gitgraph; commit; branch dev; commit; merge dev",
        "mindmap": "mindmap; root((Topic)); Branch1; Branch2",
        "timeline": "timeline; title: Events; 2024: Event1: Description",
    }


def _generate_template_usage_instructions(template: Any) -> str:
    """Generate usage instructions for a template."""
    instructions = f"To use the '{template.name}' template:\n\n"
    instructions += (
        f"1. Call create_from_template with template_name='{template.name}'\n"
    )
    instructions += "2. Provide the following parameters:\n"

    for param_name, param_info in template.parameters.items():
        param_type = (
            param_info.get("type", "any") if isinstance(param_info, dict) else "any"
        )
        instructions += f"   - {param_name} ({param_type})\n"

    instructions += f"\n3. The template will generate a {template.diagram_type} diagram"
    return instructions


def _extract_parameter_schema(parameters: dict[str, Any]) -> dict[str, Any]:
    """Extract parameter schema from template parameters."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": []}

    for param_name, param_info in parameters.items():
        if isinstance(param_info, dict):
            schema["properties"][param_name] = param_info
            if param_info.get("required", False):
                schema["required"].append(param_name)
        else:
            schema["properties"][param_name] = {"type": "string"}

    return schema


def _assess_template_complexity(template: Any) -> str:
    """Assess template complexity level."""
    content = template.template_content
    param_count = len(template.parameters)

    if param_count <= 2 and len(content) < 200:
        return "simple"
    elif param_count <= 5 and len(content) < 500:
        return "medium"
    else:
        return "complex"


def _generate_template_usage_example(template: Any) -> str:
    """Generate a usage example for a template."""
    example_params: dict[str, Any] = {}
    for param_name, param_info in template.parameters.items():
        if isinstance(param_info, dict):
            param_type = param_info.get("type", "string")
            if param_type == "string":
                example_params[param_name] = f"example_{param_name}"
            elif param_type == "list":
                example_params[param_name] = ["item1", "item2"]
            elif param_type == "number":
                example_params[param_name] = 42
            else:
                example_params[param_name] = f"example_{param_name}"
        else:
            example_params[param_name] = f"example_{param_name}"

    return f"create_from_template('{template.name}', {example_params})"


# Extended tools helper functions

def _extract_nodes_from_code(code: str) -> list[str]:
    """Extract node IDs from diagram code."""
    nodes = []
    # Pattern for node definitions like A[text], B{text}, C((text)), etc.
    pattern = r"\b([A-Za-z_][A-Za-z0-9_]*)\s*[\[\(\{]"
    matches = re.findall(pattern, code)
    for match in matches:
        if match.lower() not in ["flowchart", "graph", "subgraph", "end", "style"]:
            nodes.append(match)
    return list(dict.fromkeys(nodes))  # Remove duplicates while preserving order


def _prefix_nodes(line: str, prefix: str) -> str:
    """Add prefix to node names in a line."""
    # Simple implementation - prefix alphanumeric identifiers
    result = line
    nodes = _extract_nodes_from_code(line)
    for node in nodes:
        result = re.sub(rf"\b{node}\b", f"{prefix}{node}", result)
    return result


def _extract_nodes(diagram_code: str) -> list[dict[str, Any]]:
    """Extract detailed node information from diagram code."""
    nodes = []
    seen_ids = set()

    # Patterns for different node types
    patterns = [
        (r"([A-Za-z_][A-Za-z0-9_]*)\[([^\]]+)\]", "rectangle"),
        (r"([A-Za-z_][A-Za-z0-9_]*)\(([^\)]+)\)", "rounded"),
        (r"([A-Za-z_][A-Za-z0-9_]*)\(\(([^\)]+)\)\)", "circle"),
        (r"([A-Za-z_][A-Za-z0-9_]*)\{([^\}]+)\}", "diamond"),
        (r"([A-Za-z_][A-Za-z0-9_]*)\[\[([^\]]+)\]\]", "subroutine"),
        (r"([A-Za-z_][A-Za-z0-9_]*)\[\(([^\)]+)\)\]", "stadium"),
        (r"([A-Za-z_][A-Za-z0-9_]*)\(\[([^\]]+)\]\)", "stadium"),
    ]

    for pattern, node_type in patterns:
        matches = re.findall(pattern, diagram_code)
        for match in matches:
            node_id = match[0]
            label = match[1] if len(match) > 1 else node_id
            if node_id.lower() not in [
                "flowchart",
                "graph",
                "subgraph",
                "end",
                "style",
                "class",
            ]:
                if node_id not in seen_ids:
                    nodes.append(
                        {
                            "id": node_id,
                            "label": label,
                            "type": node_type,
                        }
                    )
                    seen_ids.add(node_id)

    return nodes


def _extract_edges(diagram_code: str) -> list[dict[str, Any]]:
    """Extract edge/connection information from diagram code."""
    edges = []

    # Patterns for different edge types
    patterns = [
        (r"([A-Za-z_][A-Za-z0-9_]*)\s*-->\s*\|([^\|]+)\|\s*([A-Za-z_][A-Za-z0-9_]*)", "arrow", True),
        (r"([A-Za-z_][A-Za-z0-9_]*)\s*-->\s*([A-Za-z_][A-Za-z0-9_]*)", "arrow", False),
        (r"([A-Za-z_][A-Za-z0-9_]*)\s*---\s*([A-Za-z_][A-Za-z0-9_]*)", "line", False),
        (r"([A-Za-z_][A-Za-z0-9_]*)\s*-\.->\s*([A-Za-z_][A-Za-z0-9_]*)", "dotted_arrow", False),
        (r"([A-Za-z_][A-Za-z0-9_]*)\s*==>\s*([A-Za-z_][A-Za-z0-9_]*)", "thick_arrow", False),
    ]

    for pattern, edge_type, has_label in patterns:
        matches = re.findall(pattern, diagram_code)
        for match in matches:
            if has_label:
                edges.append(
                    {
                        "from": match[0],
                        "to": match[2],
                        "label": match[1],
                        "type": edge_type,
                    }
                )
            else:
                edges.append(
                    {
                        "from": match[0],
                        "to": match[1],
                        "label": "",
                        "type": edge_type,
                    }
                )

    return edges


def _extract_styles(diagram_code: str) -> list[dict[str, Any]]:
    """Extract style definitions from diagram code."""
    styles = []

    # Pattern for style definitions
    pattern = r"style\s+([A-Za-z_][A-Za-z0-9_]*)\s+(.+)"
    matches = re.findall(pattern, diagram_code)

    for match in matches:
        styles.append(
            {
                "target": match[0],
                "definition": match[1],
            }
        )

    return styles


def _extract_subgraphs(diagram_code: str) -> list[dict[str, Any]]:
    """Extract subgraph information from diagram code."""
    subgraphs = []

    # Pattern for subgraph definitions
    pattern = r"subgraph\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?:\[([^\]]+)\])?"
    matches = re.findall(pattern, diagram_code)

    for match in matches:
        subgraphs.append(
            {
                "name": match[0],
                "label": match[1] if match[1] else match[0],
            }
        )

    return subgraphs


def _compare_lists(
    list1: list[dict[str, Any]], list2: list[dict[str, Any]], key: str
) -> dict[str, list[Any]]:
    """Compare two lists of dictionaries by a key."""
    set1 = {item.get(key) for item in list1}
    set2 = {item.get(key) for item in list2}

    return {
        "common": list(set1 & set2),
        "only_in_first": list(set1 - set2),
        "only_in_second": list(set2 - set1),
    }


def _compare_edge_lists(
    edges1: list[dict[str, Any]], edges2: list[dict[str, Any]]
) -> dict[str, list[Any]]:
    """Compare two lists of edges."""
    set1 = {(e.get("from"), e.get("to")) for e in edges1}
    set2 = {(e.get("from"), e.get("to")) for e in edges2}

    return {
        "common": [{"from": e[0], "to": e[1]} for e in set1 & set2],
        "only_in_first": [{"from": e[0], "to": e[1]} for e in set1 - set2],
        "only_in_second": [{"from": e[0], "to": e[1]} for e in set2 - set1],
    }


def _change_diagram_direction(diagram_code: str, direction: str) -> str:
    """Change the direction of a flowchart diagram."""
    # Replace direction in flowchart/graph declaration
    patterns = [
        (r"flowchart\s+(TD|TB|BT|LR|RL)", f"flowchart {direction}"),
        (r"graph\s+(TD|TB|BT|LR|RL)", f"graph {direction}"),
    ]

    result = diagram_code
    for pattern, replacement in patterns:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    return result


def _wrap_in_subgraph(diagram_code: str, subgraph_name: str) -> str:
    """Wrap diagram content in a subgraph."""
    lines = diagram_code.splitlines()
    result_lines = []

    for i, line in enumerate(lines):
        stripped = line.strip().lower()
        if stripped.startswith("flowchart") or stripped.startswith("graph"):
            result_lines.append(line)
            result_lines.append(f"    subgraph {subgraph_name.replace(' ', '_')}[{subgraph_name}]")
        elif i == len(lines) - 1:
            result_lines.append(f"        {line.strip()}")
            result_lines.append("    end")
        else:
            result_lines.append(f"        {line.strip()}" if line.strip() else "")

    return "\n".join(result_lines)


def _add_comments(diagram_code: str) -> str:
    """Add descriptive comments to diagram code."""
    lines = diagram_code.splitlines()
    result_lines = []

    for line in lines:
        stripped = line.strip().lower()
        if stripped.startswith("flowchart") or stripped.startswith("graph"):
            result_lines.append("%% Diagram definition")
            result_lines.append(line)
            result_lines.append("%% Node and connection definitions")
        elif "subgraph" in stripped:
            result_lines.append("%% Subgraph section")
            result_lines.append(line)
        elif "-->" in line or "---" in line:
            result_lines.append(line)
        else:
            result_lines.append(line)

    return "\n".join(result_lines)
