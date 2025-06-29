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
    
    # FastMCP should be initialized
    assert mcp is not None
    assert hasattr(mcp, 'name')
    assert mcp.name == 'archi-mcp'

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
    assert ("ArchiMate diagram created and validated successfully!" in result or 
            "ArchiMate diagram created successfully!" in result or 
            "Test Actor" in result)
    assert "VERIFIED ✅" in result or "```plantuml" in result or "plantuml" in result.lower()

@pytest.mark.asyncio
async def test_validate_archimate_model():
    """Test validate_archimate_model tool."""
    # Skip this test since FastMCP tools are not directly callable in tests
    pytest.skip("FastMCP tools not directly callable in test environment")

@pytest.mark.asyncio
async def test_generate_full_architecture():
    """Test generate_full_architecture tool."""
    # Skip this test since FastMCP tools are not directly callable in tests
    pytest.skip("FastMCP tools not directly callable in test environment")

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
    # Skip this test since FastMCP tools are not directly callable in tests
    pytest.skip("FastMCP tools not directly callable in test environment")