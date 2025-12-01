# Caching System

Mermaid Render includes a sophisticated caching system to improve performance and reduce rendering overhead.

## Overview

The caching system provides:

- **Multiple Backend Support**: Memory, file system, Redis, and database caching
- **Intelligent Cache Keys**: Content-based hashing with configuration awareness
- **Performance Monitoring**: Built-in metrics and monitoring
- **Cache Invalidation**: Smart invalidation strategies
- **Compression**: Optional compression for storage efficiency

## Quick Start

### Basic Caching

```python
from diagramaid import MermaidRenderer
from diagramaid.cache import MemoryCache

# Enable memory caching
cache = MemoryCache(max_size=1000)
renderer = MermaidRenderer(cache=cache)

# First render - cached
diagram = "flowchart TD\n    A --> B"
result = renderer.render(diagram)  # Slow - not cached

# Second render - from cache
result = renderer.render(diagram)  # Fast - from cache
```

## Cache Backends

### Memory Cache

Best for single-process applications with limited memory usage.

```python
from diagramaid.cache import MemoryCache

cache = MemoryCache(
    max_size=1000,           # Maximum number of items
    ttl=3600,               # Time to live in seconds
    cleanup_interval=300     # Cleanup interval in seconds
)
```

### File System Cache

Persistent caching using the file system.

```python
from diagramaid.cache import FileSystemCache

cache = FileSystemCache(
    cache_dir="./cache",     # Cache directory
    max_size_mb=100,        # Maximum cache size in MB
    ttl=86400,              # 24 hours TTL
    compression=True         # Enable compression
)
```

### Redis Cache

Distributed caching with Redis backend.

```python
from diagramaid.cache import RedisCache

cache = RedisCache(
    host="localhost",
    port=6379,
    db=0,
    password="your-password",
    ttl=3600,
    key_prefix="mermaid:"
)
```

### Database Cache

SQL database caching for enterprise applications.

```python
from diagramaid.cache import DatabaseCache

cache = DatabaseCache(
    connection_string="postgresql://user:pass@localhost/db",
    table_name="mermaid_cache",
    ttl=7200
)
```

## Cache Configuration

### Global Configuration

```python
from diagramaid.config import CacheConfig

config = CacheConfig(
    backend="redis",
    ttl=3600,
    max_size=10000,
    compression=True,
    monitoring=True
)

renderer = MermaidRenderer(cache_config=config)
```

### Per-Renderer Configuration

```python
# Different cache settings per renderer
svg_cache = FileSystemCache(cache_dir="./svg_cache")
png_cache = RedisCache(host="localhost", db=1)

svg_renderer = SVGRenderer(cache=svg_cache)
png_renderer = PNGRenderer(cache=png_cache)
```

## Cache Keys

### Automatic Key Generation

Cache keys are automatically generated based on:

- Diagram content (normalized)
- Renderer configuration
- Output format
- Theme settings

```python
# These will have different cache keys
result1 = renderer.render(diagram, theme="default")
result2 = renderer.render(diagram, theme="dark")
```

### Custom Cache Keys

```python
# Provide custom cache key
result = renderer.render(
    diagram,
    cache_key="my-custom-key-v1"
)
```

### Cache Key Inspection

```python
# Get the cache key that would be used
key = renderer.get_cache_key(diagram, format="svg")
print(f"Cache key: {key}")
```

## Performance Monitoring

### Cache Statistics

```python
from diagramaid.cache import CacheMonitor

monitor = CacheMonitor(cache)

# Get cache statistics
stats = monitor.get_stats()
print(f"Hit rate: {stats.hit_rate:.2%}")
print(f"Total hits: {stats.hits}")
print(f"Total misses: {stats.misses}")
print(f"Cache size: {stats.size}")
```

### Performance Metrics

```python
# Enable detailed metrics
cache = MemoryCache(enable_metrics=True)

# Access metrics
metrics = cache.get_metrics()
print(f"Average lookup time: {metrics.avg_lookup_time}ms")
print(f"Average store time: {metrics.avg_store_time}ms")
print(f"Memory usage: {metrics.memory_usage_mb}MB")
```

## Cache Management

### Manual Cache Operations

```python
# Check if item is cached
is_cached = cache.exists(key)

# Get item from cache
item = cache.get(key)

# Store item in cache
cache.set(key, value, ttl=3600)

# Remove item from cache
cache.delete(key)

# Clear entire cache
cache.clear()
```

### Cache Warming

```python
from diagramaid.cache import CacheWarmer

warmer = CacheWarmer(renderer)

# Warm cache with common diagrams
diagrams = [
    "flowchart TD\n    A --> B",
    "sequenceDiagram\n    A->>B: Hello",
    # ... more diagrams
]

warmer.warm_cache(diagrams)
```

### Cache Invalidation

```python
# Invalidate by pattern
cache.invalidate_pattern("flowchart:*")

# Invalidate by tag
cache.invalidate_tag("user-123")

# Automatic invalidation on configuration change
renderer.update_config(theme="dark")  # Invalidates related cache entries
```

## Advanced Features

### Conditional Caching

```python
# Cache only expensive operations
def should_cache(diagram, config):
    return len(diagram) > 1000 or config.format == "pdf"

cache = MemoryCache(cache_condition=should_cache)
```

### Cache Hierarchies

```python
# Multi-level caching
l1_cache = MemoryCache(max_size=100)      # Fast, small
l2_cache = FileSystemCache(max_size_mb=1000)  # Slower, larger

cache = HierarchicalCache([l1_cache, l2_cache])
```

### Async Caching

```python
from diagramaid.cache import AsyncRedisCache

async def render_with_cache():
    cache = AsyncRedisCache(host="localhost")
    renderer = AsyncMermaidRenderer(cache=cache)

    result = await renderer.render(diagram)
    return result
```

## Configuration Examples

### Development Setup

```python
# Fast, simple caching for development
cache = MemoryCache(max_size=100, ttl=300)
```

### Production Setup

```python
# Robust caching for production
cache = RedisCache(
    host="redis-cluster.example.com",
    port=6379,
    db=0,
    ttl=3600,
    max_connections=20,
    retry_on_timeout=True,
    health_check_interval=30
)
```

### High-Performance Setup

```python
# Multi-tier caching for high performance
memory_cache = MemoryCache(max_size=1000, ttl=300)
redis_cache = RedisCache(host="localhost", ttl=3600)
file_cache = FileSystemCache(cache_dir="./cache", ttl=86400)

cache = HierarchicalCache([memory_cache, redis_cache, file_cache])
```

## Troubleshooting

### Common Issues

1. **Cache Misses**: Check cache key generation and TTL settings
2. **Memory Usage**: Monitor cache size and implement cleanup
3. **Performance**: Use appropriate backend for your use case

### Debugging

```python
# Enable cache debugging
cache = MemoryCache(debug=True)

# This will log cache operations
result = renderer.render(diagram)
```

## See Also

- [Performance Guide](performance.md)
- [Configuration Reference](configuration.md)
- [API Reference](../api-reference/cache.md)
