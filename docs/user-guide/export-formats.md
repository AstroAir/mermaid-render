# Export Formats

Comprehensive guide to exporting diagrams in various formats with quality and customization options.

## Overview

Mermaid Render supports multiple export formats:

- **Vector Formats**: SVG (scalable, web-friendly)
- **Raster Formats**: PNG, JPEG (pixel-based, print-ready)
- **Document Formats**: PDF (professional documents)
- **Web Formats**: HTML (interactive, embeddable)
- **Data Formats**: JSON (structured data export)

## Supported Formats

### Vector Formats

#### SVG (Scalable Vector Graphics)

```python
from mermaid_render import MermaidRenderer

renderer = MermaidRenderer()
diagram = "flowchart TD\n    A --> B"

# Basic SVG export
result = renderer.render(diagram, format="svg")
svg_content = result.svg

# Save to file
result.save("diagram.svg")
```

**SVG Options:**

```python
# Advanced SVG configuration
result = renderer.render(diagram, format="svg", options={
    "width": 800,
    "height": 600,
    "background": "white",
    "embed_fonts": True,
    "optimize": True,
    "pretty_print": True
})
```

### Raster Formats

#### PNG (Portable Network Graphics)

```python
# PNG export with quality settings
result = renderer.render(diagram, format="png", options={
    "width": 1920,
    "height": 1080,
    "dpi": 300,
    "quality": 95,
    "background": "transparent",
    "antialias": True
})

# Save PNG
result.save("diagram.png")
```

#### JPEG (Joint Photographic Experts Group)

```python
# JPEG export (good for photographs, not ideal for diagrams)
result = renderer.render(diagram, format="jpeg", options={
    "width": 1200,
    "height": 800,
    "quality": 85,
    "background": "white",  # JPEG doesn't support transparency
    "progressive": True
})
```

### Document Formats

#### PDF (Portable Document Format)

```python
# PDF export for professional documents
result = renderer.render(diagram, format="pdf", options={
    "page_size": "A4",  # A4, A3, Letter, Legal, Custom
    "orientation": "portrait",  # portrait, landscape
    "margin": {
        "top": 20,
        "right": 20,
        "bottom": 20,
        "left": 20
    },
    "title": "System Architecture Diagram",
    "author": "Your Name",
    "subject": "Technical Documentation"
})
```

### Web Formats

#### HTML (Interactive Web Format)

```python
# HTML export with interactive features
result = renderer.render(diagram, format="html", options={
    "interactive": True,
    "zoom_enabled": True,
    "pan_enabled": True,
    "theme": "default",
    "include_css": True,
    "include_js": True,
    "responsive": True
})
```

### Data Formats

#### JSON (Structured Data)

```python
# Export diagram structure as JSON
result = renderer.render(diagram, format="json")
diagram_data = result.json

# Access structured data
print(f"Nodes: {len(diagram_data['nodes'])}")
print(f"Edges: {len(diagram_data['edges'])}")
```

## Export Options

### Quality Settings

```python
# High-quality export for print
high_quality_options = {
    "dpi": 300,
    "quality": 95,
    "antialias": True,
    "smooth_edges": True,
    "font_hinting": True
}

# Web-optimized export
web_optimized_options = {
    "dpi": 96,
    "quality": 80,
    "optimize_size": True,
    "progressive": True,
    "strip_metadata": True
}
```

### Size and Dimensions

```python
# Fixed dimensions
result = renderer.render(diagram, options={
    "width": 1200,
    "height": 800,
    "maintain_aspect_ratio": True
})

# Responsive sizing
result = renderer.render(diagram, options={
    "max_width": 1920,
    "max_height": 1080,
    "scale_to_fit": True,
    "padding": 20
})

# Custom scaling
result = renderer.render(diagram, options={
    "scale": 2.0,  # 2x scaling
    "zoom": 1.5    # 150% zoom
})
```

### Background and Transparency

```python
# Transparent background (PNG, SVG)
result = renderer.render(diagram, format="png", options={
    "background": "transparent"
})

# Solid color background
result = renderer.render(diagram, options={
    "background": "#ffffff"  # White background
})

# Gradient background
result = renderer.render(diagram, options={
    "background": {
        "type": "gradient",
        "start_color": "#ffffff",
        "end_color": "#f0f0f0",
        "direction": "vertical"
    }
})
```

## Batch Export

### Multiple Formats

```python
from mermaid_render.export import BatchExporter

exporter = BatchExporter(renderer)

# Export to multiple formats
formats = ["svg", "png", "pdf"]
results = exporter.export_multiple(diagram, formats, base_filename="diagram")

# Results: diagram.svg, diagram.png, diagram.pdf
```

### Multiple Diagrams

```python
# Export multiple diagrams
diagrams = {
    "flowchart": "flowchart TD\n    A --> B",
    "sequence": "sequenceDiagram\n    A->>B: Hello",
    "class": "classDiagram\n    class A"
}

results = exporter.export_batch(diagrams, format="svg")
```

### Directory Export

```python
# Export all diagrams in a directory
exporter.export_directory(
    input_dir="./diagrams",
    output_dir="./exports",
    format="png",
    options={"dpi": 300}
)
```

## Advanced Export Features

### Watermarks

```python
# Add watermark to exports
result = renderer.render(diagram, options={
    "watermark": {
        "text": "CONFIDENTIAL",
        "position": "bottom-right",
        "opacity": 0.3,
        "font_size": 24,
        "color": "#ff0000"
    }
})
```

### Annotations

