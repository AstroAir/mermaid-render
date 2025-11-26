# Template System

Mermaid Render includes a powerful template system for generating diagrams from structured data and creating reusable diagram patterns.

## Overview

The template system provides:

- **Data-Driven Diagrams**: Generate diagrams from JSON, CSV, databases
- **Template Engine**: Jinja2-based templating with Mermaid-specific extensions
- **Reusable Patterns**: Create and share diagram templates
- **Dynamic Content**: Real-time data integration
- **Multi-Format Support**: Templates for all diagram types

## Quick Start

### Basic Template Usage

```python
from mermaid_render.templates import TemplateManager

# Create template manager
template_manager = TemplateManager()

# Define a simple template
flowchart_template = """
flowchart TD
{% for step in steps %}
    {{ step.id }}[{{ step.name }}]
    {% if not loop.last %}
    {{ step.id }} --> {{ steps[loop.index].id }}
    {% endif %}
{% endfor %}
"""

# Register template
template_manager.register_template("process_flow", flowchart_template)

# Use template with data
data = {
    "steps": [
        {"id": "A", "name": "Start"},
        {"id": "B", "name": "Process"},
        {"id": "C", "name": "End"}
    ]
}

diagram = template_manager.render("process_flow", data)
```

## Template Types

### Flowchart Templates

```python
# Organizational chart template
org_chart_template = """
flowchart TD
{% for person in organization %}
    {{ person.id }}[{{ person.name }}<br/>{{ person.title }}]
    {% if person.manager %}
    {{ person.manager }} --> {{ person.id }}
    {% endif %}
{% endfor %}
"""

# Use with organizational data
org_data = {
    "organization": [
        {"id": "CEO", "name": "John Smith", "title": "CEO", "manager": None},
        {"id": "CTO", "name": "Jane Doe", "title": "CTO", "manager": "CEO"},
        {"id": "DEV1", "name": "Bob Wilson", "title": "Developer", "manager": "CTO"}
    ]
}
```

### Sequence Diagram Templates

```python
# API interaction template
api_template = """
sequenceDiagram
    participant Client
    participant API
    participant Database

{% for endpoint in endpoints %}
    Client->>API: {{ endpoint.method }} {{ endpoint.path }}
    {% if endpoint.requires_auth %}
    API->>API: Validate Token
    {% endif %}
    {% if endpoint.database_access %}
    API->>Database: {{ endpoint.query_type }}
    Database-->>API: {{ endpoint.response_type }}
    {% endif %}
    API-->>Client: {{ endpoint.status_code }} {{ endpoint.response }}
{% endfor %}
"""
```

### Class Diagram Templates

```python
# Database schema template
schema_template = """
classDiagram
{% for table in tables %}
    class {{ table.name }} {
        {% for column in table.columns %}
        {{ column.type }} {{ column.name }}
        {% endfor %}
        {% for method in table.methods %}
        {{ method.name }}()
        {% endfor %}
    }
{% endfor %}

{% for relation in relationships %}
    {{ relation.from }} {{ relation.type }} {{ relation.to }}
{% endfor %}
"""
```

## Data Sources

### JSON Data

```python
from mermaid_render.templates import JSONDataSource

# Load data from JSON file
json_source = JSONDataSource("data/process.json")
data = json_source.load()

diagram = template_manager.render("process_flow", data)
```

### CSV Data

```python
from mermaid_render.templates import CSVDataSource

# Load data from CSV
csv_source = CSVDataSource(
    file_path="data/employees.csv",
    mapping={
        "id": "employee_id",
        "name": "full_name",
        "title": "job_title",
        "manager": "manager_id"
    }
)

data = csv_source.load()
```

### Database Integration

```python
from mermaid_render.templates import DatabaseDataSource

# Connect to database
db_source = DatabaseDataSource(
    connection_string="postgresql://user:pass@localhost/db",
    query="""
        SELECT id, name, title, manager_id as manager
        FROM employees
        ORDER BY hierarchy_level
    """
)

data = db_source.load()
```

