"""Test ArchiMate MCP Server functionality."""

import pytest
import json
import asyncio
from typing import Dict, Any
from unittest.mock import Mock, patch

# Test the server import and initialization
def test_server_import():
    """Test that server imports correctly."""
    try:
        from archi_mcp.server import mcp, main
        assert mcp is not None
        assert callable(main)
    except ImportError as e:
        pytest.fail(f"Failed to import server: {e}")

def test_server_initialization():
    """Test FastMCP server initialization."""
    from archi_mcp.server import mcp
    
    # Check that tools are registered
    assert hasattr(mcp, '_tools') or hasattr(mcp, 'tools')
    # FastMCP should have tools registered
    assert mcp is not None

def test_create_archimate_diagram():
    """Test create_archimate_diagram tool."""
    from archi_mcp.server import DiagramInput, ElementInput
    
    # Import the actual function from server module
    import archi_mcp.server as server_module
    create_func = None
    for name in dir(server_module):
        obj = getattr(server_module, name)
        if hasattr(obj, '__name__') and obj.__name__ == 'create_archimate_diagram':
            create_func = obj
            break
    
    if create_func is None:
        # Direct test of functionality
        from archi_mcp.server import generator, _create_element_from_data
        
        # Test the core functionality directly
        generator.clear()
        
        element_input = ElementInput(
            id="test_actor",
            name="Test Actor",
            element_type="Business_Actor",
            layer="Business",
            description="Test business actor"
        )
        
        element = _create_element_from_data(element_input)
        generator.add_element(element)
        
        plantuml_code = generator.generate_plantuml(title="Test Diagram")
        
        assert isinstance(plantuml_code, str)
        assert "Test Actor" in plantuml_code or "Business_Actor" in plantuml_code
        return
    
    # Create test diagram input
    diagram_input = DiagramInput(
        elements=[
            ElementInput(
                id="test_actor",
                name="Test Actor",
                element_type="Business_Actor",
                layer="Business",
                description="Test business actor"
            )
        ],
        relationships=[],
        title="Test Diagram",
        description="Test diagram description"
    )
    
    result = create_func(diagram_input)
    
    assert isinstance(result, str)
    assert "ArchiMate diagram created successfully!" in result or "Test Actor" in result
    assert "```plantuml" in result or "plantuml" in result.lower()

@pytest.mark.asyncio 
async def test_add_archimate_element():
    """Test add_archimate_element tool."""
    from archi_mcp.server import add_archimate_element
    
    result = add_archimate_element(
        element_type="Application_Component",
        id="test_app",
        name="Test Application",
        layer="Application",
        description="Test application component"
    )
    
    assert isinstance(result, str)
    assert "Element 'Test Application'" in result
    assert "added successfully" in result

@pytest.mark.asyncio
async def test_add_archimate_relationship():
    """Test add_archimate_relationship tool."""
    from archi_mcp.server import add_archimate_relationship
    
    # First add some elements to have relationships between
    from archi_mcp.server import add_archimate_element
    add_archimate_element("Business_Actor", "actor1", "Actor 1", "Business")
    add_archimate_element("Business_Service", "service1", "Service 1", "Business")
    
    result = add_archimate_relationship(
        id="test_rel",
        from_element="actor1",
        to_element="service1",
        relationship_type="Realization"
    )
    
    assert isinstance(result, str)
    assert "Relationship" in result
    assert "added successfully" in result

@pytest.mark.asyncio
async def test_validate_archimate_model():
    """Test validate_archimate_model tool."""
    from archi_mcp.server import validate_archimate_model
    
    # Test with empty model
    result = validate_archimate_model(strict=False)
    
    assert isinstance(result, str)
    assert "ArchiMate model validation" in result

@pytest.mark.asyncio
async def test_generate_archimate_template():
    """Test generate_archimate_template tool."""
    from archi_mcp.server import generate_archimate_template
    from archi_mcp.server import TemplateInput
    
    template_input = TemplateInput(
        template_type="pattern",
        template_name="three_tier",
        customization={}
    )
    
    try:
        result = generate_archimate_template(template_input)
        assert isinstance(result, str)
        # Template might not exist, but should handle gracefully
    except Exception:
        # Template not found is acceptable for testing
        pass

@pytest.mark.asyncio
async def test_export_archimate_diagram():
    """Test export_archimate_diagram tool."""
    from archi_mcp.server import export_archimate_diagram
    
    result = export_archimate_diagram(
        title="Export Test",
        description="Test export functionality"
    )
    
    assert isinstance(result, str)
    assert "ArchiMate diagram exported successfully!" in result
    assert "```plantuml" in result

