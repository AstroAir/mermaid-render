# Configuration

Comprehensive configuration options for customizing Mermaid Render behavior, output, and performance.

## Overview

Configuration in Mermaid Render covers:

- **Renderer Settings**: Output formats, quality, dimensions
- **Theme Configuration**: Colors, fonts, styling
- **Performance Options**: Caching, optimization, timeouts
- **Security Settings**: Input validation, resource limits
- **Integration Options**: Web server, API, database settings

## Basic Configuration

### Quick Configuration

```python
from mermaid_render import MermaidRenderer
from mermaid_render.config import Config

# Basic configuration
config = Config(
    theme="dark",
    format="svg",
    width=800,
    height=600
)

renderer = MermaidRenderer(config=config)
```

### Configuration from File

```python
# Load from YAML file
config = Config.from_file("config.yaml")

# Load from JSON file
config = Config.from_json("config.json")

# Load from environment variables
config = Config.from_env()
```

## Configuration Options

### Renderer Configuration

```python
from mermaid_render.config import RendererConfig

renderer_config = RendererConfig(
    # Output format
    default_format="svg",
    supported_formats=["svg", "png", "pdf"],
    
    # Dimensions
    default_width=800,
    default_height=600,
    max_width=4000,
    max_height=4000,
    
    # Quality settings
    dpi=300,
    quality=95,
    
    # Rendering options
    background_color="transparent",
    scale=1.0,
    timeout=30,  # seconds
    
    # Error handling
    strict_mode=False,
    fallback_renderer="svg"
)
```

### Theme Configuration

```python
from mermaid_render.config import ThemeConfig

theme_config = ThemeConfig(
    # Default theme
    default_theme="default",
    
    # Theme directory
    theme_directory="./themes",
    
    # Custom themes
    custom_themes={
        "corporate": {
            "primary_color": "#2c3e50",
            "secondary_color": "#3498db",
            "font_family": "Arial, sans-serif"
        }
    },
    
    # Theme caching
    cache_themes=True,
    theme_cache_ttl=3600
)
```

### Performance Configuration

```python
from mermaid_render.config import PerformanceConfig

performance_config = PerformanceConfig(
    # Caching
    enable_caching=True,
    cache_backend="memory",  # memory, file, redis, database
    cache_ttl=3600,
    max_cache_size=1000,
    
    # Concurrency
    max_concurrent_renders=10,
    worker_threads=4,
    
    # Resource limits
    max_diagram_size=1024 * 1024,  # 1MB
    max_render_time=60,  # seconds
    memory_limit=512 * 1024 * 1024,  # 512MB
    
    # Optimization
    enable_optimization=True,
    minify_output=False,
    compress_cache=True
)
```

## Configuration Files

### YAML Configuration

```yaml
# config.yaml
renderer:
  default_format: svg
  width: 800
  height: 600
  dpi: 300
  timeout: 30

theme:
  default_theme: default
  theme_directory: ./themes
  cache_themes: true

performance:
  enable_caching: true
  cache_backend: redis
  cache_ttl: 3600
  max_concurrent_renders: 10

security:
  validate_input: true
  max_diagram_size: 1048576
  allowed_formats: [svg, png, pdf]

logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: mermaid_render.log
```

### JSON Configuration

```json
{
  "renderer": {
    "default_format": "svg",
    "width": 800,
    "height": 600,
    "dpi": 300,
    "timeout": 30
  },
  "theme": {
    "default_theme": "default",
    "theme_directory": "./themes",
    "cache_themes": true
  },
  "performance": {
    "enable_caching": true,
    "cache_backend": "redis",
    "cache_ttl": 3600,
    "max_concurrent_renders": 10
  }
}
```

### Environment Variables

```bash
# Environment configuration
export MERMAID_RENDER_THEME=dark
export MERMAID_RENDER_FORMAT=svg
export MERMAID_RENDER_WIDTH=1200
export MERMAID_RENDER_HEIGHT=800
export MERMAID_RENDER_CACHE_BACKEND=redis
export MERMAID_RENDER_CACHE_TTL=7200
export MERMAID_RENDER_LOG_LEVEL=DEBUG
```

## Advanced Configuration

### Security Configuration

```python
from mermaid_render.config import SecurityConfig

security_config = SecurityConfig(
    # Input validation
    validate_input=True,
    sanitize_input=True,
    max_input_size=1024 * 1024,  # 1MB
    
    # Resource limits
    max_nodes=1000,
    max_edges=2000,
    max_nesting_depth=10,
    
    # Allowed features
    allowed_diagram_types=["flowchart", "sequence", "class"],
    allowed_formats=["svg", "png"],
    allow_external_links=False,
    allow_javascript=False,
    
    # Rate limiting
    rate_limit_enabled=True,
    requests_per_minute=60,
    requests_per_hour=1000
)
```

### Logging Configuration

```python
from mermaid_render.config import LoggingConfig

logging_config = LoggingConfig(
    # Log level
    level="INFO",  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    
    # Output
    console_output=True,
    file_output=True,
    log_file="mermaid_render.log",
    
    # Format
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    date_format="%Y-%m-%d %H:%M:%S",
    
    # Rotation
    max_file_size=10 * 1024 * 1024,  # 10MB
    backup_count=5,
    
    # Structured logging
    structured_logging=True,
    json_format=False
)
```

### Database Configuration

```python
from mermaid_render.config import DatabaseConfig

database_config = DatabaseConfig(
    # Connection
    url="postgresql://user:pass@localhost/mermaid_db",
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    
    # Tables
    cache_table="mermaid_cache",
    session_table="mermaid_sessions",
    user_table="mermaid_users",
    
    # Options
    echo_sql=False,
    auto_create_tables=True,
    migration_directory="./migrations"
)
```

