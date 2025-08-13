# Models Module

This module contains object-oriented diagram model classes that provide clean, type-safe interfaces for creating different types of Mermaid diagrams.

## Components

### Diagram Types
- **`flowchart.py`** - Flowchart and process diagrams
- **`sequence.py`** - Sequence diagrams for interaction modeling
- **`class_diagram.py`** - UML class diagrams for object-oriented design
- **`state.py`** - State machine and state transition diagrams
- **`er_diagram.py`** - Entity-relationship diagrams for database design
- **`user_journey.py`** - User journey mapping diagrams
- **`gantt.py`** - Project timeline and Gantt charts
- **`pie_chart.py`** - Pie charts for data visualization
- **`git_graph.py`** - Git branching and workflow diagrams
- **`mindmap.py`** - Mind maps and hierarchical structures
- **`timeline.py`** - Timeline diagrams for chronological events

## Design Principles

All diagram models follow consistent design patterns:

1. **Fluent Interface**: Method chaining for intuitive diagram construction
2. **Type Safety**: Full type hints and validation
3. **Immutable Operations**: Safe concurrent access
4. **Validation**: Built-in syntax and structure validation
5. **Extensibility**: Easy to extend with custom diagram types

## Usage Example

```python
from mermaid_render.models import FlowchartDiagram, SequenceDiagram

# Create a flowchart
flowchart = FlowchartDiagram()
flowchart.add_node("start", "Start Process")
flowchart.add_node("process", "Process Data")
flowchart.add_node("end", "End Process")
flowchart.add_edge("start", "process")
flowchart.add_edge("process", "end")

# Create a sequence diagram
sequence = SequenceDiagram()
sequence.add_participant("user", "User")
sequence.add_participant("api", "API Server")
sequence.add_message("user", "api", "Login Request")
sequence.add_message("api", "user", "Login Response")

# Generate Mermaid syntax
print(flowchart.to_mermaid())
print(sequence.to_mermaid())
```

## Base Classes

All diagram models inherit from `MermaidDiagram` (defined in `core.py`), which provides:
- Common validation interface
- Mermaid syntax generation
- Caching for performance
- Error handling

## Validation

Each model includes built-in validation:
```python
diagram = FlowchartDiagram()
# ... build diagram ...

if diagram.validate():
    print("Diagram is valid")
else:
    print("Validation errors:", diagram.get_validation_errors())
```
