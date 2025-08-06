# Examples

This section contains practical examples and code samples for using Mermaid Render in various scenarios.

## 🚀 Quick Start Examples

### [Basic Usage Examples](../../examples/basic_usage.py)

Fundamental features including flowcharts, sequence diagrams, themes, and validation.

- Simple diagram creation
- Theme application
- File export
- Validation patterns

### [Advanced Usage Examples](../../examples/advanced_usage.py)

Complex features including custom themes, configuration management, and batch processing.

- Custom theme creation
- Configuration management
- Batch processing
- Error handling
- Complex diagrams with styling

## 📊 Diagram Type Examples

### [Complete Diagram Types Showcase](../../examples/diagram_types_showcase.py)

Comprehensive examples for all supported diagram types with practical use cases:

- **State Diagrams**: User authentication state machines
- **ER Diagrams**: E-commerce database schemas
- **User Journey**: Online shopping customer journeys
- **Gantt Charts**: Software development project timelines
- **Pie Charts**: Technology stack distributions
- **Git Graphs**: Feature development workflows
- **Mindmaps**: Project planning hierarchies

## 🤖 AI-Powered Features

### [AI Features Showcase](../../examples/ai_features_showcase.py)

Demonstrate AI capabilities for intelligent diagram generation:

- **Natural Language Generation**: Create diagrams from text descriptions
- **Code Analysis**: Generate diagrams from source code
- **Diagram Optimization**: AI-powered layout and style improvements
- **Quality Analysis**: Automated diagram quality assessment
- **Smart Suggestions**: AI recommendations for diagram improvements

## 📋 Template System

### [Template System Showcase](../../examples/template_system_showcase.py)

Template-based diagram generation and reusable patterns:

- **Built-in Templates**: Using pre-built diagram templates
- **Custom Templates**: Creating custom Jinja2-based templates
- **Diagram Generators**: FlowchartGenerator, SequenceGenerator, ArchitectureGenerator
- **Template Management**: Template creation, validation, and organization

## 🔗 Integration Examples

### [Integration Patterns](../../examples/integration_examples.py)

Real-world integration patterns for web frameworks and applications:

- **Flask Integration**: Complete web application with diagram editor
- **FastAPI Integration**: REST API service with interactive documentation
- **Advanced CLI**: Comprehensive command-line tool with batch processing
- **CI/CD Integration**: Automated diagram generation in build pipelines

## 🌍 Real-World Use Cases

### [Real-World Applications](../../examples/real_world_use_cases.py)

Practical applications demonstrating professional use cases:

- **Software Architecture Documentation**: Complete system architecture with microservices
- **API Documentation**: REST API structure and authentication flows
- **Business Process Modeling**: Customer onboarding and journey mapping
- **Database Design**: Comprehensive ER diagrams for e-commerce systems

## ⚡ Performance & Optimization

### [Performance & Caching Showcase](../../examples/performance_caching_showcase.py)

Performance optimization strategies and caching implementations:

- **Basic Caching**: Memory-based caching for improved performance
- **Advanced Caching**: File and Redis-based distributed caching
- **Performance Monitoring**: Built-in performance tracking and metrics
- **Cache Optimization**: Intelligent cache management and cleanup
- **Benchmark Comparisons**: Performance analysis with and without caching

## 🧪 Testing & Validation

### [Testing & Validation Showcase](../../examples/testing_validation_showcase.py)

Comprehensive testing patterns and validation strategies:

- **Unit Testing**: Testing diagram creation and rendering
- **Mock Testing**: Testing with mocked dependencies
- **Integration Testing**: Testing application services using the library
- **Validation Patterns**: Comprehensive syntax validation examples
- **Error Handling**: Robust error handling and recovery patterns

## 🤝 Interactive & Collaboration

### [Interactive & Collaboration Showcase](../../examples/interactive_collaboration_showcase.py)

Real-time collaboration and interactive editing features:

- **Interactive Builder**: Step-by-step diagram construction
- **Collaborative Editing**: Multi-user real-time editing simulation
- **Version Control**: Git-like version control for diagrams
- **Real-time Collaboration**: Live cursor tracking and change synchronization

## 🚀 Run All Examples

### [Complete Examples Runner](../../examples/run_all_examples.py)

Comprehensive script that runs all examples and generates detailed reports:

```bash
# Run all examples at once
python examples/run_all_examples.py

# This will:
# - Execute all example scripts
# - Generate performance reports
# - Create HTML summary with results
# - Organize all output files
```

**Features:**

