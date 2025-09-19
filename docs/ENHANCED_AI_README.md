# Improved AI Module - Quick Reference

## 🚀 New Features

### 1. OpenRouter Integration

Access hundreds of AI models through OpenRouter's unified API:

```python
from mermaid_render.ai import create_openrouter_provider

provider = create_openrouter_provider(
    api_key="your-openrouter-key",
    model="anthropic/claude-3-opus"
)
```

### 2. Custom Provider Support

Integrate any AI API with flexible configuration:

```python
from mermaid_render.ai import CustomProvider, CustomProviderConfig

config = CustomProviderConfig(
    name="my-api",
    base_url="https://api.example.com/v1",
    api_key="your-key",
    request_format="openai"  # or "anthropic", "custom"
)

provider = CustomProvider(config)
```

### 3. Multi-Provider Management

Automatic fallback between providers:

```python
from mermaid_render.ai import setup_multi_provider_generation

configs = [
    {"type": "openai", "config": {"api_key": "key1"}},
    {"type": "anthropic", "config": {"api_key": "key2"}},
    {"type": "openrouter", "config": {"api_key": "key3"}}
]

manager = setup_multi_provider_generation(configs)
result = manager.generate_text("Create a flowchart")
```

### 4. Enhanced Utilities

#### Batch Generation

```python
from mermaid_render.ai import batch_generate_diagrams

results = batch_generate_diagrams(
    texts=["Create flowchart", "Design sequence diagram"],
    provider_config={"type": "openai", "config": {"api_key": "key"}},
    max_concurrent=3
)
```

#### Provider Performance Comparison

```python
from mermaid_render.ai import compare_provider_performance

comparison = compare_provider_performance(
    test_prompts=["Create a diagram"],
    provider_configs=[
        {"type": "openai", "config": {"api_key": "key1"}},
        {"type": "anthropic", "config": {"api_key": "key2"}}
    ]
)
```

#### AI-Powered Validation

```python
from mermaid_render.ai import validate_diagram_with_ai

result = validate_diagram_with_ai(
    diagram_code="flowchart TD\n    A --> B",
    validation_criteria=["syntax", "clarity", "best_practices"]
)
```

## 🔧 Configuration

### Environment Variables

```bash
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export OPENROUTER_API_KEY="your-openrouter-key"
```

### Provider Configuration

```python
from mermaid_render.ai import ProviderConfig

config = ProviderConfig(
    api_key="your-key",
    model="gpt-4",
    timeout=30,
    max_retries=3,
    custom_headers={"X-Custom": "value"}
)
```

## 📚 Examples

- **Basic Usage**: `examples/enhanced_ai_features.py`
- **Documentation**: `docs/ai_module_enhancement.md`
- **Tests**: `tests/unit/test_enhanced_ai.py`

## 🛠️ Error Handling

```python
from mermaid_render.ai import (
    ProviderError,
    AuthenticationError,
    RateLimitError,
    ModelNotFoundError
)

try:
    result = provider.generate_text("prompt")
except AuthenticationError:
    print("Check your API key")
except RateLimitError:
    print("Rate limit exceeded, try again later")
except ModelNotFoundError:
    print("Model not available")
```

## 🔄 Migration from Old AI Module

The enhanced module is backward compatible:

```python
# Old way (still works)
from mermaid_render.ai import OpenAIProvider
provider = OpenAIProvider(api_key="key", model="gpt-4")

# New way (recommended)
from mermaid_render.ai import OpenAIProvider, ProviderConfig
config = ProviderConfig(api_key="key", model="gpt-4")
provider = OpenAIProvider(config)
```

## 🎯 Key Benefits

1. **Reliability**: Automatic fallback between providers
2. **Flexibility**: Support for any AI API through custom providers
3. **Performance**: Batch processing and performance monitoring
4. **Quality**: AI-powered validation and optimization
5. **Cost Optimization**: Access to hundreds of models via OpenRouter

## 🚀 Getting Started

1. Install dependencies: `pip install -r requirements.txt`
2. Set API keys as environment variables
3. Run the example: `python examples/enhanced_ai_features.py`
4. Check the full documentation: `docs/ai_module_enhancement.md`

## 📞 Support

- Documentation: `docs/ai_module_enhancement.md`
- Examples: `examples/enhanced_ai_features.py`
- Tests: `tests/unit/test_enhanced_ai.py`
- Issues: GitHub Issues