### API Data Sources

```python
from mermaid_render.templates import APIDataSource

# Fetch data from REST API
api_source = APIDataSource(
    url="https://api.example.com/processes",
    headers={"Authorization": "Bearer token"},
    transform=lambda data: {"steps": data["workflow_steps"]}
)

data = api_source.load()
```

## Template Features

### Conditional Logic

```python
conditional_template = """
flowchart TD
{% for node in nodes %}
    {{ node.id }}[{{ node.name }}]
    {% if node.type == 'decision' %}
    {{ node.id }}{{{ node.name }}}
    {% elif node.type == 'process' %}
    {{ node.id }}[{{ node.name }}]
    {% elif node.type == 'terminal' %}
    {{ node.id }}({{ node.name }})
    {% endif %}
{% endfor %}
"""
```

### Loops and Iteration

```python
nested_template = """
flowchart TD
{% for department in departments %}
    subgraph {{ department.name }}
    {% for employee in department.employees %}
        {{ department.id }}_{{ employee.id }}[{{ employee.name }}]
    {% endfor %}
    end
{% endfor %}
"""
```

### Custom Filters

```python
# Register custom filters
@template_manager.filter('snake_case')
def snake_case(text):
    return text.lower().replace(' ', '_')

@template_manager.filter('format_date')
def format_date(date_str):
    from datetime import datetime
    date = datetime.fromisoformat(date_str)
    return date.strftime('%Y-%m-%d')

# Use in templates
template_with_filters = """
flowchart TD
{% for task in tasks %}
    {{ task.name | snake_case }}[{{ task.name }}<br/>Due: {{ task.due_date | format_date }}]
{% endfor %}
"""
```

## Template Management

### Template Registry

```python
from mermaid_render.templates import TemplateRegistry

# Create registry
registry = TemplateRegistry()

# Register templates
registry.register_from_file("flowchart_basic", "templates/flowchart_basic.mmd")
registry.register_from_directory("templates/")

# List available templates
templates = registry.list_templates()
for template in templates:
    print(f"{template.name}: {template.description}")
```

### Template Inheritance

```python
# Base template
base_template = """
{% block diagram_type %}flowchart TD{% endblock %}
{% block content %}
    A[Start] --> B[End]
{% endblock %}
"""

# Child template
child_template = """
{% extends "base_flowchart" %}
{% block content %}
{% for step in steps %}
    {{ step.id }}[{{ step.name }}]
    {% if not loop.last %}
    {{ step.id }} --> {{ steps[loop.index].id }}
    {% endif %}
{% endfor %}
{% endblock %}
"""
```

### Template Composition

```python
# Reusable components
components = {
    "error_handling": """
    {% macro error_handler(node_id) %}
    {{ node_id }}_error{Error Occurred}
    {{ node_id }} --> {{ node_id }}_error
    {{ node_id }}_error --> End
    {% endmacro %}
    """,

    "logging": """
    {% macro add_logging(node_id, message) %}
    {{ node_id }}_log[Log: {{ message }}]
    {{ node_id }} --> {{ node_id }}_log
    {% endmacro %}
    """
}

# Use components in templates
template_with_components = """
{% from 'components' import error_handler, add_logging %}
flowchart TD
    Start --> Process
    {{ error_handler('Process') }}
    {{ add_logging('Process', 'Processing started') }}
"""
```

## Dynamic Templates

### Real-time Data Updates

```python
from mermaid_render.templates import DynamicTemplate

# Create dynamic template that updates with data changes
dynamic_template = DynamicTemplate(
    template_name="live_dashboard",
    data_source=api_source,
    update_interval=30,  # seconds
    auto_refresh=True
)

# Subscribe to updates
@dynamic_template.on_update
def handle_update(new_diagram):
    print("Diagram updated with new data")
    # Update UI, send to clients, etc.
```

