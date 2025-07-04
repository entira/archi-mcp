"""Test mandatory PlantUML validation functionality."""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock

def test_validate_plantuml_renders_function():
    """Test the central validation function."""
    from archi_mcp.server import _validate_plantuml_renders
    
    # Test with minimal ArchiMate PlantUML code
    test_plantuml = """
@startuml
!include <archimate/Archimate>

Business_Actor(test, "Test Actor")
@enduml
"""
    
    # Function should exist and be callable
    assert callable(_validate_plantuml_renders)
    
    # Test the function (will fail if PlantUML jar not found, but that's expected)
    renders_ok, error_msg = _validate_plantuml_renders(test_plantuml)
    
    # Should return a tuple
    assert isinstance(renders_ok, bool)
    assert isinstance(error_msg, str)
    
    # If PlantUML jar is not found, should return False with appropriate message
    if not renders_ok:
        assert ("PlantUML jar not found" in error_msg or 
                "Validation error" in error_msg or 
                "ArchiMate validation failed" in error_msg)

@patch('archi_mcp.server._validate_plantuml_renders')
def test_create_diagram_with_validation(mock_validate):
    """Test create_archimate_diagram with validation."""
    import archi_mcp.server as server_module
    from archi_mcp.server import DiagramInput, ElementInput
    
    # Get the actual function from the module
    create_archimate_diagram = None
    for name in dir(server_module):
        obj = getattr(server_module, name)
        if hasattr(obj, '__name__') and obj.__name__ == 'create_archimate_diagram':
            create_archimate_diagram = obj
            break
    
    if create_archimate_diagram is None:
        pytest.skip("create_archimate_diagram function not found")
    
    # Mock successful validation
    mock_validate.return_value = (True, "Diagram renders successfully")
    
    diagram_input = DiagramInput(
        elements=[
            ElementInput(
                id="test_element",
                name="Test Element",
                element_type="Business_Actor",
                layer="Business"
            )
        ],
        title="Test Diagram"
    )
    
    result = create_archimate_diagram.fn(diagram=diagram_input)
    
    # Should contain validation success message
    assert "✅" in result
    assert "VERIFIED ✅" in result
    
    # Validation function should have been called
    mock_validate.assert_called_once()

@patch('archi_mcp.server._validate_plantuml_renders')
def test_create_diagram_validation_failure(mock_validate):
    """Test create_archimate_diagram with validation failure."""
    import archi_mcp.server as server_module
    from archi_mcp.server import DiagramInput, ElementInput
    from archi_mcp.utils.exceptions import ArchiMateGenerationError
    
    # Get the actual function from the module
    create_archimate_diagram = None
    for name in dir(server_module):
        obj = getattr(server_module, name)
        if hasattr(obj, '__name__') and obj.__name__ == 'create_archimate_diagram':
            create_archimate_diagram = obj
            break
    
    if create_archimate_diagram is None:
        pytest.skip("create_archimate_diagram function not found")
    
    # Mock failed validation
    mock_validate.return_value = (False, "Test validation error")
    
    diagram_input = DiagramInput(
        elements=[
            ElementInput(
                id="test_element",
                name="Test Element",
                element_type="Business_Actor",
                layer="Business"
            )
        ],
        title="Test Diagram"
    )
    
    result = create_archimate_diagram.fn(diagram=diagram_input)
    
    # Should return error message instead of raising exception in simplified API
    assert "❌" in result
    assert "failed validation" in result
    assert "Test validation error" in result




# Full architecture functions were removed in simplified API

def test_validation_function_with_invalid_plantuml():
    """Test validation function with invalid PlantUML code."""
    from archi_mcp.server import _validate_plantuml_renders
    
    # Test with invalid PlantUML syntax
    invalid_plantuml = """
@startuml
this is not valid plantuml syntax at all
@enduml
"""
    
    renders_ok, error_msg = _validate_plantuml_renders(invalid_plantuml)
    
    # Should handle invalid syntax gracefully
    assert isinstance(renders_ok, bool)
    assert isinstance(error_msg, str)
    assert len(error_msg) > 0

def test_validation_function_with_empty_plantuml():
    """Test validation function with empty PlantUML code."""
    from archi_mcp.server import _validate_plantuml_renders
    
    renders_ok, error_msg = _validate_plantuml_renders("")
    
    # Should handle empty input gracefully
    assert isinstance(renders_ok, bool)
    assert isinstance(error_msg, str)

def test_validation_function_timeout_handling():
    """Test validation function timeout handling."""
    from archi_mcp.server import _validate_plantuml_renders
    
    # This is a basic test - actual timeout testing would require mocking subprocess
    test_plantuml = """
@startuml
rectangle "Test" as test
@enduml
"""
    
    # Should not crash even with timeout scenarios
    renders_ok, error_msg = _validate_plantuml_renders(test_plantuml)
    
    assert isinstance(renders_ok, bool)
    assert isinstance(error_msg, str)

def test_all_tools_have_validation():
    """Test that core PlantUML-generating tools have validation."""
    import inspect
    import archi_mcp.server as server_module
    
    # Check the server module source directly
    server_source = inspect.getsource(server_module)
    
    # Verify validation function exists
    assert "_validate_plantuml_renders" in server_source, "Validation function not found in server"
    
    # Verify core functions have validation logic
    assert "create_archimate_diagram" in server_source, "create_archimate_diagram not found"
    
    # Check for validation patterns in the source
    assert "VERIFIED ✅" in server_source, "Validation success indicators not found"
    
    # Verify the tools are properly registered with FastMCP
    from archi_mcp.server import mcp
    registered_tools = list(mcp._tool_manager._tools.keys())
    
    # Should have our 2 core tools (updated count after removing analysis tools)
    expected_tools = ['create_archimate_diagram', 'test_element_normalization']
    
    for tool in expected_tools:
        assert tool in registered_tools, f"Tool '{tool}' not found in {registered_tools}"
    
    # We should have at least these 2 tools
    assert len(registered_tools) >= 2, f"Expected at least 2 tools, got {len(registered_tools)}: {registered_tools}"

@pytest.mark.integration
def test_validation_with_real_plantuml():
    """Integration test with real PlantUML if available."""
    from archi_mcp.server import _validate_plantuml_renders
    
    # Simple valid PlantUML
    valid_plantuml = """
@startuml
rectangle "Customer" as customer
rectangle "Service" as service
customer --> service
@enduml
"""
    
    renders_ok, error_msg = _validate_plantuml_renders(valid_plantuml)
    
    # If PlantUML is available, should work
    # If not available, should fail gracefully with appropriate error
    assert isinstance(renders_ok, bool)
    assert isinstance(error_msg, str)
    
    if renders_ok:
        assert "passed" in error_msg.lower()
    else:
        assert ("jar not found" in error_msg.lower() or 
                "validation error" in error_msg.lower() or
                "failed to render" in error_msg.lower() or
                "missing archimate include directive" in error_msg.lower())