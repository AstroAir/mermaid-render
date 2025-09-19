# Mermaid Render Examples

This directory contains comprehensive examples demonstrating all features of the Mermaid Render library. Each example is self-contained and includes detailed comments explaining the concepts and usage patterns.

## 🚀 Quick Start

### Run All Examples
```bash
# Execute all examples and generate comprehensive reports
python run_all_examples.py
```

### Run Individual Examples
```bash
# Basic features
python basic_usage.py

# All diagram types
python diagram_types_showcase.py

# AI-powered features (requires AI dependencies)
python ai_features_showcase.py

# And so on...
```

## 📋 Available Examples

### 1. [Basic Usage](basic_usage.py)
**Fundamental features and simple diagrams**
- Flowchart and sequence diagram creation
- Theme application and customization
- File export and validation
- Quick rendering utilities

**Key Concepts**: Basic API usage, diagram creation, rendering pipeline

### 2. [Advanced Usage](advanced_usage.py)
**Complex features and configurations**
- Custom theme creation and management
- Configuration management
- Batch processing and export
- Complex diagrams with styling
- Error handling patterns

**Key Concepts**: Advanced configuration, batch operations, custom styling

### 3. [Diagram Types Showcase](diagram_types_showcase.py)
**All supported diagram types with practical examples**
- State diagrams (authentication systems)
- ER diagrams (database schemas)
- User journey maps (customer experiences)
- Gantt charts (project timelines)
- Pie charts (data visualization)
- Git graphs (development workflows)
- Mindmaps (project planning)

**Key Concepts**: Diagram type diversity, real-world applications

### 4. [AI Features Showcase](ai_features_showcase.py)
**AI-powered diagram generation and optimization**
- Natural language to diagram generation
- Code analysis and diagram creation
- Diagram optimization and suggestions
- Quality analysis and recommendations

**Key Concepts**: AI integration, natural language processing, optimization

**Dependencies**: `pip install mermaid-render[ai]`

### 5. [Template System Showcase](template_system_showcase.py)
**Template-based diagram generation**
- Built-in template usage
- Custom template creation
- Diagram generators (Flowchart, Sequence, Architecture)
- Template management and organization

**Key Concepts**: Template systems, code generation, reusable patterns

**Dependencies**: `pip install mermaid-render[templates]`

### 6. [Integration Examples](integration_examples.py)
**Web frameworks and application integration**
- Flask web application with diagram editor
- FastAPI REST API service
- Advanced CLI tool development
- CI/CD integration patterns

**Key Concepts**: Web integration, API development, automation

### 7. [Real-World Use Cases](real_world_use_cases.py)
**Practical applications and professional scenarios**
- Software architecture documentation
- API documentation generation
- Business process modeling
- Database design and ER diagrams

**Key Concepts**: Professional applications, documentation automation

### 8. [Performance & Caching Showcase](performance_caching_showcase.py)
**Performance optimization and caching strategies**
- Memory and file-based caching
- Performance monitoring and metrics
- Cache optimization techniques
- Benchmark comparisons

**Key Concepts**: Performance optimization, caching strategies, monitoring

**Dependencies**: `pip install mermaid-render[cache]`

### 9. [Testing & Validation Showcase](testing_validation_showcase.py)
**Testing patterns and validation strategies**
- Unit testing with mocks
- Integration testing patterns
- Validation and error handling
- Application testing strategies

**Key Concepts**: Testing methodologies, validation, error handling



## 📁 Output Structure

All examples generate organized output in the `output/` directory:

```
output/
├── basic/                    # Basic usage outputs
├── advanced/                 # Advanced feature outputs
├── diagram_types/            # All diagram type examples
├── ai_features/              # AI-generated content
├── templates/                # Template-generated diagrams
├── integration/              # Integration code examples
├── real_world/               # Professional use cases
├── performance/              # Performance reports and data
├── testing/                  # Test results and validation
├── interactive/              # Collaboration examples
├── example_execution_summary.json    # Execution summary
└── example_execution_report.html     # Detailed HTML report
```

## 🔧 Dependencies

### Core Examples (No additional dependencies)
- `basic_usage.py`
- `advanced_usage.py`
- `diagram_types_showcase.py`
- `integration_examples.py`
- `real_world_use_cases.py`
- `testing_validation_showcase.py`

### Optional Dependencies
- **AI Features**: `pip install mermaid-render[ai]`
- **Templates**: `pip install mermaid-render[templates]`
- **Caching**: `pip install mermaid-render[cache]`
- **Interactive**: `pip install mermaid-render[interactive]`

- **All Features**: `pip install mermaid-render[all]`

## 🎯 Learning Path

### Beginner
1. Start with `basic_usage.py` to understand fundamentals
2. Explore `diagram_types_showcase.py` to see all diagram types
3. Try `real_world_use_cases.py` for practical applications

### Intermediate
1. Study `advanced_usage.py` for complex configurations
2. Examine `integration_examples.py` for application patterns
3. Review `testing_validation_showcase.py` for robust development

### Advanced
1. Explore `ai_features_showcase.py` for AI capabilities
2. Study `template_system_showcase.py` for automation
3. Investigate `performance_caching_showcase.py` for optimization

## 🤝 Contributing

To contribute new examples:

1. **Follow Existing Patterns**: Use current examples as templates
2. **Include Documentation**: Add clear comments and docstrings
3. **Test Thoroughly**: Ensure examples work in different environments
4. **Generate Outputs**: Create visual examples when possible
5. **Update Documentation**: Add your example to this README

### Example Template
```python
#!/usr/bin/env python3
"""
Brief description of what this example demonstrates.

Detailed explanation of concepts covered and use cases.
"""

from pathlib import Path
from mermaid_render import MermaidRenderer

def create_output_dir():
    """Create output directory for examples."""
    output_dir = Path("output/your_example")
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

def your_example_function(output_dir: Path):
    """Demonstrate specific functionality."""
    print("Your example description...")
    
    # Your example code here
    
    print(f"✅ Example completed")

def main():
    """Run all examples in this script."""
    print("=== Your Example Title ===\n")
    
    output_dir = create_output_dir()
    print(f"Output directory: {output_dir.absolute()}\n")
    
    try:
        your_example_function(output_dir)
        print("✅ All examples completed successfully!")
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    main()
```

## 📚 Additional Resources

- **[Documentation](../docs/examples/index.md)**: Complete examples documentation
- **[API Reference](../docs/api/index.md)**: Detailed API documentation
- **[User Guide](../docs/guides/index.md)**: Step-by-step tutorials
- **[GitHub Issues](https://github.com/mermaid-render/mermaid-render/issues)**: Report bugs or request features

---

**Happy diagramming!** 🎨
