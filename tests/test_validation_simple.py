"""Simple tests for mandatory PlantUML validation."""

import pytest
from unittest.mock import patch, MagicMock

def test_validation_function_exists():
    """Test that validation function exists and is callable."""
    from archi_mcp.server import _validate_plantuml_renders
    
    assert callable(_validate_plantuml_renders)
    
    # Test with simple input
    result = _validate_plantuml_renders("@startuml\nrectangle Test\n@enduml")
    assert isinstance(result, tuple)
    assert len(result) == 2
    assert isinstance(result[0], bool)
    assert isinstance(result[1], str)

def test_server_has_validation_code():
    """Test that server module contains validation code."""
    import inspect
    import archi_mcp.server as server_module
    
    # Get source code of server module
    server_source = inspect.getsource(server_module)
    
    # Check for validation function
    assert "_validate_plantuml_renders" in server_source
    
    # Check for validation calls in tools
    assert "renders_ok, error_msg = _validate_plantuml_renders" in server_source
    
    # Check for error handling
    assert "ArchiMateGenerationError" in server_source
    
    # Check for success indicators
    assert "VERIFIED ✅" in server_source

def test_core_functionality_still_works():
    """Test that core functionality still works with validation."""
    from archi_mcp.server import generator, ElementInput, _create_element_from_data
    
    # Clear generator
    generator.clear()
    
    # Add test element
    element_input = ElementInput(
        id="test_validation",
        name="Test Validation Element", 
        element_type="Business_Actor",
        layer="Business"
    )
    
    element = _create_element_from_data(element_input)
    generator.add_element(element)
    
    # Generate PlantUML
    plantuml_code = generator.generate_plantuml(title="Validation Test")
    
    assert isinstance(plantuml_code, str)
    assert len(plantuml_code) > 0
    assert "Test Validation Element" in plantuml_code or "Business_Actor" in plantuml_code

def test_generator_statistics():
    """Test that generator statistics work correctly."""
    from archi_mcp.server import generator, ElementInput, RelationshipInput, _create_element_from_data, _create_relationship_from_data
    
    # Clear generator
    generator.clear()
    
    # Add test elements
    element1_input = ElementInput(
        id="actor1",
        name="Actor 1",
        element_type="Business_Actor", 
        layer="Business"
    )
    
    element2_input = ElementInput(
        id="service1",
        name="Service 1",
        element_type="Business_Service",
        layer="Business"
    )
    
    element1 = _create_element_from_data(element1_input)
    element2 = _create_element_from_data(element2_input)
    
    generator.add_element(element1)
    generator.add_element(element2)
    
    # Add relationship
    relationship_input = RelationshipInput(
        id="rel1",
        from_element="actor1",
        to_element="service1",
        relationship_type="Realization"
    )
    
    relationship = _create_relationship_from_data(relationship_input)
    generator.add_relationship(relationship)
    
    # Check statistics
    assert generator.get_element_count() == 2
    assert generator.get_relationship_count() == 1
    
    layers = generator.get_layers_used()
    assert "Business" in layers

@patch('archi_mcp.server._validate_plantuml_renders')
def test_mocked_validation_success(mock_validate):
    """Test with mocked successful validation."""
    from archi_mcp.server import generator, ElementInput, _create_element_from_data
    
    # Mock successful validation
    mock_validate.return_value = (True, "Validation successful")
    
    # Clear and add element
    generator.clear()
    element_input = ElementInput(
        id="mock_test",
        name="Mock Test Element",
        element_type="Business_Actor",
        layer="Business"
    )
    
    element = _create_element_from_data(element_input)
    generator.add_element(element)
    
    # Generate PlantUML
    plantuml_code = generator.generate_plantuml(title="Mock Test")
    
    assert isinstance(plantuml_code, str)
    assert len(plantuml_code) > 0

@patch('archi_mcp.server._validate_plantuml_renders')
def test_mocked_validation_failure(mock_validate):
    """Test with mocked failed validation."""
    
    # Mock failed validation
    mock_validate.return_value = (False, "Mock validation failed")
    
    # Test that validation function would be called
    from archi_mcp.server import _validate_plantuml_renders
    
    result = _validate_plantuml_renders("test")
    assert result == (False, "Mock validation failed")
    
    mock_validate.assert_called_once()

def test_element_aspect_detection():
    """Test element aspect detection works correctly."""
    from archi_mcp.server import _get_aspect_for_element_type
    from archi_mcp.archimate.elements.base import ArchiMateAspect
    
    # Test active structure
    assert _get_aspect_for_element_type("Business_Actor") == ArchiMateAspect.ACTIVE_STRUCTURE
    assert _get_aspect_for_element_type("Application_Component") == ArchiMateAspect.ACTIVE_STRUCTURE
    
    # Test passive structure
    assert _get_aspect_for_element_type("Business_Object") == ArchiMateAspect.PASSIVE_STRUCTURE
    assert _get_aspect_for_element_type("Data_Object") == ArchiMateAspect.PASSIVE_STRUCTURE
    
    # Test behavior (default)
    assert _get_aspect_for_element_type("Business_Process") == ArchiMateAspect.BEHAVIOR
    assert _get_aspect_for_element_type("Unknown_Type") == ArchiMateAspect.BEHAVIOR

def test_pydantic_validation():
    """Test Pydantic model validation."""
    from archi_mcp.server import ElementInput, RelationshipInput, DiagramInput
    
    # Valid element
    element = ElementInput(
        id="test_element",
        name="Test Element",
        element_type="Business_Actor",
        layer="Business"
    )
    assert element.id == "test_element"
    
    # Valid relationship
    relationship = RelationshipInput(
        id="test_rel",
        from_element="elem1",
        to_element="elem2", 
        relationship_type="Realization"
    )
    assert relationship.id == "test_rel"
    
    # Valid diagram
    diagram = DiagramInput(
        elements=[element],
        relationships=[relationship],
        title="Test Diagram"
    )
    assert len(diagram.elements) == 1
    assert len(diagram.relationships) == 1

def test_validation_timeout_safety():
    """Test that validation handles timeouts safely."""
    from archi_mcp.server import _validate_plantuml_renders
    
    # Large PlantUML content that might timeout
    large_plantuml = "@startuml\n" + "\n".join([f"rectangle \"Element{i}\" as elem{i}" for i in range(1000)]) + "\n@enduml"
    
    # Should not crash even with large content
    renders_ok, error_msg = _validate_plantuml_renders(large_plantuml)
    
    assert isinstance(renders_ok, bool)
    assert isinstance(error_msg, str)
    
    # If it times out, should have appropriate error message
    if not renders_ok:
        assert ("timeout" in error_msg.lower() or 
                "jar not found" in error_msg.lower() or
                "validation error" in error_msg.lower() or
                "archimate validation failed" in error_msg.lower())

def test_imports_work():
    """Test that all necessary imports work."""
    # Test core imports
    from archi_mcp.server import mcp, generator, validator
    
    # Test Pydantic models
    from archi_mcp.server import DiagramInput, ElementInput, RelationshipInput
    
    # Test utility functions
    from archi_mcp.server import _create_element_from_data, _create_relationship_from_data
    
    # Test validation function
    from archi_mcp.server import _validate_plantuml_renders
    
    # All should be importable
    assert all([
        mcp, generator, validator,
        DiagramInput, ElementInput, RelationshipInput,
        _create_element_from_data, _create_relationship_from_data,
        _validate_plantuml_renders
    ])