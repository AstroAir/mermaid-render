# Interactive Features

Mermaid Render provides rich interactive capabilities including web interfaces, diagram builders, and real-time editing tools.

## Overview

Interactive features include:

- **Web Interface**: Browser-based diagram editor
- **Diagram Builder**: Visual drag-and-drop diagram creation
- **Real-time Preview**: Live preview as you type
- **Interactive Elements**: Clickable nodes and edges
- **Export Tools**: Interactive export with format selection

## Web Interface

### Basic Setup

```python
from diagramaid.interactive import WebInterface

# Create web interface
web_interface = WebInterface(
    host="localhost",
    port=8080,
    debug=True
)

# Start the server
web_interface.run()
```

### Custom Configuration

```python
# Advanced configuration
web_interface = WebInterface(
    host="0.0.0.0",
    port=8080,
    static_folder="./static",
    template_folder="./templates",
    enable_collaboration=True,
    enable_ai_features=True,
    max_file_size=10 * 1024 * 1024  # 10MB
)
```

### Flask Integration

```python
from flask import Flask
from diagramaid.interactive import create_blueprint

app = Flask(__name__)

# Add Mermaid Render blueprint
mermaid_bp = create_blueprint(
    url_prefix="/mermaid",
    enable_api=True,
    enable_editor=True
)

app.register_blueprint(mermaid_bp)
```

## Diagram Builder

### Visual Editor

```python
from diagramaid.interactive import DiagramBuilder

# Create diagram builder
builder = DiagramBuilder(
    canvas_size=(800, 600),
    grid_enabled=True,
    snap_to_grid=True
)

# Add to web interface
web_interface.add_component(builder)
```

### Drag and Drop

```javascript
// Client-side JavaScript for drag and drop
const builder = new MermaidDiagramBuilder({
    container: '#diagram-builder',
    tools: ['flowchart', 'sequence', 'class'],
    onDiagramChange: (diagram) => {
        // Update preview
        updatePreview(diagram);
    }
});

// Add node by dragging from palette
builder.addNodeType('process', {
    shape: 'rectangle',
    label: 'Process',
    icon: 'fas fa-cog'
});
```

### Programmatic Building

```python
# Build diagram programmatically
from diagramaid.interactive import ProgrammaticBuilder

builder = ProgrammaticBuilder()

# Add nodes
node_a = builder.add_node("A", "Start", shape="circle")
node_b = builder.add_node("B", "Process", shape="rectangle")
node_c = builder.add_node("C", "End", shape="circle")

# Add connections
builder.add_edge(node_a, node_b, "begin")
builder.add_edge(node_b, node_c, "complete")

# Generate diagram
diagram = builder.build()
```

## Real-time Preview

### Live Editor

```python
from diagramaid.interactive import LiveEditor

editor = LiveEditor(
    auto_save=True,
    save_interval=5,  # seconds
    syntax_highlighting=True,
    error_highlighting=True
)

# Add to web interface
web_interface.add_editor(editor)
```

### WebSocket Updates

```python
from diagramaid.interactive import WebSocketManager

ws_manager = WebSocketManager()

@ws_manager.on_diagram_change
async def handle_diagram_change(session_id, diagram_content):
    # Validate diagram
    validation_result = validator.validate(diagram_content)

    # Send validation result back
    await ws_manager.send_to_session(session_id, {
        'type': 'validation_result',
        'valid': validation_result.is_valid,
        'errors': validation_result.errors
    })

    # Update preview if valid
    if validation_result.is_valid:
        rendered = renderer.render(diagram_content)
        await ws_manager.send_to_session(session_id, {
            'type': 'preview_update',
            'svg': rendered.svg
        })
```

## Interactive Elements

### Clickable Diagrams

```python
from diagramaid.interactive import InteractiveDiagram

# Create interactive diagram
interactive = InteractiveDiagram(
    diagram_content=diagram,
    enable_click_events=True,
    enable_hover_effects=True
)

# Add click handlers
@interactive.on_node_click
def handle_node_click(node_id, node_data):
    print(f"Clicked node: {node_id}")
    # Show node details
    return {
        'action': 'show_details',
        'data': node_data
    }

@interactive.on_edge_click
def handle_edge_click(edge_id, edge_data):
    print(f"Clicked edge: {edge_id}")
    # Show edge properties
    return {
        'action': 'show_properties',
        'data': edge_data
    }
```

### Dynamic Updates

```python
# Update diagram dynamically
interactive.update_node("A", {
    'label': 'Updated Process',
    'color': '#ff6b6b'
})

interactive.add_node("D", {
    'label': 'New Node',
    'shape': 'diamond'
})

interactive.add_edge("C", "D", "leads to")
```

## Export Tools

### Interactive Export

```python
from diagramaid.interactive import ExportTool

export_tool = ExportTool(
    supported_formats=['svg', 'png', 'pdf', 'jpg'],
    quality_options=True,
    size_options=True
)

# Add to web interface
web_interface.add_tool(export_tool)
```

