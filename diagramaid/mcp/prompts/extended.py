"""
Extended MCP prompts for diagramaid.

This module provides additional prompts for generating various diagram types
and performing advanced diagram operations.
"""

from .base import Context


def generate_er_diagram_prompt(
    database_description: str,
    include_attributes: bool = True,
    include_relationships: bool = True,
    notation_style: str = "crow_foot",
    ctx: Context | None = None,
) -> str:
    """
    Generate a prompt for creating an Entity-Relationship diagram.

    Args:
        database_description: Description of the database schema
        include_attributes: Include entity attributes
        include_relationships: Include relationship cardinality
        notation_style: Notation style (crow_foot, chen, uml)
        ctx: MCP context (optional)

    Returns:
        Formatted prompt for ER diagram generation
    """
    attributes_guidance = ""
    if include_attributes:
        attributes_guidance = """
- Include key attributes for each entity
- Mark primary keys with PK
- Mark foreign keys with FK
- Use appropriate data types (string, int, date, etc.)"""

    relationships_guidance = ""
    if include_relationships:
        relationships_guidance = """
- Show relationships between entities using proper cardinality:
  - ||--|| for one-to-one
  - ||--o{ for one-to-many
  - }o--o{ for many-to-many
- Label relationships with descriptive verbs"""

    notation_info = {
        "crow_foot": "Use crow's foot notation for cardinality",
        "chen": "Use Chen notation with diamonds for relationships",
        "uml": "Use UML-style notation",
    }

    prompt = f"""Create a Mermaid Entity-Relationship diagram for the following database:

**Database Description:** {database_description}

**Requirements:**
- Start with 'erDiagram'
- {notation_info.get(notation_style, notation_info["crow_foot"])}{attributes_guidance}{relationships_guidance}
- Use clear, meaningful entity and attribute names
- Follow database naming conventions (snake_case or PascalCase)
- Ensure referential integrity is represented

**Example syntax:**
```mermaid
erDiagram
    CUSTOMER {{
        int customer_id PK
        string name
        string email
    }}
    ORDER {{
        int order_id PK
        int customer_id FK
        date order_date
    }}
    CUSTOMER ||--o{{ ORDER : places
```

Please generate only the Mermaid code without additional explanation."""

    return prompt


def generate_state_diagram_prompt(
    system_description: str,
    include_transitions: bool = True,
    include_actions: bool = False,
    include_guards: bool = False,
    ctx: Context | None = None,
) -> str:
    """
    Generate a prompt for creating a State diagram.

    Args:
        system_description: Description of the state machine
        include_transitions: Include transition labels
        include_actions: Include entry/exit actions
        include_guards: Include guard conditions
        ctx: MCP context (optional)

    Returns:
        Formatted prompt for state diagram generation
    """
    transitions_guidance = ""
    if include_transitions:
        transitions_guidance = """
- Label transitions with triggering events
- Use clear, action-oriented labels"""

    actions_guidance = ""
    if include_actions:
        actions_guidance = """
- Include entry and exit actions where appropriate
- Use 'entry /' and 'exit /' prefixes for actions"""

    guards_guidance = ""
    if include_guards:
        guards_guidance = """
- Add guard conditions in square brackets [condition]
- Use clear boolean expressions for guards"""

    prompt = f"""Create a Mermaid State diagram for the following system:

**System Description:** {system_description}

**Requirements:**
- Start with 'stateDiagram-v2'
- Use [*] for initial and final states
- Define clear state names that describe system conditions{transitions_guidance}{actions_guidance}{guards_guidance}
- Group related states using composite states if needed
- Ensure all states are reachable and have exit paths

**Example syntax:**
```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Processing : start
    Processing --> Success : complete
    Processing --> Error : fail
    Success --> [*]
    Error --> Idle : retry
```

Please generate only the Mermaid code without additional explanation."""

    return prompt


