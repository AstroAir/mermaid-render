# Templates Module

This module provides a comprehensive template system for generating Mermaid diagrams from structured data sources and predefined patterns.

## Components

### Core Template System

- **`template_manager.py`** - Template management, storage, and retrieval
- **`schema.py`** - Template schema definition and validation
- **`library.py`** - Built-in template library and catalog

### Data Integration

- **`data_sources.py`** - Data source connectors (JSON, CSV, API, Database)
- **`generators.py`** - Specialized diagram generators for common patterns

### Supporting Infrastructure

- **`utils.py`** - Utility functions for template operations

## Key Features

- **Template Library**: Pre-built templates for common diagram patterns
- **Data Source Integration**: Generate diagrams from various data sources
- **Schema Validation**: Ensure template consistency and correctness
- **Custom Templates**: Create and manage custom diagram templates
- **Batch Generation**: Generate multiple diagrams from datasets

## Template Types

### Built-in Generators

- **FlowchartGenerator**: Process flows and workflows
- **SequenceGenerator**: API interactions and system communications
- **ClassDiagramGenerator**: Object-oriented design patterns
- **ArchitectureGenerator**: System architecture diagrams
- **ProcessFlowGenerator**: Business process modeling

## Usage Example

```python
from mermaid_render.templates import TemplateManager, FlowchartGenerator

# Use built-in generator
generator = FlowchartGenerator()
diagram = generator.generate_process_flow([
    {"id": "start", "label": "Start", "type": "start"},
    {"id": "process", "label": "Process Data", "type": "process"},
    {"id": "end", "label": "End", "type": "end"}
])

# Use template manager
template_manager = TemplateManager()
template = template_manager.get_template("user-journey")
diagram = template_manager.generate_from_template(
    template_name="user-journey",
    data={"steps": ["Login", "Browse", "Purchase", "Logout"]}
)
```

## Data Sources

The module supports multiple data sources:

```python
from mermaid_render.templates import JSONDataSource, APIDataSource

# JSON data source
json_source = JSONDataSource("data.json")
data = json_source.load()

# API data source
api_source = APIDataSource("https://api.example.com/workflow")
data = api_source.fetch()
```

## Dependencies

This module is included in the core installation and has no additional dependencies.
