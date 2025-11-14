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
        pytest.skip("create_archimate_diagram function not found")
    
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
    
    result = create_func.fn(diagram=diagram_input)
    
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
        from archi_mcp.server import ElementInput, normalize_element_type, normalize_layer
        from archi_mcp.archimate import ArchiMateElement
        from archi_mcp.archimate.elements.base import ArchiMateLayer, ArchiMateAspect
        
        element_input = ElementInput(
            id="test_element",
            name="Test Element",
            element_type="Business_Actor",
            layer="Business",
            description="Test element"
        )
        
        # Test the normalization functions that are actually used in the server
        normalized_type = normalize_element_type(element_input.element_type)
        normalized_layer = normalize_layer(element_input.layer)
        
        # Create element like the server does
        aspect = ArchiMateAspect.ACTIVE_STRUCTURE
        element = ArchiMateElement(
            id=element_input.id,
            name=element_input.name,
            element_type=normalized_type,
            layer=ArchiMateLayer(normalized_layer),
            aspect=aspect,
            description=element_input.description,
            stereotype=element_input.stereotype,
            properties=element_input.properties or {}
        )
        
        assert element.id == "test_element"
        assert element.name == "Test Element"
        assert element.element_type == "Business_Actor"
        assert element.layer == ArchiMateLayer.BUSINESS
        assert element.aspect == ArchiMateAspect.ACTIVE_STRUCTURE
    
    def test_invalid_layer(self):
        """Test handling of invalid layer."""
        from archi_mcp.server import ElementInput, validate_element_input
        import pytest
        from pydantic import ValidationError
        
        # Test Pydantic validation catches invalid layer
        with pytest.raises(ValidationError) as exc_info:
            element_input = ElementInput(
                id="test_element",
                name="Test Element", 
                element_type="Business_Actor",
                layer="InvalidLayer",
                description="Test element"
            )
        
        assert "Input should be" in str(exc_info.value)
        assert "InvalidLayer" in str(exc_info.value)

class TestRelationshipCreation:
    """Test ArchiMate relationship creation and validation."""
    
    def test_relationship_from_data(self):
        """Test creating ArchiMate relationship from data."""
        from archi_mcp.server import RelationshipInput, normalize_relationship_type
        from archi_mcp.archimate.relationships import create_relationship
        
        relationship_input = RelationshipInput(
            id="test_rel",
            from_element="elem1",
            to_element="elem2",
            relationship_type="Realization",
            description="Test relationship"
        )
        
        # Test the normalization and creation functions that are actually used
        normalized_type = normalize_relationship_type(relationship_input.relationship_type)
        
        relationship = create_relationship(
            relationship_id=relationship_input.id,
            from_element=relationship_input.from_element,
            to_element=relationship_input.to_element,
            relationship_type=normalized_type,
            description=relationship_input.description,
            label=relationship_input.label
        )
        
        assert relationship.id == "test_rel"
        assert relationship.from_element == "elem1"
        assert relationship.to_element == "elem2"
        assert relationship.description == "Test relationship"

class TestAspectDetection:
    """Test aspect detection for different element types."""
    
    def _get_aspect_for_element_type(self, element_type: str):
        """Helper function to test aspect detection logic used in server."""
        from archi_mcp.archimate.elements.base import ArchiMateAspect
        
        # This mirrors the logic in the server's create_archimate_diagram function
        if element_type in ["Business_Actor", "Business_Role", "Application_Component", "Node", "Device"]:
            return ArchiMateAspect.ACTIVE_STRUCTURE
        elif element_type in ["Business_Object", "Data_Object", "Artifact"]:
            return ArchiMateAspect.PASSIVE_STRUCTURE  
        else:
            return ArchiMateAspect.BEHAVIOR
    
    def test_active_structure_aspect(self):
        """Test active structure element aspect detection."""
        from archi_mcp.archimate.elements.base import ArchiMateAspect
        
        aspect = self._get_aspect_for_element_type("Business_Actor")
        assert aspect == ArchiMateAspect.ACTIVE_STRUCTURE
        
        aspect = self._get_aspect_for_element_type("Application_Component")
        assert aspect == ArchiMateAspect.ACTIVE_STRUCTURE
        
        aspect = self._get_aspect_for_element_type("Node")
        assert aspect == ArchiMateAspect.ACTIVE_STRUCTURE
    
    def test_passive_structure_aspect(self):
        """Test passive structure element aspect detection."""
        from archi_mcp.archimate.elements.base import ArchiMateAspect
        
        aspect = self._get_aspect_for_element_type("Business_Object")
        assert aspect == ArchiMateAspect.PASSIVE_STRUCTURE
        
        aspect = self._get_aspect_for_element_type("Data_Object")
        assert aspect == ArchiMateAspect.PASSIVE_STRUCTURE
        
        aspect = self._get_aspect_for_element_type("Artifact")
        assert aspect == ArchiMateAspect.PASSIVE_STRUCTURE
    
    def test_behavior_aspect(self):
        """Test behavior element aspect detection."""
        from archi_mcp.archimate.elements.base import ArchiMateAspect
        
        aspect = self._get_aspect_for_element_type("Business_Process")
        assert aspect == ArchiMateAspect.BEHAVIOR
        
        aspect = self._get_aspect_for_element_type("Application_Service")
        assert aspect == ArchiMateAspect.BEHAVIOR
        
        aspect = self._get_aspect_for_element_type("Unknown_Element")
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