### Batch Export

```python
# Export multiple formats at once
export_options = {
    'svg': {'quality': 'high'},
    'png': {'width': 1920, 'height': 1080, 'dpi': 300},
    'pdf': {'page_size': 'A4', 'orientation': 'landscape'}
}

results = export_tool.batch_export(diagram, export_options)
```

## Customization

### Themes and Styling

```python
from diagramaid.interactive import ThemeManager

theme_manager = ThemeManager()

# Create custom theme
custom_theme = theme_manager.create_theme(
    name="corporate",
    primary_color="#2c3e50",
    secondary_color="#3498db",
    background_color="#ecf0f1",
    font_family="Arial, sans-serif"
)

# Apply theme to interface
web_interface.apply_theme(custom_theme)
```

### Custom Components

```python
from diagramaid.interactive import CustomComponent

class DiagramStatsComponent(CustomComponent):
    def __init__(self):
        super().__init__(name="diagram_stats")

    def render(self, diagram):
        stats = self.analyze_diagram(diagram)
        return {
            'node_count': stats.node_count,
            'edge_count': stats.edge_count,
            'complexity_score': stats.complexity
        }

    def analyze_diagram(self, diagram):
        # Analyze diagram and return stats
        pass

# Add custom component
web_interface.add_component(DiagramStatsComponent())
```

## API Endpoints

### REST API

```python
from diagramaid.interactive import APIManager

api_manager = APIManager(web_interface)

# Custom API endpoints
@api_manager.route('/api/diagrams', methods=['POST'])
def create_diagram():
    data = request.get_json()
    diagram = DiagramModel.create(
        content=data['content'],
        title=data['title'],
        user_id=data['user_id']
    )
    return jsonify(diagram.to_dict())

@api_manager.route('/api/diagrams/<int:diagram_id>', methods=['GET'])
def get_diagram(diagram_id):
    diagram = DiagramModel.get_by_id(diagram_id)
    return jsonify(diagram.to_dict())
```

### GraphQL API

```python
from diagramaid.interactive import GraphQLManager
import graphene

class DiagramType(graphene.ObjectType):
    id = graphene.ID()
    title = graphene.String()
    content = graphene.String()
    created_at = graphene.DateTime()

class Query(graphene.ObjectType):
    diagram = graphene.Field(DiagramType, id=graphene.ID(required=True))
    diagrams = graphene.List(DiagramType)

# Add GraphQL endpoint
graphql_manager = GraphQLManager(schema=graphene.Schema(query=Query))
web_interface.add_graphql(graphql_manager)
```

## Mobile Support

### Responsive Design

```python
# Enable mobile-responsive interface
web_interface.configure_mobile(
    enable_touch_gestures=True,
    responsive_breakpoints={
        'mobile': 768,
        'tablet': 1024,
        'desktop': 1200
    },
    mobile_optimizations=True
)
```

### Touch Interactions

```javascript
// Client-side touch handling
const touchHandler = new TouchHandler({
    container: '#diagram-container',
    gestures: ['pan', 'zoom', 'tap', 'long-press'],
    onGesture: (gesture, data) => {
        switch(gesture) {
            case 'tap':
                handleNodeTap(data.target);
                break;
            case 'long-press':
                showContextMenu(data.position);
                break;
        }
    }
});
```

## Performance Optimization

### Lazy Loading

```python
# Enable lazy loading for large diagrams
web_interface.configure_performance(
    lazy_loading=True,
    chunk_size=100,  # Load 100 nodes at a time
    virtual_scrolling=True
)
```

### Caching Strategy

```python
# Configure client-side caching
web_interface.configure_caching(
    cache_rendered_diagrams=True,
    cache_duration=300,  # 5 minutes
    max_cache_size=50   # 50 diagrams
)
```

## Security

### Authentication

```python
from diagramaid.interactive import AuthManager

auth_manager = AuthManager(
    provider="oauth2",
    client_id="your-client-id",
    client_secret="your-client-secret",
    redirect_uri="http://localhost:8080/auth/callback"
)

web_interface.add_auth(auth_manager)
```

### Input Sanitization

```python
# Configure input sanitization
web_interface.configure_security(
    sanitize_input=True,
    max_diagram_size=1024 * 1024,  # 1MB
    allowed_file_types=['mmd', 'txt'],
    rate_limiting={
        'requests_per_minute': 60,
        'diagrams_per_hour': 100
    }
)
```

## Deployment

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080
CMD ["python", "app.py"]
```

### Production Configuration

```python
# Production settings
web_interface = WebInterface(
    host="0.0.0.0",
    port=8080,
    debug=False,
    workers=4,
    max_connections=1000,
    enable_ssl=True,
    ssl_cert="path/to/cert.pem",
    ssl_key="path/to/key.pem"
)
```

## See Also

- [Collaboration Features](collaboration.md)
- [Web Integration Guide](../guides/web-integration.md)
- [API Reference](../api-reference/interactive.md)
