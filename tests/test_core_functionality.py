"""Test core ArchiMate MCP functionality without FastMCP dependencies."""

import pytest
from typing import List

def test_element_creation():
    """Test ArchiMate element creation."""
    from archi_mcp.server import ElementInput, _create_element_from_data
    from archi_mcp.archimate.elements.base import ArchiMateLayer, ArchiMateAspect
    
    element_input = ElementInput(
        id="test_element",
        name="Test Element",
        element_type="Business_Actor",
        layer="Business",
        description="Test element"
    )
    
    element = _create_element_from_data(element_input)
    
    assert element.id == "test_element"
    assert element.name == "Test Element"
    assert element.element_type == "Business_Actor"
    assert element.layer == ArchiMateLayer.BUSINESS
    assert element.aspect == ArchiMateAspect.ACTIVE_STRUCTURE

def test_relationship_creation():
    """Test ArchiMate relationship creation."""
    from archi_mcp.server import RelationshipInput, _create_relationship_from_data
    
    relationship_input = RelationshipInput(
        id="test_rel",
        from_element="elem1",
        to_element="elem2",
        relationship_type="Realization",
        description="Test relationship"
    )
    
    relationship = _create_relationship_from_data(relationship_input)
    
    assert relationship.id == "test_rel"
    assert relationship.from_element == "elem1"
    assert relationship.to_element == "elem2"
    assert relationship.description == "Test relationship"

def test_aspect_detection():
    """Test aspect detection for different element types."""
    from archi_mcp.server import _get_aspect_for_element_type
    from archi_mcp.archimate.elements.base import ArchiMateAspect
    
    # Test active structure
    assert _get_aspect_for_element_type("Business_Actor") == ArchiMateAspect.ACTIVE_STRUCTURE
    assert _get_aspect_for_element_type("Application_Component") == ArchiMateAspect.ACTIVE_STRUCTURE
    assert _get_aspect_for_element_type("Node") == ArchiMateAspect.ACTIVE_STRUCTURE
    
    # Test passive structure
    assert _get_aspect_for_element_type("Business_Object") == ArchiMateAspect.PASSIVE_STRUCTURE
    assert _get_aspect_for_element_type("Data_Object") == ArchiMateAspect.PASSIVE_STRUCTURE
    assert _get_aspect_for_element_type("Artifact") == ArchiMateAspect.PASSIVE_STRUCTURE
    
    # Test behavior
    assert _get_aspect_for_element_type("Business_Process") == ArchiMateAspect.BEHAVIOR
    assert _get_aspect_for_element_type("Application_Service") == ArchiMateAspect.BEHAVIOR
    assert _get_aspect_for_element_type("Unknown_Element") == ArchiMateAspect.BEHAVIOR

def test_generator_functionality():
    """Test ArchiMate generator core functionality."""
    from archi_mcp.server import generator, ElementInput, _create_element_from_data
    
    # Clear generator
    generator.clear()
    
    # Add test element
    element_input = ElementInput(
        id="test_generator",
        name="Test Generator Element",
        element_type="Business_Actor",
        layer="Business"
    )
    
    element = _create_element_from_data(element_input)
    generator.add_element(element)
    
    # Check statistics
    assert generator.get_element_count() >= 1
    
    # Generate PlantUML
    plantuml_code = generator.generate_plantuml(title="Test")
    
    assert isinstance(plantuml_code, str)
    assert len(plantuml_code) > 0
    assert "Test Generator Element" in plantuml_code or "Business_Actor" in plantuml_code

def test_validator_functionality():
    """Test ArchiMate validator core functionality.""" 
    from archi_mcp.server import validator
    
    # Test with empty dictionaries (validator expects dict, not list)
    errors = validator.validate_model({}, [])
    
    # Should not crash
    assert isinstance(errors, list)

def test_full_architecture_generator_import():
    """Test that full architecture generator can be imported."""
    from archi_mcp.server import full_arch_generator, FullArchitectureInput
    
    assert full_arch_generator is not None
    
    # Test input model creation
    architecture_input = FullArchitectureInput(
        system_description="Test system",
        business_domain="testing",
        architecture_scope="system",
        include_views=["motivation"],
        implementation_phases=1
    )
    
    assert architecture_input.system_description == "Test system"
    assert architecture_input.business_domain == "testing"
    assert architecture_input.include_views == ["motivation"]

def test_pydantic_models():
    """Test Pydantic model validation."""
    from archi_mcp.server import DiagramInput, ElementInput, RelationshipInput
    
    # Test valid element
    element = ElementInput(
        id="test_id",
        name="Test Element",
        element_type="Business_Actor",
        layer="Business"
    )
    assert element.id == "test_id"
    
    # Test valid relationship
    relationship = RelationshipInput(
        id="rel_id",
        from_element="elem1",
        to_element="elem2",
        relationship_type="Realization"
    )
    assert relationship.id == "rel_id"
    
    # Test valid diagram
    diagram = DiagramInput(
        elements=[element],
        relationships=[relationship],
        title="Test Diagram"
    )
    assert len(diagram.elements) == 1
    assert len(diagram.relationships) == 1

