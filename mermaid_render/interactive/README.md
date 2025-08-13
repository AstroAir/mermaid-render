# Interactive Module

This module provides interactive web-based features for the Mermaid Render library, including a visual diagram builder, real-time editing, and web server capabilities.

## Components

### Core Interactive Services
- **`builder.py`** - Interactive diagram builder with drag-and-drop interface
- **`server.py`** - Web server for hosting interactive diagram editor
- **`websocket_handler.py`** - Real-time communication for live editing
- **`validation.py`** - Real-time validation with immediate feedback

### User Interface
- **`ui_components.py`** - Reusable UI components for the web interface
- **`templates.py`** - HTML templates for the interactive editor
- **`export.py`** - Export functionality for interactive sessions

### Supporting Infrastructure
- **`utils.py`** - Utility functions for interactive features

## Key Features

- **Visual Diagram Builder**: Drag-and-drop interface for creating diagrams
- **Real-time Editing**: Live preview and collaborative editing
- **Interactive Validation**: Immediate syntax checking and error highlighting
- **Export Integration**: Direct export from the web interface
- **WebSocket Support**: Real-time synchronization between clients

## Usage Example

```python
from mermaid_render.interactive import InteractiveServer, DiagramBuilder

# Start interactive server
server = InteractiveServer(port=8080)
server.start()

# Create diagram builder
builder = DiagramBuilder()
session = builder.create_session()

# Add interactive elements
session.add_node("start", "Start Process")
session.add_node("end", "End Process")
session.connect("start", "end")
```

## Dependencies

This module requires the `interactive` optional dependency group:
```bash
pip install mermaid-render[interactive]
```

## Web Interface

The interactive module provides a complete web interface accessible at:
- **Editor**: `http://localhost:8080/editor`
- **Gallery**: `http://localhost:8080/gallery`
- **API**: `http://localhost:8080/api/docs`

## Configuration

Interactive features can be configured:
```python
from mermaid_render import MermaidConfig

config = MermaidConfig()
config.set_interactive_port(8080)
config.set_websocket_enabled(True)
config.set_auto_save(True)
```
