#!/usr/bin/env python3
"""
Testing and validation showcase for Mermaid Render.

This script demonstrates testing patterns, validation strategies,
and error handling for applications using the library.
"""

import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from typing import Dict, Any, List, Union, Optional

from mermaid_render import (
    MermaidRenderer,
    quick_render,
    validate_mermaid_syntax,
    ValidationError,
    RenderingError,
    DiagramError,
    UnsupportedFormatError,
)
from mermaid_render.models.class_diagram import ClassMethod, ClassAttribute  # noqa: F401 (kept for reference consistency)


def create_output_dir() -> Path:
    """Create output directory for examples."""
    output_dir = Path("output/testing")
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def build_flowchart_code(title: Optional[str] = None) -> str:
    """Build a simple flowchart Mermaid string for testing."""
    lines = ["flowchart TD"]
    if title:
        lines.append(f'    %% {title}')
    lines += [
        "    start((Start))",
        "    process[Process]",
        "    end((End))",
        "    start --> process",
        "    process --> end",
    ]
    return "\n".join(lines)


def build_sequence_code(title: Optional[str] = None) -> str:
    """Build a simple sequence diagram Mermaid string for testing."""
    lines = ["sequenceDiagram", "    autonumber"]
    if title:
        lines.append(f'    %% {title}')
    lines += [
        "    participant alice as Alice",
        "    participant bob as Bob",
        "    alice->>bob: Hello Bob!",
        "    bob-->>alice: Hi Alice!",
    ]
    return "\n".join(lines)


def build_class_diagram_code(title: Optional[str] = None) -> str:
    """Build a simple class diagram Mermaid string for testing."""
    lines = ["classDiagram"]
    if title:
        lines.append(f'    %% {title}')
    lines += [
        "    class Animal {",
        "        <<abstract>>",
        "        protected string name",
        "        +void move() *",
        "    }",
        "    class Dog {",
        "        +void bark()",
        "        +void move()",
        "    }",
        "    Animal <|-- Dog",
    ]
    return "\n".join(lines)


class TestDiagramCreation(unittest.TestCase):
    """Test cases for diagram creation and validation."""
    
    def setUp(self) -> None:
        """Set up test fixtures."""
        self.renderer = MermaidRenderer()
        self.output_dir = create_output_dir()
    
    def test_flowchart_creation(self) -> None:
        """Test creating a valid flowchart (string-based)."""
        mermaid_code = build_flowchart_code("Test Flowchart")

        # Basic expectations
        self.assertIn("flowchart TD", mermaid_code)
        self.assertIn("start((Start))", mermaid_code)
        self.assertIn("process[Process]", mermaid_code)
        self.assertIn("start --> process", mermaid_code)
        
        # Test validation
        result = validate_mermaid_syntax(mermaid_code)
        self.assertTrue(result.is_valid, f"Validation errors: {result.errors}")
    
    def test_sequence_diagram_creation(self) -> None:
        """Test creating a valid sequence diagram (string-based)."""
        mermaid_code = build_sequence_code("Test Sequence")
        
        # Basic expectations
        self.assertIn("sequenceDiagram", mermaid_code)
        self.assertIn("participant alice as Alice", mermaid_code)
        self.assertIn("alice->>bob: Hello Bob!", mermaid_code)
        self.assertIn("autonumber", mermaid_code)
        
        # Test validation
        result = validate_mermaid_syntax(mermaid_code)
        self.assertTrue(result.is_valid, f"Validation errors: {result.errors}")
    
    def test_class_diagram_creation(self):
        """Test creating a valid class diagram (string-based)."""
        mermaid_code = build_class_diagram_code("Test Class Diagram")
        
        # Basic expectations
        self.assertIn("classDiagram", mermaid_code)
        self.assertIn("class Animal", mermaid_code)
        self.assertIn("Animal <|-- Dog", mermaid_code)
        
        # Test validation
        result = validate_mermaid_syntax(mermaid_code)
        self.assertTrue(result.is_valid, f"Validation errors: {result.errors}")
    
    def test_invalid_diagram_creation(self):
        """Test error handling for invalid diagrams with simple logical checks."""
        # Simulate a diagram API raising DiagramError for missing nodes in edges.
        # Since we build strings directly, emulate with a helper.
        def add_edge(nodes: set[str], src: str, dst: str):
            if src not in nodes or dst not in nodes:
                raise DiagramError(f"edge requires existing nodes: {src} -> {dst}")
        
        nodes: set[str] = set()
        with self.assertRaises(DiagramError):
            add_edge(nodes, "nonexistent1", "nonexistent2")
        
        # Duplicate node IDs simulated
        def add_node(nodes: set[str], node_id: str):
            if node_id in nodes:
                raise DiagramError(f"duplicate node id: {node_id}")
            nodes.add(node_id)
        
        add_node(nodes, "test")
        with self.assertRaises(DiagramError):
            add_node(nodes, "test")
    
    def test_validation_errors(self):
        """Test validation of invalid Mermaid syntax."""
        invalid_syntax = """
        flowchart TD
            A[Start --> B[End
            B --> C[Missing bracket
        """
        
        result = validate_mermaid_syntax(invalid_syntax)
        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.errors), 0)


