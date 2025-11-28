# AI Module

This module provides AI-powered features for the Mermaid Render library, including natural language processing, diagram generation, optimization, and intelligent suggestions.

## Components

### Core AI Services

- **`analysis.py`** - Diagram analysis and quality assessment
- **`diagram_generator.py`** - AI-powered diagram generation from text descriptions
- **`nl_processor.py`** - Natural language processing for diagram creation
- **`optimization.py`** - AI-driven diagram optimization and improvement
- **`suggestions.py`** - Intelligent suggestions for diagram enhancement

### Infrastructure

- **`providers.py`** - AI service provider integrations (OpenAI, Anthropic, etc.)
- **`utils.py`** - Utility functions for AI operations

## Key Features

- **Text-to-Diagram Generation**: Convert natural language descriptions into Mermaid diagrams
- **Diagram Analysis**: Analyze existing diagrams for quality, complexity, and best practices
- **Smart Optimization**: AI-driven suggestions for improving diagram structure and readability
- **Multi-Provider Support**: Integration with multiple AI providers for flexibility and reliability

## Usage Example

```python
from mermaid_render.ai import DiagramGenerator, DiagramAnalyzer

# Generate diagram from text
generator = DiagramGenerator()
diagram = generator.generate_from_text("Create a user login process flowchart")

# Analyze diagram quality
analyzer = DiagramAnalyzer()
analysis = analyzer.analyze(diagram.to_mermaid())
print(f"Quality score: {analysis.quality.overall_score}")
```

## Dependencies

This module requires the `ai` optional dependency group:

```bash
pip install mermaid-render[ai]
```

## Configuration

AI features can be configured through the main configuration system:

```python
from mermaid_render import MermaidConfig

config = MermaidConfig()
config.set_ai_provider("openai")
config.set_ai_api_key("your-api-key")
```
