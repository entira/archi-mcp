"""Test PlantUML generation and validation with FastMCP compatibility."""

import pytest
import re
from typing import List

def test_plantuml_generation_core():
    """Test core PlantUML generation functionality."""
    from archi_mcp.server import generator, ElementInput, _create_element_from_data
    
    # Clear generator
    generator.clear()
    
    # Create test element
    element_input = ElementInput(
        id="test_actor",
        name="Test Actor",
        element_type="Business_Actor",
        layer="Business"
    )
    
    element = _create_element_from_data(element_input)
    generator.add_element(element)
    
    # Generate PlantUML
    plantuml_code = generator.generate_plantuml(title="Test Diagram")
    
    # Validate basic PlantUML syntax
    assert isinstance(plantuml_code, str)
    assert len(plantuml_code) > 0
    assert "@startuml" in plantuml_code
    assert "@enduml" in plantuml_code
    assert "Test Actor" in plantuml_code or "Business_Actor" in plantuml_code

def test_archimate_syntax_compliance():
    """Test ArchiMate PlantUML syntax compliance."""
    from archi_mcp.server import generator, ElementInput, _create_element_from_data
    
    # Clear generator
    generator.clear()
    
    # Test different element types
    test_cases = [
        ("Business_Actor", "Business", "actor1", "Business Actor"),
        ("Application_Component", "Application", "app1", "App Component"),
        ("Node", "Technology", "node1", "Server Node")
    ]
    
    for element_type, layer, element_id, element_name in test_cases:
        # Clear for each test
        generator.clear()
        
        element_input = ElementInput(
            id=element_id,
            name=element_name,
            element_type=element_type,
            layer=layer
        )
        
        element = _create_element_from_data(element_input)
        generator.add_element(element)
        
        plantuml_code = generator.generate_plantuml()
        
        # Validate ArchiMate syntax
        assert "@startuml" in plantuml_code
        assert "@enduml" in plantuml_code
        assert element_name in plantuml_code or element_type in plantuml_code
        assert element_id in plantuml_code

def test_relationships_plantuml_syntax():
    """Test relationship PlantUML syntax generation."""
    from archi_mcp.server import (
        generator, ElementInput, RelationshipInput,
        _create_element_from_data, _create_relationship_from_data
    )
    
    # Clear generator
    generator.clear()
    
    # Create elements
    element1_input = ElementInput(
        id="actor1",
        name="Actor",
        element_type="Business_Actor",
        layer="Business"
    )
    
    element2_input = ElementInput(
        id="service1",
        name="Service", 
        element_type="Business_Service",
        layer="Business"
    )
    
    element1 = _create_element_from_data(element1_input)
    element2 = _create_element_from_data(element2_input)
    
    generator.add_element(element1)
    generator.add_element(element2)
    
    # Create relationship
    rel_input = RelationshipInput(
        id="rel1",
        from_element="actor1",
        to_element="service1",
        relationship_type="Serving"
    )
    
    relationship = _create_relationship_from_data(rel_input)
    generator.add_relationship(relationship)
    
    # Generate PlantUML
    plantuml_code = generator.generate_plantuml()
    
    # Validate relationship syntax
    assert "actor1" in plantuml_code
    assert "service1" in plantuml_code
    assert "Serving" in plantuml_code or "Rel_" in plantuml_code

def test_empty_diagram_plantuml():
    """Test PlantUML generation for empty diagrams."""
    from archi_mcp.server import generator
    from archi_mcp.utils.exceptions import ArchiMateGenerationError
    
    # Clear generator
    generator.clear()
    
    # Empty diagram should raise an error (which is correct behavior)
    with pytest.raises(ArchiMateGenerationError):
        generator.generate_plantuml(title="Empty Diagram")
    
    # Verify generator state
    assert generator.get_element_count() == 0
    assert generator.get_relationship_count() == 0

def test_multiple_elements_plantuml():
    """Test PlantUML generation with multiple elements."""
    from archi_mcp.server import generator, ElementInput, _create_element_from_data
    
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
    
    # Generate PlantUML
    plantuml_code = generator.generate_plantuml(title="Multiple Elements")
    
    # Validate multiple elements
    assert "@startuml" in plantuml_code
    assert "@enduml" in plantuml_code
    assert "Customer" in plantuml_code or "customer" in plantuml_code
    assert "Banking Service" in plantuml_code or "service" in plantuml_code
    assert "Banking App" in plantuml_code or "app" in plantuml_code
    assert generator.get_element_count() == 3