```python
# Add annotations during export
result = renderer.render(diagram, options={
    "annotations": [
        {
            "type": "text",
            "content": "Version 1.0",
            "position": {"x": 10, "y": 10},
            "style": {"font_size": 12, "color": "#666"}
        },
        {
            "type": "timestamp",
            "position": "bottom-left",
            "format": "%Y-%m-%d %H:%M"
        }
    ]
})
```

### Custom Styling

```python
# Apply custom CSS during export
custom_css = """
.node rect {
    fill: #3498db;
    stroke: #2980b9;
    stroke-width: 2px;
}
"""

result = renderer.render(diagram, options={
    "custom_css": custom_css,
    "embed_css": True
})
```

## Format-Specific Features

### SVG-Specific Options

```python
# SVG optimization and features
svg_options = {
    "optimize": True,
    "remove_unused_defs": True,
    "minify": True,
    "embed_images": True,
    "convert_text_to_paths": False,
    "precision": 2,
    "viewbox": True
}
```

### PNG-Specific Options

```python
# PNG compression and features
png_options = {
    "compression_level": 9,  # 0-9, higher = smaller file
    "interlaced": False,
    "gamma": 2.2,
    "color_type": "rgba",  # rgba, rgb, grayscale
    "bit_depth": 8
}
```

### PDF-Specific Options

```python
# PDF document properties
pdf_options = {
    "page_size": "A4",
    "orientation": "portrait",
    "compress": True,
    "embed_fonts": True,
    "pdf_version": "1.4",
    "metadata": {
        "title": "Diagram Export",
        "author": "Mermaid Render",
        "subject": "Technical Documentation",
        "keywords": "diagram, flowchart, documentation"
    },
    "security": {
        "encrypt": False,
        "user_password": None,
        "owner_password": None,
        "permissions": ["print", "copy"]
    }
}
```

## Export Validation

### Pre-Export Validation

```python
from mermaid_render.export import ExportValidator

validator = ExportValidator()

# Validate before export
validation_result = validator.validate_for_export(diagram, format="pdf")
if not validation_result.is_valid:
    print("Export validation failed:")
    for error in validation_result.errors:
        print(f"  - {error}")
```

### Post-Export Validation

```python
# Validate exported file
file_validation = validator.validate_exported_file("diagram.pdf")
print(f"File size: {file_validation.file_size} bytes")
print(f"Valid format: {file_validation.is_valid_format}")
print(f"Readable: {file_validation.is_readable}")
```

## Performance Optimization

### Export Performance

```python
# Optimize for speed
fast_export_options = {
    "quality": 70,
    "dpi": 96,
    "antialias": False,
    "optimize": False
}

# Optimize for quality
quality_export_options = {
    "quality": 95,
    "dpi": 300,
    "antialias": True,
    "smooth_edges": True,
    "optimize": True
}
```

### Caching

```python
# Enable export caching
from mermaid_render.cache import ExportCache

cache = ExportCache()
renderer = MermaidRenderer(export_cache=cache)

# First export - slow
result1 = renderer.render(diagram, format="png")

# Second export - fast (cached)
result2 = renderer.render(diagram, format="png")
```

## Integration Examples

### Web Application Export

```python
from flask import Flask, send_file
import io

app = Flask(__name__)

@app.route('/export/<format>')
def export_diagram(format):
    diagram = request.args.get('diagram')

    result = renderer.render(diagram, format=format)

    # Return file
    buffer = io.BytesIO(result.bytes)
    return send_file(
        buffer,
        mimetype=result.mime_type,
        as_attachment=True,
        download_name=f"diagram.{format}"
    )
```

### Command Line Export

```python
import argparse

def main():
    parser = argparse.ArgumentParser(description='Export Mermaid diagrams')
    parser.add_argument('input', help='Input diagram file')
    parser.add_argument('--format', default='svg', help='Output format')
    parser.add_argument('--output', help='Output file')
    parser.add_argument('--dpi', type=int, default=300, help='DPI for raster formats')

    args = parser.parse_args()

    with open(args.input, 'r') as f:
        diagram = f.read()

    result = renderer.render(diagram, format=args.format, options={
        'dpi': args.dpi
    })

    output_file = args.output or f"diagram.{args.format}"
    result.save(output_file)
    print(f"Exported to {output_file}")

if __name__ == '__main__':
    main()
```

## Best Practices

### Format Selection Guidelines

- **SVG**: Best for web, scalable, small file size
- **PNG**: Good for presentations, supports transparency
- **JPEG**: Avoid for diagrams (lossy compression)
- **PDF**: Best for documents, printing, archival
- **HTML**: Interactive web embedding

### Quality vs. File Size

```python
# Balance quality and file size
balanced_options = {
    "dpi": 150,  # Good balance for most uses
    "quality": 85,  # Good compression without visible loss
    "optimize": True,  # Enable optimization
    "progressive": True  # Better loading experience
}
```

### Accessibility

```python
# Export with accessibility features
accessible_options = {
    "alt_text": "System architecture flowchart showing data flow",
    "title": "System Architecture",
    "description": "Detailed description of the diagram",
    "high_contrast": True,
    "large_text": True
}
```

## Troubleshooting

### Common Export Issues

1. **Large file sizes**: Reduce DPI, quality, or dimensions
2. **Blurry images**: Increase DPI for raster formats
3. **Missing fonts**: Embed fonts or use web-safe fonts
4. **Transparency issues**: Check format support

### Export Debugging

```python
# Enable export debugging
result = renderer.render(diagram, format="png", debug=True)
print(f"Export time: {result.export_time}ms")
print(f"File size: {result.file_size} bytes")
print(f"Dimensions: {result.width}x{result.height}")
```

## See Also

- [Rendering Guide](rendering.md)
- [Performance Optimization](../guides/performance.md)
- [API Reference](../api-reference/export.md)