## Configuration Profiles

### Environment-Specific Profiles

```python
# Development profile
dev_config = Config(
    renderer=RendererConfig(timeout=10, strict_mode=False),
    performance=PerformanceConfig(enable_caching=False),
    logging=LoggingConfig(level="DEBUG"),
    security=SecurityConfig(validate_input=False)
)

# Production profile
prod_config = Config(
    renderer=RendererConfig(timeout=30, strict_mode=True),
    performance=PerformanceConfig(
        enable_caching=True,
        cache_backend="redis",
        max_concurrent_renders=50
    ),
    logging=LoggingConfig(level="WARNING"),
    security=SecurityConfig(
        validate_input=True,
        rate_limit_enabled=True
    )
)

# Use appropriate profile
config = prod_config if os.getenv("ENV") == "production" else dev_config
```

### Profile Inheritance

```python
# Base configuration
base_config = Config(
    renderer=RendererConfig(width=800, height=600),
    theme=ThemeConfig(default_theme="default")
)

# Extend for specific use case
api_config = base_config.extend(
    performance=PerformanceConfig(max_concurrent_renders=100),
    security=SecurityConfig(rate_limit_enabled=True)
)
```

## Dynamic Configuration

### Runtime Configuration Changes

```python
# Change configuration at runtime
renderer = MermaidRenderer(config)

# Update specific settings
renderer.config.renderer.timeout = 60
renderer.config.theme.default_theme = "dark"

# Reload configuration
renderer.reload_config()
```

### Configuration Validation

```python
from mermaid_render.config import validate_config

# Validate configuration
validation_result = validate_config(config)
if not validation_result.is_valid:
    for error in validation_result.errors:
        print(f"Config error: {error}")
```

## Integration Configuration

### Web Server Configuration

```python
from mermaid_render.config import WebConfig

web_config = WebConfig(
    # Server settings
    host="0.0.0.0",
    port=8080,
    debug=False,
    
    # SSL
    ssl_enabled=True,
    ssl_cert="path/to/cert.pem",
    ssl_key="path/to/key.pem",
    
    # CORS
    cors_enabled=True,
    cors_origins=["https://example.com"],
    
    # Authentication
    auth_enabled=True,
    auth_provider="oauth2",
    
    # Rate limiting
    rate_limit="100/hour",
    
    # File uploads
    max_upload_size=10 * 1024 * 1024,  # 10MB
    allowed_extensions=[".mmd", ".txt"]
)
```

### API Configuration

```python
from mermaid_render.config import APIConfig

api_config = APIConfig(
    # Versioning
    version="v1",
    base_path="/api/v1",
    
    # Documentation
    enable_docs=True,
    docs_path="/docs",
    
    # Response format
    default_response_format="json",
    include_metadata=True,
    
    # Pagination
    default_page_size=20,
    max_page_size=100,
    
    # Caching
    cache_responses=True,
    cache_headers=True
)
```

## Configuration Best Practices

### Security Best Practices

```python
# Secure configuration
secure_config = Config(
    security=SecurityConfig(
        validate_input=True,
        sanitize_input=True,
        max_input_size=512 * 1024,  # 512KB
        allowed_diagram_types=["flowchart", "sequence"],
        allow_external_links=False,
        allow_javascript=False,
        rate_limit_enabled=True
    ),
    renderer=RendererConfig(
        timeout=30,
        max_width=2000,
        max_height=2000
    )
)
```

### Performance Best Practices

```python
# High-performance configuration
perf_config = Config(
    performance=PerformanceConfig(
        enable_caching=True,
        cache_backend="redis",
        cache_ttl=3600,
        max_cache_size=10000,
        max_concurrent_renders=50,
        worker_threads=8,
        enable_optimization=True,
        compress_cache=True
    ),
    renderer=RendererConfig(
        timeout=60,
        quality=85  # Slightly lower quality for speed
    )
)
```

### Monitoring Configuration

```python
# Monitoring and observability
monitoring_config = Config(
    logging=LoggingConfig(
        level="INFO",
        structured_logging=True,
        json_format=True
    ),
    performance=PerformanceConfig(
        enable_metrics=True,
        metrics_endpoint="/metrics",
        health_check_endpoint="/health"
    )
)
```

## Configuration Management

### Configuration Versioning

```python
# Version configuration for compatibility
config_v1 = Config(version="1.0", ...)
config_v2 = Config(version="2.0", ...)

# Migrate configuration
migrated_config = migrate_config(config_v1, target_version="2.0")
```

### Configuration Templates

```python
# Create configuration templates
template = ConfigTemplate(
    name="web_service",
    description="Configuration for web service deployment",
    parameters={
        "host": {"type": "string", "default": "localhost"},
        "port": {"type": "integer", "default": 8080},
        "cache_backend": {"type": "string", "choices": ["memory", "redis"]}
    }
)

# Generate configuration from template
config = template.generate(host="0.0.0.0", port=80, cache_backend="redis")
```

## Troubleshooting

### Common Configuration Issues

1. **Invalid theme**: Check theme name and availability
2. **Cache connection**: Verify cache backend settings
3. **Permission errors**: Check file/directory permissions
4. **Resource limits**: Adjust timeout and memory limits

### Configuration Debugging

```python
# Enable configuration debugging
config.debug = True

# Print current configuration
print(config.to_dict())

# Validate configuration
validation = validate_config(config)
print(validation.report())
```

## See Also

- [Themes Guide](themes.md)
- [Performance Tuning](../guides/performance.md)
- [Security Guide](../guides/security.md)
- [API Reference](../api-reference/config.md)