### Parameterized Templates

```python
# Template with parameters
parameterized_template = """
flowchart {{ direction | default('TD') }}
{% for item in items %}
    {{ item.id }}[{{ item.name }}]
    {% if item.style %}
    {{ item.id }} --> {{ item.id }}_styled
    {{ item.id }}_styled[{{ item.name }}]
    style {{ item.id }}_styled fill:{{ item.style.color }}
    {% endif %}
{% endfor %}
"""

# Render with parameters
diagram = template_manager.render(
    "parameterized_flow",
    data,
    parameters={"direction": "LR"}
)
```

## Advanced Features

### Template Validation

```python
from mermaid_render.templates import TemplateValidator

validator = TemplateValidator()

# Validate template syntax
validation_result = validator.validate_template(template_content)
if not validation_result.is_valid:
    for error in validation_result.errors:
        print(f"Error: {error.message} at line {error.line}")
```

### Template Optimization

```python
from mermaid_render.templates import TemplateOptimizer

optimizer = TemplateOptimizer()

# Optimize template for performance
optimized_template = optimizer.optimize(template_content)
print(f"Optimization saved {optimizer.get_savings()}% render time")
```

### Caching

```python
# Enable template caching
template_manager.enable_caching(
    cache_compiled_templates=True,
    cache_rendered_diagrams=True,
    cache_ttl=3600  # 1 hour
)
```

## Integration Examples

### Web Framework Integration

```python
from flask import Flask, render_template_string
from mermaid_render.templates import FlaskIntegration

app = Flask(__name__)
mermaid_integration = FlaskIntegration(app, template_manager)

@app.route('/diagram/<template_name>')
def show_diagram(template_name):
    data = get_data_for_template(template_name)
    return mermaid_integration.render_template(template_name, data)
```

### CI/CD Integration

```python
# Generate diagrams in CI/CD pipeline
from mermaid_render.templates import CIIntegration

ci_integration = CIIntegration(template_manager)

# Generate architecture diagram from code
architecture_data = ci_integration.analyze_codebase("./src")
diagram = template_manager.render("architecture", architecture_data)

# Save to documentation
with open("docs/architecture.svg", "w") as f:
    f.write(diagram.render(format="svg"))
```

## Configuration

### Template Settings

```python
from mermaid_render.config import TemplateConfig

config = TemplateConfig(
    template_directory="./templates",
    auto_reload=True,
    strict_mode=False,
    enable_caching=True,
    cache_size=1000
)

template_manager = TemplateManager(config=config)
```

### Security Settings

```python
# Configure template security
config.security = {
    "sandbox_mode": True,
    "allowed_functions": ["range", "len", "enumerate"],
    "blocked_attributes": ["__class__", "__globals__"],
    "max_template_size": 1024 * 1024,  # 1MB
    "execution_timeout": 30  # seconds
}
```

## Best Practices

### Template Organization

```
templates/
├── base/
│   ├── flowchart.mmd
│   └── sequence.mmd
├── components/
│   ├── error_handling.mmd
│   └── logging.mmd
├── business/
│   ├── process_flow.mmd
│   └── org_chart.mmd
└── technical/
    ├── architecture.mmd
    └── database_schema.mmd
```

### Performance Tips

- Use template caching for frequently rendered diagrams
- Minimize data processing in templates
- Use lazy loading for large datasets
- Optimize database queries in data sources

### Error Handling

```python
try:
    diagram = template_manager.render(template_name, data)
except TemplateNotFoundError:
    print(f"Template {template_name} not found")
except TemplateRenderError as e:
    print(f"Template render error: {e.message}")
except DataSourceError as e:
    print(f"Data source error: {e.message}")
```

## See Also

- [Data Integration Guide](../guides/data-integration.md)
- [Template Examples](../examples/templates.md)
- [API Reference](../api-reference/templates.md)