class TestRenderingWithMocks(unittest.TestCase):
    """Test rendering functionality with mocked dependencies."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.output_dir = create_output_dir()
    
    @patch('mermaid_render.core.requests.post')
    def test_successful_rendering(self, mock_post):
        """Test successful rendering with mocked HTTP request."""
        # Mock successful response
        mock_response = Mock()
        mock_response.content = b'<svg>test diagram</svg>'
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'image/svg+xml'}
        mock_post.return_value = mock_response
        
        # Test rendering via MermaidRenderer.render_raw (string IO)
        renderer = MermaidRenderer()
        code = "flowchart TD\n    A[Test]"
        
        result = renderer.render_raw(code, format="svg")
        self.assertEqual(result, '<svg>test diagram</svg>')
        
        # Verify the request was made
        mock_post.assert_called_once()
    
    @patch('mermaid_render.core.requests.post')
    def test_rendering_failure(self, mock_post):
        """Test rendering failure handling."""
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response
        
        # Test rendering failure
        renderer = MermaidRenderer()
        code = "flowchart TD\n    A[Test]"
        
        with self.assertRaises(RenderingError):
            renderer.render_raw(code, format="svg")
    
    def test_unsupported_format(self):
        """Test handling of unsupported formats."""
        renderer = MermaidRenderer()
        code = "flowchart TD\n    A[Test]"
        
        with self.assertRaises(UnsupportedFormatError):
            renderer.render_raw(code, format="gif")


class TestApplicationIntegration(unittest.TestCase):
    """Test integration patterns for applications using the library."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.output_dir = create_output_dir()
    
    def test_diagram_generation_service(self):
        """Test a service that generates diagrams from data."""
        
        class DiagramService:
            def __init__(self):
                self.renderer = MermaidRenderer()
            
            def create_process_flow(self, steps: List[Dict[str, Any]]) -> str:
                """Create a process flow diagram from step data (string-based)."""
                lines = ["flowchart TD"]
                
                # Add nodes
                existing = set()
                for step in steps:
                    node_id = step['id']
                    label = step['label']
                    shape = step.get('shape', 'rectangle')
                    if node_id in existing:
                        raise DiagramError(f"duplicate node id: {node_id}")
                    existing.add(node_id)
                    if shape == 'circle':
                        lines.append(f"    {node_id}(({label}))")
                    else:
                        lines.append(f"    {node_id}[{label}]")
                
                # Add connections
                for i in range(len(steps) - 1):
                    lines.append(f"    {steps[i]['id']} --> {steps[i + 1]['id']}")
                
                return "\n".join(lines)
            
            def validate_and_render(self, diagram_code: str, format: str = "svg") -> str:
                """Validate and render diagram code."""
                # Validate first
                result = validate_mermaid_syntax(diagram_code)
                if not result.is_valid:
                    raise ValidationError(f"Invalid diagram: {result.errors}")

                # Render
                content = self.renderer.render_raw(diagram_code, format=format)
                # Convert bytes to string if needed (for PNG/PDF formats)
                if isinstance(content, bytes):
                    return content.decode('utf-8')
                # Ensure we return a string
                return str(content)
        
        # Test the service
        service = DiagramService()
        
        # Test process flow creation
        steps = [
            {"id": "start", "label": "Start", "shape": "circle"},
            {"id": "process", "label": "Process Data"},
            {"id": "end", "label": "End", "shape": "circle"}
        ]
        
        diagram_code = service.create_process_flow(steps)
        self.assertIn("flowchart TD", diagram_code)
        self.assertIn("start((Start))", diagram_code)
        
        # Test validation and rendering (with mock)
        with patch.object(service.renderer, 'render_raw') as mock_render:
            mock_render.return_value = '<svg>test</svg>'
            
            result = service.validate_and_render(diagram_code)
            self.assertEqual(result, '<svg>test</svg>')
            mock_render.assert_called_once_with(diagram_code, format="svg")
    
    def test_batch_diagram_processor(self):
        """Test a batch processor for multiple diagrams."""
        
        class BatchProcessor:
            def __init__(self):
                self.renderer = MermaidRenderer()
                self.results = []
                self.errors = []
            
            def process_diagrams(self, diagrams: Dict[str, str]) -> Dict[str, Any]:
                """Process multiple diagrams and return results."""
                results = {}
                
                for name, code in diagrams.items():
                    try:
                        # Validate
                        validation = validate_mermaid_syntax(code)
                        if not validation.is_valid:
                            results[name] = {
                                "success": False,
                                "error": "Validation failed",
                                "details": validation.errors
                            }
                            continue
                        
                        # Render (mocked)
                        with patch.object(self.renderer, 'render_raw') as mock_render:
                            mock_render.return_value = f'<svg>{name}</svg>'
                            rendered = self.renderer.render_raw(code)
                        
                        results[name] = {
                            "success": True,
                            "content": rendered,
                            "size": len(rendered)
                        }
                        
                    except Exception as e:
                        results[name] = {
                            "success": False,
                            "error": str(e),
                            "details": None
                        }
                
                return results
        
        # Test the processor
        processor = BatchProcessor()
        
        diagrams = {
            "valid_flow": "flowchart TD\n    A[Start] --> B[End]",
            "valid_seq": "sequenceDiagram\n    A->>B: Message",
            "invalid": "invalid mermaid syntax"
        }
        
        results = processor.process_diagrams(diagrams)
        
        # Check results
        self.assertTrue(results["valid_flow"]["success"])
        self.assertTrue(results["valid_seq"]["success"])
        self.assertFalse(results["invalid"]["success"])
        self.assertIn("Validation failed", results["invalid"]["error"])