def generate_gantt_chart_prompt(
    project_description: str,
    include_dependencies: bool = True,
    include_milestones: bool = True,
    date_format: str = "YYYY-MM-DD",
    ctx: Context | None = None,
) -> str:
    """
    Generate a prompt for creating a Gantt chart.

    Args:
        project_description: Description of the project timeline
        include_dependencies: Include task dependencies
        include_milestones: Include project milestones
        date_format: Date format to use
        ctx: MCP context (optional)

    Returns:
        Formatted prompt for Gantt chart generation
    """
    dependencies_guidance = ""
    if include_dependencies:
        dependencies_guidance = """
- Show task dependencies using 'after' keyword
- Ensure logical task ordering"""

    milestones_guidance = ""
    if include_milestones:
        milestones_guidance = """
- Include key milestones using 'milestone' keyword
- Place milestones at significant project points"""

    prompt = f"""Create a Mermaid Gantt chart for the following project:

**Project Description:** {project_description}

**Requirements:**
- Start with 'gantt'
- Include a descriptive title
- Use dateFormat {date_format}
- Organize tasks into logical sections{dependencies_guidance}{milestones_guidance}
- Use realistic task durations
- Ensure tasks flow logically

**Example syntax:**
```mermaid
gantt
    title Project Timeline
    dateFormat {date_format}

    section Planning
        Requirements gathering: req, 2024-01-01, 5d
        Design phase: design, after req, 3d

    section Development
        Implementation: impl, after design, 10d
        Testing: test, after impl, 5d

    section Deployment
        Release: milestone, after test, 0d
```

Please generate only the Mermaid code without additional explanation."""

    return prompt


def generate_mindmap_prompt(
    topic_description: str,
    depth_level: int = 3,
    include_icons: bool = False,
    style: str = "hierarchical",
    ctx: Context | None = None,
) -> str:
    """
    Generate a prompt for creating a Mind Map.

    Args:
        topic_description: Central topic and related concepts
        depth_level: Maximum depth of branches (1-5)
        include_icons: Include icons for visual enhancement
        style: Mind map style (hierarchical, radial)
        ctx: MCP context (optional)

    Returns:
        Formatted prompt for mind map generation
    """
    depth_guidance = {
        1: "Keep it simple with only main branches",
        2: "Include main branches and one level of sub-branches",
        3: "Include main branches, sub-branches, and details",
        4: "Create a detailed map with multiple levels",
        5: "Create a comprehensive map with full detail",
    }

    icons_guidance = ""
    if include_icons:
        icons_guidance = """
- Add relevant icons using ::icon(fa fa-icon-name) syntax
- Use icons to visually categorize branches"""

    prompt = f"""Create a Mermaid Mind Map for the following topic:

**Topic Description:** {topic_description}

**Requirements:**
- Start with 'mindmap'
- Use root((Central Topic)) for the central node
- {depth_guidance.get(depth_level, depth_guidance[3])}
- Organize branches logically by category or theme{icons_guidance}
- Use clear, concise labels for each node
- Balance the map visually

**Example syntax:**
```mermaid
mindmap
  root((Main Topic))
    Branch 1
      Sub-branch 1.1
      Sub-branch 1.2
    Branch 2
      Sub-branch 2.1
        Detail 2.1.1
      Sub-branch 2.2
    Branch 3
```

Please generate only the Mermaid code without additional explanation."""

    return prompt


def generate_timeline_prompt(
    events_description: str,
    time_scale: str = "years",
    include_descriptions: bool = True,
    ctx: Context | None = None,
) -> str:
    """
    Generate a prompt for creating a Timeline diagram.

    Args:
        events_description: Description of events to display
        time_scale: Time scale (days, months, years, decades)
        include_descriptions: Include event descriptions
        ctx: MCP context (optional)

    Returns:
        Formatted prompt for timeline generation
    """
    scale_guidance = {
        "days": "Use specific dates for events",
        "months": "Group events by month",
        "years": "Group events by year",
        "decades": "Group events by decade",
    }

    descriptions_guidance = ""
    if include_descriptions:
        descriptions_guidance = """
- Add brief descriptions for each event
- Use multiple lines for detailed events"""

    prompt = f"""Create a Mermaid Timeline diagram for the following events:

**Events Description:** {events_description}

**Requirements:**
- Start with 'timeline'
- Include a descriptive title
- {scale_guidance.get(time_scale, scale_guidance["years"])}{descriptions_guidance}
- Arrange events chronologically
- Group related events into sections if appropriate

**Example syntax:**
```mermaid
timeline
    title History of Events
    2020 : Event 1
         : Description of event 1
    2021 : Event 2
         : Description of event 2
    2022 : Event 3
         : Major milestone
```

Please generate only the Mermaid code without additional explanation."""

    return prompt


