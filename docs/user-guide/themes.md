# Themes and Styling

Mermaid Render provides comprehensive theming capabilities to customize the appearance of your diagrams.

## Overview

The theming system includes:

- **Built-in Themes**: Pre-designed themes for common use cases
- **Custom Themes**: Create your own themes with full control
- **Dynamic Theming**: Change themes at runtime
- **Theme Inheritance**: Build themes based on existing ones
- **CSS Integration**: Use CSS for advanced styling

## Built-in Themes

### Default Theme

```python
from mermaid_render import MermaidRenderer

# Use default theme
renderer = MermaidRenderer(theme="default")
diagram = "flowchart TD\n    A --> B"
result = renderer.render(diagram)
```

### Available Themes

```python
from mermaid_render.themes import get_available_themes

# List all available themes
themes = get_available_themes()
for theme in themes:
    print(f"{theme.name}: {theme.description}")
```

Common built-in themes:
- **default**: Clean, professional appearance
- **dark**: Dark mode with light text
- **neutral**: Minimal, grayscale design
- **base**: Basic styling, good for customization
- **forest**: Green color scheme
- **corporate**: Business-appropriate colors

## Using Themes

### Basic Theme Application

```python
# Apply theme during rendering
renderer = MermaidRenderer()
result = renderer.render(diagram, theme="dark")
```

### Theme Configuration

```python
from mermaid_render.config import ThemeConfig

# Configure theme settings
theme_config = ThemeConfig(
    name="dark",
    background="transparent",
    primary_color="#ffffff",
    secondary_color="#cccccc"
)

renderer = MermaidRenderer(theme_config=theme_config)
```

## Custom Themes

### Creating Custom Themes

```python
from mermaid_render.themes import Theme, ColorPalette

# Define color palette
palette = ColorPalette(
    primary="#2c3e50",
    secondary="#3498db",
    accent="#e74c3c",
    background="#ecf0f1",
    text="#2c3e50",
    border="#bdc3c7"
)

# Create custom theme
custom_theme = Theme(
    name="corporate",
    description="Corporate branding theme",
    palette=palette,
    font_family="Arial, sans-serif",
    font_size=14,
    line_width=2,
    border_radius=4
)
```

### Theme Properties

```python
# Comprehensive theme configuration
theme = Theme(
    name="custom",
    # Colors
    primary_color="#2c3e50",
    secondary_color="#3498db",
    accent_color="#e74c3c",
    background_color="#ffffff",
    text_color="#2c3e50",
    
    # Typography
    font_family="Roboto, sans-serif",
    font_size=14,
    font_weight="normal",
    
    # Shapes and borders
    border_width=1,
    border_radius=4,
    line_width=2,
    
    # Spacing
    node_padding=8,
    edge_spacing=20,
    
    # Diagram-specific settings
    flowchart_curve="basis",
    sequence_actor_margin=50,
    class_title_color="#ffffff"
)
```

## Theme Inheritance

### Extending Existing Themes

```python
from mermaid_render.themes import extend_theme

# Extend the dark theme
my_dark_theme = extend_theme("dark", {
    "primary_color": "#4a90e2",
    "accent_color": "#f39c12",
    "font_family": "Consolas, monospace"
})
```

### Theme Composition

```python
# Combine multiple theme aspects
base_theme = Theme.load("neutral")
color_scheme = ColorPalette.load("vibrant")
typography = Typography.load("modern")

composed_theme = Theme.compose(
    base=base_theme,
    colors=color_scheme,
    typography=typography
)
```

## Dynamic Theming

### Runtime Theme Changes

```python
# Change theme dynamically
renderer = MermaidRenderer()

# Render with different themes
light_result = renderer.render(diagram, theme="default")
dark_result = renderer.render(diagram, theme="dark")
```

### Conditional Theming

```python
def get_theme_for_context(context):
    if context == "presentation":
        return "high-contrast"
    elif context == "print":
        return "grayscale"
    else:
        return "default"

# Apply contextual theme
theme = get_theme_for_context("presentation")
result = renderer.render(diagram, theme=theme)
```

## CSS Integration

### Custom CSS Styling

```python
# Apply custom CSS
custom_css = """
.node rect {
    fill: #3498db;
    stroke: #2980b9;
    stroke-width: 2px;
}

.edgePath path {
    stroke: #34495e;
    stroke-width: 2px;
}

.edgeLabel {
    background-color: #ffffff;
    border: 1px solid #bdc3c7;
    border-radius: 4px;
    padding: 4px;
}
"""

result = renderer.render(diagram, custom_css=custom_css)
```

### CSS Classes