def validation_patterns_example(output_dir: Path):
    """Demonstrate validation patterns and error handling."""
    print("Validation patterns example...")
    
    test_cases: List[Dict[str, Any]] = [
        {
            "name": "Valid Flowchart",
            "code": """
flowchart TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Action 1]
    B -->|No| D[Action 2]
    C --> E[End]
    D --> E
            """,
            "expected_valid": True
        },
        {
            "name": "Valid Sequence",
            "code": """
sequenceDiagram
    participant A as Alice
    participant B as Bob
    A->>B: Hello Bob!
    B-->>A: Hi Alice!
            """,
            "expected_valid": True
        },
        {
            "name": "Invalid Syntax",
            "code": """
flowchart TD
    A[Start --> B[End
    B --> C[Missing bracket
            """,
            "expected_valid": False
        },
        {
            "name": "Empty Diagram",
            "code": "",
            "expected_valid": False
        }
    ]
    
    validation_results = []
    
    for test_case in test_cases:
        print(f"Testing: {test_case['name']}")
        
        result = validate_mermaid_syntax(test_case['code'])
        
        validation_results.append({
            "name": test_case['name'],
            "is_valid": result.is_valid,
            "expected_valid": test_case['expected_valid'],
            "errors": result.errors,
            "warnings": result.warnings if hasattr(result, 'warnings') else []
        })
        
        if result.is_valid == test_case['expected_valid']:
            print(f"  ✅ Validation result as expected: {result.is_valid}")
        else:
            print(f"  ❌ Unexpected validation result: {result.is_valid}")
        
        if not result.is_valid and result.errors:
            print(f"  Errors: {result.errors}")
    
    # Save validation results
    import json
    results_path = output_dir / "validation_results.json"
    with open(results_path, 'w') as f:
        json.dump(validation_results, f, indent=2)
    
    print(f"📁 Validation results saved to {results_path}")