def generate_pie_chart_prompt(
    data_description: str,
    show_percentages: bool = True,
    ctx: Context | None = None,
) -> str:
    """
    Generate a prompt for creating a Pie Chart.

    Args:
        data_description: Description of data to visualize
        show_percentages: Show percentage values
        ctx: MCP context (optional)

    Returns:
        Formatted prompt for pie chart generation
    """
    percentages_guidance = ""
    if show_percentages:
        percentages_guidance = """
- Mermaid will automatically calculate and display percentages
- Ensure values are proportionally accurate"""

    prompt = f"""Create a Mermaid Pie Chart for the following data:

**Data Description:** {data_description}

**Requirements:**
- Start with 'pie'
- Include a descriptive title using 'title' keyword
- Use quoted labels for each slice
- Provide numeric values for each category{percentages_guidance}
- Limit to 5-8 slices for readability
- Order slices by size (largest first) if appropriate

**Example syntax:**
```mermaid
pie title Distribution of Categories
    "Category A" : 42
    "Category B" : 30
    "Category C" : 18
    "Category D" : 10
```

Please generate only the Mermaid code without additional explanation."""

    return prompt


def generate_git_graph_prompt(
    workflow_description: str,
    include_branches: bool = True,
    include_tags: bool = False,
    branching_strategy: str = "gitflow",
    ctx: Context | None = None,
) -> str:
    """
    Generate a prompt for creating a Git Graph.

    Args:
        workflow_description: Description of the git workflow
        include_branches: Include feature branches
        include_tags: Include version tags
        branching_strategy: Branching strategy (gitflow, trunk, github_flow)
        ctx: MCP context (optional)

    Returns:
        Formatted prompt for git graph generation
    """
    strategy_guidance = {
        "gitflow": "Use main, develop, feature, release, and hotfix branches",
        "trunk": "Use main branch with short-lived feature branches",
        "github_flow": "Use main branch with feature branches and pull requests",
    }

    branches_guidance = ""
    if include_branches:
        branches_guidance = """
- Create feature branches for new work
- Show branch creation and merging"""

    tags_guidance = ""
    if include_tags:
        tags_guidance = """
- Add version tags at release points
- Use semantic versioning (v1.0.0)"""

    prompt = f"""Create a Mermaid Git Graph for the following workflow:

**Workflow Description:** {workflow_description}

**Requirements:**
- Start with 'gitgraph'
- {strategy_guidance.get(branching_strategy, strategy_guidance["gitflow"])}{branches_guidance}{tags_guidance}
- Show commits with meaningful messages
- Demonstrate proper merge flow
- Keep the graph readable

**Example syntax:**
```mermaid
gitgraph
    commit id: "Initial commit"
    branch develop
    checkout develop
    commit id: "Add feature A"
    branch feature/login
    checkout feature/login
    commit id: "Implement login"
    checkout develop
    merge feature/login
    checkout main
    merge develop tag: "v1.0.0"
```

Please generate only the Mermaid code without additional explanation."""

    return prompt


