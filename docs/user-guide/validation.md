# Validation

Comprehensive validation system for ensuring diagram syntax correctness and providing helpful error messages.

## Overview

The validation system provides:

- **Syntax Validation**: Check Mermaid diagram syntax
- **Semantic Validation**: Verify diagram logic and structure
- **Custom Validators**: Create domain-specific validation rules
- **Error Reporting**: Detailed error messages with suggestions
- **Auto-correction**: Automatic fixing of common issues

## Basic Validation

### Quick Validation

```python
from diagramaid import validate_diagram

# Simple validation
diagram = "flowchart TD\n    A --> B"
result = validate_diagram(diagram)

if result.is_valid:
    print("Diagram is valid!")
else:
    print("Validation errors:")
    for error in result.errors:
        print(f"  - {error.message}")
```

### Validation with Renderer

```python
from diagramaid import MermaidRenderer

renderer = MermaidRenderer(validate_input=True)

try:
    result = renderer.render(diagram)
except ValidationError as e:
    print(f"Validation failed: {e}")
    for error in e.errors:
        print(f"  Line {error.line}: {error.message}")
```

## Validation Types

### Syntax Validation

```python
from diagramaid.validators import SyntaxValidator

validator = SyntaxValidator()

# Check basic syntax
result = validator.validate(diagram)
print(f"Syntax valid: {result.is_valid}")

# Get detailed syntax errors
for error in result.errors:
    print(f"Line {error.line}, Column {error.column}: {error.message}")
    if error.suggestion:
        print(f"  Suggestion: {error.suggestion}")
```

### Semantic Validation

```python
from diagramaid.validators import SemanticValidator

validator = SemanticValidator()

# Check diagram logic
result = validator.validate(diagram)

# Common semantic issues
for warning in result.warnings:
    print(f"Warning: {warning.message}")
    if warning.type == "unreachable_node":
        print(f"  Node '{warning.node_id}' is not reachable")
    elif warning.type == "unused_definition":
        print(f"  Definition '{warning.definition}' is not used")
```

### Structure Validation

```python
from diagramaid.validators import StructureValidator

validator = StructureValidator(
    max_nodes=100,
    max_edges=200,
    max_depth=10,
    require_start_node=True,
    require_end_node=True
)

result = validator.validate(diagram)
```

## Validation Rules

### Built-in Rules

```python
from diagramaid.validators import ValidationRules

# Enable specific validation rules
rules = ValidationRules(
    check_syntax=True,
    check_semantics=True,
    check_accessibility=True,
    check_performance=True,
    check_best_practices=True
)

validator = DiagramValidator(rules=rules)
```

### Custom Validation Rules

```python
from diagramaid.validators import CustomRule

class NoOrphanNodesRule(CustomRule):
    def __init__(self):
        super().__init__(
            name="no_orphan_nodes",
            description="Ensure all nodes are connected"
        )

    def validate(self, diagram):
        errors = []
        # Parse diagram and check for orphan nodes
        nodes = self.parse_nodes(diagram)
        edges = self.parse_edges(diagram)

        connected_nodes = set()
        for edge in edges:
            connected_nodes.add(edge.source)
            connected_nodes.add(edge.target)

        for node in nodes:
            if node.id not in connected_nodes:
                errors.append(ValidationError(
                    message=f"Node '{node.id}' is not connected to any other node",
                    line=node.line,
                    severity="warning",
                    suggestion="Connect this node or remove it"
                ))

        return ValidationResult(errors=errors)

# Use custom rule
validator.add_rule(NoOrphanNodesRule())
```

## Error Handling

### Error Types

```python
from diagramaid.validators import ValidationError

# Different error severities
errors = [
    ValidationError(
        message="Invalid syntax",
        line=5,
        column=10,
        severity="error",  # error, warning, info
        code="SYNTAX_001"
    ),
    ValidationError(
        message="Unreachable node detected",
        line=8,
        severity="warning",
        suggestion="Connect node to the main flow"
    )
]
```

