"""Utility functions for AI-powered features."""

from typing import Any, Dict, List, Optional

from mermaid_render.ai.providers import AIProvider, CustomProviderConfig, OpenRouterProvider, ProviderManager

from .analysis import DiagramAnalyzer
from .diagram_generator import DiagramGenerator, GenerationConfig
from .nl_processor import NLProcessor
from .optimization import DiagramOptimizer
from .suggestions import SuggestionEngine


def generate_from_text(
    text: str,
    diagram_type: str = "auto",
    style_preference: str = "clean",
    complexity_level: str = "medium",
) -> Dict[str, Any]:
    """
    Generate diagram from natural language text.

    Args:
        text: Natural language description
        diagram_type: Type of diagram to generate
        style_preference: Style preference (clean, detailed, minimal)
        complexity_level: Complexity level (simple, medium, complex)

    Returns:
        Generation result dictionary
    """
    from .diagram_generator import DiagramType

    config = GenerationConfig(
        diagram_type=DiagramType(diagram_type),
        style_preference=style_preference,
        complexity_level=complexity_level,
    )

    generator = DiagramGenerator()
    result = generator.from_text(text, config)

    return result.to_dict()


def optimize_diagram(
    diagram_code: str,
    optimization_types: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Optimize diagram using AI-powered optimization.

    Args:
        diagram_code: Mermaid diagram code
        optimization_types: Types of optimization to apply

    Returns:
        List of optimization results
    """
    optimizer = DiagramOptimizer()

    if optimization_types is None:
        optimization_types = ["layout", "style"]

    results: List[Dict[str, Any]] = []

    if "layout" in optimization_types:
        layout_result = optimizer.optimize_layout(diagram_code)
        results.append(layout_result.to_dict())

    if "style" in optimization_types:
        style_result = optimizer.optimize_style(diagram_code)
        results.append(style_result.to_dict())

    return results


def analyze_diagram(
    diagram_code: str, context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Analyze diagram quality and complexity.

    Args:
        diagram_code: Mermaid diagram code
        context: Additional context about the diagram

    Returns:
        Analysis report dictionary
    """
    analyzer = DiagramAnalyzer()
    report = analyzer.analyze(diagram_code, context)

    return report.to_dict()


def get_suggestions(
    diagram_code: str,
    suggestion_types: Optional[List[str]] = None,
    priority_filter: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get AI-powered suggestions for diagram improvement.

    Args:
        diagram_code: Mermaid diagram code
        suggestion_types: Types of suggestions to get
        priority_filter: Filter by priority (low, medium, high, critical)

    Returns:
        List of suggestion dictionaries
    """
    from .suggestions import SuggestionPriority, SuggestionType

    engine = SuggestionEngine()

    if suggestion_types:
        suggestions = []
        for suggestion_type in suggestion_types:
            type_suggestions = engine.get_suggestions_by_type(
                diagram_code, SuggestionType(suggestion_type)
            )
            suggestions.extend(type_suggestions)
    else:
        suggestions = engine.get_suggestions(diagram_code)

    # Filter by priority if specified
    if priority_filter:
        priority = SuggestionPriority(priority_filter)
        suggestions = [s for s in suggestions if s.priority == priority]

    return [s.to_dict() for s in suggestions]


def extract_entities(text: str) -> Dict[str, Any]:
    """
    Extract entities from natural language text.

    Args:
        text: Input text

    Returns:
        Entity extraction result dictionary
    """
    processor = NLProcessor()
    entities = processor.extract_entities(text)

    return entities.to_dict()


def classify_intent(text: str) -> Dict[str, Any]:
    """
    Classify intent of natural language text.

    Args:
        text: Input text

    Returns:
        Intent classification result dictionary
    """
    processor = NLProcessor()
    intent = processor.classify_intent(text)

    return intent.to_dict()


def improve_diagram_with_ai(
    diagram_code: str,
    improvement_request: str,
    style_preference: str = "clean",
) -> Dict[str, Any]:
    """
    Improve existing diagram based on AI suggestions.

    Args:
        diagram_code: Current diagram code
        improvement_request: Description of desired improvements
        style_preference: Style preference for improvements

    Returns:
        Improvement result dictionary
    """
    config = GenerationConfig(style_preference=style_preference)

    generator = DiagramGenerator()
    result = generator.improve_diagram(diagram_code, improvement_request, config)

    return result.to_dict()


def get_diagram_insights(diagram_code: str) -> Dict[str, Any]:
    """
    Get comprehensive insights about a diagram.

    Args:
        diagram_code: Mermaid diagram code

    Returns:
        Comprehensive insights dictionary
    """
    # Analyze diagram
    analyzer = DiagramAnalyzer()
    analysis = analyzer.analyze(diagram_code)

    # Get suggestions
    suggestion_engine = SuggestionEngine()
    suggestions = suggestion_engine.get_suggestions(diagram_code)

    # Get optimization recommendations
    optimizer = DiagramOptimizer()
    optimization_suggestions = optimizer.get_optimization_suggestions(diagram_code)

    return {
        "analysis": analysis.to_dict(),
        "suggestions": [s.to_dict() for s in suggestions],
        "optimization_suggestions": optimization_suggestions,
        "summary": {
            "complexity_level": analysis.complexity.complexity_level,
            "overall_quality": analysis.quality.overall_score,
            "main_issues": analysis.issues[:3],  # Top 3 issues
            "top_recommendations": analysis.recommendations[
                :3
            ],  # Top 3 recommendations
        },
    }


def validate_ai_generated_diagram(diagram_code: str) -> Dict[str, Any]:
    """
    Validate AI-generated diagram for quality and correctness.

    Args:
        diagram_code: Generated diagram code

    Returns:
        Validation result dictionary
    """
    from ..validators import MermaidValidator

    # Basic syntax validation
    validator = MermaidValidator()
    syntax_result = validator.validate(diagram_code)

    # AI quality analysis
    analyzer = DiagramAnalyzer()
    quality_analysis = analyzer.analyze(diagram_code)

    # Determine overall validity
    is_valid = (
        syntax_result.is_valid
        and quality_analysis.quality.overall_score > 0.5
        and len(quality_analysis.issues) < 3
    )

    return {
        "is_valid": is_valid,
        "syntax_validation": {
            "is_valid": syntax_result.is_valid,
            "errors": syntax_result.errors,
            "warnings": syntax_result.warnings,
        },
        "quality_analysis": quality_analysis.to_dict(),
        "validation_score": (
            (1.0 if syntax_result.is_valid else 0.0) * 0.4
            + quality_analysis.quality.overall_score * 0.6
        ),
    }


def generate_diagram_variations(
    base_diagram: str,
    variation_count: int = 3,
) -> List[Dict[str, Any]]:
    """
    Generate variations of a base diagram.

    Args:
        base_diagram: Base diagram code
        variation_count: Number of variations to generate

    Returns:
        List of diagram variations
    """
    generator = DiagramGenerator()
    variations: List[Dict[str, Any]] = []

    variation_requests = [
        "Make this diagram more detailed",
        "Simplify this diagram",
        "Improve the visual styling",
        "Add more descriptive labels",
        "Reorganize the layout",
    ]

    for i in range(min(variation_count, len(variation_requests))):
        try:
            result = generator.improve_diagram(base_diagram, variation_requests[i])
            variations.append(
                {
                    "variation_id": i + 1,
                    "description": variation_requests[i],
                    "diagram_code": result.diagram_code,
                    "confidence": result.confidence_score,
                }
            )
        except Exception:
            # Skip failed variations
            continue

    return variations


def create_provider_from_config(
    provider_type: str,
    config_dict: Dict[str, Any]
) -> AIProvider:
    """
    Create an AI provider from configuration dictionary.

    Args:
        provider_type: Type of provider (openai, anthropic, openrouter, custom)
        config_dict: Configuration dictionary

    Returns:
        Configured AI provider instance

    Example:
        >>> config = {
        ...     "api_key": "your-key",
        ...     "model": "gpt-4",
        ...     "timeout": 30
        ... }
        >>> provider = create_provider_from_config("openai", config)
    """
    from .providers import ProviderFactory, ProviderConfig, CustomProviderConfig as _CustomProviderConfig

    if provider_type.lower() == "custom":
        cfg: _CustomProviderConfig = _CustomProviderConfig(**config_dict)
    else:
        cfg: ProviderConfig = ProviderConfig(**config_dict)

    return ProviderFactory.create_provider(provider_type, cfg)


def setup_multi_provider_generation(
    provider_configs: List[Dict[str, Any]],
    fallback_to_local: bool = True
) -> ProviderManager:
    """
    Setup multiple AI providers with automatic fallback.

    Args:
        provider_configs: List of provider configuration dictionaries
        fallback_to_local: Whether to add local provider as final fallback

    Returns:
        Configured ProviderManager instance

    Example:
        >>> configs = [
        ...     {"type": "openai", "config": {"api_key": "key1"}},
        ...     {"type": "anthropic", "config": {"api_key": "key2"}},
        ... ]
        >>> manager = setup_multi_provider_generation(configs)
    """
    from .providers import ProviderManager as _ProviderManager, ProviderFactory

    manager: _ProviderManager = _ProviderManager()

    for provider_config in provider_configs:
        try:
            provider_type = provider_config["type"]
            config = provider_config["config"]

            provider = create_provider_from_config(provider_type, config)
            manager.add_provider(provider)

        except Exception as e:
            import logging
            logging.warning(
                f"Failed to create provider {provider_config.get('type')}: {e}")

    if fallback_to_local:
        try:
            local_provider = ProviderFactory.create_provider("local")
            manager.add_provider(local_provider)
        except Exception as e:
            import logging
            logging.warning(f"Failed to create local provider: {e}")

    return manager


def generate_with_multiple_providers(
    text: str,
    provider_configs: List[Dict[str, Any]],
    generation_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate diagram using multiple providers with automatic fallback.

    Args:
        text: Natural language description
        provider_configs: List of provider configurations
        generation_config: Generation configuration

    Returns:
        Generation result with provider information
    """
    manager = setup_multi_provider_generation(provider_configs)

    if not manager.providers:
        raise ValueError("No providers available")

    # Use the first available provider for generation
    for provider in manager.get_available_providers():
        try:
            from .diagram_generator import DiagramGenerator, GenerationConfig

            generator = DiagramGenerator(ai_provider=provider)

            if generation_config:
                config = GenerationConfig(**generation_config)
            else:
                config = GenerationConfig()

            result = generator.from_text(text, config)
            result_dict = result.to_dict()
            result_dict["provider_used"] = provider.provider_name
            result_dict["available_providers"] = [
                p.provider_name for p in manager.get_available_providers()]

            return result_dict

        except Exception as e:
            import logging
            logging.warning(f"Provider {provider.provider_name} failed: {e}")
            continue

    raise RuntimeError("All providers failed")


def batch_generate_diagrams(
    texts: List[str],
    provider_config: Dict[str, Any],
    generation_config: Optional[Dict[str, Any]] = None,
    max_concurrent: int = 5
) -> List[Dict[str, Any]]:
    """
    Generate multiple diagrams in batch with concurrency control.

    Args:
        texts: List of natural language descriptions
        provider_config: Provider configuration
        generation_config: Generation configuration
        max_concurrent: Maximum concurrent generations

    Returns:
        List of generation results
    """
    import concurrent.futures

    def generate_single(text: str) -> Dict[str, Any]:
        """Generate a single diagram."""
        try:
            provider = create_provider_from_config(
                provider_config["type"],
                provider_config["config"]
            )

            from .diagram_generator import DiagramGenerator, GenerationConfig

            generator = DiagramGenerator(ai_provider=provider)

            if generation_config:
                config = GenerationConfig(**generation_config)
            else:
                config = GenerationConfig()

            result = generator.from_text(text, config)
            result_dict = result.to_dict()
            result_dict["input_text"] = text
            result_dict["status"] = "success"

            return result_dict

        except Exception as e:
            return {
                "input_text": text,
                "status": "error",
                "error": str(e),
                "diagram_code": None
            }

    # Use ThreadPoolExecutor for concurrent generation
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_concurrent) as executor:
        results = list(executor.map(generate_single, texts))

    return results


def compare_provider_performance(
    test_prompts: List[str],
    provider_configs: List[Dict[str, Any]],
    metrics: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Compare performance of different AI providers.

    Args:
        test_prompts: List of test prompts
        provider_configs: List of provider configurations
        metrics: Metrics to collect (response_time, quality, cost)

    Returns:
        Performance comparison results
    """
    import time

    if metrics is None:
        metrics = ["response_time", "success_rate", "quality"]

    results: Dict[str, Dict[str, Any]] = {}

    for provider_config in provider_configs:
        provider_name = f"{provider_config['type']}"
        results[provider_name] = {
            "total_requests": int(len(test_prompts)),
            "successful_requests": 0,
            "failed_requests": 0,
            "total_time": 0.0,
            "average_time": 0.0,
            "responses": []  # type: List[Dict[str, Any]]
        }

        try:
            provider = create_provider_from_config(
                provider_config["type"],
                provider_config["config"]
            )

            for prompt in test_prompts:
                start_time = time.time()

                try:
                    response = provider.generate_text(prompt)
                    end_time = time.time()

                    response_time: float = end_time - start_time
                    results[provider_name]["successful_requests"] = int(
                        results[provider_name]["successful_requests"]) + 1
                    results[provider_name]["total_time"] = float(
                        results[provider_name]["total_time"]) + response_time

                    # Ensure responses is a list
                    if not isinstance(results[provider_name]["responses"], list):
                        results[provider_name]["responses"] = []

                    results[provider_name]["responses"].append({
                        "prompt": prompt,
                        "response": response.content if hasattr(response, 'content') else str(response),
                        "response_time": response_time,
                        "status": "success"
                    })

                except Exception as e:
                    end_time = time.time()
                    response_time = end_time - start_time

                    results[provider_name]["failed_requests"] = int(
                        results[provider_name]["failed_requests"]) + 1
                    if not isinstance(results[provider_name]["responses"], list):
                        results[provider_name]["responses"] = []
                    results[provider_name]["responses"].append({
                        "prompt": prompt,
                        "error": str(e),
                        "response_time": response_time,
                        "status": "error"
                    })

            # Calculate averages
            if int(results[provider_name]["successful_requests"]) > 0:
                results[provider_name]["average_time"] = (
                    float(results[provider_name]["total_time"]) /
                    int(results[provider_name]["successful_requests"])
                )

            results[provider_name]["success_rate"] = (
                int(results[provider_name]["successful_requests"]) /
                int(results[provider_name]["total_requests"])
            )

        except Exception as e:
            results[provider_name]["setup_error"] = str(e)

    return results


def export_provider_config(provider: AIProvider) -> Dict[str, Any]:
    """
    Export provider configuration for serialization.

    Args:
        provider: AI provider instance

    Returns:
        Serializable configuration dictionary
    """
    config_dict: Dict[str, Any] = {
        "provider_type": provider.provider_name,
        "is_available": provider.is_available(),
        "supported_models": provider.get_supported_models(),
    }

    if hasattr(provider, 'config'):
        config = getattr(provider, 'config')
        config_dict["config"] = {
            "model": getattr(config, "model", None),
            "timeout": getattr(config, "timeout", None),
            "max_retries": getattr(config, "max_retries", None),
            "base_url": getattr(config, "base_url", None),
            # Note: API key is not exported for security
        }

    if hasattr(provider, 'custom_config'):
        custom = getattr(provider, 'custom_config')
        config_dict["custom_config"] = {
            "name": getattr(custom, "name", None),
            "base_url": getattr(custom, "base_url", None),
            "auth_type": getattr(custom, "auth_type", None),
            "request_format": getattr(custom, "request_format", None),
            "response_format": getattr(custom, "response_format", None),
        }

    return config_dict


def validate_diagram_with_ai(
    diagram_code: str,
    validation_criteria: Optional[List[str]] = None,
    provider_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Use AI to validate and provide feedback on diagram quality.

    Args:
        diagram_code: Mermaid diagram code
        validation_criteria: Specific criteria to validate
        provider_config: AI provider configuration

    Returns:
        AI validation results
    """
    if validation_criteria is None:
        validation_criteria = [
            "syntax_correctness",
            "logical_flow",
            "clarity",
            "completeness",
            "best_practices"
        ]

    # Create validation prompt
    criteria_text = ", ".join(validation_criteria)
    prompt = f"""
Please analyze the following Mermaid diagram code and provide feedback on: {criteria_text}

Diagram code:
```
{diagram_code}
```

Please provide:
1. Overall quality score (1-10)
2. Specific issues found
3. Suggestions for improvement
4. Compliance with best practices

Format your response as structured feedback.
"""

    try:
        if provider_config:
            provider = create_provider_from_config(
                provider_config["type"],
                provider_config["config"]
            )
        else:
            # Use default provider
            from .providers import create_default_provider_manager
            manager = create_default_provider_manager()
            if not manager.providers:
                raise ValueError("No AI providers available")
            provider = manager.providers[0]

        response = provider.generate_text(prompt)
        content = response.content if hasattr(response, 'content') else str(response)

        return {
            "validation_result": content,
            "criteria_checked": validation_criteria,
            "provider_used": provider.provider_name,
            "status": "success"
        }

    except Exception as e:
        return {
            "validation_result": None,
            "criteria_checked": validation_criteria,
            "error": str(e),
            "status": "error"
        }


def create_openrouter_provider(
    api_key: Optional[str] = None,
    model: str = "openai/gpt-3.5-turbo",
    site_url: Optional[str] = None,
    site_name: Optional[str] = None
) -> OpenRouterProvider:
    """
    Convenience function to create OpenRouter provider.

    Args:
        api_key: OpenRouter API key (or from OPENROUTER_API_KEY env var)
        model: Model to use
        site_url: Site URL for attribution
        site_name: Site name for attribution

    Returns:
        Configured OpenRouter provider
    """
    from .providers import OpenRouterProvider as _OpenRouterProvider, ProviderConfig
    import os

    if api_key is None:
        api_key = os.getenv("OPENROUTER_API_KEY")

    config = ProviderConfig(
        api_key=api_key,
        model=model,
        base_url="https://openrouter.ai/api/v1"
    )

    # Add custom headers for attribution
    custom_headers: Dict[str, str] = {}
    if site_url:
        custom_headers["HTTP-Referer"] = site_url
    if site_name:
        custom_headers["X-Title"] = site_name

    if custom_headers:
        # ProviderConfig may support arbitrary fields; set via attribute
        setattr(config, "custom_headers", custom_headers)

    return _OpenRouterProvider(config)


def create_custom_provider_config(
    name: str,
    base_url: str,
    api_key: Optional[str] = None,
    request_format: str = "openai",
    response_format: str = "openai",
    auth_type: str = "bearer",
    **kwargs: Any
) -> CustomProviderConfig:
    """
    Convenience function to create custom provider configuration.

    Args:
        name: Provider name
        base_url: API base URL
        api_key: API key
        request_format: Request format (openai, anthropic, custom)
        response_format: Response format (openai, anthropic, custom)
        auth_type: Authentication type (bearer, api_key, basic, custom)
        **kwargs: Additional configuration options

    Returns:
        Custom provider configuration
    """
    from .providers import CustomProviderConfig as _CustomProviderConfig

    return _CustomProviderConfig(
        name=name,
        base_url=base_url,
        api_key=api_key,
        request_format=request_format,
        response_format=response_format,
        auth_type=auth_type,
        **kwargs
    )