def generate_c4_diagram_prompt(
    system_description: str,
    diagram_level: str = "context",
    include_external: bool = True,
    ctx: Context | None = None,
) -> str:
    """
    Generate a prompt for creating a C4 architecture diagram.

    Args:
        system_description: Description of the system architecture
        diagram_level: C4 level (context, container, component, code)
        include_external: Include external systems/actors
        ctx: MCP context (optional)

    Returns:
        Formatted prompt for C4 diagram generation
    """
    level_guidance = {
        "context": "Show the system in context with users and external systems",
        "container": "Show the high-level containers (applications, databases) within the system",
        "component": "Show the components within a specific container",
        "code": "Show the code-level structure (classes, interfaces)",
    }

    external_guidance = ""
    if include_external:
        external_guidance = """
- Include external systems and actors
- Show system boundaries clearly"""

    prompt = f"""Create a Mermaid C4 diagram ({diagram_level} level) for the following system:

**System Description:** {system_description}

**Requirements:**
- Use flowchart syntax to represent C4 concepts
- {level_guidance.get(diagram_level, level_guidance["context"])}{external_guidance}
- Use appropriate shapes:
  - Rectangles for systems/containers
  - Rounded rectangles for components
  - Person shapes for users/actors
- Show relationships with labeled arrows
- Include brief descriptions

**Example syntax for {diagram_level} diagram:**
```mermaid
flowchart TB
    subgraph boundary[System Boundary]
        system[System Name<br/>Description]
    end

    user[fa:fa-user User<br/>Description]
    external[External System<br/>Description]

    user --> system
    system --> external
```

Please generate only the Mermaid code without additional explanation."""

    return prompt


def refactor_diagram_prompt(
    diagram_code: str,
    refactoring_goals: list[str] | None = None,
    preserve_semantics: bool = True,
    ctx: Context | None = None,
) -> str:
    """
    Generate a prompt for refactoring and improving a diagram.

    Args:
        diagram_code: The Mermaid diagram code to refactor
        refactoring_goals: Specific goals for refactoring
        preserve_semantics: Preserve the diagram's meaning
        ctx: MCP context (optional)

    Returns:
        Formatted prompt for diagram refactoring
    """
    goals_list = ""
    if refactoring_goals:
        goals_list = "\n**Specific Goals:**\n" + "\n".join(
            [f"- {goal}" for goal in refactoring_goals]
        )

    semantics_guidance = ""
    if preserve_semantics:
        semantics_guidance = """
- Preserve the original meaning and relationships
- Do not remove important information"""

    prompt = f"""Refactor and improve the following Mermaid diagram:

```mermaid
{diagram_code}
```
{goals_list}

**Requirements:**
- Improve code organization and readability
- Apply consistent naming conventions
- Optimize layout and flow direction
- Remove redundant elements
- Add appropriate styling if beneficial{semantics_guidance}

**Please provide:**
1. The refactored Mermaid code
2. A brief summary of changes made
3. Explanation of why each change improves the diagram

Generate the improved Mermaid code first, then provide explanations."""

    return prompt


def translate_diagram_prompt(
    diagram_code: str,
    target_language: str,
    preserve_technical_terms: bool = True,
    ctx: Context | None = None,
) -> str:
    """
    Generate a prompt for translating diagram labels to another language.

    Args:
        diagram_code: The Mermaid diagram code to translate
        target_language: Target language for translation
        preserve_technical_terms: Keep technical terms in original language
        ctx: MCP context (optional)

    Returns:
        Formatted prompt for diagram translation
    """
    technical_guidance = ""
    if preserve_technical_terms:
        technical_guidance = """
- Keep technical terms, acronyms, and proper nouns in their original form
- Only translate descriptive labels and comments"""

    prompt = f"""Translate the labels in the following Mermaid diagram to {target_language}:

```mermaid
{diagram_code}
```

**Requirements:**
- Translate all node labels and edge labels
- Maintain the diagram structure and syntax
- Keep the same node IDs (only translate display text){technical_guidance}
- Ensure translations are contextually appropriate
- Preserve any styling or formatting

**Please provide:**
1. The translated Mermaid code
2. A translation glossary for key terms

Generate the translated Mermaid code."""

    return prompt


