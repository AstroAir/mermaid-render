#!/usr/bin/env python3
"""
Improved AI Features Showcase

This example demonstrates the new AI module features including:
- OpenRouter provider integration
- Custom provider architecture
- Multi-provider management with fallback
- Batch generation capabilities
- Provider performance comparison
- AI-powered validation

Run with: python examples/improved_ai_features.py
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from diagramaid.ai import (
    # Improved providers
    CustomProviderConfig,
    # Utility functions
    create_openrouter_provider,
    create_provider_from_config,
    setup_multi_provider_generation,
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
            model="anthropic/claude-3-opus",
            custom_headers={
                "HTTP-Referer": "https://diagramaid.dev",
                "X-Title": "Mermaid Render AI Features",
            },
        )

        # Generate diagram
        prompt = "Create a flowchart showing the user authentication process"
        result = provider.generate_text(prompt)

        print("✅ Generated diagram using OpenRouter:")
        print(f"Model: {provider.config.model}")
        print(f"Diagram preview: {result.content[:100]}...")

    except Exception as e:
        print(f"❌ OpenRouter demo failed: {e}")


def demo_custom_provider() -> None:
    """Demonstrate custom provider creation."""
    print("\n=== Custom Provider Demo ===")

    # Create custom provider configuration
    config = CustomProviderConfig(
        name="my-custom-api",
        base_url="https://api.example.com/v1",
        api_key="demo-key",
        request_format="openai",  # Use OpenAI-compatible format
        auth_type="bearer",
        custom_headers={
            "User-Agent": "MermaidRender/1.0",
            "X-Custom-Header": "demo-value",
        },
        timeout=30,
        max_retries=3,
    )

    try:
        # Create provider from config
        provider = create_provider_from_config(config)

        print("✅ Created custom provider:")
        print(f"Name: {config.name}")
        print(f"Base URL: {config.base_url}")
        print(f"Request format: {config.request_format}")
        print(f"Timeout: {config.timeout}s")

    except Exception as e:
        print(f"❌ Custom provider demo failed: {e}")


def demo_multi_provider_management() -> None:
    """Demonstrate multi-provider management with fallback."""
    print("\n=== Multi-Provider Management Demo ===")

    try:
        # Set up multiple providers with fallback
        provider_configs = [
            {
                "type": "openai",
                "config": {
                    "api_key": os.getenv("OPENAI_API_KEY", "demo-key"),
                    "model": "gpt-4",
                    "timeout": 30,
                },
            },
            {
                "type": "anthropic",
                "config": {
                    "api_key": os.getenv("ANTHROPIC_API_KEY", "demo-key"),
                    "model": "claude-3-sonnet-20240229",
                    "timeout": 30,
                },
            },
        ]

        # Create provider manager
        manager = setup_multi_provider_generation(
            provider_configs, fallback_enabled=True, max_retries=2
        )

        print("✅ Set up multi-provider manager:")
        print(f"Providers: {len(provider_configs)}")
        print("Fallback enabled: True")
        print("Max retries: 2")

        # Simulate generation with fallback
        prompt = "Create a sequence diagram for API authentication"
        print(f"\n🔄 Generating with prompt: '{prompt}'")
        print("(This would attempt primary provider, then fallback on failure)")

    except Exception as e:
        print(f"❌ Multi-provider demo failed: {e}")


def demo_batch_generation() -> None:
    """Demonstrate batch diagram generation."""
    print("\n=== Batch Generation Demo ===")

    # Sample prompts for batch generation
    prompts = [
        "Create a flowchart for user registration",
        "Design a class diagram for a shopping cart system",
        "Generate a sequence diagram for payment processing",
        "Create a state diagram for order status",
        "Design an ER diagram for a blog database",
    ]

    try:
        # Mock batch generation (would use real provider in practice)
        print("✅ Batch generation setup:")
        print(f"Prompts to process: {len(prompts)}")
        print("Batch size: 3")
        print("Parallel processing: True")

        for i, prompt in enumerate(prompts, 1):
            print(f"  {i}. {prompt}")

        print("\n🔄 Processing batch...")
        print("(This would generate all diagrams in parallel batches)")

    except Exception as e:
        print(f"❌ Batch generation demo failed: {e}")


def demo_provider_performance_comparison() -> None:
    """Demonstrate provider performance comparison."""
    print("\n=== Provider Performance Comparison Demo ===")

    test_prompts = [
        "Create a simple flowchart with 3 nodes",
        "Design a complex system architecture diagram",
        "Generate a user journey map with 5 steps",
    ]

    provider_configs = [
        {"type": "openai", "config": {"model": "gpt-3.5-turbo"}},
        {"type": "anthropic", "config": {"model": "claude-3-haiku-20240307"}},
        {"type": "openrouter", "config": {"model": "meta-llama/llama-2-70b-chat"}},
    ]

    try:
        print("✅ Performance comparison setup:")
        print(f"Test prompts: {len(test_prompts)}")
        print(f"Providers to compare: {len(provider_configs)}")

        for i, prompt in enumerate(test_prompts, 1):
            print(f"  {i}. {prompt}")

        print("\n📊 Comparison metrics:")
        print("  - Response time")
        print("  - Diagram quality score")
        print("  - Token usage")
        print("  - Success rate")
        print("  - Cost per generation")

        print("\n🔄 Running comparison...")
        print("(This would test all providers with all prompts)")

    except Exception as e:
        print(f"❌ Performance comparison demo failed: {e}")


def demo_ai_validation() -> None:
    """Demonstrate AI-powered diagram validation."""
    print("\n=== AI-Powered Validation Demo ===")

    # Sample diagrams for validation
    diagrams = [
        {
            "name": "Valid flowchart",
            "code": """
            flowchart TD
                A[Start] --> B{Decision}
                B -->|Yes| C[Process]
                B -->|No| D[End]
                C --> D
            """,
        },
        {
            "name": "Potentially problematic diagram",
            "code": """
            graph TD
                A --> B
                B --> C
                C --> A
                D --> E
            """,
        },
    ]

    try:
        print("✅ AI validation setup:")
        print(f"Diagrams to validate: {len(diagrams)}")

        for diagram in diagrams:
            print(f"\n🔍 Validating: {diagram['name']}")
            print("  Checks:")
            print("    - Syntax correctness")
            print("    - Logical flow")
            print("    - Best practices")
            print("    - Accessibility")
            print("    - Performance implications")

        print("\n🔄 Running AI validation...")
        print("(This would analyze each diagram and provide feedback)")

    except Exception as e:
        print(f"❌ AI validation demo failed: {e}")


def main() -> None:
    """Run all AI feature demonstrations."""
    print("🚀 Improved AI Features Showcase")
    print("=" * 50)

    # Run all demonstrations
    demo_openrouter_provider()
    demo_custom_provider()
    demo_multi_provider_management()
    demo_batch_generation()
    demo_provider_performance_comparison()
    demo_ai_validation()

    print("\n" + "=" * 50)
    print("✅ All demonstrations completed!")
    print("\n💡 Tips:")
    print("  - Set API keys as environment variables for live demos")
    print("  - Check the AI module documentation for full API details")
    print("  - Use provider comparison to optimize for your use case")
    print("  - Enable AI validation for production deployments")


if __name__ == "__main__":
    main()
