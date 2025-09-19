# AI Module Improvement Guide

This document describes the improved AI module features in mermaid-render, including new providers, custom provider support, and utility functions.

## Overview

The improved AI module provides:

1. **Optimized Core Providers**: Improved OpenAI and Anthropic providers with better error handling
2. **OpenRouter Integration**: Access to hundreds of AI models through OpenRouter's unified API
3. **Custom Provider Architecture**: Flexible framework for integrating any AI API
4. **Improved Utilities**: New functions for batch processing, performance comparison, and validation
5. **Provider Management**: Automatic fallback and multi-provider support

## Quick Start

### Basic Usage with OpenRouter

```python
from mermaid_render.ai import create_openrouter_provider, generate_from_text

# Create OpenRouter provider
provider = create_openrouter_provider(
    api_key="your-openrouter-key",
    model="openai/gpt-4",
    site_url="https://your-site.com",
    site_name="Your App"
)

# Generate diagram
result = generate_from_text(
    "Create a flowchart for user authentication process",
    provider_config={"type": "openrouter", "config": {"api_key": "your-key"}}
)
```

### Multi-Provider Setup with Fallback

```python
from mermaid_render.ai import setup_multi_provider_generation

# Configure multiple providers
provider_configs = [
    {
        "type": "openai",
        "config": {"api_key": "openai-key", "model": "gpt-4"}
    },
    {
        "type": "anthropic",
        "config": {"api_key": "anthropic-key", "model": "claude-3-sonnet"}
    },
    {
        "type": "openrouter",
        "config": {"api_key": "openrouter-key", "model": "meta-llama/llama-3.1-70b"}
    }
]

# Create manager with automatic fallback
manager = setup_multi_provider_generation(provider_configs)

# Generate with automatic provider selection
result = manager.generate_text("Create a sequence diagram for API calls")
```

## Provider Types

### 1. OpenAI Provider

Enhanced with better error handling, retry logic, and configuration options.

```python
from mermaid_render.ai import OpenAIProvider, ProviderConfig

config = ProviderConfig(
    api_key="your-openai-key",
    model="gpt-4",
    timeout=30,
    max_retries=3
)

provider = OpenAIProvider(config)
```

### 2. Anthropic Provider

Improved Claude integration with support for latest models.

```python
from mermaid_render.ai import AnthropicProvider, ProviderConfig

config = ProviderConfig(
    api_key="your-anthropic-key",
    model="claude-3-5-sonnet-20241022",
    timeout=30
)

provider = AnthropicProvider(config)
```

### 3. OpenRouter Provider

Access to hundreds of models through OpenRouter's unified API.

```python
from mermaid_render.ai import OpenRouterProvider, ProviderConfig

config = ProviderConfig(
    api_key="your-openrouter-key",
    model="anthropic/claude-3-opus",
    base_url="https://openrouter.ai/api/v1",
    custom_headers={
        "HTTP-Referer": "https://your-site.com",
        "X-Title": "Your App Name"
    }
)

provider = OpenRouterProvider(config)

# List available models
models = provider.list_models()
```

### 4. Custom Provider

Flexible architecture for integrating any AI API.

```python
from mermaid_render.ai import CustomProvider, CustomProviderConfig

config = CustomProviderConfig(
    name="my-custom-api",
    base_url="https://api.example.com/v1",
    api_key="your-api-key",
    auth_type="bearer",
    request_format="openai",  # or "anthropic", "custom"
    response_format="openai",
    model_mapping={
        "default": "my-model-v1",
        "advanced": "my-model-v2"
    },
    parameter_mapping={
        "max_tokens": "max_length",
        "temperature": "randomness"
    }
)

provider = CustomProvider(config)
```

## Enhanced Utilities

### Batch Generation

Process multiple prompts efficiently:

```python
from mermaid_render.ai import batch_generate_diagrams

texts = [
    "Create a flowchart for user registration",
    "Design a sequence diagram for payment processing",
    "Generate a class diagram for user management"
]

provider_config = {
    "type": "openrouter",
    "config": {"api_key": "your-key", "model": "openai/gpt-4"}
}

results = batch_generate_diagrams(
    texts=texts,
    provider_config=provider_config,
    max_concurrent=3
)
```

