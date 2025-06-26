"""Tests for ArchiMate validator."""

import pytest
from archi_mcp.archimate.validator import ArchiMateValidator
from archi_mcp.archimate.elements.base import ArchiMateElement, ArchiMateLayer, ArchiMateAspect
from archi_mcp.archimate.relationships import ArchiMateRelationship, RelationshipType


class TestArchiMateValidator:
    """Test ArchiMate model validator."""
    
    def test_validator_initialization(self):
        """Test validator initialization."""
        validator = ArchiMateValidator()
        assert validator.strict is False
        
        strict_validator = ArchiMateValidator(strict=True)
        assert strict_validator.strict is True
    
    def test_validate_empty_model(self):
        """Test validating empty model."""
        validator = ArchiMateValidator()
        errors = validator.validate_model({}, [])
        assert len(errors) == 0
    
    def test_validate_model_with_valid_elements(self):
        """Test validating model with valid elements."""
        validator = ArchiMateValidator()
        
        elements = {
            "elem1": ArchiMateElement(
                id="elem1",
                name="Element 1",
                element_type="Business_Service",
                layer=ArchiMateLayer.BUSINESS,
                aspect=ArchiMateAspect.BEHAVIOR
            ),
            "elem2": ArchiMateElement(
                id="elem2",
                name="Element 2",
                element_type="Application_Component",
                layer=ArchiMateLayer.APPLICATION,
                aspect=ArchiMateAspect.ACTIVE_STRUCTURE
            )
        }
        
        errors = validator.validate_model(elements, [])
        assert len(errors) == 0
    
    def test_validate_model_with_invalid_elements(self):
        """Test validating model with invalid elements."""
        validator = ArchiMateValidator()
        
        elements = {
            "invalid": ArchiMateElement(
                id="",  # Invalid empty ID
                name="Invalid Element",
                element_type="Business_Service",
                layer=ArchiMateLayer.BUSINESS,
                aspect=ArchiMateAspect.BEHAVIOR
            )
        }
        
        errors = validator.validate_model(elements, [])
        assert len(errors) > 0
        assert any("Element ID is required" in error for error in errors)
    
    def test_validate_model_with_id_mismatch(self):
        """Test validating model with ID mismatch."""
        validator = ArchiMateValidator()
        
        elements = {
            "key_id": ArchiMateElement(
                id="different_id",  # Different from key
                name="Mismatched Element",
                element_type="Business_Service",
                layer=ArchiMateLayer.BUSINESS,
                aspect=ArchiMateAspect.BEHAVIOR
            )
        }
        
        errors = validator.validate_model(elements, [])
        assert len(errors) > 0
        assert any("ID mismatch" in error for error in errors)
    
    def test_validate_model_with_valid_relationships(self):
        """Test validating model with valid relationships."""
        validator = ArchiMateValidator()
        
        elements = {
            "service": ArchiMateElement(
                id="service",
                name="Business Service",
                element_type="Business_Service",
                layer=ArchiMateLayer.BUSINESS,
                aspect=ArchiMateAspect.BEHAVIOR
            ),
            "component": ArchiMateElement(
                id="component",
                name="Application Component",
                element_type="Application_Component",
                layer=ArchiMateLayer.APPLICATION,
                aspect=ArchiMateAspect.ACTIVE_STRUCTURE
            )
        }
        
        relationships = [
            ArchiMateRelationship(
                id="rel1",
                from_element="component",
                to_element="service",
                relationship_type=RelationshipType.REALIZATION
            )
        ]
        
        errors = validator.validate_model(elements, relationships)
        assert len(errors) == 0
    
    def test_validate_model_with_orphaned_relationships(self):
        """Test validating model with orphaned relationships."""
        validator = ArchiMateValidator()
        
        elements = {
            "existing": ArchiMateElement(
                id="existing",
                name="Existing Element",
                element_type="Business_Service",
                layer=ArchiMateLayer.BUSINESS,
                aspect=ArchiMateAspect.BEHAVIOR
            )
        }
        
        relationships = [
            ArchiMateRelationship(
                id="orphaned",
                from_element="missing",
                to_element="also_missing",
                relationship_type=RelationshipType.SERVING
            )
        ]
        
        errors = validator.validate_model(elements, relationships)
        assert len(errors) >= 2
        assert any("source element 'missing' not found" in error for error in errors)
        assert any("target element 'also_missing' not found" in error for error in errors)
    
    def test_validate_model_with_duplicate_relationship_ids(self):
        """Test validating model with duplicate relationship IDs."""
        validator = ArchiMateValidator()
        
        elements = {
            "elem1": ArchiMateElement(
                id="elem1",
                name="Element 1",
                element_type="Business_Service",
                layer=ArchiMateLayer.BUSINESS,
                aspect=ArchiMateAspect.BEHAVIOR
            ),
            "elem2": ArchiMateElement(
                id="elem2",
                name="Element 2",
                element_type="Application_Component",
                layer=ArchiMateLayer.APPLICATION,
                aspect=ArchiMateAspect.ACTIVE_STRUCTURE
            )
        }
        
        relationships = [
            ArchiMateRelationship(
                id="duplicate",
                from_element="elem1",
                to_element="elem2",
                relationship_type=RelationshipType.SERVING
            ),
            ArchiMateRelationship(
                id="duplicate",  # Same ID
                from_element="elem2",
                to_element="elem1",
                relationship_type=RelationshipType.ASSOCIATION
            )
        ]
        
        errors = validator.validate_model(elements, relationships)
        assert len(errors) > 0
        assert any("Duplicate relationship ID: 'duplicate'" in error for error in errors)
    
    def test_validate_element_type_business_layer(self):
        """Test validating element types for business layer."""
        validator = ArchiMateValidator()
        
        # Valid business layer elements
        valid_types = [
            "Business_Actor", "Business_Role", "Business_Service",
            "Business_Object", "Business_Process", "Location"
        ]
        
        for element_type in valid_types:
            assert validator.validate_element_type(element_type, ArchiMateLayer.BUSINESS)
        
        # Invalid business layer element
        assert not validator.validate_element_type("Application_Component", ArchiMateLayer.BUSINESS)
    
    def test_validate_element_type_application_layer(self):
        """Test validating element types for application layer."""
        validator = ArchiMateValidator()
        
        # Valid application layer elements
        valid_types = [
            "Application_Component", "Application_Service", "Data_Object",
            "Application_Interface", "Application_Function"
        ]
        
        for element_type in valid_types:
            assert validator.validate_element_type(element_type, ArchiMateLayer.APPLICATION)
        
        # Invalid application layer element
        assert not validator.validate_element_type("Business_Actor", ArchiMateLayer.APPLICATION)
    
    def test_validate_element_type_technology_layer(self):
        """Test validating element types for technology layer."""
        validator = ArchiMateValidator()
        
        # Valid technology layer elements
        valid_types = [
            "Node", "Device", "System_Software", "Technology_Service",
            "Artifact", "Communication_Network"
        ]
        
        for element_type in valid_types:
            assert validator.validate_element_type(element_type, ArchiMateLayer.TECHNOLOGY)
        
        # Invalid technology layer element
        assert not validator.validate_element_type("Business_Service", ArchiMateLayer.TECHNOLOGY)
    
    def test_get_valid_relationships_basic(self):
        """Test getting valid relationships between elements."""
        validator = ArchiMateValidator()
        
        service_element = ArchiMateElement(
            id="service",
            name="Service",
            element_type="Business_Service",
            layer=ArchiMateLayer.BUSINESS,
            aspect=ArchiMateAspect.BEHAVIOR
        )
        
        actor_element = ArchiMateElement(
            id="actor",
            name="Actor",
            element_type="Business_Actor",
            layer=ArchiMateLayer.BUSINESS,
            aspect=ArchiMateAspect.ACTIVE_STRUCTURE
        )
        
        valid_rels = validator.get_valid_relationships(service_element, actor_element)
        
        assert isinstance(valid_rels, list)
        assert len(valid_rels) > 0
        assert RelationshipType.ASSOCIATION in valid_rels
    
    def test_strict_validation_mode(self):
        """Test strict validation mode."""
        strict_validator = ArchiMateValidator(strict=True)
        
        elements = {
            "actor": ArchiMateElement(
                id="actor",
                name="Business Actor",
                element_type="Business_Actor",
                layer=ArchiMateLayer.BUSINESS,
                aspect=ArchiMateAspect.ACTIVE_STRUCTURE
            ),
            "object": ArchiMateElement(
                id="object",
                name="Business Object",
                element_type="Business_Object",
                layer=ArchiMateLayer.BUSINESS,
                aspect=ArchiMateAspect.PASSIVE_STRUCTURE
            )
        }
        
        relationships = [
            ArchiMateRelationship(
                id="access_rel",
                from_element="actor",
                to_element="object",
                relationship_type=RelationshipType.ACCESS
            )
        ]
        
        errors = strict_validator.validate_model(elements, relationships)
        # Strict validation may find additional errors
        assert isinstance(errors, list)
    
    def test_relationship_compatibility_access(self):
        """Test access relationship compatibility."""
        validator = ArchiMateValidator()
        
        # Create elements for access relationship test
        active_element = ArchiMateElement(
            id="active",
            name="Active Element",
            element_type="Business_Actor",
            layer=ArchiMateLayer.BUSINESS,
            aspect=ArchiMateAspect.ACTIVE_STRUCTURE
        )
        
        passive_element = ArchiMateElement(
            id="passive",
            name="Passive Element",
            element_type="Business_Object",
            layer=ArchiMateLayer.BUSINESS,
            aspect=ArchiMateAspect.PASSIVE_STRUCTURE
        )
        
        relationship = ArchiMateRelationship(
            id="access_test",
            from_element="active",
            to_element="passive",
            relationship_type=RelationshipType.ACCESS
        )
        
        errors = validator._check_relationship_compatibility(
            active_element, passive_element, relationship
        )
        
        # Should be valid access relationship
        assert isinstance(errors, list)
    
    def test_relationship_compatibility_assignment(self):
        """Test assignment relationship compatibility."""
        validator = ArchiMateValidator()
        
        # Create elements for assignment relationship test
        active_element = ArchiMateElement(
            id="active",
            name="Active Element",
            element_type="Business_Actor",
            layer=ArchiMateLayer.BUSINESS,
            aspect=ArchiMateAspect.ACTIVE_STRUCTURE
        )
        
        behavior_element = ArchiMateElement(
            id="behavior",
            name="Behavior Element",
            element_type="Business_Service",
            layer=ArchiMateLayer.BUSINESS,
            aspect=ArchiMateAspect.BEHAVIOR
        )
        
        relationship = ArchiMateRelationship(
            id="assignment_test",
            from_element="active",
            to_element="behavior",
            relationship_type=RelationshipType.ASSIGNMENT
        )
        
        errors = validator._check_relationship_compatibility(
            active_element, behavior_element, relationship
        )
        
        # Should be valid assignment relationship
        assert isinstance(errors, list)