# Installation

This guide covers different ways to install Mermaid Render and its dependencies.

## Basic Installation

The simplest way to install Mermaid Render is using pip:

```bash
pip install mermaid-render
```

This installs the core library with basic functionality for creating and rendering diagrams to SVG format.

## Installation with Optional Features

Mermaid Render offers several optional feature sets that you can install based on your needs:

### Full Installation (Recommended)

```bash
pip install mermaid-render[all]
```

This installs all optional features and is recommended for most users.

### Specific Feature Sets

```bash
# PDF export support
pip install mermaid-render[pdf]

# Redis caching support
pip install mermaid-render[cache]

# AI-powered features
pip install mermaid-render[ai]

# Interactive web interface
pip install mermaid-render[interactive]

# Collaboration features
pip install mermaid-render[collaboration]

# Development dependencies
pip install mermaid-render[dev]

# Documentation building
pip install mermaid-render[docs]
```

### Combining Features

You can combine multiple feature sets:

```bash
pip install mermaid-render[pdf,cache,ai]
```

## System Requirements

### Core Requirements

- **Python**: 3.9 or higher
- **Operating System**: Windows, macOS, Linux
- **Memory**: Minimum 512MB RAM (2GB+ recommended for AI features)
- **Network**: Internet connection required for online rendering services

### Optional Dependencies

| Feature        | Package                 | Purpose                     |
| -------------- | ----------------------- | --------------------------- |
| PDF Export     | `cairosvg`              | Convert SVG to PDF format   |
| Redis Cache    | `redis`                 | High-performance caching    |
| AI Features    | `openai`, `anthropic`   | Natural language processing |
| Interactive UI | `fastapi`, `websockets` | Web-based diagram builder   |

## Virtual Environment (Recommended)

It's recommended to install Mermaid Render in a virtual environment:

```bash
# Create virtual environment
python -m venv mermaid_env

# Activate virtual environment
# On Windows:
mermaid_env\Scripts\activate
# On macOS/Linux:
source mermaid_env/bin/activate

# Install Mermaid Render
pip install mermaid-render[all]
```

## Development Installation

If you want to contribute to Mermaid Render or need the latest development version:

```bash
# Clone the repository
git clone https://github.com/mermaid-render/mermaid-render.git
cd mermaid-render

# Install in development mode
pip install -e ".[dev]"
```

## Verification

Verify your installation by running:

```python
import mermaid_render
print(mermaid_render.__version__)

# Test basic functionality
from mermaid_render import quick_render

diagram_code = """
flowchart TD
    A[Start] --> B[End]
"""

svg_content = quick_render(diagram_code)
print("✅ Installation successful!")
```

## Troubleshooting

### Common Issues

#### Installation Fails with Dependency Conflicts

**Solution**: Use a fresh virtual environment:

```bash
python -m venv fresh_env
source fresh_env/bin/activate  # On Windows: fresh_env\Scripts\activate
pip install mermaid-render[all]
```

#### PDF Export Not Working

**Solution**: Install PDF dependencies:

```bash
pip install mermaid-render[pdf]
# Or manually install cairosvg
pip install cairosvg
```

#### Permission Errors on Windows

**Solution**: Run as administrator or use `--user` flag:

```bash
pip install --user mermaid-render
```

#### Network/Proxy Issues

**Solution**: Configure pip for your network:

```bash
pip install --proxy http://proxy.company.com:8080 mermaid-render
```

### Getting Help

If you encounter issues not covered here:

1. Check the [GitHub Issues](https://github.com/mermaid-render/mermaid-render/issues)
2. Search [Stack Overflow](https://stackoverflow.com/questions/tagged/mermaid-render)
3. Ask in [GitHub Discussions](https://github.com/mermaid-render/mermaid-render/discussions)

## Next Steps

Once installation is complete, proceed to the [Quick Start](quick-start.md) guide to create your first diagram!