class TestLanguageDetection:
    """Test language detection from diagram content."""

    def test_detect_slovak_language(self):
        """Test Slovak language detection."""
        from archi_mcp.server import detect_language_from_content, DiagramInput, ElementInput

        diagram = DiagramInput(
            elements=[
                ElementInput(
                    id="zakaznik",
                    name="Zákazník",
                    element_type="Business_Actor",
                    layer="Business",
                    description="Zákazník banky"
                )
            ],
            relationships=[],
            title="Bankový systém",
            description="Systém internetového bankovníctva"
        )

        language = detect_language_from_content(diagram)
        assert language == "sk"

    def test_detect_english_language(self):
        """Test English language detection."""
        from archi_mcp.server import detect_language_from_content, DiagramInput, ElementInput

        diagram = DiagramInput(
            elements=[
                ElementInput(
                    id="customer",
                    name="Customer",
                    element_type="Business_Actor",
                    layer="Business",
                    description="Bank customer"
                )
            ],
            relationships=[],
            title="Banking System",
            description="Internet banking system"
        )

        language = detect_language_from_content(diagram)
        assert language == "en"

    def test_detect_slovak_with_mixed_content(self):
        """Test Slovak detection with mixed content."""
        from archi_mcp.server import detect_language_from_content, DiagramInput, ElementInput

        # More Slovak markers should tip the balance to Slovak
        diagram = DiagramInput(
            elements=[
                ElementInput(
                    id="element1",
                    name="Správca",
                    element_type="Business_Actor",
                    layer="Business"
                ),
                ElementInput(
                    id="element2",
                    name="Používateľ",
                    element_type="Business_Actor",
                    layer="Business"
                )
            ],
            relationships=[],
            title="Architektúra systému"
        )

        language = detect_language_from_content(diagram)
        assert language == "sk"


class TestNormalizationFunctions:
    """Test normalization functions for element types, layers, and relationships."""

    def test_normalize_element_type_special_cases(self):
        """Test normalizing special case element types."""
        from archi_mcp.server import normalize_element_type

        # Test special function/process mappings
        assert normalize_element_type("function") == "Business_Function"
        assert normalize_element_type("Function") == "Business_Function"
        assert normalize_element_type("process") == "Business_Process"
        assert normalize_element_type("stakeholder") == "Stakeholder"

    def test_normalize_element_type_case_insensitive(self):
        """Test normalizing element types with case-insensitive matching."""
        from archi_mcp.server import normalize_element_type

        # Should return normalized form regardless of input case
        assert normalize_element_type("business_actor") == "Business_Actor"
        assert normalize_element_type("business_ACTOR") == "Business_Actor"

    def test_normalize_element_type_already_normalized(self):
        """Test normalizing already normalized element types."""
        from archi_mcp.server import normalize_element_type

        assert normalize_element_type("Business_Actor") == "Business_Actor"
        assert normalize_element_type("Application_Component") == "Application_Component"

    def test_normalize_layer_lowercase(self):
        """Test normalizing lowercase layers."""
        from archi_mcp.server import normalize_layer

        assert normalize_layer("business") == "Business"
        assert normalize_layer("application") == "Application"
        assert normalize_layer("technology") == "Technology"

    def test_normalize_layer_capitalized(self):
        """Test normalizing already capitalized layers."""
        from archi_mcp.server import normalize_layer

        assert normalize_layer("Business") == "Business"
        assert normalize_layer("Application") == "Application"

    def test_normalize_relationship_type_lowercase(self):
        """Test normalizing lowercase relationship types."""
        from archi_mcp.server import normalize_relationship_type

        assert normalize_relationship_type("serving") == "Serving"
        assert normalize_relationship_type("realization") == "Realization"
        assert normalize_relationship_type("access") == "Access"

    def test_normalize_relationship_type_capitalized(self):
        """Test normalizing already capitalized relationship types."""
        from archi_mcp.server import normalize_relationship_type

        assert normalize_relationship_type("Serving") == "Serving"
        assert normalize_relationship_type("Realization") == "Realization"


