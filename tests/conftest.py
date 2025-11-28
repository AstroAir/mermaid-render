"""
Pytest configuration and fixtures for the Mermaid Render test suite.
"""

import tempfile
from collections.abc import Generator
from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest

from mermaid_render import (
    ConfigManager,
    FlowchartDiagram,
    MermaidConfig,
    MermaidRenderer,
    SequenceDiagram,
    ThemeManager,
)

# Register test categories as markers


def pytest_configure(config: Any) -> None:
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


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_config() -> dict[str, Any]:
    """Sample configuration for testing."""
    return {
        "server_url": "https://mermaid.ink",
        "timeout": 30.0,
        "validate_syntax": True,
        "default_theme": "default",
        "default_format": "svg",
    }


@pytest.fixture
def mermaid_config(sample_config: Any) -> MermaidConfig:
    """Create a MermaidConfig instance for testing."""
    return MermaidConfig(**sample_config)


@pytest.fixture
def mermaid_renderer(mermaid_config: Any) -> MermaidRenderer:
    """Create a MermaidRenderer instance for testing."""
    # Disable plugin system for unit tests to allow direct mocking
    # Also disable caching to prevent test interference
    mermaid_config.update({"cache_enabled": False})
    return MermaidRenderer(config=mermaid_config, use_plugin_system=False)


@pytest.fixture(autouse=True)
def mock_mermaid_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Provide a fallback Mermaid implementation when mermaid-py is unavailable."""
    try:
        import mermaid  # type: ignore # noqa: F401

        return  # Real mermaid is available
    except Exception:
        pass

    def _make_instance(*args: Any, **kwargs: Any) -> Mock:
        instance = Mock()
        instance.__str__ = Mock(return_value="<svg>mock</svg>")
        return instance

    fake_mermaid = Mock()
    fake_mermaid.Mermaid = Mock(side_effect=_make_instance)

    # Patch core and SVG renderer modules
    monkeypatch.setattr(
        "mermaid_render.renderers.svg_renderer.md",
        fake_mermaid,
        raising=False,
    )
    monkeypatch.setattr(
        "mermaid_render.renderers.svg_renderer._MERMAID_AVAILABLE",
        True,
        raising=False,
    )
    monkeypatch.setattr(
        "mermaid_render.core.md",
        fake_mermaid,
        raising=False,
    )
    monkeypatch.setattr(
        "mermaid_render.core._MERMAID_AVAILABLE",
        True,
        raising=False,
    )


@pytest.fixture(autouse=True)
def mock_core_renderer_manager(monkeypatch: pytest.MonkeyPatch) -> None:
    """Provide a lightweight RendererManager implementation for core tests."""
    from mermaid_render.exceptions import UnsupportedFormatError
    from mermaid_render.renderers.base import RenderResult

    class FakeRendererManager:
        def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: D401
            self._active_renderers: dict[str, Any] = {}

        def render(
            self,
            mermaid_code: str,
            format: str,
            preferred_renderer: str | None = None,
            **_: Any,
        ) -> RenderResult:
            allowed = {"svg", "png", "pdf"}
            if format.lower() not in allowed:
                raise UnsupportedFormatError(f"Unsupported format: {format}")

            if format.lower() == "svg":
                content: str | bytes = '<svg xmlns="http://www.w3.org/2000/svg">mock</svg>'
            else:
                content = b"mock-binary"

            metadata = {
                "attempts": [
                    {
                        "renderer": preferred_renderer or "mock",
                        "success": True,
                    }
                ]
            }

            return RenderResult(
                content=content,
                format=format,
                renderer_name="mock",
                render_time=0.001,
                success=True,
                metadata=metadata,
            )

        def get_available_formats(self) -> set[str]:
            return {"svg", "png", "pdf"}

        def cleanup(self) -> None:
            self._active_renderers.clear()

    monkeypatch.setattr("mermaid_render.core.RendererManager", FakeRendererManager)


@pytest.fixture
def theme_manager(temp_dir: Any) -> ThemeManager:
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
def sample_themes() -> dict[str, dict[str, Any]]:
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
def diagram_test_cases() -> dict[str, str]:
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
def mock_responses() -> dict[str, Any]:
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


# Test markers are defined in pytest_configure function above
