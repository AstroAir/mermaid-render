# MCP Server Integration Testing Documentation

## Overview

This document describes the comprehensive testing framework for the MCP (Model Context Protocol) server implementation in mermaid-render. The testing suite validates the entire MCP server using FastMCP Client to create realistic client-server interactions.

## Test Files

### 1. `test_mcp_server_integration.py`
**Main comprehensive test suite** - Contains the complete testing framework with all test categories.

### 2. `test_mcp_mock_demo.py`
**Mock demonstration** - Shows the testing framework structure using mock objects (works without FastMCP installation).

### 3. `run_mcp_tests.py`
**Simple test runner** - Provides an easy way to run tests without requiring pytest.

## Testing Framework Features

### ✅ **Complete Tool Coverage**
Tests all 19 consolidated MCP tools:

**Core Rendering Tools (3)**
- `render_diagram` - Enhanced diagram rendering with quality assessment
- `validate_diagram` - Comprehensive diagram validation
- `list_themes` - Theme information and recommendations

**AI-Powered Tools (4)**
- `generate_diagram_from_text` - AI diagram generation
- `optimize_diagram` - AI-powered optimization
- `analyze_diagram` - Quality assessment and metrics
- `get_diagram_suggestions` - AI improvement suggestions

**Configuration Management (2)**
- `get_configuration` - Retrieve settings with filtering
- `update_configuration` - Update settings with validation

**Template Management (5)**
- `list_available_templates` - List templates with filtering
- `get_template_details` - Detailed template information
- `create_custom_template` - Create new templates
- `create_from_template` - Generate diagrams from templates
- `list_diagram_types` - Comprehensive diagram type information

**Information & Operations (5)**
- `get_diagram_examples` - Examples and best practices
- `get_system_information` - System capabilities and features
- `save_diagram_to_file` - File operations with validation
- `batch_render_diagrams` - Parallel processing
- `manage_cache_operations` - Cache management

### ✅ **Comprehensive Test Categories**

1. **Server Connectivity**
   - Basic ping/connectivity tests
   - Connection lifecycle management
   - Server startup/shutdown validation

2. **Tool Discovery & Registration**
   - Validates all 19 tools are properly registered
   - Checks tool metadata and descriptions
   - Verifies MCP protocol compliance

3. **Resource Discovery & Access**
   - Tests resource exposure (themes, templates, docs)
   - Validates resource URIs and content types
   - Checks resource accessibility through MCP

4. **Parameter Validation**
   - Tests input validation for all tools
   - Validates enum constraints and field requirements
   - Checks error responses for invalid parameters

5. **Error Handling**
   - Tests malformed requests and invalid data
   - Validates structured error responses
   - Checks error categorization and suggestions

6. **Integration Testing**
   - Real client-server interactions through MCP protocol
   - Concurrent client connection testing
   - End-to-end workflow validation

### ✅ **Advanced Testing Features**

- **In-Memory Transport**: Uses FastMCP's in-memory transport for efficient testing
- **Async Context Management**: Proper connection lifecycle handling
- **Concurrent Testing**: Multiple client connections simultaneously
- **Mock Framework**: Comprehensive mock implementation for development
- **Structured Reporting**: Detailed test results with success rates
- **Pytest Integration**: Compatible with pytest for CI/CD pipelines

## Usage

### Quick Test (Basic Validation)
```bash
# Using the test runner
python run_mcp_tests.py quick

# Using pytest
pytest test_mcp_server_integration.py::test_mcp_server_connectivity -v
```

### Full Test Suite (Comprehensive)
```bash
# Using the test runner
python run_mcp_tests.py

# Using pytest
pytest test_mcp_server_integration.py -v
```

### Mock Demo (No Dependencies)
```bash
# Demonstrates framework without requiring FastMCP
python test_mcp_mock_demo.py
```

### Individual Test Categories
```bash
# Test specific functionality
pytest test_mcp_server_integration.py::test_mcp_core_tools -v
pytest test_mcp_server_integration.py::test_mcp_parameter_validation -v
pytest test_mcp_server_integration.py::test_mcp_error_handling -v
```

## Test Results Interpretation

### Success Criteria
- **Connectivity**: 100% success required
- **Tool Discovery**: 100% success required (all 19 tools found)
- **Core Tools**: 80% success required (rendering functionality)
- **AI Tools**: 50% success required (may lack API keys)
- **Configuration**: 80% success required
- **Templates**: 70% success required
- **Parameter Validation**: 80% success required
- **Error Handling**: 70% success required
- **Resources**: 50% success required (some may not be implemented)
- **Concurrent Connections**: 80% success required

### Expected Outputs

**✅ Successful Test Run:**
```
🎉 ALL TESTS PASSED - MCP Server is production ready!
Overall Success Rate: 10/10 (100%)
```

**⚠️ Partial Success:**
```
⚠️ Some tests failed - Review results above
Overall Success Rate: 8/10 (80%)
```

**❌ Major Issues:**
```
❌ Critical failures detected
Overall Success Rate: 4/10 (40%)
```

## Integration with CI/CD

### GitHub Actions Example
```yaml
- name: Run MCP Integration Tests
  run: |
    pip install fastmcp pytest
    pytest test_mcp_server_integration.py -v --tb=short
```

### Local Development
```bash
# Install dependencies
pip install fastmcp pytest

# Run tests during development
python run_mcp_tests.py quick

# Full validation before commit
python run_mcp_tests.py
```

## Troubleshooting

### Common Issues

1. **FastMCP Not Available**
   - Install: `pip install fastmcp`
   - Use mock demo: `python test_mcp_mock_demo.py`

2. **AI Tools Failing**
   - Expected if no API keys configured
   - Tests use 50% success threshold for AI tools

3. **Resource Tests Failing**
   - Some resources may not be fully implemented
   - Tests use 50% success threshold for resources

4. **Timeout Issues**
   - Increase timeout in test configuration
   - Check system performance and load

### Debug Mode
```bash
# Enable verbose logging
python run_mcp_tests.py --verbose

# Run with pytest debug
pytest test_mcp_server_integration.py -v -s --tb=long
```

## Framework Architecture

### Class Structure
```python
MCPServerTestSuite
├── setup_server_and_client()
├── test_server_connectivity()
├── test_tool_discovery()
├── test_core_rendering_tools()
├── test_ai_powered_tools()
├── test_configuration_tools()
├── test_template_tools()
├── test_information_tools()
├── test_parameter_validation()
├── test_error_handling()
├── test_resource_access()
├── test_concurrent_connections()
└── run_comprehensive_test_suite()
```

### Mock Framework
```python
MockMCPClient
├── Simulates real FastMCP Client behavior
├── Provides realistic responses for all tools
├── Supports error simulation and edge cases
└── Enables testing without external dependencies
```

## Validation Results

The testing framework has been validated to ensure:

✅ **All 19 tools are properly tested**  
✅ **Parameter validation works correctly**  
✅ **Error handling is comprehensive**  
✅ **Resource exposure is validated**  
✅ **Concurrent connections are supported**  
✅ **Integration testing is thorough**  
✅ **Mock framework demonstrates all features**  

## Conclusion

This comprehensive testing framework ensures the MCP server implementation is production-ready by validating all functionality through realistic client-server interactions. The framework provides both real testing with FastMCP and mock testing for development environments, making it suitable for all stages of development and deployment.