### Error Reporting

```python
from diagramaid.validators import ErrorReporter

reporter = ErrorReporter(format="detailed")

# Generate detailed error report
report = reporter.generate_report(validation_result)
print(report)

# HTML error report
html_report = reporter.generate_html_report(validation_result)
with open("validation_report.html", "w") as f:
    f.write(html_report)
```

### Error Context

```python
# Get error context with surrounding lines
for error in result.errors:
    context = error.get_context(diagram, lines_before=2, lines_after=2)
    print(f"Error at line {error.line}:")
    print(context.formatted_text)
    print(f"  {error.message}")
```

## Auto-correction

### Automatic Fixes

```python
from diagramaid.validators import AutoCorrector

corrector = AutoCorrector(
    fix_syntax_errors=True,
    fix_formatting=True,
    fix_common_mistakes=True
)

# Attempt to fix diagram
corrected_diagram, fixes_applied = corrector.correct(diagram)

print("Fixes applied:")
for fix in fixes_applied:
    print(f"  - {fix.description}")
    print(f"    Line {fix.line}: '{fix.original}' -> '{fix.corrected}'")
```

### Suggested Fixes

```python
# Get suggestions without applying fixes
suggestions = corrector.get_suggestions(diagram)

for suggestion in suggestions:
    print(f"Line {suggestion.line}: {suggestion.description}")
    print(f"  Current: {suggestion.current}")
    print(f"  Suggested: {suggestion.suggested}")

    # Apply suggestion manually
    if input("Apply this fix? (y/n): ").lower() == 'y':
        diagram = suggestion.apply(diagram)
```

## Diagram-Specific Validation

### Flowchart Validation

```python
from diagramaid.validators import FlowchartValidator

validator = FlowchartValidator(
    require_start_node=True,
    require_end_node=True,
    max_decision_branches=5,
    check_infinite_loops=True
)

result = validator.validate(flowchart_diagram)
```

### Sequence Diagram Validation

```python
from diagramaid.validators import SequenceValidator

validator = SequenceValidator(
    check_participant_consistency=True,
    validate_message_flow=True,
    check_activation_balance=True
)

result = validator.validate(sequence_diagram)
```

### Class Diagram Validation

```python
from diagramaid.validators import ClassValidator

validator = ClassValidator(
    check_inheritance_cycles=True,
    validate_method_signatures=True,
    check_access_modifiers=True
)

result = validator.validate(class_diagram)
```

## Performance Validation

### Performance Checks

```python
from diagramaid.validators import PerformanceValidator

validator = PerformanceValidator(
    max_render_time=30,  # seconds
    max_memory_usage=100 * 1024 * 1024,  # 100MB
    warn_complex_diagrams=True
)

result = validator.validate(diagram)

for warning in result.performance_warnings:
    print(f"Performance warning: {warning.message}")
    print(f"  Estimated render time: {warning.estimated_time}s")
```

### Complexity Analysis

```python
from diagramaid.validators import ComplexityAnalyzer

analyzer = ComplexityAnalyzer()
complexity = analyzer.analyze(diagram)

print(f"Complexity score: {complexity.score}/100")
print(f"Node count: {complexity.node_count}")
print(f"Edge count: {complexity.edge_count}")
print(f"Nesting depth: {complexity.max_depth}")

if complexity.score > 80:
    print("Warning: High complexity diagram may render slowly")
```

## Accessibility Validation

### Accessibility Checks

```python
from diagramaid.validators import AccessibilityValidator

validator = AccessibilityValidator(
    check_color_contrast=True,
    check_text_size=True,
    check_alt_text=True,
    check_keyboard_navigation=True
)

result = validator.validate(diagram)

for issue in result.accessibility_issues:
    print(f"Accessibility issue: {issue.message}")
    print(f"  WCAG Level: {issue.wcag_level}")
    print(f"  Recommendation: {issue.recommendation}")
```