def error_handling_patterns_example(output_dir: Path):
    """Demonstrate comprehensive error handling patterns."""
    print("Error handling patterns example...")
    
    def safe_diagram_render(diagram_code: str, format: str = "svg") -> Dict[str, Any]:
        """Safely render a diagram with comprehensive error handling."""
        try:
            # Step 1: Validate syntax
            validation = validate_mermaid_syntax(diagram_code)
            if not validation.is_valid:
                return {
                    "success": False,
                    "error_type": "validation",
                    "message": "Diagram syntax is invalid",
                    "details": validation.errors
                }
            
            # Step 2: Check format support
            from mermaid_render.utils import get_supported_formats
            if format not in get_supported_formats():
                return {
                    "success": False,
                    "error_type": "unsupported_format",
                    "message": f"Format '{format}' is not supported",
                    "details": f"Supported formats: {get_supported_formats()}"
                }
            
            # Step 3: Attempt rendering
            result = quick_render(diagram_code, format=format)
            
            return {
                "success": True,
                "content": result,
                "format": format,
                "size": len(result)
            }
            
        except ValidationError as e:
            return {
                "success": False,
                "error_type": "validation",
                "message": "Validation failed",
                "details": str(e)
            }
        
        except RenderingError as e:
            return {
                "success": False,
                "error_type": "rendering",
                "message": "Rendering failed",
                "details": str(e)
            }
        
        except UnsupportedFormatError as e:
            return {
                "success": False,
                "error_type": "unsupported_format",
                "message": "Unsupported format",
                "details": str(e)
            }
        
        except Exception as e:
            return {
                "success": False,
                "error_type": "unknown",
                "message": "Unexpected error occurred",
                "details": str(e)
            }
    
    # Test error handling with various scenarios
    test_scenarios = [
        {
            "name": "Valid diagram",
            "code": "flowchart TD\n    A[Start] --> B[End]",
            "format": "svg"
        },
        {
            "name": "Invalid syntax",
            "code": "flowchart TD\n    A[Start --> B[End",
            "format": "svg"
        },
        {
            "name": "Unsupported format",
            "code": "flowchart TD\n    A[Start] --> B[End]",
            "format": "gif"
        },
        {
            "name": "Empty code",
            "code": "",
            "format": "svg"
        }
    ]
    
    error_results = []
    
    for scenario in test_scenarios:
        print(f"Testing scenario: {scenario['name']}")
        
        result = safe_diagram_render(scenario['code'], scenario['format'])
        error_results.append({
            "scenario": scenario['name'],
            "result": result
        })
        
        if result['success']:
            print(f"  ✅ Success: Generated {result['format']} ({result['size']} bytes)")
        else:
            print(f"  ❌ Error ({result['error_type']}): {result['message']}")
    
    # Save error handling results
    import json
    error_path = output_dir / "error_handling_results.json"
    with open(error_path, 'w') as f:
        json.dump(error_results, f, indent=2)
    
    print(f"📁 Error handling results saved to {error_path}")


def main():
    """Run all testing and validation examples."""
    print("=== Mermaid Render Testing & Validation Showcase ===\n")
    
    # Create output directory
    output_dir = create_output_dir()
    print(f"Output directory: {output_dir.absolute()}\n")
    
    # Run unit tests
    print("Running unit tests...")
    test_suite = unittest.TestLoader().loadTestsFromModule(__import__(__name__))
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_result = test_runner.run(test_suite)
    
    print(f"\n📊 Test Results:")
    print(f"   Tests run: {test_result.testsRun}")
    print(f"   Failures: {len(test_result.failures)}")
    print(f"   Errors: {len(test_result.errors)}")
    print(f"   Success rate: {((test_result.testsRun - len(test_result.failures) - len(test_result.errors)) / test_result.testsRun * 100):.1f}%")
    
    print()
    
    # Run validation examples
    try:
        validation_patterns_example(output_dir)
        print()
        
        error_handling_patterns_example(output_dir)
        print()
        
        print("✅ All testing and validation examples completed successfully!")
        print(f"Check the {output_dir} directory for test results.")
        
    except Exception as e:
        print(f"❌ Error running validation examples: {e}")
        raise


if __name__ == "__main__":
    main()
