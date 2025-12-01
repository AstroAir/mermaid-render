# Interactive Module

This module provides a comprehensive interactive web-based diagram builder for Mermaid diagrams with real-time collaboration, advanced validation, security features, and performance optimizations.

## Components

### Core Components

- **`server.py`** - FastAPI web server with WebSocket support, security middleware, and performance monitoring
- **`builder.py`** - Core diagram building logic with full Mermaid syntax support
- **`websocket_handler.py`** - WebSocket connection management with rate limiting and debouncing
- **`validation.py`** - Real-time validation integrated with core MermaidValidator
- **`export.py`** - Comprehensive diagram export functionality with MermaidRenderer integration
- **`templates.py`** - Advanced template management and loading system

### Security & Performance

- **`security.py`** - Input sanitization, rate limiting, and origin validation
- **`performance.py`** - Performance monitoring, debouncing, and resource management

### Static Assets

- **`static/js/`** - Client-side JavaScript including WebSocket communication
- **`static/css/`** - Comprehensive styling for the interactive interface
- **`templates/`** - Jinja2 templates for the web interface

## Features

### Core Features

- **Real-time collaborative editing** with WebSocket synchronization
- **Live preview** with instant diagram rendering
- **Comprehensive template library** with built-in and custom templates
- **Multi-format export** (SVG, PNG, PDF, Mermaid code, JSON)
- **Advanced validation** with real-time feedback and suggestions
- **Full Mermaid syntax support** for all diagram types

### Security Features

- **Input sanitization** to prevent XSS and injection attacks
- **Rate limiting** for API endpoints and WebSocket connections
- **Origin validation** for cross-origin request protection
- **Session management** with secure session handling
- **Resource limits** to prevent abuse and ensure stability

### Performance Features

- **Debounced operations** to reduce excessive updates
- **Connection pooling** for efficient WebSocket management
- **Performance monitoring** with detailed metrics
- **Resource management** with automatic cleanup
- **Optimized rendering** with fallback mechanisms

### Supported Diagram Types

- **Flowcharts** (`flowchart TD`, `graph TD`)
- **Sequence Diagrams** (`sequenceDiagram`)
- **Class Diagrams** (`classDiagram`)
- **State Diagrams** (`stateDiagram`)
- **Entity-Relationship Diagrams** (`erDiagram`)

## Usage Example

```python
from diagramaid.interactive import InteractiveServer, DiagramBuilder

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
pip install diagramaid[interactive]
```

## Web Interface

The interactive module provides a complete web interface accessible at:

- **Editor**: `http://localhost:8080/editor`
- **Gallery**: `http://localhost:8080/gallery`
- **API**: `http://localhost:8080/api/docs`

## Configuration

Interactive features can be configured:

```python
from diagramaid import MermaidConfig

config = MermaidConfig()
config.set_interactive_port(8080)
config.set_websocket_enabled(True)
config.set_auto_save(True)
```
