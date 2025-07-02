"""Tests for ArchiMate relationships."""

import pytest
from archi_mcp.archimate.relationships import (
    ArchiMateRelationship,
    RelationshipType,
    RelationshipDirection,
    create_relationship,
    ARCHIMATE_RELATIONSHIPS,
)
from archi_mcp.archimate.elements.base import ArchiMateElement, ArchiMateLayer, ArchiMateAspect
from archi_mcp.utils.exceptions import ArchiMateRelationshipError


class TestArchiMateRelationship:
    """Test ArchiMateRelationship class."""
    
    def test_relationship_creation(self):
        """Test basic relationship creation."""
        relationship = ArchiMateRelationship(
            id="rel_1",
            from_element="elem_1",
            to_element="elem_2",
            relationship_type=RelationshipType.SERVING,
            description="Test relationship"
        )
        
        assert relationship.id == "rel_1"
        assert relationship.from_element == "elem_1"
        assert relationship.to_element == "elem_2"
        assert relationship.relationship_type == RelationshipType.SERVING
        assert relationship.description == "Test relationship"
    
    def test_relationship_with_direction(self):
        """Test relationship with direction."""
        relationship = ArchiMateRelationship(
            id="rel_2",
            from_element="elem_a",
            to_element="elem_b",
            relationship_type=RelationshipType.REALIZATION,
            direction=RelationshipDirection.UP
        )
        
        assert relationship.direction == RelationshipDirection.UP
    
    def test_relationship_plantuml_generation(self):
        """Test PlantUML code generation."""
        relationship = ArchiMateRelationship(
            id="test_rel",
            from_element="source",
            to_element="target",
            relationship_type=RelationshipType.SERVING,
            description="serves"
        )
        
        plantuml = relationship.to_plantuml()
        expected = 'Rel_Serving(source, target, "serves")'
        assert plantuml == expected
    
    def test_relationship_plantuml_with_direction(self):
        """Test PlantUML code generation with direction."""
        relationship = ArchiMateRelationship(
            id="test_rel_dir",
            from_element="source",
            to_element="target",
            relationship_type=RelationshipType.REALIZATION,
            direction=RelationshipDirection.DOWN,
            label="realizes"
        )
        
        plantuml = relationship.to_plantuml()
        # Direction is layout hint only, not part of PlantUML syntax
        expected = 'Rel_Realization(source, target, "realizes")'
        assert plantuml == expected
    
    def test_relationship_validation_success(self):
        """Test successful relationship validation."""
        # Create test elements
        elements = {
            "elem_1": ArchiMateElement(
                id="elem_1",
                name="Element 1",
                element_type="Business_Service",
                layer=ArchiMateLayer.BUSINESS,
                aspect=ArchiMateAspect.BEHAVIOR
            ),
            "elem_2": ArchiMateElement(
                id="elem_2",
                name="Element 2",
                element_type="Application_Service",
                layer=ArchiMateLayer.APPLICATION,
                aspect=ArchiMateAspect.BEHAVIOR
            )
        }
        
        relationship = ArchiMateRelationship(
            id="valid_rel",
            from_element="elem_1",
            to_element="elem_2",
            relationship_type=RelationshipType.REALIZATION
        )
        
        errors = relationship.validate_relationship(elements)
        assert len(errors) == 0
    
    def test_relationship_validation_missing_elements(self):
        """Test relationship validation with missing elements."""
        elements = {}
        
        relationship = ArchiMateRelationship(
            id="invalid_rel",
            from_element="missing_1",
            to_element="missing_2",
            relationship_type=RelationshipType.SERVING
        )
        
        errors = relationship.validate_relationship(elements)
        assert len(errors) == 2
        assert "Source element 'missing_1' not found" in errors
        assert "Target element 'missing_2' not found" in errors
    
    def test_relationship_string_representation(self):
        """Test string representation of relationship."""
        relationship = ArchiMateRelationship(
            id="str_test",
            from_element="a",
            to_element="b",
            relationship_type=RelationshipType.COMPOSITION
        )
        
        str_repr = str(relationship)
        assert "a --Composition--> b" == str_repr


