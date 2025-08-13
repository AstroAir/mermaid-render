# Configuration Module

This module provides comprehensive configuration management for the Mermaid Render library, including global settings, theme management, and environment-specific configurations.

## Components

### Configuration Management
- **`config_manager.py`** - Advanced configuration management with file loading, environment variables, and validation
- **`theme_manager.py`** - Theme configuration and management system

## Key Features

- **Hierarchical Configuration**: Support for default, file-based, environment, and runtime configurations
- **Theme Management**: Comprehensive theme system with built-in and custom themes
- **Environment Integration**: Automatic loading of configuration from environment variables
- **Validation**: Schema-based configuration validation
- **Hot Reloading**: Dynamic configuration updates without restart

## Usage Example

```python
from mermaid_render.config import ConfigManager, ThemeManager

# Advanced configuration management
config_manager = ConfigManager()
config_manager.load_from_file("config.yaml")
config_manager.set("rendering.timeout", 60)

# Theme management
theme_manager = ThemeManager()
theme_manager.load_theme("dark")
custom_theme = theme_manager.create_custom_theme({
    "primaryColor": "#ff6b6b",
    "backgroundColor": "#2d3748"
})
```

## Configuration Structure

The configuration system supports nested settings:

```yaml
# config.yaml
rendering:
  timeout: 30
  validate_syntax: true
  
themes:
  default_theme: "default"
  custom_themes_dir: "./themes"
  
ai:
  provider: "openai"
  model: "gpt-4"
  
cache:
  enabled: true
  backend: "redis"
  ttl: 3600
```

## Environment Variables

Configuration can be overridden using environment variables:
- `MERMAID_RENDER_TIMEOUT` - Rendering timeout
- `MERMAID_RENDER_THEME` - Default theme
- `MERMAID_RENDER_AI_PROVIDER` - AI provider
- `MERMAID_RENDER_CACHE_ENABLED` - Enable/disable caching
