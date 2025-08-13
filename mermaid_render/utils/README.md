# Utils Module

This module provides utility functions and helper classes for common operations in the Mermaid Render library.

## Components

### Core Utilities
- **`helpers.py`** - General helper functions for file operations, format detection, and common tasks
- **`export.py`** - Export utilities for saving diagrams in various formats and batch operations
- **`validation.py`** - Validation utility functions and convenience methods

## Key Features

- **File Operations**: Safe file handling, directory creation, and path utilities
- **Format Detection**: Automatic format detection from file extensions
- **Batch Operations**: Export multiple diagrams efficiently
- **Validation Helpers**: Quick validation functions for common use cases
- **Filename Sanitization**: Safe filename generation and cleaning

## Usage Example

```python
from mermaid_render.utils import (
    export_to_file, 
    validate_mermaid_syntax,
    get_supported_formats,
    sanitize_filename
)

# Quick validation
is_valid = validate_mermaid_syntax("flowchart TD; A --> B")

# Export utilities
export_to_file(diagram, "output/my-diagram.svg")

# Get available formats
formats = get_supported_formats()
print(f"Supported formats: {formats}")

# Sanitize filename
safe_name = sanitize_filename("My Diagram (v1.0).svg")
```

## Export Functions

### Single Diagram Export
- `export_to_file()` - Export single diagram to file
- `export_multiple_formats()` - Export same diagram to multiple formats

### Batch Export
- `batch_export()` - Export multiple diagrams efficiently
- Support for directory organization
- Automatic format detection

## Validation Utilities

### Quick Validation
- `validate_mermaid_syntax()` - Full validation with detailed results
- `quick_validate()` - Simple boolean validation
- `get_validation_errors()` - Extract error messages only

### Specialized Validation
- `validate_node_id()` - Validate node identifiers
- `suggest_fixes()` - Get suggestions for fixing validation errors

## Helper Functions

- `detect_diagram_type()` - Automatically detect diagram type from code
- `get_available_themes()` - List all available themes
- `ensure_directory()` - Create directories safely
- `sanitize_filename()` - Clean filenames for safe file operations