def convert_to_diagram_prompt(
    source_format: str,
    source_content: str,
    target_diagram_type: str = "flowchart",
    ctx: Context | None = None,
) -> str:
    """
    Generate a prompt for converting other formats to Mermaid diagrams.

    Args:
        source_format: Source format (json, yaml, csv, text, pseudocode)
        source_content: Content in the source format
        target_diagram_type: Target Mermaid diagram type
        ctx: MCP context (optional)

    Returns:
        Formatted prompt for format conversion
    """
    format_guidance = {
        "json": "Parse the JSON structure and represent it as a diagram",
        "yaml": "Parse the YAML structure and represent it as a diagram",
        "csv": "Parse the CSV data and represent relationships as a diagram",
        "text": "Extract entities and relationships from the text",
        "pseudocode": "Convert the algorithm steps into a flowchart",
    }

    prompt = f"""Convert the following {source_format.upper()} content to a Mermaid {target_diagram_type} diagram:

**Source Content ({source_format}):**
```{source_format}
{source_content}
```

**Requirements:**
- {format_guidance.get(source_format, "Parse the content and create an appropriate diagram")}
- Create a {target_diagram_type} diagram
- Preserve all important information from the source
- Use clear, descriptive labels
- Organize the diagram logically

**Please provide:**
1. The Mermaid diagram code
2. Brief notes on how the conversion was done

Generate the Mermaid code."""

    return prompt


def document_architecture_prompt(
    system_name: str,
    components: list[str],
    interactions: list[str] | None = None,
    diagram_types: list[str] | None = None,
    ctx: Context | None = None,
) -> str:
    """
    Generate a prompt for creating comprehensive architecture documentation.

    Args:
        system_name: Name of the system
        components: List of system components
        interactions: List of component interactions
        diagram_types: Types of diagrams to generate
        ctx: MCP context (optional)

    Returns:
        Formatted prompt for architecture documentation
    """
    components_list = "\n".join([f"- {comp}" for comp in components])

    interactions_list = ""
    if interactions:
        interactions_list = "\n**Interactions:**\n" + "\n".join(
            [f"- {inter}" for inter in interactions]
        )

    diagrams_list = ""
    if diagram_types:
        diagrams_list = "\n**Diagram Types to Generate:**\n" + "\n".join(
            [f"- {dt}" for dt in diagram_types]
        )
    else:
        diagrams_list = """
**Diagram Types to Generate:**
- System context diagram (flowchart)
- Component interaction diagram (sequence)
- Data flow diagram (flowchart)"""

    prompt = f"""Create comprehensive architecture documentation for the following system:

**System Name:** {system_name}

**Components:**
{components_list}
{interactions_list}
{diagrams_list}

**Requirements:**
- Create multiple diagrams showing different aspects of the system
- Include clear labels and descriptions
- Show relationships and data flow
- Use appropriate diagram types for each aspect
- Ensure diagrams are consistent with each other

**Please provide:**
1. Multiple Mermaid diagrams (each in its own code block)
2. Brief description of what each diagram shows
3. Key architectural decisions highlighted

Generate all diagrams with explanations."""

    return prompt


