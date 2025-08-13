# Validators Module

This module provides comprehensive validation capabilities for Mermaid diagram syntax, structure, and best practices.

## Components

### Core Validation
- **`validator.py`** - Main MermaidValidator class with comprehensive validation logic

## Key Features

- **Syntax Validation**: Check Mermaid diagram syntax for correctness
- **Structural Validation**: Ensure diagram structure follows Mermaid specifications
- **Semantic Validation**: Validate logical consistency and relationships
- **Best Practice Validation**: Suggest improvements and optimizations
- **Multi-Diagram Support**: Validation for all supported diagram types

## Supported Diagram Types

The validator supports all major Mermaid diagram types:
- Flowcharts (`flowchart TD`, `graph TD`)
- Sequence Diagrams (`sequenceDiagram`)
- Class Diagrams (`classDiagram`)
- State Diagrams (`stateDiagram`, `stateDiagram-v2`)
- Entity-Relationship Diagrams (`erDiagram`)
- User Journey Maps (`journey`)
- Gantt Charts (`gantt`)
- Pie Charts (`pie`)
- Git Graphs (`gitgraph`)
- Mind Maps (`mindmap`)
- Timeline Diagrams (`timeline`)

## Usage Example

```python
from mermaid_render.validators import MermaidValidator

# Create validator
validator = MermaidValidator()

# Validate diagram
result = validator.validate("""
flowchart TD
    A[Start] --> B[Process]
    B --> C[End]
""")

if result.is_valid:
    print("Diagram is valid!")
else:
    print("Validation errors:")
    for error in result.errors:
        print(f"  - {error}")
    
    print("Warnings:")
    for warning in result.warnings:
        print(f"  - {warning}")
```

## Validation Results

The `ValidationResult` class provides detailed feedback:

```python
class ValidationResult:
    is_valid: bool           # Overall validation status
    errors: List[str]        # Critical errors that prevent rendering
    warnings: List[str]      # Non-critical issues and suggestions
    diagram_type: str        # Detected diagram type
    line_errors: Dict[int, List[str]]  # Line-specific errors
```

## Advanced Features

### Custom Validation Rules
```python
validator = MermaidValidator()
validator.add_custom_rule("no_long_labels", lambda code: ...)
```

### Validation Configuration
```python
validator = MermaidValidator(
    strict_mode=True,
    max_nodes=100,
    max_edges=200
)
```

## Integration

The validator is integrated throughout the library:
- Automatic validation in renderers
- Real-time validation in interactive mode
- Template validation in template system
- CLI validation commands
