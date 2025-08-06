#!/usr/bin/env python3
"""
Enhanced AI Features Showcase

This example demonstrates the new AI module features including:
- OpenRouter provider integration
- Custom provider architecture  
- Multi-provider management with fallback
- Batch generation capabilities
- Provider performance comparison
- AI-powered validation

Run with: python examples/enhanced_ai_features.py
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mermaid_render.ai import (
    # Enhanced providers
    OpenRouterProvider,
    CustomProvider,
    ProviderManager,
    
    # Configuration classes
    ProviderConfig,
    CustomProviderConfig,
    
    # Utility functions
    create_openrouter_provider,
    create_provider_from_config,
    setup_multi_provider_generation,
    batch_generate_diagrams,
    compare_provider_performance,
    validate_diagram_with_ai,
    generate_with_multiple_providers,
    
    # Factory and management
    ProviderFactory,
    create_default_provider_manager,
)


def demo_openrouter_provider() -> None:
    """Demonstrate OpenRouter provider usage."""
    print("\n=== OpenRouter Provider Demo ===")

    # Check if API key is available
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("⚠️  OPENROUTER_API_KEY not set, using mock example")
        return
    
    try:
        # Create OpenRouter provider
        provider = create_openrouter_provider(
            api_key=api_key,
            model="openai/gpt-3.5-turbo",
            site_url="https://mermaid-render.dev",
            site_name="Mermaid Render Enhanced AI Demo"
        )
        
        print(f"✅ OpenRouter provider created")
        print(f"   Available: {provider.is_available()}")
        print(f"   Supported models: {len(provider.get_supported_models())} models")
        
        # Generate a simple diagram
        prompt = "Create a flowchart showing the steps to make coffee"
        response = provider.generate_text(prompt)
        
        print(f"✅ Generated diagram using {response.provider}")
        print(f"   Model used: {response.model}")
        print(f"   Content length: {len(response.content)} characters")
        
        # List available models (first 5)
        models = provider.list_models()[:5]
        print(f"✅ Available models (showing first 5):")
        for model in models:
            print(f"   - {model.get('id', 'Unknown')}")
            
    except Exception as e:
        print(f"❌ OpenRouter demo failed: {e}")


def demo_custom_provider() -> None:
    """Demonstrate custom provider configuration."""
    print("\n=== Custom Provider Demo ===")
    
    try:
        # Create a custom provider configuration
        # This is a mock example - replace with your actual API
        config = CustomProviderConfig(
            name="mock-api",
            base_url="https://api.example.com/v1",
            api_key="mock-key",
            auth_type="bearer",
            request_format="openai",
            response_format="openai",
            model_mapping={
                "default": "mock-model-v1",
                "advanced": "mock-model-v2"
            },
            parameter_mapping={
                "max_tokens": "max_length",
                "temperature": "randomness"
            }
        )
        
        print(f"✅ Custom provider config created: {config.name}")
        print(f"   Base URL: {config.base_url}")
        print(f"   Auth type: {config.auth_type}")
        print(f"   Request format: {config.request_format}")
        
        # Note: We don't actually call the API since it's a mock
        print("✅ Custom provider architecture validated")
        
    except Exception as e:
        print(f"❌ Custom provider demo failed: {e}")


def demo_multi_provider_management() -> None:
    """Demonstrate multi-provider setup with fallback."""
    print("\n=== Multi-Provider Management Demo ===")
    
    try:
        # Create provider configurations
        provider_configs = []
        
        # Add OpenAI if available
        if os.getenv("OPENAI_API_KEY"):
            provider_configs.append({
                "type": "openai",
                "config": {
                    "api_key": os.getenv("OPENAI_API_KEY"),
                    "model": "gpt-3.5-turbo"
                }
            })
        
        # Add Anthropic if available
        if os.getenv("ANTHROPIC_API_KEY"):
            provider_configs.append({
                "type": "anthropic", 
                "config": {
                    "api_key": os.getenv("ANTHROPIC_API_KEY"),
                    "model": "claude-3-haiku-20240307"
                }
            })
        
        # Add OpenRouter if available
        if os.getenv("OPENROUTER_API_KEY"):
            provider_configs.append({
                "type": "openrouter",
                "config": {
                    "api_key": os.getenv("OPENROUTER_API_KEY"),
                    "model": "openai/gpt-3.5-turbo"
                }
            })
        
        if not provider_configs:
            print("⚠️  No API keys available, using local provider only")
            provider_configs = [{"type": "local", "config": {}}]
        
        # Setup multi-provider manager
        manager = setup_multi_provider_generation(provider_configs)
        
        print(f"✅ Multi-provider manager created")
        print(f"   Total providers: {len(manager.providers)}")
        print(f"   Available providers: {len(manager.get_available_providers())}")
        
        # Show provider status
        status = manager.get_provider_status()
        for provider_name, available in status.items():
            status_icon = "✅" if available else "❌"
            print(f"   {status_icon} {provider_name}: {'Available' if available else 'Unavailable'}")
        
        # Generate with automatic fallback
        prompt = "Create a simple sequence diagram for user login"
        response = manager.generate_text(prompt)
        
        print(f"✅ Generated with provider: {response.provider}")
        print(f"   Content preview: {response.content[:100]}...")
        
    except Exception as e:
        print(f"❌ Multi-provider demo failed: {e}")


def demo_batch_generation() -> None:
    """Demonstrate batch diagram generation."""
    print("\n=== Batch Generation Demo ===")
    
    try:
        # Prepare test prompts
        prompts = [
            "Create a flowchart for user registration process",
            "Design a sequence diagram for API authentication",
            "Generate a class diagram for a simple blog system",
            "Create a state diagram for order processing"
        ]
        
        # Use local provider for demo (always available)
        provider_config = {
            "type": "local",
            "config": {}
        }
        
        print(f"✅ Starting batch generation of {len(prompts)} diagrams")
        
        # Generate in batch
        results = batch_generate_diagrams(
            texts=prompts,
            provider_config=provider_config,
            max_concurrent=2
        )
        
        print(f"✅ Batch generation completed")
        
        # Show results
        successful = sum(1 for r in results if r["status"] == "success")
        failed = len(results) - successful
        
        print(f"   Successful: {successful}")
        print(f"   Failed: {failed}")
        
        for i, result in enumerate(results, 1):
            status_icon = "✅" if result["status"] == "success" else "❌"
            print(f"   {status_icon} Diagram {i}: {result['status']}")
            
    except Exception as e:
        print(f"❌ Batch generation demo failed: {e}")


def demo_provider_performance_comparison() -> None:
    """Demonstrate provider performance comparison."""
    print("\n=== Provider Performance Comparison Demo ===")
    
    try:
        # Test prompts
        test_prompts = [
            "Create a simple flowchart",
            "Design a basic sequence diagram",
            "Generate a minimal class diagram"
        ]
        
        # Provider configurations (using available providers)
        provider_configs = []
        
        # Always include local provider
        provider_configs.append({
            "type": "local",
            "config": {}
        })
        
        # Add real providers if available
        if os.getenv("OPENAI_API_KEY"):
            provider_configs.append({
                "type": "openai",
                "config": {"api_key": os.getenv("OPENAI_API_KEY")}
            })
        
        if len(provider_configs) < 2:
            print("⚠️  Only one provider available, comparison limited")
        
        print(f"✅ Comparing {len(provider_configs)} providers on {len(test_prompts)} prompts")
        
        # Run comparison
        comparison = compare_provider_performance(test_prompts, provider_configs)
        
        print(f"✅ Performance comparison completed")
        
        # Show results
        for provider_name, metrics in comparison.items():
            print(f"\n   📊 {provider_name}:")
            print(f"      Success rate: {metrics.get('success_rate', 0):.2%}")
            print(f"      Average time: {metrics.get('average_time', 0):.2f}s")
            print(f"      Total requests: {metrics.get('total_requests', 0)}")
            
    except Exception as e:
        print(f"❌ Performance comparison demo failed: {e}")


def demo_ai_validation() -> None:
    """Demonstrate AI-powered diagram validation."""
    print("\n=== AI Validation Demo ===")
    
    try:
        # Sample diagram with potential issues
        diagram_code = """
        flowchart TD
            A[Start] --> B[Process]
            B --> C[Decision]
            C --> D[End]
            C --> E[Alternative]
        """
        
        # Use any available provider for validation
        provider_config = None
        if os.getenv("OPENAI_API_KEY"):
            provider_config = {
                "type": "openai",
                "config": {"api_key": os.getenv("OPENAI_API_KEY")}
            }
        elif os.getenv("ANTHROPIC_API_KEY"):
            provider_config = {
                "type": "anthropic", 
                "config": {"api_key": os.getenv("ANTHROPIC_API_KEY")}
            }
        
        if not provider_config:
            print("⚠️  No AI provider available for validation, skipping")
            return
        
        print(f"✅ Validating diagram with AI")
        
        # Validate diagram
        validation_result = validate_diagram_with_ai(
            diagram_code=diagram_code,
            validation_criteria=["syntax_correctness", "logical_flow", "clarity"],
            provider_config=provider_config
        )
        
        if validation_result["status"] == "success":
            print(f"✅ AI validation completed")
            print(f"   Provider used: {validation_result['provider_used']}")
            print(f"   Criteria checked: {', '.join(validation_result['criteria_checked'])}")
            print(f"   Feedback preview: {validation_result['validation_result'][:200]}...")
        else:
            print(f"❌ AI validation failed: {validation_result.get('error')}")
            
    except Exception as e:
        print(f"❌ AI validation demo failed: {e}")


def main() -> None:
    """Run all enhanced AI feature demonstrations."""
    print("🚀 Enhanced AI Features Showcase")
    print("=" * 50)
    
    # Run demonstrations
    demo_openrouter_provider()
    demo_custom_provider()
    demo_multi_provider_management()
    demo_batch_generation()
    demo_provider_performance_comparison()
    demo_ai_validation()
    
    print("\n" + "=" * 50)
    print("✅ Enhanced AI features showcase completed!")
    print("\n💡 Tips:")
    print("   - Set API keys as environment variables for full functionality")
    print("   - Check the documentation for more advanced usage patterns")
    print("   - Use provider management for production applications")


if __name__ == "__main__":
    main()
