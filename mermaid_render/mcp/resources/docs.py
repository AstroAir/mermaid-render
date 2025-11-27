"""
Documentation resources for MCP.

This module provides documentation-related resource implementations.
"""

import json

from .base import Context, ResourceError, logger


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
                "node_types": [
                    "rectangle",
                    "rounded",
                    "circle",
                    "rhombus",
                    "hexagon",
                    "parallelogram",
                ],
                "use_cases": [
                    "Process flows",
                    "Decision trees",
                    "Algorithms",
                    "Workflows",
                ],
            },
            "sequence": {
                "name": "Sequence Diagram",
                "description": "Sequence diagrams show interactions between participants over time",
                "syntax": "sequenceDiagram\n    participant A\n    participant B\n    A->>B: Message\n    B-->>A: Response",
                "keywords": ["sequenceDiagram"],
                "elements": ["participant", "actor", "note", "loop", "alt", "opt"],
                "arrow_types": ["->", "->>", "-->>", "-x", "--x"],
                "use_cases": [
                    "API interactions",
                    "System communications",
                    "User flows",
                    "Protocol diagrams",
                ],
            },
            "class": {
                "name": "Class Diagram",
                "description": "Class diagrams show the structure of classes and their relationships",
                "syntax": "classDiagram\n    class Animal {\n        +name: string\n        +makeSound()\n    }\n    Animal <|-- Dog",
                "keywords": ["classDiagram"],
                "relationships": [
                    "inheritance",
                    "composition",
                    "aggregation",
                    "association",
                ],
                "visibility": [
                    "public (+)",
                    "private (-)",
                    "protected (#)",
                    "package (~)",
                ],
                "use_cases": [
                    "Object-oriented design",
                    "Database schemas",
                    "System architecture",
                    "Code documentation",
                ],
            },
            "state": {
                "name": "State Diagram",
                "description": "State diagrams show the states of a system and transitions between them",
                "syntax": "stateDiagram-v2\n    [*] --> Still\n    Still --> [*]\n    Still --> Moving\n    Moving --> Still",
                "keywords": ["stateDiagram", "stateDiagram-v2"],
                "elements": ["state", "transition", "choice", "fork", "join"],
                "use_cases": [
                    "State machines",
                    "Workflow states",
                    "System behavior",
                    "Protocol states",
                ],
            },
            "er": {
                "name": "Entity Relationship Diagram",
                "description": "ER diagrams show relationships between entities in a database",
                "syntax": "erDiagram\n    CUSTOMER {\n        string name\n        string email\n    }\n    ORDER {\n        int id\n        date created\n    }\n    CUSTOMER ||--o{ ORDER : places",
                "keywords": ["erDiagram"],
                "relationships": ["one-to-one", "one-to-many", "many-to-many"],
                "cardinality": ["||--||", "||--o{", "}o--||", "}o--o{"],
                "use_cases": [
                    "Database design",
                    "Data modeling",
                    "System architecture",
                    "Documentation",
                ],
            },
            "journey": {
                "name": "User Journey",
                "description": "User journey diagrams show user experiences and touchpoints",
                "syntax": "journey\n    title My working day\n    section Go to work\n      Make tea: 5: Me\n      Go upstairs: 3: Me",
                "keywords": ["journey"],
                "elements": ["title", "section", "task"],
                "use_cases": [
                    "User experience design",
                    "Customer journey mapping",
                    "Process improvement",
                    "Service design",
                ],
            },
            "gantt": {
                "name": "Gantt Chart",
                "description": "Gantt charts show project schedules and task dependencies",
                "syntax": "gantt\n    title Project Timeline\n    dateFormat YYYY-MM-DD\n    section Planning\n    Task 1: 2023-01-01, 30d",
                "keywords": ["gantt"],
                "elements": ["title", "dateFormat", "section", "task"],
                "use_cases": [
                    "Project management",
                    "Timeline planning",
                    "Resource allocation",
                    "Progress tracking",
                ],
            },
            "pie": {
                "name": "Pie Chart",
                "description": "Pie charts show proportional data as slices of a circle",
                "syntax": 'pie title Survey Results\n    "Option A" : 42\n    "Option B" : 30\n    "Option C" : 28',
                "keywords": ["pie"],
                "elements": ["title", "data"],
                "use_cases": [
                    "Data visualization",
                    "Survey results",
                    "Market share",
                    "Budget allocation",
                ],
            },
            "gitgraph": {
                "name": "Git Graph",
                "description": "Git graphs show branching and merging in version control",
                "syntax": "gitgraph\n    commit\n    branch develop\n    checkout develop\n    commit\n    checkout main\n    merge develop",
                "keywords": ["gitgraph"],
                "elements": ["commit", "branch", "checkout", "merge"],
                "use_cases": [
                    "Version control visualization",
                    "Release planning",
                    "Development workflows",
                    "Code review",
                ],
            },
            "mindmap": {
                "name": "Mind Map",
                "description": "Mind maps show hierarchical information radiating from a central topic",
                "syntax": "mindmap\n  root((Central Topic))\n    Branch 1\n      Sub-branch 1\n      Sub-branch 2\n    Branch 2",
                "keywords": ["mindmap"],
                "elements": ["root", "branch", "sub-branch"],
                "use_cases": [
                    "Brainstorming",
                    "Knowledge organization",
                    "Planning",
                    "Learning",
                ],
            },
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
                    "code": "flowchart TD\n    A[Start] --> B{Is it working?}\n    B -->|Yes| C[Great!]\n    B -->|No| D[Fix it]\n    D --> B\n    C --> E[End]",
                },
                {
                    "title": "Decision Tree",
                    "description": "Flowchart representing a decision-making process",
                    "code": "flowchart LR\n    A[Problem] --> B{Can we solve it?}\n    B -->|Yes| C[Solve it]\n    B -->|No| D{Can we learn from it?}\n    D -->|Yes| E[Learn from it]\n    D -->|No| F[Let it go]\n    C --> G[Success]\n    E --> G\n    F --> G",
                },
            ],
            "sequence": [
                {
                    "title": "API Authentication",
                    "description": "Sequence diagram showing API authentication flow",
                    "code": "sequenceDiagram\n    participant C as Client\n    participant A as Auth Server\n    participant R as Resource Server\n    \n    C->>A: Login Request\n    A-->>C: Access Token\n    C->>R: API Request + Token\n    R->>A: Validate Token\n    A-->>R: Token Valid\n    R-->>C: API Response",
                }
            ],
            "class": [
                {
                    "title": "Animal Hierarchy",
                    "description": "Class diagram showing inheritance",
                    "code": "classDiagram\n    class Animal {\n        +String name\n        +int age\n        +makeSound()\n        +move()\n    }\n    \n    class Dog {\n        +String breed\n        +bark()\n    }\n    \n    class Cat {\n        +boolean indoor\n        +meow()\n    }\n    \n    Animal <|-- Dog\n    Animal <|-- Cat",
                }
            ],
        }

        if diagram_type not in examples:
            raise ResourceError(f"No examples found for diagram type '{diagram_type}'")

        return json.dumps(
            {"diagram_type": diagram_type, "examples": examples[diagram_type]}, indent=2
        )

    except Exception as e:
        logger.error(f"Error getting diagram examples for {diagram_type}: {e}")
        raise ResourceError(f"Failed to get diagram examples: {e}")
