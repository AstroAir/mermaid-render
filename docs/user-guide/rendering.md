# Rendering

Learn how to render your diagrams to different output formats with optimal quality and performance.

## The Rendering Pipeline

Mermaid Render uses a multi-stage pipeline to convert your diagram objects into final output:

```
Diagram Object → Mermaid Syntax → Validation → Rendering → Output Format
```

## Output Formats

### SVG (Scalable Vector Graphics)

**Best for:** Web pages, documentation sites, scalable graphics

```python
from mermaid_render import MermaidRenderer, FlowchartDiagram

diagram = FlowchartDiagram()
diagram.add_node("A", "Start")
diagram.add_node("B", "End")
diagram.add_edge("A", "B")

renderer = MermaidRenderer()
svg_content = renderer.render(diagram, format="svg")

# SVG is returned as a string
print(type(svg_content))  # <class 'str'>
```

**Advantages:**

- ✅ Infinite scalability without quality loss
- ✅ Small file sizes
- ✅ Editable with code or graphics tools
- ✅ Best web performance

**Use Cases:**

- Web documentation
- Interactive diagrams
- Print-ready graphics
- Presentations

### PNG (Portable Network Graphics)

**Best for:** Documents, presentations, fixed-size images

```python
# Render to PNG with custom dimensions
png_bytes = renderer.render(diagram, format="png", width=800, height=600)

# PNG is returned as bytes
print(type(png_bytes))  # <class 'bytes'>

# Save to file
renderer.save(diagram, "diagram.png", format="png", width=1200, height=800)
```

**Advantages:**

- ✅ Universal compatibility
- ✅ Good for fixed layouts
- ✅ Supports transparency
- ✅ Excellent for documents

**Use Cases:**

- Word documents
- PowerPoint presentations
- Email attachments
- Social media sharing

### PDF (Portable Document Format)

**Best for:** Printing, archival, professional documents

```python
# Render to PDF
pdf_bytes = renderer.render(diagram, format="pdf")

# PDF is returned as bytes
print(type(pdf_bytes))  # <class 'bytes'>

# Save with custom page size
renderer.save(diagram, "diagram.pdf", format="pdf", page_size="A4")
```

**Advantages:**

- ✅ Perfect for printing
- ✅ Professional appearance
- ✅ Consistent across platforms
- ✅ Vector-based quality

**Use Cases:**

- Technical documentation
- Reports and proposals
- Archival storage
- Professional presentations

## Rendering Options

### Quality Settings

```python
from mermaid_render import MermaidConfig, MermaidRenderer

# High-quality configuration
config = MermaidConfig(
    timeout=60,           # Longer timeout for complex diagrams
    scale=2.0,           # Higher resolution for PNG
    background="white",   # Explicit background color
    validate_syntax=True  # Ensure quality
)

renderer = MermaidRenderer(config=config)
```

### Custom Dimensions

```python
# Specific dimensions for PNG
renderer.save(diagram, "large.png", format="png", width=1920, height=1080)

# Aspect ratio preservation
renderer.save(diagram, "wide.png", format="png", width=1600)  # Height auto-calculated
```

### Background and Transparency

```python
# Transparent background (PNG only)
renderer.save(diagram, "transparent.png", format="png", transparent=True)

# Custom background color
renderer.save(diagram, "colored.png", format="png", background="#f0f0f0")
```

## Performance Optimization

### Caching

Enable caching for better performance with repeated renders:

```python
config = MermaidConfig(cache_enabled=True, cache_ttl=3600)
renderer = MermaidRenderer(config=config)

# First render: slow (generates and caches)
result1 = renderer.render(diagram, format="svg")

# Second render: fast (uses cache)
result2 = renderer.render(diagram, format="svg")
```

### Batch Rendering

Render multiple diagrams efficiently:

```python
from mermaid_render.utils import batch_render

diagrams = {
    "process_flow": flowchart_diagram,
    "api_sequence": sequence_diagram,
    "system_arch": class_diagram
}

# Render all diagrams in multiple formats
results = batch_render(
    diagrams,
    formats=["svg", "png"],
    output_dir="documentation/diagrams/",
    theme="neutral"
)
```

### Async Rendering

For high-throughput applications:

```python
import asyncio
from mermaid_render import AsyncMermaidRenderer

async def render_many_diagrams(diagrams):
    renderer = AsyncMermaidRenderer()

    tasks = [
        renderer.render_async(diagram, format="svg")
        for diagram in diagrams
    ]

    results = await asyncio.gather(*tasks)
    return results

# Usage
diagrams = [diagram1, diagram2, diagram3]
results = asyncio.run(render_many_diagrams(diagrams))
```