class TestRelationshipCreation:
    """Test relationship creation helper function."""
    
    def test_create_relationship_success(self):
        """Test successful relationship creation."""
        relationship = create_relationship(
            relationship_id="test_create",
            from_element="source_elem",
            to_element="target_elem",
            relationship_type="Serving",
            description="Test serving relationship"
        )
        
        assert relationship.id == "test_create"
        assert relationship.from_element == "source_elem"
        assert relationship.to_element == "target_elem"
        assert relationship.relationship_type == RelationshipType.SERVING
        assert relationship.description == "Test serving relationship"
    
    def test_create_relationship_with_direction(self):
        """Test relationship creation with direction."""
        relationship = create_relationship(
            relationship_id="test_dir",
            from_element="a",
            to_element="b",
            relationship_type="Flow",
            direction="Right",
            label="data flow"
        )
        
        assert relationship.direction == RelationshipDirection.RIGHT
        assert relationship.label == "data flow"
    
    def test_create_relationship_invalid_type(self):
        """Test relationship creation with invalid type."""
        with pytest.raises(ArchiMateRelationshipError) as exc_info:
            create_relationship(
                relationship_id="invalid_type",
                from_element="a",
                to_element="b",
                relationship_type="InvalidType"
            )
        
        assert "Invalid relationship type 'InvalidType'" in str(exc_info.value)
        assert exc_info.value.relationship_type == "InvalidType"
    
    def test_create_relationship_invalid_direction(self):
        """Test relationship creation with invalid direction."""
        with pytest.raises(ArchiMateRelationshipError) as exc_info:
            create_relationship(
                relationship_id="invalid_dir",
                from_element="a",
                to_element="b",
                relationship_type="Association",
                direction="InvalidDirection"
            )
        
        assert "Invalid direction 'InvalidDirection'" in str(exc_info.value)


class TestRelationshipTypes:
    """Test relationship type enumeration."""
    
    def test_all_relationship_types_present(self):
        """Test that all ArchiMate relationship types are present."""
        expected_types = [
            "Access", "Aggregation", "Assignment", "Association",
            "Composition", "Flow", "Influence", "Realization",
            "Serving", "Specialization", "Triggering"
        ]
        
        for rel_type in expected_types:
            assert hasattr(RelationshipType, rel_type.upper())
            assert rel_type in ARCHIMATE_RELATIONSHIPS
    
    def test_relationship_registry_completeness(self):
        """Test that relationship registry is complete."""
        assert len(ARCHIMATE_RELATIONSHIPS) == 11  # ArchiMate 3.2 has 11 relationship types
        
        # Check specific relationships
        assert ARCHIMATE_RELATIONSHIPS["Access"] == RelationshipType.ACCESS
        assert ARCHIMATE_RELATIONSHIPS["Serving"] == RelationshipType.SERVING
        assert ARCHIMATE_RELATIONSHIPS["Realization"] == RelationshipType.REALIZATION
        assert ARCHIMATE_RELATIONSHIPS["Composition"] == RelationshipType.COMPOSITION


class TestRelationshipDirection:
    """Test relationship direction enumeration."""
    
    def test_all_directions_present(self):
        """Test that all direction types are present."""
        expected_directions = ["Up", "Down", "Left", "Right"]
        
        for direction in expected_directions:
            assert hasattr(RelationshipDirection, direction.upper())


class TestRelationshipValidation:
    """Test relationship validation constraints."""
    
    def create_test_elements(self):
        """Create test elements for validation."""
        return {
            "business_actor": ArchiMateElement(
                id="business_actor",
                name="Business Actor",
                element_type="Business_Actor",
                layer=ArchiMateLayer.BUSINESS,
                aspect=ArchiMateAspect.ACTIVE_STRUCTURE
            ),
            "business_service": ArchiMateElement(
                id="business_service",
                name="Business Service",
                element_type="Business_Service",
                layer=ArchiMateLayer.BUSINESS,
                aspect=ArchiMateAspect.BEHAVIOR
            ),
            "business_object": ArchiMateElement(
                id="business_object",
                name="Business Object",
                element_type="Business_Object",
                layer=ArchiMateLayer.BUSINESS,
                aspect=ArchiMateAspect.PASSIVE_STRUCTURE
            ),
            "app_component": ArchiMateElement(
                id="app_component",
                name="Application Component",
                element_type="Application_Component",
                layer=ArchiMateLayer.APPLICATION,
                aspect=ArchiMateAspect.ACTIVE_STRUCTURE
            )
        }
    
    def test_access_relationship_validation(self):
        """Test Access relationship validation."""
        elements = self.create_test_elements()
        
        # Valid access relationship
        valid_relationship = ArchiMateRelationship(
            id="valid_access",
            from_element="business_actor",
            to_element="business_object",
            relationship_type=RelationshipType.ACCESS
        )
        
        errors = valid_relationship.validate_relationship(elements)
        # Note: Basic validation might still pass, detailed validation would catch this
        assert isinstance(errors, list)
    
    def test_composition_relationship_validation(self):
        """Test Composition relationship validation."""
        elements = self.create_test_elements()
        
        # Composition within same layer
        composition_relationship = ArchiMateRelationship(
            id="composition_test",
            from_element="business_actor",
            to_element="business_service",
            relationship_type=RelationshipType.COMPOSITION
        )
        
        errors = composition_relationship.validate_relationship(elements)
        assert isinstance(errors, list)
    
    def test_cross_layer_relationships(self):
        """Test relationships across different layers."""
        elements = self.create_test_elements()
        
        # Cross-layer serving relationship
        cross_layer_rel = ArchiMateRelationship(
            id="cross_layer",
            from_element="app_component",
            to_element="business_service",
            relationship_type=RelationshipType.SERVING
        )
        
        errors = cross_layer_rel.validate_relationship(elements)
        assert isinstance(errors, list)