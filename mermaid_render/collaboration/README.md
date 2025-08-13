# Collaboration Module

This module provides collaborative features for the Mermaid Render library, enabling real-time collaboration, version control, and team-based diagram editing.

## Components

### Core Collaboration Services

- **`collaboration_manager.py`** - Main collaboration orchestration and session management
- **`version_control.py`** - Version control integration and diagram versioning
- **`diff_engine.py`** - Diagram difference detection and visualization
- **`merge_resolver.py`** - Conflict resolution for collaborative editing
- **`comments.py`** - Comment system for diagram annotations and feedback

### Supporting Infrastructure

- **`activity_log.py`** - Activity tracking and audit logging
- **`utils.py`** - Utility functions for collaboration features

## Key Features

- **Real-time Collaboration**: Multiple users can edit diagrams simultaneously
- **Version Control**: Track changes and maintain diagram history
- **Conflict Resolution**: Intelligent merging of concurrent edits
- **Comment System**: Add annotations and feedback to diagrams
- **Activity Tracking**: Monitor user actions and changes

## Usage Example

```python
from mermaid_render.collaboration import CollaborationManager

# Create collaborative session
manager = CollaborationManager()
session = manager.create_session("project-diagrams")

# Add collaborators
session.add_collaborator("user1@example.com")
session.add_collaborator("user2@example.com")

# Track changes
session.commit_changes("Updated user flow diagram")
```

## Dependencies

This module requires the `collaboration` optional dependency group:

```bash
pip install mermaid-render[collaboration]
```

## Configuration

Collaboration features require database and WebSocket configuration:

```python
from mermaid_render import MermaidConfig

config = MermaidConfig()
config.set_database_url("postgresql://localhost/mermaid_collab")
config.set_websocket_enabled(True)
```