## Batch Validation

### Multiple Diagram Validation

```python
from diagramaid.validators import BatchValidator

validator = BatchValidator()

# Validate multiple diagrams
diagrams = [
    ("flowchart.mmd", flowchart_content),
    ("sequence.mmd", sequence_content),
    ("class.mmd", class_content)
]

results = validator.validate_batch(diagrams)

# Generate summary report
summary = validator.generate_summary(results)
print(f"Total diagrams: {summary.total}")
print(f"Valid diagrams: {summary.valid}")
print(f"Diagrams with errors: {summary.errors}")
print(f"Diagrams with warnings: {summary.warnings}")
```

### CI/CD Integration

```python
# Validation for continuous integration
from diagramaid.validators import CIValidator

ci_validator = CIValidator(
    fail_on_errors=True,
    fail_on_warnings=False,
    output_format="junit",
    output_file="validation_results.xml"
)

# Validate all diagrams in directory
exit_code = ci_validator.validate_directory("./diagrams")
sys.exit(exit_code)
```

## Configuration

### Validation Configuration

```python
from diagramaid.config import ValidationConfig

config = ValidationConfig(
    # Enable/disable validation types
    syntax_validation=True,
    semantic_validation=True,
    performance_validation=True,
    accessibility_validation=False,

    # Error handling
    strict_mode=False,
    max_errors=10,
    stop_on_first_error=False,

    # Auto-correction
    enable_auto_correction=True,
    auto_fix_syntax=True,
    auto_fix_formatting=True,

    # Custom rules
    custom_rules_directory="./validation_rules",

    # Output
    verbose_errors=True,
    include_suggestions=True,
    color_output=True
)
```

### Rule Configuration

```python
# Configure specific validation rules
rule_config = {
    "max_nodes": 200,
    "max_edges": 400,
    "max_nesting_depth": 8,
    "require_documentation": True,
    "enforce_naming_convention": "camelCase",
    "check_spelling": True,
    "dictionary_file": "custom_dictionary.txt"
}

validator = DiagramValidator(rule_config=rule_config)
```

## Integration Examples

### Web Application Integration

```python
from flask import Flask, request, jsonify

app = Flask(__name__)
validator = DiagramValidator()

@app.route('/validate', methods=['POST'])
def validate_endpoint():
    diagram = request.json['diagram']
    result = validator.validate(diagram)

    return jsonify({
        'valid': result.is_valid,
        'errors': [error.to_dict() for error in result.errors],
        'warnings': [warning.to_dict() for warning in result.warnings],
        'suggestions': [fix.to_dict() for fix in result.suggestions]
    })
```

### Editor Integration

```python
# Real-time validation for editors
class EditorValidator:
    def __init__(self):
        self.validator = DiagramValidator()
        self.debounce_timer = None

    def validate_on_change(self, diagram_content):
        # Debounce validation to avoid excessive calls
        if self.debounce_timer:
            self.debounce_timer.cancel()

        self.debounce_timer = Timer(0.5, self._validate, [diagram_content])
        self.debounce_timer.start()

    def _validate(self, content):
        result = self.validator.validate(content)
        self.update_editor_markers(result)
```

## Best Practices

### Validation Strategy

1. **Early Validation**: Validate during editing, not just before rendering
2. **Progressive Validation**: Start with syntax, then semantics
3. **User-Friendly Messages**: Provide clear, actionable error messages
4. **Performance Awareness**: Don't over-validate large diagrams

### Error Message Guidelines

```python
# Good error messages
ValidationError(
    message="Missing closing bracket for node 'A'",
    line=5,
    column=15,
    suggestion="Add ']' after node label",
    code="SYNTAX_BRACKET_001"
)

# Avoid vague messages
ValidationError(message="Syntax error")  # Too vague
```

## See Also

- [Error Handling Guide](../guides/error-handling.md)
- [Best Practices](../guides/best-practices.md)
- [API Reference](../api-reference/validators.md)