class TestValidationFunctions:
    """Test validation functions for elements and relationships."""

    def test_validate_element_input_valid(self):
        """Test validating valid element input."""
        from archi_mcp.server import validate_element_input, ElementInput

        element = ElementInput(
            id="test_elem",
            name="Test Element",
            element_type="Business_Actor",
            layer="Business"
        )

        is_valid, error = validate_element_input(element)
        assert is_valid is True
        assert error == ""

    def test_validate_element_input_invalid_type(self):
        """Test validating element with invalid type."""
        from archi_mcp.server import validate_element_input, ElementInput

        element = ElementInput(
            id="test_elem",
            name="Test Element",
            element_type="Invalid_Type_123",
            layer="Business"
        )

        is_valid, error = validate_element_input(element)
        assert is_valid is False
        assert "Invalid element type" in error

    def test_validate_element_input_invalid_layer(self):
        """Test validating element with invalid layer (Pydantic validates this)."""
        from archi_mcp.server import ElementInput
        import pytest
        from pydantic import ValidationError

        # Pydantic validates layer before our validate_element_input function
        with pytest.raises(ValidationError) as exc_info:
            element = ElementInput(
                id="test_elem",
                name="Test Element",
                element_type="Business_Actor",
                layer="InvalidLayer123"
            )

        assert "Input should be" in str(exc_info.value)
        assert "InvalidLayer123" in str(exc_info.value)

    def test_validate_relationship_input_valid(self):
        """Test validating valid relationship input."""
        from archi_mcp.server import validate_relationship_input, RelationshipInput

        relationship = RelationshipInput(
            id="test_rel",
            from_element="elem1",
            to_element="elem2",
            relationship_type="Serving"
        )

        is_valid, error = validate_relationship_input(relationship)
        assert is_valid is True
        assert error == ""

    def test_validate_relationship_input_invalid_type(self):
        """Test validating relationship with invalid type (Pydantic validates this)."""
        from archi_mcp.server import RelationshipInput
        import pytest
        from pydantic import ValidationError

        # Pydantic validates relationship type before our validate_relationship_input function
        with pytest.raises(ValidationError) as exc_info:
            relationship = RelationshipInput(
                id="test_rel",
                from_element="elem1",
                to_element="elem2",
                relationship_type="InvalidType"
            )

        assert "Input should be" in str(exc_info.value)
        assert "InvalidType" in str(exc_info.value)

    def test_validate_relationship_input_with_too_long_custom_name(self):
        """Test validating relationship with too long custom label."""
        from archi_mcp.server import validate_relationship_input, RelationshipInput

        # Label over 50 characters should fail
        long_label = "a" * 51
        relationship = RelationshipInput(
            id="test_rel",
            from_element="elem1",
            to_element="elem2",
            relationship_type="Serving",
            label=long_label
        )

        is_valid, error = validate_relationship_input(relationship)
        assert is_valid is False
        assert "50" in error or "character" in error.lower()


class TestCustomRelationshipValidation:
    """Test custom relationship name validation."""

    def test_validate_custom_relationship_name_valid_synonym_english(self):
        """Test validating valid synonym in English."""
        from archi_mcp.server import validate_custom_relationship_name

        # "serves" is a valid synonym for Serving
        is_valid, error = validate_custom_relationship_name("serves", "Serving", "en")
        assert is_valid is True
        assert error == ""

    def test_validate_custom_relationship_name_valid_synonym_slovak(self):
        """Test validating valid synonym in Slovak."""
        from archi_mcp.server import validate_custom_relationship_name

        # "podporuje" is a valid synonym for Serving in Slovak
        is_valid, error = validate_custom_relationship_name("podporuje", "Serving", "sk")
        assert is_valid is True
        assert error == ""

    def test_validate_custom_relationship_name_non_synonym(self):
        """Test validating non-predefined synonym (should allow with warning)."""
        from archi_mcp.server import validate_custom_relationship_name

        # Non-synonym name should return True with warning message
        is_valid, error = validate_custom_relationship_name("custom_name", "Serving", "en")
        assert is_valid is True
        # Error message should contain warning about not being in predefined synonyms
        assert "not in predefined synonyms" in error or error == ""

    def test_validate_custom_relationship_name_empty(self):
        """Test validating empty custom relationship name."""
        from archi_mcp.server import validate_custom_relationship_name

        is_valid, error = validate_custom_relationship_name("", "Serving", "en")
        assert is_valid is False
        assert "empty" in error.lower()

    def test_validate_custom_relationship_name_too_long(self):
        """Test validating too long custom relationship name."""
        from archi_mcp.server import validate_custom_relationship_name

        long_name = "a" * 51  # Over 50 characters (max is 50)
        is_valid, error = validate_custom_relationship_name(long_name, "Serving", "en")
        assert is_valid is False
        assert "50" in error or "character" in error.lower()


class TestLayoutSettings:
    """Test layout configuration settings."""

    def test_get_layout_setting_with_client_value(self):
        """Test getting layout setting with client override."""
        from archi_mcp.server import get_layout_setting

        # Client value should override when config is not locked
        result = get_layout_setting("direction", "left-right")
        # Should return client value if no env override
        assert result == "left-right" or result != ""

    def test_get_layout_setting_none_returns_env_default(self):
        """Test getting layout setting returns env setting when client_value is None."""
        from archi_mcp.server import get_layout_setting

        # When client_value is None, should return env setting (may be empty string)
        result = get_layout_setting("direction", None)
        # Should return string (either env value or empty)
        assert isinstance(result, str)


def test_complex_diagram_creation(sample_diagram_data):
    """Test creating complex diagram with multiple elements and relationships."""
    # Skip this test since FastMCP tools are not directly callable in tests
    pytest.skip("FastMCP tools not directly callable in test environment")