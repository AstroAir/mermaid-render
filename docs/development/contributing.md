# Contributing

Thank you for your interest in contributing to Mermaid Render! This guide will help you get started with contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. We are committed to providing a welcoming and inclusive environment for all contributors.

## Ways to Contribute

### 🐛 Bug Reports

- Search existing issues first
- Use the bug report template
- Provide clear reproduction steps
- Include system information

### ✨ Feature Requests

- Check the roadmap and existing issues
- Use the feature request template
- Explain the use case and benefits
- Consider implementation complexity

### 📚 Documentation

- Fix typos and improve clarity
- Add examples and tutorials
- Update API documentation
- Translate content

### 💻 Code Contributions

- Bug fixes
- New features
- Performance improvements
- Test coverage improvements

## Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/mermaid-render.git
cd mermaid-render
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### 3. Create a Branch

```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Or a bug fix branch
git checkout -b fix/issue-number
```

## Development Workflow

### Code Style

We use several tools to maintain code quality:

```bash
# Format code
black mermaid_render tests

# Sort imports
isort mermaid_render tests

# Lint code
ruff check mermaid_render tests

# Type checking
mypy mermaid_render

# Run all checks
make check-all
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=mermaid_render --cov-report=html

# Run specific test file
pytest tests/test_core.py

# Run tests for specific functionality
pytest -k "test_flowchart"
```

### Documentation

```bash
# Build documentation locally
mkdocs serve

# Check for broken links
mkdocs build --strict
```

## Contribution Guidelines

### Code Quality

- **Type Hints**: All new code must include type hints
- **Documentation**: Public APIs must have comprehensive docstrings
- **Tests**: New features require tests with >90% coverage
- **Performance**: Consider performance impact of changes

### Commit Messages

Use conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build/tooling changes

Examples:

```
feat(models): add support for timeline diagrams

fix(renderers): handle timeout errors gracefully

docs(api): improve FlowchartDiagram examples
```

### Pull Request Process

1. **Create Quality PR**

   - Clear title and description
   - Link related issues
   - Include screenshots for UI changes
   - Update documentation if needed

2. **Ensure CI Passes**

   - All tests pass
   - Code coverage maintained
   - Linting passes
   - Type checking passes

3. **Request Review**

   - Tag relevant maintainers
   - Respond to feedback promptly
   - Make requested changes

4. **Merge**
   - Squash commits if requested
   - Update changelog if needed

## Development Setup Details

### Project Structure

```
mermaid_render/
├── mermaid_render/          # Main package
│   ├── core.py             # Core classes
│   ├── models/             # Diagram models
│   ├── renderers/          # Rendering backends
│   ├── utils/              # Utilities
│   └── ...
├── tests/                  # Test suite
├── docs/                   # Documentation
├── examples/               # Example scripts
└── tools/                  # Development tools
```

### Adding New Diagram Types

1. **Create Model Class**

   ```python
   # mermaid_render/models/new_diagram.py
   from .base import BaseDiagram

   class NewDiagram(BaseDiagram):
       def __init__(self, title: Optional[str] = None):
           super().__init__(title)
           # Implementation
   ```

2. **Add Tests**

   ```python
   # tests/models/test_new_diagram.py
   def test_new_diagram_creation():
       diagram = NewDiagram(title="Test")
       assert diagram.title == "Test"
   ```

3. **Update Documentation**

   - Add to API reference
   - Include in user guide
   - Add examples

4. **Export in **init**.py**

   ```python
   from .models.new_diagram import NewDiagram
   __all__ = [..., "NewDiagram"]
   ```

### Adding New Features

1. **Design First**

   - Create issue for discussion
   - Consider API design
   - Plan implementation

2. **Implement**

   - Follow existing patterns
   - Add comprehensive tests
   - Update documentation

3. **Review**
   - Self-review code
   - Test edge cases
   - Check performance impact

## Testing Guidelines

### Test Structure

```python
import pytest
from mermaid_render import FlowchartDiagram

class TestFlowchartDiagram:
    def test_creation(self):
        """Test basic diagram creation."""
        diagram = FlowchartDiagram(title="Test")
        assert diagram.title == "Test"

    def test_add_node(self):
        """Test adding nodes to diagram."""
        diagram = FlowchartDiagram()
        node = diagram.add_node("A", "Start")
        assert node.id == "A"
        assert node.label == "Start"

    @pytest.mark.parametrize("shape", ["circle", "diamond", "rectangle"])
    def test_node_shapes(self, shape):
        """Test different node shapes."""
        diagram = FlowchartDiagram()
        node = diagram.add_node("A", "Test", shape=shape)
        assert node.shape == shape
```

### Test Categories

- **Unit Tests**: Test individual functions/methods
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete workflows
- **Performance Tests**: Test performance characteristics

## Documentation Guidelines

### Docstring Format

Use Google-style docstrings:

```python
def add_node(self, id: str, label: str, shape: str = "rectangle") -> Node:
    """Add a node to the diagram.

    Args:
        id: Unique node identifier
        label: Display text for the node
        shape: Shape of the node (rectangle, circle, diamond)

    Returns:
        The created Node object

    Raises:
        DiagramError: If node ID already exists

    Examples:
        >>> diagram = FlowchartDiagram()
        >>> node = diagram.add_node("start", "Begin Process", shape="circle")
        >>> print(node.id)
        start
    """
```

### Documentation Types

- **API Reference**: Auto-generated from docstrings
- **User Guide**: Tutorials and examples
- **Examples**: Real-world usage patterns
- **Development**: Contributing and setup guides

## Release Process

### Version Numbers

We follow semantic versioning (SemVer):

- **Major** (1.0.0 → 2.0.0): Breaking changes
- **Minor** (1.0.0 → 1.1.0): New features, backward compatible
- **Patch** (1.0.0 → 1.0.1): Bug fixes, backward compatible

### Release Checklist

1. **Prepare Release**

   - Update version numbers
   - Update changelog
   - Run full test suite
   - Update documentation

2. **Create Release**

   - Tag release in Git
   - Build and publish to PyPI
   - Create GitHub release
   - Update documentation site

3. **Post-Release**
   - Announce release
   - Update examples
   - Monitor for issues

## Getting Help

### Development Questions

- **GitHub Discussions**: General questions and ideas
- **GitHub Issues**: Bug reports and feature requests
- **Discord**: Real-time chat with maintainers
- **Email**: Direct contact for sensitive issues

### Resources

- **Documentation**: Comprehensive guides and API reference
- **Examples**: Real-world usage patterns
- **Tests**: Look at existing tests for patterns
- **Code**: Browse the codebase for implementation details

## Recognition

We value all contributions and recognize contributors in:

- README.md contributors section
- Release notes and changelogs
- GitHub contributors page
- Annual contributor highlights

### Contributor Levels

- **Contributor**: Made at least one merged contribution
- **Regular Contributor**: Multiple contributions over time
- **Core Contributor**: Significant ongoing contributions
- **Maintainer**: Commit access and release responsibilities

## Thank You

Every contribution, no matter how small, helps make Mermaid Render better for everyone. We appreciate your time and effort in improving the project!

## Next Steps

Ready to contribute? Here's what to do next:

1. **[Set up your development environment](setup.md)**
2. **Browse [open issues](https://github.com/mermaid-render/mermaid-render/issues)**
3. **Join our [Discord community](https://discord.gg/mermaid-render)**
4. **Read the [testing guide](testing.md)**

Welcome to the Mermaid Render community! 🎉
