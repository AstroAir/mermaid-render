# Mermaid Render - Plugin-Based Renderer System

This directory contains the plugin-based renderer architecture for Mermaid Render, providing a flexible and extensible system for rendering Mermaid diagrams using multiple backends.

## Architecture Overview

The plugin-based renderer system consists of several key components:

### Core Components

- **`base.py`**: Abstract base class and interfaces for all renderers
- **`registry.py`**: Registry system for managing and discovering renderer plugins
- **`manager.py`**: Orchestration layer that handles renderer selection and fallback
- **`error_handler.py`**: Enhanced error handling with categorization and recovery suggestions
- **`validation.py`**: Comprehensive input validation and sanitization
- **`config_manager.py`**: Configuration management for renderer-specific settings
- **`logging_config.py`**: Structured logging and performance monitoring

### Renderer Implementations

#### Legacy Renderer Adapters

- **`svg_renderer_plugin.py`**: Plugin adapter for the original SVGRenderer
- **`png_renderer_plugin.py`**: Plugin adapter for the original PNGRenderer  
- **`pdf_renderer_plugin.py`**: Plugin adapter for the original PDFRenderer

#### New Renderer Backends

- **`playwright_renderer.py`**: High-fidelity rendering using Playwright and Mermaid.js
- **`nodejs_renderer.py`**: Local rendering using Node.js and Mermaid CLI
- **`graphviz_renderer.py`**: Alternative rendering using Graphviz for flowcharts

## Renderer Capabilities

Each renderer supports different capabilities:

| Capability | SVG | PNG | PDF | Playwright | Node.js | Graphviz |
|------------|-----|-----|-----|------------|---------|----------|
| **Caching** | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| **Validation** | ✓ | ✗ | ✗ | ✓ | ✓ | ✗ |
| **Batch Processing** | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| **Theme Support** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Custom Config** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Performance Metrics** | ✓ | ✗ | ✗ | ✓ | ✓ | ✓ |
| **Local Rendering** | ✓ | ✗ | ✗ | ✓ | ✓ | ✓ |
| **Remote Rendering** | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |

## Usage Examples

### Basic Plugin System Usage

```python
from mermaid_render.renderers import RendererManager, get_global_registry

# Get the global registry
registry = get_global_registry()
print(f"Available renderers: {registry.list_renderers()}")

# Create a renderer manager
manager = RendererManager()

# Render with automatic renderer selection
result = manager.render(
    mermaid_code="graph TD\n    A --> B",
    format="svg"
)

print(f"Rendered with: {result.renderer_name}")
print(f"Success: {result.success}")
print(f"Render time: {result.render_time:.3f}s")
```

### Renderer-Specific Configuration

```python
from mermaid_render.renderers import RendererConfigManager

# Configure Playwright renderer
config_manager = RendererConfigManager()
config_manager.set_renderer_config("playwright", "browser_type", "firefox")
config_manager.set_renderer_config("playwright", "headless", False)

# Configure Node.js renderer
config_manager.set_renderer_config("nodejs", "timeout", 60.0)
config_manager.set_renderer_config("nodejs", "mmdc_path", "/usr/local/bin/mmdc")

# Save configurations
config_manager.save_renderer_config("playwright", config_manager.get_renderer_config("playwright"))
```

### Error Handling and Debugging

```python
from mermaid_render.renderers import setup_logging, ErrorHandler

# Enable detailed logging
setup_logging(level="DEBUG", log_file="mermaid_render.log")

# Create debug session
from mermaid_render.renderers.logging_config import create_debug_session
debug_session = create_debug_session("my_debug_session")

# Handle errors with detailed context
try:
    result = manager.render("invalid syntax", "svg")
except Exception as e:
    error_handler = ErrorHandler()
    # Error context would be created automatically in real usage
    print(f"Error occurred: {e}")
```

### Custom Renderer Development