def test_invalid_layer_handling():
    """Test handling of invalid layers."""
    from archi_mcp.server import ElementInput, _create_element_from_data
    from archi_mcp.utils.exceptions import ArchiMateValidationError
    
    element_input = ElementInput(
        id="test_element",
        name="Test Element",
        element_type="Business_Actor",
        layer="InvalidLayer"
    )
    
    with pytest.raises(ArchiMateValidationError):
        _create_element_from_data(element_input)

def test_archimate_layers():
    """Test ArchiMate layer enumeration."""
    from archi_mcp.archimate.elements.base import ArchiMateLayer
    
    # Test valid layers
    valid_layers = ["Business", "Application", "Technology", "Physical", "Motivation", "Strategy", "Implementation"]
    
    for layer_name in valid_layers:
        layer = ArchiMateLayer(layer_name)
        assert layer.value == layer_name
    
    # Test invalid layer
    with pytest.raises(ValueError):
        ArchiMateLayer("InvalidLayer")

def test_relationship_types():
    """Test ArchiMate relationship types."""
    from archi_mcp.archimate.relationships import RelationshipType
    
    # Test valid relationship types
    valid_types = ["Access", "Aggregation", "Assignment", "Association", "Composition", "Flow", "Influence", "Realization", "Serving", "Specialization", "Triggering"]
    
    for rel_type in valid_types:
        relationship_type = RelationshipType(rel_type)
        assert relationship_type.value == rel_type
    
    # Test invalid relationship type
    with pytest.raises(ValueError):
        RelationshipType("InvalidRelationship")

def test_complex_diagram_creation():
    """Test creating complex diagram with multiple elements."""
    from archi_mcp.server import (
        generator, ElementInput, RelationshipInput, 
        _create_element_from_data, _create_relationship_from_data
    )
    
    # Clear generator
    generator.clear()
    
    # Create multiple elements
    elements_data = [
        {"id": "customer", "name": "Customer", "element_type": "Business_Actor", "layer": "Business"},
        {"id": "service", "name": "Banking Service", "element_type": "Business_Service", "layer": "Business"},
        {"id": "app", "name": "Banking App", "element_type": "Application_Component", "layer": "Application"}
    ]
    
    for elem_data in elements_data:
        element_input = ElementInput(**elem_data)
        element = _create_element_from_data(element_input)
        generator.add_element(element)
    
    # Create relationships (use valid ArchiMate relationships)
    relationships_data = [
        {"id": "rel1", "from_element": "customer", "to_element": "service", "relationship_type": "Serving"},
        {"id": "rel2", "from_element": "app", "to_element": "service", "relationship_type": "Realization"}
    ]
    
    for rel_data in relationships_data:
        relationship_input = RelationshipInput(**rel_data)
        relationship = _create_relationship_from_data(relationship_input)
        generator.add_relationship(relationship)
    
    # Generate diagram
    plantuml_code = generator.generate_plantuml(title="Complex Diagram")
    
    # Validate result
    assert isinstance(plantuml_code, str)
    assert len(plantuml_code) > 0
    assert generator.get_element_count() == 3
    assert generator.get_relationship_count() == 2
    
    # Check that elements and relationships are in the output
    assert "Customer" in plantuml_code or "Business_Actor" in plantuml_code
    assert "Banking Service" in plantuml_code or "Business_Service" in plantuml_code

def test_server_module_imports():
    """Test that all necessary server modules can be imported."""
    # Test core imports
    from archi_mcp.server import (
        mcp, main, generator, validator, full_arch_generator
    )
    
    # Test Pydantic models
    from archi_mcp.server import (
        DiagramInput, ElementInput, RelationshipInput,
        TemplateInput, FullArchitectureInput, LayoutInput
    )
    
    # Test utility functions
    from archi_mcp.server import (
        _create_element_from_data, _create_relationship_from_data,
        _get_aspect_for_element_type
    )
    
    # All imports should succeed
    assert all([
        mcp, main, generator, validator, full_arch_generator,
        DiagramInput, ElementInput, RelationshipInput,
        TemplateInput, FullArchitectureInput, LayoutInput,
        _create_element_from_data, _create_relationship_from_data,
        _get_aspect_for_element_type
    ])

def test_performance_basic():
    """Basic performance test for core operations."""
    import time
    from archi_mcp.server import generator, ElementInput, _create_element_from_data
    
    # Clear generator
    generator.clear()
    
    # Time element creation and addition
    start_time = time.time()
    
    for i in range(10):
        element_input = ElementInput(
            id=f"perf_element_{i}",
            name=f"Performance Element {i}",
            element_type="Business_Actor",
            layer="Business"
        )
        element = _create_element_from_data(element_input)
        generator.add_element(element)
    
    plantuml_code = generator.generate_plantuml(title="Performance Test")
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Should complete within reasonable time
    assert execution_time < 5.0, f"Core operations too slow: {execution_time} seconds"
    assert isinstance(plantuml_code, str)
    assert generator.get_element_count() >= 10