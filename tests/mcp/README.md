# MCP Server Tests

This directory contains comprehensive tests for the MCP (Model Context Protocol) server implementation in mermaid-render.

## Test Files

### Core Test Files

- **`test_mcp_server_integration.py`** - Main comprehensive integration test suite
  - Tests all 19 MCP tools through FastMCP Client
  - Validates server connectivity, tool discovery, parameter validation
  - Tests error handling, resource access, concurrent connections
  - Requires FastMCP installation

- **`test_mcp_mock_demo.py`** - Mock demonstration of testing framework
  - Demonstrates testing framework structure using mock objects
  - Works without FastMCP installation
  - Validates framework design and functionality

- **`run_mcp_tests.py`** - Simple test runner
  - Easy execution without requiring pytest
  - Supports both quick and comprehensive test modes
  - Provides clear output and error reporting

## Usage

### Quick Test (Basic Validation)
```bash
cd tests/mcp
python run_mcp_tests.py quick
```

### Full Test Suite (Comprehensive)
```bash
cd tests/mcp
python run_mcp_tests.py
```

### Mock Demo (No Dependencies)
```bash
cd tests/mcp
python test_mcp_mock_demo.py
```

### Pytest Integration
```bash
# From project root
pytest tests/mcp/test_mcp_server_integration.py -v

# Individual test categories
pytest tests/mcp/test_mcp_server_integration.py::test_mcp_server_connectivity -v
pytest tests/mcp/test_mcp_server_integration.py::test_mcp_core_tools -v
```

## Test Coverage

### Tools Tested (19 total)
- **Core Rendering**: render_diagram, validate_diagram, list_themes
- **AI-Powered**: generate_diagram_from_text, optimize_diagram, analyze_diagram, get_diagram_suggestions
- **Configuration**: get_configuration, update_configuration
- **Templates**: list_available_templates, get_template_details, create_custom_template, create_from_template, list_diagram_types
- **Information**: get_diagram_examples, get_system_information, save_diagram_to_file, batch_render_diagrams, manage_cache_operations

### Test Categories
- Server connectivity and lifecycle
- Tool discovery and registration
- Resource discovery and access
- Parameter validation and error handling
- Integration testing through MCP protocol
- Concurrent client connections

## Requirements

### For Full Integration Tests
- FastMCP: `pip install fastmcp`
- pytest: `pip install pytest`

### For Mock Demo
- No additional dependencies required

## Documentation

For detailed documentation, see:
- `docs/testing/MCP_TESTING_DOCUMENTATION.md` - Complete testing framework documentation
- `docs/testing/MCP_TESTING_SUMMARY.md` - Implementation summary and achievements

## Success Criteria

- **Connectivity**: 100% success required
- **Tool Discovery**: 100% success required (all 19 tools found)
- **Core Tools**: 80% success required
- **Parameter Validation**: 80% success required
- **Error Handling**: 70% success required
- **Overall**: 80% success rate for production readiness

## Troubleshooting

### Common Issues
1. **FastMCP Not Available**: Use mock demo or install FastMCP
2. **AI Tools Failing**: Expected if no API keys configured (50% threshold)
3. **Resource Tests Failing**: Some resources may not be implemented (50% threshold)

### Debug Mode
```bash
python run_mcp_tests.py --verbose
pytest tests/mcp/test_mcp_server_integration.py -v -s --tb=long
```
