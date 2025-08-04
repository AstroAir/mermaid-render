"""
Pytest configuration and fixtures for the Mermaid Render test suite.
"""

import tempfile
from pathlib import Path
from typing import Any, Dict

import pytest

# Register test categories as markers
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow tests")
    config.addinivalue_line("markers", "network: Tests requiring network access")
    config.addinivalue_line("markers", "svg: SVG rendering tests")
    config.addinivalue_line("markers", "browser: Browser compatibility tests")
    config.addinivalue_line("markers", "error_handling: Error handling tests")
    config.addinivalue_line("markers", "theme: Theme support tests")
    config.addinivalue_line("markers", "export: Export functionality tests")
    config.addinivalue_line("markers", "remote: Remote rendering tests")
    config.addinivalue_line("markers", "performance: Performance tests")

from mermaid_render import (
    ConfigManager,
    FlowchartDiagram,
    MermaidConfig,
    MermaidRenderer,
    SequenceDiagram,
    ThemeManager,
)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_config() -> Dict[str, Any]:
    """Sample configuration for testing."""
    return {
        "server_url": "https://mermaid.ink",
        "timeout": 30.0,
        "validate_syntax": True,
        "default_theme": "default",
        "default_format": "svg",
    }


@pytest.fixture
def mermaid_config(sample_config) -> MermaidConfig:
    """Create a MermaidConfig instance for testing."""
    return MermaidConfig(**sample_config)


@pytest.fixture
def mermaid_renderer(mermaid_config) -> MermaidRenderer:
    """Create a MermaidRenderer instance for testing."""
    return MermaidRenderer(config=mermaid_config)


@pytest.fixture
def theme_manager(temp_dir) -> ThemeManager:
    """Create a ThemeManager instance for testing."""
    return ThemeManager(custom_themes_dir=temp_dir / "themes")


@pytest.fixture
def config_manager() -> ConfigManager:
    """Create a ConfigManager instance for testing."""
    return ConfigManager(load_env=False)


@pytest.fixture
def sample_flowchart() -> FlowchartDiagram:
    """Create a sample flowchart diagram for testing."""
    flowchart = FlowchartDiagram(direction="TD")
    flowchart.add_node("A", "Start", shape="circle")
    flowchart.add_node("B", "Process", shape="rectangle")
    flowchart.add_node("C", "End", shape="circle")
    flowchart.add_edge("A", "B", label="Begin")
    flowchart.add_edge("B", "C", label="Finish")
    return flowchart


@pytest.fixture
def sample_sequence() -> SequenceDiagram:
    """Create a sample sequence diagram for testing."""
    sequence = SequenceDiagram(title="Sample Sequence")
    sequence.add_participant("Alice")
    sequence.add_participant("Bob")
    sequence.add_message("Alice", "Bob", "Hello Bob!", "sync")
    sequence.add_message("Bob", "Alice", "Hi Alice!", "return")
    return sequence


@pytest.fixture
def sample_mermaid_code() -> str:
    """Sample Mermaid diagram code for testing."""
    return """
flowchart TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Process]
    B -->|No| D[Skip]
    C --> E[End]
    D --> E
"""


@pytest.fixture
def invalid_mermaid_code() -> str:
    """Invalid Mermaid diagram code for testing."""
    return """
flowchart TD
    A[Start --> B{Decision
    B -->|Yes| C[Process]
    B -->|No| D[Skip
    C --> E[End]
    D --> E
"""


@pytest.fixture
def sample_themes() -> Dict[str, Dict[str, Any]]:
    """Sample theme configurations for testing."""
    return {
        "test_theme": {
            "theme": "test",
            "primaryColor": "#ff0000",
            "primaryTextColor": "#ffffff",
            "primaryBorderColor": "#000000",
            "lineColor": "#333333",
        },
        "custom_theme": {
            "theme": "custom",
            "primaryColor": "#00ff00",
            "primaryTextColor": "#000000",
            "primaryBorderColor": "#666666",
            "lineColor": "#999999",
        },
    }


# Test data fixtures
@pytest.fixture
def diagram_test_cases():
    """Test cases for different diagram types."""
    return {
        "flowchart": """
flowchart TD
    A[Start] --> B[Process]
    B --> C[End]
""",
        "sequence": """
sequenceDiagram
    participant A as Alice
    participant B as Bob
    A->>B: Hello Bob!
    B-->>A: Hi Alice!
""",
        "class": """
classDiagram
    class Animal {
        +String name
        +move() void
    }
    class Dog {
        +bark() void
    }
    Animal <|-- Dog
""",
        "state": """
stateDiagram-v2
    [*] --> Still
    Still --> [*]
    Still --> Moving
    Moving --> Still
    Moving --> Crash
    Crash --> [*]
""",
    }


@pytest.fixture
def mock_responses():
    """Mock HTTP responses for testing."""
    return {
        "svg_success": """<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
    <rect width="100" height="100" fill="blue"/>
</svg>""",
        "png_success": b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00d\x00\x00\x00d\x08\x06\x00\x00\x00p\xe2\x95[\x00\x00\x00\x19tEXtSoftware\x00Adobe ImageReadyq\xc9e<\x00\x00\x00\x0eIDATx\xdab\x00\x02\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82",
    }


# Utility functions for tests
def assert_valid_svg(content: str) -> None:
    """Assert that content is valid SVG."""
    assert content.strip().startswith("<svg")
    assert "</svg>" in content
    assert 'xmlns="http://www.w3.org/2000/svg"' in content


def assert_valid_png(content: bytes) -> None:
    """Assert that content is valid PNG."""
    assert content.startswith(b"\x89PNG")
    assert b"IEND" in content


def create_test_diagram(diagram_type: str = "flowchart") -> str:
    """Create a test diagram of the specified type."""
    diagrams = {
        "flowchart": """
flowchart TD
    A[Start] --> B[Process]
    B --> C[End]
""",
        "sequence": """
sequenceDiagram
    participant A
    participant B
    A->>B: Message
    B-->>A: Response
""",
    }
    return diagrams.get(diagram_type, diagrams["flowchart"])


# Markers for different test categories
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.slow = pytest.mark.slow
pytest.mark.network = pytest.mark.network