def repair_diagram_prompt(
    diagram_code: str,
    validation_errors: list[str] | None = None,
    validation_warnings: list[str] | None = None,
    repair_focus: str = "all",
    ctx: Context | None = None,
) -> str:
    """
    Generate a prompt for AI-assisted diagram repair.

    This prompt is designed to work with the auto-repair workflow, providing
    AI with context about validation errors and requesting specific fixes.

    Args:
        diagram_code: The Mermaid diagram code to repair
        validation_errors: List of validation errors found
        validation_warnings: List of validation warnings found
        repair_focus: Focus area - 'syntax', 'structure', 'style', or 'all'
        ctx: MCP context (optional)

    Returns:
        Formatted prompt for AI-assisted diagram repair
    """
    errors_section = ""
    if validation_errors:
        errors_section = "\n**Validation Errors:**\n" + "\n".join(
            [f"- ❌ {error}" for error in validation_errors]
        )

    warnings_section = ""
    if validation_warnings:
        warnings_section = "\n**Validation Warnings:**\n" + "\n".join(
            [f"- ⚠️ {warning}" for warning in validation_warnings]
        )

    focus_guidance = {
        "syntax": """Focus on fixing syntax errors:
- Correct arrow syntax (-->, --->, etc.)
- Fix bracket matching
- Correct diagram type declarations
- Fix node ID formatting""",
        "structure": """Focus on structural improvements:
- Ensure proper diagram hierarchy
- Fix missing connections
- Correct subgraph definitions
- Validate relationship cardinality""",
        "style": """Focus on style and readability:
- Improve node naming conventions
- Add appropriate styling
- Enhance visual organization
- Apply consistent formatting""",
        "all": """Address all issues comprehensively:
- Fix all syntax errors first
- Correct structural problems
- Improve style and readability
- Apply best practices""",
    }

    prompt = f"""Repair and fix the following Mermaid diagram:

```mermaid
{diagram_code}
```
{errors_section}
{warnings_section}

**Repair Focus:** {repair_focus}

**Instructions:**
{focus_guidance.get(repair_focus, focus_guidance["all"])}

**Requirements:**
1. Preserve the original intent and meaning of the diagram
2. Fix all identified errors and warnings
3. Ensure the repaired diagram is valid Mermaid syntax
4. Maintain or improve readability
5. Add comments if complex fixes are made

**Please provide:**
1. The fully repaired Mermaid diagram code
2. A numbered list of changes made
3. Brief explanation for each fix

Generate the repaired Mermaid code first, then list the changes."""

    return prompt


def fix_syntax_errors_prompt(
    diagram_code: str,
    specific_errors: list[str] | None = None,
    ctx: Context | None = None,
) -> str:
    """
    Generate a prompt specifically for fixing syntax errors.

    Args:
        diagram_code: The Mermaid diagram code with syntax errors
        specific_errors: List of specific syntax errors to fix
        ctx: MCP context (optional)

    Returns:
        Formatted prompt for syntax error fixing
    """
    errors_list = ""
    if specific_errors:
        errors_list = "\n**Specific Errors to Fix:**\n" + "\n".join(
            [f"- {error}" for error in specific_errors]
        )

    prompt = f"""Fix the syntax errors in the following Mermaid diagram:

```mermaid
{diagram_code}
```
{errors_list}

**Common Syntax Issues to Check:**
1. Arrow syntax: Use --> for solid arrows, -.-> for dotted
2. Bracket matching: Ensure all [ ], ( ), {{ }} are properly closed
3. Diagram type: Must be valid (flowchart, sequenceDiagram, classDiagram, etc.)
4. Direction: For flowcharts, use TD, LR, TB, RL, BT
5. Node IDs: Should start with a letter, use only alphanumeric and underscores
6. Labels: Text in brackets should be properly quoted if containing special chars

**Output:**
Provide ONLY the corrected Mermaid code without any explanation.
The code should be immediately usable."""

    return prompt


def improve_diagram_quality_prompt(
    diagram_code: str,
    quality_aspects: list[str] | None = None,
    ctx: Context | None = None,
) -> str:
    """
    Generate a prompt for improving diagram quality and best practices.

    Args:
        diagram_code: The Mermaid diagram code to improve
        quality_aspects: Specific aspects to focus on
        ctx: MCP context (optional)

    Returns:
        Formatted prompt for quality improvement
    """
    aspects = quality_aspects or ["readability", "consistency", "completeness"]
    aspects_list = "\n".join([f"- {aspect.title()}" for aspect in aspects])

    prompt = f"""Improve the quality of the following Mermaid diagram:

```mermaid
{diagram_code}
```

**Quality Aspects to Address:**
{aspects_list}

**Best Practices to Apply:**
1. **Naming**: Use clear, descriptive names for nodes and relationships
2. **Organization**: Group related elements logically
3. **Flow**: Ensure clear directional flow (top-to-bottom or left-to-right)
4. **Simplicity**: Remove redundant elements while preserving meaning
5. **Consistency**: Use consistent styling and naming conventions
6. **Documentation**: Add comments for complex sections

**Please provide:**
1. The improved Mermaid diagram
2. Summary of quality improvements made
3. Any remaining suggestions for further improvement

Generate the improved diagram first."""

    return prompt