```python
# Use predefined CSS classes
diagram_with_classes = """
flowchart TD
    A[Start]:::highlight --> B[Process]:::normal
    B --> C[End]:::success
    
    classDef highlight fill:#e74c3c,stroke:#c0392b,color:#fff
    classDef normal fill:#3498db,stroke:#2980b9,color:#fff
    classDef success fill:#27ae60,stroke:#229954,color:#fff
"""
```

## Diagram-Specific Theming

### Flowchart Themes

```python
flowchart_theme = Theme(
    name="flowchart_modern",
    node_fill="#3498db",
    node_stroke="#2980b9",
    node_text_color="#ffffff",
    edge_color="#34495e",
    edge_width=2,
    curve_style="basis"
)
```

### Sequence Diagram Themes

```python
sequence_theme = Theme(
    name="sequence_professional",
    actor_background="#ecf0f1",
    actor_border="#bdc3c7",
    actor_text_color="#2c3e50",
    message_color="#3498db",
    activation_background="#3498db",
    activation_border="#2980b9"
)
```

### Class Diagram Themes

```python
class_theme = Theme(
    name="class_uml",
    class_background="#ffffff",
    class_border="#2c3e50",
    class_title_background="#3498db",
    class_title_color="#ffffff",
    method_color="#27ae60",
    attribute_color="#e67e22"
)
```

## Theme Management

### Theme Registry

```python
from mermaid_render.themes import ThemeRegistry

# Register custom theme
registry = ThemeRegistry()
registry.register(custom_theme)

# Load theme by name
theme = registry.get("corporate")
```

### Theme Validation

```python
from mermaid_render.themes import validate_theme

# Validate theme configuration
validation_result = validate_theme(custom_theme)
if not validation_result.is_valid:
    for error in validation_result.errors:
        print(f"Theme error: {error}")
```

## Advanced Features

### Responsive Themes

```python
# Define responsive theme
responsive_theme = Theme(
    name="responsive",
    breakpoints={
        "mobile": {"font_size": 12, "node_padding": 6},
        "tablet": {"font_size": 14, "node_padding": 8},
        "desktop": {"font_size": 16, "node_padding": 10}
    }
)
```

### Theme Variables

```python
# Use theme variables
theme_with_variables = Theme(
    name="variable_theme",
    variables={
        "primary": "#3498db",
        "secondary": "#2ecc71",
        "danger": "#e74c3c"
    },
    node_fill="var(--primary)",
    success_color="var(--secondary)",
    error_color="var(--danger)"
)
```

### Theme Animations

```python
# Add animation support
animated_theme = Theme(
    name="animated",
    animations={
        "node_hover": "scale(1.05)",
        "edge_draw": "stroke-dasharray: 5,5",
        "fade_in": "opacity: 0 to 1"
    }
)
```

## Export with Themes

### Theme-Aware Export

```python
# Export with theme applied
result = renderer.render(diagram, theme="corporate")

# Save with theme
result.save("diagram.svg")  # Theme is embedded
result.save("diagram.png", dpi=300)  # Theme applied to raster
```

### Multiple Theme Export

```python
# Export same diagram with different themes
themes = ["default", "dark", "corporate"]
for theme_name in themes:
    result = renderer.render(diagram, theme=theme_name)
    result.save(f"diagram_{theme_name}.svg")
```

## Best Practices

### Theme Design Guidelines

1. **Consistency**: Use consistent colors and spacing
2. **Accessibility**: Ensure sufficient contrast ratios
3. **Readability**: Choose legible fonts and sizes
4. **Purpose**: Match theme to intended use case

### Performance Considerations

```python
# Cache themes for better performance
from mermaid_render.themes import ThemeCache

cache = ThemeCache()
cached_theme = cache.get_or_create("corporate", create_corporate_theme)
```

### Theme Testing

```python
# Test theme with different diagram types
test_diagrams = [
    "flowchart TD\n    A --> B",
    "sequenceDiagram\n    A->>B: Hello",
    "classDiagram\n    class A"
]

for diagram in test_diagrams:
    result = renderer.render(diagram, theme="custom")
    # Validate result
```

## Configuration

### Global Theme Settings

```python
from mermaid_render.config import GlobalConfig

GlobalConfig.set_default_theme("corporate")
GlobalConfig.set_theme_directory("./themes")
GlobalConfig.enable_theme_caching(True)
```

### Environment-Based Themes

```python
import os

# Use different themes based on environment
theme = "dark" if os.getenv("DARK_MODE") else "default"
renderer = MermaidRenderer(theme=theme)
```

## See Also

- [Configuration Guide](configuration.md)
- [Styling Examples](../examples/styling.md)
- [API Reference](../api-reference/themes.md)