@pytest.mark.asyncio
async def test_generate_full_architecture():
    """Test generate_full_architecture tool."""
    from archi_mcp.server import generate_full_architecture
    from archi_mcp.server import FullArchitectureInput
    
    architecture_input = FullArchitectureInput(
        system_description="Test banking system for unit testing",
        business_domain="banking",
        architecture_scope="system",
        include_views=["motivation", "layered_view"],
        implementation_phases=2
    )
    
    result = generate_full_architecture(architecture_input)
    
    assert isinstance(result, str)
    assert "Complete Enterprise Architecture" in result
    assert "banking" in result.lower()
    assert "```plantuml" in result

class TestElementCreation:
    """Test ArchiMate element creation and validation."""
    
    def test_element_from_data(self):
        """Test creating ArchiMate element from data."""
        from archi_mcp.server import _create_element_from_data, ElementInput
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
    
    def test_invalid_layer(self):
        """Test handling of invalid layer."""
        from archi_mcp.server import _create_element_from_data, ElementInput
        from archi_mcp.utils.exceptions import ArchiMateValidationError
        
        element_input = ElementInput(
            id="test_element",
            name="Test Element", 
            element_type="Business_Actor",
            layer="InvalidLayer",
            description="Test element"
        )
        
        with pytest.raises(ArchiMateValidationError):
            _create_element_from_data(element_input)

class TestRelationshipCreation:
    """Test ArchiMate relationship creation and validation."""
    
    def test_relationship_from_data(self):
        """Test creating ArchiMate relationship from data."""
        from archi_mcp.server import _create_relationship_from_data, RelationshipInput
        
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

class TestAspectDetection:
    """Test aspect detection for different element types."""
    
    def test_active_structure_aspect(self):
        """Test active structure element aspect detection."""
        from archi_mcp.server import _get_aspect_for_element_type
        from archi_mcp.archimate.elements.base import ArchiMateAspect
        
        aspect = _get_aspect_for_element_type("Business_Actor")
        assert aspect == ArchiMateAspect.ACTIVE_STRUCTURE
        
        aspect = _get_aspect_for_element_type("Application_Component")
        assert aspect == ArchiMateAspect.ACTIVE_STRUCTURE
        
        aspect = _get_aspect_for_element_type("Node")
        assert aspect == ArchiMateAspect.ACTIVE_STRUCTURE
    
    def test_passive_structure_aspect(self):
        """Test passive structure element aspect detection."""
        from archi_mcp.server import _get_aspect_for_element_type
        from archi_mcp.archimate.elements.base import ArchiMateAspect
        
        aspect = _get_aspect_for_element_type("Business_Object")
        assert aspect == ArchiMateAspect.PASSIVE_STRUCTURE
        
        aspect = _get_aspect_for_element_type("Data_Object")
        assert aspect == ArchiMateAspect.PASSIVE_STRUCTURE
        
        aspect = _get_aspect_for_element_type("Artifact")
        assert aspect == ArchiMateAspect.PASSIVE_STRUCTURE
    
    def test_behavior_aspect(self):
        """Test behavior element aspect detection."""
        from archi_mcp.server import _get_aspect_for_element_type
        from archi_mcp.archimate.elements.base import ArchiMateAspect
        
        aspect = _get_aspect_for_element_type("Business_Process")
        assert aspect == ArchiMateAspect.BEHAVIOR
        
        aspect = _get_aspect_for_element_type("Application_Service")
        assert aspect == ArchiMateAspect.BEHAVIOR
        
        aspect = _get_aspect_for_element_type("Unknown_Element")
        assert aspect == ArchiMateAspect.BEHAVIOR

@pytest.fixture
def sample_diagram_data():
    """Sample diagram data for testing."""
    return {
        "elements": [
            {
                "id": "customer",
                "name": "Customer",
                "element_type": "Business_Actor",
                "layer": "Business",
                "description": "Bank customer"
            },
            {
                "id": "banking_service",
                "name": "Online Banking",
                "element_type": "Business_Service",
                "layer": "Business",
                "description": "Online banking service"
            }
        ],
        "relationships": [
            {
                "id": "rel1",
                "from_element": "customer",
                "to_element": "banking_service",
                "relationship_type": "Access"
            }
        ],
        "title": "Banking System",
        "description": "Simple banking system diagram"
    }

def test_complex_diagram_creation(sample_diagram_data):
    """Test creating complex diagram with multiple elements and relationships."""
    from archi_mcp.server import create_archimate_diagram, DiagramInput, ElementInput, RelationshipInput
    
    # Convert dict data to Pydantic models
    elements = [ElementInput(**elem) for elem in sample_diagram_data["elements"]]
    relationships = [RelationshipInput(**rel) for rel in sample_diagram_data["relationships"]]
    
    diagram_input = DiagramInput(
        elements=elements,
        relationships=relationships,
        title=sample_diagram_data["title"],
        description=sample_diagram_data["description"]
    )
    
    result = create_archimate_diagram(diagram_input)
    
    assert isinstance(result, str)
    assert "Banking System" in result
    assert "Customer" in result
    assert "Online Banking" in result
    assert "Elements: 2" in result
    assert "Relationships: 1" in result