def test_special_characters_handling():
    """Test handling of special characters in PlantUML."""
    from archi_mcp.server import generator, ElementInput, _create_element_from_data
    
    # Clear generator
    generator.clear()
    
    # Create element with special characters
    element_input = ElementInput(
        id="special_element",
        name="Element with \"quotes\" & symbols",
        element_type="Business_Actor",
        layer="Business",
        description="Description with special chars: & < > \" '"
    )
    
    element = _create_element_from_data(element_input)
    generator.add_element(element)
    
    # Generate PlantUML
    plantuml_code = generator.generate_plantuml()
    
    # Should handle special characters without breaking
    assert isinstance(plantuml_code, str)
    assert len(plantuml_code) > 0
    assert "@startuml" in plantuml_code
    assert "@enduml" in plantuml_code
    # Basic validation - PlantUML should be structurally valid
    assert plantuml_code.count("@startuml") == plantuml_code.count("@enduml")

def test_archimate_element_types_validation():
    """Test that valid ArchiMate element types work correctly."""
    from archi_mcp.server import generator, ElementInput, _create_element_from_data
    
    # Test valid element types across different layers
    valid_elements = [
        ("Business_Actor", "Business"),
        ("Business_Service", "Business"),
        ("Application_Component", "Application"),
        ("Application_Service", "Application"),
        ("Node", "Technology"),
        ("Device", "Technology"),
        ("Stakeholder", "Motivation"),
        ("Goal", "Motivation")
    ]
    
    for element_type, layer in valid_elements:
        # Clear for each test
        generator.clear()
        
        element_input = ElementInput(
            id=f"test_{element_type.lower()}",
            name=f"Test {element_type}",
            element_type=element_type,
            layer=layer
        )
        
        element = _create_element_from_data(element_input)
        generator.add_element(element)
        
        plantuml_code = generator.generate_plantuml()
        
        # Should generate valid PlantUML
        assert isinstance(plantuml_code, str)
        assert len(plantuml_code) > 0
        assert "@startuml" in plantuml_code
        assert "@enduml" in plantuml_code
        assert element_type in plantuml_code or f"test_{element_type.lower()}" in plantuml_code

def test_plantuml_archimate_includes():
    """Test that PlantUML includes proper ArchiMate library references."""
    from archi_mcp.server import generator, ElementInput, _create_element_from_data
    
    # Clear generator
    generator.clear()
    
    # Add test element
    element_input = ElementInput(
        id="include_test",
        name="Include Test",
        element_type="Business_Actor",
        layer="Business"
    )
    
    element = _create_element_from_data(element_input)
    generator.add_element(element)
    
    # Generate PlantUML
    plantuml_code = generator.generate_plantuml()
    
    # Should include ArchiMate library references
    assert "!include" in plantuml_code or "archimate" in plantuml_code.lower()
    assert "@startuml" in plantuml_code
    assert "@enduml" in plantuml_code

def test_performance_large_diagram():
    """Test performance with larger diagrams."""
    import time
    from archi_mcp.server import generator, ElementInput, _create_element_from_data
    
    # Clear generator
    generator.clear()
    
    # Create many elements
    start_time = time.time()
    
    for i in range(20):
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
    
    # Should complete in reasonable time
    assert execution_time < 5.0, f"PlantUML generation too slow: {execution_time} seconds"
    assert isinstance(plantuml_code, str)
    assert len(plantuml_code) > 0
    assert generator.get_element_count() == 20
    assert "@startuml" in plantuml_code
    assert "@enduml" in plantuml_code

def test_plantuml_line_structure():
    """Test that generated PlantUML has proper line structure."""
    from archi_mcp.server import generator, ElementInput, _create_element_from_data
    
    # Clear generator
    generator.clear()
    
    # Add test element
    element_input = ElementInput(
        id="structure_test",
        name="Structure Test",
        element_type="Business_Actor",
        layer="Business"
    )
    
    element = _create_element_from_data(element_input)
    generator.add_element(element)
    
    # Generate PlantUML
    plantuml_code = generator.generate_plantuml(title="Structure Test")
    
    # Split into lines and validate structure
    lines = plantuml_code.split('\n')
    
    # Should have multiple lines
    assert len(lines) >= 3
    
    # First line should be @startuml
    assert lines[0].strip() == "@startuml"
    
    # Last line should be @enduml
    assert lines[-1].strip() == "@enduml"
    
    # Should contain title
    title_found = any("Structure Test" in line for line in lines)
    assert title_found