## Error Handling

### Common Rendering Issues

```python
from mermaid_render.exceptions import (
    RenderingError,
    ValidationError,
    UnsupportedFormatError,
    TimeoutError
)

def safe_render(diagram, output_path, format="svg"):
    try:
        renderer = MermaidRenderer()
        renderer.save(diagram, output_path, format=format)
        return True

    except ValidationError as e:
        print(f"Invalid diagram: {e}")

    except RenderingError as e:
        print(f"Rendering failed: {e}")

    except TimeoutError as e:
        print(f"Rendering timed out: {e}")

    except UnsupportedFormatError as e:
        print(f"Format not supported: {e}")

    return False
```

### Debugging Rendering Issues

```python
# Enable debug mode
config = MermaidConfig(debug=True, verbose=True)
renderer = MermaidRenderer(config=config)

# Check generated Mermaid syntax
mermaid_code = diagram.to_mermaid()
print("Generated Mermaid code:")
print(mermaid_code)

# Validate before rendering
validation_result = diagram.validate()
if not validation_result.is_valid:
    print("Validation errors:", validation_result.errors)
```

## Advanced Rendering

### Custom Renderers

Create custom rendering backends:

```python
from mermaid_render.renderers import BaseRenderer

class CustomRenderer(BaseRenderer):
    def render(self, diagram, format="svg", **options):
        # Custom rendering logic
        mermaid_code = diagram.to_mermaid()
        # Process with custom backend
        return processed_result

# Use custom renderer
renderer = CustomRenderer()
result = renderer.render(diagram)
```

### Server-Side Rendering

For web applications:

```python
from flask import Flask, Response
from mermaid_render import quick_render

app = Flask(__name__)

@app.route('/diagram/<diagram_type>')
def generate_diagram(diagram_type):
    # Generate diagram based on type
    diagram_code = get_diagram_template(diagram_type)

    # Render to SVG
    svg_content = quick_render(diagram_code, format="svg", theme="dark")

    return Response(svg_content, mimetype="image/svg+xml")
```

### Integration with Documentation Tools

#### Sphinx Integration

```python
# sphinx_mermaid_extension.py
from mermaid_render import quick_render

def render_mermaid_directive(diagram_code, output_path):
    svg_content = quick_render(diagram_code, format="svg")
    with open(output_path, 'w') as f:
        f.write(svg_content)
```

#### MkDocs Integration

```python
# mkdocs_mermaid_plugin.py
from mkdocs.plugins import BasePlugin
from mermaid_render import quick_render

class MermaidPlugin(BasePlugin):
    def on_page_markdown(self, markdown, page, config, files):
        # Process mermaid code blocks
        return process_mermaid_blocks(markdown)
```

## Best Practices

### Format Selection

| Use Case          | Recommended Format | Reason                  |
| ----------------- | ------------------ | ----------------------- |
| Web documentation | SVG                | Scalable, small files   |
| Word documents    | PNG                | Universal compatibility |
| Presentations     | PNG or PDF         | Fixed layout            |
| Printing          | PDF                | Vector quality          |
| Social sharing    | PNG                | Wide support            |

### Quality Guidelines

1. **SVG**: Always use for web when possible
2. **PNG**: Use at least 2x scale for high-DPI displays
3. **PDF**: Specify page size for consistent layout
4. **Caching**: Enable for production applications
5. **Validation**: Always validate before rendering

### Performance Tips

1. **Cache frequently used diagrams**
2. **Use batch rendering for multiple diagrams**
3. **Optimize diagram complexity**
4. **Choose appropriate timeouts**
5. **Monitor rendering performance**

## Troubleshooting

### Common Issues

**Rendering timeouts:**

```python
config = MermaidConfig(timeout=120)  # Increase timeout
```

**Poor image quality:**

```python
# Use higher scale for PNG
renderer.save(diagram, "high_quality.png", format="png", scale=3.0)
```

**Memory issues with large diagrams:**

```python
# Process in smaller batches
for batch in chunk_diagrams(all_diagrams, batch_size=10):
    batch_render(batch)
```

## Next Steps

- Learn about [Themes](themes.md) for visual consistency
- Explore [Export Formats](export-formats.md) for advanced options
- Check [Configuration](configuration.md) for fine-tuning
- Review [Examples](../examples/) for real-world patterns