- **Automated Execution**: Runs all examples with timeout protection
- **Performance Tracking**: Measures execution time for each example
- **Error Handling**: Captures and reports any failures
- **HTML Reports**: Generates comprehensive HTML reports
- **File Organization**: Organizes all generated diagrams and data

## 📁 Example Repository Structure

```
examples/
├── basic_usage.py                          # Fundamental features
├── advanced_usage.py                       # Complex configurations
├── diagram_types_showcase.py               # All diagram types
├── ai_features_showcase.py                 # AI-powered features
├── template_system_showcase.py             # Template system
├── integration_examples.py                 # Web frameworks & CLI
├── real_world_use_cases.py                # Practical applications
├── performance_caching_showcase.py         # Performance optimization
├── testing_validation_showcase.py          # Testing patterns
├── interactive_collaboration_showcase.py   # Collaboration features
└── run_all_examples.py                    # Execute all examples

output/                                     # Generated files
├── basic/                                  # Basic example outputs
├── advanced/                              # Advanced example outputs
├── diagram_types/                         # All diagram type examples
├── ai_features/                           # AI-generated diagrams
├── templates/                             # Template-generated diagrams
├── integration/                           # Integration code examples
├── real_world/                            # Real-world use cases
├── performance/                           # Performance reports
├── testing/                               # Test results
├── interactive/                           # Collaboration examples
├── example_execution_summary.json         # Execution summary
└── example_execution_report.html          # Detailed HTML report
```

## 🎯 Getting Started

### Quick Start Guide

1. **Choose Your Starting Point**:
   - New to the library? Start with [Basic Usage Examples](../../examples/basic_usage.py)
   - Need specific diagram types? Check [Diagram Types Showcase](../../examples/diagram_types_showcase.py)
   - Building an application? See [Integration Examples](../../examples/integration_examples.py)

2. **Run Examples Locally**:

   ```bash
   # Clone the repository
   git clone https://github.com/mermaid-render/mermaid-render.git
   cd mermaid-render

   # Install with examples dependencies
   pip install -e ".[dev,examples]"

   # Run individual examples
   python examples/basic_usage.py
   python examples/diagram_types_showcase.py

   # Or run all examples at once
   python examples/run_all_examples.py
   ```

3. **Explore Generated Files**:
   - All examples generate files in the `output/` directory
   - Check the HTML report for detailed execution results
   - Browse generated diagrams organized by category

### Example Dependencies

Different examples may require additional dependencies:

- **Basic Examples**: No additional dependencies
- **AI Features**: `pip install mermaid-render[ai]`
- **Templates**: `pip install mermaid-render[templates]`
- **Caching**: `pip install mermaid-render[cache]`
- **Interactive**: `pip install mermaid-render[interactive]`
- **Collaboration**: `pip install mermaid-render[collaboration]`
- **All Features**: `pip install mermaid-render[all]`

## 💡 Tips for Using Examples

### Customization

- All examples are designed to be easily modified
- Change diagram content, themes, and output formats to suit your needs
- Use examples as starting points for your own applications

### Performance

- Run the performance examples to understand optimization strategies
- Use caching for production applications with frequent diagram generation
- Monitor performance with the built-in performance tracking tools

### Integration

- Web framework examples show complete integration patterns
- CLI examples demonstrate command-line tool development
- Use the testing examples to ensure robust applications

### Troubleshooting

- Check the validation examples for syntax error handling
- Review error handling patterns for robust applications
- Use the testing showcase for debugging strategies

## 🤝 Contributing Examples

We welcome contributions of new examples! To contribute:

1. **Follow the Pattern**: Use existing examples as templates
2. **Add Documentation**: Include clear comments and descriptions
3. **Test Thoroughly**: Ensure examples work with different configurations
4. **Submit PR**: Create a pull request with your new examples

### Example Guidelines

- **Clear Purpose**: Each example should demonstrate specific features
- **Self-Contained**: Examples should run independently
- **Well-Commented**: Include explanatory comments
- **Error Handling**: Show proper error handling patterns
- **Output Generation**: Generate visual outputs when possible

## 📚 Additional Resources

- **[API Documentation](../api/index.md)**: Complete API reference
- **[User Guide](../guides/index.md)**: Step-by-step tutorials
- **[GitHub Repository](https://github.com/mermaid-render/mermaid-render)**: Source code and issues
- **[Community Discussions](https://github.com/mermaid-render/mermaid-render/discussions)**: Ask questions and share ideas

---

**Ready to get started?** Run `python examples/run_all_examples.py` to see all features in action!
