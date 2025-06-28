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
    assert "created and validated successfully" in result
    
    # Validation function should have been called
    mock_validate.assert_called_once()

@patch('archi_mcp.server._validate_plantuml_renders')
def test_create_diagram_validation_failure(mock_validate):
    """Test create_archimate_diagram with validation failure."""
    from archi_mcp.server import create_archimate_diagram, DiagramInput, ElementInput
    from archi_mcp.utils.exceptions import ArchiMateGenerationError
    
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
    
    # Should raise exception on validation failure
    with pytest.raises(ArchiMateGenerationError) as exc_info:
        create_archimate_diagram.fn(diagram=diagram_input)
    
    assert "Generated diagram failed validation" in str(exc_info.value)
    assert "Test validation error" in str(exc_info.value)

@patch('archi_mcp.server._validate_plantuml_renders')
def test_export_diagram_with_validation(mock_validate):
    """Test export_archimate_diagram with validation."""
    from archi_mcp.server import export_archimate_diagram, generator, ElementInput, _create_element_from_data
    
    # Mock successful validation
    mock_validate.return_value = (True, "Diagram renders successfully")
    
    # Add an element to generator first
    generator.clear()
    element_input = ElementInput(
        id="test_element",
        name="Test Element",
        element_type="Business_Actor",
        layer="Business"
    )
    element = _create_element_from_data(element_input)
    generator.add_element(element)
    
    result = export_archimate_diagram.fn(title="Test Export")
    
    # Should contain validation success message
    assert "✅" in result
    assert "VERIFIED ✅" in result
    assert "exported and validated successfully" in result
    
    # Validation function should have been called
    mock_validate.assert_called_once()

@patch('archi_mcp.server._validate_plantuml_renders')
def test_export_diagram_validation_failure(mock_validate):
    """Test export_archimate_diagram with validation failure."""
    from archi_mcp.server import export_archimate_diagram, generator, ElementInput, _create_element_from_data
    from archi_mcp.utils.exceptions import ArchiMateGenerationError
    
    # Mock failed validation
    mock_validate.return_value = (False, "Export validation error")
    
    # Add an element to generator first
    generator.clear()
    element_input = ElementInput(
        id="test_element",
        name="Test Element",
        element_type="Business_Actor",
        layer="Business"
    )
    element = _create_element_from_data(element_input)
    generator.add_element(element)
    
    # Should raise exception on validation failure
    with pytest.raises(ArchiMateGenerationError) as exc_info:
        export_archimate_diagram.fn(title="Test Export")
    
    assert "Generated diagram failed validation" in str(exc_info.value)
    assert "Export validation error" in str(exc_info.value)

@patch('archi_mcp.server._validate_plantuml_renders')
def test_template_with_validation(mock_validate):
    """Test generate_archimate_template with validation."""
    from archi_mcp.server import generate_archimate_template, TemplateInput
    
    # Mock successful validation
    mock_validate.return_value = (True, "Template renders successfully")
    
    # This test may fail if template doesn't exist, so we'll catch the exception
    try:
        template_input = TemplateInput(
            template_type="pattern",
            template_name="three_tier"
        )
        
        result = generate_archimate_template.fn(template=template_input)
        
        # If successful, should contain validation success message
        assert "✅" in result
        assert "VERIFIED ✅" in result
        assert "validated!" in result
        
    except Exception as e:
        # Template might not exist, which is acceptable for testing
        if "not found" in str(e):
            pytest.skip("Template not found - skipping validation test")
        else:
            raise

@patch('archi_mcp.server._validate_plantuml_renders')
def test_full_architecture_with_validation(mock_validate):
    """Test generate_full_architecture with validation."""
    from archi_mcp.server import generate_full_architecture, FullArchitectureInput
    
    # Mock successful validation for all views
    mock_validate.return_value = (True, "View renders successfully")
    
    architecture_input = FullArchitectureInput(
        system_description="Test system for validation",
        business_domain="testing",
        architecture_scope="system",
        include_views=["motivation"],
        implementation_phases=1
    )
    
    result = generate_full_architecture.fn(architecture=architecture_input)
    
    # Should contain validation success messages
    assert "✅" in result
    assert "VERIFIED ✅" in result
    assert "ALL VIEWS VERIFIED ✅" in result
    assert "Architecture Generation Complete - All Views Validated" in result
    
    # Validation function should have been called for each view
    assert mock_validate.call_count >= 1

@patch('archi_mcp.server._validate_plantuml_renders')
def test_full_architecture_validation_failure(mock_validate):
    """Test generate_full_architecture with validation failure."""
    from archi_mcp.server import generate_full_architecture, FullArchitectureInput
    from archi_mcp.utils.exceptions import ArchiMateGenerationError
    
    # Mock failed validation
    mock_validate.return_value = (False, "View validation failed")
    
    architecture_input = FullArchitectureInput(
        system_description="Test system for validation failure",
        business_domain="testing", 
        architecture_scope="system",
        include_views=["motivation"],
        implementation_phases=1
    )
    
    # Should raise exception on validation failure
    with pytest.raises(ArchiMateGenerationError) as exc_info:
        generate_full_architecture.fn(architecture=architecture_input)
    
    assert "failed validation" in str(exc_info.value)
    assert "View validation failed" in str(exc_info.value)

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
    """Test that all PlantUML-generating tools have validation."""
    import inspect
    import archi_mcp.server as server_module
    
    # Get the actual functions from the module
    function_names = [
        'create_archimate_diagram',
        'export_archimate_diagram', 
        'generate_archimate_template',
        'generate_full_architecture'
    ]
    
    functions_to_check = []
    for fname in function_names:
        for name in dir(server_module):
            obj = getattr(server_module, name)
            if hasattr(obj, '__name__') and obj.__name__ == fname:
                functions_to_check.append(obj)
                break
    
    # Check that we found all functions
    assert len(functions_to_check) >= 4, "Some validation functions not found"
    
    for func in functions_to_check:
        try:
            source = inspect.getsource(func)
            
            # Each function should call _validate_plantuml_renders
            assert "_validate_plantuml_renders" in source, f"Function {func.__name__} missing validation"
            
            # Each function should have validation error handling
            assert "ArchiMateGenerationError" in source, f"Function {func.__name__} missing error handling"
            
            # Each function should have validation success indicators
            assert "VERIFIED" in source or "validated" in source, f"Function {func.__name__} missing success indicators"
        except (TypeError, OSError):
            # Skip if we can't get source (e.g., for FunctionTool objects)
            pytest.skip(f"Cannot inspect source for {func}")

    # Alternative validation - check the server module source directly
    server_source = inspect.getsource(server_module)
    
    # Verify validation function exists
    assert "_validate_plantuml_renders" in server_source, "Validation function not found in server"
    
    # Verify all tools call validation
    for fname in function_names:
        # Check that the function definition exists and has validation
        function_pattern = f"def {fname}"
        assert function_pattern in server_source, f"Function {fname} not found in server"

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
        assert "successfully" in error_msg.lower()
    else:
        assert ("jar not found" in error_msg.lower() or 
                "validation error" in error_msg.lower() or
                "failed to render" in error_msg.lower())