To create a custom renderer, inherit from `BaseRenderer`:

```python
from mermaid_render.renderers.base import BaseRenderer, RendererInfo, RenderResult

class MyCustomRenderer(BaseRenderer):
    def get_info(self):
        return RendererInfo(
            name="custom",
            description="My custom renderer",
            supported_formats={"svg"},
            capabilities={RendererCapability.LOCAL_RENDERING},
        )
    
    def render(self, mermaid_code, format, theme=None, config=None, **options):
        # Your custom rendering logic here
        content = f"<svg>Custom render of: {mermaid_code}</svg>"
        
        return RenderResult(
            content=content,
            format=format,
            renderer_name="custom",
            render_time=0.1,
            success=True,
        )
    
    def is_available(self):
        return True  # Check if your renderer dependencies are available

# Register your custom renderer
from mermaid_render.renderers import register_renderer
register_renderer(MyCustomRenderer, "custom")
```

## Configuration Schemas

### Playwright Renderer Configuration

```json
{
  "browser_type": "chromium",  // "chromium", "firefox", "webkit"
  "headless": true,
  "timeout": 30000,           // milliseconds
  "viewport_width": 1200,
  "viewport_height": 800,
  "mermaid_version": "10.6.1"
}
```

### Node.js Renderer Configuration

```json
{
  "mmdc_path": "mmdc",        // Path to mmdc command
  "node_path": "node",        // Path to node command
  "timeout": 30.0,            // seconds
  "puppeteer_config": {},     // Puppeteer-specific config
  "temp_dir": null            // Temporary directory for files
}
```

### Graphviz Renderer Configuration

```json
{
  "engine": "dot",            // "dot", "neato", "fdp", "sfdp", "circo"
  "dpi": 96,
  "rankdir": "TB",            // "TB", "BT", "LR", "RL"
  "node_shape": "box",
  "edge_style": "solid"
}
```

## Performance and Monitoring

The plugin system includes comprehensive performance monitoring:

```python
# Get performance statistics
stats = manager.get_performance_stats()
print(f"Total renders: {stats['total_renders']}")
print(f"Success rate: {stats['successful_renders'] / stats['total_renders'] * 100:.1f}%")
print(f"Fallback usage: {stats['fallback_uses']}")

# Renderer usage statistics
for renderer, count in stats['renderer_usage'].items():
    print(f"{renderer}: {count} renders")
```

## Error Recovery

The system provides intelligent error recovery with detailed suggestions:

- **Dependency Issues**: Automatic detection with installation instructions
- **Network Problems**: Fallback to local renderers
- **Timeout Errors**: Suggestions for timeout adjustment or renderer switching
- **Syntax Errors**: Detailed validation with line-specific feedback
- **Configuration Errors**: Schema validation with helpful error messages

## Extending the System

The plugin architecture is designed for easy extension:

1. **Create Custom Renderers**: Implement the `BaseRenderer` interface
2. **Add New Capabilities**: Extend the `RendererCapability` enum
3. **Custom Error Handling**: Add patterns to the error handler
4. **Configuration Schemas**: Define JSON schemas for validation
5. **Performance Metrics**: Add custom metrics to renderer implementations

## Migration Guide

### From Legacy to Plugin System

```python
# Old way
from mermaid_render import MermaidRenderer
renderer = MermaidRenderer()
result = renderer.render_raw("graph TD\n    A --> B", "svg")

# New way (plugin-based features)
from mermaid_render import PluginMermaidRenderer
renderer = PluginMermaidRenderer()
result = renderer.render("graph TD\n    A --> B", format="svg")

# Hybrid approach (legacy renderer with plugin system)
from mermaid_render import MermaidRenderer
renderer = MermaidRenderer(use_plugin_system=True, preferred_renderer="playwright")
result = renderer.render_raw("graph TD\n    A --> B", "svg")
```

The plugin system maintains full backward compatibility while providing advanced capabilities.