### Provider Performance Comparison

Compare different providers on your use cases:

```python
from mermaid_render.ai import compare_provider_performance

test_prompts = [
    "Create a simple flowchart",
    "Design a complex system architecture",
    "Generate a user journey map"
]

provider_configs = [
    {"type": "openai", "config": {"api_key": "key1"}},
    {"type": "anthropic", "config": {"api_key": "key2"}},
    {"type": "openrouter", "config": {"api_key": "key3"}}
]

comparison = compare_provider_performance(test_prompts, provider_configs)
```

### AI-Powered Validation

Use AI to validate and improve diagrams:

```python
from mermaid_render.ai import validate_diagram_with_ai

diagram_code = """
flowchart TD
    A[Start] --> B[Process]
    B --> C[End]
"""

validation_result = validate_diagram_with_ai(
    diagram_code=diagram_code,
    validation_criteria=["syntax_correctness", "logical_flow", "clarity"],
    provider_config={"type": "openai", "config": {"api_key": "your-key"}}
)
```

## Configuration Examples

### Environment Variables

Set up providers using environment variables:

```bash
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export OPENROUTER_API_KEY="your-openrouter-key"
```

### JSON Configuration

```json
{
  "providers": [
    {
      "type": "openai",
      "config": {
        "api_key": "${OPENAI_API_KEY}",
        "model": "gpt-4",
        "timeout": 30,
        "max_retries": 3
      }
    },
    {
      "type": "openrouter",
      "config": {
        "api_key": "${OPENROUTER_API_KEY}",
        "model": "anthropic/claude-3-opus",
        "custom_headers": {
          "HTTP-Referer": "https://your-site.com"
        }
      }
    }
  ]
}
```

### YAML Configuration

```yaml
providers:
  - type: anthropic
    config:
      api_key: ${ANTHROPIC_API_KEY}
      model: claude-3-5-sonnet-20241022
      timeout: 45

  - type: custom
    config:
      name: my-api
      base_url: https://api.example.com/v1
      api_key: ${CUSTOM_API_KEY}
      request_format: openai
      auth_type: bearer
```

## Error Handling

The enhanced AI module provides comprehensive error handling:

```python
from mermaid_render.ai import (
    ProviderError,
    AuthenticationError,
    RateLimitError,
    ModelNotFoundError
)

try:
    result = provider.generate_text("Create a diagram")
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except RateLimitError as e:
    print(f"Rate limit exceeded: {e}")
except ModelNotFoundError as e:
    print(f"Model not found: {e}")
except ProviderError as e:
    print(f"Provider error: {e}")
```

## Best Practices

1. **Use Provider Manager**: Set up multiple providers with fallback for reliability
2. **Configure Timeouts**: Set appropriate timeouts for your use case
3. **Handle Rate Limits**: Implement retry logic and respect rate limits
4. **Secure API Keys**: Use environment variables, never hardcode keys
5. **Monitor Performance**: Use performance comparison tools to optimize
6. **Validate Results**: Use AI validation for critical applications

## Migration Guide

### From Old AI Module

The enhanced module is backward compatible. Update your imports:

```python
# Old
from mermaid_render.ai import OpenAIProvider

# New (same, but enhanced)
from mermaid_render.ai import OpenAIProvider, ProviderConfig

# New features
from mermaid_render.ai import (
    OpenRouterProvider,
    CustomProvider,
    ProviderManager,
    create_openrouter_provider
)
```

### Configuration Migration

Old provider initialization:

```python
provider = OpenAIProvider(api_key="key", model="gpt-4")
```

New provider initialization:

```python
config = ProviderConfig(api_key="key", model="gpt-4")
provider = OpenAIProvider(config)
```

## Troubleshooting

### Common Issues

1. **Provider Not Available**: Check API keys and network connectivity
2. **Model Not Found**: Verify model name and provider support
3. **Rate Limits**: Implement exponential backoff and respect limits
4. **Timeout Errors**: Increase timeout values for complex requests

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Next Steps

- Explore the examples in `/examples/ai_features_showcase.py`
- Check the API reference for detailed parameter descriptions
- Join our community for support and feature requests
